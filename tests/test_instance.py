from os.path import isdir, isfile, islink, join, splitdrive
import pytest

from conftest import test_folder_structure_path
from odksm_test import ODKSMTest
from odk_servermanager.instance import ServerInstance, ServerInstanceSettings


class TestServerSettings:
    """Test: ServerInstanceSettings..."""

    def test_should_have_decent_default(self):
        """Server settings should have decent default."""
        instance_name = "server0"
        settings = ServerInstanceSettings(instance_name)
        assert settings.server_instance_name == instance_name
        assert settings.arma_folder == settings["arma_folder"]  # since it's a box
        assert settings.arma_folder == r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3"
        assert settings.mods_to_be_copied == []
        assert settings.linked_mod_folder_name == "!Mods_linked"
        assert settings.copied_mod_folder_name == "!Mods_copied"
        assert settings.server_instance_prefix == "__server__"
        assert settings.server_instance_root == r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3"

    def test_should_be_settable(self):
        """Server settings should be settable."""
        instance_name = "server0"
        arma_folder = r"C:\My Games\Arma 3"
        mods_to_be_copied = []
        linked_mod_folder_name = "!Mods_l"
        copied_mod_folder_name = "!Mods_c"
        server_instance_prefix = "__SSS__"
        server_instance_root = r"C:\My Servers\Arma 3"
        settings = ServerInstanceSettings(instance_name, arma_folder, mods_to_be_copied, linked_mod_folder_name,
                                          copied_mod_folder_name, server_instance_prefix, server_instance_root)
        assert settings.arma_folder == arma_folder
        assert settings.mods_to_be_copied == mods_to_be_copied
        assert settings.linked_mod_folder_name == linked_mod_folder_name
        assert settings.copied_mod_folder_name == copied_mod_folder_name
        assert settings.server_instance_prefix == server_instance_prefix
        assert settings.server_instance_root == server_instance_root


class TestAServerInstance:
    """Test: A server Instance..."""

    def test_should_save_its_config(self):
        """A server instance should save its config."""
        settings = ServerInstanceSettings("server0")
        instance = ServerInstance(settings)
        assert instance.S == settings


class TestWhenBatComposingTheServerInstance(ODKSMTest):
    """Test: when bat composing bat the server instance..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestCompileBat setup"""
        request.cls.test_path = test_folder_structure_path()
        server_instance_name = "TestServer0"
        request.cls.settings = ServerInstanceSettings(
            server_instance_name=server_instance_name,
            arma_folder=self.test_path,
            server_instance_root=self.test_path,
            server_title="ODK Training Server",
            mods_to_be_copied=["CBA_A3"],
            user_mods_list=["ace", "CBA_A3", "ODKAI"],
            server_mods_list=["AdvProp", "ODKMIN"],
            server_port="2202",
            server_config="serverTraining.cfg",
            server_cfg="Arma3Training.cfg",
            server_max_mem="8192",
            server_flags="-filePatching -autoinit -enableHT"
        )
        request.cls.instance = ServerInstance(self.settings)
        self.instance._compile_bat_file()
        request.cls.compiled_bat = join(self.instance._get_server_instance_path(), "run_server.bat")

    def test_should_create_the_bat_file(self):
        """When bat composing the server instance should create the bat file."""
        assert isfile(self.compiled_bat)

    def test_should_correctly_fill_in_settings(self):
        """When bat composing the server instance should correctly fill in settings."""
        test_bat = join("tests", "resources", "run_server.bat")
        with open(test_bat, "r") as test, open(self.compiled_bat, "r") as compiled:
            compiled_file = compiled.read()
            test_file = test.read()
            # fix generic path in the test file
            instance_path = self.instance._get_server_instance_path()
            test_file = test_file.replace(r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3",
                                          instance_path)
            test_file = test_file.replace("C:", splitdrive(self.compiled_bat)[0])
            assert test_file == compiled_file


