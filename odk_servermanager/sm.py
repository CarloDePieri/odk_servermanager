import os


class DuplicateServerName(Exception):
    """"""


def symlink(source: str, link_name: str) -> None:
    """A symlink function that should work both on Windows and on Linux."""
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()


def new_server_folder(server_name: str, server_root: str) -> None:
    """Create a new server folder."""
    server_folder = os.path.join(server_root, "__server__" + server_name)
    if not os.path.isdir(server_folder):
        os.mkdir(server_folder)
    else:
        raise DuplicateServerName()
