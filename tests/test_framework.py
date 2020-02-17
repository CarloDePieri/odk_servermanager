from conftest import _reset_folder_structure, test_folder_structure_name
import os
import shutil


class TestFolderStructureReset:

    def test_should_create_the_structure_if_not_there(self):
        # ensure there's no folder structure
        if os.path.isdir(test_folder_structure_name):
            shutil.rmtree(test_folder_structure_name, ignore_errors=True)
        _reset_folder_structure()
        assert os.path.isdir(test_folder_structure_name)

    def test_should_reset_the_structure_if_already_there(self):
        # ensure there's a folder structure to begin with
        _reset_folder_structure()
        testfile = "tests/resources/Arma/testfile.txt"
        with open(testfile, "w+") as f:
            f.write("Hello there!")
        _reset_folder_structure()
        assert not os.path.isfile(testfile)
