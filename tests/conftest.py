import os
import pytest
import shutil
import zipfile
from typing import Callable
from unittest.mock import patch

test_resources = "tests/resources/"
test_preset_file_name = test_resources + "preset.html"
test_folder_structure_name = test_resources + "Arma"
test_folder_structure_zip = test_resources + "folder_structure.zip"


def test_folder_structure_path(): return os.path.abspath(test_folder_structure_name)


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


@pytest.fixture()
def observe_function(mocker):
    """Mock the provided function, setting as side effect the function itself.
    This allows to normally execute the function and to observe its calls."""
    def _wrapper(function: Callable):
        # noinspection PyUnresolvedReferences
        name = function.__module__ + "." + function.__name__
        return mocker.patch(name, side_effect=function)
    return _wrapper


def spy(method: Callable):
    # noinspection PyUnresolvedReferences
    return patch.object(method.__self__, method.__name__, wraps=method)
