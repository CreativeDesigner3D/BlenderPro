from . import ui_layer_manager
from . import space_view3d
from . import space_info
from . import object_properties_panel
# from . import object_library
from . import library

def register():
    ui_layer_manager.register()
    space_view3d.register()
    space_info.register()
    object_properties_panel.register()
    library.register()
#     object_library.register()