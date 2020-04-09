from os import mkdir

import pytest

from conftest import test_folder_structure_path, test_resources, touch
from os.path import islink, isfile, join, abspath

from odk_servermanager.utils import symlink, compile_from_template, symlink_everything_from_folder
from odksm_test import ODKSMTest


class TestSymlinkFunction:
    """Test: symlink function..."""

    def test_should_create_a_symlink(self, reset_folder_structure):
        """Symlink function should create a symlink."""
        test_path = test_folder_structure_path()
        src = join(test_path, "TestFolder1")
        dest = join(test_path, "__server__TestServer0", "TestFolder1")
        symlink(src, dest)
        assert islink(dest)
        assert isfile(join(dest, "testFile1.txt"))

    def test_should_work_on_old_win(self, reset_folder_structure, mocker, monkeypatch):
        """Symlink function should work on old win."""
        mocker.patch("os.symlink", "")  # disable modern symlink
        test_path = test_folder_structure_path()
        src = join(test_path, "TestFolder1")
        dest = join(test_path, "__server__TestServer0", "TestFolder1")
        symlink(src, dest)
        assert islink(dest)
        assert isfile(join(dest, "testFile1.txt"))
        with pytest.raises(OSError):
            symlink(src, dest)  # check that errors correctly


class TestCompileFromTemplate(ODKSMTest):
    """Test: Compile from template..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestCompileFromTemplate setup"""
        template_file = abspath(join(test_resources, "template.txt"))
        with open(template_file, "r") as f:
            request.cls.template_file_content = f.read()
        request.cls.compiled_file = join(test_folder_structure_path(), "compiled.ini")

    def test_should_output_the_file(self, reset_folder_structure):
        """Compile from template should output the file."""
        compile_from_template(self.template_file_content, self.compiled_file, {})
        assert isfile(self.compiled_file)

    def test_should_return_the_compiled_file(self, reset_folder_structure):
        """Compile from template should return the compiled file."""
        target = "TITLE\nThis is a DESC."
        settings = {"title": "TITLE", "description": "DESC"}
        compile_from_template(self.template_file_content, self.compiled_file, settings)
        with open(self.compiled_file, "r") as f:
            assert f.read() == target


class TestSymlinkEverythingFromDir(ODKSMTest):
    """Test: SymlinkEverythingFromDir..."""

    @pytest.fixture(autouse=True)
    def setup(self, request, reset_folder_structure):
        """TestSymlinkEverythingFromDir setup"""
        request.cls.test_path = test_folder_structure_path()
        request.cls.target = join(self.test_path, "folderT")
        request.cls.origin = join(self.test_path, "folderA")
        mkdir(self.target)
        mkdir(self.origin)
        mkdir(join(self.origin, "folderB"))
        touch(join(self.origin, "folderB", "testA"))
        mkdir(join(self.origin, "folderC"))
        touch(join(self.origin, "folderC", "testB"))
        touch(join(self.origin, "testC"))

    def test_should_work(self, reset_folder_structure):
        """Symlink everything from dir should work."""
        symlink_everything_from_folder(self.origin, self.target)
        assert islink(join(self.target, "folderB"))
        assert islink(join(self.target, "folderC"))
        assert isfile(join(self.target, "folderB", "testA"))
        assert isfile(join(self.target, "folderC", "testB"))
        assert islink(join(self.target, "testC"))

    def test_should_accept_exceptions(self, reset_folder_structure):
        """Symlink everything from dir should accept exceptions."""
        symlink_everything_from_folder(self.origin, self.target, ["folderB"])
        assert not islink(join(self.target, "folderB"))
        assert islink(join(self.target, "folderC"))
        assert isfile(join(self.target, "folderC", "testB"))
        assert islink(join(self.target, "testC"))
