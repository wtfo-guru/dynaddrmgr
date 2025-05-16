"""Test level module for package wtfimap."""

import os
from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner
from jinja2 import Template
from pyfakefs.fake_filesystem import FakeFilesystem
from wtforglib.errors import raise_filenotfound_if
from wtforglib.functions import strtobool, unix_basename

os.environ["DYN_ADDR_MGR_ENV"] = "test"


class TrialData:  # noqa: WPS214
    """Test data class."""

    _real_data_dir: Path
    _fake_test_dir: Path
    _fake_backup_dir: Path
    _gl_pipeline: str

    def __init__(self) -> None:
        """Construct a TrialData object."""
        self._real_data_dir = Path(__file__).parent.resolve() / "data"
        self._fake_test_dir = Path("/test_data")
        self._fake_backup_dir = self._fake_test_dir / "backup"
        self._is_ci = os.getenv("CI", "false")

    def is_ci(self) -> bool:
        """Return True if running in a gitlab pipeline."""
        return strtobool(self._is_ci)

    def setup(self, ffs: FakeFilesystem) -> None:
        """Setup testing environment."""
        resolved_contents = "nameserver 8.8.4.4\nnamserver 8.8.8.8\n"
        resolv_conf = "/etc/resolv.conf"
        ffs.create_file(resolv_conf, contents=resolved_contents)
        raise_filenotfound_if(resolv_conf)

    def add_real_files(self, ffs: FakeFilesystem, base_fns: List[str]) -> Path:
        """Prepare data for a test run.

        Parameters
        ----------
        ffs : FakeFilesystem
            FakeFilesystem fixture
        base_fn : str
            Base filename of test data files
        """
        for bn in base_fns:
            real = self._real_fn(bn)
            fake = self._fake_fn(bn)
            ffs.add_real_file(real, target_path=fake)
            raise_filenotfound_if(fake)
        return self._fake_test_dir

    def add_real_template(self, ffs: FakeFilesystem, base_fn: str) -> str:
        """Prepare data for a test run.

        Parameters
        ----------
        ffs : FakeFilesystem
            FakeFilesystem fixture
        base_fn : str
            Base filename of test data files
        """
        scratch = self._real_fn(base_fn)
        fake = self._fake_fn(base_fn)
        ffs.add_real_file(scratch, target_path=fake)
        raise_filenotfound_if(fake)
        scratch = self._fake_fn(unix_basename(fake, ".j2"))
        tmpl_data = {
            "test_data_dir": str(self._fake_test_dir),
            "test_backup_dir": str(self._fake_backup_dir),
        }
        template: Template
        with open(fake, "r") as jinja_file:
            template = Template(jinja_file.read())
        ffs.create_file(scratch, contents=template.render(template_dict=tmpl_data))
        raise_filenotfound_if(scratch)
        return scratch

    def _real_fn(self, base_fn: str) -> str:
        return str(self._real_data_dir / base_fn)

    def _fake_fn(self, base_fn: str) -> str:
        return str(self._fake_test_dir / base_fn)


@pytest.fixture()  # noqa: PT001
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()  # noqa: PT001
def test_data() -> TrialData:
    return TrialData()
