from . import ui_layer_manager
from . import archipack
from . import space_view3d
from . import space_info

def register():
    ui_layer_manager.register()
    archipack.register()
    space_view3d.register()
    space_info.register()