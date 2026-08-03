"""
Top level module for dynaddrmgr application.

Classes:
    UfwHandler

Misc variables:
    TEST_STATUS
"""

import re
import sys
import tempfile
from pathlib import Path

from wtforglib.kinds import StrAnyDict

from dynaddrmgr.app import WtfProcessResult
from dynaddrmgr.constants import TEST_DIR
from dynaddrmgr.fwhdlr import FirewallHandler
from dynaddrmgr.rule import FwRule

UFW = "ufw"


class UfwHandler(FirewallHandler):  # noqa: WPS214
    """UFW handler class."""

    regex_port_proto = re.compile(r"(\d+)\/([a-z]+)")
    regex_app = re.compile(r"([ a-zA-Z]+)")
    regex_status = re.compile(r"Status:\s+([a-zA-Z]+)")
    regex_app_line = re.compile(
        r"\[\s*([0-9]+)\]\s+([ /0-9a-zA-Z()]+)\s+ALLOW IN\s+([.:/a-f0-9]+)\s+#(.*)$",
    )

    status: str
    before: str
    after: str

    def __init__(self, config: StrAnyDict, **kwargs: bool) -> None:
        """Initialize FirewallHandler.

        Parameters
        ----------
        config : str
            Path to configuration file.

        Keyword arguments
        -----------------
        debug : bool
        noop : bool
        test : bool
        verbose : bool
        """
        super().__init__(config, **kwargs)
        self.status = ""
        self.before = ""
        self.after = ""

    def _exec_setup(self) -> int:
        """Setup before execute."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".before",
            delete=False,
        ) as before_file:
            self.before = before_file.name
            status = self._get_status(before_file.name)
            before_file.write(status)
            before_file.close()
        return self._parse_status(status)

    def _get_status(self, filename: str) -> str:
        """Get current status."""
        if self.test:
            td = Path(TEST_DIR)
            if td.is_dir():
                return self._get_test_status(td, filename)
        cmd_result = self._run_command((UFW, "status", "numbered"), always=True)
        return cmd_result.stdout

    def _get_test_status(self, td: Path, filename: str) -> str:
        """Read status from a test file."""
        if "pytest" in sys.modules:
            if filename.endswith(".before"):
                tfn = Path(td / "ufw.status.before")
            elif filename.endswith(".after"):
                tfn = Path(td / "ufw.status.after")
        else:
            tfn = Path(td / "ufw.status")
        return tfn.read_text()

    def _exec_cleanup(self) -> int:
        """Cleanup after execute."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".after",
            delete=False,
        ) as after_file:
            self.after = after_file.name
            status = self._get_status(after_file.name)
            after_file.write(status)
            after_file.close()
            cmd_args = ("diff", "-uN", self.before, self.after)
            cmd_result = self._run_command(cmd_args, check=False)
            if cmd_result.returncode > 0:
                if cmd_result.stdout:
                    print(cmd_result.stdout)
                if cmd_result.returncode > 1 and cmd_result.stderr:
                    print(cmd_result.stderr)
            if not self.debug:
                Path(self.before).unlink()
                Path(self.after).unlink()
            return 0 if cmd_result.returncode < 2 else cmd_result.returncode

    def _validate_ufw_status(self, status: str) -> None:
        """Validate UFW status.

        Parameters
        ----------
        status : str
            Ufw status

        Raises
        ------
        RuntimeError
            If status is not valid
        """
        if status != "active":
            raise RuntimeError(
                f"ufw status must be 'active' not '{self.status}",
            )
        self.status = status

    def _parse_status(self, ufw_status: str) -> int:  # noqa: WPS231 C901
        """Parse ufw status output."""
        for line in ufw_status.splitlines():
            line = line.strip()
            if not line:
                continue
            if not self.status:
                mm = re.match(self.regex_status, line)
                if mm:
                    self._validate_ufw_status(mm.group(1).lower())
                continue
            if "(dynaddrmgr)" not in line:  # we only care about our rules
                continue
            mm = re.match(self.regex_app_line, line)
            if not mm:
                continue
            port, protocol = self._parse_port_protocol(mm.group(2).strip())
            self.before_rules.append(
                FwRule(
                    port,
                    protocol,
                    mm.group(3).strip(),
                    mm.group(4).strip(),
                    mm.group(1).strip(),
                ),
            )
        self.logger.debug(f"Before rules: {len(self.before_rules)}")
        return 0

    def _parse_port_protocol(self, field: str) -> tuple[str, str]:
        """
        Parse a port/protocol field.

        :param field: The port/protocol field.
        :return: A tuple containing the port and protocol.
        """
        port = ""
        proto = ""
        mm = re.match(self.regex_port_proto, field)
        if mm:
            port = mm.group(1)
            proto = mm.group(2)
            if not re.match("tcp|udp$", proto):
                raise ValueError(f"Invalid protocol: {proto}")
        else:
            field = field.replace("(v6)", "").strip()
            mm = re.match(self.regex_app, field)
            if mm:
                port = mm.group(1)
                proto = "app"
        return (port, proto)

    def _delete_unmatched_rules(self) -> int:
        """Delete unmatched rules."""
        errors = 0
        indices: list[int] = []
        for rule in self.before_rules:
            if not rule.status:
                if rule.index > 0:
                    indices.append(rule.index)
                else:
                    self.logger.error(
                        f"Skipping rule {rule} because index is < 1.",
                    )
        for idx in sorted(indices, key=int, reverse=True):
            cmd_result = self._run_command((UFW, "--force", "delete", str(idx)))
            if cmd_result.returncode != 0:
                errors += 1
        return errors

    def _run_app_command(self, rule: FwRule) -> WtfProcessResult:
        """Run app command.

        Parameters
        ----------
        rule : FwRule
            The rule to run

        Returns
        -------
        WtfProcessResult
            The result of the command
        """
        return self._run_command(
            (
                UFW,
                "allow",
                "from",
                str(rule.ipaddr),
                "to",
                "any",
                "app",
                str(rule.allow),
                "comment",
                rule.comment,
            ),
        )

    def _run_port_command(self, rule: FwRule) -> WtfProcessResult:
        """Run port command.

        Parameters
        ----------
        rule : FwRule
            The rule to run

        Returns
        -------
        WtfProcessResult
            The result of the command
        """
        if rule.protocol:
            return self._run_command(
                (
                    UFW,
                    "allow",
                    "from",
                    str(rule.ipaddr),
                    "to",
                    "any",
                    "port",
                    str(rule.allow),
                    "proto",
                    rule.protocol,
                    "comment",
                    rule.comment,
                ),
            )
        return self._run_command(
            (
                UFW,
                "allow",
                "from",
                str(rule.ipaddr),
                "to",
                "any",
                "port",
                str(rule.allow),
                "comment",
                rule.comment,
            ),
        )

    def _add_unmatched_rules(self) -> int:
        """Add unmatched rules."""
        errors = 0
        for rule in self.new_rules:
            if rule.status:
                continue  # skipping matched rules
            if rule.protocol:
                # ufw allow from 174.24.93.102 to any port 33060 proto tcp
                # comment '33060/tcp cosprings.teknofile.net'
                if rule.protocol == "app":
                    cmd_result = self._run_app_command(rule)
                else:
                    cmd_result = self._run_port_command(rule)
            if cmd_result.returncode != 0:
                errors += 1
        return errors
