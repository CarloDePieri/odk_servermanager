from os.path import isdir, join
from typing import Callable, List

import pytest

from conftest import test_folder_structure_path
from odksm_test import ODKSMTest
from odk_servermanager.modfix import ModFix


class TestAModFix(ODKSMTest):
    """Test: A Mod Fix..."""

    def test_should_take_as_arguments_hooks(self):
        """A mod fix should take as arguments hooks."""
        fix = ModFix(
            name="testmod",
            hook_pre=lambda x: 1,
            hook_replace=lambda x: 2,
            hook_post=lambda x: 3
        )
        assert isinstance(fix.hook_replace, Callable)
        assert isinstance(fix.hook_pre, Callable)
        assert isinstance(fix.hook_post, Callable)
        assert fix.hook_pre(None) == 1
        assert fix.hook_replace(None) == 2
        assert fix.hook_post(None) == 3
        assert fix.name == "testmod"

    def test_module_should_offer_a_list_of_registered_fix(self):
        """A mod fix module should offer a list of registered fix."""
        from odk_servermanager.modfix import registered_fix
        assert isinstance(registered_fix, List)


@pytest.mark.runthis
class TestAServerInstance(ODKSMTest):
    """Test: A Server Instance ..."""

    @staticmethod
    def dummy_hook(server_instance):
        pass

    @pytest.fixture(autouse=True)
    def setup(self, request, reset_folder_structure):
        """TestAServerInstance setup"""
        from odk_servermanager.instance import ServerInstanceSettings, ServerInstance
        request.cls.test_path = test_folder_structure_path()
        settings = ServerInstanceSettings("test", user_mods_list=["ace"], mods_to_be_copied=["ace"],
                                          arma_folder=self.test_path, server_instance_root=self.test_path)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()

    def test_should_have_the_registered_fix_list(self, reset_folder_structure):
        """A server instance should have the registered fix list."""
        from odk_servermanager.modfix import registered_fix
        assert self.instance.registered_fix == registered_fix

    def test_should_call_its_pre_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its pre hook if present."""
        df = mocker.patch.object(self, "dummy_hook", side_effect=self.dummy_hook)
        self.instance.registered_fix = [ModFix(name="ace", hook_pre=self.dummy_hook)]
        self.instance._init_mods(["ace"])
        df.assert_called_with(self.instance)
        assert isdir(join(self.instance._get_server_instance_path(), self.instance.S.copied_mod_folder_name, "@ace"))

    def test_should_call_its_post_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its post hook if present."""
        df = mocker.patch.object(self, "dummy_hook", side_effect=self.dummy_hook)
        self.instance.registered_fix = [ModFix(name="ace", hook_post=self.dummy_hook)]
        self.instance._init_mods(["ace"])
        df.assert_called_with(self.instance)
        assert isdir(join(self.instance._get_server_instance_path(), self.instance.S.copied_mod_folder_name, "@ace"))

    def test_should_call_its_replace_hook_if_present(self, mocker, reset_folder_structure):
        """A server instance should call its replace hook if present."""
        df = mocker.patch.object(self, "dummy_hook", side_effect=self.dummy_hook)
        self.instance.registered_fix = [ModFix(name="ace", hook_replace=self.dummy_hook)]
        self.instance._init_mods(["ace"])
        df.assert_called_with(self.instance)
        assert not isdir(join(self.instance._get_server_instance_path(), self.instance.S.copied_mod_folder_name, "@ace"))
