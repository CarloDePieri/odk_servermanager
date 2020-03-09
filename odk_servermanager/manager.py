from typing import List

import reusables
from box import ConfigBox
from bs4 import BeautifulSoup

from odk_servermanager.instance import ServerInstance, ModNotFound
from odk_servermanager.settings import ServerBatSettings, ServerConfigSettings, ServerInstanceSettings, ModFixSettings


class ServerManager:

    settings: ServerInstanceSettings
    instance: ServerInstance

    def __init__(self, config_file: str):
        self.config_file = config_file

    def manage_instance(self):
        """Offer a basic ui so that the user can distinguish between instance's init and update."""
        print("\n ======[ WELCOME TO ODKSM! ]======\n")
        try:
            self._recover_settings()
            self.instance = ServerInstance(self.settings)
        except Exception as err:
            self._ui_abort("\n [ERR] Error while loading the configuration file.\n Something was wrong in the odksm "
                           "config file or in the Arma 3 mod preset.\n\n {}\n\n "
                           "Check the documentation in the wiki, in the README.md or in the "
                           "odksm_servermanager/settings.py.\n Bye!\n".format(err))
        try:
            print("\n Loaded config file: {}\n Instance name: {}"
                  "\n Server title: {}\n".format(self.config_file, self.instance.S.server_instance_name,
                                                 self.instance.S.config_settings.hostname))
            if not self.instance.is_folder_instance_already_there():
                self._ui_init()
            else:
                self._ui_update()
        except ModNotFound as err:
            self._ui_abort("\n [ERR] Error while loading mods: {}\n".format(err.args[0]))
        except Exception as err:
            self._ui_abort("\n [ERR] Generic error.\n\n {}\n\n Please take notes on what you were doing and contact "
                           "odksm team on github!\nYOUR SERVER INSTANCE MAY BE CORRUPTED! You should delete it and "
                           "generate it again.\n Bye!\n".format(err))

    def _ui_init(self):
        """UI to init an instance."""
        user_answer = input(" Do you want to continue? (y/n) ")
        if self._is_positive_answer(user_answer):
            print("\n > Starting server instance INIT for {}!".format(self.instance.S.server_instance_name))
            self.instance.init()
            self._ui_print_warnings()
            print("\n [OK] Init done! Bye!\n")
        else:
            self._ui_abort()

    def _ui_update(self):
        """UI to update an instance."""
        name = self.instance.S.server_instance_name
        answer = input(" [WARNING] A server instance called {} seems already present.\n Continuing will "
                       "UPDATE the existing server instance. Be sure to understand everything this entails.\n\n"
                       " Do you want to continue? (y/n) ".format(name))
        if self._is_positive_answer(answer):
            print("\n > Starting server instance UPDATE for {}!".format(name))
            self.instance.update()
            self._ui_print_warnings()
            print("\n [OK] Update done! Bye!\n\n")
        else:
            self._ui_abort()

    def _ui_print_warnings(self):
        """Print warnings if needed."""
        if len(self.instance.warnings) > 0:
            print("\n We got some warnings:")
            for warn in self.instance.warnings:
                print(" [WARN] {}".format(warn))

    @staticmethod
    def _ui_abort(message: str = "\n [ABORTED] Bye!\n") -> None:
        """Print the given message and quit the program."""
        print(message)
        exit(1)

    @staticmethod
    def _is_positive_answer(answer: str) -> bool:
        """Parse the answer and return True if positive."""
        return answer.lower() == "y" or answer.lower() == "yes"

    def _recover_settings(self):
        """Recover all needed settings, including mods presets."""
        self._parse_config()
        if "user_mods_preset" in self.settings:
            mods = self._parse_mods_preset(self.settings.user_mods_preset)
            # do not use shorthand += here: there's a bug in Box that will break things
            self.settings.user_mods_list = self.settings.user_mods_list + mods

    def _parse_config(self) -> None:
        """Parse the config file and create all settings container object."""
        settings = ConfigBox(reusables.config_dict(self.config_file))
        # compose the bat settings container
        bat_settings = ServerBatSettings(**settings.bat.to_dict())
        # compose the config settings container
        config_settings = ServerConfigSettings(**settings.config.to_dict())
        # fix list element in odksm settings
        for el in ["user_mods_list", "mods_to_be_copied", "server_mods_list", "skip_keys"]:
            if el in settings.ODKSM:
                el_list = settings.ODKSM.list(el)
                settings.ODKSM[el] = list(filter(lambda x: x != "", el_list))
        # check for mod_fix
        if "mod_fix_settings" in settings:
            enabled_fixes = []
            if "enabled_fixes" in settings.mod_fix_settings:
                enabled_fixes = settings.mod_fix_settings.list("enabled_fixes")
                settings.mod_fix_settings.pop("enabled_fixes")  # delete the enabled_fixes from there
            mod_fix_settings = settings.mod_fix_settings.to_dict()
            fix_settings = ModFixSettings(enabled_fixes=enabled_fixes, mod_fix_settings=mod_fix_settings)
        else:
            fix_settings = ModFixSettings()
        # create the settings container
        self.settings = ServerInstanceSettings(**settings.ODKSM.to_dict(),
                                               bat_settings=bat_settings, config_settings=config_settings,
                                               fix_settings=fix_settings)
        # add missing mod_fix mods to mods_to_be_copied
        from odk_servermanager.modfix import register_fixes
        mod_fixes = register_fixes(fix_settings.enabled_fixes)
        for fix in mod_fixes:
            if fix.name not in self.settings.mods_to_be_copied:
                self.settings.mods_to_be_copied.append(fix.name)

    def _parse_mods_preset(self, filename: str) -> List[str]:
        """Parse an Arma 3 preset and return the List of all selected mods names."""
        # Open the preset file and read its content
        with open(filename, "r") as f:
            xml = f.read()
        # Parse the file and extract all mods names
        parsed_xml = BeautifulSoup(xml, 'html.parser')
        mods_data = parsed_xml.select("tr[data-type=\"ModContainer\"]")
        mods_name = list(map(
            lambda x: self._display_name_filter(x.select_one("td[data-type=\"DisplayName\"]").text),
            mods_data))
        return mods_name

    @staticmethod
    def _display_name_filter(name: str) -> str:
        """Fix some display names peculiarities."""
        return name.replace(":", "-")
