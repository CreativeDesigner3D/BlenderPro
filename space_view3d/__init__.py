from . import view3d_ui
from . import view3d_ops
from . import object_properties_panel
from . import ui_layer_manager

def register():
    view3d_ui.register()
    view3d_ops.register()
    object_properties_panel.register()
    ui_layer_manager.register()