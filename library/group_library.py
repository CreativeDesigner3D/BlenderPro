import bpy
import os
from ..bp_lib import utils
from . import library_utils

OBJECT_FOLDER = os.path.join(library_utils.LIBRARY_FOLDER,"groups")
preview_collections = {}
preview_collections["group_categories"] = library_utils.create_image_preview_collection()
preview_collections["group_items"] = library_utils.create_image_preview_collection()

def enum_group_categories(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(OBJECT_FOLDER)
    pcoll = preview_collections["group_categories"]
    return library_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_group_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(OBJECT_FOLDER,self.group_category)
    pcoll = preview_collections["group_items"]
    return library_utils.get_image_enum_previews(icon_dir,pcoll)

def update_group_category(self,context):
    if preview_collections["group_items"]:
        bpy.utils.previews.remove(preview_collections["group_items"])
        preview_collections["group_items"] = library_utils.create_image_preview_collection()     
        
    enum_group_names(self,context)

class LIBRARY_OT_add_group_from_library(bpy.types.Operator):
    bl_idname = "library.add_group_from_library"
    bl_label = "Add Group From Library"
    
    obj_name = bpy.props.StringProperty(name="Obj Name")
    group_category = bpy.props.EnumProperty(name="Group Category",items=enum_group_categories,update=update_group_category)
    group_name = bpy.props.EnumProperty(name="Group Name",items=enum_group_names)
    
    drawing_plane = None
    grp = None
    parent_objects = []
    group_objects = []
    
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
        layout.prop(self,'group_category',text="",icon='FILE_FOLDER')  
        layout.template_icon_view(self,"group_name",show_labels=True)  
        layout.label(self.group_name)
        
    def execute(self, context):
        self.create_drawing_plane(context)
        self.grp = self.get_group(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_group(self,context):
        group_file_path = os.path.join(OBJECT_FOLDER ,self.group_category,self.group_name + ".blend")
        with bpy.data.libraries.load(group_file_path, False, False) as (data_from, data_to):
            
            for grp in data_from.groups:
                data_to.groups = [grp]
                break
            
        for grp in data_to.groups:
            for obj in grp.objects:
                self.group_objects.append(obj)
                context.scene.objects.link(obj)
                if obj.parent is None:
                    self.parent_objects.append(obj)   

            return grp

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
        selected_point, selected_obj = utils.get_selection_point(context,event,exclude_objects=self.group_objects)

        self.position_group(selected_point,selected_obj)
        
        if self.event_is_place_group(event):
            return self.finish(context)

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def event_is_place_group(self,event):
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

    def position_group(self,selected_point,selected_obj):
        for obj in self.parent_objects:
            obj.location = selected_point

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.group_objects:
            obj_list.append(obj)
        utils.delete_obj_list(obj_list)
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            utils.delete_obj_list([self.drawing_plane])
        context.area.tag_redraw()
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(LIBRARY_OT_add_group_from_library)

def unregister():
    bpy.utils.unregister_class(LIBRARY_OT_add_group_from_library)
    