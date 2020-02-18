import pytest

import odk_servermanager.sm as sm
from conftest import test_folder_structure_path
from os.path import islink, isfile, isdir, join


class TestCreateInstance:
    """Test: create instance..."""
    test_path = test_folder_structure_path()

    def test_should_create_a_new_folder_with_a_given_name(self, reset_folder_structure):
        """Create instance should create a new folder with a given name."""
        server_name = "TestServer1"
        sm.new_server_folder(server_name)
        assert isdir(join(self.test_path, "__server__" + server_name))

    def test_should_raise_an_error_with_an_already_existing_server_instance(self, reset_folder_structure):
        """Create instance should raise an error with an already existing server instance."""
        server_name = "TestServer0"
        from odk_servermanager.sm import DuplicateServerName
        with pytest.raises(DuplicateServerName) as err:
            sm.new_server_folder(server_name)

    def test_should_symlink_and_create_all_needed_stuff_from_the_main_folder(self, reset_folder_structure, mocker):
        """Create instance should symlink and create all needed stuff from the main folder."""
        server_name = "TestServer0"
        server_folder = join(self.test_path, "__server__" + server_name)
        mocker.patch("odk_servermanager.sm.ARMA_FOLDER", self.test_path)
        sm.prepare_server_core(server_name)
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
        server_name = "TestServer0"
        server_folder = join(self.test_path, "__server__" + server_name)
        # ensure the mod folders are there
        from os import mkdir
        mkdir(join(server_folder, "!Mods_copied"))
        mkdir(join(server_folder, "!Mods_linked"))
        sm.init_mods(user_mods_list, server_name)
        cba_folder = join(server_folder, "!Mods_copied", "@CBA_A3")
        assert isdir(cba_folder) and not islink(cba_folder)
        assert islink(join(server_folder, "!Mods_linked", "@ace"))
        assert islink(join(server_folder, "!Mods_linked", "@ODKAI"))
        assert islink(join(server_folder, "!Mods_linked", "!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"))


class TestCompileBat:
    """Test: CompileBat..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestCompileBat setup"""
        test_path = test_folder_structure_path()
        server_name = "TestServer0"
        user_mods_list = ["ace", "CBA_A3", "ODKAI"]
        server_mods_list = ["AdvProp", "ODKMIN"]
        settings = {
            "server_title": "ODK Training Server",
            "server_drive": "C:",
            "server_root": r'"C:\Program Files (x86)\Steam\steamapps\common\Arma 3"',
            "server_port": "2202",
            "server_config": "serverTraining.cfg",
            "server_cfg": "Arma3Training.cfg",
            "server_max_mem": "8192",
            "server_flags": "-filePatching -autoinit -enableHT"
        }
        sm.compile_bat_file(server_name, settings, user_mods_list, server_mods_list)
        server_folder = join(test_path, sm._get_server_instance_path(server_name))
        request.cls.compiled_bat = join(server_folder, "run_server.bat")

    def test_should_create_the_bat_file(self):
        """Compile bat should create the bat file."""
        assert isfile(self.compiled_bat)

    def test_should_correctly_fill_out_settings(self):
        """Compile bat should correctly fill out settings."""
        test_bat = join("tests", "resources", "run_server.bat")
        with open(test_bat, "r") as test, open(self.compiled_bat, "r") as compiled:
            assert test.read() == compiled.read()


class TestUtils:
    """Test: Utils..."""

    def test_for_composing_mods_relative_path_should_work(self):
        """Utils for composing mods relative path should work."""
        assert sm._compose_relative_path_copied_mods("CBA_A3") == "!Mods_copied/@CBA_A3"
        assert sm._compose_relative_path_linked_mods("ace") == "!Mods_linked/@ace"

    def test_should_be_able_to_get_a_server_instance_path(self):
        """Utils should be able to get a server instance path."""
        from conftest import test_folder_structure_path
        assert sm._get_server_instance_path("Server1") == test_folder_structure_path() + r"\__server__Server1"
