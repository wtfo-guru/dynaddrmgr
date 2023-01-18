"""
Top level module for dynaddrmgr application.

Classes:
    TemplateManager
"""
import filecmp
from os import R_OK, W_OK, access
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Tuple

from jinja2 import Template
from wtforglib.kinds import StrAnyDict
from wtforglib.versionfile import version_file

from dynaddrmgr.app import DynAddrMgr
from dynaddrmgr.wtforg import verify_directory

TmplVar = Dict[str, Tuple[str, ...]]


class TemplateManager(DynAddrMgr):  # noqa: WPS214
    """
    Template manager.

    This class is responsible for managing the templates specified
    in the configuration file.
    """

    def manage_templates(self) -> int:
        """Manage the templates specified in the configuration file.

        Returns
        -------
        int
            exit_code

        Raises
        ------
        KeyError
            When dynamic_host_templates not in self.config
        """
        dynhosttmpls: Optional[Dict[str, StrAnyDict]] = self.config.get(
            "dynamic_host_templates",
        )
        if dynhosttmpls is None:
            raise KeyError("dynamic_host_templates key is required in configuration")
        errors = 0
        for tmpl_name, tmpl_value in dynhosttmpls.items():
            if not self._verify_config_data(tmpl_name, tmpl_value):
                errors += 1
                continue
            tmpl_var: TmplVar = {}
            if not self._template_vars(tmpl_name, tmpl_value, tmpl_var):
                errors += 1
                continue
            errors += self._render_template(
                tmpl_value.get("src", ""),
                tmpl_var,
                tmpl_value.get("dest", ""),
                tmpl_value.get("backup", 0),
            )
        return errors

    def _verify_config_data(self, tmpl_name: str, tmpl_value: StrAnyDict) -> bool:
        """Verifies the configuration.

        Parameters
        ----------
        tmpl_name : str
            Name of the template
        tmpl_value : StrAnyDict
            Template values

        Returns
        -------
        bool
            True if the configuration is valid
        """
        if self._verify_template_required_keys(tmpl_name, tmpl_value):
            if self._verify_template_source(tmpl_value.get("src", "")):
                if self._verify_target(tmpl_value.get("dest", "")):
                    return True
        return False

    def _render_template(
        self,
        source: str,
        tmpl_var: TmplVar,
        dest: str,
        backup: int,
    ) -> int:
        """Render the template to the file system.

        Parameters
        ----------
        source : str
            Path to the template source file
        tmpl_var : TmplVar
            Varible to pass into template engine
        dest : str
            Path to the output file
        backup : int
            Max number of backups to keep (if any)

        Returns
        -------
        int
            exit_code
        """
        template = Template(self._read_template_source(source))
        tfile = NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=None,
            delete=False,
        )
        tfile.write(template.render(dynhost_list=tmpl_var))
        tfile.close()
        self._write_output(Path(dest), Path(tfile.name), backup)
        return 0

    def _write_output(self, dpath: Path, tpath: Path, backup: int) -> None:
        """Write output to output file, unlink temporary file.

        Parameters
        ----------
        dpath : Path
            Path to the output file
        tpath : Path
            Path to the temporary generated template file
        backup : int
            Number of backups to keep if any
        """
        if dpath.exists():
            diff = filecmp.cmp(dpath, tpath)
            exists = True
        else:
            exists = False
            diff = True
        if diff:
            if not self.noop:
                if exists:
                    self._backup_file(str(dpath), backup)
                    tpath.replace(dpath)
                else:
                    tpath.rename(dpath)
        if not self.debug:
            tpath.unlink()

    def _backup_file(self, dest: str, backup: int) -> None:
        """Backup the output before replacing.

        Parameters
        ----------
        dest : str
            Path to output file.
        backup : int
            Number of backup files to keep (if any)
        """
        if backup:
            version_file(dest, "rename", backup, debug=self.debug)

    def _read_template_source(self, source: str) -> str:
        """Retruns the template data from the given source.

        Parameters
        ----------
        source : str
            Path to the template source

        Returns
        -------
        str
            The template data
        """
        with open(source, "r") as jinja_file:
            return jinja_file.read()

    def _template_vars(
        self,
        tmpl_name: str,
        tmpl_value: StrAnyDict,
        tmpl_var: TmplVar,
    ) -> bool:
        """Lookup ip sources for template hosts."""
        hosts: List[StrAnyDict] = tmpl_value.get("hosts", {})
        for host in hosts:
            name = host.get("name", "")
            if name:
                tmpl_var[name] = self._lookup_host(
                    name,
                    host.get("ipv4", True),
                    host.get("ipv6", True),
                    host.get("ipv6net", 0),
                )
            else:
                self.logger.error(
                    "Template {0} hosts name not specified!!".format(tmpl_name),
                )
                return False
        return True

    def _verify_template_required_keys(
        self,
        tmpl_name: str,
        tmpl_value: StrAnyDict,
    ) -> bool:
        """Verify that the template required keys exist."""
        for key in ("src", "dest", "hosts"):
            kv = tmpl_value.get(key)
            if kv is None:
                self.logger.error(
                    "Template {0} does not have a {1} key!!".format(tmpl_name, key),
                )
                return False
        return True

    def _verify_target(self, dest: str) -> bool:
        """Verifies the output file.

        Parameters
        ----------
        dest : str
            Path to the output file

        Returns
        -------
        bool
            True if target directory exists and writable and file does not exist
            True if target exists, is a file, and writable
        """
        dspec = Path(dest)
        if dspec.exists():
            if not dspec.is_file():
                self.logger.error("Template dest '{0}' not a file!!".format(dest))
                return False
            if not access(dspec, W_OK):
                self.logger.error("Template dest '{0}' not readable!!".format(dest))
                return False
        else:
            return self._verify_target_directory(dspec.parent)
        return True

    def _verify_target_directory(self, pspec: Path) -> bool:
        """Verifies the target directory.

        Parameters
        ----------
        pspec : Path
            Path to the target directory

        Returns
        -------
        bool
            True if exists, is directory and is writable.
        """
        retval, error_message = verify_directory(pspec)
        if not retval:
            self.logger.error(error_message)
        return retval

    def _verify_template_source(self, source: str) -> bool:
        """Verifies the template source.

        Parameters
        ----------
        source : str
            Path to the template source

        Returns
        -------
        bool
            True if source exists, is a file, is readable
        """
        spec = Path(source)
        if not spec.exists():
            self.logger.error("Template src '{0}' not found!!".format(source))
            return False
        if not spec.is_file():
            self.logger.error("Template src '{0}' not a file!!".format(source))
            return False
        if not access(spec, R_OK):
            self.logger.error("Template src '{0}' not readable!!".format(source))
            return False
        return True
