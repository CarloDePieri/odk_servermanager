from os.path import join, isfile, isdir, abspath
from typing import Dict

import pytest

from conftest import test_preset_file_name, test_resources, test_folder_structure_path
from odk_servermanager.config_ini import ConfigIni
from odk_servermanager.manager import ServerManager
from odk_servermanager.settings import ServerInstanceSettings, ServerBatSettings, ServerConfigSettings, ModFixSettings
from odk_servermanager.modfix import MisconfiguredModFix, NonExistingFixFile, ModFix
from odksm_test import ODKSMTest
from odk_servermanager.utils import rmtree


class TestPresetImporting(ODKSMTest):
    """The preset mechanism should..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPresetImporting setup"""
        request.cls.manager = ServerManager("")

    def test_should_parse_all_mods(self):
        """The preset mechanism should parse all mod in the preset"""
        mods = self.manager._parse_mods_preset(test_preset_file_name)
        assert len(mods) == 4

    def test_should_return_a_list_of_mod_names(self):
        """The preset mechanism should return a list of mod names"""
        mods_name = self.manager._parse_mods_preset(test_preset_file_name)
        assert isinstance(mods_name, list)
        assert isinstance(mods_name[0], str)
        assert "ODKAI" in mods_name
        assert "ACE Compat - RHS- GREF"  # this checks for a filter fix on the name

    def test_should_ignore_the_preset_without_proper_setting(self, mocker, sc_stub, sb_stub):
        """Preset importing should ignore the preset without proper setting."""
        manager = ServerManager("")
        mocker.patch("odk_servermanager.manager.ServerManager._parse_config", side_effect=None)
        parse_preset_fun = mocker.patch("odk_servermanager.manager.ServerManager._parse_mods_preset", side_effect=None)
        manager.settings = ServerInstanceSettings("test", bat_settings=sb_stub, config_settings=sc_stub)
        manager._recover_settings()
        parse_preset_fun.assert_not_called()


class TestThePresetManager:
    """Test: The preset manager..."""

    def test_should_be_able_to_read_a_config_file(self):
        """The preset manager should be able to read a config file."""
        sm = ServerManager()
        sm.config_file = join(test_resources, "config.ini")
        sm._parse_config()
        assert isinstance(sm.settings, ServerInstanceSettings)
        assert isinstance(sm.settings.bat_settings, ServerBatSettings)
        assert isinstance(sm.settings.config_settings, ServerConfigSettings)
        assert isinstance(sm.settings.fix_settings, ModFixSettings)
        assert sm.settings.server_instance_name == "training"
        assert sm.settings.mods_to_be_copied == ["ace"]
        assert sm.settings.bat_settings.server_title == "TEST SERVER"
        assert sm.settings.config_settings.password == "p4ssw0rd"
        assert sm.settings.fix_settings.mod_fix_settings["cba_settings"] == "tests/resources/server.cfg"
        assert sm.settings.fix_settings.enabled_fixes == ["cba_a3"]
        assert len(sm.settings.skip_keys) == 1  # this check that empty list field in config don't pollute the list

    def test_should_handle_a_missing_enabled_fixes_in_the_mod_fix_settings_section(self, mocker):
        """The preset manager should handle a missing enabled_fixes in the mod_fix_settings section."""
        sm = ServerManager()
        sm.config_file = join(test_resources, "config.ini")
        # simulate a missing enabled_fixes
        original_read_file = ConfigIni.read_file  # cache the original method before patching it

        def fake_read(config_file: str) -> Dict:
            data = original_read_file(config_file)
            data["mod_fix_settings"].pop("enabled_fixes")
            return data
        mocker.patch("odk_servermanager.manager.ConfigIni.read_file",
                     side_effect=fake_read)
        sm._parse_config()

    def test_should_read_the_config_and_parse_the_preset_if_present_at_init(self):
        """The preset manager should read the config and parse the preset if present at init."""
        sm = ServerManager()
        sm.config_file = join(test_resources, "config.ini")
        sm._recover_settings()
        assert isinstance(sm.settings, ServerInstanceSettings)
        assert len(sm.settings.user_mods_list) == 6

    def test_should_correctly_modify_mods_to_be_copied_from_the_registered_fix(self, mocker):
        """The preset manager should correctly modify mods_to_be_copied from the registered_fix."""
        linked = self._prepare_mod_fix_with_dummy_hook("ODKMIN", "hook_init_link_replace")
        not_there = self._prepare_mod_fix_with_dummy_hook("NotThere", "hook_init_copied_replace")
        copied = self._prepare_mod_fix_with_dummy_hook("CBA_A3", "hook_init_copy_replace")
        mocker.patch("odk_servermanager.modfix.register_fixes", side_effect=lambda x: [linked, not_there, copied])
        sm = ServerManager()
        sm.config_file = join(test_resources, "config.ini")
        sm._parse_config()
        assert "NotThere" not in sm.settings.mods_to_be_copied
        assert "ODKMIN" not in sm.settings.mods_to_be_copied
        assert "CBA_A3" in sm.settings.mods_to_be_copied

    @staticmethod
    def _prepare_mod_fix_with_dummy_hook(name: str, hook_name: str) -> ModFix:
        class ModFixTest(ModFix):
            """"""
        mf = ModFixTest()
        mf.name = name
        setattr(mf, hook_name, lambda x: None)
        return mf


