import os
import pytest
import shutil
import zipfile

test_resources = "tests/resources/"
test_preset_file_name = test_resources + "preset.html"
test_folder_structure_name = test_resources + "Arma"
test_folder_structure_zip = test_resources + "folder_structure.zip"


def test_folder_structure_path(): return os.path.abspath(test_folder_structure_name)


@pytest.fixture(scope="session", autouse=True)
def pre_test():
    # prepare something ahead of all tests
    from unittest.mock import patch
    # overwrite some configuration
    test_root = test_folder_structure_path()
    with patch("odk_servermanager.sm.SERVER_INSTANCE_ROOT", test_root), \
         patch("odk_servermanager.sm.ARMA_FOLDER", test_root):
        yield


def _reset_folder_structure():
    """Reset the folder structure to test on"""
    # Delete the old folder if present
    if os.path.isdir(test_folder_structure_name):
        shutil.rmtree(test_folder_structure_name, ignore_errors=True)
    # Extract a pristine folder structure
    with zipfile.ZipFile(test_folder_structure_zip, 'r') as zip_ref:
        zip_ref.extractall("./" + test_resources)


@pytest.fixture()
def reset_folder_structure():
    """Reset the folder structure to test on"""
    _reset_folder_structure()


@pytest.fixture("class")
def class_reset_folder_structure():
    """Reset the folder structure to test on"""
    _reset_folder_structure()
