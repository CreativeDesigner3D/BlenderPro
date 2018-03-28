import bpy
from bl_ui.properties_paint_common import UnifiedPaintPanel

def clear_view3d_properties_shelf():
    if hasattr(bpy.types, 'VIEW3D_PT_grease_pencil'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_grease_pencil)
    if hasattr(bpy.types, 'VIEW3D_PT_grease_pencil_palettecolor'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_grease_pencil_palettecolor)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_properties'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_properties)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_cursor'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_cursor)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_name'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_name)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_display'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_display)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_stereo'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_stereo)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_shading'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_shading)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_motion_tracking'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_motion_tracking)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_meshdisplay'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_meshdisplay)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_meshstatvis'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_meshstatvis)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_curvedisplay'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_curvedisplay)
    if hasattr(bpy.types, 'VIEW3D_PT_background_image'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_background_image)
    if hasattr(bpy.types, 'VIEW3D_PT_transform_orientations'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_transform_orientations)
    if hasattr(bpy.types, 'VIEW3D_PT_etch_a_ton'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_etch_a_ton)
    if hasattr(bpy.types, 'VIEW3D_PT_context_properties'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_context_properties)
    if hasattr(bpy.types, 'VIEW3D_PT_tools_animation'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_animation)
    if hasattr(bpy.types, 'VIEW3D_PT_tools_relations'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_relations)        
    if hasattr(bpy.types, 'VIEW3D_PT_tools_rigid_body'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_rigid_body)   

def clear_view3d_tools_shelf():
    if hasattr(bpy.types, 'VIEW3D_PT_tools_grease_pencil_brush'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_grease_pencil_brush)          
    if hasattr(bpy.types, 'VIEW3D_PT_tools_grease_pencil_draw'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_grease_pencil_draw)      
    if hasattr(bpy.types, 'VIEW3D_PT_tools_add_object'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_add_object)  
    if hasattr(bpy.types, 'VIEW3D_PT_tools_transform'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_transform)            
    if hasattr(bpy.types, 'VIEW3D_PT_tools_object'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_object)            
    if hasattr(bpy.types, 'VIEW3D_PT_tools_history'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_history)

def clear_view3d_header():
    if hasattr(bpy.types, 'VIEW3D_HT_header'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_HT_header)   
    if hasattr(bpy.types, 'INFO_HT_header'):
        bpy.utils.unregister_class(bpy.types.INFO_HT_header)           

def clear_view3d_menus():
    if hasattr(bpy.types, 'VIEW3D_MT_view'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_MT_view)

class VIEW3D_HT_header(bpy.types.Header):
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        layout = self.layout

        obj = context.active_object
        toolsettings = context.tool_settings
        view = context.space_data
        
        row = layout.row(align=True)
        
        row.template_header()
        
        VIEW3D_MT_menus.draw_collapsible(context, layout)
        
        layout.template_header_3D()

        if obj:
            mode = obj.mode
            # Particle edit
            if mode == 'PARTICLE_EDIT':
                layout.prop(toolsettings.particle_edit, "select_mode", text="", expand=True)

            # Occlude geometry
            if ((view.viewport_shade not in {'BOUNDBOX', 'WIREFRAME'} and (mode == 'PARTICLE_EDIT' or (mode == 'EDIT' and obj.type == 'MESH'))) or
                    (mode == 'WEIGHT_PAINT')):
                layout.prop(view, "use_occlude_geometry", text="")

            # Proportional editing
            if context.gpencil_data and context.gpencil_data.use_stroke_edit_mode:
                row = layout.row(align=True)
                row.prop(toolsettings, "proportional_edit", icon_only=True,text="Proportional Edit")
                if toolsettings.proportional_edit != 'DISABLED':
                    row.prop(toolsettings, "proportional_edit_falloff", icon_only=True)
            elif mode in {'EDIT', 'PARTICLE_EDIT'}:
                row = layout.row(align=True)
                row.prop(toolsettings, "proportional_edit", icon_only=True)
                if toolsettings.proportional_edit != 'DISABLED':
                    row.prop(toolsettings, "proportional_edit_falloff", icon_only=True)
            elif mode == 'OBJECT':
                row = layout.row(align=True)
                row.prop(toolsettings, "use_proportional_edit_objects", icon_only=True)
                if toolsettings.use_proportional_edit_objects:
                    row.prop(toolsettings, "proportional_edit_falloff", icon_only=True)
        else:
            # Proportional editing
            if context.gpencil_data and context.gpencil_data.use_stroke_edit_mode:
                row = layout.row(align=True)
                row.prop(toolsettings, "proportional_edit", icon_only=True)
                if toolsettings.proportional_edit != 'DISABLED':
                    row.prop(toolsettings, "proportional_edit_falloff", icon_only=True)

