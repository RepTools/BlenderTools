bl_info = {
    "name": "Distributed Animation Renderer (Slave)",
    "blender": (4, 5, 0),
    "category": "Render",
    "version": (0, 1, 0),
    "author": "AJ Frio",
    "description": "Joins distributed rendering and renders assigned frames.",
}

import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
)

import socket
import struct
import json
import threading
import os
import tempfile
import uuid
import time
import subprocess
import traceback
from typing import Optional, Tuple


UDP_DISCOVERY_PORT = 55333
TCP_CONTROL_PORT = 55334
DISCOVERY_MAGIC = "AR_DISCOVERY_V1"


def _safe_log(message: str) -> None:
    print(f"[AR-SLAVE] {message}")


class MessageProtocol:
    @staticmethod
    def send(sock: socket.socket, header: dict, binary: Optional[bytes] = None) -> None:
        payload_size = len(binary) if binary else 0
        header = dict(header)
        header["bin_size"] = payload_size
        header_bytes = json.dumps(header).encode("utf-8")
        try:
            peer = "unknown"
            try:
                host, port = sock.getpeername()
                peer = f"{host}:{port}"
            except Exception:
                pass
            _safe_log(f"TX to {peer}: {header.get('type')} bin={payload_size}")
        except Exception:
            pass
        sock.sendall(struct.pack("!I", len(header_bytes)))
        sock.sendall(header_bytes)
        if payload_size:
            sock.sendall(binary)  # type: ignore[arg-type]

    @staticmethod
    def recv(sock: socket.socket) -> Optional[Tuple[dict, Optional[bytes]]]:
        def recvn(n: int) -> Optional[bytes]:
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
        try:
            peer = "unknown"
            try:
                host, port = sock.getpeername()
                peer = f"{host}:{port}"
            except Exception:
                pass
            _safe_log(f"RX from {peer}: {header.get('type')} bin={bin_size}")
        except Exception:
            pass
        binary = None
        if bin_size:
            binary = recvn(bin_size)
            if binary is None:
                return None
        return header, binary


class SlaveState:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.master_name: str = ""
        self.master_addr: Optional[str] = None
        self.connected: bool = False
        self.client_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.identity = {
            "id": str(uuid.uuid4()),
            "name": socket.gethostname(),
        }
        self.job_active = False
        self.temp_blend_path: Optional[str] = None
        self.render_format: str = "PNG"
        self.frame_padding = 5


SLAVE_STATE = SlaveState()


class DiscoveryBroadcaster(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.stop_event = threading.Event()

    def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)
        while not self.stop_event.is_set():
            try:
                payload = json.dumps({
                    "magic": DISCOVERY_MAGIC,
                    "role": "slave",
                    "name": SLAVE_STATE.identity["name"],
                    "id": SLAVE_STATE.identity["id"],
                }).encode("utf-8")
                sock.sendto(payload, ("255.255.255.255", UDP_DISCOVERY_PORT))
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
            _safe_log(f"Failed to bind discovery: {exc}")
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
                if msg.get("role") != "master":
                    continue
                with SLAVE_STATE.lock:
                    SLAVE_STATE.master_addr = addr[0]
                    SLAVE_STATE.master_name = str(msg.get("name", addr[0]))
            except Exception:
                continue


def _ensure_temp_dir() -> str:
    d = os.path.join(tempfile.gettempdir(), "ar_slave")
    os.makedirs(d, exist_ok=True)
    return d


