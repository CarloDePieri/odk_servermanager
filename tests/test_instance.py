from os.path import isdir, isfile, islink, join, splitdrive
from os import listdir, mkdir
import pytest

from conftest import test_folder_structure_path, spy
from odksm_test import ODKSMTest
from odk_servermanager.instance import ServerInstance
from odk_servermanager.settings import ServerInstanceSettings, ServerBatSettings


class TestAServerInstance:
    """Test: A server Instance..."""

    def test_should_save_its_config(self, sc_stub, sb_stub):
        """A server instance should save its config."""
        settings = ServerInstanceSettings("server0", sb_stub, sc_stub)
        instance = ServerInstance(settings)
        assert instance.S == settings


class TestWhenBatComposingTheServerInstance(ODKSMTest):
    """Test: when bat composing bat the server instance..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub):
        """TestCompileBat setup"""
        request.cls.test_path = test_folder_structure_path()
        server_instance_name = "TestServer0"
        sb = ServerBatSettings(server_title="ODK Training Server", server_port="2202",
                               server_config="serverTraining.cfg", server_cfg="Arma3Training.cfg",
                               server_max_mem="8192", server_flags="-filePatching -autoinit -enableHT")
        sc = c_sc_stub
        request.cls.settings = ServerInstanceSettings(
            server_instance_name=server_instance_name,
            bat_settings=sb,
            config_settings=sc,
            arma_folder=self.test_path,
            server_instance_root=self.test_path,
            mods_to_be_copied=["CBA_A3"],
            user_mods_list=["ace", "CBA_A3", "ODKAI"],
            server_mods_list=["AdvProp", "ODKMIN"],
        )
        request.cls.instance = ServerInstance(self.settings)
        self.instance._compile_bat_file()
        request.cls.compiled_bat = join(self.instance.get_server_instance_path(), "run_server.bat")

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
            instance_path = self.instance.get_server_instance_path()
            test_file = test_file.replace(r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3",
                                          instance_path)
            test_file = test_file.replace("C:", splitdrive(self.compiled_bat)[0])
            assert test_file == compiled_file


class TestOurTestServerInstance(ODKSMTest):
    """Test: our test server instance..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, c_sc_stub, c_sb_stub):
        """TestOurTestServerInstance setup"""
        server_name = "TestServer0"
        mods_to_be_copied = ["CBA_A3"]
        request.cls.test_path = test_folder_structure_path()
        request.cls.sb = c_sb_stub
        request.cls.sc = c_sc_stub
        request.cls.settings = ServerInstanceSettings(
            server_name,
            self.sb, self.sc,
            mods_to_be_copied=mods_to_be_copied,
            arma_folder=self.test_path,
            server_instance_root=self.test_path
        )
        request.cls.instance = ServerInstance(self.settings)

    def test_should_be_able_to_create_a_new_instance_folder(self, reset_folder_structure):
        """Our test server instance should be able to create a new instance folder."""
        server_name = "TestServer1"
        settings = self.settings.copy()
        settings.server_instance_name = server_name
        instance = ServerInstance(settings)
        instance._new_server_folder()
        assert isdir(join(self.test_path, "__server__" + server_name))

    def test_should_raise_an_error_with_an_already_existing_server_instance(self, reset_folder_structure):
        """Create instance should raise an error with an already existing server instance."""
        from odk_servermanager.instance import DuplicateServerName
        with pytest.raises(DuplicateServerName):
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
        # Check Mods
        mods_linked_folder = join(server_folder, "!Mods_linked")
        mods_copied_folder = join(server_folder, "!Mods_copied")
        assert isdir(mods_copied_folder) and not islink(mods_copied_folder)
        assert isdir(mods_linked_folder) and not islink(mods_linked_folder)
        # Check keys
        keys_folder = join(server_folder, "Keys")
        assert isdir(keys_folder) and not islink(keys_folder)
        assert isfile(join(keys_folder, "a3.bikey"))
        assert isfile(join(keys_folder, "a3c.bikey"))
        assert isfile(join(keys_folder, "gm.bikey"))

    def test_should_protect_run_server_bat(self, reset_folder_structure):
        """Our test server instance should protect run_server.bat."""
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        with open(join(self.test_path, "run_server.bat"), "w+") as f:
            f.write("protected")
        self.instance._prepare_server_core()
        assert not islink(join(server_folder, "run_server.bat"))

    def test_should_init_copied_and_linked_mods(self, reset_folder_structure):
        """Create instance should init copied and linked mods."""
        user_mods_list = ["ace", "CBA_A3", "ODKAI"]
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        # ensure the mod folders are there
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
        assert self.instance.get_server_instance_path() == path

    def test_should_be_able_to_recognize_a_key_file(self, reset_folder_structure):
        """Our test server instance should be able to recognize a key file."""
        assert self.instance._is_keyfile(join(self.test_path, "!Workshop", "@ace", "keys", "ace_3.13.0.45.bikey"))
        assert not self.instance._is_keyfile(join(self.test_path, "testFile0.txt"))

    def test_should_be_able_to_symlink_all_needed_keys(self, reset_folder_structure):
        """Our test server instance should be able to symlink all needed keys."""
        # THIS TEST DEPENDS ON _prepare_server_core AND _init_mods ... would be too long to set up otherwise
        user_mods_list = ["ace", "CBA_A3", "ODKAI"]
        server_mods_list = ["ODKMIN"]
        self.instance.S.user_mods_list = user_mods_list
        self.instance.S.server_mods_list = server_mods_list
        self.instance._prepare_server_core()
        self.instance._init_mods(user_mods_list)
        self.instance._init_mods(server_mods_list)
        keys_folder = join(self.instance.get_server_instance_path(), self.instance.keys_folder_name)
        # end setup, begin actual test
        self.instance._link_keys()
        keys_folder_files = listdir(keys_folder)
        assert len(keys_folder_files) == len(self.instance.S.user_mods_list) + len(
            self.instance.S.server_mods_list) + len(self.instance.arma_keys)

    def test_should_simply_skip_mods_without_keys_when_linking_keys(self, reset_folder_structure):
        """Our test server instance should simply skip mods without keys when linking keys."""
        copied_mods = join(self.instance.get_server_instance_path(), "!Mods_copied")
        mkdir(join(self.instance.get_server_instance_path(), "!Mods_linked"))
        keys_folder = join(self.instance.get_server_instance_path(), "Keys")
        mkdir(copied_mods)
        mkdir(keys_folder)
        mkdir(join(copied_mods, "test_mod"))
        self.instance.S.mods_to_be_copied = ["test_mod"]
        self.instance.S.user_mods_list = ["test_mod"]
        self.instance.S.server_mods_list = []
        self.instance._link_keys()
        assert len(listdir(keys_folder)) == 0


