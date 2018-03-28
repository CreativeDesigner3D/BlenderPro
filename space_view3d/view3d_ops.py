import bpy
import mathutils
import bgl
import math
import bmesh
from ..bp_lib.assembly import Assembly
from ..bp_lib.opengl import TextBox
from ..bp_lib import utils, unit
from bpy_extras.view3d_utils import location_3d_to_region_2d

ISWALL = "ISWALL"
ISROOMMESH = "ISROOMMESH"

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

        view_box = layout.box()
        view_box.label("Viewport Options",icon='SCENE')
        row = view_box.row()
        row.label("Viewport Lens Angle:")
        row.prop(context.space_data,"lens",text="")
        row = view_box.row(align=True)
        row.label("Clipping Distance:")
        row.prop(context.space_data,"clip_start",text="Start")
        row.prop(context.space_data,"clip_end",text="End")
        layout.separator()
        view_box.prop(context.space_data,"lock_camera",text="Lock Camera to View")

        col = view_box.column()
        col.prop(view, "show_only_render")
        col.prop(view, "show_world")

        col = view_box.column()
        row = col.row()
        row.prop(view, "show_outline_selected")
        row.prop(view, "show_all_objects_origin")
        row = col.row()
        row.prop(view, "show_relationship_lines")
        row.prop(view, "show_backface_culling")

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
        sub.prop(view, "grid_subdivisions",text="Subdivisions")

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

class OPS_draw_assembly(bpy.types.Operator):
    bl_idname = "view3d.draw_assembly"
    bl_label = "Draw Assembly"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    snapping_point_2d = (0,0,0)
    placement_point_3d = (0,0,0)
    
    drawing_plane = None
    cube = None
    ray_cast_objects = []
    placed_first_point = False
    first_point = (0,0,0)
    selected_point = (0,0,0)
    found_snap_point = False
    
    def cancel_drop(self,context):
        utils.delete_object_and_children(self.cube.obj_bp)
        self.finish(context)
        
    def finish(self,context):
        bpy.ops.object.select_all(action='DESELECT')

        obj = None 
        mesh = None
        for child in self.cube.obj_bp.children:
            
            if ISROOMMESH in child:
                mesh = child
            
            if 'ISXDIM' in child:
                if math.fabs(child.location.x) < unit.inch(1):
                    obj = child
                    
            if 'ISYDIM' in child:
                if math.fabs(child.location.y) < unit.inch(1):
                    obj = child
                    
            if 'ISZDIM' in child:
                if math.fabs(child.location.z) < unit.inch(1):
                    obj = child

        if obj:
            obj.select = True
            context.scene.objects.active = obj
            bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        #CANNOT RUN THIS CODE WHILE IN TRANSLATE OPERATOR
#         if mesh:
#             list_mod = []
#             if mesh:
#                 for mod in obj.modifiers:
#                     if mod.type in {'HOOK'}:
#                         list_mod.append(mod.name)
#     
#             for mod in list_mod:
#                 bpy.ops.object.modifier_apply(apply_as='DATA',modifier=mod)
#                 
#             bpy.ops.mesh.select_all(action='DESELECT')
#             mesh.select = True
#             context.scene.objects.active = mesh
#                 
#             bpy.ops.object.editmode_toggle()
#             bpy.ops.mesh.select_all(action='SELECT')
#             bpy.ops.mesh.normals_make_consistent()
#             bpy.ops.object.editmode_toggle()
        
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
        
        if self.placed_first_point:
            help_text = "Command Help:\nLEFT CLICK: Place Second Point\nRIGHT CLICK: Cancel Command"
        else:
            help_text = "Command Help:\nLEFT CLICK: Place First Point\nRIGHT CLICK: Cancel Command"
        
        if self.found_snap_point:
            help_text += "\n SNAP TO VERTEX"
        
        help_box = TextBox(
            x=0,y=0,
            width=500,height=0,
            border=10,margin=100,
            message=help_text)
        help_box.x = (self.mouse_x + (help_box.width) / 2 + 10) - region.x
        help_box.y = (self.mouse_y - 10) - region.y

        help_box.draw()
        
        # SNAP POINT
        bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
     
        bgl.glColor4f(255, 0.0, 0.0, 1.0)
        bgl.glEnable(bgl.GL_BLEND)
         
        bgl.glPointSize(10)
        bgl.glBegin(bgl.GL_POINTS)
     
        if self.snapping_point_2d:
            bgl.glVertex2f(self.snapping_point_2d[0], self.snapping_point_2d[1])
     
        bgl.glEnd()
        bgl.glPopAttrib()
     
        # restore opengl defaults
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def event_is_place_last_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        else:
            return False

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

    def calc_distance(self,point1,point2):
        """ This gets the distance between two points (X,Y,Z)
        """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        
        return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) 

    def get_snap_point(self,context,selected_point,selected_obj):
        """
            Used to set the self.snapping_point_2d for opengl and
            Used to set the self.placement_point_3d for final placement position
        """
        if selected_obj is not None:
            obj_data = selected_obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
            mesh = obj_data
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)
            for i, v in enumerate(mesh.vertices):
                kd.insert(selected_obj.matrix_world * v.co, i)
            kd.balance()
            snapping_point, index, dist = kd.find(selected_point)
            
            dist = self.calc_distance(snapping_point, selected_point)
            
            if dist > .5:
                #TOO FAR AWAY FROM SNAP POINT
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  selected_point)
                self.placement_point_3d = selected_point
                self.found_snap_point = False
            else:
                #FOUND POINT TO SNAP TO
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  snapping_point)
                self.placement_point_3d = snapping_point
                self.found_snap_point = True
                
            bpy.data.meshes.remove(obj_data)
        
    def position_cube(self,context,selected_point,selected_obj):
        self.get_snap_point(context, selected_point, selected_obj)
        
        if not self.placed_first_point:
            self.cube.obj_bp.location = self.placement_point_3d
            self.first_point = self.placement_point_3d
        else:
            self.cube.x_dim(value = self.placement_point_3d[0] - self.first_point[0])
            self.cube.y_dim(value = self.placement_point_3d[1] - self.first_point[1])
            self.cube.z_dim(value = self.placement_point_3d[2] - self.first_point[2])
            
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        selected_point, selected_obj = utils.get_selection_point(context,event)
        
        self.position_cube(context,selected_point,selected_obj)
        
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