class TestAServerManagerAtInit(ODKSMTest):
    """Test: A Server Manager at Init..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestAServerManagerAtInit setup"""
        request.cls.config_file = join(test_resources, "config.ini")
        request.cls.sm = ServerManager()

    def test_should_init_the_server_instance(self, reset_folder_structure, mocker):
        """A server manager at init should init the server instance."""
        answer = mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self.sm.manage_instance(self.config_file)
        answer.assert_called()
        assert isfile(join(self.sm.instance.get_server_instance_path(),
                           self.sm.settings.bat_settings.server_config_file_name))

    def test_should_quit_if_not_confirmed_at_init(self, reset_folder_structure, mocker):
        """A server manager at init should quit if not confirmed at init."""
        answer = mocker.patch("builtins.input", return_value="n")  # this fails the user input check
        abort = mocker.patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort)
        with pytest.raises(SystemExit):
            self.sm.manage_instance(self.config_file)
        answer.assert_called()
        abort.assert_called()

    def test_should_ask_confirmation_before_update_if_called_twice(self, reset_folder_structure, mocker):
        """A server manager at init should ask confirmation before update if called twice."""
        # setup
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self.sm.manage_instance(self.config_file)
        # end setup
        answer = mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        update = mocker.patch("odk_servermanager.instance.ServerInstance.update", side_effect=self.sm.instance.update)
        self.sm.manage_instance(self.config_file)
        answer.assert_called()
        update.assert_called()

    def test_should_stop_when_updating_if_its_told_to_do_so(self, reset_folder_structure, mocker):
        """A server manager at init should stop when updating if its told to do so."""
        # setup
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self.sm.manage_instance(self.config_file)
        # end setup
        answer = mocker.patch("builtins.input", return_value="n")
        update = mocker.patch("odk_servermanager.instance.ServerInstance.update", side_effect=self.sm.instance.update)
        abort = mocker.patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort)
        with pytest.raises(SystemExit):
            self.sm.manage_instance(self.config_file)
        answer.assert_called()
        update.assert_not_called()
        abort.assert_called()

    def test_should_stop_with_non_existing_mod(self, reset_folder_structure, mocker):
        """A server manager at init should stop with non existing mod."""
        rmtree(join(test_folder_structure_path(), "!Workshop", "@CBA_A3"))
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self._assert_aborting(self.sm.manage_instance, {"config_file": self.config_file})

    def test_should_check_the_config_file(self, reset_folder_structure):
        """A server manager at init should check the config file."""
        sm = ServerManager(join(test_folder_structure_path(), "template.txt"))
        self._assert_aborting(sm.manage_instance, {"config_file": self.config_file})

    def test_should_catch_exception_regarding_mod_fixes(self, reset_folder_structure, mocker):
        """A server manager at init should catch exception regarding mod fixes."""
        def broken_fixes(error):
            raise error("something went wrong")
        mocker.patch("odk_servermanager.modfix.register_fixes", side_effect=lambda x: broken_fixes(MisconfiguredModFix))
        self._assert_aborting(self.sm.manage_instance, {"config_file": self.config_file})
        mocker.patch("odk_servermanager.modfix.register_fixes", side_effect=lambda x: broken_fixes(NonExistingFixFile))
        self._assert_aborting(self.sm.manage_instance, {"config_file": self.config_file})

    def test_should_manage_errors_while_parsing_configurations(self, reset_folder_structure, mocker):
        """A server manager at init should manage errors while parsing configurations."""
        def broken_configs():
            raise Exception
        mocker.patch("odk_servermanager.manager.ServerManager._recover_settings",
                     side_effect=lambda x: broken_configs())
        self._assert_aborting(self.sm.manage_instance, {"config_file": self.config_file})

    def test_should_manage_errors_while_executing_mod_fixes(self, reset_folder_structure, mocker):
        """A server manager at init should manage errors while executing mod fixes."""
        def broken_hook():
            raise Exception
        mocker.patch("odk_servermanager.modfix.cba_a3.ModFixCBA.hook_init_copy_replace",
                     side_effect=broken_hook)
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self._assert_aborting(self.sm.manage_instance, {"config_file": self.config_file})

    def test_should_abort_with_more_general_errors(self, reset_folder_structure, mocker):
        """A server manager at init should abort with more general errors."""
        def broken_stuff():
            raise Exception
        mocker.patch("odk_servermanager.manager.ServerManager._ui_init", side_effect=broken_stuff)
        self._assert_aborting(self.sm.manage_instance, {"config_file": self.config_file})

    def _assert_aborting(self, function, args):
        """Helper to test that the given function is actually making the manager abort."""
        from unittest.mock import patch
        with patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort) as abort:
            with pytest.raises(SystemExit):
                function(**args)
            abort.assert_called()


