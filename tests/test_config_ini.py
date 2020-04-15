from os.path import join

import pytest

from conftest import test_resources
from odk_servermanager.config_ini import ConfigIni
from odksm_test import ODKSMTest


class TestAConfigIni(ODKSMTest):
    """Test: AConfigIni..."""

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

