import os
import shutil
from typing import List


def is_keyfile(filename: str) -> bool:
    """Check if a file seems to be an Arma 3 mod key."""
    file_ext = os.path.splitext(filename)[-1].lower()
    return os.path.isfile(filename) and (file_ext == ".bikey")


def clear_keys_folder(folder_name: str) -> None:
    """Delete every key in the Keys folder."""
    for filename in os.listdir(folder_name):
        file_path = os.path.join(folder_name, filename)
        if is_keyfile(file_path):
            os.unlink(file_path)


def copy_keys(mods_list: List[str], mods_folder: str, keys_folder: str) -> None:
    """Copy all provided mods' keys into the keys_folder."""
    for mod_name in mods_list:
        mod_folder = os.path.join(mods_folder, "@" + mod_name)
        mod_key_folder = os.path.join(mod_folder, "keys")
        keyfile = list(filter(lambda x: is_keyfile(os.path.join(mod_key_folder, x)), os.listdir(mod_key_folder)))[0]
        src = os.path.join(mod_key_folder, keyfile)
        dest = os.path.join(keys_folder, keyfile)
        # copy of the file
        shutil.copy(src, dest)
        # copy over the permissions,modification
        shutil.copystat(src, dest)


def set_up_keys(mods_list: List[str], mods_folder: str, keys_folder: str) -> None:
    """Clear the keys folder and then copy all provided mods' keys there."""
    clear_keys_folder(keys_folder)
    copy_keys(mods_list, mods_folder, keys_folder)
