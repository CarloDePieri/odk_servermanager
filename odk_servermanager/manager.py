from typing import List

import reusables
from box import ConfigBox
from bs4 import BeautifulSoup

from odk_servermanager.instance import ServerInstance
from odk_servermanager.settings import ServerBatSettings, ServerConfigSettings, ServerInstanceSettings


class ServerManager:

    settings: ServerInstanceSettings
    instance: ServerInstance

    def __init__(self, config_file: str):
        self.config_file = config_file

    def manage_instance(self):
        """Offer a basic gui so that the user can distinguish between instance's init and update."""
        self._recover_settings()
        self.instance = ServerInstance(self.settings)
        name = self.instance.S.server_instance_name
        if not self.instance.is_folder_instance_already_there():
            print("Starting server instance INIT for {}!".format(name))
            self.instance.init()
        else:
            question = "WARNING! A server instance called {} seems already present.\nContinuing will mean UPDATING " \
                       "the existing server instance. Be sure to understand everything this entails. " \
                       "Do you want to continue? (y/n) ".format(name)
            answer = input(question)
            if answer.lower() == "y" or answer.lower() == "yes":
                print("Alright! Starting server instance UPDATE for {}!".format(name))
                self.instance.update()
            else:
                print("Ok! BYE!")
                return

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
                settings.ODKSM[el] = settings.ODKSM.list(el)
        # check for mod_fix
        if "mod_fix_settings" in settings:
            settings.ODKSM.mod_fix_settings = settings.mod_fix_settings.to_dict()
        # create the settings container
        self.settings = ServerInstanceSettings(**settings.ODKSM.to_dict(),
                                               bat_settings=bat_settings, config_settings=config_settings)

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
