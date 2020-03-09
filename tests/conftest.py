import os
from os.path import join

import pytest
import shutil
import zipfile
from typing import Callable, List
from unittest.mock import patch

from odk_servermanager.settings import ServerBatSettings, ServerConfigSettings

test_resources = join("tests", "resources")
test_preset_file_name = join(test_resources, "preset.html")
test_folder_structure_name = join(test_resources, "Arma")
test_folder_structure_zip = join(test_resources, "folder_structure.zip")


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


def touch(file_name: str, content: str = "") -> None:
    """Helper function to quickly write into a file"""
    with open(file_name, "w+") as f:
        f.write(content)


@pytest.fixture()
def assert_requires_arguments():
    """Helper fixture for asserting function argument requirements"""
    def _wrapper(function: Callable, arguments: List[str]):
        with pytest.raises(TypeError) as err:
            function()
        for arg in arguments:
            assert err.value.args[0].find(arg) > 0
    return _wrapper


# Test stubs
def sb_stub_obj() -> ServerBatSettings:
    return ServerBatSettings("title", "2000", r"serverConfig.cfg", r"serverCfg.cfg", "128")


def sc_stub_obj() -> ServerConfigSettings:
    return ServerConfigSettings("title", "123", "456", "missionName")


@pytest.fixture()
def sb_stub() -> ServerBatSettings:
    """Return a mock ServerBatInstance object"""
    return sb_stub_obj()


@pytest.fixture()
def sc_stub() -> ServerConfigSettings:
    """Return a mock ServerBatInstance object"""
    return sc_stub_obj()


@pytest.fixture(scope="class")
def c_sb_stub() -> ServerBatSettings:
    """Return a mock ServerBatInstance object"""
    return sb_stub_obj()


@pytest.fixture(scope="class")
def c_sc_stub() -> ServerConfigSettings:
    """Return a mock ServerBatInstance object"""
    return sc_stub_obj()
