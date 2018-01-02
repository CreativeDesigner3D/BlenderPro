'''
Utility Functions
'''

import bpy
from bpy_extras import view3d_utils

def delete_obj_list(obj_list):
    """ This function deletes every object in the list
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in obj_list:
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                if driver.data_path in {'hide','hide_select'}: # THESE DRIVERS MUST BE REMOVED TO DELETE OBJECTS
                    obj.driver_remove(driver.data_path) 
        
        obj.parent = None
        obj.hide_select = False
        obj.hide = False
        obj.select = True
        
        if obj.name in bpy.context.scene.objects:
            bpy.context.scene.objects.unlink(obj)

#   I HAVE HAD PROBLEMS WITH THIS CRASHING BLENDER
#   HOPEFULLY THE do_unlink PARAMETER WORKS
    for obj in obj_list:
        bpy.data.objects.remove(obj,do_unlink=True)
        
def delete_object_and_children(obj_bp):
    """ Deletes a object and all it's children
    """
    obj_list = []
    obj_list.append(obj_bp)
    for child in obj_bp.children:
        if len(child.children) > 0:
            delete_object_and_children(child)
        else:
            obj_list.append(child)
    delete_obj_list(obj_list)

def get_selection_point(context, event, ray_max=10000.0,objects=None,floor=None):
    """Gets the point to place an object based on selection"""
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_target = ray_origin + view_vector
 
    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""
 
        for obj in context.visible_objects:
             
            if objects:
                if obj in objects:
                    yield (obj, obj.matrix_world.copy())
             
            else:
                if floor is not None and obj == floor:
                    yield (obj, obj.matrix_world.copy())
                     
#                 if obj.draw_type != 'WIRE':
                if obj.type == 'MESH':
                    yield (obj, obj.matrix_world.copy())

                if obj.dupli_type != 'NONE':
                    obj.dupli_list_create(scene)
                    for dob in obj.dupli_list:
                        obj_dupli = dob.object
                        if obj_dupli.type == 'MESH':
                            yield (obj_dupli, dob.matrix.copy())
 
            obj.dupli_list_clear()
 
    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""
        try:
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv * ray_origin
            ray_target_obj = matrix_inv * ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj
     
            # cast the ray
            success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
     
            if success:
                return location, normal, face_index
            else:
                return None, None, None
        except:
            print("ERROR IN obj_ray_cast",obj)
            return None, None, None
             
    best_length_squared = ray_max * ray_max
    best_obj = None
    best_hit = scene.cursor_location
    for obj, matrix in visible_objects_and_duplis():
        if obj.type == 'MESH':
            if obj.data:
                hit, normal, face_index = obj_ray_cast(obj, matrix)
                if hit is not None:
                    hit_world = matrix * hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if length_squared < best_length_squared:
                        best_hit = hit_world
                        best_length_squared = length_squared
                        best_obj = obj
                        
    return best_hit, best_obj