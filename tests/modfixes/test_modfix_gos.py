from os.path import islink, join

import pytest

from conftest import test_folder_structure_path
from odksm_test import ODKSMTest
from odk_servermanager.instance import ServerInstance
from odk_servermanager.settings import ModFixSettings, ServerInstanceSettings


class TestAModfixGos(ODKSMTest):
    """Test: AModfixGOS..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, c_sc_stub, c_sb_stub, class_reset_folder_structure):
        """TestAModfixGos setup"""
        request.cls.test_path = test_folder_structure_path()
        fix_settings = ModFixSettings(enabled_fixes=["gos"])
        settings = ServerInstanceSettings("test", c_sb_stub, c_sc_stub,
                                          user_mods_list=["G.O.S Dariyah", "G.O.S Al Rayak"],
                                          arma_folder=self.test_path,
                                          server_instance_root=self.test_path,
                                          fix_settings=fix_settings)
        request.cls.instance = ServerInstance(settings)
        self.instance._new_server_folder()
        self.instance._prepare_server_core()
        self.instance._start_op_on_mods("init", ["G.O.S Dariyah"])
        self.instance._start_op_on_mods("init", ["G.O.S Al Rayak"])
        request.cls.moda_folder = join(self.instance.get_server_instance_path(),
                                       self.instance.S.copied_mod_folder_name, "@G.O.S Dariyah")
        request.cls.modb_folder = join(self.instance.get_server_instance_path(),
                                       self.instance.S.copied_mod_folder_name, "@G.O.S Al Rayak")

    def test_should_have_linked_the_keys_folder(self):
        """A modfix gos should have linked the keys folder."""
        assert islink(join(self.moda_folder, "PublicKey_GOS_Makhno"))
        assert islink(join(self.modb_folder, "PublicKey_GOS_Makhno"))
        assert islink(join(self.moda_folder, "keys"))
        assert islink(join(self.modb_folder, "keys"))
        self.instance._link_keys()
        assert islink(join(self.instance.get_server_instance_path(), "Keys", "GOSMAKHNO.bikey"))

    def test_should_link_the_keys_also_after_an_update(self):
        """A modfix gos should link the keys also after an update."""
        self.instance._start_op_on_mods("update", ["G.O.S Dariyah"])
        self.instance._start_op_on_mods("update", ["G.O.S Al Rayak"])
        self.instance._clear_keys()
        self.instance._link_keys()
        assert islink(join(self.instance.get_server_instance_path(), "Keys", "GOSMAKHNO.bikey"))
