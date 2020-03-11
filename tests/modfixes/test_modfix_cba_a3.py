from os.path import join, islink, isfile

import pytest

from conftest import test_folder_structure_path, touch
from odksm_test import ODKSMTest
from odk_servermanager.settings import ModFixSettings, ServerInstanceSettings
from odk_servermanager.instance import ServerInstance


class TestModFixCba(ODKSMTest):
    """Test: ModFix cba..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub, c_sb_stub):
        """TestModFixCba setup"""
        request.cls.test_path = test_folder_structure_path()
        custom_cba = join(self.test_path, "cba_settings.sqf")
        touch(custom_cba, "test")
        fix_settings = ModFixSettings(enabled_fixes=["cba_a3"], mod_fix_settings={"cba_settings": custom_cba})
        settings = ServerInstanceSettings("test", c_sb_stub, c_sc_stub, user_mods_list=["CBA_A3"],
                                          arma_folder=self.test_path,
                                          server_instance_root=self.test_path,
                                          fix_settings=fix_settings)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        request.cls.mod_folder = join(self.instance.get_server_instance_path(),
                                      self.instance.S.linked_mod_folder_name, "@CBA_A3")
        request.cls.cba_settings = join(self.instance.get_server_instance_path(), "userconfig", "cba_settings.sqf")

    def test_should_create_the_folder(self):
        """Mod fix cba should create the folder."""
        assert islink(self.mod_folder)

    def test_should_copy_the_custom_cba_settings(self):
        """Mod fix cba should copy the custom cba settings."""
        assert isfile(self.cba_settings)
        with open(self.cba_settings, "r") as f:
            assert f.read() == "test"

    def test_should_keep_modification_to_the_cba_settings_on_update(self):
        """Mod fix cba should keep modification to the cba_settings on update."""
        with open(self.cba_settings, "a+") as f:
            assert f.write("\nnew_config")
        self.instance._start_op_on_mods("update", ["CBA_A3"])
        with open(self.cba_settings, "r") as f:
            assert f.read() == "test\nnew_config"
