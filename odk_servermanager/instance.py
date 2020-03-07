from os import mkdir, listdir, unlink, remove
from os.path import isdir, islink, join, splitext, isfile, abspath
from typing import List

import pkg_resources

from odk_servermanager.settings import ServerInstanceSettings
from odk_servermanager.utils import symlink, compile_from_template, copytree, rmtree


class ServerInstance:
    """This class is responsible for creating and keeping updated all needed files to launch an
    Arma 3dedicated server instance."""

    keys_folder_name = "Keys"
    arma_keys = ["a3.bikey", "a3c.bikey", "gm.bikey"]
    warnings: List[str] = []

    def __init__(self, settings: ServerInstanceSettings):
        self.S = settings
        from odk_servermanager.modfix import register_fixes
        self.registered_fix = register_fixes()

    def get_server_instance_path(self) -> str:
        """Return the server instance path."""
        return join(self.S.server_instance_root, self.S.server_instance_prefix + self.S.server_instance_name)

    def is_folder_instance_already_there(self) -> bool:
        """Check if the folder instance is already present."""
        return isdir(self.get_server_instance_path())

    def _new_server_folder(self) -> None:
        """Create a new server folder."""
        if not self.is_folder_instance_already_there():
            mkdir(self.get_server_instance_path())
        else:
            raise DuplicateServerName()

    def _filter_symlinks(self, element: str) -> bool:
        """Filter out certain directory that won't be symlinked."""
        not_to_be_symlinked = ["!Workshop", self.keys_folder_name, "run_server.bat", self.S.bat_settings.server_config_file_name,
                               "__odksm__"]
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

    def _symlink_mod(self, mod_name) -> None:
        """Symlink a single mod in the linked mod folder."""
        server_folder = self.get_server_instance_path()
        workshop_folder = join(self.S.arma_folder, "!Workshop")
        mod_folder = "@" + mod_name
        target_folder = join(server_folder, self.S.linked_mod_folder_name)
        if not islink(join(target_folder, mod_folder)):
            symlink(join(workshop_folder, mod_folder), join(target_folder, mod_folder))

    def _symlink_warning_folder(self) -> None:
        """Symlink the warning folder inside the linked mod folder if needed."""
        server_folder = self.get_server_instance_path()
        workshop_folder = join(self.S.arma_folder, "!Workshop")
        linked_mod_folder = join(server_folder, self.S.linked_mod_folder_name)
        warning_folder_name = "!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"
        warning_folder = join(linked_mod_folder, warning_folder_name)
        if not islink(warning_folder):
            symlink(join(workshop_folder, warning_folder_name), warning_folder)

    def _copy_mod(self, mod_name):
        """Copy the given mod, taking care of calling the ModFix hook if a ModFix is registered."""
        server_folder = self.get_server_instance_path()
        workshop_folder = join(self.S.arma_folder, "!Workshop")
        mod_folder = "@" + mod_name
        # Check if mod fixes are registered for this mod
        mod_fix = list(filter(lambda x: x.name == mod_name, self.registered_fix))
        mod_fix = mod_fix[0] if len(mod_fix) > 0 else None
        # If available, call its pre hook
        if mod_fix is not None and mod_fix.hook_pre is not None:
            mod_fix.hook_pre(self)
        # Now check that the mod is not already copied
        target_folder = join(server_folder, self.S.copied_mod_folder_name)
        if not isdir(join(target_folder, mod_folder)):
            # If available, call its replace hook, else simply copy the mod
            if mod_fix is not None and mod_fix.hook_replace is not None:
                mod_fix.hook_replace(self)
            else:
                copytree(join(workshop_folder, mod_folder), join(target_folder, mod_folder))
        # If available, call its post hook
        if mod_fix is not None and mod_fix.hook_post is not None:
            mod_fix.hook_post(self)

    def _add_warning(self, message: str) -> None:
        """Add a warning to the warnings list."""
        if message not in self.warnings:
            self.warnings.append(message)

    def _init_mods(self, mods_list: List[str]) -> None:
        """This will link mods to an instance, copying or symlinking them."""
        if len(mods_list) > 0:
            for mod in mods_list:
                if mod in self.S.mods_to_be_copied:
                    self._copy_mod(mod)
                else:
                    self._symlink_mod(mod)
            self._symlink_warning_folder()

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
        if self.S.bat_settings.bat_template == "":
            template_file_content = self._read_resource_file('templates/run_server_template.txt')
        else:
            with open(self.S.bat_settings.bat_template, "r") as template:
                template_file_content = template.read()
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
        if self.S.config_settings.config_template == "":
            template_file_content = self._read_resource_file('templates/server_cfg_template.txt')
        else:
            with open(self.S.config_settings.config_template, "r") as template:
                template_file_content = template.read()
        compiled_config_path = join(self.get_server_instance_path(), self.S.bat_settings.server_config_file_name)
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
                # check if the key is already there
                if not islink(dest):
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

    def _check_mods_duplicate(self) -> None:
        """Check for mods duplicates in the mods lists."""
        mods = self.S.user_mods_list + self.S.server_mods_list
        for mod in mods:
            if mods.count(mod) > 1:
                op = "copy" if mod in self.S.mods_to_be_copied else "link"
                self._add_warning("Tried to {} the mod '{}' more than once! There's a duplicate "
                                  "somewhere!".format(op, mod))

    def _check_mods(self) -> None:
        """Perform some test on the mods lists."""
        self._check_mods_folders()
        self._check_mods_duplicate()

    def init(self) -> None:
        """Create the new instance folder, filled with everything needed to start it."""
        # check mods folder
        self._check_mods()
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
        # compile the config file
        self._compile_config_file()

    def _clear_linked_mods(self) -> None:
        """Clear the linked mods folder."""
        linked_mods_folder = join(self.get_server_instance_path(), self.S.linked_mod_folder_name)
        for mod in listdir(linked_mods_folder):
            if mod.startswith("@"):
                unlink(join(linked_mods_folder, mod))

    def _clear_copied_mod(self, mod_name: str) -> None:
        """Clear the copied mod folder."""
        copied_mods_folder = join(self.get_server_instance_path(), self.S.copied_mod_folder_name)
        rmtree(join(copied_mods_folder, "@" + mod_name))

    def _clear_old_copied_mods(self) -> None:
        """Delete all copied mods that are no longer in the mods_to_be_copied"""
        copied_mods_folder = join(self.get_server_instance_path(), self.S.copied_mod_folder_name)
        for mod in listdir(copied_mods_folder):
            if mod[1:] not in self.S.mods_to_be_copied:
                rmtree(join(copied_mods_folder, mod))

    def _update_copied_mod(self, mod_name: str) -> None:
        """Update a to be copied mod, calling the ModFix hooks if a ModFix is present."""
        # Check if mod fixes are registered for this mod
        mod_fix = list(filter(lambda x: x.name == mod_name, self.registered_fix))
        mod_fix = mod_fix[0] if len(mod_fix) > 0 else None
        # If available, call its pre update hook
        if mod_fix is not None and mod_fix.hook_update_pre is not None:
            mod_fix.hook_update_pre(self)
        if mod_fix is not None and mod_fix.hook_update_replace is not None:
            mod_fix.hook_update_replace(self)
        else:
            self._clear_copied_mod(mod_name)
            self._copy_mod(mod_name)
        if mod_fix is not None and mod_fix.hook_update_post is not None:
            mod_fix.hook_update_post(self)

    def _update_mods(self, mods: List[str]) -> None:
        """Update (symlinking or copying) all mods from a list."""
        for mod in mods:
            if mod in self.S.mods_to_be_copied:
                copied_mods_folder = join(self.get_server_instance_path(), self.S.copied_mod_folder_name)
                already_there_mods = map(lambda x: x[1:], listdir(copied_mods_folder))
                if mod in already_there_mods:
                    # These are the only ones that get really updated
                    self._update_copied_mod(mod)
                else:
                    self._copy_mod(mod)
            else:
                self._symlink_mod(mod)

    def _update_all_mods(self) -> None:
        """Update both user and server mods and perform some cleanup tasks."""
        self._clear_linked_mods()
        self._clear_old_copied_mods()
        self._update_mods(self.S.user_mods_list)
        self._update_mods(self.S.server_mods_list)
        self._symlink_warning_folder()

    def _clear_keys(self) -> None:
        """Clear all keys from the keys folder except the arma ones."""
        keys_dir = join(self.get_server_instance_path(), self.keys_folder_name)
        for key in listdir(keys_dir):
            key_file = join(keys_dir, key)
            if key not in self.arma_keys and self._is_keyfile(key_file):
                if islink(key_file):
                    unlink(key_file)
                else:
                    remove(key_file)

    def _update_keys(self) -> None:
        """Reset the keys and relink them."""
        self._clear_keys()
        self._link_keys()

    def _clear_compiled_files(self) -> None:
        """Delete all compiled files."""
        for file in ["run_server.bat", self.S.bat_settings.server_config_file_name]:
            remove(join(self.get_server_instance_path(), file))

    def _update_compiled_files(self) -> None:
        """Delete and regenerate all compiled files"""
        self._clear_compiled_files()
        self._compile_bat_file()
        self._compile_config_file()

    def update(self) -> None:
        """Update an existing instance. This method assumes that the server instance is already there and functioning!
        This will relink all linked mods and keys. It will REPLACE compiled files like run_server.bat and the server
        config file with newly generated ones. By default this will also REPLACE all copied mod."""
        self._check_mods()
        self._update_all_mods()
        self._update_keys()
        self._update_compiled_files()


class DuplicateServerName(Exception):
    """"""


class ModNotFound(Exception):
    """"""
