"""
Blender script: Unhide and un-holdout all parts and folders.
Makes every collection and object visible in viewport and render,
and clears any holdout property so nothing is masked.
Run in Blender's Scripting workspace or via: blender file.blend -P showAll.py
"""

import bpy


def get_view_layer_collection(collection, view_layer=None):
    """Get the view layer collection for a given collection (for exclude property)."""
    if view_layer is None:
        view_layer = bpy.context.view_layer

    def find_layer_collection(layer_coll, target_coll):
        if layer_coll.collection == target_coll:
            return layer_coll
        for child in layer_coll.children:
            result = find_layer_collection(child, target_coll)
            if result:
                return result
        return None

    return find_layer_collection(view_layer.layer_collection, collection)


def set_collection_visibility(collection, visible):
    """Set collection visibility for viewport and render; recursively sets objects and child collections."""
    if not collection:
        return
    collection.hide_viewport = not visible
    collection.hide_render = not visible

    # View layer: exclude and hide flags (each "folder" in outliner has its own viewport/render visibility)
    layer_coll = get_view_layer_collection(collection)
    if layer_coll:
        layer_coll.exclude = not visible
        if hasattr(layer_coll, "hide_viewport"):
            layer_coll.hide_viewport = not visible
        if hasattr(layer_coll, "hide_render"):
            layer_coll.hide_render = not visible

    for obj in collection.objects:
        obj.hide_viewport = not visible
        obj.hide_render = not visible

    for child_coll in collection.children:
        set_collection_visibility(child_coll, visible)


def set_holdout_on_object(obj, holdout_enabled):
    """Set holdout on a single object (Cycles is_holdout; any type that has it)."""
    if not obj:
        return
    if hasattr(obj, "is_holdout"):
        obj.is_holdout = holdout_enabled


def set_holdout_property(collection_or_object, holdout_enabled):
    """Set holdout on a collection (all objects recursively) or a single object."""
    if isinstance(collection_or_object, bpy.types.Collection):
        for obj in collection_or_object.objects:
            set_holdout_on_object(obj, holdout_enabled)
        for child_coll in collection_or_object.children:
            set_holdout_property(child_coll, holdout_enabled)
    elif isinstance(collection_or_object, bpy.types.Object):
        set_holdout_on_object(collection_or_object, holdout_enabled)


def show_all_in_collection(collection):
    """Recursively unhide collection, all its objects, child collections, and clear holdout."""
    if not collection:
        return
    set_collection_visibility(collection, True)
    set_holdout_property(collection, False)
    for child_coll in collection.children:
        show_all_in_collection(child_coll)


def set_layer_collection_visible(layer_coll, visible):
    """Set visibility on a view-layer LayerCollection (the 'folder' in the outliner).
    Also clears holdout and indirect_only so no collection is in a holdout state."""
    layer_coll.exclude = not visible
    if hasattr(layer_coll, "hide_viewport"):
        layer_coll.hide_viewport = not visible
    if hasattr(layer_coll, "hide_render"):
        layer_coll.hide_render = not visible
    # Per–view-layer holdout: LayerCollection can be set to holdout (mask) in the outliner.
    if hasattr(layer_coll, "holdout"):
        layer_coll.holdout = False
    if hasattr(layer_coll, "indirect_only"):
        layer_coll.indirect_only = False
    for child in layer_coll.children:
        set_layer_collection_visible(child, visible)


def _exit_local_view():
    """Exit Local View (Numpad /) in any 3D viewport so nothing is isolated."""
    try:
        for window in getattr(bpy.context.window_manager, "windows", []):
            for area in getattr(window.screen, "areas", []):
                if area.type != "VIEW_3D":
                    continue
                for space in getattr(area, "spaces", []):
                    if space.type == "VIEW_3D" and getattr(space, "local_view", None):
                        if hasattr(bpy.context, "temp_override"):
                            with bpy.context.temp_override(window=window, area=area):
                                bpy.ops.view3d.localview(frame_selected=False)
                        else:
                            bpy.ops.view3d.localview(frame_selected=False)
                        return
    except Exception:
        pass


def show_all():
    """Unhide and un-holdout all collections and objects in the scene."""
    # 1. ALL SCENES & VIEW LAYERS: Make every LayerCollection visible (exclude + hide_viewport + hide_render).
    #    If we only update the active view layer, other layers or the outliner state can leave things hidden.
    for scene in bpy.data.scenes:
        for view_layer in scene.view_layers:
            set_layer_collection_visible(view_layer.layer_collection, True)

    # 2. Data collections: unhide and un-exclude (viewport + render)
    for coll in bpy.data.collections:
        show_all_in_collection(coll)

    # 3. All objects: clear global visibility + per–view-layer "eye" hide + holdout
    for obj in bpy.data.objects:
        obj.hide_viewport = False
        obj.hide_render = False
        set_holdout_on_object(obj, False)
        # Per–view-layer hide (eye icon in outliner); must be cleared in each view layer.
        for scene in bpy.data.scenes:
            for view_layer in scene.view_layers:
                try:
                    obj.hide_set(False, view_layer=view_layer)
                except Exception:
                    pass

    # 4. Again ensure every LayerCollection in every scene/view layer is visible
    for scene in bpy.data.scenes:
        for view_layer in scene.view_layers:
            set_layer_collection_visible(view_layer.layer_collection, True)

    # 5. Exit Local View if active so the 3D viewport shows everything
    _exit_local_view()

    print("showAll: All parts and folders are now visible; holdouts cleared.")


if __name__ == "__main__":
    show_all()
