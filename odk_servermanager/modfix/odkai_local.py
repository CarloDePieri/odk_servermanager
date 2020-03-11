from os import unlink
from os.path import join, abspath, islink

from odk_servermanager.instance import ServerInstance
from odk_servermanager.modfix import ModFix
from odk_servermanager.utils import symlink


class ModFixODKAILocal(ModFix):
    """ModFix for the mod 'ODKAI'. It allows us to use a local copy of the mod while we develop it."""

    name: str = "ODKAI"

    def hook_init_link_replace(self, server_instance: ServerInstance) -> None:
        """Used to symlink a local version of ODKAI in the instance.

        This hook will look for following fields in mod_fix_settings:
        :odkai_local_path: the full path of the folder containing the mod
        """
        self._link_local_copy(server_instance)

    def hook_update_link_replace(self, server_instance: ServerInstance) -> None:
        """Make sure the local copy is symlinked."""
        mod_folder = join(server_instance.get_server_instance_path(), server_instance.S.linked_mod_folder_name,
                          "@" + self.name)
        if islink(mod_folder):
            unlink(mod_folder)
        self._link_local_copy(server_instance)

    def _link_local_copy(self, server_instance: ServerInstance) -> None:
        """Actually link the local copy."""
        mod_folder = join(server_instance.get_server_instance_path(), server_instance.S.linked_mod_folder_name,
                          "@" + self.name)
        mod_fix_settings = server_instance.S.fix_settings.mod_fix_settings
        local_folder = abspath(mod_fix_settings["odkai_local_path"])
        symlink(local_folder, mod_folder)


to_be_registered = ModFixODKAILocal()
