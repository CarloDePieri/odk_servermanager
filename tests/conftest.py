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
test_preset_tofix_file_name = join(test_resources, "preset-tofix.html")
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


@pytest.fixture()
def have_same_content():
    """Helper fixture checking files content equality."""
    def _wrapper(first_file_path: str, second_file_path: str) -> bool:
        with open(first_file_path, "r") as first, open(second_file_path, "r") as second:
            return first.read() == second.read()
    return _wrapper


@pytest.fixture()
def patch_with_hook(mocker):
    """This fixture is used to mock the given 'function_to_mock_name' and modify its output via a 'function_hook'.

    It will call a mocker.patch() on the given 'function_to_mock_name' and apply as a side_effect a function with the
    same signature that will first call the original, not mocked 'function_to_mock', pipe the output to 'function_hook'
    and return the final chained output.
    It can work with methods, but the 'function_to_mock' must be a bound function, meaning that it must be passed as
    object.method, NOT as class.method.

    function_to_mock: the actual function or method to be mocked
    function_to_mock_name: the name of the function that will be passed to patch. Remember: the location is relevant!
    function_hook: this is the function that will take the original function output as input (so it must be built
                    accordingly) and can then modify it.
    """
    def _wrapper(function_to_mock: Callable, function_to_mock_name: str, function_hook: Callable):
        from inspect import signature

        def copy_signature(source_fct):
            """Decorator used to mock a function signature."""
            def copy(target_fct):
                target_fct.__signature__ = signature(source_fct)
                return target_fct
            return copy

        @copy_signature(function_to_mock)
        def mocked_function(*args, **kwds):
            """A function with the same signature as 'function_to_mock', that calls it and concatenate the results into
            'function_hook', returning the final result."""
            # assert that arguments are correct: this improve clarity of eventual errors
            signature(mocked_function).bind(*args, **kwds)
            # now concatenate the original function with the hook and return it
            return function_hook(function_to_mock(*args, **kwds))

        # now actually mock the function_to_mock
        mocker.patch(function_to_mock_name, side_effect=mocked_function)
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