class TestWhenBootstrapping(ODKSMTest):
    """Test: when bootstrapping..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestWhenBootstrapping setup"""
        request.cls.sm = ServerManager()
        request.cls.default_file = join(test_resources, "bootstrap.ini")
        request.cls.test_path = test_folder_structure_path()

    def test_it_should_abort_if_there_are_missing_fields_in_the_default_config_ini(self, mocker):
        """When bootstrapping it should abort if there are missing fields in the default config ini."""
        mocker.patch("odk_servermanager.manager.ConfigIni.read_file",
                     return_value={"bootstrap": {"odksm_folder_path": ""}})
        self._assert_aborting(self.sm.bootstrap, {"default_config_file": self.default_file})
        mocker.patch("odk_servermanager.manager.ConfigIni.read_file",
                     return_value={"bootstrap": {"instances_root": ""}})
        self._assert_aborting(self.sm.bootstrap, {"default_config_file": self.default_file})

    def test_it_should_create_the_folder(self, reset_folder_structure, mocker):
        """When bootstrapping it should create the folder."""
        mocker.patch("builtins.input", side_effect=["training", "n"])
        self.sm.bootstrap(self.default_file)
        assert isdir(join(self.test_path, "training"))

    def test_it_should_compile_the_config_ini_file(self, reset_folder_structure, mocker):
        """When bootstrapping it should compile the config.ini file."""
        mocker.patch("builtins.input", side_effect=["training", "n"])
        self.sm.bootstrap(self.default_file)
        instance_folder = join(self.test_path, "training")
        config_file = join(instance_folder, "config.ini")
        assert isfile(config_file)
        # now try and read back that file
        data = ConfigIni.read_file(config_file)
        assert data["bat"]["server_max_mem"] == "8192"
        assert data["ODKSM"]["server_instance_name"] == "training"
        assert data["ODKSM"]["server_instance_root"] == abspath(join("tests/resources/Arma", "training"))

    def test_should_compile_the_odksm_bat_file(self, reset_folder_structure, mocker):
        """When bootstrapping should compile the odksm.bat file."""
        mocker.patch("builtins.input", side_effect=["training", "n"])
        self.sm.bootstrap(self.default_file)
        instance_folder = join(self.test_path, "training")
        bat_file = join(instance_folder, "ODKSM.bat")
        assert isfile(bat_file)
        with open(bat_file, "r") as f:
            assert "path/to/odksm_folder" in f.read()

    def test_should_ask_and_eventually_provide_for_custom_templates(self, reset_folder_structure,
                                                                    mocker, have_same_content):
        """When bootstrapping should ask and eventually provide for custom templates."""
        mocker.patch("builtins.input", side_effect=["training", "y", "y", "y"])
        self.sm.bootstrap(self.default_file)
        instance_folder = join(self.test_path, "training")
        bat_template = join(instance_folder, "run_server_template.txt")
        config_template = join(instance_folder, "server_cfg_template.txt")
        assert isfile(bat_template)
        assert have_same_content(bat_template, self.sm._get_resource_file("templates/run_server_template.txt"))
        assert isfile(config_template)
        assert have_same_content(config_template, self.sm._get_resource_file("templates/server_cfg_template.txt"))
        config_file = join(instance_folder, "config.ini")
        data = ConfigIni.read_file(config_file)
        assert data["bat"]["bat_template"] == bat_template

    def _assert_aborting(self, function, args):
        """Helper to test that the given function is actually making the manager abort."""
        from unittest.mock import patch
        with patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort) as abort:
            with pytest.raises(SystemExit):
                function(**args)
            abort.assert_called()


class TestWhenDebugging:
    """Test: When debugging..."""

    @staticmethod
    def raise_err():
        raise Exception

    def test_should_print_the_stacktrace_to_a_file(self, reset_folder_structure, mocker):
        """When debugging should print the stacktrace to a file."""
        import time
        ts = time.gmtime()
        debug_file_folder = test_folder_structure_path()
        debug_file = join(debug_file_folder, "odksm_{}.log".format(time.strftime("%Y%m%d_%H%M%S", ts)))
        manager = ServerManager(debug_logs_path=debug_file_folder)
        # first check outside an exception
        manager._print_debug_log()
        assert not isfile(debug_file)
        # now check inside an exception
        try:
            raise Exception("custom_test_exception")
        except Exception:
            mocker.patch("time.gmtime", return_value=ts)
            manager._print_debug_log()
            assert isfile(debug_file)
            with open(debug_file, "r") as log:
                content = log.read()
                assert content.find("custom_test_exception") > 0

    def test_ui_abort_should_call_print_debug_log_if_needed(self, reset_folder_structure, mocker):
        """When debugging _ui_abort should call print_debug_log if needed."""
        print_logs_fun = mocker.patch("odk_servermanager.manager.ServerManager._print_debug_log")
        manager = ServerManager()
        debugger = ServerManager(debug_logs_path="somepath")
        with pytest.raises(SystemExit):
            manager._ui_abort()
        print_logs_fun.assert_not_called()
        with pytest.raises(SystemExit):
            debugger._ui_abort()
        print_logs_fun.assert_called()