class OPS_draw_plane(bpy.types.Operator):
    bl_idname = "view3d.draw_plane"
    bl_label = "Draw Plane"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    snapping_point_2d = (0,0,0)
    placement_point_3d = (0,0,0)
    
    drawing_plane = None
    cube = None
    plane = None
    ray_cast_objects = []
    placed_first_point = False
    first_point = (0,0,0)
    selected_point = (0,0,0)
    found_snap_point = False
    
    def cancel_drop(self,context):
        utils.delete_object_and_children(self.plane)
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
        
        if self.placed_first_point:
            help_text = "Command Help:\nLEFT CLICK: Place Second Point\nRIGHT CLICK: Cancel Command"
        else:
            help_text = "Command Help:\nLEFT CLICK: Place First Point\nRIGHT CLICK: Cancel Command"
        
        if self.found_snap_point:
            help_text += "\n SNAP TO VERTEX"
        
        help_box = TextBox(
            x=0,y=0,
            width=500,height=0,
            border=10,margin=100,
            message=help_text)
        help_box.x = (self.mouse_x + (help_box.width) / 2 + 10) - region.x
        help_box.y = (self.mouse_y - 10) - region.y
        
        help_box.draw()
        
        # SNAP POINT
        bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
     
        bgl.glColor4f(255, 0.0, 0.0, 1.0)
        bgl.glEnable(bgl.GL_BLEND)
         
        bgl.glPointSize(10)
        bgl.glBegin(bgl.GL_POINTS)
     
        if self.snapping_point_2d:
            bgl.glVertex2f(self.snapping_point_2d[0], self.snapping_point_2d[1])
     
        bgl.glEnd()
        bgl.glPopAttrib()
     
        # restore opengl defaults
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

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

    def calc_distance(self,point1,point2):
        """ This gets the distance between two points (X,Y,Z)
        """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        
        return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) 

    def get_snap_point(self,context,selected_point,selected_obj):
        """
            Used to set the self.snapping_point_2d for opengl and
            Used to set the self.placement_point_3d for final placement position
        """
        if selected_obj is not None:
            obj_data = selected_obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
            mesh = obj_data
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)
            for i, v in enumerate(mesh.vertices):
                kd.insert(selected_obj.matrix_world * v.co, i)
            kd.balance()
            snapping_point, index, dist = kd.find(selected_point)
            
            dist = self.calc_distance(snapping_point, selected_point)
            
            if dist > .5:
                #TOO FAR AWAY FROM SNAP POINT
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  selected_point)
                self.placement_point_3d = selected_point
                self.found_snap_point = False
            else:
                #FOUND POINT TO SNAP TO
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  snapping_point)
                self.placement_point_3d = snapping_point
                self.found_snap_point = True
                
            bpy.data.meshes.remove(obj_data)
        
    def position_cube(self,context,selected_point,selected_obj):
        self.get_snap_point(context, selected_point, selected_obj)
        
        if not self.placed_first_point:
            
            self.plane.location = self.placement_point_3d
            self.first_point = self.placement_point_3d
            
        else:
            
            for i, vert in enumerate(self.plane.data.vertices):
                
                if i == 0:
                    vert.co = (0,0,0)
                if i == 1:
                    vert.co = (self.placement_point_3d[0] - self.first_point[0],0,0)
                if i == 2:
                    vert.co = (self.placement_point_3d[0] - self.first_point[0],self.placement_point_3d[1] - self.first_point[1],0)
                if i == 3:
                    vert.co = (0,self.placement_point_3d[1] - self.first_point[1],0)
            
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        selected_point, selected_obj = utils.get_selection_point(context,event)
        
        self.position_cube(context,selected_point,selected_obj)

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
        
        width = 0
        height = 0
        depth = 0
        
        verts = [(0.0, 0.0, 0.0),
                 (0.0, depth, 0.0),
                 (width, depth, 0.0),
                 (width, 0.0, 0.0),
                 ]
    
        faces = [(0, 1, 2, 3),
                ]
        
        mesh = bpy.data.meshes.new("Plane")
        
        bm = bmesh.new()
    
        for v_co in verts:
            bm.verts.new(v_co)
        
        for f_idx in faces:
            bm.verts.ensure_lookup_table()
            bm.faces.new([bm.verts[i] for i in f_idx])
        
        bm.to_mesh(mesh)
        
        mesh.update()
        
        obj_mesh = bpy.data.objects.new(mesh.name, mesh)
        bpy.context.scene.objects.link(obj_mesh)     
        self.plane = obj_mesh   
        
        #CREATE CUBE
