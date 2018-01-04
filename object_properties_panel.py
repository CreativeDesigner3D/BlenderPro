import bpy
import math
from bpy.app.translations import pgettext_iface as iface_ #for decimate modifier
from . import unit, utils

enum_object_tabs = [('INFO'," ","Show the Main Information"),
                    ('DISPLAY',"","Show Options for how the Object is Displayed"),
                    ('MATERIAL',"","Show the materials assign to the object"),
                    ('CONSTRAINTS',"","Show the constraints assigned to the object"),
                    ('MODIFIERS',"","Show the modifiers assigned to the object"),
                    ('MESHDATA',"","Show the Mesh Data Information"),
                    ('CURVEDATA',"","Show the Curve Data Information"),
                    ('TEXTDATA',"","Show the Text Data Information"),
                    ('EMPTYDATA',"","Show the Empty Data Information"),
                    ('LIGHTDATA',"","Show the Light Data Information"),
                    ('CAMERADATA',"","Show the Camera Data Information"),
                    ('DRIVERS',"","Show the Drivers assigned to the Object")]     

def draw_modifier(mod,layout,obj):
    
    def draw_show_expanded(mod,layout):
        if mod.show_expanded:
            layout.prop(mod,'show_expanded',text="",emboss=False)
        else:
            layout.prop(mod,'show_expanded',text="",emboss=False)
    
    def draw_apply_close(layout,mod_name):
        layout.operator('object.modifier_apply',text="",icon='EDIT',emboss=False).modifier = mod.name
        layout.operator('object.modifier_remove',text="",icon='PANEL_CLOSE',emboss=False).modifier = mod.name
    
    def draw_array_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_ARRAY')
        draw_apply_close(row,mod.name)
        
        if mod.show_expanded:
            box = col.box()
            box.prop(mod, "fit_type")
    
            if mod.fit_type == 'FIXED_COUNT':
                box.prop(mod, "count")
            elif mod.fit_type == 'FIT_LENGTH':
                box.prop(mod, "fit_length")
            elif mod.fit_type == 'FIT_CURVE':
                box.prop(mod, "curve")
    
            box.separator()
    
            split = box.split()
    
            col = split.column()
            col.prop(mod, "use_constant_offset")
            sub = col.column()
            sub.active = mod.use_constant_offset
            sub.prop(mod, "constant_offset_displace", text="")
    
            col.separator()
    
            col.prop(mod, "use_merge_vertices", text="Merge")
            sub = col.column()
            sub.active = mod.use_merge_vertices
            sub.prop(mod, "use_merge_vertices_cap", text="First Last")
            sub.prop(mod, "merge_threshold", text="Distance")
    
            col = split.column()
            col.prop(mod, "use_relative_offset")
            sub = col.column()
            sub.active = mod.use_relative_offset
            sub.prop(mod, "relative_offset_displace", text="")
    
            col.separator()
    
            col.prop(mod, "use_object_offset")
            sub = col.column()
            sub.active = mod.use_object_offset
            sub.prop(mod, "offset_object", text="")
    
            box.separator()
    
            box.prop(mod, "start_cap")
            box.prop(mod, "end_cap")
            
    def draw_bevel_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_BEVEL')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.prop(mod, "width")
            col.prop(mod, "segments")
            col.prop(mod, "profile")
    
            col = split.column()
            col.prop(mod, "use_only_vertices")
            col.prop(mod, "use_clamp_overlap")
    
            box.label(text="Limit Method:")
            box.row().prop(mod, "limit_method", expand=True)
            if mod.limit_method == 'ANGLE':
                box.prop(mod, "angle_limit")
            elif mod.limit_method == 'VGROUP':
                box.label(text="Vertex Group:")
                box.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
    
            box.label(text="Width Method:")
            box.row().prop(mod, "offset_type", expand=True)
    
    def draw_boolean_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_BOOLEAN')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.label(text="Operation:")
            col.prop(mod, "operation", text="")
    
            col = split.column()
            col.label(text="Object:")
            col.prop(mod, "object", text="")
    
    def draw_curve_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_CURVE')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.label(text="Object:")
            col.prop(mod, "object", text="")
            col = split.column()
            col.label(text="Vertex Group:")
            col.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
            box.label(text="Deformation Axis:")
            box.row().prop(mod, "deform_axis", expand=True)
    
    def draw_decimate_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_DECIM')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            decimate_type = mod.decimate_type
    
            row = box.row()
            row.prop(mod, "decimate_type", expand=True)
    
            if decimate_type == 'COLLAPSE':
                box.prop(mod, "ratio")
    
                split = box.split()
                row = split.row(align=True)
                row.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
                row.prop(mod, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
    
                split.prop(mod, "use_collapse_triangulate")
            elif decimate_type == 'UNSUBDIV':
                box.prop(mod, "iterations")
            else:  # decimate_type == 'DISSOLVE':
                box.prop(mod, "angle_limit")
                box.prop(mod, "use_dissolve_boundaries")
                box.label("Delimit:")
                row = box.row()
                row.prop(mod, "delimit")
    
            box.label(text=iface_("Face Count: %d") % mod.face_count, translate=False)
    
    def draw_edge_split_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_EDGESPLIT')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.prop(mod, "use_edge_angle", text="Edge Angle")
            sub = col.column()
            sub.active = mod.use_edge_angle
            sub.prop(mod, "split_angle")
    
            split.prop(mod, "use_edge_sharp", text="Sharp Edges")
    
    def draw_hook_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='HOOK')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.label(text="Object:")
            col.prop(mod, "object", text="")
            if mod.object and mod.object.type == 'ARMATURE':
                col.label(text="Bone:")
                col.prop_search(mod, "subtarget", mod.object.data, "bones", text="")
            col = split.column()
            col.label(text="Vertex Group:")
            col.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
    
            layout.separator()
    
            split = box.split()
    
