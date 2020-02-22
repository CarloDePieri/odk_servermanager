import odk_servermanager.keysmanager as km
from conftest import test_folder_structure_name
import os


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

    def test_should_first_clear_the_keys_folder_and_then_copy_the_keys_there(self, reset_folder_structure,
                                                                             observe_function, mocker):
        """Keys set up should first clear the keys folder and then copy the keys there."""
        observe_function(km.clear_keys_folder)
        observe_function(km.copy_keys)
        mods_list = ["ODKAI", "ace"]
        mods_folder = os.path.join(os.path.abspath(test_folder_structure_name), "!Workshop")
        keys_folder = os.path.join(os.path.abspath(test_folder_structure_name), "Keys")
        km.set_up_keys(mods_list, mods_folder, keys_folder)
        km.clear_keys_folder.assert_called_with(keys_folder)
        km.copy_keys.assert_called_with(mods_list, mods_folder, keys_folder)
        files_in_keys_dir = os.listdir(keys_folder)
        keys = list(filter(lambda x: km.is_keyfile(os.path.join(keys_folder, x)), files_in_keys_dir))
        assert len(keys) == 2
