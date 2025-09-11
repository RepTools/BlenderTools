bl_info = {
    "name": "Distributed Animation Renderer (Master)",
    "blender": (4, 5, 0),
    "category": "Render",
    "version": (0, 1, 0),
    "author": "AJ Frio",
    "description": "Coordinates distributed rendering across networked Blender instances.",
}

import bpy
import bpy.types as _btypes
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)

import socket
import struct
import json
import threading
import queue
import time
import os
import tempfile
import subprocess
import uuid
import traceback
from typing import Optional, Tuple


# Networking configuration
UDP_DISCOVERY_PORT = 55333
TCP_CONTROL_PORT = 55334
DISCOVERY_BROADCAST_ADDR = "255.255.255.255"
DISCOVERY_MAGIC = "AR_DISCOVERY_V1"


def _safe_log(message: str) -> None:
    print(f"[AR-MASTER] {message}")


class MessageProtocol:
    @staticmethod
    def send(sock: socket.socket, header: dict, binary: Optional[bytes] = None) -> None:
        try:
            payload_size = len(binary) if binary else 0
            header = dict(header)
            header["bin_size"] = payload_size
            header_bytes = json.dumps(header).encode("utf-8")
            sock.sendall(struct.pack("!I", len(header_bytes)))
            sock.sendall(header_bytes)
            if payload_size:
                sock.sendall(binary)  # type: ignore[arg-type]
        except Exception as exc:
            raise RuntimeError(f"Failed to send message: {exc}") from exc

    @staticmethod
    def recv(sock: socket.socket) -> Optional[Tuple[dict, Optional[bytes]]]:
        def recvn(n: int) -> bytes | None:
            data = b""
            while len(data) < n:
                chunk = sock.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
            return data

        size_bytes = recvn(4)
        if not size_bytes:
            return None
        (header_len,) = struct.unpack("!I", size_bytes)
        header_bytes = recvn(header_len)
        if not header_bytes:
            return None
        header = json.loads(header_bytes.decode("utf-8"))
        bin_size = int(header.get("bin_size", 0))
        binary = None
        if bin_size:
            binary = recvn(bin_size)
            if binary is None:
                return None
        return header, binary


class SlaveInfo:
    def __init__(self, slave_id: str, name: str, address: tuple[str, int]):
        self.slave_id = slave_id
        self.name = name
        self.address = address
        self.connected = False
        self.last_seen = time.time()


class MasterState:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.slaves: dict[str, SlaveInfo] = {}
        self.connections: dict[str, "SlaveConnection"] = {}
        self.job_active = False
        self.job_cancel_event = threading.Event()
        self.job_id: Optional[str] = None
        self.total_frames = 0
        self.frames_done = 0
        self.frames_in_progress: dict[str, int] = {}
        self.frame_queue: queue.Queue[int] = queue.Queue()
        self.output_dir: Optional[str] = None
        self.temp_blend_path: Optional[str] = None
        self.local_worker_thread: Optional[threading.Thread] = None
        self.local_worker_active = False

    def reset_job(self) -> None:
        with self.lock:
            self.job_active = False
            self.job_cancel_event.clear()
            self.job_id = None
            self.total_frames = 0
            self.frames_done = 0
            self.frames_in_progress.clear()
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
            self.output_dir = None
            self.local_worker_active = False
            self.local_worker_thread = None
            tmp = self.temp_blend_path
            self.temp_blend_path = None
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


MASTER_STATE = MasterState()


class DiscoveryBroadcaster(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.stop_event = threading.Event()

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)
        hostname = socket.gethostname()
        while not self.stop_event.is_set():
            try:
                payload = json.dumps({
                    "magic": DISCOVERY_MAGIC,
                    "role": "master",
                    "name": hostname,
                    "port": TCP_CONTROL_PORT,
                }).encode("utf-8")
                sock.sendto(payload, (DISCOVERY_BROADCAST_ADDR, UDP_DISCOVERY_PORT))
            except Exception:
                pass
            self.stop_event.wait(2.0)


