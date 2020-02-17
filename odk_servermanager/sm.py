from os.path import join, isdir
from os import listdir, mkdir
from typing import List, Dict

# CONFIG - put these here for now
MODS_TO_BE_COPIED = ["CBA_A3"]
LINKED_MOD_FOLDER_NAME = "!Mods_linked"
COPIED_MOD_FOLDER_NAME = "!Mods_copied"
SERVER_INSTANCE_PREFIX = "__server__"


class DuplicateServerName(Exception):
    """"""


def symlink(source: str, link_name: str) -> None:
    """A symlink function that should work both on Linux and Windows (old and new)."""
    import os
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()


def _compose_server_instance_path(server_name: str, server_root: str) -> str:
    """Compose the server folder name."""
    return join(server_root, SERVER_INSTANCE_PREFIX + server_name)


def new_server_folder(server_name: str, server_root: str) -> None:
    """Create a new server folder."""
    server_folder = _compose_server_instance_path(server_name, server_root)
    if not isdir(server_folder):
        mkdir(server_folder)
    else:
        raise DuplicateServerName()


def filter_symlinks(element: str) -> bool:
    """Filter out certain directory that won't be symlinked."""
    not_to_be_symlinked = ["!Workshop", "Keys"]
    return not (element.startswith(SERVER_INSTANCE_PREFIX) or element in not_to_be_symlinked)


def prepare_server_core(server_name: str, server_root: str) -> None:
    """Symlink or create all needed files and dir for a new server instance."""
    # make all needed symlink
    server_folder = _compose_server_instance_path(server_name, server_root)
    folder_list = listdir(server_root)
    to_be_linked = list(filter(lambda x: filter_symlinks(x), folder_list))
    for el in to_be_linked:
        src = join(server_root, el)
        dest = join(server_folder, el)
        symlink(src, dest)
    # Create the needed folder
    to_be_created = ["Keys", LINKED_MOD_FOLDER_NAME, COPIED_MOD_FOLDER_NAME]
    for folder in to_be_created:
        folder = join(server_folder, folder)
        mkdir(folder)


def _compose_relative_path_linked_mods(mod_name: str) -> str:
    """Helper used in bat compilation. Generate a linked mod paths."""
    return LINKED_MOD_FOLDER_NAME + "/@" + mod_name


def _compose_relative_path_copied_mods(mod_name: str) -> str:
    """Helper used in bat compilation. Generate a copied mod paths."""
    return COPIED_MOD_FOLDER_NAME + "/@" + mod_name


def _compose_relative_path_mods(mods_list: List[str]) -> str:
    """Helper used in bat compilation. Generate a full mod paths list."""
    user_mods = ""
    for mod in mods_list:
        if mod in MODS_TO_BE_COPIED:
            path = _compose_relative_path_copied_mods(mod)
        else:
            path = _compose_relative_path_linked_mods(mod)
        user_mods += path + ";"
    return user_mods


def compile_bat_file(server_name: str, server_root: str, settings: Dict, user_mods_list: List[str], server_mods_list: List[str]) -> None:
    """Compile an instance specific bat file to run the server."""
    import pkg_resources
    from jinja2 import Template
    # recover template file
    template_file_content = pkg_resources.resource_string('odk_servermanager', 'templates/run_server_template.txt')
    template = Template(template_file_content.decode("UTF-8"))
    # prepare needed elements
    compiled_bat_path = join(_compose_server_instance_path(server_name, server_root), "run_server.bat")
    user_mods = _compose_relative_path_mods(user_mods_list)
    server_mods = _compose_relative_path_mods(server_mods_list)
    # compile the template with all correct configuration and save the file
    compiled = template.render(
        server_title=settings["server_title"],
        server_port=settings["server_port"],
        server_max_mem=settings["server_max_mem"],
        server_config=settings["server_config"],
        server_cfg=settings["server_cfg"],
        server_flags=settings["server_flags"],
        server_drive=settings["server_drive"],
        server_root=settings["server_root"],
        user_mods=user_mods,
        server_mods=server_mods
    )
    with open(compiled_bat_path, "w+") as f:
        f.write(compiled)
