from . import object_library
from . import group_library
from . import material_library

def register():
    object_library.register()
    group_library.register()
    material_library.register()