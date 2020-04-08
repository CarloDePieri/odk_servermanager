from typing import Callable, List

import pytest

from conftest import test_folder_structure_path
from odksm_test import ODKSMTest
from odk_servermanager.modfix import ModFix, register_fixes, NonExistingFixFile, MisconfiguredModFix, ErrorInModFix
from odk_servermanager.modfix.cba_a3 import ModFixCBA
from odk_servermanager.settings import ServerInstanceSettings, ModFixSettings
from odk_servermanager.instance import ServerInstance


class TestAModFix(ODKSMTest):
    """Test: A Mod Fix..."""

    def test_should_take_as_arguments_hooks(self):
        """A mod fix should take as arguments hooks."""
        class ModFixTest(ModFix):
            name = "ace"
            hook_init_copy_pre = lambda s, x: 1
            hook_init_copy_replace = lambda s, x: 2
            hook_init_copy_post = lambda s, x: 3
            hook_update_copy_pre = lambda s, x: 4
            hook_update_copy_replace = lambda s, x: 5
            hook_update_copy_post = lambda s, x: 6
        fix = ModFixTest()
        assert isinstance(fix.hook_init_copy_replace, Callable)
        assert isinstance(fix.hook_init_copy_pre, Callable)
        assert isinstance(fix.hook_init_copy_post, Callable)
        assert isinstance(fix.hook_update_copy_replace, Callable)
        assert isinstance(fix.hook_update_copy_pre, Callable)
        assert isinstance(fix.hook_update_copy_post, Callable)
        assert fix.hook_init_copy_pre(None) == 1
        assert fix.hook_init_copy_replace(None) == 2
        assert fix.hook_init_copy_post(None) == 3
        assert fix.hook_update_copy_pre(None) == 4
        assert fix.hook_update_copy_replace(None) == 5
        assert fix.hook_update_copy_post(None) == 6
        assert fix.name == "ace"

    def test_module_should_offer_a_list_of_registered_fix(self):
        """A mod fix module should offer a list of registered fix."""
        fixes = register_fixes(["cba_a3"])
        assert isinstance(fixes, List)
        assert isinstance(fixes[0], ModFixCBA)

    def test_should_raise_an_error_with_mis_configured_fixes(self, monkeypatch):
        """A mod fix should raise an error with mis-configured fixes."""
        with pytest.raises(NonExistingFixFile):
            register_fixes(["NOT_THERE"])
        monkeypatch.delattr("odk_servermanager.modfix.cba_a3.to_be_registered")  # simulate a broken mod fix
        with pytest.raises(MisconfiguredModFix):
            register_fixes(["cba_a3"])


class TestAServerInstance(ODKSMTest):
    """Test: A Server Instance ..."""

    def dummy_hook(self, server_instance, call_data):
        pass

    def broken_hook(self, server_instance, call_data):
        raise Exception

    @pytest.fixture(autouse=True)
    def setup(self, request, reset_folder_structure, sc_stub, sb_stub):
        """TestAServerInstance setup"""
        request.cls.test_path = test_folder_structure_path()
        request.cls.enabled_fixes = ["cba_a3"]
        settings = ServerInstanceSettings("test", sb_stub, sc_stub, user_mods_list=["ace"], mods_to_be_copied=["ace"],
                                          fix_settings=ModFixSettings(enabled_fixes=self.enabled_fixes),
                                          arma_folder=self.test_path, server_instance_root=self.test_path)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        self.instance._copy_mod("CBA_A3")

    def test_should_have_the_registered_fix_list(self, reset_folder_structure):
        """A server instance should have the registered fix list."""
        from odk_servermanager.modfix import register_fixes
        assert self.instance.registered_fix == register_fixes(["cba_a3"])

    @pytest.mark.parametrize("time", ["pre", "replace", "post"])
    @pytest.mark.parametrize("operation", ["copy", "link"])
    @pytest.mark.parametrize("stage", ["update", "init"])
    def test_should_call_its_hooks(self, time, operation, stage, mocker):
        """A server instance should call its hooks."""
        mod_name = "CBA_A3"

        class ModFixTest(ModFix):
            name = mod_name
        mf = ModFixTest()
        hook_name = "hook_{}_{}_{}".format(stage, operation, time)
        mf.__setattr__(hook_name, self.dummy_hook)
        hook = mocker.patch.object(mf, hook_name, side_effect=mf.__getattribute__(hook_name))
        default_op = mocker.patch.object(self.instance, "_do_default_op", side_effect=self.instance._do_default_op)
        self.instance.registered_fix = [mf]
        self.instance._apply_hooks_and_do_op(stage, operation, mod_name)
        call_data = [stage, operation, mod_name]
        hook.assert_called_with(self.instance, call_data)
        if time == "replace":
            default_op.assert_not_called()
        else:
            default_op.assert_called()
        mf.__setattr__(hook_name, self.broken_hook)
        with pytest.raises(ErrorInModFix):
            self.instance._apply_hooks_and_do_op(stage, operation, mod_name)
