import pytest

import odk_servermanager.sm as sm
from conftest import test_folder_structure_path
from os.path import islink, isfile, isdir, join


class TestSymlinkFunction:
    """Test: symlink function..."""

    def test_should_create_a_symlink(self, reset_folder_structure):
        """Symlink function should create a symlink."""
        test_path = test_folder_structure_path()
        src = join(test_path, "TestFolder1")
        dest = join(test_path, "__server__TestServer0", "TestFolder1")
        sm.symlink(src, dest)
        assert islink(dest)
        assert isfile(join(dest, "testFile1.txt"))


class TestCreateInstance:
    """Test: create instance..."""
    test_path = test_folder_structure_path()

    def test_should_create_a_new_folder_with_a_given_name(self, reset_folder_structure):
        """Create instance should create a new folder with a given name."""
        server_name = "TestServer1"
        sm.new_server_folder(server_name, self.test_path)
        assert isdir(join(self.test_path, "__server__" + server_name))

    def test_should_raise_an_error_with_an_already_existing_server_instance(self, reset_folder_structure):
        """Create instance should raise an error with an already existing server instance."""
        server_name = "TestServer0"
        from odk_servermanager.sm import DuplicateServerName
        with pytest.raises(DuplicateServerName) as err:
            sm.new_server_folder(server_name, self.test_path)

    def test_should_symlink_and_create_all_needed_stuff_from_the_main_folder(self, reset_folder_structure):
        """Create instance should symlink and create all needed stuff from the main folder."""
        server_name = "TestServer0"
        server_folder = join(self.test_path, "__server__" + server_name)
        sm.prepare_server_core(server_name, self.test_path)
        # Check that it didn't copy over the wrong stuff
        assert not isdir(join(server_folder, "!Workshop"))
        assert not isdir(join(server_folder, "__server__TestServer0"))
        # Check all symlink
        assert islink(join(server_folder, "TestFolder1"))
        assert islink(join(server_folder, "TestFolder2"))
        assert islink(join(server_folder, "testFile0.txt"))
        assert islink(join(server_folder, "testFile3.txt"))
        assert isfile(join(server_folder, "TestFolder1", "testFile1.txt"))
        assert isfile(join(server_folder, "TestFolder2", "testFile2.txt"))
        # Check folders
        keys_folder = join(server_folder, "Keys")
        mods_linked_folder = join(server_folder, "!Mods_linked")
        mods_copied_folder = join(server_folder, "!Mods_copied")
        assert isdir(keys_folder) and not islink(keys_folder)
        assert isdir(mods_copied_folder) and not islink(mods_copied_folder)
        assert isdir(mods_linked_folder) and not islink(mods_linked_folder)
