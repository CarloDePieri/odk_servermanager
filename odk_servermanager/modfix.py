import shutil
from os import mkdir, listdir
from os.path import join
from typing import Callable, List, Union
from odk_servermanager.instance import ServerInstance
from odk_servermanager.utils import symlink


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


class ModFixCBA(ModFix):
    """ModFix for the mod 'CBA: Community Based Addons for Arma 3'."""

    name: str = "CBA_A3"

    def hook_replace(self, server_instance: ServerInstance) -> None:
        """Used to symlink all mod files and folders but the userconfig one, where a custom cba settings file can be placed.

        This hook will look for following fields in mod_fix_settings:
        :cba_settings: the full path of the custom cba settings. If not found, will default to the empty default one.
        """
        # Create the folder
        arma_mod_folder = join(server_instance.S.arma_folder, "!Workshop", "@" + self.name)
        mod_folder = join(server_instance.get_server_instance_path(), server_instance.S.copied_mod_folder_name,
                          "@" + self.name)
        mkdir(mod_folder)
        # Symlink everything but the userconfig folder
        to_be_symlinked = list(filter(lambda x: x != "userconfig", listdir(arma_mod_folder)))
        for el in to_be_symlinked:
            src = join(arma_mod_folder, el)
            dest = join(mod_folder, el)
            symlink(src, dest)
        # Create the userconfig folder
        mkdir(join(mod_folder, "userconfig"))
        # Recover the custom cba settings if present else copy the original one
        mod_fix_settings = server_instance.S.mod_fix_settings
        if mod_fix_settings is not None and mod_fix_settings.get("cba_settings", None) is not None:
            src = mod_fix_settings["cba_settings"]
            dest = join(mod_folder, "userconfig", "cba_settings.sqf")
            shutil.copy2(src, dest)
        else:
            src = join(arma_mod_folder, "userconfig", "cba_settings.sqf")
            dest = join(mod_folder, "userconfig", "cba_settings.sqf")
            shutil.copy2(src, dest)

    def hook_update_replace(self, server_instance: ServerInstance) -> None:
        """This empty hook will prevent the update of an already there cba instance.
        This is because the hook_replace already take care of mod updating via symlinking and we don't want to lose
        eventual customization to the cba_settings."""
        pass


# This module variable will store all registered ModFix and then will be used by ServerInstance to know which fix to
# apply.
registered_fix: List[ModFix] = [
    ModFixCBA()
]
