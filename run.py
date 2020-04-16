import argparse
from os.path import abspath
from typing import Dict

from odk_servermanager.manager import ServerManager


def parse_cmdline() -> Dict:
    """Parse the command line and return a dict containing data needed to start operations."""
    opts = {}
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--manage")
    group.add_argument("-b", "--bootstrap")
    group.add_argument("-c", "--config")  # DEPRECATED
    parser.add_argument("--debug-logs-path")
    settings = parser.parse_args()
    if settings.manage is not None or settings.config is not None:
        # manage was set, so this is a manage op
        opts["op"] = "manage"
        if settings.manage is not None:
            opts["config_file"] = abspath(settings.manage)
        else:
            opts["config_file"] = abspath(settings.config)
            print("\n [WARN] Deprecated flag '--config' should be replaced with '--manage'.\n\n")
    else:
        # bootstrap was set instead
        opts["op"] = "bootstrap"
        opts["config_file"] = abspath(settings.bootstrap)
    opts["debug_logs_path"] = settings.debug_logs_path
    return opts


def run() -> None:
    """Decide which operation is requested and execute it."""
    settings = parse_cmdline()
    if settings["debug_logs_path"] is not None:
        sm = ServerManager(debug_logs_path=settings["debug_logs_path"])
    else:
        sm = ServerManager()
    if settings["op"] == "manage":
        sm.manage_instance(settings["config_file"])
    elif settings["op"] == "bootstrap":
        sm.bootstrap(settings["config_file"])


if __name__ == '__main__':
    run()