#         self.cube = Assembly()
#         self.cube.create_assembly()
#         mesh_obj = self.cube.add_mesh("RoomCube")
#         mesh_obj[ISROOMMESH] = True
#         self.cube.x_dim(value = 0)
#         self.cube.y_dim(value = 0)
#         self.cube.z_dim(value = 0)
        
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

class OPS_draw_curve(bpy.types.Operator):
    bl_idname = "view3d.draw_curve"
    bl_label = "Draw Curve"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    snapping_point_2d = (0,0,0)
    placement_point_3d = (0,0,0)
    
    drawing_plane = None
    
    curve = None
    current_point = None

    ray_cast_objects = []
    placed_first_point = False
    first_point = (0,0,0)
    selected_point = (0,0,0)
    found_snap_point = False
    
    def cancel_drop(self,context):
        utils.delete_object_and_children(self.plane)
        self.finish(context)
        
    def remove_last_vert_and_set_handle_type(self):
        bpy.ops.object.editmode_toggle()
        self.curve.data.splines[0].bezier_points[-1].select_control_point = True
        bpy.ops.curve.dissolve_verts()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()

    def finish(self,context):
        self.remove_last_vert_and_set_handle_type()
        context.space_data.draw_handler_remove(self._draw_handle, 'WINDOW')
        
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
        
        if self.placed_first_point:
            help_text = "Command Help:\nLEFT CLICK: Place Second Point\nRIGHT CLICK: Cancel Command"
        else:
            help_text = "Command Help:\nLEFT CLICK: Place First Point\nRIGHT CLICK: Cancel Command"
        
        if self.found_snap_point:
            help_text += "\n SNAP TO VERTEX"
        
        help_box = TextBox(
            x=0,y=0,
            width=500,height=0,
            border=10,margin=100,
            message=help_text)
        help_box.x = (self.mouse_x + (help_box.width) / 2 + 10) - region.x
        help_box.y = (self.mouse_y - 10) - region.y
        
        help_box.draw()
        
        # SNAP POINT
        bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
     
        bgl.glColor4f(255, 0.0, 0.0, 1.0)
        bgl.glEnable(bgl.GL_BLEND)
         
        bgl.glPointSize(10)
        bgl.glBegin(bgl.GL_POINTS)
     
        if self.snapping_point_2d:
            bgl.glVertex2f(self.snapping_point_2d[0], self.snapping_point_2d[1])
     
        bgl.glEnd()
        bgl.glPopAttrib()
     
        # restore opengl defaults
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def event_is_place_first_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point == False:
            return True
        else:
            return False

    def event_is_place_next_point(self,event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.placed_first_point:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.placed_first_point:
            return True
        else:
            return False

    def calc_distance(self,point1,point2):
        """ This gets the distance between two points (X,Y,Z)
        """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        
        return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) 

    def get_snap_point(self,context,selected_point,selected_obj):
        """
            Used to set the self.snapping_point_2d for opengl and
            Used to set the self.placement_point_3d for final placement position
        """
        if selected_obj is not None:
            obj_data = selected_obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
            mesh = obj_data
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)
            for i, v in enumerate(mesh.vertices):
                kd.insert(selected_obj.matrix_world * v.co, i)
            kd.balance()
            snapping_point, index, dist = kd.find(selected_point)
            
            dist = self.calc_distance(snapping_point, selected_point)
            
            if dist > .5:
                #TOO FAR AWAY FROM SNAP POINT
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  selected_point)
                self.placement_point_3d = selected_point
                self.found_snap_point = False
            else:
                #FOUND POINT TO SNAP TO
                self.snapping_point_2d = location_3d_to_region_2d(context.region, 
                                                                  context.space_data.region_3d, 
                                                                  snapping_point)
                self.placement_point_3d = snapping_point
                self.found_snap_point = True
                
            bpy.data.meshes.remove(obj_data)
        
    def position_curve(self,context,selected_point,selected_obj):
        self.get_snap_point(context, selected_point, selected_obj)
        
        if not self.placed_first_point:
            
            self.curve.location = self.placement_point_3d
            self.first_point = self.placement_point_3d
            
        else:
            
            self.current_point.co = (self.placement_point_3d[0] - self.first_point[0],
                                     self.placement_point_3d[1] - self.first_point[1],
                                     self.placement_point_3d[2] - self.first_point[2])
    
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        selected_point, selected_obj = utils.get_selection_point(context,event)
        
        self.position_curve(context,selected_point,selected_obj)

        if self.event_is_place_next_point(event):
            self.curve.data.splines[0].bezier_points.add()
            self.current_point = self.curve.data.splines[0].bezier_points[-1]
            self.current_point.handle_left_type = 'VECTOR'
            self.current_point.handle_right_type = 'VECTOR'            

        if self.event_is_place_first_point(event):
            self.placed_first_point = True
            spline = self.curve.data.splines.new('BEZIER')
            spline.bezier_points.add()
            self.curve.data.splines.active = spline
            self.current_point = spline.bezier_points[-1]
            self.current_point.handle_left_type = 'VECTOR'
            self.current_point.handle_right_type = 'VECTOR'

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.finish(context)

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
        
        curve = bpy.data.curves.new("Curve",'CURVE')
        obj_curve = bpy.data.objects.new(curve.name,curve)
        bpy.context.scene.objects.link(obj_curve)  
        context.scene.objects.active = obj_curve
        self.curve = obj_curve

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

