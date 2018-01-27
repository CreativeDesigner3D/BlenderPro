from . import info_ops
from . import info_ui

def register():
    info_ops.register()
    info_ui.register()