#             col = split.column()
#             col.prop(mod, "falloff")
#             col.prop(mod, "force", slider=True)
    
            col = split.column()
            col.operator("object.hook_reset", text="Reset")
            col.operator("object.hook_recenter", text="Recenter")
    
            if obj.mode == 'EDIT':
                layout.separator()
                row = layout.row()
                row.operator("object.hook_select", text="Select")
                row.operator("object.hook_assign", text="Assign")
    
    def draw_mask_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_MASK')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.label(text="Mode:")
            col.prop(mod, "mode", text="")
    
            col = split.column()
            if mod.mode == 'ARMATURE':
                col.label(text="Armature:")
                col.prop(mod, "armature", text="")
            elif mod.mode == 'VERTEX_GROUP':
                col.label(text="Vertex Group:")
                row = col.row(align=True)
                row.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
                sub = row.row(align=True)
                sub.active = bool(mod.vertex_group)
                sub.prop(mod, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
    
    def draw_mirror_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_MIRROR')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split(percentage=0.25)
    
            col = split.column()
            col.label(text="Axis:")
            col.prop(mod, "use_x")
            col.prop(mod, "use_y")
            col.prop(mod, "use_z")
    
            col = split.column()
            col.label(text="Options:")
            col.prop(mod, "use_mirror_merge", text="Merge")
            col.prop(mod, "use_clip", text="Clipping")
            col.prop(mod, "use_mirror_vertex_groups", text="Vertex Groups")
    
            col = split.column()
            col.label(text="Textures:")
            col.prop(mod, "use_mirror_u", text="U")
            col.prop(mod, "use_mirror_v", text="V")
    
            col = box.column()
    
            if mod.use_mirror_merge is True:
                col.prop(mod, "merge_threshold")
            col.label(text="Mirror Object:")
            col.prop(mod, "mirror_object", text="") 
    
    def draw_solidify_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_SOLIDIFY')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            split = box.split()
    
            col = split.column()
            col.prop(mod, "thickness")
            col.prop(mod, "thickness_clamp")
    
            col.separator()
    
            row = col.row(align=True)
            row.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
            sub = row.row(align=True)
            sub.active = bool(mod.vertex_group)
            sub.prop(mod, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
    
            sub = col.row()
            sub.active = bool(mod.vertex_group)
            sub.prop(mod, "thickness_vertex_group", text="Factor")
    
            col.label(text="Crease:")
            col.prop(mod, "edge_crease_inner", text="Inner")
            col.prop(mod, "edge_crease_outer", text="Outer")
            col.prop(mod, "edge_crease_rim", text="Rim")
    
            col = split.column()
    
            col.prop(mod, "offset")
            col.prop(mod, "use_flip_normals")
    
            col.prop(mod, "use_even_offset")
            col.prop(mod, "use_quality_normals")
            col.prop(mod, "use_rim")
    
            col.separator()
    
            col.label(text="Material Index Offset:")
    
            sub = col.column()
            row = sub.split(align=True, percentage=0.4)
            row.prop(mod, "material_offset", text="")
            row = row.row(align=True)
            row.active = mod.use_rim
            row.prop(mod, "material_offset_rim", text="Rim")
    
    def draw_subsurf_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_SUBSURF')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            box.row().prop(mod, "subdivision_type", expand=True)
    
            split = box.split()
            col = split.column()
            col.label(text="Subdivisions:")
            col.prop(mod, "levels", text="View")
            col.prop(mod, "render_levels", text="Render")
    
            col = split.column()
            col.label(text="Options:")
            col.prop(mod, "use_subsurf_uv")
            col.prop(mod, "show_only_control_edges")
    
    def draw_skin_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_SKIN')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            box.operator("object.skin_armature_create", text="Create Armature")
    
            box.separator()
    
            col = box.column(align=True)
            col.prop(mod, "branch_smoothing")
            col.prop(mod, "use_smooth_shade")
    
            split = box.split()
    
            col = split.column()
            col.label(text="Selected Vertices:")
            sub = col.column(align=True)
            sub.operator("object.skin_loose_mark_clear", text="Mark Loose").action = 'MARK'
            sub.operator("object.skin_loose_mark_clear", text="Clear Loose").action = 'CLEAR'
    
            sub = col.column()
            sub.operator("object.skin_root_mark", text="Mark Root")
            sub.operator("object.skin_radii_equalize", text="Equalize Radii")
    
            col = split.column()
            col.label(text="Symmetry Axes:")
            col.prop(mod, "use_x_symmetry")
            col.prop(mod, "use_y_symmetry")
            col.prop(mod, "use_z_symmetry")
    
    def draw_triangulate_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_TRIANGULATE')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            row = box.row()
    
            col = row.column()
            col.label(text="Quad Method:")
            col.prop(mod, "quad_method", text="")
            col = row.column()
            col.label(text="Ngon Method:")
            col.prop(mod, "ngon_method", text="")  
    
    def draw_simple_deform_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_SIMPLEDEFORM')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            box.row().prop(mod, "deform_method", expand=True)
    
            split = box.split()
    
            col = split.column()
            col.label(text="Vertex Group:")
            col.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
    
            split = box.split()
    
            col = split.column()
            col.label(text="Origin:")
            col.prop(mod, "origin", text="")
    
            if mod.deform_method in {'TAPER', 'STRETCH', 'TWIST'}:
                col.label(text="Lock:")
                col.prop(mod, "lock_x")
                col.prop(mod, "lock_y")
    
            col = split.column()
            col.label(text="Deform:")
            if mod.deform_method in {'TAPER', 'STRETCH'}:
                col.prop(mod, "factor")
            else:
                col.prop(mod, "angle")
            col.prop(mod, "limits", slider=True)
    
    def draw_wireframe_modifier(layout):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        draw_show_expanded(mod,row)
        row.prop(mod,'name',text="",icon='MOD_WIREFRAME')
        draw_apply_close(row,mod.name)
        if mod.show_expanded:
            box = col.box()
            has_vgroup = bool(mod.vertex_group)
    
            split = box.split()
    
            col = split.column()
            col.prop(mod, "thickness", text="Thickness")
    
            row = col.row(align=True)
            row.prop_search(mod, "vertex_group", obj, "vertex_groups", text="")
            sub = row.row(align=True)
            sub.active = has_vgroup
            sub.prop(mod, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
            row = col.row(align=True)
            row.active = has_vgroup
            row.prop(mod, "thickness_vertex_group", text="Factor")
    
            col.prop(mod, "use_crease", text="Crease Edges")
            col.prop(mod, "crease_weight", text="Crease Weight")
    
            col = split.column()
    
            col.prop(mod, "offset")
            col.prop(mod, "use_even_offset", text="Even Thickness")
            col.prop(mod, "use_relative_offset", text="Relative Thickness")
            col.prop(mod, "use_boundary", text="Boundary")
            col.prop(mod, "use_replace", text="Replace Original")
    
            col.prop(mod, "material_offset", text="Material Offset")                            
    
    if mod.type == 'ARRAY':
        draw_array_modifier(layout)
    elif mod.type == 'BEVEL':
        draw_bevel_modifier(layout)
    elif mod.type == 'BOOLEAN':
        draw_boolean_modifier(layout)
    elif mod.type == 'CURVE':
        draw_curve_modifier(layout)
    elif mod.type == 'DECIMATE':
        draw_decimate_modifier(layout)
    elif mod.type == 'EDGE_SPLIT':
        draw_edge_split_modifier(layout)
    elif mod.type == 'HOOK':
        draw_hook_modifier(layout)
    elif mod.type == 'MASK':
        draw_mask_modifier(layout)
    elif mod.type == 'MIRROR':
        draw_mirror_modifier(layout)
    elif mod.type == 'SOLIDIFY':
        draw_solidify_modifier(layout)
    elif mod.type == 'SUBSURF':
        draw_subsurf_modifier(layout)
    elif mod.type == 'SKIN':
        draw_skin_modifier(layout)
    elif mod.type == 'SIMPLE_DEFORM':
        draw_simple_deform_modifier(layout)
    elif mod.type == 'TRIANGULATE':
        draw_triangulate_modifier(layout)
    elif mod.type == 'WIREFRAME':
        draw_wireframe_modifier(layout)
    else:
        row = layout.row()
        row.label(mod.name + " view ")
    
def draw_constraint(con,layout,obj):

    def draw_show_expanded(con,layout):
        if con.show_expanded:
            layout.prop(con,'show_expanded',text="",emboss=False)
        else:
            layout.prop(con,'show_expanded',text="",emboss=False)

    def space_template(layout, con, target=True, owner=True):
        if target or owner:

            split = layout.split(percentage=0.2)

            split.label(text="Space:")
            row = split.row()

            if target:
                row.prop(con, "target_space", text="")

            if target and owner:
                row.label(icon='ARROW_LEFTRIGHT')

            if owner:
                row.prop(con, "owner_space", text="")

    def target_template(layout, con, subtargets=True):
        layout.prop(con, "target")  # XXX limiting settings for only 'curves' or some type of object

        if con.target and subtargets:
            if con.target.type == 'ARMATURE':
                layout.prop_search(con, "subtarget", con.target.data, "bones", text="Bone")

                if hasattr(con, "head_tail"):
                    row = layout.row()
                    row.label(text="Head/Tail:")
                    row.prop(con, "head_tail", text="")
            elif con.target.type in {'MESH', 'LATTICE'}:
                layout.prop_search(con, "subtarget", con.target, "vertex_groups", text="Vertex Group")

    def draw_copy_location_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:
            target_template(box, con)
            
            split = box.split()
    
            col = split.column()
            col.prop(con, "use_x", text="X")
            sub = col.column()
            sub.active = con.use_x
            sub.prop(con, "invert_x", text="Invert")
    
            col = split.column()
            col.prop(con, "use_y", text="Y")
            sub = col.column()
            sub.active = con.use_y
            sub.prop(con, "invert_y", text="Invert")
    
            col = split.column()
            col.prop(con, "use_z", text="Z")
            sub = col.column()
            sub.active = con.use_z
            sub.prop(con, "invert_z", text="Invert")
    
            box.prop(con, "use_offset")
    
            space_template(box, con)
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")            
     
    def draw_copy_rotation_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            target_template(box, con)
    
            split = box.split()
    
            col = split.column()
            col.prop(con, "use_x", text="X")
            sub = col.column()
            sub.active = con.use_x
            sub.prop(con, "invert_x", text="Invert")
    
            col = split.column()
            col.prop(con, "use_y", text="Y")
            sub = col.column()
            sub.active = con.use_y
            sub.prop(con, "invert_y", text="Invert")
    
            col = split.column()
            col.prop(con, "use_z", text="Z")
            sub = col.column()
            sub.active = con.use_z
            sub.prop(con, "invert_z", text="Invert")
    
            box.prop(con, "use_offset")
    
            space_template(box, con) 
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")            
    
    def draw_copy_scale_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            target_template(box, con)
    
            row = box.row(align=True)
            row.prop(con, "use_x", text="X")
            row.prop(con, "use_y", text="Y")
            row.prop(con, "use_z", text="Z")
    
            box.prop(con, "use_offset")
    
            space_template(box, con)
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")  
    
    def draw_copy_transforms_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            target_template(box, con)

            space_template(box, con)
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")  
    
    def draw_limit_distance_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            target_template(box, con)
    
            col = box.column(align=True)
            col.prop(con, "distance")
            col.operator("constraint.limitdistance_reset")
    
            row = box.row()
            row.label(text="Clamp Region:")
            row.prop(con, "limit_mode", text="")
    
            row = box.row()
            row.prop(con, "use_transform_limit")
            row.label()
    
            space_template(box, con) 
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")  
    
    def draw_limit_location_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            split = box.split()
    
            col = split.column()
            col.prop(con, "use_min_x")
            sub = col.column()
            sub.active = con.use_min_x
            sub.prop(con, "min_x", text="")
            col.prop(con, "use_max_x")
            sub = col.column()
            sub.active = con.use_max_x
            sub.prop(con, "max_x", text="")
    
            col = split.column()
            col.prop(con, "use_min_y")
            sub = col.column()
            sub.active = con.use_min_y
            sub.prop(con, "min_y", text="")
            col.prop(con, "use_max_y")
            sub = col.column()
            sub.active = con.use_max_y
            sub.prop(con, "max_y", text="")
    
            col = split.column()
            col.prop(con, "use_min_z")
            sub = col.column()
            sub.active = con.use_min_z
            sub.prop(con, "min_z", text="")
            col.prop(con, "use_max_z")
            sub = col.column()
            sub.active = con.use_max_z
            sub.prop(con, "max_z", text="")
    
            row = box.row()
            row.prop(con, "use_transform_limit")
            row.label()
    
            row = box.row()
            row.label(text="Convert:")
            row.prop(con, "owner_space", text="")
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")  
    
    def draw_limit_rotation_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            split = box.split()
    
            col = split.column(align=True)
            col.prop(con, "use_limit_x")
            sub = col.column(align=True)
            sub.active = con.use_limit_x
            sub.prop(con, "min_x", text="Min")
            sub.prop(con, "max_x", text="Max")
    
            col = split.column(align=True)
            col.prop(con, "use_limit_y")
            sub = col.column(align=True)
            sub.active = con.use_limit_y
            sub.prop(con, "min_y", text="Min")
            sub.prop(con, "max_y", text="Max")
    
            col = split.column(align=True)
            col.prop(con, "use_limit_z")
            sub = col.column(align=True)
            sub.active = con.use_limit_z
            sub.prop(con, "min_z", text="Min")
            sub.prop(con, "max_z", text="Max")
    
            box.prop(con, "use_transform_limit")
    
            row = box.row()
            row.label(text="Convert:")
            row.prop(con, "owner_space", text="")
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")   
    
    def draw_limit_scale_constraint(layout):
        col = layout.column(align=True)
        box = col.template_constraint(con)

        if con.show_expanded:        
            split = box.split()
    
            col = split.column()
            col.prop(con, "use_min_x")
            sub = col.column()
            sub.active = con.use_min_x
            sub.prop(con, "min_x", text="")
            col.prop(con, "use_max_x")
            sub = col.column()
            sub.active = con.use_max_x
            sub.prop(con, "max_x", text="")
    
            col = split.column()
            col.prop(con, "use_min_y")
            sub = col.column()
            sub.active = con.use_min_y
            sub.prop(con, "min_y", text="")
            col.prop(con, "use_max_y")
            sub = col.column()
            sub.active = con.use_max_y
            sub.prop(con, "max_y", text="")
    
            col = split.column()
            col.prop(con, "use_min_z")
            sub = col.column()
            sub.active = con.use_min_z
            sub.prop(con, "min_z", text="")
            col.prop(con, "use_max_z")
            sub = col.column()
            sub.active = con.use_max_z
            sub.prop(con, "max_z", text="")
    
            row = box.row()
            row.prop(con, "use_transform_limit")
            row.label()
    
            row = box.row()
            row.label(text="Convert:")
            row.prop(con, "owner_space", text="")
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")                     
            
    if con.type == 'COPY_LOCATION':
        draw_copy_location_constraint(layout)
    elif con.type == 'COPY_ROTATION':
        draw_copy_rotation_constraint(layout)
    elif con.type == 'COPY_SCALE':
        draw_copy_scale_constraint(layout)
    elif con.type == 'COPY_TRANSFORMS':
        draw_copy_transforms_constraint(layout)
    elif con.type == 'LIMIT_DISTANCE':
        draw_limit_distance_constraint(layout)
    elif con.type == 'LIMIT_LOCATION':
        draw_limit_location_constraint(layout)
    elif con.type == 'LIMIT_ROTATION':
        draw_limit_rotation_constraint(layout)
    elif con.type == 'LIMIT_SCALE':
        draw_limit_scale_constraint(layout)
    else:
        row = layout.row()
        row.label(con.name + " view ")            

def draw_object_properties(layout,obj,context):
    props = get_scene_props(bpy.context.scene)
    col = layout.column(align=True)
    box = col.box()
    col = box.column(align=True)
    row = col.row(align=True)
    draw_object_tabs(row,obj)
    box = col.box()
    col = box.column()
    if props.tabs == 'INFO':
        draw_object_info(col,obj)
    if props.tabs == 'DISPLAY':
#         box = col.box()
        row = col.row()
        row.prop(obj,'draw_type',expand=True)
        box.prop(obj,'hide_select')
        box.prop(obj,'hide')
        box.prop(obj,'hide_render')
        box.prop(obj,'show_x_ray',icon='GHOST_ENABLED',text='Show X-Ray')
        box.prop(obj.cycles_visibility,'camera',icon='CAMERA_DATA',text='Show in Viewport Render')
    if props.tabs == 'MATERIAL':
        draw_object_materials(col,obj,context)
    if props.tabs == 'CONSTRAINTS':
#         row = col.row()
        col.operator_menu_enum("object.constraint_add", "type", text="Add Constraint",icon='CONSTRAINT_DATA')
#         row.operator_menu_enum("fd_object.add_constraint", "type", icon='CONSTRAINT_DATA')
#         row.operator("fd_object.collapse_all_constraints",text="",icon='FULLSCREEN_EXIT')
        for con in obj.constraints:
            draw_constraint(con,col,obj)
    if props.tabs == 'MODIFIERS':
#         row = col.row()
        col.operator_menu_enum("object.modifier_add", "type",icon='MODIFIER')
#         row.operator("fd_object.collapse_all_modifiers",text="",icon='FULLSCREEN_EXIT')
        for mod in obj.modifiers:
            draw_modifier(mod,col,obj)
    if props.tabs == 'MESHDATA':
        pass
    if props.tabs == 'CURVEDATA':
        pass
    if props.tabs == 'TEXTDATA':
        pass
    if props.tabs == 'EMPTYDATA':
        pass
    if props.tabs == 'LIGHTDATA':
        pass
    if props.tabs == 'CAMERADATA':
        pass
    if props.tabs == 'DRIVERS':
        draw_object_drivers(col,obj)

def draw_object_tabs(layout,obj):
    props = get_scene_props(bpy.context.scene)
    layout.prop_enum(props, "tabs", 'INFO', icon="BLANK1" if props.tabs == 'INFO' else "INFO", text="Info" if props.tabs == 'INFO' else "") 
    if obj.type == 'MESH':
        layout.prop_enum(props, "tabs", 'DISPLAY', icon="BLANK1" if props.tabs == 'DISPLAY' else "RESTRICT_VIEW_OFF", text="Display" if props.tabs == 'DISPLAY' else "") 
        layout.prop_enum(props, "tabs", 'MATERIAL', icon="BLANK1" if props.tabs == 'MATERIAL' else "MATERIAL", text="Material" if props.tabs == 'MATERIAL' else "") 
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon="BLANK1" if props.tabs == 'CONSTRAINTS' else "CONSTRAINT", text="Constraints" if props.tabs == 'CONSTRAINTS' else "") 
        layout.prop_enum(props, "tabs", 'MODIFIERS', icon="BLANK1" if props.tabs == 'MODIFIERS' else "MODIFIER", text="Modifiers" if props.tabs == 'MODIFIERS' else "") 
        layout.prop_enum(props, "tabs", 'MESHDATA', icon="BLANK1" if props.tabs == 'MESHDATA' else "MESH_DATA", text="Data" if props.tabs == 'MESHDATA' else "")  
    if obj.type == 'CURVE':
        layout.prop_enum(props, "tabs", 'DISPLAY', icon='RESTRICT_VIEW_OFF', text="") 
        layout.prop_enum(props, "tabs", 'MATERIAL', icon='MATERIAL', text="") 
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon='CONSTRAINT', text="") 
        layout.prop_enum(props, "tabs", 'MODIFIERS', icon='MODIFIER', text="") 
        layout.prop_enum(props, "tabs", 'CURVEDATA', icon='CURVE_DATA', text="")  
    if obj.type == 'FONT':
        layout.prop_enum(props, "tabs", 'DISPLAY', icon='RESTRICT_VIEW_OFF', text="") 
        layout.prop_enum(props, "tabs", 'MATERIAL', icon='MATERIAL', text="") 
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon='CONSTRAINT', text="") 
        layout.prop_enum(props, "tabs", 'MODIFIERS', icon='MODIFIER', text="") 
        layout.prop_enum(props, "tabs", 'TEXTDATA', icon='FONT_DATA', text="")  
    if obj.type == 'EMPTY':
        layout.prop_enum(props, "tabs", 'DISPLAY', icon='RESTRICT_VIEW_OFF', text="") 
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon='CONSTRAINT', text="") 
        layout.prop_enum(props, "tabs", 'EMPTYDATA', icon='EMPTY_DATA', text="")  
    if obj.type == 'LAMP':
        layout.prop_enum(props, "tabs", 'DISPLAY', icon='RESTRICT_VIEW_OFF', text="") 
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon='CONSTRAINT', text="") 
        layout.prop_enum(props, "tabs", 'LIGHTDATA', icon='LAMP_SPOT', text="")  
    if obj.type == 'CAMERA':
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon='CONSTRAINT', text="") 
        layout.prop_enum(props, "tabs", 'CAMERADATA', icon='OUTLINER_DATA_CAMERA', text="")
    if obj.type == 'ARMATURE':
        layout.prop_enum(props, "tabs", 'DISPLAY', icon='RESTRICT_VIEW_OFF', text="") 
        layout.prop_enum(props, "tabs", 'CONSTRAINTS', icon='CONSTRAINT', text="")
    layout.prop_enum(props, "tabs", 'DRIVERS', icon="BLANK1" if props.tabs == 'DRIVERS' else "AUTO", text="Drivers" if props.tabs == 'DRIVERS' else "")
    
