from os.path import join, isfile
from typing import Dict

import pytest

from conftest import test_preset_file_name, test_resources
from odk_servermanager.manager import ServerManager
from odk_servermanager.settings import ServerInstanceSettings, ServerBatSettings, ServerConfigSettings
from odksm_test import ODKSMTest


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
        assert isinstance(sm.settings.mod_fix_settings, Dict)
        assert sm.settings.server_instance_name == "training"
        assert sm.settings.mods_to_be_copied == ["CBA_A3"]
        assert sm.settings.bat_settings.server_title == "TEST SERVER"
        assert sm.settings.config_settings.password == "p4ssw0rd"
        assert sm.settings.mod_fix_settings["cba_settings"] == "tests/resources/server.cfg"
        assert len(sm.settings.skip_keys) == 1  # this check that empty list field in config don't pollute the list

    def test_should_read_the_config_and_parse_the_preset_if_present_at_init(self):
        """The preset manager should read the config and parse the preset if present at init."""
        sm = ServerManager(join(test_resources, "config.ini"))
        sm._recover_settings()
        assert isinstance(sm.settings, ServerInstanceSettings)
        assert len(sm.settings.user_mods_list) == 5


@pytest.mark.runthis
class TestAServerManagerAtInit(ODKSMTest):
    """Test: A Server Manager at Init..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestAServerManagerAtInit setup"""
        request.cls.sm = ServerManager(join(test_resources, "config.ini"))

    def test_should_init_the_server_instance(self, reset_folder_structure):
        """A server manager at init should init the server instance."""
        self.sm.manage_instance()
        assert isfile(join(self.sm.instance.get_server_instance_path(), self.sm.settings.bat_settings.server_config_file_name))

    def test_should_ask_confirmation_before_update_if_called_twice(self, reset_folder_structure, mocker):
        """A server manager at init should ask confirmation before update if called twice."""
        self.sm.manage_instance()
        answer = mocker.patch("builtins.input", return_value="y")
        update = mocker.patch("odk_servermanager.instance.ServerInstance.update", side_effect=self.sm.instance.update)
        self.sm.manage_instance()
        answer.assert_called()
        update.assert_called()

    def test_should_stop_when_updating_if_its_told_to_do_so(self, reset_folder_structure, mocker):
        """A server manager at init should stop when updating if its told to do so."""
        self.sm.manage_instance()
        answer = mocker.patch("builtins.input", return_value="n")
        update = mocker.patch("odk_servermanager.instance.ServerInstance.update", side_effect=self.sm.instance.update)
        self.sm.manage_instance()
        answer.assert_called()
        update.assert_not_called()
