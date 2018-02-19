import bpy
import os
from . import utils_library
from ..bp_lib.xml import BlenderProXML
import xml.etree.ElementTree as ET
from bpy.app.handlers import persistent

@persistent
def update_library_paths_on_startup(scene=None):
    wm_props = bpy.context.window_manager.bp_lib
    if os.path.exists(utils_library.get_library_path_file()):
        tree = ET.parse(utils_library.get_library_path_file())
        root = tree.getroot()
        for elm in root.findall("LibraryPaths"):
            items = elm.getchildren()
            for item in items:
                
                if item.tag == 'Objects':
                    if os.path.exists(str(item.text)):
                        wm_props.object_library_path = item.text
                    else:
                        wm_props.object_library_path = ""
                        
                if item.tag == 'Materials':
                    if os.path.exists(str(item.text)):
                        wm_props.material_library_path = item.text
                    else:
                        wm_props.material_library_path = ""
                        
                if item.tag == 'Groups':
                    if os.path.exists(str(item.text)):
                        wm_props.group_library_path = item.text
                    else:
                        wm_props.group_library_path = "" 
                                              
def update_library_paths(self,context):
    utils_library.write_xml_file()

class PROPS_window_manager(bpy.types.PropertyGroup):
    object_library_path = bpy.props.StringProperty(name="Object Library Path",
                                                   default="",
                                                   subtype='DIR_PATH',
                                                   update=update_library_paths)
    
    group_library_path = bpy.props.StringProperty(name="Group Library Path",
                                                  default="",
                                                  subtype='DIR_PATH',
                                                  update=update_library_paths)
    
    material_library_path = bpy.props.StringProperty(name="Material Library Path",
                                                     default="",
                                                     subtype='DIR_PATH',
                                                     update=update_library_paths)        

    object_category = bpy.props.StringProperty(name="Object Category",
                                               default="",
                                               update=update_library_paths)   
        
    group_category = bpy.props.StringProperty(name="Group Category",
                                              default="",
                                              update=update_library_paths)  
    
    material_category = bpy.props.StringProperty(name="Material Category",
                                                 default="",
                                                 update=update_library_paths)  
                
def register():
    bpy.app.handlers.load_post.append(update_library_paths_on_startup)
    
    bpy.utils.register_class(PROPS_window_manager) 
    bpy.types.WindowManager.bp_lib = bpy.props.PointerProperty(type = PROPS_window_manager)
    