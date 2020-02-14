from arma_keysmanager.km import parse_preset
import pytest

preset_file_name = "tests/preset.html"

class TestPresetImporting:

    def test_should_parse_all_mods(self, reset_folder_structure):
        """The preset mechanism should parse all mod in the preset"""
        mods = parse_preset(preset_file_name)
        assert len(mods) == 4

    def test_should_return_a_list_of_mod_names(self):
        """The preset mechanism should return a list of mod names"""
        mods_name = parse_preset(preset_file_name)
        assert isinstance(mods_name, list)
        assert isinstance(mods_name[0], str)
        assert "ODKAI" in mods_name
