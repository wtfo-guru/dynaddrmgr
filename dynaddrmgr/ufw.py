"""
Top level module for dynaddrmgr application.

Classes:
    UfwHandler

Misc variables:
    TEST_STATUS
"""
import re
import tempfile
from pathlib import Path
from typing import List, Tuple

from wtforglib.kinds import StrAnyDict

from dynaddrmgr.fwhdlr import FirewallHandler
from dynaddrmgr.rule import FwRule

TEST_STATUS = """Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    174.24.93.102              # 22/tcp-cosprings.teknofile.net (dynaddrmgr)
[ 2] 22/tcp                     ALLOW IN    24.48.209.165              # 22/tcp-dynpr.wtforg.net (dynaddrmgr)
[ 3] 2666/tcp                   ALLOW IN    Anywhere
[ 4] 5432/tcp                   ALLOW IN    24.48.209.165              # 5432/tcp-dynpr.wtforg.net (dynaddrmgr)
[ 5] 5432/tcp                   ALLOW IN    174.24.93.102              # 5432/tcp-cosprings.teknofile.net (dynaddrmgr)
[ 6] 3306/tcp                   ALLOW IN    24.48.209.165              # 3306/tcp-dynpr.wtforg.net (dynaddrmgr)
[ 7] 33060/tcp                  ALLOW IN    24.48.209.165              # 33060/tcp-dynpr.wtforg.net (dynaddrmgr)
[ 8] 33060/tcp                  ALLOW IN    174.24.93.102              # 33060/tcp-cosprings.teknofile.net (dynaddrmgr)
[ 9] 3306/tcp                   ALLOW IN    174.24.93.102              # 3306/tcp-cosprings.teknofile.net (dynaddrmgr)
[10] 2666/tcp (v6)              ALLOW IN    Anywhere (v6)
[11] 33060/tcp                  ALLOW IN    2605:ba00:6108:633::/64    # 33060/tcp-dynpr.wtforg.net (dynaddrmgr)
[12] 3306/tcp                   ALLOW IN    2605:ba00:6108:633::/64    # 3306/tcp-dynpr.wtforg.net (dynaddrmgr)
[13] 5432/tcp                   ALLOW IN    2605:ba00:6108:633::/64    # 5432/tcp-dynpr.wtforg.net (dynaddrmgr)
"""  # noqa: E501

UFW = "ufw"


class UfwHandler(FirewallHandler):  # noqa: WPS214
    """UFW handler class."""

    regex_port = re.compile(r"(\d+)")
    regex_proto = re.compile(r"\d+\/([a-z]+)")
    regex_status = re.compile(r"Status:\s+([a-zA-Z]+)")
    regex_stat_line = re.compile(
        r"\[([ 0-9]+)\]\s+([/0-9tcpud]+)\s+ALLOW IN\s+([.:/a-f0-9]+)\s+#(.*)$",
    )

    status: str
    before: str
    after: str

    def __init__(self, config: StrAnyDict, **kwargs) -> None:
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
        before_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".before",
            delete=False,
        )
        self.before = before_file.name
        if self.test:
            status = TEST_STATUS
        else:
            cmd_result = self._run_command((UFW, "status", "numbered"), always=True)
            status = cmd_result.stdout
        before_file.write(status)
        before_file.close()
        return self._parse_status(status)

    def _exec_cleanup(self) -> int:
        """Cleanup after execute."""
        after_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".after",
            delete=False,
        )
        self.after = after_file.name
        if self.test:
            status = TEST_STATUS
        else:
            cmd_result = self._run_command((UFW, "status", "numbered"), always=True)
            status = cmd_result.stdout
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
                "ufw status must be 'active' not '{0}".format(self.status),
            )
        self.status = status

    def _parse_status(self, ufwstatus: str) -> int:  # noqa: WPS231 C901
        """Parse ufw status output."""
        for line in ufwstatus.splitlines():
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
            mm = re.match(self.regex_stat_line, line)
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
        self.logger.debug("Before rules: {0}".format(len(self.before_rules)))
        return 0

    def _parse_port_protocol(self, field: str) -> Tuple[str, str]:
        """
        Parse a port/protocol field.

        :param field: The port/protocol field.
        :return: A tuple containing the port and protocol.
        """
        port = ""
        proto = ""
        match = re.match(self.regex_port, field)
        if match:
            port = match.group(1)
            match = re.match(self.regex_proto, field)
            if match:
                proto = match.group(1)
                if not re.match("tcp|udp$", proto):
                    raise ValueError("Invalid protocol: {0}".format(proto))
        return (port, proto)

    def _delete_unmatched_rules(self) -> int:
        """Delete unmatched rules."""
        errors = 0
        indices: List[int] = []
        for rule in self.before_rules:
            if not rule.status:
                if rule.index > 0:
                    indices.append(rule.index)
                else:
                    self.logger.error(
                        "Skipping rule %s because index is less than one.",  # noqa: WPS323 E501
                        rule,
                    )
        for idx in sorted(indices, key=int, reverse=True):
            cmd_result = self._run_command((UFW, "--force", "delete", str(idx)))
            if cmd_result.returncode != 0:
                errors += 1
        return errors

    def _add_unmatched_rules(self) -> int:
        """Add unmatched rules."""
        errors = 0
        for rule in self.new_rules:
            if rule.status:
                continue  # skipping matched rules
            if rule.protocol:
                # ufw allow from 174.24.93.102 to any port 33060 proto tcp
                # comment '33060/tcp cosprings.teknofile.net'
                cmd_result = self._run_command(
                    (
                        UFW,
                        "allow",
                        "from",
                        str(rule.ipaddr),
                        "to",
                        "any",
                        "port",
                        str(rule.port),
                        "proto",
                        rule.protocol,
                        "comment",
                        rule.comment,
                    ),
                )
            else:
                cmd_result = self._run_command(
                    (
                        UFW,
                        "allow",
                        "from",
                        str(rule.ipaddr),
                        "to",
                        "any",
                        "port",
                        str(rule.port),
                        "comment",
                        rule.comment,
                    ),
                )
            if cmd_result.returncode != 0:
                errors += 1
        return errors
