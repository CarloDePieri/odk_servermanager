import sys
import time
import traceback
from os import mkdir
from os.path import join, abspath, isdir
from typing import List, Union

import pkg_resources
from bs4 import BeautifulSoup

from odk_servermanager.config_ini import ConfigIni
from odk_servermanager.instance import ServerInstance, ModNotFound
from odk_servermanager.modfix import MisconfiguredModFix, NonExistingFixFile, ErrorInModFix
from odk_servermanager.settings import ServerBatSettings, ServerConfigSettings, ServerInstanceSettings, ModFixSettings
from odk_servermanager.utils import compile_from_template, copy


class ServerManager:

    settings: ServerInstanceSettings
    instance: ServerInstance
    config_file: str

    def __init__(self, debug_logs_path: Union[str, None] = None):
        self.debug_logs_path = debug_logs_path

    def bootstrap(self, default_config_file: str = None) -> None:
        """Interactive UI to start building a new server instance."""
        print("\n ======[ WELCOME TO ODKSM! ]======\n")
        try:
            # try and read the config
            data = ConfigIni.read_file(default_config_file, bootstrap=True)
            # check for needed fields
            if data["bootstrap"].get("instances_root", "") == "":
                raise ValueError("'instances_root' field can't be empty in the [bootstrap] section!")
            if data["bootstrap"].get("odksm_folder_path", "") == "":
                raise ValueError("'odksm_folder_path' field can't be empty in the [bootstrap] section!")
        except Exception as err:
            self._ui_abort("\n [ERR] Error while reading the default config file!\n\n {}\n\n "
                           "Check the documentation in the wiki, in the bootstrap.ini example file, in the README.md or"
                           " in the odksm_servermanager/settings.py.\n Bye!\n".format(err))
        try:
            # Check the instances_root exists
            instances_root = data["bootstrap"]["instances_root"]
            if not isdir(instances_root):
                raise Exception("Could not find the instances_folder '{}'".format(instances_root))
            print("\n This utility will help you start creating your server instance.\n")
            instance_name = input(" Choose a unique name for the instance: ")
            # check if custom templates are needed
            custom_bat_template_needed = False
            custom_config_template_needed = False
            custom_templates_needed_string = input(" Will you need custom templates? (y/n) ")
            if custom_templates_needed_string == "y":
                print("\n OK! Now.. \n")
                custom_bat_template_needed_string = input(" ... will you need a custom BAT template? (y/n) ")
                if custom_bat_template_needed_string == "y":
                    custom_bat_template_needed = True
                custom_config_template_needed_string = input(" ... will you need a custom CONFIG template? (y/n) ")
                if custom_config_template_needed_string == "y":
                    custom_config_template_needed = True
            # create the folder
            instance_dir = join(instances_root, instance_name)
            mkdir(instance_dir)
            # copy templates if needed
            if custom_bat_template_needed:
                bat_template_file_name = "run_server_template.txt"
                bat_template_file = join(instance_dir, bat_template_file_name)
                template_file = self._get_resource_file("templates/{}".format(bat_template_file_name))
                copy(template_file, bat_template_file)
                data["bat"]["bat_template"] = abspath(bat_template_file)
            if custom_config_template_needed:
                config_template_file_name = "server_cfg_template.txt"
                config_template_file = join(instance_dir, config_template_file_name)
                template_file = self._get_resource_file("templates/{}".format(config_template_file_name))
                copy(template_file, config_template_file)
                data["config"]["config_template"] = abspath(config_template_file)
            # prepare some fields for the config file
            data["ODKSM"]["server_instance_name"] = instance_name
            data["ODKSM"]["server_instance_root"] = abspath(instance_dir)
            # generate the config.ini file
            ConfigIni().create_file(join(instance_dir, "config.ini"), data)
            # compile the ODKSM.bat file
            bat_template = pkg_resources.resource_string("odk_servermanager",
                                                         "templates/ODKSM_bat_template.txt").decode("UTF-8")
            bat_file = join(instance_dir, "ODKSM.bat")
            compile_from_template(bat_template, bat_file, {"odksm_folder_path": data["bootstrap"]["odksm_folder_path"]})
            print("\n Instance folder created!\n\n [WARNING] IMPORTANT! YOU ARE NOT DONE! You still need to edit the\n"
                  " config.ini file in the folder and to run the actual ODKSM.bat tool.\n Bye!\n")
        except Exception as err:
            self._ui_abort("\n [ERR] Error while bootstrapping the instance!\n\n {}\n\n "
                           "Check the documentation in the wiki, in the bootstrap.ini example file, in the README.md or"
                           " in the odksm_servermanager/settings.py.\n Bye!\n".format(err))

    @staticmethod
    def _get_resource_file(file: str) -> str:
        """Return the actual file path of a resource file."""
        return pkg_resources.resource_filename('odk_servermanager', file)

    def manage_instance(self, config_file: str) -> None:
        """Offer a basic ui so that the user can distinguish between instance's init and update."""
        self.config_file = config_file
        print("\n ======[ WELCOME TO ODKSM! ]======\n")
        try:
            self._recover_settings()
            self.instance = ServerInstance(self.settings)
        except (NonExistingFixFile, MisconfiguredModFix) as err:
            self._ui_abort("\n [ERR] Error while loading mod fix: {}\n Bye!\n".format(err.args[0]))
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
            self._ui_abort("\n [ERR] Error while loading mods: {}\n Bye!\n".format(err.args[0]))
        except ErrorInModFix as err:
            self._ui_abort("\n [ERR] Error while executing mod fix: {}\nYOUR SERVER INSTANCE MAY BE CORRUPTED! You "
                           "should delete it and generate it again.\n Bye!\n".format(err.args[0]))
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

    def _ui_abort(self, message: str = "\n [ABORTED] Bye!\n") -> None:
        """Print the given message and quit the program."""
        if self.debug_logs_path is not None:
            self._print_debug_log()
        print(message)
        exit(1)

    @staticmethod
    def _is_positive_answer(answer: str) -> bool:
        """Parse the answer and return True if positive."""
        return answer.lower() == "y" or answer.lower() == "yes"

    def _recover_settings(self):
        """Recover all needed settings, including mods presets."""
        self._parse_config()
        if self.settings.user_mods_preset != "":
            mods = self._parse_mods_preset(self.settings.user_mods_preset)
            # do not use shorthand += here: there's a bug in Box that will break things
            self.settings.user_mods_list = self.settings.user_mods_list + mods

    def _parse_config(self) -> None:
        """Parse the config file and create all settings container object."""
        # Recover data in the file
        data = ConfigIni.read_file(self.config_file)
        # Create settings containers
        config_settings = ServerConfigSettings(**data["config"])
        bat_settings = ServerBatSettings(**data["bat"])
        enabled_fixes = []
        if "enabled_fixes" in data["mod_fix_settings"]:
            enabled_fixes = data["mod_fix_settings"].pop("enabled_fixes")
        fix_settings = ModFixSettings(enabled_fixes=enabled_fixes,
                                      mod_fix_settings=data["mod_fix_settings"])
        # create the global settings container
        self.settings = ServerInstanceSettings(**data["ODKSM"],
                                               bat_settings=bat_settings, config_settings=config_settings,
                                               fix_settings=fix_settings)
        # add missing mod_fix mods to mods_to_be_copied
        from odk_servermanager.modfix import register_fixes
        mod_fixes = register_fixes(fix_settings.enabled_fixes)
        for fix in mod_fixes:
            # Check that it's a required mod:
            if fix.name in self.settings.user_mods_list + self.settings.server_mods_list:
                copy_hooks = ["hook_init_copy_pre", "hook_init_copy_replace", "hook_init_copy_post",
                              "hook_update_copy_pre", "hook_update_copy_replace", "hook_update_copy_post"]
                for copy_hook in copy_hooks:
                    # Check if there's a copy hook enabled...
                    if getattr(fix, copy_hook) is not None and fix.name not in self.settings.mods_to_be_copied:
                        # ... if so, add the mod to mods_to_be_copied
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

    def _print_debug_log(self):
        """Print in a log file the stacktrace."""
        if self.debug_logs_path is not None and self._are_in_exception():
            # Recover the traceback
            tb = traceback.format_exc()
            log_name = "odksm_{}.log".format(time.strftime("%Y%m%d_%H%M%S", time.gmtime()))
            log_file = join(self.debug_logs_path, log_name)
            with open(log_file, "w+") as log:
                log.write(tb)

    @staticmethod
    def _are_in_exception():
        """Return true if we are currently handling an exception"""
        return sys.exc_info() != (None, None, None)
