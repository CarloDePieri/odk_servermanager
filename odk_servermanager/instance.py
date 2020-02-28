import shutil
from os import mkdir, listdir
from os.path import isdir, islink, join, splitext, isfile, abspath
from typing import List

import pkg_resources

from odk_servermanager.settings import ServerInstanceSettings
from odk_servermanager.utils import symlink, compile_from_template


class ServerInstance:
    """This class is responsible for creating and keeping updated all needed files to launch an
    Arma 3dedicated server instance."""

    keys_folder_name = "Keys"
    arma_keys = ["a3.bikey", "a3c.bikey", "gm.bikey"]

    def __init__(self, settings: ServerInstanceSettings):
        self.S = settings
        from odk_servermanager.modfix import registered_fix
        self.registered_fix = registered_fix

    def get_server_instance_path(self) -> str:
        """Return the server instance path."""
        return join(self.S.server_instance_root, self.S.server_instance_prefix + self.S.server_instance_name)

    def _new_server_folder(self) -> None:
        """Create a new server folder."""
        server_folder = self.get_server_instance_path()
        if not isdir(server_folder):
            mkdir(server_folder)
        else:
            raise DuplicateServerName()

    def _filter_symlinks(self, element: str) -> bool:
        """Filter out certain directory that won't be symlinked."""
        not_to_be_symlinked = ["!Workshop", self.keys_folder_name, "run_server.bat", self.S.bat_settings.server_config]
        return not (element.startswith(self.S.server_instance_prefix) or element in not_to_be_symlinked)

    def _prepare_server_core(self) -> None:
        """Symlink or create all needed files and dir for a new server instance."""
        # make all needed symlink
        server_folder = self.get_server_instance_path()
        arma_folder_list = listdir(self.S.arma_folder)
        to_be_linked = list(filter(lambda x: self._filter_symlinks(x), arma_folder_list))
        for el in to_be_linked:
            src = join(self.S.arma_folder, el)
            dest = join(server_folder, el)
            symlink(src, dest)
        # Create the needed folder
        to_be_created = [self.keys_folder_name, self.S.linked_mod_folder_name, self.S.copied_mod_folder_name]
        for folder in to_be_created:
            folder = join(server_folder, folder)
            mkdir(folder)
        # Copy the arma keyfiles
        for key in self.arma_keys:
            arma_key_folder = join(self.S.arma_folder, self.keys_folder_name)
            instance_key_folder = join(server_folder, self.keys_folder_name)
            symlink(join(arma_key_folder, key), join(instance_key_folder, key))

    def _init_mods(self, mods_list: List[str]) -> None:
        """This will link mods to an instance, copying or symlinking them."""
        if len(mods_list) > 0:
            server_folder = self.get_server_instance_path()
            workshop_folder = join(self.S.arma_folder, "!Workshop")
            for mod in mods_list:
                mod_folder = "@" + mod
                if mod in self.S.mods_to_be_copied:
                    # Check if mod fixes are registered for this mod
                    mod_fix = list(filter(lambda x: x.name == mod, self.registered_fix))
                    mod_fix = mod_fix[0] if len(mod_fix) > 0 else None
                    # If available, call its pre hook
                    if mod_fix is not None and mod_fix.hook_pre is not None:
                        mod_fix.hook_pre(self)
                    # If available, call its replace hook, else simply copy the mod
                    if mod_fix is not None and mod_fix.hook_replace is not None:
                        mod_fix.hook_replace(self)
                    else:
                        target_folder = join(server_folder, self.S.copied_mod_folder_name)
                        shutil.copytree(join(workshop_folder, mod_folder), join(target_folder, mod_folder))
                    # If available, call its post hook
                    if mod_fix is not None and mod_fix.hook_post is not None:
                        mod_fix.hook_post(self)
                else:
                    target_folder = join(server_folder, self.S.linked_mod_folder_name)
                    symlink(join(workshop_folder, mod_folder), join(target_folder, mod_folder))
            linked_mod_folder = join(server_folder, self.S.linked_mod_folder_name)
            warning_folder_name = "!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"
            warning_folder = join(linked_mod_folder, warning_folder_name)
            if not islink(warning_folder):
                symlink(join(workshop_folder, warning_folder_name), warning_folder)

    def _compose_relative_path_linked_mods(self, mod_name: str) -> str:
        """Helper used in bat compilation. Generate a linked mod paths."""
        return self.S.linked_mod_folder_name + "/@" + mod_name

    def _compose_relative_path_copied_mods(self, mod_name: str) -> str:
        """Helper used in bat compilation. Generate a copied mod paths."""
        return self.S.copied_mod_folder_name + "/@" + mod_name

    def _compose_relative_path_mods(self, mods_list: List[str]) -> str:
        """Helper used in bat compilation. Generate a full mod paths list."""
        user_mods = ""
        for mod in mods_list:
            if mod in self.S.mods_to_be_copied:
                path = self._compose_relative_path_copied_mods(mod)
            else:
                path = self._compose_relative_path_linked_mods(mod)
            user_mods += path + ";"
        return user_mods

    def _compile_bat_file(self) -> None:
        """Compile an instance specific bat file to run the server."""
        # recover template file and prepare composed bat file path
        template_file_content = self._read_resource_file('templates/run_server_template.txt')
        compiled_bat_path = join(self.get_server_instance_path(), "run_server.bat")
        # prepare settings
        settings = self.S.bat_settings.copy()
        settings.user_mods = self._compose_relative_path_mods(self.S.user_mods_list)
        settings.server_mods = self._compose_relative_path_mods(self.S.server_mods_list)
        settings.server_drive = self.S.server_drive
        settings.server_root = self.get_server_instance_path()
        # compose and save the bat
        compile_from_template(template_file_content, compiled_bat_path, settings)

    def _compile_config_file(self) -> None:
        """Compile an instance specific cfg file that will be passed as -config flag to the server."""
        # recover template file and prepare composed bat file path
        template_file_content = self._read_resource_file('templates/server_cfg_template.txt')
        compiled_config_path = join(self.get_server_instance_path(), self.S.bat_settings.server_config)
        # prepare settings
        settings = self.S.config_settings.to_dict()
        # compose and save the bat
        compile_from_template(template_file_content, compiled_config_path, settings)

    @staticmethod
    def _read_resource_file(file: str) -> str:
        """Return the content of a resource file."""
        return pkg_resources.resource_string('odk_servermanager', file).decode("UTF-8")

    @staticmethod
    def _is_keyfile(filename: str) -> bool:
        """Check if a file seems to be an Arma 3 mod key."""
        file_ext = splitext(filename)[-1].lower()
        return (isfile(filename) or islink(filename)) and (file_ext == ".bikey")

    def _link_keys_in_folder(self, folder: str) -> None:
        """Link alla keys from the mod in the given folder to the instance keys folder."""
        for mod_folder_name in filter(lambda x: x not in self.S.skip_keys, listdir(folder)):
            mod_folder = abspath(join(folder, mod_folder_name))
            # look for the key folder there
            key_folder = list(filter(lambda name: name.lower() == "keys" or name.lower() == "key", listdir(mod_folder)))
            if len(key_folder) > 0:
                # if there's one, the key inside needs to be linked over the main key folder
                mod_key_folder = join(mod_folder, key_folder[0])
                key_file = list(filter(lambda x: self._is_keyfile(join(mod_key_folder, x)), listdir(mod_key_folder)))[0]
                src = join(mod_key_folder, key_file)
                dest = join(self.get_server_instance_path(), self.keys_folder_name, key_file)
                symlink(src, dest)

    def _link_keys(self) -> None:
        """Link all keys from the copied and the linked mod folders to the instance keys folder."""
        root = self.get_server_instance_path()
        self._link_keys_in_folder(join(root, self.S.copied_mod_folder_name))
        self._link_keys_in_folder(join(root, self.S.linked_mod_folder_name))

    def _check_mods_folders(self) -> None:
        """Check that every specified mod is present in the main !Workshop dir."""
        mods_folders_name = listdir(join(self.S.arma_folder, "!Workshop"))
        mods = self.S.user_mods_list + self.S.server_mods_list + self.S.mods_to_be_copied
        for mod in mods:
            if "@" + mod not in mods_folders_name:
                raise ModNotFound("Could not find a mod named {}".format(mod))

    def init(self):
        """Create the new instance folder, filled with everything needed to start it."""
        # check mods folder
        self._check_mods_folders()
        # create the folder
        self._new_server_folder()
        # prepare all arma files and folder
        self._prepare_server_core()
        # symlink or copy user and server mods
        self._init_mods(self.S.user_mods_list)
        self._init_mods(self.S.server_mods_list)
        # link keys
        self._link_keys()
        # compile the bat
        self._compile_bat_file()


class DuplicateServerName(Exception):
    """"""


class ModNotFound(Exception):
    """"""