#                     show_snap = False
#                     if obj is None:
#                         show_snap = True
#                     else:
#                         if mode not in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'}:
#                             show_snap = True
#                         else:
#                             paint_settings = UnifiedPaintPanel.paint_settings(context)
#                             if paint_settings:
#                                 brush = paint_settings.brush
#                                 if brush and brush.stroke_method == 'CURVE':
#                                     show_snap = True
    
#             if show_snap:
        snap_element = toolsettings.snap_element
        row = layout.row(align=True)
        row.prop(toolsettings, "use_snap", text="")
        row.prop(toolsettings, "snap_element", icon_only=True)
        if snap_element == 'INCREMENT':
            row.prop(toolsettings, "use_snap_grid_absolute", text="")
        else:
            row.prop(toolsettings, "snap_target", text="")
            if obj:
                if mode == 'EDIT':
                    row.prop(toolsettings, "use_snap_self", text="")
                if mode in {'OBJECT', 'POSE', 'EDIT'} and snap_element != 'VOLUME':
                    row.prop(toolsettings, "use_snap_align_rotation", text="")

        if snap_element == 'VOLUME':
            row.prop(toolsettings, "use_snap_peel_object", text="")
        elif snap_element == 'FACE':
            row.prop(toolsettings, "use_snap_project", text="")

class VIEW3D_MT_menus(bpy.types.Menu):
    bl_space_type = 'VIEW3D_MT_editor_menus'
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("VIEW3D_MT_view",icon='VIEWZOOM',text="   View   ")
        layout.menu("VIEW3D_MT_add_object",icon='GREASEPENCIL',text="   Add   ")
        layout.menu("VIEW3D_MT_tools",icon='MODIFIER',text="   Tools   ")
        

