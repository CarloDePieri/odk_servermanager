import odk_servermanager.sm as sm
from conftest import test_folder_structure_path
from os.path import islink, isfile, join


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
