import bpy
import os
import subprocess
from ..bp_lib import utils
from . import utils_library

MATERIAL_FOLDER = os.path.join(utils_library.LIBRARY_FOLDER,"materials")
preview_collections = {}
preview_collections["material_categories"] = utils_library.create_image_preview_collection()
preview_collections["material_items"] = utils_library.create_image_preview_collection()

def get_library_path():
    props = utils_library.get_wm_props()
    if os.path.exists(props.material_library_path):
        return props.material_library_path
    else:
        return MATERIAL_FOLDER
    
def enum_material_categories(self,context):
    if context is None:
        return []
    
    icon_dir = get_library_path()
    pcoll = preview_collections["material_categories"]
    return utils_library.get_folder_enum_previews(icon_dir,pcoll)

def enum_material_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(get_library_path(),self.material_category)
    pcoll = preview_collections["material_items"]
    return utils_library.get_image_enum_previews(icon_dir,pcoll)

def update_material_category(self,context):
    if preview_collections["material_items"]:
        bpy.utils.previews.remove(preview_collections["material_items"])
        preview_collections["material_items"] = utils_library.create_image_preview_collection()     
        
    enum_material_names(self,context)

def clear_material_categories(self,context):
    if preview_collections["material_categories"]:
        bpy.utils.previews.remove(preview_collections["material_categories"])
        preview_collections["material_categories"] = utils_library.create_image_preview_collection()

    enum_material_categories(self,context)

class LIBRARY_MT_material_library(bpy.types.Menu):
    bl_label = "Material Library"

    def draw(self, context):
        layout = self.layout
        layout.operator('library.save_material_to_library',icon='BACK')
        layout.separator()
        layout.operator('library.open_browser_window',icon='FILE_FOLDER').path = get_library_path()
        layout.operator('library.create_new_folder',icon='NEWFOLDER').path = get_library_path()        
        layout.operator('library.change_material_library_path',icon='EXTERNAL_DATA')     
        
class LIBRARY_OT_change_material_library_path(bpy.types.Operator):
    bl_idname = "library.change_material_library_path"
    bl_label = "Change Material Library Path"
    
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
            wm.bp_lib.material_library_path = self.directory
            clear_material_categories(self,context)
        return {'FINISHED'}

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
        wm = context.window_manager
        wm_props = wm.bp_lib
        if self.material_category != "":
            wm_props.material_category = self.material_category           
        return True

    def invoke(self,context,event):
        update_material_category(self,context)
        wm = context.window_manager
        wm_props = wm.bp_lib
        if wm_props.material_category != "":
            self.material_category = wm_props.material_category        
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
        material_file_path = os.path.join(get_library_path() ,self.material_category,self.material_name + ".blend")
        with bpy.data.libraries.load(material_file_path, False, False) as (data_from, data_to):
            
            for mat in data_from.materials:
                data_to.materials = [mat]
                break
            
        for mat in data_to.materials:
            return mat
    
    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = utils.get_selection_point(context,event)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select = True
            context.scene.objects.active = selected_obj
        
            if self.event_is_place_material(event):
                if len(selected_obj.data.uv_textures) == 0:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT') 
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)  
                    bpy.ops.object.editmode_toggle()

                if len(selected_obj.material_slots) == 0:
                    bpy.ops.object.material_slot_add()

                if len(selected_obj.material_slots) > 1:
                    bpy.ops.library.assign_material_dialog('INVOKE_DEFAULT',material_name = self.mat.name, object_name = selected_obj.name)
                    return self.finish(context)
                else:
                    for slot in selected_obj.material_slots:
                        slot.material = self.mat                  
                        
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
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}
    
class LIBRARY_OT_assign_material(bpy.types.Operator):
    bl_idname = "library.assign_material"
    bl_label = "Assign Material"
    
    obj_name = bpy.props.StringProperty(name="Obj Name")
    material_category = bpy.props.EnumProperty(name="Material Category",items=enum_material_categories,update=update_material_category)
    material_name = bpy.props.EnumProperty(name="Material Name",items=enum_material_names)
    
    drawing_plane = None
    mat = None
    
    @classmethod
    def poll(cls, context):
        if context.scene.outliner.selected_material_index + 1 <= len(bpy.data.materials):
            return True
        else:
            return False

    def check(self, context):
        return True
        
    def execute(self, context):
        self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def get_material(self,context):
        return bpy.data.materials[context.scene.outliner.selected_material_index]
    
    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj = utils.get_selection_point(context,event)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select = True
            context.scene.objects.active = selected_obj
            
            if self.event_is_place_material(event):
                if len(selected_obj.data.uv_textures) == 0:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT') 
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)  
                    bpy.ops.object.editmode_toggle()
                    
                if len(selected_obj.material_slots) == 0:
                    bpy.ops.object.material_slot_add()
                    
                if len(selected_obj.material_slots) > 1:
                    bpy.ops.library.assign_material_dialog('INVOKE_DEFAULT',material_name = self.mat.name, object_name = selected_obj.name)
                    return self.finish(context)
                else:        
                    for slot in selected_obj.material_slots:
                        slot.material = self.mat                  
                        
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
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}    
    
