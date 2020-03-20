from os import unlink
from os.path import join, isfile, islink

from odk_servermanager.instance import ServerInstance
from odk_servermanager.modfix import ModFix
from odk_servermanager.utils import copy, symlink


class ModFixCBA(ModFix):
    """ModFix for the mod 'CBA: Community Based Addons for Arma 3'.

    REQUIRED SETTINGS IN [mod_fix_settings] SECTION
    -----------------------------------------------
    :cba_settings: Path of the custom cba_settings.sqf file

    OPTIONAL SETTINGS IN [mod_fix_settings] SECTION
    -----------------------------------------------
    :instance_specific_cba: Defaults on False. If True the cba gets copied instead of symlinked, and won't be changed by
    instance updates.
    """

    name: str = "CBA_A3"

    def hook_init_link_post(self, server_instance: ServerInstance) -> None:
        """Copy the cba_settings.sqf file in the right dir."""
        if self._is_cba_instance_specific(server_instance):
            self._copy_cba(server_instance)
        else:
            self._link_cba(server_instance)

    def hook_update_link_post(self, server_instance: ServerInstance) -> None:
        """Make sure a cba_settings is copied over even on update, if its not already there."""
        cba_settings_target = self._get_cba_path(server_instance)
        if self._is_cba_instance_specific(server_instance):
            if islink(cba_settings_target):
                # the init was not instance specific, so clear the old link
                unlink(cba_settings_target)
            self._copy_cba(server_instance)
        else:
            if isfile(cba_settings_target):
                # the init was instance specific, so clear the old file
                unlink(cba_settings_target)
            self._link_cba(server_instance)

    def _copy_cba(self, server_instance: ServerInstance) -> None:
        """Actually copy the cba_settings.sqf specified in the cba_settings field."""
        cba_settings_target = self._get_cba_path(server_instance)
        if not isfile(cba_settings_target):
            copy(self._get_default_cba_path(server_instance), cba_settings_target)

    def _link_cba(self, server_instance: ServerInstance) -> None:
        """Symlink the cba_settings.sqf specified in the cba_settings field."""
        cba_settings_target = self._get_cba_path(server_instance)
        if not islink(cba_settings_target):
            symlink(self._get_default_cba_path(server_instance), cba_settings_target)

    @staticmethod
    def _get_cba_path(instance: ServerInstance) -> str:
        """Return the path of the instance cba_settings."""
        return join(instance.get_server_instance_path(), "userconfig", "cba_settings.sqf")

    @staticmethod
    def _get_default_cba_path(instance: ServerInstance) -> str:
        """Return the path of the custom cba_settings specified in the config.ini."""
        return instance.S.fix_settings.mod_fix_settings["cba_settings"]

    @staticmethod
    def _is_cba_instance_specific(instance: ServerInstance) -> bool:
        """Whether the cba_settings should be instance specific (and therefore copied, not symlinked)."""
        return instance.S.fix_settings.mod_fix_settings.get("instance_specific_cba", False)


to_be_registered = ModFixCBA()
