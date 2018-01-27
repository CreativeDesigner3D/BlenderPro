from . import space_view3d
from . import space_info
from . import library

def register():
    space_view3d.register()
    space_info.register()
    library.register()