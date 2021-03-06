from os import mkdir, unlink
from os.path import join, islink, isfile

import pytest

from conftest import test_folder_structure_path, touch
from odksm_test import ODKSMTest
from odk_servermanager.instance import ServerInstance
from odk_servermanager.settings import ModFixSettings, ServerInstanceSettings
from odk_servermanager.utils import symlink


class TestAModFixOdkaiLocal(ODKSMTest):
    """Test: A ModFix ODKAILocal..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, c_sc_stub, c_sb_stub, class_reset_folder_structure):
        """TestAModFixOdkailocal setup"""
        # prepare the local folder
        request.cls.test_path = test_folder_structure_path()
        local_folder = join(self.test_path, "local_odkai")
        mkdir(local_folder)
        touch(join(local_folder, "local_mod"), "this is a local mod")

        fix_settings = ModFixSettings(enabled_fixes=["odkai_local"],
                                      mod_fix_settings={"odkai_local_path": local_folder})
        settings = ServerInstanceSettings("test", c_sb_stub, c_sc_stub, user_mods_list=["ODKAI"],
                                          arma_folder=self.test_path,
                                          server_instance_root=self.test_path,
                                          fix_settings=fix_settings)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        self.instance._start_op_on_mods("init", ["ODKAI"])
        request.cls.mod_folder = join(self.instance.get_server_instance_path(),
                                      self.instance.S.linked_mod_folder_name, "@ODKAI")

    def test_should_symlink_the_local_copy(self):
        """A mod fix odkailocal should symlink the local copy."""
        assert islink(self.mod_folder)

    def test_on_update_should_force_the_local_copy(self):
        """A mod fix odkai local on update should force the local copy."""
        unlink(self.mod_folder)
        symlink(join(self.test_path, "!Workshop", "@ODKAI"), self.mod_folder)
        assert not isfile(join(self.mod_folder, "local_mod"))
        self.instance._start_op_on_mods("update", ["ODKAI"])
        assert islink(self.mod_folder)
        assert isfile(join(self.mod_folder, "local_mod"))