class VIEW3D_MT_view(bpy.types.Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        layout.operator("view3d.toolshelf",icon='MENU_PANEL')
        layout.operator("view3d.properties",icon='MENU_PANEL')
        layout.separator()
        layout.operator("view3d.view_all",icon='VIEWZOOM')
        layout.operator("view3d.view_selected",text="Zoom To Selected",icon='ZOOM_SELECTED')

        layout.separator()

        layout.operator("view3d.navigate",icon='RESTRICT_VIEW_OFF',text="First Person View")
        
        layout.separator()

        layout.operator("view3d.viewnumpad", text="Camera",icon='CAMERA_DATA').type = 'CAMERA'
        layout.operator("view3d.viewnumpad", text="Top",icon='TRIA_DOWN').type = 'TOP'
        layout.operator("view3d.viewnumpad", text="Front",icon='TRIA_UP').type = 'FRONT'
        layout.operator("view3d.viewnumpad", text="Left",icon='TRIA_LEFT').type = 'LEFT'
        layout.operator("view3d.viewnumpad", text="Right",icon='TRIA_RIGHT').type = 'RIGHT'

        layout.separator()

        layout.operator("view3d.view_persportho",icon='SCENE')
        
        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.separator()

        layout.operator("screen.area_dupli",icon='GHOST')
        layout.operator("screen.region_quadview",icon='IMGDISPLAY')
        layout.operator("screen.screen_full_area",icon='FULLSCREEN_ENTER')    
        
        layout.separator()
        
        layout.operator("space_view3d.viewport_options",text="Viewport Settings...",icon='SCRIPTPLUGINS')


class VIEW3D_MT_add_object(bpy.types.Menu):
    bl_label = "Add Object"

    def draw(self, context):
        layout = self.layout

        # note, don't use 'EXEC_SCREEN' or operators wont get the 'v3d' context.

        # Note: was EXEC_AREA, but this context does not have the 'rv3d', which prevents
        #       "align_view" to work on first call (see [#32719]).
        layout.operator_context = 'EXEC_REGION_WIN'

        #layout.operator_menu_enum("object.mesh_add", "type", text="Mesh", icon='OUTLINER_OB_MESH')
        layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')

        #layout.operator_menu_enum("object.curve_add", "type", text="Curve", icon='OUTLINER_OB_CURVE')
        layout.menu("INFO_MT_curve_add", icon='OUTLINER_OB_CURVE')
        #layout.operator_menu_enum("object.surface_add", "type", text="Surface", icon='OUTLINER_OB_SURFACE')
        layout.menu("INFO_MT_surface_add", icon='OUTLINER_OB_SURFACE')
        layout.menu("INFO_MT_metaball_add", text="Metaball", icon='OUTLINER_OB_META')
        layout.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
        layout.separator()

        layout.menu("INFO_MT_armature_add", icon='OUTLINER_OB_ARMATURE')
        layout.operator("object.add", text="Lattice", icon='OUTLINER_OB_LATTICE').type = 'LATTICE'
        layout.operator_menu_enum("object.empty_add", "type", text="Empty", icon='OUTLINER_OB_EMPTY')
        layout.separator()

        layout.operator("object.speaker_add", text="Speaker", icon='OUTLINER_OB_SPEAKER')
        layout.separator()

        layout.operator("view3d.add_camera",text="Camera",icon='OUTLINER_OB_CAMERA')

#         if INFO_MT_camera_add.is_extended():
#             layout.menu("INFO_MT_camera_add", icon='OUTLINER_OB_CAMERA')
#         else:
#             INFO_MT_camera_add.draw(self, context)

        layout.menu("INFO_MT_lamp_add", icon='OUTLINER_OB_LAMP')
        layout.separator()

        layout.operator_menu_enum("object.effector_add", "type", text="Force Field", icon='OUTLINER_OB_FORCE_FIELD')
        layout.separator()

        if len(bpy.data.groups) > 10:
            layout.operator_context = 'INVOKE_REGION_WIN'
            layout.operator("object.group_instance_add", text="Group Instance...", icon='OUTLINER_OB_GROUP_INSTANCE')
        else:
            layout.operator_menu_enum("object.group_instance_add", "group", text="Group Instance", icon='OUTLINER_OB_GROUP_INSTANCE')
                    
#         layout = self.layout
# 
#         # note, don't use 'EXEC_SCREEN' or operators wont get the 'v3d' context.
# 
#         # Note: was EXEC_AREA, but this context does not have the 'rv3d', which prevents
#         #       "align_view" to work on first call (see [#32719]).
#         layout.operator_context = 'INVOKE_REGION_WIN'
#         layout.operator("view3d.draw_mesh", icon='MESH_GRID')
# 
#         layout.operator_context = 'EXEC_REGION_WIN'
#         layout.separator()
#         layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')
# 
#         layout.menu("INFO_MT_curve_add", icon='OUTLINER_OB_CURVE')
#         layout.operator_context = 'EXEC_REGION_WIN'
#         layout.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
#         layout.separator()
# 
#         layout.operator_menu_enum("object.empty_add", "type", text="Empty", icon='OUTLINER_OB_EMPTY')
#         layout.separator()
#         layout.operator("view3d.add_camera",text="Camera",icon='OUTLINER_OB_CAMERA')
#         layout.menu("VIEW3D_MT_add_lamp", icon='OUTLINER_OB_LAMP')
#         layout.separator()
#         
#         if len(bpy.data.groups) > 10:
#             layout.operator_context = 'INVOKE_REGION_WIN'
#             layout.operator("object.group_instance_add", text="Group Instance...", icon='OUTLINER_OB_EMPTY')
#         else:
#             layout.operator_menu_enum("object.group_instance_add", "group", text="Group Instance", icon='OUTLINER_OB_EMPTY')


class VIEW3D_MT_add_lamp(bpy.types.Menu):
    bl_label = "Lamp"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.lamp_add",icon='LAMP_POINT',text="Add Point Lamp").type = 'POINT'
        layout.operator("object.lamp_add",icon='LAMP_SUN',text="Add Sun Lamp").type = 'SUN'
        layout.operator("object.lamp_add",icon='LAMP_SPOT',text="Add Spot Lamp").type = 'SPOT'
        layout.operator("object.lamp_add",icon='LAMP_AREA',text="Add Area Lamp").type = 'AREA'


class VIEW3D_MT_tools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Object"

    def draw(self, context):
        edit_mesh = False
        edit_curve = False 
        
        if context.object and context.object.type == 'MESH' and context.object.mode == 'EDIT':
            edit_mesh = True
        if context.object and context.object.type == 'MESH' and context.object.mode == 'EDIT':
            edit_curve = True      
                  
        layout = self.layout
        layout.menu("VIEW3D_MT_drawing_tools",icon='GREASEPENCIL')
        layout.menu("VIEW3D_MT_objecttools",icon='OBJECT_DATA')
        layout.menu("VIEW3D_MT_cursor_tools",icon='CURSOR')
        layout.menu("VIEW3D_MT_selectiontools",icon='MAN_TRANS')
        row = layout.row()
        row.enabled = edit_mesh
        row.menu("VIEW3D_MT_editmeshtools",icon='EDITMODE_HLT')
        row = layout.row()
        row.enabled = edit_curve        
        row.menu("VIEW3D_MT_editcurvetools",icon='CURVE_BEZCURVE')


class VIEW3D_MT_cursor_tools(bpy.types.Menu):
    bl_label = "Cursor Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator('view3d.set_cursor_location',text="Set Cursor Location...",icon='CURSOR')
        layout.separator()
        layout.operator("view3d.snap_cursor_to_selected",icon='CURSOR')
        layout.operator("view3d.snap_cursor_to_center",icon='GRID')
        layout.operator("view3d.snap_selected_to_cursor",icon='SPACE2')


class VIEW3D_MT_transformtools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Transforms"

    def draw(self, context):
        layout = self.layout
        layout.operator("transform.translate",text='Grab',icon='MAN_TRANS')
        layout.operator("transform.rotate",icon='MAN_ROT')
        layout.operator("transform.resize",text="Scale",icon='MAN_SCALE')


class VIEW3D_MT_selectiontools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Selection Tools"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            if context.active_object.mode == 'OBJECT':
                layout.operator("object.select_all",text='Toggle De/Select',icon='MAN_TRANS')
            else:
                layout.operator("mesh.select_all",text='Toggle De/Select',icon='MAN_TRANS')
        else:
            layout.operator("object.select_all",text='Toggle De/Select',icon='MAN_TRANS')
        layout.operator("view3d.select_border",icon='BORDER_RECT')
        layout.operator("view3d.select_circle",icon='BORDER_LASSO')
        if context.active_object and context.active_object.mode == 'EDIT':    
            layout.separator()
            layout.menu('VIEW3D_MT_mesh_selection',text="Mesh Selection",icon='MAN_TRANS')


class VIEW3D_MT_origintools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Origin Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.origin_set",text="Origin to Cursor",icon='CURSOR').type = 'ORIGIN_CURSOR'
        layout.operator("object.origin_set",text="Origin to Geometry",icon='CLIPUV_HLT').type = 'ORIGIN_GEOMETRY'
        
        
class VIEW3D_MT_shadetools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Object Shading"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.shade_smooth",icon='SOLID')
        layout.operator("object.shade_flat",icon='SNAP_FACE')