class OPS_add_text(bpy.types.Operator):
    bl_idname = "view3d.add_text"
    bl_label = "Add Text"
    
    enter_text = bpy.props.StringProperty(name='Enter Text')
    split_with = bpy.props.StringProperty(name='Split With')
    split_text_with_character = bpy.props.BoolProperty(name="Split Text with Character")

    def check(self, context):
        return True

    def execute(self, context):
        if self.split_with != "":
            objs = []
            split_text = self.enter_text.split(self.split_with)
            current_y = context.scene.cursor_location[1]
            for text in split_text:
                bpy.ops.object.text_add()
                obj = context.active_object
                obj.name = text
                obj.data.body = text
                obj.location.y = current_y
                obj.select = True
                current_y -= obj.dimensions.y
                objs.append(obj)
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objs:
                obj.select = True
        else:
            bpy.ops.object.text_add()
            obj = context.active_object
            obj.name = self.enter_text
            obj.data.body = self.enter_text
            obj.select = True
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"enter_text")
        col.prop(self,"split_text_with_character")
        if self.split_text_with_character:
            col.prop(self,"split_with",text="Enter Character")

class OPS_update_selected_text_with_active_font(bpy.types.Operator):
    bl_idname = "view3d.update_selected_text_with_active_font"
    bl_label = "Update Selected Text with Active Font"

    def execute(self, context):
        active_font = context.active_object.data.font
        for obj in context.selected_objects:
            obj.data.font = active_font
        return {'FINISHED'}

class OPS_place_empty(bpy.types.Operator):
    bl_idname = "view3d.place_empty"
    bl_label = "Place Empty"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        obj = context.active_object
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        return {'FINISHED'}

