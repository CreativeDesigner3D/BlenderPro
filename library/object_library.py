import bpy
import os
import subprocess
from ..bp_lib import utils
from . import utils_library

OBJECT_FOLDER = os.path.join(utils_library.LIBRARY_FOLDER,"objects")
preview_collections = {}
preview_collections["object_categories"] = utils_library.create_image_preview_collection()
preview_collections["object_items"] = utils_library.create_image_preview_collection()

def get_library_path():
    props = utils_library.get_wm_props()
    if os.path.exists(props.object_library_path):
        return props.object_library_path
    else:
        return OBJECT_FOLDER

def enum_object_categories(self,context):
    if context is None:
        return []

    icon_dir = get_library_path()
    pcoll = preview_collections["object_categories"]
    return utils_library.get_folder_enum_previews(icon_dir,pcoll)

def enum_object_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(get_library_path(),self.object_category)
    pcoll = preview_collections["object_items"]
    return utils_library.get_image_enum_previews(icon_dir,pcoll)

def update_object_category(self,context):
    if preview_collections["object_items"]:
        bpy.utils.previews.remove(preview_collections["object_items"])
        preview_collections["object_items"] = utils_library.create_image_preview_collection()
        
    enum_object_names(self,context)

def clear_object_categories(self,context):
    if preview_collections["object_categories"]:
        bpy.utils.previews.remove(preview_collections["object_categories"])
        preview_collections["object_categories"] = utils_library.create_image_preview_collection()

    enum_object_categories(self,context)

class LIBRARY_MT_object_library(bpy.types.Menu):
    bl_label = "Object Library"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        
        layout.operator('library.save_object_to_library',icon='BACK')
        layout.separator()
        layout.operator('library.open_browser_window',icon='FILE_FOLDER').path = get_library_path()
        layout.operator('library.create_new_folder',icon='NEWFOLDER').path = get_library_path()        
        layout.operator('library.change_object_library_path',icon='EXTERNAL_DATA')
        
class LIBRARY_OT_change_object_library_path(bpy.types.Operator):
    bl_idname = "library.change_object_library_path"
    bl_label = "Change Object Library Path"

    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    
    def draw(self, context):
        pass

    def invoke(self, context, event):
        wm = context.window_manager
        if os.path.exists(get_library_path()):
            self.directory = get_library_path()
        wm.fileselect_add(self)      
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if os.path.exists(self.directory):
            wm = context.window_manager
            wm.bp_lib.object_library_path = self.directory
            clear_object_categories(self,context)
        return {'FINISHED'}

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
        wm = context.window_manager
        wm_props = wm.bp_lib
        if self.object_category != "":
            wm_props.object_category = self.object_category
        return True

    def invoke(self,context,event):
        clear_object_categories(self,context)
        update_object_category(self,context)
        wm = context.window_manager
        wm_props = wm.bp_lib
        if wm_props.object_category != "":
            self.object_category = wm_props.object_category              
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
        object_file_path = os.path.join(get_library_path() ,self.object_category,self.object_name + ".blend")
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
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select = True        
        context.area.tag_redraw()
        return {'FINISHED'}

class LIBRARY_OT_save_object_to_library(bpy.types.Operator):
    bl_idname = "library.save_object_to_library"
    bl_label = "Save Object to Library"
    
    obj_name = bpy.props.StringProperty(name="Obj Name")
    object_category = bpy.props.EnumProperty(name="Object Category",items=enum_object_categories,update=update_object_category)
    
    obj = None
    
    @classmethod
    def poll(cls, context):
        if context.scene.outliner.selected_object_index + 1 <= len(context.scene.objects):
            return True
        else:
            return False

    def check(self, context):
        return True

    def invoke(self,context,event):
        clear_object_categories(self,context)
        self.obj_name = context.active_object.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout
        path = os.path.join(get_library_path() ,self.object_category) 
        files = os.listdir(path)

        layout.label("Select folder to save object to")
        layout.prop(self,'object_category',text="",icon='FILE_FOLDER')
        layout.label("Name: " + self.obj_name)
        if self.obj_name + ".blend" in files or self.obj_name + ".png" in files:
            layout.label("File already exists",icon="ERROR")        
        
    def create_object_thumbnail_script(self,source_dir,source_file,object_name):
        file = open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w')
        file.write("import bpy\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for obj in data_from.objects:\n")
        file.write("        if obj == '" + object_name + "':\n")
        file.write("            data_to.objects = [obj]\n")
        file.write("            break\n")
        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.scene.objects.link(obj)\n")
        file.write("    obj.select = True\n")
        file.write("    if obj.type == 'CURVE':\n")
        file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
        file.write("        obj.data.dimensions = '2D'\n")
        file.write("    bpy.context.scene.objects.active = obj\n")
        file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,object_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_object_save_script(self,source_dir,source_file,object_name):
        file = open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("bpy.context.user_preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for obj in data_from.objects:\n")
        file.write("        if obj == '" + object_name + "':\n")
        file.write("            data_to.objects = [obj]\n")
        file.write("            break\n")
        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.scene.objects.link(obj)\n")
        file.write("    obj.select = True\n")
        file.write("    if obj.type == 'CURVE':\n")
        file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
        file.write("        obj.data.dimensions = '2D'\n")
        file.write("    bpy.context.scene.objects.active = obj\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,object_name) + ".blend')\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'save_temp.py')        
        
    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
        
        obj_to_save = context.scene.objects[context.scene.outliner.selected_object_index]
        directory_to_save_to = os.path.join(get_library_path() ,self.object_category) 
        
        thumbnail_script_path = self.create_object_thumbnail_script(directory_to_save_to, bpy.data.filepath, obj_to_save.name)
        save_script_path = self.create_object_save_script(directory_to_save_to, bpy.data.filepath, obj_to_save.name)

#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        subprocess.call(bpy.app.binary_path + ' "' + utils_library.get_thumbnail_file_path() + '" -b --python "' + thumbnail_script_path + '"')   
        subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(LIBRARY_MT_object_library)
    bpy.utils.register_class(LIBRARY_OT_add_object_from_library)
    bpy.utils.register_class(LIBRARY_OT_save_object_to_library)
    bpy.utils.register_class(LIBRARY_OT_change_object_library_path)
    
def unregister():
    bpy.utils.unregister_class(LIBRARY_MT_object_library)
    bpy.utils.unregister_class(LIBRARY_OT_add_object_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_save_object_to_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_object_library_path)
    