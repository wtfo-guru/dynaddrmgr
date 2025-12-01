"""Test level module for dynaddrmgr."""

import testfixtures
from click.testing import CliRunner
from pyfakefs.fake_filesystem import FakeFilesystem

from dynaddrmgr import dyntmpls
from dynaddrmgr.constants import VERSION
from tests.conftest import TrialData

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


def test_dyntmpls_version(runner: CliRunner) -> None:
    """Test version option."""
    test_result = runner.invoke(dyntmpls.main, ["--version"])
    assert not test_result.exception
    assert test_result.exit_code == 0
    assert test_result.output.strip() == "main, version {0}".format(VERSION)


def test_dyntmpls_help(runner: CliRunner) -> None:
    """Test help option."""
    test_result = runner.invoke(dyntmpls.main, ["-h"])  # verifies the short context
    assert test_result.exit_code == 0
    assert not test_result.exception
    testfixtures.compare(HELPTXT, test_result.output)


def test_access_templates(
    runner: CliRunner, fs: FakeFilesystem, test_data: TrialData
) -> None:
    """Test access templates."""
    real_files = [
        "access-wtf-trusted.conf",
        "access_wtf_trusted.conf.j2",
        "00-defaults.local",
        "00-defaults-vultr.conf.j2",
    ]
    test_data.setup(fs)  # set up resolv.conf for testing
    fake_dir = test_data.add_real_files(fs, real_files)
    assert fake_dir.exists()
    cfg = test_data.add_real_template(fs, "dynaddrmgr.yaml.j2")
    test_result = runner.invoke(dyntmpls.main, ["-c", cfg, "-d", "-t"])
    assert not test_result.exception
    assert test_result.exit_code == 0
