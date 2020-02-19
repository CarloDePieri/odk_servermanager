import shutil
from os import mkdir, listdir
from os.path import isdir, join, splitdrive
from typing import List

from box import Box

from odk_servermanager.utils import symlink

default_arma_path = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3"


class ServerInstanceSettings(Box):
    """TODO"""
    # DOC FOR EACH SETTING
    # ODKSM settings
    server_instance_name: str
    arma_folder: str
    server_instance_root: str
    server_instance_prefix: str
    linked_mod_folder_name: str
    copied_mod_folder_name: str
    # mods
    mods_to_be_copied: List[str]
    user_mods_list: List[str]
    server_mods_list: List[str]
    # ARMA settings
    server_title: str
    server_port: str
    server_config: str
    server_cfg: str
    server_max_mem: str
    server_flags: str

    def __init__(self,
                 server_instance_name: str,
                 arma_folder=default_arma_path,
                 mods_to_be_copied=None,
                 linked_mod_folder_name="!Mods_linked",
                 copied_mod_folder_name="!Mods_copied",
                 server_instance_prefix="__server__",
                 server_instance_root=default_arma_path,
                 user_mods_list=None,
                 server_mods_list=None,
                 server_title="ODK Training Server",
                 server_port="2202",
                 server_config="serverCfg.cfg",
                 server_cfg="serverConfig.cfg",
                 server_max_mem="8192",
                 server_flags=""
                 ):
        super().__init__(
            server_instance_name=server_instance_name,
            arma_folder=arma_folder,
            server_instance_root=server_instance_root,
            server_instance_prefix=server_instance_prefix,
            copied_mod_folder_name=copied_mod_folder_name,
            linked_mod_folder_name=linked_mod_folder_name,
            mods_to_be_copied=mods_to_be_copied if mods_to_be_copied is not None else [],
            user_mods_list=user_mods_list if user_mods_list is not None else [],
            server_mods_list=server_mods_list if mods_to_be_copied is not None else [],
            server_title=server_title,
            server_port=server_port,
            server_config=server_config,
            server_cfg=server_cfg,
            server_max_mem=server_max_mem,
            server_flags=server_flags
            )


class ServerInstance:
    """TODO"""

    def __init__(self, settings: ServerInstanceSettings):
        self.S = settings

    def _get_server_instance_path(self) -> str:
        """Return the server instance path."""
        return join(self.S.server_instance_root, self.S.server_instance_prefix + self.S.server_instance_name)

    def _new_server_folder(self) -> None:
        """Create a new server folder."""
        server_folder = self._get_server_instance_path()
        if not isdir(server_folder):
            mkdir(server_folder)
        else:
            raise DuplicateServerName()

    def _filter_symlinks(self, element: str) -> bool:
        """Filter out certain directory that won't be symlinked."""
        not_to_be_symlinked = ["!Workshop", "Keys"]
        return not (element.startswith(self.S.server_instance_prefix) or element in not_to_be_symlinked)

    def _prepare_server_core(self) -> None:
        """Symlink or create all needed files and dir for a new server instance."""
        # make all needed symlink
        server_folder = self._get_server_instance_path()
        arma_folder_list = listdir(self.S.arma_folder)
        to_be_linked = list(filter(lambda x: self._filter_symlinks(x), arma_folder_list))
        for el in to_be_linked:
            src = join(self.S.arma_folder, el)
            dest = join(server_folder, el)
            symlink(src, dest)
        # Create the needed folder
        to_be_created = ["Keys", self.S.linked_mod_folder_name, self.S.copied_mod_folder_name]
        for folder in to_be_created:
            folder = join(server_folder, folder)
            mkdir(folder)

    def _init_mods(self, mods_list: List[str]) -> None:
        """This will link mods to an instance, copying or symlinking them."""
        server_folder = self._get_server_instance_path()
        workshop_folder = join(self.S.arma_folder, "!Workshop")
        for mod in mods_list:
            mod_folder = "@" + mod
            if mod in self.S.mods_to_be_copied:
                fun = shutil.copytree  # this will actually copy the mod
                target_folder = join(server_folder, self.S.copied_mod_folder_name)
            else:
                fun = symlink  # this will simply symlink the mod
                target_folder = join(server_folder, self.S.linked_mod_folder_name)
            fun(join(workshop_folder, mod_folder), join(target_folder, mod_folder))
        linked_mod_folder = join(server_folder, self.S.linked_mod_folder_name)
        warning_folder = "!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"
        symlink(join(workshop_folder, warning_folder), join(linked_mod_folder, warning_folder))

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
        import pkg_resources
        from jinja2 import Template
        # recover template file
        template_file_content = pkg_resources.resource_string('odk_servermanager', 'templates/run_server_template.txt')
        template = Template(template_file_content.decode("UTF-8"))
        # prepare needed elements
        compiled_bat_path = join(self._get_server_instance_path(), "run_server.bat")
        user_mods = self._compose_relative_path_mods(self.S.user_mods_list)
        server_mods = self._compose_relative_path_mods(self.S.server_mods_list)
        instance_path = self._get_server_instance_path()
        # compile the template with all correct configuration and save the file
        compiled = template.render(
            server_title=self.S.server_title,
            server_port=self.S.server_port,
            server_max_mem=self.S.server_max_mem,
            server_config=self.S.server_config,
            server_cfg=self.S.server_cfg,
            server_flags=self.S.server_flags,
            server_drive=splitdrive(instance_path)[0],
            server_root='"{}"'.format(instance_path),
            user_mods=user_mods,
            server_mods=server_mods
        )
        with open(compiled_bat_path, "w+") as f:
            f.write(compiled)


class DuplicateServerName(Exception):
    """"""