class DiscoveryListener(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.stop_event = threading.Event()

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", UDP_DISCOVERY_PORT))
        except Exception as exc:
            _safe_log(f"Failed to bind discovery port: {exc}")
            return
        sock.settimeout(1.0)
        while not self.stop_event.is_set():
            try:
                data, addr = sock.recvfrom(65535)
            except socket.timeout:
                continue
            except Exception:
                break
            try:
                msg = json.loads(data.decode("utf-8"))
                if msg.get("magic") != DISCOVERY_MAGIC:
                    continue
                if msg.get("role") != "slave":
                    continue
                slave_name = str(msg.get("name", "unknown"))
                slave_id = str(msg.get("id", slave_name))
                with MASTER_STATE.lock:
                    info = MASTER_STATE.slaves.get(slave_id)
                    if not info:
                        info = SlaveInfo(slave_id, slave_name, (addr[0], 0))
                        MASTER_STATE.slaves[slave_id] = info
                    info.last_seen = time.time()
            except Exception:
                continue


class SlaveConnection(threading.Thread):
    def __init__(self, conn: socket.socket, address: tuple[str, int]) -> None:
        super().__init__(daemon=True)
        self.conn = conn
        self.address = address
        self.stop_event = threading.Event()
        self.slave_id: Optional[str] = None
        self.slave_name: Optional[str] = None

    def identify(self, slave_id: str, slave_name: str) -> None:
        self.slave_id = slave_id
        self.slave_name = slave_name
        with MASTER_STATE.lock:
            info = MASTER_STATE.slaves.get(slave_id)
            if not info:
                info = SlaveInfo(slave_id, slave_name, self.address)
                MASTER_STATE.slaves[slave_id] = info
            info.connected = True
            info.name = slave_name
            info.address = self.address
            info.last_seen = time.time()
            MASTER_STATE.connections[slave_id] = self

    def run(self) -> None:
        try:
            while not self.stop_event.is_set():
                msg = MessageProtocol.recv(self.conn)
                if msg is None:
                    break
                header, binary = msg
                mtype = header.get("type")
                if mtype == "hello":
                    sid = str(header.get("id", "")) or str(uuid.uuid4())
                    sname = str(header.get("name", sid))
                    self.identify(sid, sname)
                    MessageProtocol.send(self.conn, {"type": "hello_ack"})
                    if MASTER_STATE.job_active and MASTER_STATE.temp_blend_path:
                        try:
                            with open(MASTER_STATE.temp_blend_path, "rb") as f:
                                blend_bytes = f.read()
                            header = _build_job_init_header(blend_bytes)
                            MessageProtocol.send(self.conn, header, blend_bytes)
                            self._assign_next_frame()
                        except Exception as exc:
                            _safe_log(f"Failed to init new slave: {exc}")
                elif mtype == "ready":
                    self._assign_next_frame()
                elif mtype == "frame_result":
                    frame = int(header.get("frame"))
                    ext = str(header.get("ext", "png"))
                    size = int(header.get("bin_size", 0))
                    if binary and size == len(binary):
                        self._store_frame(frame, ext, binary)
                        with MASTER_STATE.lock:
                            MASTER_STATE.frames_done += 1
                            if self.slave_id in MASTER_STATE.frames_in_progress:
                                del MASTER_STATE.frames_in_progress[self.slave_id]  # type: ignore[index]
                        self._assign_next_frame()
                elif mtype == "log":
                    text = str(header.get("text", ""))
                    _safe_log(f"Slave {self.slave_name or self.address} log: {text}")
                elif mtype == "bye":
                    break
        except Exception as exc:
            _safe_log(f"Slave connection error: {exc}")
        finally:
            try:
                self.conn.close()
            except Exception:
                pass
            with MASTER_STATE.lock:
                if self.slave_id and self.slave_id in MASTER_STATE.connections:
                    del MASTER_STATE.connections[self.slave_id]
                if self.slave_id and self.slave_id in MASTER_STATE.slaves:
                    MASTER_STATE.slaves[self.slave_id].connected = False

    def _assign_next_frame(self) -> None:
        if MASTER_STATE.job_cancel_event.is_set():
            try:
                MessageProtocol.send(self.conn, {"type": "cancel"})
            except Exception:
                pass
            return
        try:
            frame = MASTER_STATE.frame_queue.get_nowait()
        except queue.Empty:
            return
        with MASTER_STATE.lock:
            if self.slave_id:
                MASTER_STATE.frames_in_progress[self.slave_id] = frame
        try:
            MessageProtocol.send(self.conn, {"type": "assign", "frame": frame})
        except Exception as exc:
            _safe_log(f"Failed to assign frame {frame}: {exc}")
            with MASTER_STATE.lock:
                if self.slave_id and self.slave_id in MASTER_STATE.frames_in_progress:
                    del MASTER_STATE.frames_in_progress[self.slave_id]
            MASTER_STATE.frame_queue.put(frame)

    def _store_frame(self, frame: int, ext: str, data: bytes) -> None:
        out_dir = MASTER_STATE.output_dir or _ensure_output_dir()
        MASTER_STATE.output_dir = out_dir
        fname = f"frame_{frame:04d}.{ext}"
        fpath = os.path.join(out_dir, fname)
        try:
            with open(fpath, "wb") as f:
                f.write(data)
        except Exception as exc:
            _safe_log(f"Failed to write frame {frame}: {exc}")


def _ensure_output_dir() -> str:
    base = bpy.path.abspath(bpy.context.scene.render.filepath)
    if not base:
        base = os.path.join(tempfile.gettempdir(), "ar_output")
    if not os.path.isabs(base):
        base = bpy.path.abspath(base)
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        base = os.path.join(tempfile.gettempdir(), "ar_output")
        os.makedirs(base, exist_ok=True)
    return base


class ControlServer(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.stop_event = threading.Event()

    def run(self) -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            srv.bind(("", TCP_CONTROL_PORT))
            srv.listen(50)
        except Exception as exc:
            _safe_log(f"Failed to bind control port: {exc}")
            return
        srv.settimeout(1.0)
        while not self.stop_event.is_set():
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            except Exception:
                break
            handler = SlaveConnection(conn, addr)
            handler.start()


def _pack_and_copy_blend() -> str:
    scene = bpy.context.scene
    try:
        bpy.ops.file.pack_all()
    except Exception:
        pass
    tmp_dir = tempfile.gettempdir()
    fname = f"ar_job_{uuid.uuid4().hex}.blend"
    tmp_path = os.path.join(tmp_dir, fname)
    bpy.ops.wm.save_as_mainfile(filepath=tmp_path, copy=True)
    return tmp_path


def _build_job_init_header(blend_bytes: bytes) -> dict:
    scene = bpy.context.scene
    render = scene.render
    ext = scene.render.image_settings.file_format.lower()
    if ext == "jpeg":
        ext = "jpg"
    header = {
        "type": "job_init",
        "job_id": MASTER_STATE.job_id,
        "frame_start": int(scene.frame_start),
        "frame_end": int(scene.frame_end),
        "frame_step": max(1, int(scene.frame_step)),
        "res_x": int(render.resolution_x),
        "res_y": int(render.resolution_y),
        "format": scene.render.image_settings.file_format,
        "engine": scene.render.engine,
        "bin_size": len(blend_bytes),
        "blend_name": os.path.basename(MASTER_STATE.temp_blend_path or "scene.blend"),
    }
    return header


def _start_local_worker() -> None:
    if not MASTER_STATE.temp_blend_path:
        return

    def worker() -> None:
        MASTER_STATE.local_worker_active = True
        try:
            blender_bin = bpy.app.binary_path
            while not MASTER_STATE.job_cancel_event.is_set():
                try:
                    frame = MASTER_STATE.frame_queue.get_nowait()
                except queue.Empty:
                    break
                out_dir = _ensure_output_dir()
                out_pattern = os.path.join(out_dir, f"frame_#####")
                cmd = [
                    blender_bin,
                    "-b",
                    MASTER_STATE.temp_blend_path,
                    "-o",
                    out_pattern,
                    "-F",
                    bpy.context.scene.render.image_settings.file_format,
                    "-f",
                    str(frame),
                ]
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    ext = bpy.context.scene.render.image_settings.file_format.lower()
                    if ext == "jpeg":
                        ext = "jpg"
                    file_name = f"frame_{frame:05d}.{ext}"
                    src_path = os.path.join(out_dir, file_name)
                    if not os.path.exists(src_path):
                        # Some Blender versions use 4-digit padding depending on pattern; try 4
                        file_name = f"frame_{frame:04d}.{ext}"
                        src_path = os.path.join(out_dir, file_name)
                    if os.path.exists(src_path):
                        with open(src_path, "rb") as f:
                            data = f.read()
                        # Already in output dir; nothing else to do
                        with MASTER_STATE.lock:
                            MASTER_STATE.frames_done += 1
                    else:
                        with MASTER_STATE.lock:
                            MASTER_STATE.frames_done += 1
                except Exception as exc:
                    _safe_log(f"Local render failed for frame {frame}: {exc}")
                    traceback.print_exc()
        finally:
            MASTER_STATE.local_worker_active = False

    t = threading.Thread(target=worker, daemon=True)
    MASTER_STATE.local_worker_thread = t
    t.start()


def _start_job_distribution() -> None:
    MASTER_STATE.job_id = uuid.uuid4().hex
    MASTER_STATE.job_active = True
    MASTER_STATE.job_cancel_event.clear()

    MASTER_STATE.temp_blend_path = _pack_and_copy_blend()
    _safe_log(f"Prepared blend: {MASTER_STATE.temp_blend_path}")
    blend_bytes = b""
    with open(MASTER_STATE.temp_blend_path, "rb") as f:
        blend_bytes = f.read()

    scene = bpy.context.scene
    frames = list(range(scene.frame_start, scene.frame_end + 1, max(1, scene.frame_step)))
    for fr in frames:
        MASTER_STATE.frame_queue.put(int(fr))
    MASTER_STATE.total_frames = len(frames)
    MASTER_STATE.frames_done = 0

    for conn in list(MASTER_STATE.connections.values()):
        try:
            header = _build_job_init_header(blend_bytes)
            MessageProtocol.send(conn.conn, header, blend_bytes)
        except Exception as exc:
            _safe_log(f"Failed to send job to {conn.address}: {exc}")

    for conn in list(MASTER_STATE.connections.values()):
        try:
            conn._assign_next_frame()
        except Exception:
            pass

    _start_local_worker()


def _cancel_job() -> None:
    MASTER_STATE.job_cancel_event.set()
    for conn in list(MASTER_STATE.connections.values()):
        try:
            MessageProtocol.send(conn.conn, {"type": "cancel"})
        except Exception:
            pass
    MASTER_STATE.reset_job()


class AR_MasterProps(bpy.types.PropertyGroup):
    show_slaves: BoolProperty(name="Show Slaves", default=False)
    progress: FloatProperty(name="Progress", default=0.0, subtype="PERCENTAGE", min=0.0, max=100.0)
    status_text: StringProperty(name="Status", default="Idle")
    connected_count: IntProperty(name="Connected", default=0)


class AR_OT_MasterStart(bpy.types.Operator):
    bl_idname = "ar.master_start"
    bl_label = "Start Distributed Render"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if MASTER_STATE.job_active:
            self.report({"WARNING"}, "Job already running")
            return {"CANCELLED"}
        try:
            _start_job_distribution()
            context.scene.ar_master.status_text = "Rendering..."
            return {"FINISHED"}
        except Exception as exc:
            _safe_log(f"Failed to start render: {exc}")
            traceback.print_exc()
            self.report({"ERROR"}, f"Start failed: {exc}")
            return {"CANCELLED"}


class AR_OT_MasterCancel(bpy.types.Operator):
    bl_idname = "ar.master_cancel"
    bl_label = "Cancel Distributed Render"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if not MASTER_STATE.job_active:
            self.report({"INFO"}, "No active job")
            return {"CANCELLED"}
        try:
            _cancel_job()
            context.scene.ar_master.status_text = "Cancelled"
            return {"FINISHED"}
        except Exception as exc:
            self.report({"ERROR"}, f"Cancel failed: {exc}")
            return {"CANCELLED"}


class AR_PT_MasterPanel(bpy.types.Panel):
    bl_label = "Distributed Renderer (Master)"
    bl_idname = "AR_PT_master_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Renderer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ar_master

        # Read-only snapshot; do not write to ID properties here
        with MASTER_STATE.lock:
            connected_count = len([c for c in MASTER_STATE.slaves.values() if c.connected])
            total = MASTER_STATE.total_frames
            done = MASTER_STATE.frames_done
        fraction = (float(done) / float(total)) if total > 0 else 0.0

        row = layout.row()
        row.label(text=f"Connected: {connected_count}")
        layout.prop(props, "show_slaves", text="Show Slaves")
        if props.show_slaves:
            box = layout.box()
            with MASTER_STATE.lock:
                if not MASTER_STATE.slaves:
                    box.label(text="No slaves discovered yet")
                else:
                    for s in MASTER_STATE.slaves.values():
                        status = "Connected" if s.connected else "Seen"
                        box.label(text=f"{s.name} ({status})")

        layout.separator()
        row = layout.row()
        row.operator(AR_OT_MasterStart.bl_idname, icon="RENDER_ANIMATION")
        row.operator(AR_OT_MasterCancel.bl_idname, icon="CANCEL")
        layout.separator()
        layout.template_progress_bar(fraction, text=f"{int(done)}/{int(total)} frames")
        layout.label(text=props.status_text)


_threads_started = False
_discovery_broadcaster: Optional[DiscoveryBroadcaster] = None
_discovery_listener: Optional[DiscoveryListener] = None
_control_server: Optional[ControlServer] = None


def _ui_timer_update() -> float:
    scene = bpy.context.scene
    if not hasattr(scene, "ar_master"):
        return 1.0
    props = scene.ar_master
    with MASTER_STATE.lock:
        total = MASTER_STATE.total_frames
        done = MASTER_STATE.frames_done
    fraction = (float(done) / float(total)) if total > 0 else 0.0
    props.progress = 100.0 * fraction
    if MASTER_STATE.job_active:
        props.status_text = "Rendering..."
    else:
        if props.status_text == "Rendering...":
            props.status_text = "Idle"
    return 0.5


classes = (
    AR_MasterProps,
    AR_OT_MasterStart,
    AR_OT_MasterCancel,
    AR_PT_MasterPanel,
)


def register():
    global _threads_started, _discovery_broadcaster, _discovery_listener, _control_server
    for cls in classes:
        bpy.utils.register_class(cls)
    if not hasattr(bpy.types.Scene, "ar_master"):
        bpy.types.Scene.ar_master = bpy.props.PointerProperty(type=AR_MasterProps)

    if not _threads_started:
        _discovery_broadcaster = DiscoveryBroadcaster()
        _discovery_listener = DiscoveryListener()
        _control_server = ControlServer()
        _discovery_broadcaster.start()
        _discovery_listener.start()
        _control_server.start()
        _threads_started = True
    bpy.app.timers.register(_ui_timer_update, persistent=True)


def unregister():
    global _threads_started, _discovery_broadcaster, _discovery_listener, _control_server
    try:
        bpy.app.timers.unregister(_ui_timer_update)
    except Exception:
        pass
    if _threads_started:
        if _discovery_broadcaster:
            _discovery_broadcaster.stop_event.set()
        if _discovery_listener:
            _discovery_listener.stop_event.set()
        if _control_server:
            _control_server.stop_event.set()
        _threads_started = False
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    if hasattr(bpy.types.Scene, "ar_master"):
        try:
            del bpy.types.Scene.ar_master
        except Exception:
            pass