class TestServerInstanceInit(ODKSMTest):
    """Test: ServerInstance init..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub):
        """TestServerInstanceInit setup"""
        server_name = "TestServer1"
        request.cls.test_path = test_folder_structure_path()
        sb = ServerBatSettings(server_title="ODK Training Server", server_port="2202",
                               server_config="serverTraining.cfg", server_cfg="Arma3Training.cfg",
                               server_max_mem="8192", server_flags="-filePatching -autoinit -enableHT")
        sc = c_sc_stub
        request.cls.settings = ServerInstanceSettings(
            server_instance_name=server_name,
            bat_settings=sb,
            config_settings=sc,
            arma_folder=self.test_path,
            server_instance_root=self.test_path,
            mods_to_be_copied=["CBA_A3"],
            user_mods_list=["ace", "CBA_A3", "ODKAI"],
            server_mods_list=["AdvProp", "ODKMIN"],
        )
        request.cls.instance = ServerInstance(self.settings)
        request.cls.instance_folder = self.instance.get_server_instance_path()
        # set up all needed spies
        with spy(self.instance._new_server_folder) as request.cls.new_server_fun, \
                spy(self.instance._prepare_server_core) as request.cls.prepare_server_fun, \
                spy(self.instance._init_mods) as request.cls.init_mods_fun, \
                spy(self.instance._link_keys) as request.cls.init_keys_fun, \
                spy(self.instance._compile_bat_file) as request.cls.compiled_bat_fun:
            self.instance.init()

    def test_should_create_the_folder_if_needed(self):
        """Server instance init should create the folder if needed."""
        self.new_server_fun.assert_called()
        assert isdir(self.instance_folder)

    def test_should_symlink_all_needed_arma_files(self):
        """Server instance init should symlink all needed arma files."""
        self.prepare_server_fun.assert_called()
        assert isdir(join(self.instance_folder, "Keys"))

    def test_should_copy_and_symlink_all_mods(self):
        """Server instance init should copy and symlink all mods."""
        from unittest.mock import call
        ca = call(self.instance.S.user_mods_list)
        cb = call(self.instance.S.server_mods_list)
        self.init_mods_fun.assert_has_calls([ca, cb])
        assert isdir(join(self.instance_folder, self.instance.S.copied_mod_folder_name, "@CBA_A3"))
        assert islink(join(self.instance_folder, self.instance.S.linked_mod_folder_name, "@ace"))

    def test_should_symlink_all_mods_keys(self):
        """Server instance init should symlink all mods keys."""
        self.init_keys_fun.assert_called()
        keys_folder = join(self.instance.get_server_instance_path(), self.instance.keys_folder_name)
        keys_folder_files = listdir(keys_folder)
        assert len(keys_folder_files) == len(self.instance.S.user_mods_list) + len(
            self.instance.S.server_mods_list) + len(self.instance.arma_keys)

    def test_should_generate_the_bat_file(self):
        """Server instance init should generate the bat file."""
        self.compiled_bat_fun.assert_called()
        assert isfile(join(self.instance_folder, "run_server.bat"))


class TestAnInstanceWithANonExistingMod(ODKSMTest):
    """Test: An instance with a non existing mod..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub, c_sb_stub):
        """TestAnInstanceWithANonExistingMod setup"""
        server_name = "TestServer1"
        request.cls.test_path = test_folder_structure_path()
        request.cls.settings = ServerInstanceSettings(
            server_name,
            c_sb_stub, c_sc_stub,
            user_mods_list=["NOT_THERE"],
            arma_folder=self.test_path,
            server_instance_root=self.test_path,
        )
        request.cls.instance = ServerInstance(self.settings)

    def test_should_raise_an_error(self, reset_folder_structure):
        """An instance with a non existing mod should raise an error."""
        from odk_servermanager.instance import ModNotFound
        with pytest.raises(ModNotFound):
            self.instance._check_mods_folders()

    def test_should_check_for_it_and_stop_before_changing_anything(self, reset_folder_structure):
        """An instance with a non existing mod should check for it and stop before changing anything."""
        from odk_servermanager.instance import ModNotFound
        with pytest.raises(ModNotFound), spy(self.instance._check_mods_folders) as check_fun:
            self.instance.init()
        check_fun.assert_called()
        assert not isdir(self.instance.get_server_instance_path())
