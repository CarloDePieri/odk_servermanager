from os.path import join, isfile

from odk_servermanager.instance import ServerInstance
from odk_servermanager.modfix import ModFix
from odk_servermanager.utils import copy


class ModFixCBA(ModFix):
    """ModFix for the mod 'CBA: Community Based Addons for Arma 3'."""

    name: str = "CBA_A3"

    def hook_init_link_post(self, server_instance: ServerInstance) -> None:
        """Copy the cba_settings.sqf file in the right dir."""
        self._copy_cba(server_instance)

    def hook_update_link_post(self, server_instance: ServerInstance) -> None:
        """Make sure a cba_settings is copied over even on update, if its not already there."""
        self._copy_cba(server_instance)

    @staticmethod
    def _copy_cba(server_instance: ServerInstance) -> None:
        """Actually copy the cba_settings.sqf specified in the cba_settings field to the right folder."""
        cba_settings_target = join(server_instance.get_server_instance_path(), "userconfig", "cba_settings.sqf")
        if not isfile(cba_settings_target):
            custom_cba_settings_path = server_instance.S.fix_settings.mod_fix_settings["cba_settings"]
            copy(custom_cba_settings_path, cba_settings_target)


to_be_registered = ModFixCBA()
