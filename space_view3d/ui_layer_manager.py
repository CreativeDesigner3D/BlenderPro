# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Layer Management",
    "author": "Alfonso Annarumma, Bastien Montagne",
    "version": (1, 5, 4),
    "blender": (2, 76, 0),
    "location": "Toolshelf > Layers Tab",
    "warning": "",
    "description": "Display and Edit Layer Name",
    "wiki_url": "https://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/3D_interaction/layer_manager",
    "category": "3D View",
}

import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os
import math
from bpy.app.handlers import persistent
from ..bp_lib import utils

EDIT_MODES = {'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_METABALL', 'EDIT_TEXT', 'EDIT_ARMATURE'}

NUM_LAYERS = 20

FAKE_LAYER_GROUP = [True] * NUM_LAYERS


class NamedLayer(PropertyGroup):
    name = StringProperty(
            name="Layer Name"
            )
    use_lock = BoolProperty(
            name="Lock Layer",
            default=False
            )
    use_object_select = BoolProperty(
            name="Object Select",
            default=True
            )
    use_wire = BoolProperty(
            name="Wire Layer",
            default=False
            )


class NamedLayers(PropertyGroup):
    layers = CollectionProperty(type=NamedLayer)

    use_hide_empty_layers = BoolProperty(
            name="Hide Empty Layer",
            default=False
            )
    use_extra_options = BoolProperty(
            name="Show Extra Options",
            default=True
            )
    use_layer_indices = BoolProperty(
            name="Show Layer Indices",
            default=False
            )
    use_classic = BoolProperty(
            name="Classic",
            default=False,
            description="Use a classic layer selection visibility"
            )
    use_init = BoolProperty(
            default=True,
            options={'HIDDEN'}
            )


# Stupid, but only solution currently is to use a handler to init that layers collection...
@persistent
def check_init_data(scene):
    namedlayers = scene.namedlayers
    if namedlayers.use_init:
        
        while namedlayers.layers:
            namedlayers.layers.remove(0)
        for i in range(NUM_LAYERS):
            layer = namedlayers.layers.add()
            layer.name = "Layer%.2d" % (i + 1)  # Blender use layer nums starting from 1, not 0.
        namedlayers.use_init = False
        print(namedlayers.layers)

def update_object_selection(self,context):
    if self.selected_object_index < len(context.scene.objects):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.scene.objects[self.selected_object_index]
        context.scene.objects.active = obj
        obj.select = True
    
def update_world_selection(self,context):
    if self.selected_world_index <= len(bpy.data.worlds) - 1:
        world = bpy.data.worlds[self.selected_world_index]
        context.scene.world = world  
    
def update_scene_selection(self,context):
    context.screen.scene = bpy.data.scenes[self.selected_scene_index] 
    if context.screen.scene.outliner.selected_scene_index != self.selected_scene_index:
        context.screen.scene.outliner.selected_scene_index = self.selected_scene_index
    
def update_group_selection(self,context):
    if self.selected_group_index + 1 >= len(bpy.data.groups):
        group = bpy.data.groups[self.selected_group_index]
        bpy.ops.object.select_all(action = 'DESELECT')
        for obj in group.objects:
            obj.select = True
            
def update_group_object_selection(self,context):
    if self.selected_group_index + 1 >= len(bpy.data.groups):
        group = bpy.data.groups[self.selected_group_index]
        if self.selected_group_object_index < len(group.objects):
            bpy.ops.object.select_all(action = 'DESELECT')
            obj = group.objects[self.selected_group_object_index]
            context.scene.objects.active = obj
            obj.select = True

class Outliner(PropertyGroup):
    outliner_tabs = bpy.props.EnumProperty(name="Outliner Tabs",
        items=[('SCENES',"Scenes","Show the Scene Options"),
               ('WORLDS',"Worlds","Show the World Options"),
               ('MATERIALS',"Materials","Show the Material Options"),
               ('OBJECTS',"Objects","Show the World Options"),
               ('GROUPS',"Groups","Show the Group Options"),
               ('LAYERS',"Layers","Show the Layer Options")],
        default='SCENES')
    
    selected_object_index = IntProperty(name="Selected Object Index", default=0, update = update_object_selection)
    selected_world_index = IntProperty(name="Selected World Index", default=0, update = update_world_selection)
    selected_material_index = IntProperty(name="Selected Material Index", default=0)
    selected_scene_index = IntProperty(name="Selected Scene Index", default=0, update = update_scene_selection)
    selected_group_index = IntProperty(name="Selected Group Index", default=0, update = update_group_selection)
    selected_group_object_index = IntProperty(name="Selected Group Object Index", default=0, update = update_group_object_selection)
    
    background_image_scale = FloatProperty(name="Background Image Scale",unit='LENGTH')

