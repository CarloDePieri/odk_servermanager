import pytest

from conftest import test_preset_file_name
from odk_servermanager.manager import ServerManager
from odksm_test import ODKSMTest


class TestPresetImporting(ODKSMTest):
    """The preset mechanism should..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPresetImporting setup"""
        request.cls.manager = ServerManager()

    def test_should_parse_all_mods(self):
        """The preset mechanism should parse all mod in the preset"""
        mods = self.manager._parse_preset(test_preset_file_name)
        assert len(mods) == 4

    def test_should_return_a_list_of_mod_names(self):
        """The preset mechanism should return a list of mod names"""
        mods_name = self.manager._parse_preset(test_preset_file_name)
        assert isinstance(mods_name, list)
        assert isinstance(mods_name[0], str)
        assert "ODKAI" in mods_name
        assert "ACE Compat - RHS- GREF"  # this checks for a filter fix on the name
