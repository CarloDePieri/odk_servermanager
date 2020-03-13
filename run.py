import argparse
from os.path import abspath

from odk_servermanager.manager import ServerManager


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug-logs-path")
    parser.add_argument("--config")
    settings = parser.parse_args()
    config_file = abspath(settings.config)
    if settings.debug_logs_path is not None:
        sm = ServerManager(config_file=config_file, debug_logs_path=settings.debug_logs_path)
    else:
        sm = ServerManager(config_file=config_file)
    sm.manage_instance()
