import pytest

from conftest import test_folder_structure_path, test_resources
from os.path import islink, isfile, join, abspath

from odk_servermanager.utils import symlink, compile_from_template
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


class TestCompileFromTemplate(ODKSMTest):
    """Test: Compile from template..."""

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestCompileFromTemplate setup"""
        request.cls.template_file = abspath(join(test_resources, "template.ini"))
        request.cls.compiled_file = join(test_folder_structure_path(), "compiled.ini")

    def test_should_output_the_file(self, reset_folder_structure):
        """Compile from template should output the file."""
        compile_from_template(self.template_file, self.compiled_file, {})
        assert isfile(self.compiled_file)

    def test_should_return_the_compiled_file(self, reset_folder_structure):
        """Compile from template should return the compiled file."""
        target = "TITLE\nThis is a DESC."
        settings = {"title": "TITLE", "description": "DESC"}
        compile_from_template(self.template_file, self.compiled_file, settings)
        with open(self.compiled_file, "r") as f:
            assert f.read() == target