def draw_object_info(layout,obj):
#     box = layout.box()
    row = layout.row()
    row.prop(obj,'name')
    if obj.type in {'MESH','CURVE','LATTICE','TEXT'}:
        pass
#         row.operator('fd_object.toggle_edit_mode',text="",icon='EDITMODE_HLT').object_name = obj.name
    
    has_hook_modifier = False
    for mod in obj.modifiers:
        if mod.type == 'HOOK':
            has_hook_modifier =  True
    
    has_shape_keys = False
    if obj.type == 'MESH':
        if obj.data.shape_keys:
            if len(obj.data.shape_keys.key_blocks) > 0:
                has_shape_keys = True
    
    if has_hook_modifier or has_shape_keys:
        row = layout.row()
        col = row.column(align=True)
        col.label("Dimension")
        col.label("X: " + str(obj.dimensions.x))
        col.label("Y: " + str(obj.dimensions.y))
        col.label("Z: " + str(obj.dimensions.z))
        col = row.column(align=True)
        col.label("Location")
        col.label("X: " + str(obj.location.x))
        col.label("Y: " + str(obj.location.y))
        col.label("Z: " + str(obj.location.z))
        col = row.column(align=True)
        col.label("Rotation")
        col.label("X: " + str(round(math.degrees(obj.rotation_euler.x),4)))
        col.label("Y: " + str(round(math.degrees(obj.rotation_euler.y),4)))
        col.label("Z: " + str(round(math.degrees(obj.rotation_euler.z),4)))
        if has_hook_modifier:
            layout.operator("fd_object.apply_hook_modifiers",icon='HOOK').object_name = obj.name
        if has_shape_keys:
            layout.operator("fd_object.apply_shape_keys",icon='SHAPEKEY_DATA').object_name = obj.name
    else:
        if obj.type not in {'EMPTY','CAMERA','LAMP'}:
            layout.label('Dimensions:')
            col = layout.column(align=True)
            #X
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=0,text="")
            if obj.lock_scale[0]:
                row.label("X: " + str(obj.dimensions.x))
            else:
                row.prop(obj,"dimensions",index=0,text="X")
            #Y
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=1,text="")
            if obj.lock_scale[1]:
                row.label("Y: " + str(obj.dimensions.y))
            else:
                row.prop(obj,"dimensions",index=1,text="Y")
            #Z
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=2,text="")
            if obj.lock_scale[2]:
                row.label("Z: " + str(obj.dimensions.z))
            else:
                row.prop(obj,"dimensions",index=2,text="Z")
                
        col1 = layout.row()
        if obj:
            col2 = col1.split()
            col = col2.column(align=True)
            col.label('Location:')
            #X
            row = col.row(align=True)
            row.prop(obj,"lock_location",index=0,text="")
            if obj.lock_location[0]:
                row.label("X: " + str(obj.location.x))
            else:
                row.prop(obj,"location",index=0,text="X")
            #Y    
            row = col.row(align=True)
            row.prop(obj,"lock_location",index=1,text="")
            if obj.lock_location[1]:
                row.label("Y: " + str(obj.location.y))
            else:
                row.prop(obj,"location",index=1,text="Y")
            #Z    
            row = col.row(align=True)
            row.prop(obj,"lock_location",index=2,text="")
            if obj.lock_location[2]:
                row.label("Z: " + str(obj.location.z))
            else:
                row.prop(obj,"location",index=2,text="Z")
                
            col2 = col1.split()
            col = col2.column(align=True)
            col.label('Rotation:')
            #X
            row = col.row(align=True)
            row.prop(obj,"lock_rotation",index=0,text="")
            if obj.lock_rotation[0]:
                row.label("X: " + str(round(math.degrees(obj.rotation_euler.x),4)))
            else:
                row.prop(obj,"rotation_euler",index=0,text="X")
            #Y    
            row = col.row(align=True)
            row.prop(obj,"lock_rotation",index=1,text="")
            if obj.lock_rotation[1]:
                row.label("Y: " + str(round(math.degrees(obj.rotation_euler.y),4)))
            else:
                row.prop(obj,"rotation_euler",index=1,text="Y")
            #Z    
            row = col.row(align=True)
            row.prop(obj,"lock_rotation",index=2,text="")
            if obj.lock_rotation[2]:
                row.label("Y: " + str(round(math.degrees(obj.rotation_euler.z),4)))
            else:
                row.prop(obj,"rotation_euler",index=2,text="Z")
                
