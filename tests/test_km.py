from arma_keysmanager.km import parse_preset
import pytest

preset_file_name = "tests/preset.html"

class TestPresetImporting:

    def test_should_parse_all_mods(self):
        mods = parse_preset(preset_file_name)
        assert len(mods) == 4

    def test_should_return_a_list_of_mod_names(self):
        mods_name = parse_preset(preset_file_name)
        assert "ODKAI" in mods_name
