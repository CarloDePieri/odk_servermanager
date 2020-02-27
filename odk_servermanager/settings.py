from os.path import splitdrive

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
    :server_root: The complete path to the server instance root
    :server_port: The port the server is running on
    :server_config: The path to the config file
    :server_cfg: The path to the cfg file
    :server_max_mem: The max memory that the server will be able to allocate

    OPTIONAL FIELDS
    ---------------
    :server_flags: Default to empty, any addition flag to be passed to the server
    """

    def __init__(self, server_title: str, server_root: str, server_port: str, server_config: str, server_cfg: str,
                 server_max_mem: str, server_flags: str = "", **kwargs):
        server_drive = splitdrive(server_root)[0]
        super(Box, self).__init__(server_title=server_title, server_root=server_root, server_port=server_port,
                                  server_config=server_config, server_cfg=server_cfg, server_max_mem=server_max_mem,
                                  server_flags=server_flags, server_drive=server_drive, **kwargs)


