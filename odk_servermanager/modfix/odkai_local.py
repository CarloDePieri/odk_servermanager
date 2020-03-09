from os.path import join, abspath

from odk_servermanager.instance import ServerInstance
from odk_servermanager.modfix import ModFix
from odk_servermanager.utils import symlink


class ModFixODKAILocal(ModFix):
    """ModFix for the mod 'ODKAI'. It allows us to use a local copy of the mod while we develop it."""

    name: str = "ODKAI"

    def hook_replace(self, server_instance: ServerInstance) -> None:
        """Used to symlink a local version of ODKAI in the instance.

        This hook will look for following fields in mod_fix_settings:
        :odkai_local_path: the full path of the folder containing the mod
        """
        mod_folder = join(server_instance.get_server_instance_path(), server_instance.S.copied_mod_folder_name,
                          "@" + self.name)
        mod_fix_settings = server_instance.S.fix_settings.mod_fix_settings
        local_folder = abspath(mod_fix_settings["odkai_local_path"])
        symlink(local_folder, mod_folder)

    def hook_update_replace(self, server_instance: ServerInstance) -> None:
        """This empty hook will prevent the update of an already there ODKAI.
        This is because the mod is actually a symlink and does not need to be updated."""
        pass


to_be_registered = ModFixODKAILocal()
