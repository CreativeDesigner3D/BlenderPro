import bpy
import os
from ..bp_lib.xml import BlenderProXML

LIBRARY_FOLDER = os.path.join(os.path.dirname(__file__),"data")
LIBRARY_PATH_FILENAME = "blender_pro_paths.xml"

def get_wm_props():
    wm = bpy.context.window_manager
    return wm.bp_lib

def get_thumbnail_file_path():
    return os.path.join(os.path.dirname(__file__),"thumbnail.blend")

def get_library_path_file():
    """ Returns the path to the file that stores all of the library paths.
    """
    path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "blender_pro")

    if not os.path.exists(path):
        os.makedirs(path)
        
    return os.path.join(path,LIBRARY_PATH_FILENAME)

def get_folder_enum_previews(path,key):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the folders from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        folders = []
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)

        for i, name in enumerate(folders):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, "", 'IMAGE')
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def get_image_enum_previews(path,key,force_reload=False):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the images from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        image_paths = []
        for fn in os.listdir(path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, filepath, 'IMAGE',force_reload)
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def write_xml_file():
    xml = BlenderProXML()
    root = xml.create_tree()
    paths = xml.add_element(root,'LibraryPaths')
    
    wm = bpy.context.window_manager
    wm_props = wm.bp_lib
    
    if os.path.exists(wm_props.object_library_path):
        xml.add_element_with_text(paths,'Objects',wm_props.object_library_path)
    else:
        xml.add_element_with_text(paths,'Objects',"")
        
    if os.path.exists(wm_props.material_library_path):
        xml.add_element_with_text(paths,'Materials',wm_props.material_library_path)
    else:
        xml.add_element_with_text(paths,'Materials',"")
        
    if os.path.exists(wm_props.group_library_path):
        xml.add_element_with_text(paths,'Groups',wm_props.group_library_path)
    else:
        xml.add_element_with_text(paths,'Groups',"")
    
    xml.write(get_library_path_file())

def create_image_preview_collection():
    import bpy.utils.previews
    col = bpy.utils.previews.new()
    col.my_previews_dir = ""
    col.my_previews = ()
    return col