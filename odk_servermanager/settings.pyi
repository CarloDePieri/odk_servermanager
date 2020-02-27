from typing import List, Dict


class ServerConfigSettings:
    hostname: str
    password: str
    password_admin: str
    template: str


class ServerBatSettings:
    server_title: str
    server_port: str
    server_config: str
    server_cfg: str
    server_max_mem: str
    server_flags: str


class ServerInstanceSettings:
    server_instance_name: str
    bat_settings: ServerBatSettings
    config_settings: ServerConfigSettings
    arma_folder: str
    server_instance_root: str
    server_drive: str
    server_instance_prefix: str
    linked_mod_folder_name: str
    copied_mod_folder_name: str
    mods_to_be_copied: List[str]
    user_mods_list: List[str]
    server_mods_list: List[str]
    skip_keys: List[str]
    mod_fix_settings: Dict[str, str]
