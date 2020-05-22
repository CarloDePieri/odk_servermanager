from os import unlink, mkdir
from os.path import join, islink, isfile
from shutil import rmtree

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
        request.cls.custom_cba = join(self.test_path, "cba_settings.sqf")
        touch(self.custom_cba, "test")
        fix_settings = ModFixSettings(enabled_fixes=["cba_a3"], mod_fix_settings={"cba_settings": self.custom_cba})
        settings = ServerInstanceSettings("test", c_sb_stub, c_sc_stub, user_mods_list=["CBA_A3"],
                                          arma_folder=self.test_path,
                                          server_instance_root=self.test_path,
                                          fix_settings=fix_settings)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        request.cls.mod_folder = join(self.instance.get_server_instance_path(),
                                      self.instance.S.linked_mod_folder_name, "@CBA_A3")
        request.cls.cba_settings = join(self.instance.get_server_instance_path(), "userconfig", "cba_settings.sqf")

    @pytest.fixture(autouse=True)
    def single_test_setup(self):
        """TestModFixCba single test setup"""
        yield
        unlink(self.mod_folder)
        rmtree(join(self.instance.get_server_instance_path(), "userconfig"))
        mkdir(join(self.instance.get_server_instance_path(), "userconfig"))

    def test_should_create_the_folder(self):
        """Mod fix cba should create the folder."""
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        assert islink(self.mod_folder)

    def test_should_link_the_cba_settings_by_default(self, have_same_content):
        """Mod fix cba should link the cba_settings by default."""
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        assert islink(self.cba_settings)
        assert have_same_content(self.cba_settings, self.custom_cba)

    def test_should_maintain_the_link_to_the_cba_settings_by_default_when_updating(self, have_same_content):
        """Mod fix cba should maintain the link to the cba_settings by default when updating."""
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        self.instance._start_op_on_mods("update", ["CBA_A3"])
        assert islink(self.cba_settings)
        assert have_same_content(self.cba_settings, self.custom_cba)

    def test_should_copy_the_custom_cba_settings_with_the_right_settings(self, monkeypatch, have_same_content):
        """Mod fix cba should copy the custom cba settings with the right settings."""
        monkeypatch.setitem(self.instance.S.fix_settings.mod_fix_settings, "instance_specific_cba", True)
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        assert isfile(self.cba_settings)
        assert not islink(self.cba_settings)
        assert have_same_content(self.cba_settings, self.custom_cba)

    def test_should_keep_modification_to_the_cba_settings_when_updating_a_copy(self, monkeypatch, have_same_content):
        """Mod fix cba should keep modification to the cba_settings when updating a copy."""
        monkeypatch.setitem(self.instance.S.fix_settings.mod_fix_settings, "instance_specific_cba", True)
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        with open(self.cba_settings, "a+") as f:
            assert f.write("\nnew_config")
        self.instance._start_op_on_mods("update", ["CBA_A3"])
        assert isfile(self.cba_settings)
        assert not islink(self.cba_settings)
        # now check that edits have not been lost
        assert not have_same_content(self.cba_settings, self.custom_cba)

    def test_should_behave_when_updating_from_symlinked_to_copied_cba(self, monkeypatch):
        """Mod fix cba should behave when updating from symlinked to copied cba."""
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        monkeypatch.setitem(self.instance.S.fix_settings.mod_fix_settings, "instance_specific_cba", True)
        self.instance._start_op_on_mods("update", ["CBA_A3"])
        assert isfile(self.cba_settings)
        assert not islink(self.cba_settings)

    def test_should_behave_when_updating_from_copied_to_symlinked_cba(self, monkeypatch):
        """Mod fix cba should behave when updating from copied to symlinked cba."""
        monkeypatch.setitem(self.instance.S.fix_settings.mod_fix_settings, "instance_specific_cba", True)
        self.instance._start_op_on_mods("init", ["CBA_A3"])
        monkeypatch.setitem(self.instance.S.fix_settings.mod_fix_settings, "instance_specific_cba", False)
        self.instance._start_op_on_mods("update", ["CBA_A3"])
        assert islink(self.cba_settings)
