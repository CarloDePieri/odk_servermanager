import os
from importlib import import_module
from os.path import isfile, join
from typing import Callable, Union, List
from odk_servermanager.instance import ServerInstance

HOOK_TYPE = Union[Callable[[ServerInstance], None], None]


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

    TAKE NOTICE: DO NOT OVERWRITE hook_caller. It's the wrapper used to to call hooks and manage errors.
    """
    name: str = ""
    hook_pre: HOOK_TYPE = None
    hook_replace: HOOK_TYPE = None
    hook_post: HOOK_TYPE = None
    hook_update_pre: HOOK_TYPE = None
    hook_update_replace: HOOK_TYPE = None
    hook_update_post: HOOK_TYPE = None

    def hook_caller(self, hook_name: str, server_instance: ServerInstance) -> None:
        """DO NOT OVERWRITE THIS METHOD. Wrapper to manage errors in hook execution."""
        try:
            getattr(self, "hook_{}".format(hook_name))(server_instance)
        except Exception:
            # This is intentionally broad to defend against all kind of errors inside user mod fix
            raise ErrorInModFix("Error when executing the '{}' mod fix.".format(self.name))


def register_fixes(enabled_fixes: List[str]) -> List[ModFix]:
    """Return a list of ModFix objects dynamically recovered from the list passed as argument."""
    registered_fix = []
    to_skip = ["__init__", "modfix"]
    for fix_name in enabled_fixes:
        try:
            if not isfile(join(os.path.dirname(__file__), "{}.py".format(fix_name))):
                raise NonExistingFixFile("Could not find the file {}.py in the modfix folder.".format(fix_name))
            if fix_name not in to_skip:
                module = import_module("odk_servermanager.modfix.{}".format(fix_name))
                mod_fix = module.to_be_registered
                registered_fix.append(mod_fix)
        except NonExistingFixFile:
            raise
        except Exception:
            # This is intentionally broad to defend against all kind of errors inside user mod fix
            raise MisconfiguredModFix("General error when importing {} mod fix.".format(fix_name))
    return registered_fix


class NonExistingFixFile(Exception):
    """"""


class MisconfiguredModFix(Exception):
    """"""


class ErrorInModFix(Exception):
    """"""