class OPS_place_area_lamp(bpy.types.Operator):
    bl_idname = "view3d.place_area_lamp"
    bl_label = "Place Area Lamp"
    bl_options = {'UNDO'}
    
    #READONLY
    _draw_handle = None
    mouse_x = 0
    mouse_y = 0
    
    drawing_plane = None
    lamp = None
    ray_cast_objects = []
    placed_first_point = False
    selected_point = (0,0,0)
    
    def cancel_drop(self,context):
        utils.delete_object_and_children(self.lamp)
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

    def position_lamp(self,selected_point):
        if not self.placed_first_point:
            self.lamp.location = selected_point
            self.selected_point = selected_point
        else:
            self.lamp.data.size = utils.calc_distance((self.selected_point[0],0,0),(selected_point[0],0,0))
            self.lamp.data.size_y = utils.calc_distance((0,self.selected_point[1],0),(0,selected_point[1],0))
            self.lamp.location.x = self.selected_point[0] + ((selected_point[0]/2) - (self.selected_point[0]/2))
            self.lamp.location.y = self.selected_point[1] + ((selected_point[1]/2) - (self.selected_point[1]/2))
            self.lamp.location.z = self.selected_point[2]
#             self.lamp.x_dim(value = selected_point[0] - self.selected_point[0])
#             self.lamp.y_dim(value = selected_point[1] - self.selected_point[1])
#             self.lamp.z_dim(value = selected_point[2] - self.selected_point[2])
            
    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        
        selected_point, selected_obj = utils.get_selection_point(context,event)
        
        self.position_lamp(selected_point)
        
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
        
        lamp = bpy.data.lamps.new("Room Lamp",'AREA')
        lamp.shape = 'RECTANGLE'
        obj_lamp = bpy.data.objects.new("Room Lamp", lamp)
        context.scene.objects.link(obj_lamp)
        self.lamp = obj_lamp
        self.lamp.data.use_nodes = True
#         bpy.ops.cycles.use_shading_nodes()
        
        #CREATE CUBE
#         self.cube = Assembly()
#         self.cube.create_assembly()
#         mesh_obj = self.cube.add_mesh("RoomCube")
#         mesh_obj[ISROOMMESH] = True
#         self.cube.x_dim(value = 0)
#         self.cube.y_dim(value = 0)
#         self.cube.z_dim(value = 0)
        
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

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

class OPS_set_base_point(bpy.types.Operator):
    bl_idname = "view3d.set_base_point"
    bl_label = "Set Base Point"
    bl_options = {'UNDO'}

    object_name = bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        cursor_x = context.scene.cursor_location[0]
        cursor_y = context.scene.cursor_location[1]
        cursor_z = context.scene.cursor_location[2]
        bpy.ops.view3d.snap_cursor_to_selected()
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
            
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        context.scene.cursor_location = (cursor_x,cursor_y,cursor_z)
        if obj.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
            
        return {'FINISHED'}    

class OPS_create_group_instance(bpy.types.Operator):
    bl_idname = "view3d.create_group_instance"
    bl_label = "Create Group Instance"
    bl_options = {'UNDO'}

    group_name = bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        grp = bpy.data.groups[self.group_name]
        obj = bpy.data.objects.new(self.group_name,None)
        context.scene.objects.link(obj)
        obj.dupli_type = 'GROUP'
        obj.dupli_group = grp
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj
        return {'FINISHED'}

class OPS_open_texture_editor(bpy.types.Operator):
    bl_idname = "object_props.open_texture_editor"
    bl_label = "Open Texture Editor"

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'MESH':
            return True
        else:
            return False
        
    def execute(self, context):
        if context.object.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
            
        bpy.ops.mesh.select_all(action='SELECT')
        
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'USER_PREFERENCES':
                window.screen.areas[0].type = 'IMAGE_EDITOR'
        return {'FINISHED'} 

def register():
    bpy.utils.register_class(OPS_viewport_options)
    bpy.utils.register_class(OPS_change_shademode)
    bpy.utils.register_class(OPS_draw_assembly)
    bpy.utils.register_class(OPS_draw_plane)
    bpy.utils.register_class(OPS_draw_curve)
    bpy.utils.register_class(OPS_add_camera)
    bpy.utils.register_class(OPS_add_text)
    bpy.utils.register_class(OPS_update_selected_text_with_active_font)
    bpy.utils.register_class(OPS_place_empty)
    bpy.utils.register_class(OPS_place_area_lamp)
    bpy.utils.register_class(OPS_set_cursor_location)
    bpy.utils.register_class(OPS_snapping_options)
    bpy.utils.register_class(OPS_set_base_point)
    bpy.utils.register_class(OPS_create_group_instance)
    bpy.utils.register_class(OPS_open_texture_editor)
    
def unregister():
    pass