def classFactory(iface):
    from .swmmtools import SWMMTools
    return SWMMTools(iface)