class SCENE_OT_namedlayer_toggle_visibility(Operator):
    """Show or hide given layer (shift to extend)"""
    bl_idname = "scene.namedlayer_toggle_visibility"
    bl_label = "Show/Hide Layer"

    layer_idx = IntProperty()
    group_idx = IntProperty()
    use_spacecheck = BoolProperty()
    extend = BoolProperty(options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.scene and (context.area.spaces.active.type == 'VIEW_3D')

    def execute(self, context):
        scene = context.scene
        layer_cont = context.area.spaces.active if self.use_spacecheck else context.scene
        layer_idx = self.layer_idx

        if layer_idx == -1:
            group_idx = self.group_idx
            layergroups = scene.layergroups[group_idx]
            group_layers = layergroups.layers
            layers = layer_cont.layers

            if layergroups.use_toggle:
                layer_cont.layers = [not group_layer and layer for group_layer, layer in zip(group_layers, layers)]
                layergroups.use_toggle = False
            else:
                layer_cont.layers = [group_layer or layer for group_layer, layer in zip(group_layers, layers)]
                layergroups.use_toggle = True
        else:
            if self.extend:
                layer_cont.layers[layer_idx] = not layer_cont.layers[layer_idx]
            else:
                layers = [False] * NUM_LAYERS
                layers[layer_idx] = True
                layer_cont.layers = layers
        return {'FINISHED'}

    def invoke(self, context, event):
        self.extend = event.shift
        return self.execute(context)


class SCENE_OT_namedlayer_move_to_layer(Operator):
    """Move selected objects to this Layer (shift to extend)"""
    bl_idname = "scene.namedlayer_move_to_layer"
    bl_label = "Move Objects To Layer"

    layer_idx = IntProperty()
    extend = BoolProperty(options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.scene

    def execute(self, context):
        layer_idx = self.layer_idx
        scene = context.scene

        # Cycle all objects in the layer
        for obj in scene.objects:
            if obj.select:
                # If object is in at least one of the scene's visible layers...
                if True in {ob_layer and sce_layer for ob_layer, sce_layer in zip(obj.layers, scene.layers)}:
                    if self.extend:
                        obj.layers[layer_idx] = not obj.layers[layer_idx]
                    else:
                        layer = [False] * NUM_LAYERS
                        layer[layer_idx] = True
                        obj.layers = layer
        return {'FINISHED'}

    def invoke(self, context, event):
        self.extend = event.shift
        return self.execute(context)


class SCENE_OT_namedlayer_toggle_wire(Operator):
    """Toggle all objects on this layer draw as wire"""
    bl_idname = "scene.namedlayer_toggle_wire"
    bl_label = "Toggle Objects Draw Wire"

    layer_idx = IntProperty()
    use_wire = BoolProperty()
    group_idx = IntProperty()

    @classmethod
    def poll(cls, context):
        return context.scene and (context.area.spaces.active.type == 'VIEW_3D')

    def execute(self, context):
        scene = context.scene
        layer_idx = self.layer_idx
        use_wire = self.use_wire

        view_3d = context.area.spaces.active

        # Check if layer have some thing
        if view_3d.layers_used[layer_idx] or layer_idx == -1:
            display = 'WIRE' if use_wire else 'TEXTURED'
            # Cycle all objects in the layer.
            for obj in context.scene.objects:
                if layer_idx == -1:
                    group_idx = self.group_idx
                    group_layers = scene.layergroups[group_idx].layers
                    layers = obj.layers
                    if True in {layer and group_layer for layer, group_layer in zip(layers, group_layers)}:
                        obj.draw_type = display
                        scene.layergroups[group_idx].use_wire = use_wire
                else:
                    if obj.layers[layer_idx]:
                        obj.draw_type = display
                        scene.namedlayers.layers[layer_idx].use_wire = use_wire

        return {'FINISHED'}


class SCENE_OT_namedlayer_lock_all(Operator):
    """Lock all objects on this layer"""
    bl_idname = "scene.namedlayer_lock_all"
    bl_label = "Lock Objects"

    layer_idx = IntProperty()
    use_lock = BoolProperty()
    group_idx = IntProperty()

    @classmethod
    def poll(cls, context):
        return context.scene and (context.area.spaces.active.type == 'VIEW_3D')

    def execute(self, context):
        scene = context.scene
        view_3d = context.area.spaces.active
        layer_idx = self.layer_idx
        group_idx = self.group_idx
        group_layers = FAKE_LAYER_GROUP if group_idx < 0 else scene.layergroups[group_idx].layers
        use_lock = self.use_lock

        # check if layer have some thing
        if layer_idx == -1 or view_3d.layers_used[layer_idx]:
            # Cycle all objects in the layer.
            for obj in context.scene.objects:
                if layer_idx == -1:
                    layers = obj.layers
                    if True in {layer and group_layer for layer, group_layer in zip(layers, group_layers)}:
                        obj.hide_select = not use_lock
                        obj.select = False
                        scene.layergroups[group_idx].use_lock = not use_lock
                else:
                    if obj.layers[layer_idx]:
                        obj.hide_select = not use_lock
                        obj.select = False
                        scene.namedlayers.layers[layer_idx].use_lock = not use_lock

        return {'FINISHED'}


class SCENE_OT_namedlayer_select_objects_by_layer(Operator):
    """Select all the objects on this Layer (shift for multi selection, ctrl to make active the last selected object)"""
    bl_idname = "scene.namedlayer_select_objects_by_layer"
    bl_label = "Select Objects In Layer"

    select_obj = BoolProperty()
    layer_idx = IntProperty()

    extend = BoolProperty(options={'SKIP_SAVE'})
    active = BoolProperty(options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.scene and (context.area.spaces.active.type == 'VIEW_3D')

    def execute(self, context):
        scene = context.scene
        view_3d = context.area.spaces.active
        select_obj = self.select_obj
        layer_idx = self.layer_idx

        not_all_selected = 0
        # check if layer have some thing
        if view_3d.layers_used[layer_idx]:
            objects = []
            for obj in context.scene.objects:
                if obj.layers[layer_idx]:
                    objects.append(obj)
                    not_all_selected -= 1
                    if self.active:
                        context.scene.objects.active = obj
                    if obj.select:
                        not_all_selected += 1
            if not not_all_selected:
                for obj in objects:
                    obj.select = False
            else:
                bpy.ops.object.select_by_layer(extend=self.extend, layers=layer_idx + 1)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.extend = event.shift
        self.active = event.ctrl
        return self.execute(context)


class SCENE_OT_namedlayer_show_all(Operator):
    """Show or hide all layers in the scene"""
    bl_idname = "scene.namedlayer_show_all"
    bl_label = "Select All Layers"

    show = BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.scene and (context.area.spaces.active.type == 'VIEW_3D')

    def execute(self, context):
        scene = context.scene
        view_3d = context.area.spaces.active
        show = self.show
        active_layer = scene.active_layer

        # check for lock camera and layer is active
        layer_cont = scene if view_3d.lock_camera_and_layers else view_3d

        if show:
            layer_cont.layers[:] = [True] * NUM_LAYERS
            # Restore active layer (stupid, but Scene.active_layer is readonly).
            layer_cont.layers[active_layer] = False
            layer_cont.layers[active_layer] = True
        else:
            layers = [False] * NUM_LAYERS
            # Keep selection of active layer
            layers[active_layer] = True
            layer_cont.layers[:] = layers

        return {'FINISHED'}


class SCENE_OT_create_new_scene(Operator):
    """Creates a New Scene"""
    bl_idname = "scene.create_new_scene"
    bl_label = "Create New Scene"

    def execute(self, context):
        bpy.ops.scene.new(type='EMPTY')
#         scene_number = 1
#         while "scene " + str(scene_number) not in bpy.data.scenes:
#             scene_number += 1
#         bpy.data.scenes.new(name="scene" )

        return {'FINISHED'}
    
class GROUP_OT_make_group_from_selection(Operator):
    bl_idname = "group.make_group_from_selection"
    bl_label = "Make Group From Selection"
    bl_description = "This will create a group from the selected objects"
    bl_options = {'UNDO'}

    group_name = StringProperty(name="Group Name",default = "New Group")

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) > 0:
            return True
        else:
            return False

    def execute(self, context):
        for obj in context.selected_objects:
            obj.hide = False
            obj.hide_select = False
            obj.select = True
        bpy.ops.group.create(name=self.group_name)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"group_name")    
    
class WORLD_OT_create_world_from_hdr(Operator):
    """Creates a New World from a HDR"""
    bl_idname = "world.create_new_world_from_hdr"
    bl_label = "Create New World From HDR"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def draw(self, context):
        self.layout.operator('file.select_all_toggle')  

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        file_path, file_name = os.path.split(self.filepath)
        filename , ext = os.path.splitext(file_name)        
        
        world = bpy.data.worlds.new(filename)
        context.scene.world = world
        new_image = bpy.data.images.load(self.filepath)
        
        world.use_nodes = True
        texture = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        texture.image = new_image
        texture.location = world.node_tree.nodes[0].location
        texture.location = (-200,300)
        
        mapping = world.node_tree.nodes.new("ShaderNodeMapping")
        mapping.location = world.node_tree.nodes[0].location
        mapping.location = (-550,300)

        texcord = world.node_tree.nodes.new("ShaderNodeTexCoord")
        texcord.location = world.node_tree.nodes[0].location
        texcord.location = (-750,300)
        
        background = world.node_tree.nodes[1]
        
        new_links = world.node_tree.links.new
        new_links(background.inputs[0], texture.outputs[0])        
        new_links(texture.inputs[0], mapping.outputs[0])
        new_links(mapping.inputs[0], texcord.outputs[0])
        
        return {'FINISHED'}
    
class SCENE_OT_set_background_image_scale(Operator):
    bl_idname = "scene.set_background_image_scale"
    bl_label = "Set Background Image Scale"
    bl_options = {'UNDO'}
    
    image_name = bpy.props.StringProperty(name="Image Name")
    
    #READONLY
    drawing_plane = None

    first_point = (0,0,0)
    second_point = (0,0,0)
    
    header_text = "Select the First Point"
    
    def cancel_drop(self,context,event):
        context.window.cursor_set('DEFAULT')
        utils.delete_obj_list([self.drawing_plane])
        return {'FINISHED'}
        
    def __del__(self):
        bpy.context.area.header_text_set()
        
    def event_is_cancel(self,event):
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'ESC' and event.value == 'PRESS':
            return True
        else:
            return False
            
    def calc_distance(self,point1,point2):
        """ This gets the distance between two points (X,Y,Z)
        """
        return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2)             

    def modal(self, context, event):
        
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        selected_point, selected_obj = utils.get_selection_point(context,event,objects=[self.drawing_plane]) #Pass in Drawing Plane
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.first_point != (0,0,0):
                    self.second_point = selected_point
                    
                    distance = self.calc_distance(self.first_point,self.second_point)
                    
                    diff = context.scene.outliner.background_image_scale / distance

                    view = context.space_data
                    for bg in view.background_images:
                        if bg.image.name == self.image_name:
                            bg_size = bg.size
                            bg.size = bg_size*diff
                    return self.cancel_drop(context,event)
                else:
                    self.first_point = selected_point

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
            
        if self.event_is_cancel(event):
            return self.cancel_drop(context,event)
            
        return {'RUNNING_MODAL'}
        
    def execute(self,context):
        view3d = context.space_data.region_3d
        self.first_point = (0,0,0)
        self.second_point = (0,0,0)
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.draw_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)
        self.drawing_plane.rotation_mode = 'QUATERNION'
        self.drawing_plane.rotation_quaternion = view3d.view_rotation
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    