class VIEW3D_MT_objecttools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Object Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("transform.translate",text='Grab',icon='MAN_TRANS')
        layout.operator("transform.rotate",icon='MAN_ROT')
        layout.operator("transform.resize",text="Scale",icon='MAN_SCALE')        
        layout.separator()
        layout.operator("object.duplicate_move",icon='PASTEDOWN')
        layout.operator("object.convert", text="Convert to Mesh",icon='MOD_REMESH').target = 'MESH'
        layout.operator("object.join",icon='ROTATECENTER')         
        layout.separator()
        layout.menu("VIEW3D_MT_origintools",icon='SPACE2')
        layout.separator()
        layout.menu("VIEW3D_MT_shadetools",icon='MOD_MULTIRES')
        layout.separator()
        layout.operator("object.delete",icon='X').use_global = False


class VIEW3D_MT_editmeshtools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Edit Mesh Tools"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        layout.operator("view3d.edit_mesh_extrude_move_normal",icon='CURVE_PATH')
        layout.operator("mesh.inset",icon='MOD_MESHDEFORM')
        layout.operator("mesh.bevel",icon='MOD_BEVEL')
        layout.separator()
        layout.operator("mesh.knife_tool",icon='SCULPTMODE_HLT')
        layout.operator("mesh.subdivide",icon='OUTLINER_OB_LATTICE')
        layout.operator("mesh.loopcut_slide",icon='SNAP_EDGE')
        layout.operator("transform.edge_slide",icon='SNAP_EDGE')
        layout.operator("mesh.bisect",icon='MOD_DISPLACE')
        layout.separator()
        layout.operator("mesh.edge_face_add",icon='SNAP_FACE')
        layout.operator("mesh.separate",icon='UV_ISLANDSEL').type = 'SELECTED'
        layout.operator("mesh.remove_doubles",icon='MOD_DISPLACE')
        layout.separator()
        layout.operator("mesh.duplicate_move",icon='GHOST')
        layout.operator("transform.vertex_random",icon='STICKY_UVS_DISABLE')
        layout.separator()
        layout.operator("mesh.normals_make_consistent",icon='FULLSCREEN_ENTER')
        layout.operator("mesh.flip_normals",icon='AUTOMERGE_OFF')
        layout.operator("view3d.set_base_point",icon='SPACE2').object_name = obj.name 
        layout.separator()
        layout.menu('VIEW3D_MT_edit_mesh_delete',icon='X')
        
