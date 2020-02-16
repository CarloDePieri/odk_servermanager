from os.path import join, isdir
from os import listdir, mkdir


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
    return join(server_root, "__server__" + server_name)


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
    return not (element.startswith("__server__") or element in not_to_be_symlinked)


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
    to_be_created = ["Keys", "!Mods_linked", "!Mods_copied"]
    for folder in to_be_created:
        folder = join(server_folder, folder)
        mkdir(folder)
