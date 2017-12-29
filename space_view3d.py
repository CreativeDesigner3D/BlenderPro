import bpy
from .assembly import Assembly
from .opengl import TextBox
from . import utils
from . import unit

ISWALL = "ISWALL"
ISROOMMESH = "ISROOMMESH"

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

        row = layout.row(align=True)
#         row.separator()
        
        row.template_header()
        
        VIEW3D_MT_menus.draw_collapsible(context, layout)
        
        if context.space_data.viewport_shade == 'WIREFRAME':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Wire Frame",icon='WIRE')
        if context.space_data.viewport_shade == 'SOLID':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Solid",icon='SOLID')
        if context.space_data.viewport_shade == 'MATERIAL':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Material",icon='MATERIAL')
        if context.space_data.viewport_shade == 'RENDERED':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Rendered",icon='SMOOTH')

        row = layout.row()
        row.prop(context.space_data,"pivot_point",text="")
        
        row = layout.row(align=True)
        row.prop(context.space_data,"show_manipulator",text="")
        row.prop(context.space_data,"transform_manipulators",text="")
        row.prop(context.space_data,"transform_orientation",text="")
        
        if obj:
            if obj.type in {'MESH','CURVE'}:
                if obj.mode == 'EDIT':
                    layout.operator_menu_enum('fd_general.change_mode',"mode",icon='EDITMODE_HLT',text="Edit Mode")
                else:
                    layout.operator_menu_enum('fd_general.change_mode',"mode",icon='OBJECT_DATAMODE',text="Object Mode")
                
        row = layout.row(align=True)
        row.operator('view3d.ruler',text="Ruler")

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
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("view3d.draw_mesh", icon='MESH_GRID')

        layout.operator_context = 'EXEC_REGION_WIN'
        layout.separator()
        layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')

        layout.menu("INFO_MT_curve_add", icon='OUTLINER_OB_CURVE')
        layout.operator_context = 'EXEC_REGION_WIN'
        layout.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
        layout.separator()

        layout.operator_menu_enum("object.empty_add", "type", text="Empty", icon='OUTLINER_OB_EMPTY')
        layout.separator()
        layout.operator("view3d.add_camera",text="Camera",icon='OUTLINER_OB_CAMERA')
        layout.menu("VIEW3D_MT_add_lamp", icon='OUTLINER_OB_LAMP')
        layout.separator()
        
        if len(bpy.data.groups) > 10:
            layout.operator_context = 'INVOKE_REGION_WIN'
            layout.operator("object.group_instance_add", text="Group Instance...", icon='OUTLINER_OB_EMPTY')
        else:
            layout.operator_menu_enum("object.group_instance_add", "group", text="Group Instance", icon='OUTLINER_OB_EMPTY')

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
        layout = self.layout
        layout.menu("VIEW3D_MT_objecttools",icon='OBJECT_DATA')
        layout.menu("VIEW3D_MT_cursor_tools",icon='CURSOR')
        layout.menu("VIEW3D_MT_selectiontools",icon='MAN_TRANS')
        layout.separator()
        layout.operator("view3d.snapping_options",icon='SNAP_ON')

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
#         layout.menu("VIEW3D_MT_transformtools",icon='MAN_TRANS')
        layout.separator()
        layout.operator("object.duplicate_move",icon='PASTEDOWN')
        layout.operator("object.convert", text="Convert to Mesh",icon='MOD_REMESH').target = 'MESH'
        layout.operator("object.join",icon='ROTATECENTER')
        layout.separator()
        layout.menu("VIEW3D_MT_selectiontools",icon='MOD_MULTIRES')            
        layout.separator()
        layout.menu("VIEW3D_MT_origintools",icon='SPACE2')
        layout.separator()
        layout.menu("VIEW3D_MT_shadetools",icon='MOD_MULTIRES')
        layout.separator()
        layout.operator("object.delete",icon='X').use_global = False