#     row = box.row()
#     row.prop(obj.mv,'comment')
    
def draw_object_materials(layout,obj,context):

    
    mat = None
    ob = context.object
    slot = None
    space = context.space_data
    
    if ob:
        mat = ob.active_material
    
    if ob:
        is_sortable = len(ob.material_slots) > 1
        rows = 1
        if (is_sortable):
            rows = 4

        row = layout.row()

        row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ZOOMIN', text="")
        col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

        col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

        if is_sortable:
            col.separator()

            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

#     split = layout.split(percentage=0.65)

    if ob:
        layout.template_ID(ob, "active_material", new="material.new")
        row = layout.row()

        if slot:
            row.prop(slot, "link", text="")
        else:
            row.label()
    elif mat:
        layout.template_preview(mat)
#         split.template_ID(space, "pin_id")
#         split.separator()
                
    if mat:
        layout.template_preview(mat)
    
                
    if obj.type in {'MESH','CURVE'}:
        pass
    if obj.mode == 'EDIT':
        row = layout.row(align=True)
        row.operator("object.material_slot_assign", text="Assign")
        row.operator("object.material_slot_select", text="Select")
        row.operator("object.material_slot_deselect", text="Deselect")
        
    layout.operator('fd_general.open_new_window',text="Open Material Editor",icon='NODETREE').space_type = 'NODE_EDITOR'

