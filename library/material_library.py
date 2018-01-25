import bpy
import os
from .. import utils
from . import library_utils

MATERIAL_FOLDER = os.path.join(library_utils.LIBRARY_FOLDER,"materials")
preview_collections = {}
preview_collections["material_categories"] = library_utils.create_image_preview_collection()
preview_collections["material_items"] = library_utils.create_image_preview_collection()

def enum_material_categories(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(MATERIAL_FOLDER)
    pcoll = preview_collections["material_categories"]
    return library_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_material_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(MATERIAL_FOLDER,self.material_category)
    pcoll = preview_collections["material_items"]
    return library_utils.get_image_enum_previews(icon_dir,pcoll)

def update_material_category(self,context):
    if preview_collections["material_items"]:
        bpy.utils.previews.remove(preview_collections["material_items"])
        preview_collections["material_items"] = library_utils.create_image_preview_collection()     
        
    enum_material_names(self,context)

class LIBRARY_OT_add_material_from_library(bpy.types.Operator):
    bl_idname = "library.add_material_from_library"
    bl_label = "Add Material From Library"
    
    obj_name = bpy.props.StringProperty(name="Obj Name")
    material_category = bpy.props.EnumProperty(name="Material Category",items=enum_material_categories,update=update_material_category)
    material_name = bpy.props.EnumProperty(name="Material Name",items=enum_material_names)
    
    drawing_plane = None
    mat = None
    
    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        return True

    def invoke(self,context,event):
        self.parent_objects = []
        self.group_objects = []
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self,'material_category',text="",icon='FILE_FOLDER')  
        layout.template_icon_view(self,"material_name",show_labels=True)  
        layout.label(self.material_name)
        
    def execute(self, context):
        self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def get_material(self,context):
        material_file_path = os.path.join(MATERIAL_FOLDER ,self.material_category,self.material_name + ".blend")
        with bpy.data.libraries.load(material_file_path, False, False) as (data_from, data_to):
            
            for mat in data_from.materials:
                data_to.materials = [mat]
                break
            
        for mat in data_to.materials:
            return mat
    
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = utils.get_selection_point(context,event,exclude_objects=self.group_objects)

        if self.event_is_place_material(event):
            return self.finish(context)

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def event_is_place_material(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_cancel_command(self,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return True
        else:
            return False
    
    def event_is_pass_through(self,event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return True
        else:
            return False

    def cancel_drop(self,context):
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(LIBRARY_OT_add_material_from_library)

def unregister():
    bpy.utils.unregister_class(LIBRARY_OT_add_material_from_library)
    