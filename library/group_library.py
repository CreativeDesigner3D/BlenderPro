import bpy
import os
import subprocess
from ..bp_lib import utils
from . import utils_library

GROUP_FOLDER = os.path.join(utils_library.LIBRARY_FOLDER,"groups")
preview_collections = {}
preview_collections["group_categories"] = utils_library.create_image_preview_collection()
preview_collections["group_items"] = utils_library.create_image_preview_collection()

def get_library_path():
    props = utils_library.get_wm_props()
    if os.path.exists(props.group_library_path):
        return props.group_library_path
    else:
        return GROUP_FOLDER
    
def enum_group_categories(self,context):
    if context is None:
        return []
    
    icon_dir = get_library_path()
    pcoll = preview_collections["group_categories"]
    return utils_library.get_folder_enum_previews(icon_dir,pcoll)

def enum_group_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(get_library_path(),self.group_category)
    pcoll = preview_collections["group_items"]
    return utils_library.get_image_enum_previews(icon_dir,pcoll)

def update_group_category(self,context):
    if preview_collections["group_items"]:
        bpy.utils.previews.remove(preview_collections["group_items"])
        preview_collections["group_items"] = utils_library.create_image_preview_collection()     
        
    enum_group_names(self,context)

def clear_group_categories(self,context):
    if preview_collections["group_categories"]:
        bpy.utils.previews.remove(preview_collections["group_categories"])
        preview_collections["group_categories"] = utils_library.create_image_preview_collection()

    enum_group_categories(self,context)

class LIBRARY_MT_group_library(bpy.types.Menu):
    bl_label = "Group Library"

    def draw(self, context):
        layout = self.layout
        layout.operator('library.save_group_to_library',icon='BACK')
        layout.separator()
        layout.operator('library.open_browser_window',icon='FILE_FOLDER').path = get_library_path()
        layout.operator('library.create_new_folder',icon='NEWFOLDER').path = get_library_path()        
        layout.operator('library.change_group_library_path',icon='EXTERNAL_DATA')        

class LIBRARY_OT_change_group_library_path(bpy.types.Operator):
    bl_idname = "library.change_group_library_path"
    bl_label = "Change Group Library Path"

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
            wm.bp_lib.group_library_path = self.directory
            clear_group_categories(self,context)
        return {'FINISHED'}

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
        wm = context.window_manager
        wm_props = wm.bp_lib
        if self.group_category != "":
            wm_props.group_category = self.group_category
        return True

    def invoke(self,context,event):
        self.parent_objects = []
        self.group_objects = []
        update_group_category(self,context)
        wm = context.window_manager
        wm_props = wm.bp_lib
        if wm_props.group_category != "":
            self.group_category = wm_props.group_category
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
        group_file_path = os.path.join(get_library_path() ,self.group_category,self.group_name + ".blend")
        with bpy.data.libraries.load(group_file_path, False, False) as (data_from, data_to):
            
            for grp in data_from.groups:
                if grp == self.group_name:
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
        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.parent_objects:
            obj.select = True
        #SELECT BASE POINTS
        context.area.tag_redraw()
        return {'FINISHED'}
    
class LIBRARY_OT_save_group_to_library(bpy.types.Operator):
    bl_idname = "library.save_group_to_library"
    bl_label = "Save Group to Library"
    
    grp_name = bpy.props.StringProperty(name="Group Name")
    group_category = bpy.props.EnumProperty(name="Object Category",items=enum_group_categories,update=update_group_category)
    save_file = bpy.props.BoolProperty(name="Save File")
    create_new_category = bpy.props.BoolProperty(name="Create New Category")
    new_category_name = bpy.props.StringProperty(name="New Category Name")
    
    @classmethod
    def poll(cls, context):
        if context.scene.outliner.selected_group_index + 1 <= len(bpy.data.groups):
            return True
        else:
            return False

    def check(self, context):
        return True

    def create_group_thumbnail_script(self,source_dir,source_file,group_name):
        file = open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w')
        file.write("import bpy\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for grp in data_from.groups:\n")
        file.write("        if grp == '" + group_name + "':\n")
        file.write("            data_to.groups = [grp]\n")
        file.write("            break\n")
        file.write("for grp in data_to.groups:\n")
        file.write("    for obj in grp.objects:\n")
        file.write("        bpy.context.scene.objects.link(obj)\n")
        file.write("        obj.select = True\n")
        file.write("        bpy.context.scene.objects.active = obj\n")
        file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,group_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_group_save_script(self,source_dir,source_file,group_name):
        file = open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.user_preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for grp in data_from.groups:\n")
        file.write("        if grp == '" + group_name + "':\n")
        file.write("            data_to.groups = [grp]\n")
        file.write("            break\n")
        file.write("for grp in data_to.groups:\n")
        file.write("    for obj in grp.objects:\n")
        file.write("        bpy.context.scene.objects.link(obj)\n")
        file.write("        obj.select = True\n")
        file.write("        bpy.context.scene.objects.active = obj\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,group_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def invoke(self,context,event):
        grp = bpy.data.groups[context.scene.outliner.selected_group_index]
        self.grp_name = grp.name
        clear_group_categories(self,context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self, context):
        layout = self.layout
        path = os.path.join(get_library_path() ,self.group_category) 
        files = os.listdir(path)
        if self.create_new_category:
            row = layout.split(percentage=.6)
            row.label("Enter new folder name:",icon='FILE_FOLDER')
            row.prop(self,'create_new_category',text="Create New")
            layout.prop(self,'new_category_name',text="",icon='FILE_FOLDER')
        else:
            row = layout.split(percentage=.6)
            row.label("Select folder to save to:",icon='FILE_FOLDER')
            row.prop(self,'create_new_category',text="Create New")
            layout.prop(self,'group_category',text="",icon='FILE_FOLDER')
        layout.label("Name: " + self.grp_name)
        if self.grp_name + ".blend" in files or self.grp_name + ".png" in files:
            layout.label("File already exists",icon="ERROR")  
        if bpy.data.filepath != "" and bpy.data.is_dirty:
            row = layout.split(percentage=.6)
            row.label("File is not saved",icon="ERROR")
            row.prop(self,'save_file',text="Auto Save")
        
    def execute(self, context):
        
        grp_to_save = bpy.data.groups[context.scene.outliner.selected_group_index]
        directory_to_save_to = os.path.join(get_library_path() ,self.group_category) 
        
        thumbnail_script_path = self.create_group_thumbnail_script(directory_to_save_to, bpy.data.filepath, grp_to_save.name)
        save_script_path = self.create_group_save_script(directory_to_save_to, bpy.data.filepath, grp_to_save.name)

        if not os.path.exists(bpy.app.tempdir):
            os.makedirs(bpy.app.tempdir)

#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        subprocess.call(bpy.app.binary_path + ' "' + utils_library.get_thumbnail_file_path() + '" -b --python "' + thumbnail_script_path + '"')   
        subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)        
        
        return {'FINISHED'}    
    
def register():
    bpy.utils.register_class(LIBRARY_MT_group_library)
    bpy.utils.register_class(LIBRARY_OT_add_group_from_library)
    bpy.utils.register_class(LIBRARY_OT_save_group_to_library)
    bpy.utils.register_class(LIBRARY_OT_change_group_library_path)

def unregister():
    bpy.utils.unregister_class(LIBRARY_MT_group_library)
    bpy.utils.unregister_class(LIBRARY_OT_add_group_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_save_group_to_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_group_library_path)
    