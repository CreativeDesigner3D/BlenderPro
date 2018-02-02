from . import props_library
from . import ops_library
from . import object_library
from . import group_library
from . import material_library

def register():
    props_library.register()
    ops_library.register()
    object_library.register()
    group_library.register()
    material_library.register()