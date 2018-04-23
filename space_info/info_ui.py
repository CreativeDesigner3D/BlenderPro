import bpy

class INFO_HT_header(bpy.types.Header):
    bl_space_type = 'INFO'

    def draw(self, context):
        layout = self.layout

        window = context.window
        scene = context.scene
        rd = scene.render

        row = layout.row(align=True)
        row.template_header()
        INFO_MT_menus.draw_collapsible(context, layout)
        if window.screen.show_fullscreen:
            layout.operator("screen.back_to_previous", icon='SCREEN_BACK', text="Back to Previous")
            layout.separator()
        layout.separator()
        if context.active_object:
            if context.active_object.mode == 'EDIT':
                layout.label('You are currently in Edit Mode type the TAB key to return to object mode',icon='ERROR')

        layout.template_running_jobs()

        layout.template_reports_banner()

        row = layout.row(align=True)

        if bpy.app.autoexec_fail is True and bpy.app.autoexec_fail_quiet is False:
            layout.operator_context = 'EXEC_DEFAULT'
            row.label("Auto-run disabled: %s" % bpy.app.autoexec_fail_message, icon='ERROR')
            if bpy.data.is_saved:
                props = row.operator("wm.open_mainfile", icon='SCREEN_BACK', text="Reload Trusted")
                props.filepath = bpy.data.filepath
                props.use_scripts = True

            row.operator("script.autoexec_warn_clear", text="Ignore")
            return   
        
        box = row.box()
        tab_row = box.row(align=True)
        for screen in bpy.data.screens:
            icon = 'FILE_TICK'
            icon = 'LAYER_USED'
            icon = 'LAYER_ACTIVE'
            if screen.name == context.window.screen.name:
                icon='FILE_TICK'
            else:
                icon='LAYER_USED'
            tab_row.operator('info.change_interface',text=screen.name,icon=icon).interface_name = screen.name
            
        row.label(text=scene.statistics(), translate=False)
        
            
            
class INFO_MT_menus(bpy.types.Menu):
    bl_idname = "INFO_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("INFO_MT_file",icon='FILE_FOLDER',text="   File   ")
        layout.menu("INFO_MT_edit",icon='RECOVER_AUTO',text="   Edit   ")
        layout.menu("INFO_MT_rendering",icon='RENDER_STILL',text="   Render    ")
        layout.menu("INFO_MT_help",icon='HELP',text="   Help   ")
        

class INFO_MT_file(bpy.types.Menu):
    bl_label = "File"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.read_homefile", text="New", icon='NEW')
        layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER').load_ui = False
        layout.menu("INFO_MT_file_open_recent", icon='OPEN_RECENT')
        layout.operator("wm.recover_last_session", icon='RECOVER_LAST')
        layout.operator("wm.recover_auto_save", text="Recover Auto Save...", icon='RECOVER_AUTO')

        layout.separator()

        layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
        layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_as_mainfile", text="Save As...", icon='SAVE_AS')
        
        layout.separator()

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.link", text="Link", icon='LINK_BLEND')
        layout.operator("wm.append", text="Append", icon='APPEND_BLEND')

        layout.separator()

        layout.operator("screen.userpref_show", text="User Preferences...", icon='PREFERENCES')
        layout.separator()
        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_homefile", icon='SAVE_PREFS')
        layout.operator("wm.read_factory_settings", icon='LOAD_FACTORY')

        layout.separator()

        layout.menu("INFO_MT_file_import", icon='IMPORT')
        layout.menu("INFO_MT_file_export", icon='EXPORT')
        
        layout.separator()
    
        if any(bpy.utils.app_template_paths()):
            app_template = context.user_preferences.app_template
            if app_template:
                layout.operator(
                    "wm.read_factory_settings",
                    text="Load Factory Template Settings",
                    icon='LOAD_FACTORY',
                ).app_template = app_template
            del app_template
        
        layout.menu("USERPREF_MT_app_templates", icon='FILE_BLEND')        
        
        layout.separator()

        layout.menu("INFO_MT_file_external_data", icon='EXTERNAL_DATA')

        layout.separator()

        layout.operator_context = 'EXEC_AREA'
        layout.operator("wm.quit_blender", text="Quit", icon='QUIT')
        
class INFO_MT_edit(bpy.types.Menu):
    bl_idname = "INFO_MT_edit"
    bl_label = "Edit"

    def draw(self, context):
        layout = self.layout
        layout.operator("ed.undo",icon='LOOP_BACK')
        layout.operator("ed.redo",icon='LOOP_FORWARDS')
        layout.operator("ed.undo_history",icon='RECOVER_LAST') 
        layout.separator()
        layout.menu("INFO_MT_interface",icon='SPLITSCREEN',text="Interface")       
        
class INFO_MT_rendering(bpy.types.Menu):
    bl_label = "Rendering"

    def draw(self, context):
        layout = self.layout
        layout.operator("render.render", text="Render Image", icon='RENDER_STILL').use_viewport = True
        layout.operator("render.opengl", text="Render OpenGL")
        layout.separator()
        layout.operator("info.render_settings",text="Render Settings",icon='INFO')        
        
class INFO_MT_interface(bpy.types.Menu):
    bl_space_type = 'VIEW3D_MT_interface'
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        for screen in bpy.data.screens:
            icon = 'FILE_TICK'
            icon = 'LAYER_USED'
            icon = 'LAYER_ACTIVE'
            if screen.name == context.window.screen.name:
                icon='FILE_TICK'
            else:
                icon='LAYER_USED'
            layout.operator('info.change_interface',text=screen.name,icon=icon).interface_name = screen.name
            
        layout.separator()
        layout.operator('info.copy_current_interface',icon='GHOST')    
        layout.operator('info.delete_current_interface',icon='X')  

def register():
    
    bpy.utils.register_class(INFO_HT_header)
    bpy.utils.register_class(INFO_MT_menus)
    bpy.utils.register_class(INFO_MT_file)
    bpy.utils.register_class(INFO_MT_edit)
    bpy.utils.register_class(INFO_MT_rendering)
    bpy.utils.register_class(INFO_MT_interface)
    
def unregister():
    pass        