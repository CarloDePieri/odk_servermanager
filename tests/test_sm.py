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
