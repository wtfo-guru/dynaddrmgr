"""Test level module for dynaddrmgr."""

from pathlib import Path

import testfixtures
from click.testing import CliRunner
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_subprocess.fake_process import FakeProcess

from dynaddrmgr import dynrules
from dynaddrmgr.constants import AFTER, BEFORE, VERSION

HELPTXT = """Usage: main [OPTIONS]

  Main function for dynamic firewall rule manager.

Options:
  -c, --config TEXT             Specify config file
  -d, --debug / --no-debug      Specify debug mode, default: False
  -n, --noop / --no-noop        Specify noop mode, default: False
  -t, --test / --no-test        Specify test mode, default: False
  -v, --verbose / --no-verbose  Specify verbose mode, default: False
  --version                     Show the version and exit.
  -h, --help                    Show this message and exit.
"""

TD = Path(__file__).parent.resolve() / "data"


def test_dynrules_version(runner: CliRunner) -> None:
    """Test version option."""
    test_result = runner.invoke(dynrules.main, ["--version"])
    assert not test_result.exception
    assert test_result.exit_code == 0
    assert test_result.output.strip() == "main, version {0}".format(VERSION)


def test_dynrules_help(runner: CliRunner) -> None:
    """Test help option."""
    test_result = runner.invoke(dynrules.main, ["-h"])  # verifies the short context
    assert test_result.exit_code == 0
    assert not test_result.exception
    testfixtures.compare(HELPTXT, test_result.output)


def callback_function(process) -> None:
    process.returncode = 0
    with open(TD / "ufw.status", "r") as fd:
        process.stdout = fd.read()


def test_rules(runner: CliRunner, fs: FakeFilesystem, fp: FakeProcess) -> None:
    """Test rule output."""
    cfg_fn = "{0}/dynaddrmgr.yaml".format(Path(BEFORE).parent)
    fs.add_real_file(TD / "resolv.conf", target_path="/etc/resolv.conf")
    fs.add_real_file(TD / "etc.hosts", target_path="/etc/hosts")
    fs.add_real_file(TD / "dynaddrmgr.dns", target_path=cfg_fn)
    fs.add_real_file(TD / "ufw.status.before", target_path=BEFORE)
    fs.add_real_file(TD / "ufw.status.after", target_path=AFTER)
    fp.register(["ufw", "status", "numbered"], callback=callback_function)
    test_result = runner.invoke(dynrules.main, ["-d", "-t", "-c", cfg_fn, "--noop"])
    assert not test_result.exception
    assert test_result.exit_code == 0