class LIBRARY_OT_save_material_to_library(bpy.types.Operator):
    bl_idname = "library.save_material_to_library"
    bl_label = "Save Material to Library"
    
    mat_name = bpy.props.StringProperty(name="Material Name")
    material_category = bpy.props.EnumProperty(name="Material Category",items=enum_material_categories,update=update_material_category)
    save_file = bpy.props.BoolProperty(name="Save File")
    create_new_category = bpy.props.BoolProperty(name="Create New Category")
    new_category_name = bpy.props.StringProperty(name="New Category Name")
        
    @classmethod
    def poll(cls, context):
        if context.scene.outliner.selected_material_index + 1 <= len(bpy.data.materials):
            return True
        else:
            return False

    def check(self, context):     
        return True

    def invoke(self,context,event):
        mat = bpy.data.materials[context.scene.outliner.selected_material_index]
        self.mat_name = mat.name
        clear_material_categories(self,context)
        wm = context.window_manager

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def create_material_thumbnail_script(self,source_dir,source_file,material_name):
        file = open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w')
        file.write("import bpy\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for mat in data_from.materials:\n")
        file.write("        if mat == '" + material_name + "':\n")
        file.write("            data_to.materials = [mat]\n")
        file.write("            break\n")
        file.write("for mat in data_to.materials:\n")
        file.write("    bpy.ops.mesh.primitive_cube_add()\n")
        file.write("    obj = bpy.context.scene.objects.active\n")
        file.write("    bpy.ops.object.shade_smooth()\n")
        file.write("    obj.dimensions = (2,2,2)\n")
        file.write("    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)\n")
        file.write("    mod = obj.modifiers.new('bevel','BEVEL')\n")
        file.write("    mod.segments = 5\n")
        file.write("    mod.width = .05\n")
        file.write("    bpy.ops.object.modifier_apply(modifier='bevel')\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.mesh.select_all(action='SELECT')\n")
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.object.material_slot_add()\n")
        file.write("    for slot in obj.material_slots:\n")
        file.write("        slot.material = mat\n")
        file.write("    bpy.context.scene.objects.active = obj\n")
        file.write("    bpy.ops.view3d.camera_to_view_selected()\n")
        file.write("    render = bpy.context.scene.render\n")
        file.write("    render.use_file_extension = True\n")
        file.write("    render.filepath = r'" + os.path.join(source_dir,material_name) + "'\n")
        file.write("    bpy.ops.render.render(write_still=True)\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_material_save_script(self,source_dir,source_file,material_name):
        file = open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w')
        file.write("import bpy\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for mat in data_from.materials:\n")
        file.write("        if mat == '" + material_name + "':\n")
        file.write("            data_to.materials = [mat]\n")
        file.write("            break\n")
        file.write("for mat in data_to.materials:\n")
        file.write("    bpy.ops.mesh.primitive_cube_add()\n")
        file.write("    obj = bpy.context.scene.objects.active\n")
        file.write("    bpy.ops.object.shade_smooth()\n")
        file.write("    obj.dimensions = (2,2,2)\n")
        file.write("    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)\n")
        file.write("    mod = obj.modifiers.new('bevel','BEVEL')\n")
        file.write("    mod.segments = 5\n")
        file.write("    mod.width = .05\n")
        file.write("    bpy.ops.object.modifier_apply(modifier='bevel')\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.mesh.select_all(action='SELECT')\n")
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.object.material_slot_add()\n")
        file.write("    for slot in obj.material_slots:\n")
        file.write("        slot.material = mat\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,material_name) + ".blend')\n")
        file.close()
        
        return os.path.join(bpy.app.tempdir,'save_temp.py')
        
    def draw(self, context):
        layout = self.layout
        path = os.path.join(get_library_path() ,self.material_category) 
        files = os.listdir(path)        
        layout.label("Select folder to save material to")
        layout.prop(self,'material_category',text="",icon='FILE_FOLDER')
        layout.label("Name: " + self.mat_name)
        if self.mat_name + ".blend" in files or self.mat_name + ".png" in files:
            layout.label("File already exists",icon="ERROR")           
        
    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
        
        mat_to_save = bpy.data.materials[context.scene.outliner.selected_material_index]
        directory_to_save_to = os.path.join(get_library_path() ,self.material_category)
        
        thumbnail_script_path = self.create_material_thumbnail_script(directory_to_save_to, bpy.data.filepath, mat_to_save.name)
        save_script_path = self.create_material_save_script(directory_to_save_to, bpy.data.filepath, mat_to_save.name)
        
#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        subprocess.call(bpy.app.binary_path + ' "' + utils_library.get_thumbnail_file_path() + '" -b --python "' + thumbnail_script_path + '"')   
        subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        return {'FINISHED'}
        
class LIBRARY_OT_assign_material_dialog(bpy.types.Operator):
    bl_idname = "library.assign_material_dialog"
    bl_label = "Assign Material Dialog"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name = bpy.props.StringProperty(name="Material Name")
    object_name = bpy.props.StringProperty(name="Object Name")
    
    obj = None
    material = None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        self.material = bpy.data.materials[self.material_name]
        self.obj = bpy.data.objects[self.object_name]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)
        
    def draw(self,context):
        layout = self.layout
        layout.label(self.obj.name,icon='OBJECT_DATA')
        for index, mat_slot in enumerate(self.obj.material_slots):
            row = layout.split(percentage=.55)
            if mat_slot.name == "":
                row.label('No Material')
            else:
                row.prop(mat_slot,"name",text="",icon='MATERIAL')
#                 row.prop(mat_slot,"name",text=self.obj.cabinetlib.material_slots[index].name if len(self.obj.cabinetlib.material_slots) >= index+1 else "")
            props = row.operator('library.assign_material_to_slot',text="Assign",icon='BACK')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index
        
            props = row.operator('library.replace_all_materials',text="Replace All",icon='FILE_REFRESH')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index
        
    def execute(self,context):
        return {'FINISHED'}        
        
class LIBRARY_OT_assign_material_to_slot(bpy.types.Operator):
    bl_idname = "library.assign_material_to_slot"
    bl_label = "Assign Material to Slot"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name = bpy.props.StringProperty(name="Material Name")
    object_name = bpy.props.StringProperty(name="Object Name")
    
    index = bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        obj.material_slots[self.index].material = mat
        return {'FINISHED'}
        
class LIBRARY_OT_replace_all_materials(bpy.types.Operator):
    bl_idname = "library.replace_all_materials"
    bl_label = "Assign Material to Slot"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name = bpy.props.StringProperty(name="Material Name")
    object_name = bpy.props.StringProperty(name="Object Name")
    
    index = bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        mat_to_replace = obj.material_slots[self.index].material
        obj.material_slots[self.index].material = mat
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                if slot.material == mat_to_replace:
                    slot.material = mat
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(LIBRARY_MT_material_library)
    bpy.utils.register_class(LIBRARY_OT_add_material_from_library)
    bpy.utils.register_class(LIBRARY_OT_save_material_to_library)
    bpy.utils.register_class(LIBRARY_OT_change_material_library_path)
    bpy.utils.register_class(LIBRARY_OT_assign_material)
    bpy.utils.register_class(LIBRARY_OT_assign_material_dialog)
    bpy.utils.register_class(LIBRARY_OT_assign_material_to_slot)
    bpy.utils.register_class(LIBRARY_OT_replace_all_materials)
    
    
def unregister():
    bpy.utils.unregister_class(LIBRARY_MT_material_library)
    bpy.utils.unregister_class(LIBRARY_OT_add_material_from_library)
    bpy.utils.unregister_class(LIBRARY_OT_save_material_to_library)
    bpy.utils.unregister_class(LIBRARY_OT_change_material_library_path)
    bpy.utils.unregister_class(LIBRARY_OT_assign_material)
    bpy.utils.unregister_class(LIBRARY_OT_assign_material_dialog)
    bpy.utils.unregister_class(LIBRARY_OT_assign_material_to_slot)
    bpy.utils.unregister_class(LIBRARY_OT_replace_all_materials)
    