class VIEW3D_MT_editcurvetools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Edit Curve Tools"

    def draw(self, context):
        layout = self.layout
        obj = context.object        
        layout.operator("curve.subdivide",icon='OUTLINER_OB_LATTICE')
        layout.operator("curve.split",icon='SCULPTMODE_HLT')
        layout.operator("curve.spin",icon='CURVE_NCURVE')
        layout.operator("curve.extrude_move",icon='CURVE_PATH')   
        layout.operator("curve.switch_direction",icon='AUTOMERGE_OFF')  
        layout.operator("curve.cyclic_toggle",icon='CURVE_NCIRCLE')
        layout.separator()
        layout.operator("curve.separate",icon='UV_ISLANDSEL')    
        layout.separator()
        layout.menu("VIEW3D_MT_edit_curve_delete", "Delete",icon='X')
        
class VIEW3D_MT_mesh_selection(bpy.types.Menu):
    bl_label = "Mesh Selection"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.select_mode",text="Vertex Select",icon='VERTEXSEL').type='VERT'
        layout.operator("mesh.select_mode",text="Edge Select",icon='EDGESEL').type='EDGE'
        layout.operator("mesh.select_mode",text="Face Select",icon='FACESEL').type='FACE'

class VIEW3D_MT_drawing_tools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Drawing Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.draw_assembly", icon='MESH_CUBE',text="Draw Box") 
        layout.operator("view3d.draw_plane", icon='MESH_PLANE',text="Draw Plane")   
        layout.operator("view3d.draw_curve", icon='CURVE_DATA',text="Draw Lines")  
        layout.operator("view3d.place_area_lamp", icon='LAMP_POINT',text="Draw Area Lamp")    

class VIEW3D_PT_Standard_Objects(bpy.types.Panel):
    bl_label = "Standard Objects"
    bl_idname = "VIEW3D_PT_Standard_Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Draw"
    bl_context = "objectmode"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        
        box = self.layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.label("Drawing Tools",icon='GREASEPENCIL')
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.3        
        row.operator("view3d.draw_assembly", icon='MESH_CUBE',text="Draw Box") 
        row = col.row(align=True)  
        row.scale_y = 1.3        
        row.operator("view3d.draw_plane", icon='MESH_PLANE',text="Draw Plane")   
        row = col.row(align=True)
        row.scale_y = 1.3        
        row.operator("view3d.draw_curve", icon='CURVE_DATA',text="Draw Lines")          
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator("view3d.place_area_lamp", icon='LAMP_POINT',text="Draw Area Lamp")        

def register():
    clear_view3d_properties_shelf()
    clear_view3d_tools_shelf()
    clear_view3d_header()
    clear_view3d_menus()
    
    bpy.utils.register_class(VIEW3D_HT_header)
    bpy.utils.register_class(VIEW3D_MT_menus)
    bpy.utils.register_class(VIEW3D_MT_view)
    bpy.utils.register_class(VIEW3D_MT_add_object)
    bpy.utils.register_class(VIEW3D_MT_add_lamp)
    bpy.utils.register_class(VIEW3D_MT_tools)
    bpy.utils.register_class(VIEW3D_MT_cursor_tools) 
    bpy.utils.register_class(VIEW3D_MT_transformtools) 
    bpy.utils.register_class(VIEW3D_MT_selectiontools) 
    bpy.utils.register_class(VIEW3D_MT_origintools) 
    bpy.utils.register_class(VIEW3D_MT_shadetools) 
    bpy.utils.register_class(VIEW3D_MT_objecttools) 
    bpy.utils.register_class(VIEW3D_MT_editmeshtools) 
    bpy.utils.register_class(VIEW3D_MT_mesh_selection)  
    bpy.utils.register_class(VIEW3D_MT_drawing_tools) 
    bpy.utils.register_class(VIEW3D_MT_editcurvetools) 
#     bpy.utils.register_class(VIEW3D_PT_Standard_Objects)
    
def unregister():
    pass