def draw_object_drivers(layout,obj):
    if obj:
        if not obj.animation_data:
            layout.label("There are no drivers assigned to the object",icon='ERROR')
        else:
            if len(obj.animation_data.drivers) == 0:
                layout.label("There are no drivers assigned to the object",icon='ERROR')
            for DR in obj.animation_data.drivers:
                box = layout.box()
                row = box.row()
                DriverName = DR.data_path
                if DriverName in {"location","rotation_euler","dimensions" ,"lock_scale",'lock_location','lock_rotation'}:
                    if DR.array_index == 0:
                        DriverName = DriverName + " X"
                    if DR.array_index == 1:
                        DriverName = DriverName + " Y"
                    if DR.array_index == 2:
                        DriverName = DriverName + " Z"                     
                value = eval('bpy.data.objects["' + obj.name + '"].' + DR.data_path)
                if type(value).__name__ == 'str':
                    row.label(DriverName + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'float':
                    row.label(DriverName + " = " + str(unit.meter_to_active_unit(value)),icon='AUTO')
                elif type(value).__name__ == 'int':
                    row.label(DriverName + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'bool':
                    row.label(DriverName + " = " + str(value),icon='AUTO')
                elif type(value).__name__ == 'bpy_prop_array':
                    row.label(DriverName + " = " + str(value[DR.array_index]),icon='AUTO')
                elif type(value).__name__ == 'Vector':
                    row.label(DriverName + " = " + str(unit.meter_to_active_unit(value[DR.array_index])),icon='AUTO')
                elif type(value).__name__ == 'Euler':
                    row.label(DriverName + " = " + str(unit.meter_to_active_unit(value[DR.array_index])),icon='AUTO')
                else:
                    row.label(DriverName + " = " + str(type(value)),icon='AUTO')
 
#                 props = row.operator("fd_driver.add_variable_to_object",text="",icon='ZOOMIN')
#                 props.object_name = obj.name
#                 props.data_path = DR.data_path
#                 props.array_index = DR.array_index
#                 obj_bp = utils.get_assembly_bp(obj)
#                 if obj_bp:
#                     props = row.operator('fd_driver.get_vars_from_object',text="",icon='DRIVER')
#                     props.object_name = obj.name
#                     props.var_object_name = obj_bp.name
#                     props.data_path = DR.data_path
#                     props.array_index = DR.array_index
                utils.draw_driver_expression(box,DR)
#                 draw_add_variable_operators(box,obj.name,DR.data_path,DR.array_index)
                utils.draw_driver_variables(box,DR,obj.name)

class PANEL_object_properties(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        layout.label(text="Object: " + obj.name,icon='OBJECT_DATA')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            draw_object_properties(layout,obj,context)
            
class OPS_open_new_window(bpy.types.Operator):
    bl_idname = "fd_general.open_new_window"
    bl_label = "Open New Window"

    space_type = bpy.props.StringProperty(name="Space Type")
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'USER_PREFERENCES':
                window.screen.areas[0].type = self.space_type
        return {'FINISHED'}            
            
def get_scene_props(scene):
    return scene.obj_panel
            
class scene_props(bpy.types.PropertyGroup):

    tabs = bpy.props.EnumProperty(name="type",
        items=enum_object_tabs,
        description="Select the Object Type.",
        default='INFO')       
            
            
            
def register():
    bpy.utils.register_class(PANEL_object_properties)
    bpy.utils.register_class(scene_props)
    bpy.utils.register_class(OPS_open_new_window)
    bpy.types.Scene.obj_panel = bpy.props.PointerProperty(type = scene_props)
    
def unregister():
    pass            