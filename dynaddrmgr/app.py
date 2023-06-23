"""
Top level module for dynaddrmgr application.

Classes:
    DynAddrMgr

Misc variables:
    APPNM
"""
import subprocess  # noqa: S404
import sys
from typing import List, Tuple, Union

from dns.exception import DNSException
from nslookup import DNSresponse, Nslookup
from wtforglib.ipaddress_foos import ipv6_to_netprefix, is_ipv6_address
from wtforglib.kinds import StrAnyDict
from wtforglib.scribe import Scribe

APPNM = "dynaddrmgr"


class FakedProcessResult(object):
    """Faked process result."""

    stdout: str
    stderr: str
    returncode: int

    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0) -> None:
        """Creates a fake process result.

        Parameters
        ----------
        stdout : str
            Fake stdout
        stderr : str
            Fake stderr
        returncode : int
            Fake returcode
        """
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


if sys.version_info >= (3, 9):
    WtfProcessResult = Union[subprocess.CompletedProcess[str], FakedProcessResult]
else:
    WtfProcessResult = Union[subprocess.CompletedProcess, FakedProcessResult]


class DynAddrMgr(Scribe):
    """App class represents the main dynaddrmgr application."""

    config: StrAnyDict
    debug: bool
    test: bool
    verbose: bool
    dns: Nslookup

    def __init__(self, config: StrAnyDict, **kwargs):  # noqa: WPS210
        """Initialize DynAddrMgr application object.

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
        self.dns = Nslookup()
        self.config = config
        self.debug = kwargs.get("debug", False)
        self.noop = kwargs.get("noop", False)
        self.test = kwargs.get("test", False)
        self.verbose = kwargs.get("verbose", False)
        logfn = self.config.get("logfile", "")
        syslognm = APPNM if self.config.get("syslog", False) else ""
        screen = self.debug or self.test or self.verbose
        if not logfn and not syslognm and not screen:
            syslognm = APPNM
        if self.debug or self.test:
            level = "debug"
        elif self.verbose:
            level = "info"
        else:
            level = "warn"
        super().__init__(
            name=APPNM,
            level=level,
            logfn=logfn,
            syslognm=syslognm,
            screen=screen,
        )

    def _six_to_net(self, prefix_len: int, ips: List[str]) -> Tuple[str, ...]:
        """Return a tuple of ip source where ip addresses are converted to networks.

        Parameters
        ----------
        prefix_len : int
            Prefix length of ipv6 networks
        ips : List[str]
            List of IP addresses to convert if needed

        Returns
        -------
        Tuple[str, ...]
            List of converted addresses
        """
        converted: List[str] = []
        for ip in ips:
            if is_ipv6_address(ip):
                converted.append(ipv6_to_netprefix(ip, prefix_len))
            else:
                converted.append(ip)
        return tuple(converted)

    def _lookup_host(  # noqa: WPS231
        self,
        name: str,
        ipv4: bool,
        ipv6: bool,
        ipv6net: int = 0,
    ) -> Tuple[str, ...]:
        """Retrun a unique list of IP source strings.

        Parameters
        ----------
        name : str
            Host name
        ipv4 : bool
            Lookup ipv4 flag
        ipv6 : bool
            Lookup ipv6 flag
        ipv6net : int
            Prefix length if ipv6 addreses represent networks

        Returns
        -------
        Tuple[str, ...]
            Unique list of IP source strings

        Raises
        ------
        DNSException
            If lookup failed
        """
        ips: DNSresponse
        if ipv4 and ipv6:
            ips = self.dns.dns_lookup_all(name)
        elif ipv4:
            ips = self.dns.dns_lookup(name)
        elif ipv6:
            ips = self.dns.dns_lookup6(name)
        if ips.answer:
            first_set = set(ips.answer)
            if ipv6net and ipv6:
                return self._six_to_net(ipv6net, list(first_set))
            return tuple(first_set)
        raise DNSException(  # type: ignore [no-untyped-call]
            "'{0}' name not found.!!!".format(name),
        )

    def _run_command(
        self,
        args: Tuple[str, ...],
        **kwargs,
    ) -> WtfProcessResult:
        """Runs commands specified by args."""
        always = kwargs.get("always", False)
        check = kwargs.get("check", True)
        cmd_str = "{0}".format(" ".join(args))
        if not always and self.noop:
            print("noex: {0}".format(cmd_str))
            return FakedProcessResult()
        self.logger.info("ex: {0}".format(cmd_str))
        return subprocess.run(
            args,
            check=check,
            shell=False,  # noqa: S603
            capture_output=True,
            encoding="utf-8",
        )