def _client_loop(master_ip: str) -> None:
    _safe_log(f"Connecting to master at {master_ip}:{TCP_CONTROL_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    try:
        sock.connect((master_ip, TCP_CONTROL_PORT))
    except Exception as exc:
        _safe_log(f"Connect failed: {exc}")
        return
    sock.settimeout(2.0)
    try:
        MessageProtocol.send(sock, {"type": "hello", **SLAVE_STATE.identity})
        hello = None
        while not SLAVE_STATE.stop_event.is_set():
            try:
                hello = MessageProtocol.recv(sock)
                if hello is not None:
                    break
            except (socket.timeout, TimeoutError):
                continue
        if not hello:
            _safe_log("No hello ack from master")
            return
        _safe_log("Connected to master")
        with SLAVE_STATE.lock:
            SLAVE_STATE.connected = True

        while not SLAVE_STATE.stop_event.is_set():
            try:
                msg = MessageProtocol.recv(sock)
            except (socket.timeout, TimeoutError):
                continue
            if msg is None:
                break
            header, binary = msg
            mtype = header.get("type")
            if mtype == "job_init":
                _handle_job_init(header, binary, sock)
            elif mtype == "assign":
                frame = int(header.get("frame"))
                _render_frame_and_send(sock, frame)
            elif mtype == "cancel":
                _safe_log("Job cancelled by master")
                with SLAVE_STATE.lock:
                    SLAVE_STATE.job_active = False
                    if SLAVE_STATE.temp_blend_path and os.path.exists(SLAVE_STATE.temp_blend_path):
                        try:
                            os.remove(SLAVE_STATE.temp_blend_path)
                        except Exception:
                            pass
                    SLAVE_STATE.temp_blend_path = None
            else:
                pass
    except Exception as exc:
        _safe_log(f"Client error: {exc}")
        traceback.print_exc()
    finally:
        try:
            sock.close()
        except Exception:
            pass
        with SLAVE_STATE.lock:
            SLAVE_STATE.connected = False


def _handle_job_init(header: dict, binary: Optional[bytes], sock: socket.socket) -> None:
    if not binary:
        return
    temp_dir = _ensure_temp_dir()
    fname = header.get("blend_name") or f"job_{uuid.uuid4().hex}.blend"
    blend_path = os.path.join(temp_dir, str(fname))
    try:
        with open(blend_path, "wb") as f:
            f.write(binary)
    except Exception as exc:
        _safe_log(f"Failed to write blend: {exc}")
        return
    with SLAVE_STATE.lock:
        SLAVE_STATE.temp_blend_path = blend_path
        SLAVE_STATE.job_active = True
        SLAVE_STATE.render_format = str(header.get("format", "PNG"))
    _safe_log(f"Job init received: frames {header.get('frame_start')}..{header.get('frame_end')} step {header.get('frame_step')} format {SLAVE_STATE.render_format}")
    MessageProtocol.send(sock, {"type": "ready"})


def _render_frame_and_send(sock: socket.socket, frame: int) -> None:
    with SLAVE_STATE.lock:
        if not SLAVE_STATE.temp_blend_path:
            MessageProtocol.send(sock, {"type": "log", "text": "No blend loaded"})
            return
        blend_path = SLAVE_STATE.temp_blend_path
        fmt = SLAVE_STATE.render_format
    blender_bin = bpy.app.binary_path
    out_dir = _ensure_temp_dir()
    out_pattern = os.path.join(out_dir, "frame_#####")
    _safe_log(f"Rendering frame {frame} using {fmt} ...")
    cmd = [
        blender_bin,
        "-b",
        blend_path,
        "-o",
        out_pattern,
        "-F",
        fmt,
        "-f",
        str(frame),
    ]
    try:
        t0 = time.time()
        proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dt = time.time() - t0
        _safe_log(f"Rendered frame {frame} in {dt:0.1f}s, stdout {len(proc.stdout)}B")
    except Exception as exc:
        MessageProtocol.send(sock, {"type": "log", "text": f"Render failed for frame {frame}: {exc}"})
        return

    ext = fmt.lower()
    if ext == "jpeg":
        ext = "jpg"
    filename = f"frame_{frame:05d}.{ext}"
    fpath = os.path.join(out_dir, filename)
    if not os.path.exists(fpath):
        filename = f"frame_{frame:04d}.{ext}"
        fpath = os.path.join(out_dir, filename)
    try:
        with open(fpath, "rb") as f:
            data = f.read()
        _safe_log(f"Sending frame {frame} ({len(data)} bytes)")
        MessageProtocol.send(sock, {"type": "frame_result", "frame": frame, "ext": ext}, data)
        MessageProtocol.send(sock, {"type": "ready"})
    except Exception as exc:
        MessageProtocol.send(sock, {"type": "log", "text": f"Failed sending frame {frame}: {exc}"})


class AR_SlaveProps(bpy.types.PropertyGroup):
    connected: BoolProperty(name="Connected", default=False)
    master_name: StringProperty(name="Master", default="")


class AR_PT_SlavePanel(bpy.types.Panel):
    bl_label = "Distributed Renderer (Slave)"
    bl_idname = "AR_PT_slave_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Renderer"

    def draw(self, context):
        layout = self.layout
        # Read-only snapshot for drawing; don't write to ID properties in draw()
        connected = False
        master_name = ""
        with SLAVE_STATE.lock:
            connected = SLAVE_STATE.connected
            master_name = SLAVE_STATE.master_name
        status = "Connected" if connected else "Searching..."
        layout.label(text=f"Status: {status}")
        layout.label(text=f"Master: {master_name or '-'}")


_threads_started = False
_disc_broadcaster: Optional[DiscoveryBroadcaster] = None
_disc_listener: Optional[DiscoveryListener] = None
_client_thread: Optional[threading.Thread] = None


def _maintain_connection_timer() -> float:
    with SLAVE_STATE.lock:
        master_ip = SLAVE_STATE.master_addr
        connected = SLAVE_STATE.connected
        running = SLAVE_STATE.client_thread is not None and SLAVE_STATE.client_thread.is_alive()
    if master_ip and not connected and not running:
        def starter():
            _client_loop(master_ip)
        t = threading.Thread(target=starter, daemon=True)
        with SLAVE_STATE.lock:
            SLAVE_STATE.client_thread = t
        t.start()
    return 1.0


classes = (
    AR_SlaveProps,
    AR_PT_SlavePanel,
)


def register():
    global _threads_started, _disc_broadcaster, _disc_listener
    for cls in classes:
        bpy.utils.register_class(cls)
    if not hasattr(bpy.types.Scene, "ar_slave"):
        bpy.types.Scene.ar_slave = bpy.props.PointerProperty(type=AR_SlaveProps)

    if not _threads_started:
        _disc_broadcaster = DiscoveryBroadcaster()
        _disc_listener = DiscoveryListener()
        _disc_broadcaster.start()
        _disc_listener.start()
        _threads_started = True
    bpy.app.timers.register(_maintain_connection_timer, persistent=True)


def unregister():
    global _threads_started, _disc_broadcaster, _disc_listener
    try:
        bpy.app.timers.unregister(_maintain_connection_timer)
    except Exception:
        pass
    if _threads_started:
        if _disc_broadcaster:
            _disc_broadcaster.stop_event.set()
        if _disc_listener:
            _disc_listener.stop_event.set()
        _threads_started = False
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    if hasattr(bpy.types.Scene, "ar_slave"):
        try:
            del bpy.types.Scene.ar_slave
        except Exception:
            pass


