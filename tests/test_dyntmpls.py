"""Test level module for dynaddrmgr."""

import pytest
import testfixtures
from click.testing import CliRunner

from dynaddrmgr import VERSION, dyntmpls

HELPTXT = """Usage: main [OPTIONS]

  Main function for dynamic template manager.

Options:
  -c, --config TEXT             Specify config file
  -d, --debug / --no-debug      Specify debug mode, default: False
  -n, --noop / --no-noop        Specify noop mode, default: False
  -t, --test / --no-test        Specify test mode, default: False
  -v, --verbose / --no-verbose  Specify verbose mode, default: False
  --version                     Show the version and exit.
  -h, --help                    Show this message and exit.
"""


@pytest.fixture
def runner():
    """Fixture to create a test runner."""
    return CliRunner()


def test_dyntmpls_version(runner):
    """Test version option."""
    test_result = runner.invoke(dyntmpls.main, ["--version"])
    assert not test_result.exception
    assert test_result.exit_code == 0
    assert test_result.output.strip() == "main, version {0}".format(VERSION)


def test_dyntmpls_help(runner):
    """Test help option."""
    test_result = runner.invoke(dyntmpls.main, ["-h"])  # verifies the short context
    assert test_result.exit_code == 0
    assert not test_result.exception
    testfixtures.compare(HELPTXT, test_result.output)
