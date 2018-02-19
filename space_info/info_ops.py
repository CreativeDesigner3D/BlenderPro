import bpy
        
class OPS_render_settings(bpy.types.Operator): 
    bl_idname = "info.render_settings"
    bl_label = "Render Settings"
    
    room_builder_tabs = bpy.props.EnumProperty(name="Room Builder Tabs",
        items=[('MAIN',"Main Settings","Displays the Main Rendering Options"),
               ('LIGHTING',"Lighting","Library of Room Assets"),
               ('2D',"2D Views","Creates 2D Views For your Room")],
        default='MAIN')    
    
    def execute(self, context):
        return {'FINISHED'}
    
    def check(self,context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        rd = scene.render
        cycles = scene.cycles
        image_settings = rd.image_settings

        box = layout.box()
        row = box.row(align=True)
        if rd.has_multiple_engines:
            row.prop(rd, "engine", text="Rendering Engine")               
        
        row = box.row()
        row.prop(cycles, "device", text="CPU")
        
        row = box.row(align=True)
        row.label(text="Render Size:",icon='STICKY_UVS_VERT')        
        row.prop(rd, "resolution_x", text="X")
        row.prop(rd, "resolution_y", text="Y")
        row = box.row(align=True)
        row.label("Resolution Percentage:")
        row.prop(rd, "resolution_percentage", text="")
        
        row = box.row()
        row.label(text="Rendering Quality:",icon='IMAGE_COL')
        row.prop(scene.cycles,"samples",text='Passes')
        row = box.row()
        row.label(text="Image Format:",icon='IMAGE_DATA')
        row.prop(image_settings,"file_format",text="")
        row = box.row()
        row.label(text="Display Mode:",icon='RENDER_RESULT')
        row.prop(rd,"display_mode",text="")
        row = box.row()
        row.label(text="Use Transparent Film:",icon='SEQUENCE')
        row.prop(scene.cycles,"film_transparent",text='')

        row = box.row()
        row.prop(rd, "use_freestyle", text="Use Freestyle")       
        if rd.use_freestyle: 
            rl = rd.layers.active
            if len(rl.freestyle_settings.linesets) > 0:
                linestyle = rl.freestyle_settings.linesets[0].linestyle            
                row = box.row()
                row.prop(linestyle, "color", text="Line Color")
                row = box.row()
                row.prop(bpy.data.worlds[0], "horizon_color", text="Background Color")        
        
class OPS_reload_blender_pro(bpy.types.Operator): 
    bl_idname = "info.reload_blender_pro"
    bl_label = "Reload Blender Pro"
    bl_description = "Reloads Blender Pro Modules"
    
    def execute(self, context):
        from .. import space_view3d
#         from .. import space_info
#         from .. import library

        space_view3d.register()
#         space_info.register()
#         library.register()
        return {'FINISHED'}        
        
class OPS_change_interface(bpy.types.Operator): 
    bl_idname = "info.change_interface"
    bl_label = "Change Interface"
    bl_description = "Select to change active interface layout"
    
    interface_name = bpy.props.StringProperty(name="Interface Name",default = "New Interface")
    
    def execute(self, context):
        context.window.screen = bpy.data.screens[self.interface_name]
        return {'FINISHED'}
        
class OPS_duplicate_current_interface(bpy.types.Operator): 
    bl_idname = "info.copy_current_interface"
    bl_label = "Duplicate Current Interface"
    bl_description = "This will copy the active interface layout"
    
    interface_name = bpy.props.StringProperty(name="Interface Name",default = "New Interface")
    
    def execute(self, context):
        bpy.ops.screen.new()
        context.window.screen.name = self.interface_name
        # screen.new() doesn't set screen to be active
        # manually have to clean up blenders renaming
        for screen in bpy.data.screens:
            screen.name = screen.name.replace(".001","")
        bpy.ops.info.change_interface(interface_name = self.interface_name)
        return {'FINISHED'}
    
    def check(self,context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label("Enter a name for the new interface")
        layout.prop(self,'interface_name')
   
class OPS_delete_current_interface(bpy.types.Operator): 
    bl_idname = "info.delete_current_interface"
    bl_label = "Delete Current Interface"
    bl_description = "This will delete the active interface layout"
    
    def execute(self, context):
        bpy.ops.screen.delete()
        return {'FINISHED'}
    
    def check(self,context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the active interface layout")
        layout.label("Active Interface Layout: " + context.window.screen.name)
        
def register():
    
    bpy.utils.register_class(OPS_render_settings)
    bpy.utils.register_class(OPS_reload_blender_pro)
    bpy.utils.register_class(OPS_change_interface)
    bpy.utils.register_class(OPS_duplicate_current_interface)
    bpy.utils.register_class(OPS_delete_current_interface)
    
def unregister():
    pass        