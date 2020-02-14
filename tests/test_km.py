from arma_keysmanager.km import parse_preset, clear_keys_folder
from conftest import test_folder_structure_name, test_preset_file_name
import os
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


class TestKeysSetUp:
    """The keys set up should..."""

    def test_should_clear_the_keys_folder(self, reset_folder_structure):
        """The keys set up should clear the provided Keys folder"""
        keys_folder = os.path.join(test_folder_structure_name, "Keys")
        test_key = os.path.join(keys_folder, "testkey.bikey")
        with open(test_key, "w+") as f:
            f.write("0")
        clear_keys_folder(keys_folder)
        assert not os.path.isfile(test_key)
