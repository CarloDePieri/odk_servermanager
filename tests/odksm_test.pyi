from odk_servermanager.manager import ServerManager
from odk_servermanager.instance import ServerInstance, ServerInstanceSettings


class ODKSMTest:
    manager: ServerManager
    instance: ServerInstance
    settings: ServerInstanceSettings