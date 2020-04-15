from os.path import join, isfile

import pytest

from conftest import test_resources, test_folder_structure_path
from odk_servermanager.config_ini import ConfigIni
from odksm_test import ODKSMTest


class TestAConfigIni(ODKSMTest):
    """Test: AConfigIni..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure):
        """TestAConfigIni setup"""
        request.cls.test_path = test_folder_structure_path()

    def test_should_be_able_to_read_a_config_ini_file(self):
        """A config ini should be able to read a config ini file."""
        config_file = join(test_resources, "config.ini")
        data = ConfigIni.read_file(config_file)
        for key in ["ODKSM", "bat", "config", "mod_fix_settings"]:
            assert key in data
        # check some fields
        assert data["bat"]["server_title"] == "TEST SERVER"
        assert data["config"]["password"] == "p4ssw0rd"
        for supposed_list in ["server_mods_list", "mods_to_be_copied", "user_mods_list", "skip_keys"]:
            assert isinstance(data["ODKSM"][supposed_list], list)
        assert isinstance(data["mod_fix_settings"]["enabled_fixes"], list)
        assert data["mod_fix_settings"]["cba_settings"] == "tests/resources/server.cfg"

    def test_should_be_able_to_get_the_config_ini_structure(self):
        """A config ini should be able to get the config.ini structure."""
        data = ConfigIni._get_config_structure()
        assert isinstance(data, dict)
        assert len(data) == 2
        assert len(data["sections"]) == 4

    def test_should_be_able_to_create_a_config_ini_file(self, reset_folder_structure, have_same_content):
        """A config ini should be able to create a config ini file."""
        data = {
            "config": {
                "hostname": "TEST SERVER",
                "password": "p4ssw0rd",
                "password_admin": "p4ssw0rd!",
                "mission_template": "mission.name"
            },
            "bat": {
                "server_title": "TEST SERVER",
                "server_port": "2202",
                "server_max_mem": "8192",
                "server_config_file_name": "serverConfig.cfg",
                "server_cfg_file_name": "Arma3Training.cfg"
            },
            "ODKSM": {
                "server_instance_name": "training"
            }
        }
        config_file = join(self.test_path, "config.ini")
        ConfigIni().create_file(config_file, data)
        assert isfile(config_file)
        control = join(test_resources, "config_commented.ini")
        assert have_same_content(config_file, control)

    def test_should_be_able_to_create_a_config_ini_file_without_comments(self, reset_folder_structure,
                                                                         have_same_content):
        """A config ini should be able to create a config ini file without comments."""
        data = {
            "config": {
                "hostname": "TEST SERVER",
                "password": "p4ssw0rd",
                "password_admin": "p4ssw0rd!",
                "mission_template": "mission.name"
            },
            "bat": {
                "server_title": "TEST SERVER",
                "server_port": "2202",
                "server_max_mem": "8192",
                "server_config_file_name": "ServerConfig.cfg",
                "server_cfg_file_name": "Arma3Training.cfg"
            },
            "ODKSM": {
                "server_instance_name": "training",
                "server_mods_list": ["ODKMIN"],
                "mods_to_be_copied": ["ace"],
                "user_mods_list":  ["ace", "CBA_A3"],
                "user_mods_preset": "tests/resources/preset.html",
                "arma_folder": "tests/resources/Arma",
                "skip_keys": ""
            },
            "mod_fix_settings": {
                "enabled_fixes": ["cba_a3"],
                "cba_settings": "tests/resources/server.cfg"
            }
        }
        config_file = join(self.test_path, "config.ini")
        ConfigIni().create_file(config_file, data, add_comments=False, add_no_value_entry=False)
        assert isfile(config_file)
        control = join(test_resources, "config.ini")
        assert have_same_content(config_file, control)

    def test_should_be_able_to_create_a_config_ini_file_starting_from_the_data_of_another(self, reset_folder_structure,
                                                                                          have_same_content):
        """A config ini should be able to create a config.ini file starting from the data of another."""
        control = join(test_resources, "config_commented.ini")
        config_file = join(self.test_path, "config.ini")
        data = ConfigIni.read_file(control)
        ConfigIni().create_file(config_file, data)
        assert isfile(config_file)
        assert have_same_content(config_file, control)