class OPS_viewport_options(bpy.types.Operator):
    bl_idname = "space_view3d.viewport_options"
    bl_label = "Viewport Options"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        view = context.space_data

        camera_box = layout.box()
        camera_box.label("Viewport Options",icon='SCENE')
        camera_box.prop(context.space_data,"lens",text="Viewport Lens Angle")
        row = camera_box.row()
        row.prop(context.space_data,"clip_start",text="Viewport Clipping Start")
        row.prop(context.space_data,"clip_end",text="Viewport Clipping End")
        layout.separator()
        camera_box.prop(context.space_data,"lock_camera",text="Lock Camera to View")

        col = camera_box.column()
        col.prop(view, "show_only_render")
        col.prop(view, "show_world")

        col = camera_box.column()
        col.prop(view, "show_outline_selected")
        col.prop(view, "show_all_objects_origin")
        col.prop(view, "show_relationship_lines")

        grid_box = layout.box()
        grid_box.label("Grid Options",icon='GRID')
        
        col = grid_box.column()
        split = col.split(percentage=0.55)
        split.prop(view, "show_floor", text="Grid Floor")

        row = split.row(align=True)
        row.prop(view, "show_axis_x", text="X", toggle=True)
        row.prop(view, "show_axis_y", text="Y", toggle=True)
        row.prop(view, "show_axis_z", text="Z", toggle=True)

        sub = col.column(align=True)
        sub.active = bool(view.show_floor or view.region_quadviews or not view.region_3d.is_perspective)
        subsub = sub.column(align=True)
        subsub.active = view.show_floor
        subsub.prop(view, "grid_lines", text="Lines")
        sub.prop(view, "grid_scale", text="Scale")

class OPS_change_shademode(bpy.types.Operator):
    bl_idname = "view3d.change_shademode"
    bl_label = "Change Shademode"

    shade_mode = bpy.props.EnumProperty(
            name="Shade Mode",
            items=(('WIREFRAME', "Wire Frame", "WIREFRAME",'WIRE',1),
                   ('SOLID', "Solid", "SOLID",'SOLID',2),
                   ('MATERIAL', "Material","MATERIAL",'MATERIAL',3),
                   ('RENDERED', "Rendered", "RENDERED",'SMOOTH',4)
                   ),
            )

    def execute(self, context):
        context.scene.render.engine = 'CYCLES'
        context.space_data.viewport_shade = self.shade_mode
        return {'FINISHED'}

