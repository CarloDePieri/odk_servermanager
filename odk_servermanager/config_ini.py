from typing import Dict

import reusables
from box import ConfigBox


class ConfigIni:
    """Class responsible to deal with config.ini files."""

    @staticmethod
    def read_file(file_path: str) -> Dict:
        """Read the given file and parse and return raw settings from it."""
        config = {"mod_fix_settings": {}}
        settings = ConfigBox(reusables.config_dict(file_path))
        # extract bat settings
        config["bat_settings"] = settings.bat.to_dict()
        # extract arma config settings
        config["config_settings"] = settings.config.to_dict()
        # fix list element in odksm settings
        for el in ["user_mods_list", "mods_to_be_copied", "server_mods_list", "skip_keys"]:
            if el in settings.ODKSM:
                el_list = settings.ODKSM.list(el)
                settings.ODKSM[el] = list(filter(lambda x: x != "", el_list))
        # now save the odksm section
        config["odksm"] = settings.ODKSM.to_dict()
        # check for mod fixes
        enabled_fixes = []
        if "enabled_fixes" in settings.mod_fix_settings:
            enabled_fixes = settings.mod_fix_settings.list("enabled_fixes")
            settings.mod_fix_settings.pop("enabled_fixes")  # delete the enabled_fixes from there
        config["mod_fix_settings"]["settings"] = settings.mod_fix_settings.to_dict()
        config["mod_fix_settings"]["enabled_fixes"] = enabled_fixes
        return config
