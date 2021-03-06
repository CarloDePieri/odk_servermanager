from os.path import isdir, isfile, islink, join, splitdrive
from os import listdir, mkdir
from unittest.mock import call

import pytest

from conftest import test_folder_structure_path, spy, touch, test_resources
from odksm_test import ODKSMTest
from odk_servermanager.instance import ServerInstance
from odk_servermanager.settings import ServerInstanceSettings, ServerBatSettings, ServerConfigSettings


class TestAServerInstance:
    """Test: A server Instance..."""

    def test_should_save_its_config(self, sc_stub, sb_stub):
        """A server instance should save its config."""
        settings = ServerInstanceSettings("server0", sb_stub, sc_stub)
        instance = ServerInstance(settings)
        assert instance.S == settings


class TestWhenConfigComposingTheServerInstance(ODKSMTest):
    """Test: when config composing the server instance..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sb_stub):
        """TestWhenConfigComposingTheServerInstance setup"""
        request.cls.test_path = test_folder_structure_path()
        server_instance_name = "TestServer0"
        sc = ServerConfigSettings(
            hostname="TRAINING SERVER",
            password="123",
            password_admin="abc",
            mission_template="mission.name"
        )
        request.cls.settings = ServerInstanceSettings(
            server_instance_name=server_instance_name,
            bat_settings=c_sb_stub,
            config_settings=sc,
            arma_folder=self.test_path,
            server_instance_root=self.test_path,
            mods_to_be_copied=["CBA_A3"],
            user_mods_list=["ace", "CBA_A3", "ODKAI"],
            server_mods_list=["AdvProp", "ODKMIN"],
        )
        request.cls.instance = ServerInstance(self.settings)
        self.instance._compile_config_file()
        request.cls.compiled_config = join(self.instance.get_server_instance_path(),
                                           self.instance.S.bat_settings.server_config_file_name)

    def test_should_create_the_file(self):
        """When config composing the server instance should create the file."""
        assert isfile(self.compiled_config)

    def test_it_should_correctly_fill_in_settings(self):
        """When config composing the server instance it should correctly fill in settings."""
        from conftest import test_resources
        test_config = join(test_resources, "server.cfg")
        with open(test_config, "r") as test, open(self.compiled_config, "r") as compiled:
            assert test.read() == compiled.read()

    def test_should_be_able_to_take_a_custom_template(self):
        """When config composing the server instance should be able to take a custom template."""
        self.instance.S.config_settings.config_template = join(test_resources, "simple_template_config.txt")
        self.instance._compile_config_file()
        with open(self.compiled_config, "r") as compiled:
            assert compiled.read() == "TRAINING SERVER\n123\nabc\nmission.name"


class TestWhenBatComposingTheServerInstance(ODKSMTest):
    """Test: when bat composing bat the server instance..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub):
        """TestCompileBat setup"""
        request.cls.test_path = test_folder_structure_path()
        server_instance_name = "training"
        sb = ServerBatSettings(server_title="ODK Training Server", server_port="2202",
                               server_config_file_name="serverTraining.cfg", server_cfg_file_name="Arma3Training.cfg",
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
        self.instance._new_server_folder()
        self.instance._compile_bat_file()
        request.cls.compiled_bat = join(self.instance.get_server_instance_path(), "run_server.bat")

    def test_should_create_the_bat_file(self):
        """When bat composing the server instance should create the bat file."""
        assert isfile(self.compiled_bat)

    def test_should_correctly_fill_in_settings(self):
        """When bat composing the server instance should correctly fill in settings."""
        from conftest import test_resources
        test_bat = join(test_resources, "run_server.bat")
        with open(test_bat, "r") as test, open(self.compiled_bat, "r") as compiled:
            compiled_file = compiled.read()
            test_file = test.read()
            # fix generic path in the test file
            instance_path = self.instance.get_server_instance_path()
            test_file = test_file.replace(r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3",
                                          instance_path)
            test_file = test_file.replace("C:", splitdrive(self.compiled_bat)[0])
            assert test_file == compiled_file

    def test_should_be_able_to_take_a_custom_template_file(self):
        """When bat composing the server instance should be able to take a custom template file."""
        self.instance.S.bat_settings.bat_template = join(test_resources, "simple_template_bat.txt")
        self.instance._compile_bat_file()
        with open(self.compiled_bat, "r") as compiled:
            assert compiled.read() == "ODK Training Server\n2202\nserverTraining.cfg\nArma3Training.cfg\n8192"


class TestOurTestServerInstance(ODKSMTest):
    """Test: our test server instance..."""

    @pytest.fixture(autouse=True)
    def setup(self, request, sc_stub, sb_stub):
        """TestOurTestServerInstance setup"""
        server_name = "TestServer0"
        mods_to_be_copied = ["CBA_A3"]
        request.cls.test_path = test_folder_structure_path()
        request.cls.sb = sb_stub
        request.cls.sc = sc_stub
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

    def test_should_symlink_and_create_all_needed_stuff_from_the_main_folder(self, reset_folder_structure, mocker):
        """Create instance should symlink and create all needed stuff from the main folder."""
        mocker.patch.object(self.instance, "arma_keys", self.instance.arma_keys + ["not-there.bikey"])
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        mkdir(join(self.test_path, "__odksm__"))
        self.instance._prepare_server_core()
        # Check that it didn't copy over the wrong stuff
        assert not isdir(join(server_folder, "!Workshop"))
        assert not isdir(join(server_folder, "__server__TestServer0"))
        assert not islink(join(server_folder, "__odksm__"))
        assert not islink(join(server_folder, "userconfig"))
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
        assert islink(join(keys_folder, "a3.bikey"))
        assert islink(join(keys_folder, "a3c.bikey"))
        assert islink(join(keys_folder, "gm.bikey"))
        assert not islink(join(keys_folder, "not-there.bikey"))
        # Check userconfig dir
        assert isdir(join(server_folder, "userconfig"))

    def test_should_protect_run_server_bat(self, reset_folder_structure):
        """Our test server instance should protect run_server.bat."""
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        with open(join(self.test_path, "run_server.bat"), "w+") as f:
            f.write("protected")
        self.instance._prepare_server_core()
        assert not islink(join(server_folder, "run_server.bat"))

    def test_should_protect_server_config_file_name(self, reset_folder_structure):
        """Our test server instance should protect server_config_file_name."""
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        name = self.instance.S.bat_settings.server_config_file_name
        with open(join(self.test_path, name), "w+") as f:
            f.write("protected")
        self.instance._prepare_server_core()
        assert not islink(join(server_folder, name))

    def test_should_init_copied_and_linked_mods(self, reset_folder_structure):
        """Create instance should init copied and linked mods."""
        user_mods_list = ["ace", "CBA_A3", "ODKAI"]
        server_folder = join(self.test_path, "__server__" + self.instance.S.server_instance_name)
        # ensure the mod folders are there
        mkdir(join(server_folder, "!Mods_copied"))
        mkdir(join(server_folder, "!Mods_linked"))
        self.instance._start_op_on_mods("init", user_mods_list)
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
        self.instance._start_op_on_mods("init", user_mods_list)
        self.instance._start_op_on_mods("init", server_mods_list)
        keys_folder = join(self.instance.get_server_instance_path(), self.instance.keys_folder_name)
        # end setup, begin actual test
        self.instance._link_keys()
        keys_folder_files = listdir(keys_folder)
        # now check the copied keys - beware, no server mods keys!
        assert len(keys_folder_files) == len(self.instance.S.user_mods_list) + len(self.instance.arma_keys)

    def test_should_skip_a_key_already_present_when_linking_them(self, reset_folder_structure):
        """Our test server instance should skip a key already present when linking them."""
        # THIS TEST DEPENDS ON _prepare_server_core AND _init_mods ... would be too long to set up otherwise
        user_mods_list = ["3CB BAF Equipment", "3CB BAF Equipment (comp)"]
        self.instance.S.user_mods_list = user_mods_list
        self.instance._prepare_server_core()
        self.instance._start_op_on_mods("init", user_mods_list)
        # end setup, begin actual test
        # this will fail if not handled correctly
        self.instance._link_keys()

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

    def test_should_be_able_to_link_a_mod(self, reset_folder_structure):
        """Our test server instance should be able to link a mod."""
        self.instance.S.user_mods_list = ["ace"]
        linked_mods = join(self.instance.get_server_instance_path(), self.instance.S.linked_mod_folder_name)
        mkdir(linked_mods)
        self.instance._symlink_mod("ace")
        assert islink(join(linked_mods, "@ace"))

    def test_should_skip_a_mod_if_already_there(self, reset_folder_structure):
        """Our test server instance should skip a mod if already there."""
        user_mods_list = ["3CB BAF Equipment", "3CB BAF Equipment", "ace", "ace"]
        self.instance.S.user_mods_list = user_mods_list
        self.instance.S.mods_to_be_copied = ["ace"]
        self.instance._prepare_server_core()
        warnings = len(self.instance.warnings)
        self.instance._start_op_on_mods("init", user_mods_list)
        self.instance._check_mods_duplicate()
        assert len(self.instance.warnings) == warnings + 2

    def test_should_be_able_to_link_the_warning_folder(self, reset_folder_structure):
        """Our test server instance should be able to link the warning folder."""
        linked_mods = join(self.instance.get_server_instance_path(), self.instance.S.linked_mod_folder_name)
        mkdir(linked_mods)
        warning_folder_name = "!DO_NOT_CHANGE_FILES_IN_THESE_FOLDERS"
        self.instance._symlink_warning_folder()
        assert islink(join(linked_mods, warning_folder_name))
        self.instance._symlink_warning_folder()  # be sure it manages an already existing symlink
        assert islink(join(linked_mods, warning_folder_name))

    def test_should_be_able_to_copy_a_mod(self, reset_folder_structure):
        """Our test server instance should be able to copy a mod."""
        copied_mods = join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name)
        mkdir(copied_mods)
        self.instance._copy_mod("ace")
        assert isdir(join(copied_mods, "@ace"))

    def test_should_be_able_to_clean_linked_mods(self, reset_folder_structure, mocker):
        """Our test server instance should be able to clean linked mods."""
        linked_mods = join(self.instance.get_server_instance_path(), self.instance.S.linked_mod_folder_name)
        mkdir(linked_mods)
        mocker.patch.dict(self.instance.S, {"mods_to_be_copied": []})
        mocker.patch.dict(self.instance.S, {"user_mods_list": ["ace", "CBA_A3", "ODKAI"]})
        self.instance._start_op_on_mods("init", ["ace", "CBA_A3", "ODKAI"])
        assert islink(join(linked_mods, "@ace"))
        assert islink(join(linked_mods, "@CBA_A3"))
        assert islink(join(linked_mods, "@ODKAI"))
        mocker.patch.dict(self.instance.S, {"mods_to_be_copied": ["CBA_A3"]})
        mocker.patch.dict(self.instance.S, {"user_mods_list": ["CBA_A3", "ODKAI"]})
        self.instance._clear_old_linked_mods()
        assert not islink(join(linked_mods, "@ace"))
        assert not islink(join(linked_mods, "@CBA_A3"))
        assert islink(join(linked_mods, "@ODKAI"))

    def test_should_be_able_to_clean_a_copied_mod_folder(self, reset_folder_structure):
        """Our test server instance should be able to clean a copied mod folder."""
        copied_mods = join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name)
        mkdir(copied_mods)
        self.instance._copy_mod("CBA_A3")
        assert isdir(join(copied_mods, "@CBA_A3"))
        self.instance._clear_copied_mod("CBA_A3")
        assert not isdir(join(copied_mods, "@CBA_A3"))

    def test_should_be_able_to_clean_old_and_useless_copied_mod_folder(self, reset_folder_structure):
        """Our test server instance should be able to clean old and useless copied mod folder."""
        copied_mods = join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name)
        mkdir(copied_mods)
        self.instance.S.mods_to_be_copied = ["ace"]
        self.instance._copy_mod("CBA_A3")
        self.instance._copy_mod("ace")
        assert isdir(join(copied_mods, "@CBA_A3"))
        assert isdir(join(copied_mods, "@ace"))
        self.instance._clear_old_copied_mods()
        assert not isdir(join(copied_mods, "@CBA_A3"))
        assert isdir(join(copied_mods, "@ace"))

    def test_should_be_able_to_update_its_mods(self, reset_folder_structure):
        """Our test server instance should be able to update its mods."""
        copied_mods_folder = join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name)
        linked_mods_folder = join(self.instance.get_server_instance_path(), self.instance.S.linked_mod_folder_name)
        mkdir(linked_mods_folder)
        mkdir(copied_mods_folder)
        self.instance.S.user_mods_list = ["ace", "AdvProp", "ODKAI"]
        self.instance.S.mods_to_be_copied = ["ace", "AdvProp"]
        self.instance._start_op_on_mods("init", self.instance.S.user_mods_list)
        touch(join(copied_mods_folder, "@ace", "config"))
        self.instance.S.user_mods_list = ["ace", "ODKAI", "ODKMIN"]
        self.instance.S.mods_to_be_copied = ["ace", "ODKAI"]
        # end setup
        self.instance._update_all_mods()
        assert isdir(join(copied_mods_folder, "@ace"))  # was present, is still present, so the folder gets copied over
        assert not isfile(join(copied_mods_folder, "@ace", "config"))  # old customizations get overwritten
        assert not isdir(join(copied_mods_folder, "@AdvProp"))  # no more needed folder gets discarded
        assert isdir(join(copied_mods_folder, "@ODKAI"))  # newly added mod folder gets added
        assert not islink(join(linked_mods_folder, "@ODKAI"))  # no more linked
        assert islink(join(linked_mods_folder, "@ODKMIN"))

    def test_should_be_able_to_clean_the_keys_folder(self, reset_folder_structure):
        """Our test server instance should be able to clean the keys folder."""
        self.instance._prepare_server_core()
        self.instance.S.user_mods_list = ["ace", "AdvProp", "ODKAI"]
        self.instance._start_op_on_mods("init", self.instance.S.user_mods_list)
        self.instance._link_keys()
        keys_dir = join(self.instance.get_server_instance_path(), self.instance.keys_folder_name)
        touch(join(keys_dir, "manual_key.bikey"))
        self.instance._clear_keys()
        keys = listdir(keys_dir)
        assert keys == self.instance.arma_keys

    def test_should_be_able_to_update_keys(self, reset_folder_structure):
        """Our test server instance should be able to update keys."""
        self.instance._prepare_server_core()
        self.instance.S.user_mods_list = ["ace", "AdvProp", "ODKAI"]
        self.instance._start_op_on_mods("init", self.instance.S.user_mods_list)
        self.instance._link_keys()
        self.instance.S.user_mods_list = ["ODKAI"]
        self.instance._update_all_mods()
        with spy(self.instance._clear_keys) as clear_keys_fun, spy(self.instance._link_keys) as link_keys_fun:
            self.instance._update_keys()
        clear_keys_fun.assert_called()
        link_keys_fun.assert_called()
        keys = listdir(join(self.instance.get_server_instance_path(), self.instance.keys_folder_name))
        assert len(keys) == len(self.instance.arma_keys) + 1

    def test_should_be_able_to_clear_the_compiled_files(self, reset_folder_structure):
        """Our test server instance should be able to clear the compiled files."""
        self.instance._prepare_server_core()
        self.instance._compile_bat_file()
        self.instance._compile_config_file()
        self.instance._clear_compiled_files()
        assert not isfile(join(self.instance.get_server_instance_path(), "run_server.bat"))
        assert not isfile(join(self.instance.get_server_instance_path(), self.instance.S.bat_settings.server_config_file_name))

    def test_should_be_able_to_update_compiled_files(self, reset_folder_structure):
        """Our test server instance should be able to update compiled files."""
        self.instance._prepare_server_core()
        self.instance._compile_bat_file()
        self.instance._compile_config_file()
        with spy(self.instance._clear_compiled_files) as clear_files_fun, \
                spy(self.instance._compile_bat_file) as compile_bat_fun, \
                spy(self.instance._compile_config_file) as compile_config_fun:
            self.instance._update_compiled_files()
        clear_files_fun.assert_called()
        compile_bat_fun.assert_called()
        compile_config_fun.assert_called()

    def test_should_be_able_to_update(self, reset_folder_structure):
        """Our test server instance should be able to update."""
        self.instance._prepare_server_core()
        self.instance._compile_bat_file()
        self.instance._compile_config_file()
        i = self.instance
        with spy(i._check_mods) as check_mods_fun, \
                spy(i._update_all_mods) as update_mods_fun, \
                spy(i._update_keys) as update_keys_fun, \
                spy(i._update_compiled_files) as update_files_fun:
            i.update()
        check_mods_fun.assert_called()
        update_mods_fun.assert_called()
        update_keys_fun.assert_called()
        update_files_fun.assert_called()

    def test_should_be_able_to_do_simple_op_instead_of_calling_hooks(self, reset_folder_structure, mocker):
        """Our test server instance should be able to do simple op instead of calling hooks."""
        self.instance._prepare_server_core()
        mocker.patch.object(self.instance, "registered_fix", return_value=[])
        with spy(self.instance._copy_mod) as copy_mod_function:
            self.instance._apply_hooks_and_do_op("init", "copy", "CBA_A3")
        copy_mod_function.assert_called()
        with spy(self.instance._symlink_mod) as symlink_mod_function:
            self.instance._apply_hooks_and_do_op("init", "link", "ace")
        symlink_mod_function.assert_called()

    def test_should_call_hooks_at_init_mods_time(self, reset_folder_structure):
        """Our test server instance should call hooks at init mods time."""
        self.instance._prepare_server_core()
        with spy(self.instance._apply_hooks_and_do_op) as apply_hooks_function:
            self.instance._start_op_on_mods("init", ["ace", "CBA_A3"])
        apply_hooks_function.assert_has_calls([call("init", "link", "ace"), call("init", "copy", "CBA_A3")])

    def test_should_have_a_working_do_default_op(self, reset_folder_structure, mocker):
        """Our test server instance should have a working do_default_op."""
        copy_fun = mocker.patch("odk_servermanager.instance.ServerInstance._copy_mod", side_effect=lambda x: None)
        symlink_fun = mocker.patch("odk_servermanager.instance.ServerInstance._symlink_mod", side_effect=lambda x: None)
        clear_mod_fun = mocker.patch("odk_servermanager.instance.ServerInstance._clear_copied_mod", side_effect=lambda x: None)
        self.instance._do_default_op("init", "copy", "ace")
        copy_fun.assert_called_once()
        self.instance._do_default_op("init", "link", "ace")
        symlink_fun.assert_called_once()
        copy_fun.reset_mock()
        copied_mod_folder = join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name)
        mkdir(copied_mod_folder)
        self.instance._do_default_op("update", "copy", "ace")
        copy_fun.assert_called_once()
        clear_mod_fun.assert_not_called()
        copy_fun.reset_mock()
        mkdir(join(copied_mod_folder, "@ace"))
        self.instance._do_default_op("update", "copy", "ace")
        clear_mod_fun.assert_called_once()
        copy_fun.assert_called_once()

    def test_should_be_able_to_skip_keys_when_linking_them(self, reset_folder_structure, mocker):
        """Our test server instance should be able to skip keys when linking them."""
        self.instance._prepare_server_core()
        mocker.patch.object(self.instance.S, "mods_to_be_copied", [])
        mocker.patch.object(self.instance.S, "user_mods_list", ["ace"])
        mocker.patch.object(self.instance.S, "skip_keys", ["ace"])
        self.instance._symlink_mod("ace")
        self.instance._link_keys()
        keys_folder = join(self.instance.get_server_instance_path(), self.instance.keys_folder_name)
        keys_folder_files = listdir(keys_folder)
        assert len(keys_folder_files) == len(self.instance.arma_keys)

    def test_should_manage_empty_keys_folder_inside_a_mod_folder(self, reset_folder_structure, mocker):
        """Our test server instance should manage empty keys folder inside a mod folder."""
        mod_root_folder = join(self.test_path, "testMods")
        mkdir(mod_root_folder)
        mkdir(join(mod_root_folder, "ModA"))
        mkdir(join(mod_root_folder, "ModA", "Keys"))
        mocker.patch.object(self.instance, "_should_link_mod_key", lambda x: True)
        self.instance._link_keys_in_folder(mod_root_folder)  # this should not raise exception, but simply skip

    def test_should_manage_multiple_keys_per_mod(self, reset_folder_structure, mocker):
        """Our test server instance should manage multiple keys per mod."""
        mod_root_folder = join(self.test_path, "testMods")
        mkdir(mod_root_folder)
        mkdir(join(mod_root_folder, "ModA"))
        mkdir(join(mod_root_folder, "ModA", "Keys"))
        touch(join(mod_root_folder, "ModA", "Keys", "keya.bikey"))
        touch(join(mod_root_folder, "ModA", "Keys", "keyb.bikey"))
        mocker.patch.object(self.instance, "_should_link_mod_key", lambda x: True)
        instance_key_folder = join(self.instance.get_server_instance_path(), "Keys")
        mkdir(instance_key_folder)
        self.instance._link_keys_in_folder(mod_root_folder)
        assert islink(join(instance_key_folder, "keya.bikey"))
        assert islink(join(instance_key_folder, "keyb.bikey"))


