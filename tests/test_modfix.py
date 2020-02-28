from os.path import isdir, join, islink, isfile
from typing import Callable, List

import pytest

from conftest import test_folder_structure_path, touch
from odksm_test import ODKSMTest
from odk_servermanager.modfix import ModFix
from odk_servermanager.settings import ServerInstanceSettings
from odk_servermanager.instance import ServerInstance


class TestAModFix(ODKSMTest):
    """Test: A Mod Fix..."""

    def test_should_take_as_arguments_hooks(self):
        """A mod fix should take as arguments hooks."""
        class ModFixTest(ModFix):
            name = "ace"
            hook_pre = lambda s, x: 1
            hook_replace = lambda s, x: 2
            hook_post = lambda s, x: 3
            hook_update_pre = lambda s, x: 4
            hook_update_replace = lambda s, x: 5
            hook_update_post = lambda s, x: 6
        fix = ModFixTest()
        assert isinstance(fix.hook_replace, Callable)
        assert isinstance(fix.hook_pre, Callable)
        assert isinstance(fix.hook_post, Callable)
        assert isinstance(fix.hook_update_replace, Callable)
        assert isinstance(fix.hook_update_pre, Callable)
        assert isinstance(fix.hook_update_post, Callable)
        assert fix.hook_pre(None) == 1
        assert fix.hook_replace(None) == 2
        assert fix.hook_post(None) == 3
        assert fix.hook_update_pre(None) == 4
        assert fix.hook_update_replace(None) == 5
        assert fix.hook_update_post(None) == 6
        assert fix.name == "ace"

    def test_module_should_offer_a_list_of_registered_fix(self):
        """A mod fix module should offer a list of registered fix."""
        from odk_servermanager.modfix import registered_fix
        assert isinstance(registered_fix, List)


class TestAServerInstance(ODKSMTest):
    """Test: A Server Instance ..."""

    def dummy_hook(self, server_instance):
        pass

    @pytest.fixture(autouse=True)
    def setup(self, request, reset_folder_structure, sc_stub, sb_stub):
        """TestAServerInstance setup"""
        request.cls.test_path = test_folder_structure_path()
        settings = ServerInstanceSettings("test", sb_stub, sc_stub, user_mods_list=["ace"], mods_to_be_copied=["ace"],
                                          arma_folder=self.test_path, server_instance_root=self.test_path)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        self.instance._copy_mod("CBA_A3")

    def test_should_have_the_registered_fix_list(self, reset_folder_structure):
        """A server instance should have the registered fix list."""
        from odk_servermanager.modfix import registered_fix
        assert self.instance.registered_fix == registered_fix

    def test_should_call_its_pre_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its pre hook if present."""
        class ModFixTest(ModFix):
            name = "ace"
            hook_pre = self.dummy_hook
        mf = ModFixTest()
        hook = mocker.patch.object(mf, "hook_pre", side_effect=mf.hook_pre)
        self.instance.registered_fix = [mf]
        self.instance._copy_mod("ace")
        hook.assert_called_with(self.instance)
        assert isdir(join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name, "@ace"))

    def test_should_call_its_post_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its post hook if present."""
        class ModFixTest(ModFix):
            name = "ace"
            hook_post = self.dummy_hook
        mf = ModFixTest()
        hook = mocker.patch.object(mf, "hook_post", side_effect=mf.hook_post)
        self.instance.registered_fix = [mf]
        self.instance._copy_mod("ace")
        hook.assert_called_with(self.instance)
        assert isdir(join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name, "@ace"))

    def test_should_call_its_replace_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its replace hook if present."""
        class ModFixTest(ModFix):
            name = "ace"
            hook_replace = self.dummy_hook
        mf = ModFixTest()
        hook = mocker.patch.object(mf, "hook_replace", side_effect=mf.hook_replace)
        self.instance.registered_fix = [mf]
        self.instance._copy_mod("ace")
        hook.assert_called_with(self.instance)
        assert not isdir(join(self.instance.get_server_instance_path(),
                              self.instance.S.copied_mod_folder_name, "@ace"))

    def test_should_call_its_pre_update_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its pre update hook if present."""
        class ModFixTest(ModFix):
            name = "CBA_A3"
            hook_update_pre = self.dummy_hook
        mf = ModFixTest()
        hook = mocker.patch.object(mf, "hook_update_pre", side_effect=mf.hook_update_pre)
        self.instance.registered_fix = [mf]
        self.instance._update_copied_mod("CBA_A3")
        hook.assert_called_with(self.instance)

    def test_should_call_its_post_update_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its post update hook if present."""
        class ModFixTest(ModFix):
            name = "CBA_A3"
            hook_update_post = self.dummy_hook
        mf = ModFixTest()
        hook = mocker.patch.object(mf, "hook_update_post", side_effect=mf.hook_update_post)
        self.instance.registered_fix = [mf]
        self.instance._update_copied_mod("CBA_A3")
        hook.assert_called_with(self.instance)

    def test_should_call_its_replace_update_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its replace update hook if present."""
        class ModFixTest(ModFix):
            name = "CBA_A3"
            hook_update_replace = self.dummy_hook
        mf = ModFixTest()
        hook = mocker.patch.object(mf, "hook_update_replace", side_effect=mf.hook_update_replace)
        custom_file = join(self.instance.get_server_instance_path(), self.instance.S.copied_mod_folder_name,
                           "@CBA_A3", "custom")
        touch(custom_file)
        self.instance.registered_fix = [mf]
        self.instance._update_copied_mod("CBA_A3")
        hook.assert_called_with(self.instance)
        assert isfile(custom_file)


