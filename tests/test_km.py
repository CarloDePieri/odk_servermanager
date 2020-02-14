from arma_keysmanager.km import parse_preset, clear_keys_folder
from conftest import test_folder_structure_name, test_preset_file_name
import pytest


class TestPresetImporting:
    """The preset mechanism should..."""

    def test_should_parse_all_mods(self):
        """The preset mechanism should parse all mod in the preset"""
        mods = parse_preset(test_preset_file_name)
        assert len(mods) == 4

    def test_should_return_a_list_of_mod_names(self):
        """The preset mechanism should return a list of mod names"""
        mods_name = parse_preset(test_preset_file_name)
        assert isinstance(mods_name, list)
        assert isinstance(mods_name[0], str)
        assert "ODKAI" in mods_name