class TestServerInstanceInit(ODKSMTest):
    """Test: ServerInstance init..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub):
        """TestServerInstanceInit setup"""
        server_name = "TestServer1"
        request.cls.test_path = test_folder_structure_path()
        sb = ServerBatSettings(server_title="ODK Training Server", server_port="2202",
                               server_config_file_name="serverTraining.cfg", server_cfg_file_name="Arma3Training.cfg",
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
                spy(self.instance._check_mods) as request.cls.check_mods_fun, \
                spy(self.instance._prepare_server_core) as request.cls.prepare_server_fun, \
                spy(self.instance._start_op_on_mods) as request.cls.init_mods_fun, \
                spy(self.instance._link_keys) as request.cls.init_keys_fun, \
                spy(self.instance._compile_bat_file) as request.cls.compiled_bat_fun, \
                spy(self.instance._compile_config_file) as request.cls.compiled_config_fun:
            self.instance.init()

    def test_should_check_the_mods(self):
        """Server instance init should check the mods."""
        self.check_mods_fun.assert_called()

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
        ca = call("init", self.instance.S.user_mods_list)
        cb = call("init", self.instance.S.server_mods_list)
        self.init_mods_fun.assert_has_calls([ca, cb])
        assert isdir(join(self.instance_folder, self.instance.S.copied_mod_folder_name, "@CBA_A3"))
        assert islink(join(self.instance_folder, self.instance.S.linked_mod_folder_name, "@ace"))

    def test_should_symlink_all_user_mods_keys(self):
        """Server instance init should symlink all user mods keys."""
        self.init_keys_fun.assert_called()
        keys_folder = join(self.instance.get_server_instance_path(), self.instance.keys_folder_name)
        keys_folder_files = listdir(keys_folder)
        assert len(keys_folder_files) == len(self.instance.S.user_mods_list) + len(self.instance.arma_keys)

    def test_should_generate_the_bat_file(self):
        """Server instance init should generate the bat file."""
        self.compiled_bat_fun.assert_called()
        assert isfile(join(self.instance_folder, "run_server.bat"))

    def test_should_generate_the_config_file(self):
        """Server instance init should generate the config file."""
        self.compiled_config_fun.assert_called()
        assert isfile(join(self.instance_folder, self.instance.S.bat_settings.server_config_file_name))


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
