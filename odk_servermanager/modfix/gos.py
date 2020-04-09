from os import mkdir
from os.path import join, isdir
from typing import List

from odk_servermanager.instance import ServerInstance
from odk_servermanager.modfix import ModFix
from odk_servermanager.utils import symlink, symlink_everything_from_folder, rmtree


class ModFixGOS(ModFix):
    """ModFix for all GOS mods... it allows the symlinking of keys even with their unusual folders structure."""

    name: str = "gos"
    mods: List[str] = ["G.O.S Al Rayak", "G.O.S Dariyah", "G.O.S Gunkizli", "G.O.S Kalu Khan", "G.O.S Leskovets",
                       "G.O.S N'ziwasogo", "G.O.S Song Bin Tahn", "G.O.S Song Bin Tanh 2.0 (APEX)"]
    keys_folder_name: str = "PublicKey_GOS_Makhno"

    def does_apply_to_mod(self, mod_name: str) -> bool:
        """Check that the mod is in the supported mods list."""
        return mod_name in self.mods

    def update_mods_to_be_copied_list(self, mods_to_be_copied_list: List[str],
                                      user_mods_list: List[str], server_mods_list: List[str]) -> None:
        """Update the given mods_to_be_copied list with all needed mods from our mods list."""
        requested_mods = list(filter(lambda mod: mod in user_mods_list or mod in server_mods_list, self.mods))
        for requested_mod in requested_mods:
            if requested_mod not in mods_to_be_copied_list:
                mods_to_be_copied_list.append(requested_mod)

    def hook_init_copy_replace(self, server_instance: ServerInstance, call_data: List[str]) -> None:
        """Put the mod in copied_mods folder and symlink everything from the original mod, then simulate a regular
        folder structure."""
        mod_name = call_data[2]
        target_mod_folder = join(server_instance.get_server_instance_path(), server_instance.S.copied_mod_folder_name,
                                 "@{}".format(mod_name))
        self._do_op(mod_name, server_instance.S.arma_folder, target_mod_folder)

    def hook_update_copy_replace(self, server_instance: ServerInstance, call_data: List[str]) -> None:
        """Exactly the same as the init_copy, but ensure the folder is deleted first, to start anew."""
        mod_name = call_data[2]
        target_mod_folder = join(server_instance.get_server_instance_path(), server_instance.S.copied_mod_folder_name,
                                 "@{}".format(mod_name))
        if isdir(target_mod_folder):
            # Delete the old folder, it's better to start anew
            rmtree(target_mod_folder)
        self._do_op(mod_name, server_instance.S.arma_folder, target_mod_folder)

    def _do_op(self, mod_name, arma_folder, target_mod_folder) -> None:
        """Actually create the folder, symlink everything and symlink the keys folder."""
        mod_folder = join(arma_folder, "!Workshop", "@{}".format(mod_name))
        mkdir(target_mod_folder)
        symlink_everything_from_folder(mod_folder, target_mod_folder)
        unusual_keys_folder = join(target_mod_folder, self.keys_folder_name)
        correct_keys_folder = join(target_mod_folder, "Keys")
        symlink(unusual_keys_folder, correct_keys_folder)


to_be_registered = ModFixGOS()
