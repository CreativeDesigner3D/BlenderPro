import bpy
import os
from ..bp_lib import utils
from . import library_utils

OBJECT_FOLDER = os.path.join(library_utils.LIBRARY_FOLDER,"objects")
preview_collections = {}
preview_collections["object_categories"] = library_utils.create_image_preview_collection()
preview_collections["object_items"] = library_utils.create_image_preview_collection()

def enum_object_categories(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(OBJECT_FOLDER)
    pcoll = preview_collections["object_categories"]
    return library_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_object_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(OBJECT_FOLDER,self.object_category)
    pcoll = preview_collections["object_items"]
    return library_utils.get_image_enum_previews(icon_dir,pcoll)

def update_object_category(self,context):
    if preview_collections["object_items"]:
        bpy.utils.previews.remove(preview_collections["object_items"])
        preview_collections["object_items"] = library_utils.create_image_preview_collection()     
        
    enum_object_names(self,context)

class LIBRARY_OT_add_object_from_library(bpy.types.Operator):
    bl_idname = "library.add_object_from_library"
    bl_label = "Add Object From Library"
    
    obj_name = bpy.props.StringProperty(name="Obj Name")
    object_category = bpy.props.EnumProperty(name="Object Category",items=enum_object_categories,update=update_object_category)
    object_name = bpy.props.EnumProperty(name="Object Name",items=enum_object_names)
    
    drawing_plane = None
    obj = None
    
    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self,'object_category',text="",icon='FILE_FOLDER')  
        layout.template_icon_view(self,"object_name",show_labels=True)  
        layout.label(self.object_name)
        
    def execute(self, context):
        self.create_drawing_plane(context)
        self.obj = self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        object_file_path = os.path.join(OBJECT_FOLDER ,self.object_category,self.object_name + ".blend")
        with bpy.data.libraries.load(object_file_path, False, False) as (data_from, data_to):
            for obj in data_from.objects:
                data_to.objects = [obj]
                break
        for obj in data_to.objects:
            context.scene.objects.link(obj)
            return obj

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.draw_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = utils.get_selection_point(context,event,exclude_objects=[self.obj])

        self.position_object(selected_point,selected_obj)
        
        if self.event_is_place_object(event):
            return self.finish(context)

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def event_is_place_object(self,event):
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

    def position_object(self,selected_point,selected_obj):
        self.obj.location = selected_point

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.obj)
        utils.delete_obj_list(obj_list)
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            utils.delete_obj_list([self.drawing_plane])
        context.area.tag_redraw()
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(LIBRARY_OT_add_object_from_library)        

def unregister():
    bpy.utils.unregister_class(LIBRARY_OT_add_object_from_library)
    