from os import getcwd
from os.path import join
from unittest.mock import call

import pytest

from run import parse_cmdline, run


class TestWhenParsingCmdLine:
    """Test: When parsing cmd line..."""

    def test_should_recognize_the_manage_parameter_when_present(self, mocker):
        """When parsing cmd line should recognize the manage parameter when present."""
        mocker.patch("sys.argv", ["run.py", "--manage", "config.ini"])
        opts = parse_cmdline()
        abs_config_file = join(getcwd(), "config.ini")
        assert opts["config_file"] == abs_config_file
        assert opts["op"] == "manage"

    def test_should_recognize_a_manage_parameter_with_an_absolute_path(self, mocker):
        """When parsing cmd line should recognize a manage parameter with an absolute path."""
        abs_config_file = join(getcwd(), "config.ini")
        mocker.patch("sys.argv", ["run.py", "--manage", abs_config_file])
        opts = parse_cmdline()
        assert opts["config_file"] == abs_config_file
        assert opts["op"] == "manage"

    def test_b_and_m_should_be_mutually_exclusive(self, mocker):
        """When parsing cmd line -b and -m should be mutually exclusive."""
        mocker.patch("sys.argv", ["run.py", "-m", "-b"])
        with pytest.raises(SystemExit, match="2"):
            parse_cmdline()

    def test_bootstrap_should_accept_an_argument(self, mocker):
        """When parsing cmd line bootstrap should accept an argument."""
        abs_config_file = join(getcwd(), "config.ini")
        mocker.patch("sys.argv", ["run.py", "--bootstrap", abs_config_file])
        opts = parse_cmdline()
        assert opts["config_file"] == abs_config_file
        assert opts["op"] == "bootstrap"

    def test_should_not_accept_no_argument_with_bootstrap_or_manage(self, mocker):
        """When parsing cmd line should not accept no argument with bootstrap or manage."""
        mocker.patch("sys.argv", ["run.py", "--bootstrap"])
        with pytest.raises(SystemExit, match="2"):
            parse_cmdline()
        mocker.patch("sys.argv", ["run.py", "--manage"])
        with pytest.raises(SystemExit, match="2"):
            parse_cmdline()

    def test_either_b_or_m_should_be_provided(self, mocker):
        """When parsing cmd line either -b or -m should be provided."""
        mocker.patch("sys.argv", ["run.py"])
        with pytest.raises(SystemExit, match="2"):
            parse_cmdline()

    def test__config_should_still_work(self, mocker):
        """When parsing cmd line --config should still work."""
        abs_config_file = join(getcwd(), "config.ini")
        mocker.patch("sys.argv", ["run.py", "--config", abs_config_file])
        opts = parse_cmdline()
        assert opts["config_file"] == abs_config_file
        assert opts["op"] == "manage"


class TestWhenRunningTheTool:
    """Test: When running the tool..."""

    def test_should_call_manage_when_so_instructed(self, mocker):
        """When running the tool should call manage when so instructed."""
        abs_config_file = join(getcwd(), "config.ini")
        mocker.patch("sys.argv", ["run.py", "--manage", abs_config_file])
        sm = mocker.patch("run.ServerManager", autospec=True)
        run()
        # check that ServerManager has been created
        sm.assert_called_once()
        # check that manage_instance has been called correctly
        assert call().manage_instance(abs_config_file) in sm.method_calls

    def test_it_should_pick_up_debug_flags(self, mocker):
        """When running the tool it should pick up debug flags."""
        abs_config_file = join(getcwd(), "config.ini")
        mocker.patch("sys.argv", ["run.py", "--manage", abs_config_file, "--debug-logs-path", "this_file"])
        sm = mocker.patch("run.ServerManager", autospec=True)
        run()
        sm.assert_called_once_with(debug_logs_path="this_file")

    def test_should_call_bootstrap_with_a_config_file_when_instructed_to_do_so(self, mocker):
        """When running the tool should call bootstrap with a config file when instructed to do so."""
        abs_config_file = join(getcwd(), "config.ini")
        mocker.patch("sys.argv", ["run.py", "--bootstrap", abs_config_file])
        sm = mocker.patch("run.ServerManager", autospec=True)
        run()
        sm.assert_called_once()
        assert call().bootstrap(abs_config_file) in sm.method_calls
