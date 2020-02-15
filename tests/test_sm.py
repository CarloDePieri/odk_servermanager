import pytest

import odk_servermanager.sm as sm
from conftest import test_folder_structure_path
import os


class TestSymlinkFunction:
    """Test: symlink function..."""

    def test_should_create_a_symlink(self, reset_folder_structure):
        """Symlink function should create a symlink."""
        test_path = test_folder_structure_path()
        src = os.path.join(test_path, "TestFolder1")
        dest = os.path.join(test_path, "__server__TestServer0", "TestFolder1")
        sm.symlink(src, dest)
        assert os.path.islink(dest)
        assert os.path.isfile(os.path.join(dest, "testFile1.txt"))


class TestCreateInstance:
    """Test: create instance..."""

    def test_should_create_a_new_folder_with_a_given_name(self, reset_folder_structure):
        """Create instance should create a new folder with a given name."""
        test_path = test_folder_structure_path()
        server_name = "TestServer1"
        sm.new_server_folder(server_name, test_path)
        assert os.path.isdir(os.path.join(test_path, "__server__" + server_name))

    def test_should_raise_an_error_with_an_already_existing_server_instance(self, reset_folder_structure):
        """Create instance should raise an error with an already existing server instance."""
        test_path = test_folder_structure_path()
        server_name = "TestServer0"
        from odk_servermanager.sm import DuplicateServerName
        with pytest.raises(DuplicateServerName) as err:
            sm.new_server_folder(server_name, test_path)

