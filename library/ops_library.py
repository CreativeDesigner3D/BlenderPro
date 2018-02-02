import bpy
from ..bp_lib import unit
import os

class OPS_open_browser_window(bpy.types.Operator):
    bl_idname = "library.open_browser_window"
    bl_label = "Open Browser Window"
    bl_description = "This will open the path that is passed in a file browser"

    path = bpy.props.StringProperty(name="Message",default="Error")

    def execute(self, context):
        import subprocess
        if 'Windows' in str(bpy.app.build_platform):
            subprocess.Popen(r'explorer ' + self.path)
        elif 'Darwin' in str(bpy.app.build_platform):
            subprocess.Popen(['open' , os.path.normpath(self.path)])
        else:
            subprocess.Popen(['xdg-open' , os.path.normpath(self.path)])
        return {'FINISHED'}
    
class LIBRARY_OT_create_new_folder(bpy.types.Operator):
    bl_idname = "library.create_new_folder"
    bl_label = "Create New Folder"
    
    path = bpy.props.StringProperty(name="Path",description="Path to Add Folder to To")
    folder_name = bpy.props.StringProperty(name="Folder Name",description="Folder Name to Create")

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        layout.label("Enter the Category Name to Add")
        layout.prop(self,'folder_name',icon='FILE_FOLDER')

    def execute(self, context):
        path = os.path.join(self.path, self.folder_name)
    
        if not os.path.exists(path):
            os.makedirs(path)
            
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(LIBRARY_OT_create_new_folder)
    bpy.utils.register_class(OPS_open_browser_window)