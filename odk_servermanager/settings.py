import os
from os.path import splitdrive
from typing import List, Dict

from box import Box


class ServerConfigSettings(Box):
    """Config container for the server.config file.
    Other than the required arguments, any additional named arguments will be saved.

    REQUIRED FIELDS
    ---------------
    :hostname: The server instance name
    :password: The user password for accessing the server
    :password_admin: The password admin uses to manage the server
    :template: Filename of pbo in MPMissions folder"""

    def __init__(self, hostname: str, password: str, password_admin: str, template: str, **kwargs):
        super(Box, self).__init__(hostname=hostname, password=password, password_admin=password_admin,
                                  template=template, **kwargs)


class ServerBatSettings(Box):
    """Config container for the run_server.bat file.
    Other than the required and optional arguments, any additional named arguments will be saved.

    REQUIRED FIELDS
    ---------------
    :server_title: The server instance name that will appear in the monitoring tool
    :server_port: The port the server is running on
    :server_config: The path to the config file
    :server_cfg: The path to the cfg file
    :server_max_mem: The max memory that the server will be able to allocate

    OPTIONAL FIELDS
    ---------------
    :server_flags: Default to empty, any addition flag to be passed to the server
    """

    def __init__(self, server_title: str, server_port: str, server_config: str, server_cfg: str,
                 server_max_mem: str, server_flags: str = "", **kwargs):
        super(Box, self).__init__(server_title=server_title, server_port=server_port,
                                  server_config=server_config, server_cfg=server_cfg, server_max_mem=server_max_mem,
                                  server_flags=server_flags, **kwargs)


class ServerInstanceSettings(Box):
    """Config container for the ODKSM module.

    REQUIRED FIELDS
    ---------------
    :server_instance_name: The name that will appear in the instance folder name
    :bat_settings: The settings needed to generate the bat file
    :config_settings: The settings needed to generate the config file

    OPTIONAL FIELDS
    ---------------
    :arma_folder: The folder that contains the game, default to the steam default folder
    :mods_to_be_copied: mods from this list will be copied, not linked
    :linked_mod_folder_name: the name of the linked mod folder
    :copied_mod_folder_name: the name of the copied mod folder
    :server_instance_prefix: every instance folder name will be prefixed by this
    :server_instance_root: every instance folder will be put in this root folder, default to :arma_folder:
    :user_mods_list: the list of the user mods
    :server_mods_list: the list of the server mods
    :skip_keys: which key will be skipped and not linked to the main Keys folder
    :mod_fix_settings: settings used by the mod fixes
    """

    def __init__(self, server_instance_name: str,
                 bat_settings: ServerBatSettings, config_settings: ServerConfigSettings,
                 arma_folder: str = "", mods_to_be_copied: List[str] = [],
                 linked_mod_folder_name: str = "!Mods_linked", copied_mod_folder_name: str = "!Mods_copied",
                 server_instance_prefix: str = "__server__", server_instance_root: str = "",
                 user_mods_list: List[str] = [], server_mods_list: List[str] = [], skip_keys: List[str] = [],
                 mod_fix_settings: Dict[str, str] = []):
        if arma_folder == "":
            arma_folder = os.path.join(os.getenv("ProgramFiles"), r"Steam\steamapps\common\Arma 3")
        if server_instance_root == "":
            server_instance_root = arma_folder
        server_drive = splitdrive(server_instance_root)[0]
        super(Box, self).__init__(server_instance_name=server_instance_name, arma_folder=arma_folder,
                                  bat_settings=bat_settings, config_settings=config_settings,
                                  mods_to_be_copied=mods_to_be_copied, linked_mod_folder_name=linked_mod_folder_name,
                                  copied_mod_folder_name=copied_mod_folder_name,
                                  server_instance_prefix=server_instance_prefix,
                                  server_instance_root=server_instance_root,
                                  user_mods_list=user_mods_list, server_mods_list=server_mods_list,
                                  skip_keys=skip_keys + ["!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"],
                                  server_drive=server_drive,
                                  mod_fix_settings=mod_fix_settings)
