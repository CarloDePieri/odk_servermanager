import sys
from os.path import abspath

from odk_servermanager.manager import ServerManager


if __name__ == '__main__':
    config_file = abspath(sys.argv[1])
    sm = ServerManager(config_file=config_file)
    sm.manage_instance()