class SCENE_PT_outliner(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Layer Management"
    bl_category = "Outliner"
    bl_context = "objectmode"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(self, context):
        return ((getattr(context, "mode", 'EDIT_MESH') not in EDIT_MODES) and
                (context.area.spaces.active.type == 'VIEW_3D'))

    def draw_layers_interface(self,layout,context):
        scene = context.scene
        view_3d = context.area.spaces.active
        actob = context.object
        namedlayers = scene.namedlayers
        use_extra = namedlayers.use_extra_options
        use_hide = namedlayers.use_hide_empty_layers
        use_indices = namedlayers.use_layer_indices
        use_classic = namedlayers.use_classic
                
        # Check for lock camera and layer is active
        if view_3d.lock_camera_and_layers:
            layer_cont = scene
            use_spacecheck = False
        else:
            layer_cont = view_3d
            use_spacecheck = True                
                
        row = layout.row()
        col = row.column()
        col.prop(view_3d, "lock_camera_and_layers", text="")
        # Check if there is a layer off
        show = (False in {layer for layer in layer_cont.layers})
        icon = 'RESTRICT_VIEW_ON' if show else 'RESTRICT_VIEW_OFF'
        col.operator("scene.namedlayer_show_all", emboss=False, icon=icon, text="").show = show

        col = row.column()
        col.prop(namedlayers, "use_classic")
        col.prop(namedlayers, "use_extra_options", text="Options")

        col = row.column()
        col.prop(namedlayers, "use_layer_indices", text="Indices")
        col.prop(namedlayers, "use_hide_empty_layers", text="Hide Empty")

        col = layout.column()
        for layer_idx in range(NUM_LAYERS):
            namedlayer = namedlayers.layers[layer_idx]
            is_layer_used = view_3d.layers_used[layer_idx]

            if (use_hide and not is_layer_used):
                # Hide unused layers and this one is unused, skip.
                continue

            row = col.row(align=True)

            # layer index
            if use_indices:
                sub = row.row(align=True)
                sub.alignment = 'LEFT'
                sub.label(text="%.2d." % (layer_idx + 1))

            # visualization
            icon = 'RESTRICT_VIEW_OFF' if layer_cont.layers[layer_idx] else 'RESTRICT_VIEW_ON'
            if use_classic:
                op = row.operator("scene.namedlayer_toggle_visibility", text="", icon=icon, emboss=True)
                op.layer_idx = layer_idx
                op.use_spacecheck = use_spacecheck
            else:
                row.prop(layer_cont, "layers", index=layer_idx, emboss=True, icon=icon, toggle=True, text="")

            # Name (use special icon for active layer)
            icon = 'FILE_TICK' if (getattr(layer_cont, "active_layer", -1) == layer_idx) else 'NONE'
            row.prop(namedlayer, "name", text="", icon=icon)

            if use_extra:
                use_lock = namedlayer.use_lock

                # Select by type operator
                sub = row.column(align=True)
                sub.enabled = not use_lock
                sub.operator("scene.namedlayer_select_objects_by_layer", icon='RESTRICT_SELECT_OFF',
                             text="", emboss=True).layer_idx = layer_idx

                # Lock operator
                icon = 'LOCKED' if use_lock else 'UNLOCKED'
                op = row.operator("scene.namedlayer_lock_all", text="", emboss=True, icon=icon)
                op.layer_idx = layer_idx
                op.group_idx = -1
                op.use_lock = use_lock

                # Merge layer
                # check if layer has something
                has_active = (actob and actob.layers[layer_idx])
                icon = ('LAYER_ACTIVE' if has_active else 'LAYER_USED') if is_layer_used else 'RADIOBUT_OFF'
                row.operator("scene.namedlayer_move_to_layer", text="", emboss=True, icon=icon).layer_idx = layer_idx

                # Wire view
                use_wire = namedlayer.use_wire
                icon = 'WIRE' if use_wire else 'POTATO'
                op = row.operator("scene.namedlayer_toggle_wire", text="", emboss=True, icon=icon)
                op.layer_idx = layer_idx
                op.use_wire = not use_wire

            if not (layer_idx + 1) % 5:
                col.separator()

        if len(scene.objects) == 0:
            layout.label(text="No objects in scene")

    def draw_scene_image(self,layout,view,bg,i):
        layout.active = view.show_background_images
        box = layout.box()
        row = box.row(align=True)
        row.prop(bg, "show_expanded", text="", emboss=False)
        if bg.source == 'IMAGE' and bg.image:
            row.prop(bg.image, "name", text="", emboss=False)
        elif bg.source == 'MOVIE_CLIP' and bg.clip:
            row.prop(bg.clip, "name", text="", emboss=False)
        else:
            row.label(text="Select an Image with the open button")

        if bg.show_background_image:
            row.prop(bg, "show_background_image", text="", emboss=False, icon='RESTRICT_VIEW_OFF')
        else:
            row.prop(bg, "show_background_image", text="", emboss=False, icon='RESTRICT_VIEW_ON')

        row.operator("view3d.background_image_remove", text="", emboss=False, icon='X').index = i

        if bg.show_expanded:
            
            has_bg = False
            if bg.source == 'IMAGE':
                row = box.row()
                row.template_ID(bg, "image", open="image.open")
                
                if bg.image is not None:
                    box.prop(bg, "view_axis", text="Display View")
                    box.prop(bg, "draw_depth", expand=False,text="Draw Depth")
                    has_bg = True

#                     if use_multiview and bg.view_axis in {'CAMERA', 'ALL'}:
#                         box.prop(bg.image, "use_multiview")
# 
#                         column = box.column()
#                         column.active = bg.image.use_multiview
# 
#                         column.label(text="Views Format:")
#                         column.row().prop(bg.image, "views_format", expand=True)

            elif bg.source == 'MOVIE_CLIP':
                box.prop(bg, "use_camera_clip")

                column = box.column()
                column.active = not bg.use_camera_clip
                column.template_ID(bg, "clip", open="clip.open")

                if bg.clip:
                    column.template_movieclip(bg, "clip", compact=True)

                if bg.use_camera_clip or bg.clip:
                    has_bg = True

                column = box.column()
                column.active = has_bg
                column.prop(bg.clip_user, "proxy_render_size", text="")
                column.prop(bg.clip_user, "use_render_undistorted")

            if has_bg:
                row = box.row()
                row.label("Image Opacity")
                row.prop(bg, "opacity", slider=True,text="")

                row = box.row()
                row.label("Rotation:")
                row.prop(bg, "rotation",text="")

                row = box.row()
                row.label("Location:")
                row.prop(bg, "offset_x", text="X")
                row.prop(bg, "offset_y", text="Y")

                row = box.row()
                row.label("Flip Image:")
                row.prop(bg, "use_flip_x",text="Horizontally")
                row.prop(bg, "use_flip_y",text="Vertically")

                row = box.row()
                row.prop(bpy.context.scene.outliner, "background_image_scale", text="Known Dimension")
                row.operator("scene.set_background_image_scale",text="Select Two Points",icon='MAN_TRANS').image_name = bg.image.name

                row = box.row()
                row.label("Image Size:")
                row.prop(bg, "size",text="")        

    def draw_scenes(self,layout,context):
        layout.operator("scene.create_new_scene",icon='ZOOMIN')
        
        if len(bpy.data.scenes) > 0:
            layout.template_list("FD_UL_scenes", "", bpy.data, "scenes", context.scene.outliner, "selected_scene_index", rows=4)
            unit = context.scene.unit_settings
            box = layout.box()
            box.label("Scene Properties: " + context.scene.name)
            split = box.split(percentage=0.35)
            split.label("Unit Type:")
            split.prop(unit, "system", text="")
            split = box.split(percentage=0.35)
            split.label("Angle:")
            split.prop(unit, "system_rotation", text="")

            layout.operator("view3d.background_image_add", text="Add Image",icon='ZOOMIN')
            view = context.space_data
            for i, bg in enumerate(view.background_images):
                self.draw_scene_image(layout, view, bg, i)
            
    def draw_worlds(self,layout,context):
        scene = context.scene
        world = scene.world
        view = context.space_data
        layout.operator("world.new",icon='ZOOMIN')
        layout.operator("world.create_new_world_from_hdr",icon='FILE_IMAGE')

        if len(bpy.data.worlds) > 0:
            layout.template_list("FD_UL_worlds", "", bpy.data, "worlds", scene.outliner, "selected_world_index", rows=4)
        
        box = layout.box()
        box.label("Active World Properties: " + world.name,icon='WORLD')
        box.prop(world,'name')
        box.prop(view, "show_world",text="Show World in Viewport")
        for node in world.node_tree.nodes:
            if node.bl_idname == 'ShaderNodeBackground':
                box.prop(node.inputs[1],'default_value',text="Strength")
            if node.bl_idname == 'ShaderNodeMapping':
                box.prop(node,'rotation')
        box.operator('object_props.open_new_window',text="Show Node Editor",icon='NODETREE').space_type = 'NODE_EDITOR' 
        
    def draw_materials(self,layout,context):
        scene = context.scene
        layout.operator("material.new")
        row = layout.row()
        row.scale_y = 1.3
        row.operator("library.add_material_from_library",text="Material Library",icon='EXTERNAL_DATA')        
        
        if len(bpy.data.materials) > 0:
            layout.template_list("FD_UL_materials", "", bpy.data, "materials", scene.outliner, "selected_material_index", rows=4)
        
    def draw_objects(self,layout,context):
        scene = context.scene
        layout.menu("VIEW3D_MT_add_object",text="Add Object",icon='OBJECT_DATA')
        row = layout.row()
        row.scale_y = 1.3
        row.operator("library.add_object_from_library",text="Object Library",icon='EXTERNAL_DATA')
        
        if len(scene.objects) > 0:
            layout.template_list("FD_UL_objects", "", scene, "objects", scene.outliner, "selected_object_index", rows=4)
            if scene.outliner.selected_object_index <= len(scene.objects) -1:
                box = layout.box()
                obj = scene.objects[scene.outliner.selected_object_index]
                box.label("Object Properties: " + obj.name)
                box.prop(obj,'name')

    def draw_groups(self,layout,context):
        scene = context.scene
        layout.operator('group.make_group_from_selection',icon='ZOOMIN')
        row = layout.row()
        row.scale_y = 1.3        
        row.operator("library.add_group_from_library",text="Group Library",icon='EXTERNAL_DATA')
        if len(bpy.data.groups) > 0:
            layout.template_list("FD_UL_groups", "", bpy.data, "groups", scene.outliner, "selected_group_index", rows=4)   
            if scene.outliner.selected_group_index <= len(bpy.data.groups) -1:
                box = layout.box()
                group = bpy.data.groups[scene.outliner.selected_group_index]
                
                box.label("Group Properties: " + group.name)
                box.prop(group,'name')
                box.template_list("FD_UL_objects", "", group, "objects", scene.outliner, "selected_group_object_index", rows=4)  

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop_enum(scene.outliner, "outliner_tabs", 'SCENES', icon='SCENE_DATA', text="Scenes") 
        row.prop_enum(scene.outliner, "outliner_tabs", 'WORLDS', icon='WORLD_DATA', text="Worlds") 
        row.prop_enum(scene.outliner, "outliner_tabs", 'MATERIALS', icon='MATERIAL', text="Materials") 
        row = col.row(align=True)
        row.prop_enum(scene.outliner, "outliner_tabs", 'OBJECTS', icon='OBJECT_DATA', text="Objects") 
        row.prop_enum(scene.outliner, "outliner_tabs", 'GROUPS', icon='OUTLINER_OB_GROUP_INSTANCE', text="Groups") 
        row.prop_enum(scene.outliner, "outliner_tabs", 'LAYERS', icon='RENDERLAYERS', text="Layers") 

        if scene.outliner.outliner_tabs == 'SCENES':
            self.draw_scenes(box, context)
                
        if scene.outliner.outliner_tabs == 'WORLDS':
            self.draw_worlds(box, context)

        if scene.outliner.outliner_tabs == 'MATERIALS':
            self.draw_materials(box, context)

        if scene.outliner.outliner_tabs == 'OBJECTS':
            self.draw_objects(box, context)

        if scene.outliner.outliner_tabs == 'GROUPS':
            self.draw_groups(box, context)

        if scene.outliner.outliner_tabs == 'LAYERS':
            self.draw_layers_interface(box, context)

class FD_UL_objects(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.type == 'MESH':
            layout.label(item.name,icon='OUTLINER_OB_MESH')
        if item.type == 'EMPTY':
            layout.label(item.name,icon='OUTLINER_OB_EMPTY')
        if item.type == 'CAMERA':
            layout.label(item.name,icon='OUTLINER_OB_CAMERA')
        if item.type == 'LAMP':
            layout.label(item.name,icon='OUTLINER_OB_LAMP')          
        if item.type == 'FONT':
            layout.label(item.name,icon='OUTLINER_OB_FONT')    
        if item.type == 'CURVE':
            layout.label(item.name,icon='OUTLINER_OB_CURVE')                          
        if context.scene.objects.active:
            if context.scene.objects.active.name == item.name:
                layout.label('',icon='FILE_TICK')
        layout.prop(item,'hide',emboss=False,icon_only=True)
        layout.prop(item,'hide_select',emboss=False,icon_only=True)
        layout.prop(item,'hide_render',emboss=False,icon_only=True)

class FD_UL_worlds(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name,icon='WORLD_DATA')
        if item.name == context.scene.world.name:
            layout.label('',icon='FILE_TICK')

class FD_UL_materials(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name,icon='MATERIAL')

class FD_UL_scenes(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name,icon='SCENE_DATA')

class FD_UL_groups(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name,icon='GROUP')

# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = (
        SCENE_PT_outliner,
        )

def update_panel(self, context):
    message = "Layer Management: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)
                
        for panel in panels:
            panel.bl_category = context.user_preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass

def register():
    bpy.utils.register_class(NamedLayer)
    bpy.utils.register_class(NamedLayers)
    bpy.utils.register_class(Outliner)
    
    bpy.utils.register_class(SCENE_OT_create_new_scene)
    bpy.utils.register_class(SCENE_OT_namedlayer_toggle_visibility)
    bpy.utils.register_class(SCENE_OT_namedlayer_move_to_layer)
    bpy.utils.register_class(SCENE_OT_namedlayer_toggle_wire)
    bpy.utils.register_class(SCENE_OT_namedlayer_lock_all)
    bpy.utils.register_class(SCENE_OT_namedlayer_select_objects_by_layer)
    bpy.utils.register_class(SCENE_OT_namedlayer_show_all)
    bpy.utils.register_class(GROUP_OT_make_group_from_selection)
    bpy.utils.register_class(WORLD_OT_create_world_from_hdr)
    bpy.utils.register_class(SCENE_OT_set_background_image_scale)
    bpy.utils.register_class(SCENE_PT_outliner)
    bpy.utils.register_class(FD_UL_objects)
    bpy.utils.register_class(FD_UL_worlds)
    bpy.utils.register_class(FD_UL_materials)
    bpy.utils.register_class(FD_UL_scenes)
    bpy.utils.register_class(FD_UL_groups)

    bpy.types.Scene.namedlayers = PointerProperty(type=NamedLayers)
    bpy.types.Scene.outliner = PointerProperty(type=Outliner)
    bpy.app.handlers.scene_update_post.append(check_init_data)


def unregister():
    bpy.utils.unregister_class(NamedLayer)
    bpy.utils.unregister_class(NamedLayers)
    bpy.utils.unregister_class(Outliner)
    bpy.utils.unregister_class(SCENE_OT_namedlayer_toggle_visibility)
    bpy.utils.unregister_class(SCENE_OT_namedlayer_move_to_layer)
    bpy.utils.unregister_class(SCENE_OT_namedlayer_toggle_wire)
    bpy.utils.unregister_class(SCENE_OT_namedlayer_lock_all)
    bpy.utils.unregister_class(SCENE_OT_namedlayer_select_objects_by_layer)
    bpy.utils.unregister_class(SCENE_OT_namedlayer_show_all)
    bpy.utils.unregister_class(GROUP_OT_make_group_from_selection)
    bpy.utils.unregister_class(SCENE_PT_outliner)
    bpy.utils.unregister_class(FD_UL_objects)
    bpy.utils.unregister_class(FD_UL_worlds)
    bpy.utils.unregister_class(FD_UL_materials)
    bpy.utils.unregister_class(FD_UL_scenes)
    bpy.utils.unregister_class(FD_UL_groups)
    
    bpy.app.handlers.scene_update_post.remove(check_init_data)
    del bpy.types.Scene.layergroups
    del bpy.types.Scene.layergroups_index
    del bpy.types.Scene.namedlayers
    del bpy.types.Scene.outliner

if __name__ == "__main__":
    register()