class TestModFixCba(ODKSMTest):
    """Test: ModFix cba..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, class_reset_folder_structure, c_sc_stub, c_sb_stub):
        """TestModFixCba setup"""
        request.cls.test_path = test_folder_structure_path()
        custom_cba = join(self.test_path, "cba_settings.sqf")
        touch(custom_cba, "test")
        settings = ServerInstanceSettings("test", c_sb_stub, c_sc_stub, user_mods_list=["CBA_A3"],
                                          mods_to_be_copied=["CBA_A3"], arma_folder=self.test_path,
                                          server_instance_root=self.test_path,
                                          mod_fix_settings={"cba_settings": custom_cba})
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        self.instance._copy_mod("CBA_A3")
        request.cls.mod_folder = join(self.instance.get_server_instance_path(),
                                      self.instance.S.copied_mod_folder_name, "@CBA_A3")

    def test_should_create_the_folder(self):
        """Mod fix cba should create the folder."""
        assert isdir(self.mod_folder)

    def test_should_link_everything_but_the_userconfig_folder(self):
        """Mod fix cba should link everything but the userconfig folder."""
        assert islink(join(self.mod_folder, "keys"))
        assert not islink(join(self.mod_folder, "userconfig"))

    def test_should_create_the_userconfig_folder(self):
        """Mod fix cba should create the userconfig folder."""
        assert isdir(join(self.mod_folder, "userconfig"))

    def test_should_copy_the_custom_cba_settings(self):
        """Mod fix cba should copy the custom cba settings."""
        cba_settings = join(self.mod_folder, "userconfig", "cba_settings.sqf")
        assert isfile(cba_settings)
        with open(cba_settings, "r") as f:
            assert f.read() == "test"

    def test_should_manage_its_update(self):
        """Mod fix cba should manage its update."""
        cba_settings = join(self.mod_folder, "userconfig", "cba_settings.sqf")
        with open(cba_settings, "a+") as f:
            assert f.write("\nnew_config")
        self.instance._update_copied_mod("CBA_A3")
        with open(cba_settings, "r") as f:
            assert f.read() == "test\nnew_config"
