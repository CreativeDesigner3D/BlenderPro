"""
This module defines the basic classes needed for assemblies. 

"""

import bpy
import bmesh

def hook_vertex_group_to_object(obj_mesh,vertex_group,obj_hook):
    """ This function adds a hook modifier to the verties 
        in the vertex_group to the obj_hook
    """
    bpy.ops.object.select_all(action = 'DESELECT')
    obj_hook.hide = False
    obj_hook.hide_select = False
    obj_hook.select = True
    obj_mesh.hide = False
    obj_mesh.hide_select = False
    if vertex_group in obj_mesh.vertex_groups:
        vgroup = obj_mesh.vertex_groups[vertex_group]
        obj_mesh.vertex_groups.active_index = vgroup.index
        bpy.context.scene.objects.active = obj_mesh
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.vertex_group_select()
        if obj_mesh.data.total_vert_sel > 0:
            bpy.ops.object.hook_add_selob()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.editmode_toggle()

class Assembly:
    """
    An Assembly is a way to control a group of blender objects 
    in python. All assemblies have a base point which all objects
    are parented to. The X, Y, and Dimension objects control 
    the size of the group.
    
    The Base Point Object is tagged with "ISBP"
    The X Dimension is tagged with "ISXDIM"
    The Y Dimension is tagged with "ISYDIM"
    The Z Dimension is tagged with "ISZDIM"
    
    """
    obj_bp = None
    obj_x = None
    obj_y = None
    obj_z = None
    
    def __init__(self,obj_bp=None):
        """ 
        Assembly Constructor. If you want to create an instance of
        an existing Assembly then pass in the base point of the assembly 
        in the obj_bp parameter
        
        **Parameters:**
        
        * **obj_bp** (bpy.types.object, (optional))
        
        **Returns:** None
        """
        if obj_bp:
            self.obj_bp = obj_bp
            for child in obj_bp.children:
                if "ISXDIM" in child:
                    self.obj_x = child
                if "ISYDIM" in child:
                    self.obj_y = child
                if "ISZDIM" in child:
                    self.obj_z = child
                if self.obj_x and self.obj_y and self.obj_z:
                    break    
    
    def create_assembly(self):
        """ 
        This creates the basic structure for an assembly.
        This must be called first when creating an assembly from a script.
        """
        
        self.obj_bp = bpy.data.objects.new("ASSEMBLY.Base_Point",None)
        self.obj_bp["ISBP"] = True
        self.obj_bp.empty_draw_type = 'SPHERE'
        self.obj_bp.empty_draw_size = .05
        bpy.context.scene.objects.link(self.obj_bp)
        
        self.obj_x = bpy.data.objects.new("ASSEMBLY.X_DIM",None)
        self.obj_x["ISXDIM"] = True
        self.obj_x.empty_draw_type = 'PLAIN_AXES'
        self.obj_x.empty_draw_size = .05
        self.obj_x.lock_location = (False,True,True)
        bpy.context.scene.objects.link(self.obj_x)
        self.obj_x.parent = self.obj_bp
        
        self.obj_y = bpy.data.objects.new("ASSEMBLY.Y_DIM",None)
        self.obj_y["ISYDIM"] = True
        self.obj_y.empty_draw_type = 'CONE'
        self.obj_y.empty_draw_size = .05
        self.obj_y.lock_location = (True,False,True)
        bpy.context.scene.objects.link(self.obj_y)
        self.obj_y.parent = self.obj_bp
        
        self.obj_z = bpy.data.objects.new("ASSEMBLY.Z_DIM",None)
        self.obj_z["ISZDIM"] = True
        self.obj_z.empty_draw_type = 'SINGLE_ARROW'
        self.obj_z.empty_draw_size = .3
        self.obj_z.lock_location = (True,True,False)
        bpy.context.scene.objects.link(self.obj_z)
        self.obj_z.parent = self.obj_bp
        
    def x_loc(self,expression="",expression_vars=[],value=0):
        self.obj_bp.location.x = value
        
    def y_loc(self,expression="",expression_vars=[],value=0):
        self.obj_bp.location.y = value
        
    def z_loc(self,expression="",expression_vars=[],value=0):
        self.obj_bp.location.z = value           
        
    def x_rot(self,expression="",expression_vars=[],value=0):
        self.obj_bp.rotation_euler.x = value
        
    def y_rot(self,expression="",expression_vars=[],value=0):
        self.obj_bp.rotation_euler.y = value
        
    def z_rot(self,expression="",expression_vars=[],value=0):
        self.obj_bp.rotation_euler.z = value          
        
    def x_dim(self,expression="",expression_vars=[],value=0):
        self.obj_x.location.x = value
        
    def y_dim(self,expression="",expression_vars=[],value=0):
        self.obj_y.location.y = value
        
    def z_dim(self,expression="",expression_vars=[],value=0):
        self.obj_z.location.z = value   
        
    def add_mesh(self,name,include_hooks = True):
        """
        Adds a mesh to the assembly that fills the entire assembly
        
        **Parameters:**
        
        * **name** (string)
        * **include_hooks** (boolean, (optional))

        **Returns:** bpy.types.Object
        
        """
        width = self.obj_x.location.x
        height = self.obj_z.location.z
        depth = self.obj_y.location.y
        
        verts = [(0.0, 0.0, 0.0),
                 (0.0, depth, 0.0),
                 (width, depth, 0.0),
                 (width, 0.0, 0.0),
                 (0.0, 0.0, height),
                 (0.0, depth, height),
                 (width, depth, height),
                 (width, 0.0, height),
                 ]
    
        faces = [(0, 1, 2, 3),
                 (4, 7, 6, 5),
                 (0, 4, 5, 1),
                 (1, 5, 6, 2),
                 (2, 6, 7, 3),
                 (4, 0, 3, 7),
                ]
        
        mesh = bpy.data.meshes.new(name)
        
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
        obj_mesh.parent = self.obj_bp
        
        if include_hooks:
            vg_x_dim = obj_mesh.vertex_groups.new(name="X Dimension")
            vg_x_dim.add([2,3,6,7],1,'ADD')
            
            vg_y_dim = obj_mesh.vertex_groups.new(name="Y Dimension")
            vg_y_dim.add([1,2,5,6],1,'ADD')
            
            vg_z_dim = obj_mesh.vertex_groups.new(name="Z Dimension")
            vg_z_dim.add([4,5,6,7],1,'ADD')
            
            hook_vertex_group_to_object(obj_mesh,"X Dimension",self.obj_x)
            hook_vertex_group_to_object(obj_mesh,"Y Dimension",self.obj_y)
            hook_vertex_group_to_object(obj_mesh,"Z Dimension",self.obj_z)
            
        return obj_mesh