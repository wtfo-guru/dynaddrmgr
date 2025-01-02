"""Test level module for dynaddrmgr."""

import pytest
import testfixtures
from click.testing import CliRunner

from dynaddrmgr import dynrules
from dynaddrmgr.constants import VERSION

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

TSTATUS = """Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    174.24.93.102              # 22/tcp cosprings.teknofile.net
[ 2] 22/tcp                     ALLOW IN    24.48.209.165              # 22/tcp dynpr.wtforg.net
[ 3] 2666/tcp                   ALLOW IN    Anywhere
[ 4] 5432/tcp                   ALLOW IN    24.48.209.165              # 5432/tcp dynpr.wtforg.net
[ 5] 5432/tcp                   ALLOW IN    174.24.93.102              # 5432/tcp cosprings.teknofile.net
[ 6] 3306/tcp                   ALLOW IN    24.48.209.165              # 3306/tcp dynpr.wtforg.net
[ 7] 33060/tcp                  ALLOW IN    24.48.209.165              # 33060/tcp dynpr.wtforg.net
[ 8] 33060/tcp                  ALLOW IN    174.24.93.102              # 33060/tcp cosprings.teknofile.net
[ 9] 3306/tcp                   ALLOW IN    174.24.93.102              # 3306/tcp cosprings.teknofile.net
[10] 2666/tcp (v6)              ALLOW IN    Anywhere (v6)
[11] 33060/tcp                  ALLOW IN    2605:ba00:6108:633::/64    # 33060/tcp dynpr.wtforg.net
[12] 3306/tcp                   ALLOW IN    2605:ba00:6108:633::/64    # 3306/tcp dynpr.wtforg.net
[13] 5432/tcp                   ALLOW IN    2605:ba00:6108:633::/64    # 5432/tcp dynpr.wtforg.net
"""  # noqa: E501


@pytest.fixture
def runner():
    """Fixture to create a test runner."""
    return CliRunner()


def test_dynrules_version(runner):
    """Test version option."""
    test_result = runner.invoke(dynrules.main, ["--version"])
    assert not test_result.exception
    assert test_result.exit_code == 0
    assert test_result.output.strip() == "main, version {0}".format(VERSION)


def test_dynrules_help(runner):
    """Test help option."""
    test_result = runner.invoke(dynrules.main, ["-h"])  # verifies the short context
    assert test_result.exit_code == 0
    assert not test_result.exception
    testfixtures.compare(HELPTXT, test_result.output)
