from functools import reduce
from typing import Dict

import pkg_resources
import reusables
import json
from box import ConfigBox


class ConfigIni:
    """Class responsible to deal with config.ini files."""

    content: str = ""

    def create_file(self, file_path: str,
                    data: Dict = {}, add_comments: bool = True, add_no_value_entry: bool = True) -> None:
        """Create a config.ini file. Can fill it with data from a dict. Add comments and no value entry by default, but
        can omit them for a cleaner config file."""
        config_structure = self._get_config_structure()
        first_line = True
        if add_comments:
            self._add_line(config_structure["header"])
            first_line = False
        for section in config_structure["sections"]:
            if first_line:
                first_line = False
            else:
                self._add_empty_line()
            self._add_line("[{}]".format(section["title"]))
            if add_comments:
                for description_line in section["description"]:
                    self._add_line(";;; {}".format(description_line))
            for entry in section["entries"]:
                if add_comments:
                    self._add_line(";; {}".format(entry["description"]))
                self._set_entry_value(data, section["title"], entry, add_no_value_entry)
        with open(file_path, "w+") as f:
            f.write(self.content)

    def _set_entry_value(self, data: Dict, section_title: str, entry: Dict, add_no_value_entry: bool) -> None:
        """Add to the file content the value, trying to get it from the provided data if possible."""
        # try to get the actual entry
        actual_entry = data.get(section_title, {}).get(entry["name"])
        if actual_entry is None:
            if add_no_value_entry:
                # no custom entry was provided, fallback to commented entry
                default_value = entry.get("default_value", "")
                self._add_line(";{} = {}".format(entry["name"], default_value))
        else:
            if isinstance(actual_entry, list):
                if len(actual_entry) > 0:
                    # The entry is a list, fix it
                    actual_entry = reduce(lambda x, y: "{}, {}".format(x, y), actual_entry)
                else:
                    actual_entry = ""
            self._add_line("{} = {}".format(entry["name"], actual_entry))

    def _add_line(self, line: str) -> None:
        """Add a line of text to the file content."""
        self.content += "{}\n".format(line)

    def _add_empty_line(self) -> None:
        """Add an empty line to the file content."""
        self.content += "\n"

    @staticmethod
    def _get_config_structure() -> Dict:
        """Return the config.ini structure as a dictionary, parsed from the json file in the templates folder."""
        config_structure_json = pkg_resources.resource_string('odk_servermanager',
                                                              "templates/config_ini.json").decode("UTF-8")
        return json.loads(config_structure_json)

    @staticmethod
    def read_file(file_path: str, bootstrap: bool = False) -> Dict:
        """Read the given file and parse and return raw settings from it."""
        config = {"mod_fix_settings": {}}
        settings = ConfigBox(reusables.config_dict(file_path))
        # extract bat settings
        config["bat"] = settings.bat.to_dict()
        # extract arma config settings
        config["config"] = settings.config.to_dict()
        # fix list element in odksm settings
        for el in ["user_mods_list", "mods_to_be_copied", "server_mods_list", "skip_keys"]:
            if el in settings.ODKSM:
                el_list = settings.ODKSM.list(el)
                settings.ODKSM[el] = list(filter(lambda x: x != "", el_list))
        # now save the odksm section
        config["ODKSM"] = settings.ODKSM.to_dict()
        # check for mod fixes
        config["mod_fix_settings"] = settings.mod_fix_settings.to_dict()
        if "enabled_fixes" in settings.mod_fix_settings:
            config["mod_fix_settings"]["enabled_fixes"] = settings.mod_fix_settings.list("enabled_fixes")
        if bootstrap:
            config["bootstrap"] = settings.bootstrap.to_dict()
        return config
