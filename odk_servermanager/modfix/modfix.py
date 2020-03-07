import os
from importlib import import_module
from typing import Callable, Union, List
from odk_servermanager.instance import ServerInstance


class ModFix:
    """Generic class used to apply specific operations before, in place of or after copying a certain mod
    into its server instance folder.
    All hooks are functions that take as its only argument the ServerInstance object.

    :name: The mod DisplayName
    :hook_pre: This hook gets called before the mod copy begin.
    :hook_replace: This hook gets called instead of the usual mod copy.
    :hook_post: This hook gets called after the mod copy end.
    :hook_update_pre: This hook gets called before the mod update begin.
    :hook_update_replace: This hook gets called instead of the usual mod update.
    :hook_update_post: This hook gets called after the mod update end.
    """
    name: str = ""
    hook_pre: Union[Callable[[ServerInstance], None], None] = None
    hook_replace: Union[Callable[[ServerInstance], None], None] = None
    hook_post: Union[Callable[[ServerInstance], None], None] = None
    hook_update_pre: Union[Callable[[ServerInstance], None], None] = None
    hook_update_replace: Union[Callable[[ServerInstance], None], None] = None
    hook_update_post: Union[Callable[[ServerInstance], None], None] = None


def register_fixes() -> List[ModFix]:
    """Return a list of ModFix objects dynamically recovered from all modules in the modfix package folder."""
    registered_fix = []
    to_skip = ["__init__.py", "modfix.py"]
    for module_file in os.listdir(os.path.dirname(__file__)):
        if module_file not in to_skip and module_file[-3:] == '.py':
            module = import_module("odk_servermanager.modfix.{}".format(module_file[:-3]))
            mod_fix = module.to_be_registered
            registered_fix.append(mod_fix)
    return registered_fix
