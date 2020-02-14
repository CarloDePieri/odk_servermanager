import arma_keysmanager.km as km
from conftest import test_folder_structure_name, test_preset_file_name
import os


class TestPresetImporting:
    """The preset mechanism should..."""

    def test_should_parse_all_mods(self):
        """The preset mechanism should parse all mod in the preset"""
        mods = km.parse_preset(test_preset_file_name)
        assert len(mods) == 4

    def test_should_return_a_list_of_mod_names(self):
        """The preset mechanism should return a list of mod names"""
        mods_name = km.parse_preset(test_preset_file_name)
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
        km.clear_keys_folder(keys_folder)
        assert not os.path.isfile(test_key)

    def test_should_copy_all_keys_to_the_keys_folder(self, reset_folder_structure):
        mods_list = ["ODKAI",
                     "3CB BAF Equipment",
                     "ace",
                     "Task Force Arrowhead Radio (BETA!!!)"]
        mods_folder = os.path.join(os.path.abspath(test_folder_structure_name), "!Workshop")
        keys_folder = os.path.join(os.path.abspath(test_folder_structure_name), "Keys")
        km.copy_keys(mods_list, mods_folder, keys_folder)
        files_in_keys_dir = os.listdir(keys_folder)
        keys = list(filter(lambda x: km.is_keyfile(os.path.join(keys_folder, x)), files_in_keys_dir))
        assert len(keys) == 4
        assert "ODKAI_V1_3_5.bikey" in keys

    def test_should_first_clear_the_keys_folder_and_then_copy_the_keys_there(self, reset_folder_structure, mocker):
        """Keys set up should first clear the keys folder and then copy the keys there."""
        mocker.patch("arma_keysmanager.km.clear_keys_folder", side_effect=km.clear_keys_folder)
        mocker.patch("arma_keysmanager.km.copy_keys", side_effect=km.copy_keys)
        mods_list = ["ODKAI",
                     "ace"]
        mods_folder = os.path.join(os.path.abspath(test_folder_structure_name), "!Workshop")
        keys_folder = os.path.join(os.path.abspath(test_folder_structure_name), "Keys")
        km.set_up_keys(mods_list, mods_folder, keys_folder)
        km.clear_keys_folder.assert_called_with(keys_folder)
        km.copy_keys.assert_called_with(mods_list, mods_folder, keys_folder)
        files_in_keys_dir = os.listdir(keys_folder)
        keys = list(filter(lambda x: km.is_keyfile(os.path.join(keys_folder, x)), files_in_keys_dir))
        assert len(keys) == 2
