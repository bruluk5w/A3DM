import importlib
import os
import pkgutil
import sys

DEBUG = False


def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py

    Individual modules can define a __reload_order_index__ property which
    will be used to reload the modules in a specific order. The default is 0.
    """

    def get_submodule_names(path=path[0], root=""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            elif module_name != __file__:
                module_names.append(root + module_name)

        return module_names

    def import_submodules(names):
        modules = []
        for name in names:
            modules.append(importlib.import_module("." + name, package_name))
        return modules

    def reload_modules(modules):
        modules.sort(key=lambda module: getattr(module, "__reload_order_index__", 0))
        for module in modules:
            importlib.reload(module)

    names = get_submodule_names()
    modules = import_submodules(names)
    if reload:
        reload_modules(modules)
    return names


def register():
    if DEBUG:
        DEBUG_EGG = r"C:/Program Files/JetBrains/PyCharm 2020.2.3/debug-eggs/pydevd-pycharm.egg"
        if not DEBUG_EGG in sys.path:
            sys.path.append(DEBUG_EGG)

        import pydevd_pycharm
        importlib.reload(pydevd_pycharm)
        try:
            pydevd_pycharm.settrace('127.0.0.1', port=12346, stdoutToServer=True, stderrToServer=True)
        except ConnectionRefusedError as e:
            print(e)


def unregister():
    pass