class OPS_draw_mesh(bpy.types.Operator):
    bl_idname = "view3d.draw_mesh"
    bl_label = "Draw Mesh"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    drawing_plane = None
    cube = None
    ray_cast_objects = []
    placed_first_point = False
    selected_point = (0,0,0)
    
    def cancel_drop(self,context):
        utils.delete_object_and_children(self.cube.obj_bp)
        self.finish(context)
        
    def finish(self,context):
        context.space_data.draw_handler_remove(self._draw_handle, 'WINDOW')
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            utils.delete_obj_list([self.drawing_plane])
        context.area.tag_redraw()
        return {'FINISHED'}

    @staticmethod
    def _window_region(context):
        window_regions = [region
                          for region in context.area.regions
                          if region.type == 'WINDOW']
        return window_regions[0]

    def draw_opengl(self,context):     
        region = self._window_region(context)
        
        help_box = TextBox(
            x=0,y=0,
            width=500,height=0,
            border=10,margin=100,
            message="Command Help:\nLEFT CLICK: Place Wall\nRIGHT CLICK: Cancel Command")
        help_box.x = (self.mouse_x + (help_box.width) / 2 + 10) - region.x
        help_box.y = (self.mouse_y - 10) - region.y

        help_box.draw()

    def event_is_place_first_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        else:
            return False

    def event_is_place_second_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point:
            return True
        else:
            return False

    def position_cube(self,selected_point):
        if not self.placed_first_point:
            self.cube.obj_bp.location = selected_point
            self.selected_point = selected_point
        else:
            self.cube.x_dim(value = selected_point[0] - self.selected_point[0])
            self.cube.y_dim(value = selected_point[1] - self.selected_point[1])
            self.cube.z_dim(value = selected_point[2] - self.selected_point[2])
            
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        selected_point, selected_obj = utils.get_selection_point(context,event)
        
        self.position_cube(selected_point)

        if self.event_is_place_second_point(event):
            return self.finish(context)

        if self.event_is_place_first_point(event):
            self.placed_first_point = True

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_drop(context)
            return {'CANCELLED'}
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}
        
    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.draw_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)
        self.ray_cast_objects.append(self.drawing_plane)

    def invoke(self, context, event):
        self.ray_cast_objects = []
        for obj in bpy.data.objects:
            if ISWALL in obj or ISROOMMESH in obj:
                self.ray_cast_objects.append(obj)
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self._draw_handle = context.space_data.draw_handler_add(
            self.draw_opengl, (context,), 'WINDOW', 'POST_PIXEL')
        self.placed_first_point = False
        self.selected_point = (0,0,0)
        
        self.create_drawing_plane(context)
        
        #CREATE CUBE
        self.cube = Assembly()
        self.cube.create_assembly()
        mesh_obj = self.cube.add_mesh("RoomCube")
        mesh_obj[ISROOMMESH] = True
        self.cube.x_dim(value = 0)
        self.cube.y_dim(value = 0)
        self.cube.z_dim(value = 0)
        
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

class OPS_add_camera(bpy.types.Operator):
    bl_idname = "view3d.add_camera"
    bl_label = "Add Camera"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.camera_add(view_align=False)
        camera = context.active_object
        bpy.ops.view3d.camera_to_view()
        camera.data.clip_start = unit.inch(1)
        camera.data.clip_end = 9999
        camera.data.ortho_scale = 200.0
        return {'FINISHED'}

class OPS_set_cursor_location(bpy.types.Operator):
    bl_idname = "view3d.set_cursor_location"
    bl_label = "Cursor Location"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene,"cursor_location",text="")

class OPS_snapping_options(bpy.types.Operator):
    bl_idname = "view3d.snapping_options"
    bl_label = "Snapping Options"

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        toolsettings = context.tool_settings
        obj = context.object
        if not obj or obj.mode not in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'}:
            snap_element = toolsettings.snap_element
#             row = layout.row(align=True)
            if toolsettings.use_snap:
                layout.prop(toolsettings, "use_snap", text="Snapping On")
                layout.label("Tip: Hold Ctrl to deactivate snapping when snapping is turned ON")
            else:
                layout.prop(toolsettings, "use_snap", text="Snapping Off")
                layout.label("Tip: Hold Ctrl to activate snapping when snapping is turned OFF")
                
            layout.prop(toolsettings, "snap_element", icon_only=False)
            if snap_element == 'INCREMENT':
                layout.prop(toolsettings, "use_snap_grid_absolute")
            else:
                layout.prop(toolsettings, "snap_target")
                if obj:
                    if obj.mode in {'OBJECT', 'POSE'} and snap_element != 'VOLUME':
                        layout.prop(toolsettings, "use_snap_align_rotation")
                    elif obj.mode == 'EDIT':
                        layout.prop(toolsettings, "use_snap_self")

            if snap_element == 'VOLUME':
                layout.prop(toolsettings, "use_snap_peel_object")
            elif snap_element == 'FACE':
                layout.prop(toolsettings, "use_snap_project")

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
    bpy.utils.register_class(OPS_viewport_options)
    bpy.utils.register_class(OPS_change_shademode)
    bpy.utils.register_class(OPS_draw_mesh)
    bpy.utils.register_class(OPS_add_camera)
    bpy.utils.register_class(OPS_set_cursor_location)
    bpy.utils.register_class(OPS_snapping_options)    
    
def unregister():
    pass