"""
Top level module for dynaddrmgr application.

Classes:
    FakedProcessResult
    FirewallHandler
"""
import tempfile
from logging import Logger
from pathlib import Path
from typing import List, NoReturn

from wtforglib.kinds import StrAnyDict

from dynaddrmgr.app import DynAddrMgr
from dynaddrmgr.dynhost import DynamicHost
from dynaddrmgr.rule import FwRule


class FirewallHandler(DynAddrMgr):  # noqa: WPS214 WPS230
    """
    Firewall handler.

    This class is responsible for handling common firewall actions.
    """

    logger: Logger
    debug: bool
    noop: bool
    test: bool
    verbose: bool
    dynamic_hosts: List[DynamicHost]
    before_rules: List[FwRule]
    new_rules: List[FwRule]

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
        self.dynamic_hosts = []
        self.before_rules = []
        self.new_rules = []

    def unhandled(self, action: str) -> NoReturn:
        """Raises NotImplementedError."""
        raise NotImplementedError(
            "class {0} doesn't handle a file {1}!".format(
                self.__class__.__name__,
                action,
            ),
        )

    def manage_rules(self) -> int:
        """Manage firewall rules.

        Returns
        -------
        int
            exit_code

        Raises
        ------
        KeyError
            When dynamic_hosts_open_ports not in self.config
        """
        dynhosts = self.config.get("dynamic_hosts_open_ports")
        if dynhosts is None:
            raise KeyError("dynamic_hosts_open_ports key is required in configuration")
        return self._exec(dynhosts)

    def _exec(self, dynhosts: List[StrAnyDict]) -> int:
        """
        Run FirewallHandler.

        Returns:
            int: Exit code.
        """
        if not self._validate_hosts(dynhosts):
            return 1
        errors = self._exec_setup()
        for host in self.dynamic_hosts:  # noqa: WPS519
            errors += self._exec_host(host)
        errors += self._reconcile_rules()
        errors += self._exec_cleanup()
        return errors

    def _reconcile_rules(self) -> int:
        """
        Reconcile rules.

        Returns:
            int: Exit code.
        """
        errors = 0
        for nr in self.new_rules:
            for br in self.before_rules:
                if nr == br:
                    nr.status = 1  # matched
                    br.status = 1  # matched
                    self.logger.debug(
                        "Skipping rule %s because it is already in the before list.",  # noqa: WPS323 E501
                        nr,
                    )
                    break
        errors += self._delete_unmatched_rules()
        errors += self._add_unmatched_rules()
        self._save_before_after_rules()
        return errors

    def _delete_unmatched_rules(self) -> int:
        """Delete unmatched rules (Abstract Function)."""
        self.unhandled("_delete_unmatched_rules")

    def _add_unmatched_rules(self) -> int:
        """Add unmatched rules (Abstract Function)."""
        self.unhandled("_add_unmatched_rules")

    def _save_before_after_rules(self) -> None:
        """Write rules to /tmp/dynaddrmgr."""
        if self.debug:
            bug_dir = Path(tempfile.gettempdir()) / "dynaddrmgr"
            bug_dir.mkdir(mode=0o750, parents=False, exist_ok=True)  # noqa: WPS432
            with open(bug_dir / "before.rules", "w") as fbefore:
                for brule in self.before_rules:
                    print(brule, file=fbefore)
            with open(bug_dir / "new.rules", "w") as fnew:
                for rule in self.new_rules:
                    print(rule, file=fnew)

    def _exec_host(self, host: DynamicHost) -> int:
        """Open ports for host if required.

        Parameters
        ----------
        host : DynamicHost
            Host to open ports for

        Returns
        -------
            int: Exit code.
        """
        ips = self._lookup_host(host.name, host.ipv4, host.ipv6, host.ipv6net)
        if ips:
            self.new_rules.extend(host.rules(ips))
        else:
            return 1
        return 0

    def _exec_setup(self) -> int:
        """Setup before execute (Abstract Function)."""
        self.unhandled("_exec_setup")

    def _exec_cleanup(self) -> int:
        """Cleanup after execute (Abstract Function)."""
        self.unhandled("_exec_cleanup")

    def _validate_hosts(self, dynhosts: List[StrAnyDict]) -> bool:
        """
        Validate configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        for host_info in dynhosts:
            self.dynamic_hosts.append(DynamicHost(host_info))
        return True
