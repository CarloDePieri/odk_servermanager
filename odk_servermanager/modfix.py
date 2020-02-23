from typing import Callable, List, Union

server_instance_cls = "ServerInstance"


class ModFix:
    """Class used to apply specific operations before, in place of or after copying a certain mod into its server
    instance folder.
    All hooks are function that take as only argument the ServerInstance object.

    :name: The mod DisplayName
    :hook_pre: This hook gets called before the mod copy begin.
    :hook_replace: This hook gets called instead of the usual mod copy.
    :hook_post: This hook gets called after the mod copy end.
    """
    hook_pre: Union[Callable[[server_instance_cls], None], None]
    hook_replace: Union[Callable[[server_instance_cls], None], None]
    hook_post: Union[Callable[[server_instance_cls], None], None]

    def __init__(self, name, hook_replace=None, hook_pre=None, hook_post=None):
        self.name = name
        self.hook_replace = hook_replace
        self.hook_pre = hook_pre
        self.hook_post = hook_post


registered_fix: List[ModFix] = []
