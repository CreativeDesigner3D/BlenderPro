from . import ui_layer_manager
from . import archipack
from . import space_view3d
from . import space_info
from . import object_properties_panel

def register():
    ui_layer_manager.register()
    archipack.register()
    space_view3d.register()
    space_info.register()
    object_properties_panel.register()