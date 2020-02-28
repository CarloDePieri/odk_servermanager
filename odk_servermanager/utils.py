import shutil
from os.path import isdir, abspath
from typing import Dict


def symlink(source: str, link_name: str) -> None:
    """A symlink function that should work both on Linux and Windows (old and new)."""
    source = abspath(source)
    link_name = abspath(link_name)
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


def copytree(source: str, dest: str) -> None:
    """Copy a folder using shutil.copytree, and ensure we pass in absolute paths."""
    source = abspath(source)
    dest = abspath(dest)
    shutil.copytree(source, dest)


def copy(source: str, dest: str) -> None:
    """Copy a file using shutil.copy2, and ensure we pass in absolute paths."""
    source = abspath(source)
    dest = abspath(dest)
    shutil.copy2(source, dest)


def rmtree(target: str) -> None:
    """Delete a folder with shutil.rmtree ensuring we use an absolute paths."""
    target = abspath(target)
    shutil.rmtree(target)


def compile_from_template(template_file_content: str, compiled_file: str, settings: Dict) -> None:
    """Read a template file and compiled it with the provided settings"""
    from jinja2 import Template
    template = Template(template_file_content)
    compiled = template.render(settings)
    with open(compiled_file, "w+") as f:
        f.write(compiled)
