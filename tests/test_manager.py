from os.path import join, isfile

import pytest

from conftest import test_preset_file_name, test_resources, test_folder_structure_path
from odk_servermanager.manager import ServerManager
from odk_servermanager.settings import ServerInstanceSettings, ServerBatSettings, ServerConfigSettings, ModFixSettings
from odk_servermanager.modfix import MisconfiguredModFix, NonExistingFixFile
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


class TestThePresetManager:
    """Test: The preset manager..."""

    def test_should_be_able_to_read_a_config_file(self):
        """The preset manager should be able to read a config file."""
        sm = ServerManager(join(test_resources, "config.ini"))
        sm._parse_config()
        assert isinstance(sm.settings, ServerInstanceSettings)
        assert isinstance(sm.settings.bat_settings, ServerBatSettings)
        assert isinstance(sm.settings.config_settings, ServerConfigSettings)
        assert isinstance(sm.settings.fix_settings, ModFixSettings)
        assert sm.settings.server_instance_name == "training"
        assert sm.settings.mods_to_be_copied == ["ace", "CBA_A3"]
        assert sm.settings.bat_settings.server_title == "TEST SERVER"
        assert sm.settings.config_settings.password == "p4ssw0rd"
        assert sm.settings.fix_settings.mod_fix_settings["cba_settings"] == "tests/resources/server.cfg"
        assert sm.settings.fix_settings.enabled_fixes == ["cba_a3"]
        assert len(sm.settings.skip_keys) == 1  # this check that empty list field in config don't pollute the list

    def test_should_read_the_config_and_parse_the_preset_if_present_at_init(self):
        """The preset manager should read the config and parse the preset if present at init."""
        sm = ServerManager(join(test_resources, "config.ini"))
        sm._recover_settings()
        assert isinstance(sm.settings, ServerInstanceSettings)
        assert len(sm.settings.user_mods_list) == 5


class TestAServerManagerAtInit(ODKSMTest):
    """Test: A Server Manager at Init..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestAServerManagerAtInit setup"""
        request.cls.sm = ServerManager(join(test_resources, "config.ini"))

    def test_should_init_the_server_instance(self, reset_folder_structure, mocker):
        """A server manager at init should init the server instance."""
        answer = mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self.sm.manage_instance()
        answer.assert_called()
        assert isfile(join(self.sm.instance.get_server_instance_path(), self.sm.settings.bat_settings.server_config_file_name))

    def test_should_quit_if_not_confirmed_at_init(self, reset_folder_structure, mocker):
        """A server manager at init should quit if not confirmed at init."""
        answer = mocker.patch("builtins.input", return_value="n")  # this fails the user input check
        abort = mocker.patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort)
        with pytest.raises(SystemExit):
            self.sm.manage_instance()
        answer.assert_called()
        abort.assert_called()

    def test_should_ask_confirmation_before_update_if_called_twice(self, reset_folder_structure, mocker):
        """A server manager at init should ask confirmation before update if called twice."""
        # setup
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self.sm.manage_instance()
        # end setup
        answer = mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        update = mocker.patch("odk_servermanager.instance.ServerInstance.update", side_effect=self.sm.instance.update)
        self.sm.manage_instance()
        answer.assert_called()
        update.assert_called()

    def test_should_stop_when_updating_if_its_told_to_do_so(self, reset_folder_structure, mocker):
        """A server manager at init should stop when updating if its told to do so."""
        # setup
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self.sm.manage_instance()
        # end setup
        answer = mocker.patch("builtins.input", return_value="n")
        update = mocker.patch("odk_servermanager.instance.ServerInstance.update", side_effect=self.sm.instance.update)
        abort = mocker.patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort)
        with pytest.raises(SystemExit):
            self.sm.manage_instance()
        answer.assert_called()
        update.assert_not_called()
        abort.assert_called()

    def test_should_stop_with_non_existing_mod(self, reset_folder_structure, mocker):
        """A server manager at init should stop with non existing mod."""
        rmtree(join(test_folder_structure_path(), "!Workshop", "@CBA_A3"))
        mocker.patch("builtins.input", return_value="y")  # this skips the user input check
        self._assert_aborting(self.sm.manage_instance)

    def test_should_check_the_config_file(self, reset_folder_structure, mocker):
        """A server manager at init should check the config file."""
        sm = ServerManager(join(test_folder_structure_path(), "template.txt"))
        self._assert_aborting(sm.manage_instance)

    def test_should_catch_exception_regarding_mod_fixes(self, mocker):
        """A server manager at init should catch exception regarding mod fixes."""
        def broken_fixes(error):
            raise error("something went wrong")
        mocker.patch("odk_servermanager.modfix.register_fixes", side_effect=lambda x: broken_fixes(MisconfiguredModFix))
        self._assert_aborting(self.sm.manage_instance)
        mocker.patch("odk_servermanager.modfix.register_fixes", side_effect=lambda x: broken_fixes(NonExistingFixFile))
        self._assert_aborting(self.sm.manage_instance)

    def test_should_manage_errors_while_parsing_configurations(self, mocker):
        """A server manager at init should manage errors while parsing configurations."""
        def broken_configs():
            raise Exception
        mocker.patch("odk_servermanager.manager.ServerManager._recover_settings", side_effect=lambda x: broken_configs())
        self._assert_aborting(self.sm.manage_instance)

    def _assert_aborting(self, function):
        """Helper to test that the given function is actually making the manager abort."""
        from unittest.mock import patch
        with patch("odk_servermanager.manager.ServerManager._ui_abort", side_effect=self.sm._ui_abort) as abort:
            with pytest.raises(SystemExit):
                function()
            abort.assert_called()