class TestOurTestServerInstance(ODKSMTest):
    """Test: our test server instance..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestOurTestServerInstance setup"""
        server_name = "TestServer0"
        mods_to_be_copied = ["CBA_A3"]
        request.cls.test_path = test_folder_structure_path()
        request.cls.settings = ServerInstanceSettings(
            server_name,
            mods_to_be_copied=mods_to_be_copied,
            arma_folder=self.test_path,
            server_instance_root=self.test_path
        )
        request.cls.instance = ServerInstance(self.settings)

    def test_should_be_able_to_create_a_new_instance_folder(self, reset_folder_structure):
        """Our test server instance should be able to create a new instance folder."""
        server_name = "TestServer1"
        settings = ServerInstanceSettings(server_name, arma_folder=self.test_path, server_instance_root=self.test_path)
        instance = ServerInstance(settings)
        instance._new_server_folder()
        assert isdir(join(self.test_path, "__server__" + server_name))

    def test_should_raise_an_error_with_an_already_existing_server_instance(self, reset_folder_structure):
        """Create instance should raise an error with an already existing server instance."""
        from odk_servermanager.instance import DuplicateServerName
        with pytest.raises(DuplicateServerName) as err:
            self.instance._new_server_folder()

    def test_should_symlink_and_create_all_needed_stuff_from_the_main_folder(self, reset_folder_structure):
        """Create instance should symlink and create all needed stuff from the main folder."""
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        self.instance._prepare_server_core()
        # Check that it didn't copy over the wrong stuff
        assert not isdir(join(server_folder, "!Workshop"))
        assert not isdir(join(server_folder, "__server__TestServer0"))
        # Check all symlink
        assert islink(join(server_folder, "TestFolder1"))
        assert islink(join(server_folder, "TestFolder2"))
        assert islink(join(server_folder, "testFile0.txt"))
        assert islink(join(server_folder, "testFile3.txt"))
        assert isfile(join(server_folder, "TestFolder1", "testFile1.txt"))
        assert isfile(join(server_folder, "TestFolder2", "testFile2.txt"))
        # Check folders
        keys_folder = join(server_folder, "Keys")
        mods_linked_folder = join(server_folder, "!Mods_linked")
        mods_copied_folder = join(server_folder, "!Mods_copied")
        assert isdir(keys_folder) and not islink(keys_folder)
        assert isdir(mods_copied_folder) and not islink(mods_copied_folder)
        assert isdir(mods_linked_folder) and not islink(mods_linked_folder)

    def test_should_init_copied_and_linked_mods(self, reset_folder_structure):
        """Create instance should init copied and linked mods."""
        user_mods_list = ["ace", "CBA_A3", "ODKAI"]
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)

        # ensure the mod folders are there
        from os import mkdir
        mkdir(join(server_folder, "!Mods_copied"))
        mkdir(join(server_folder, "!Mods_linked"))

        self.instance._init_mods(user_mods_list)
        cba_folder = join(server_folder, "!Mods_copied", "@CBA_A3")
        assert isdir(cba_folder) and not islink(cba_folder)
        assert islink(join(server_folder, "!Mods_linked", "@ace"))
        assert islink(join(server_folder, "!Mods_linked", "@ODKAI"))
        assert islink(join(server_folder, "!Mods_linked", "!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"))

    def test_should_be_able_to_create_mods_relative_paths(self):
        """Our test server instance should be able to create mods relative paths."""
        assert self.instance._compose_relative_path_copied_mods("CBA_A3") == "!Mods_copied/@CBA_A3"
        assert self.instance._compose_relative_path_linked_mods("ace") == "!Mods_linked/@ace"

    def test_should_be_able_to_get_the_server_instance_path(self):
        """Our test server instance should be able to get the server instance path."""
        path = self.test_path + r"\__server__" + self.instance.S.server_instance_name
        assert self.instance._get_server_instance_path() == path