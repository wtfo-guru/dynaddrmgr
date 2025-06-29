"""
Top level module for dynaddrmgr application.

Classes:
    DynAddrMgr

Misc variables:
    APPNM
"""

import subprocess  # noqa: S404
from ipaddress import ip_network
from typing import List, Tuple, Union

from dns.exception import DNSException
from nslookup import DNSresponse, Nslookup  # type: ignore[import-untyped]
from wtforglib.ipaddress_foos import ipv6_to_netprefix, is_ipv6_address
from wtforglib.kinds import StrAnyDict

from dynaddrmgr.singles import DailyLogger

APPNM = "dynaddrmgr"


class FakedProcessResult:
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
            Fake returncode
        """
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __repr__(self) -> str:
        args = [
            "returncode={!r}".format(self.returncode),
        ]
        if self.stdout is not None:
            args.append("stdout={!r}".format(self.stdout))
        if self.stderr is not None:
            args.append("stderr={!r}".format(self.stderr))
        return "{}({})".format(type(self).__name__, ", ".join(args))


WtfProcessResult = Union[subprocess.CompletedProcess[str], FakedProcessResult]


class DynAddrMgr:  # noqa: WPS230
    """App class represents the main dynaddrmgr application."""

    config: StrAnyDict
    debug: bool
    test: bool
    verbose: bool
    dns: Nslookup
    logger: DailyLogger

    _noop: bool

    def __init__(self, config: StrAnyDict, **kwargs: bool):  # noqa: WPS210
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
        self._noop = kwargs.get("noop", False)
        self.test = kwargs.get("test", False)
        self.verbose = kwargs.get("verbose", False)
        if self.debug:
            log_level = "DEBUG"
        elif self.verbose:
            log_level = "INFO"
        else:
            log_level = "WARNING"
        self.logger = DailyLogger(level=log_level)

    def _to_net(
        self,
        prefix_len: int,
        ips: List[str],
        ipv6net_style: str = "standard",
        ipv4net: bool = False,
    ) -> Tuple[str, ...]:
        """Return a tuple of ip source where ip addresses are converted to networks.

        Parameters
        ----------
        prefix_len : int
            Prefix length of ipv6 networks
        ips : List[str]
            List of IP addresses to convert if needed
        ipv6net_style : string
            One of standard, postfix
        ipv4net : bool
            Network notation

        Returns
        -------
        Tuple[str, ...]
            List of converted addresses
        """
        converted: List[str] = []
        for ip in ips:
            if is_ipv6_address(ip):
                converted.append(ipv6_to_netprefix(ip, prefix_len, ipv6net_style))
            elif ipv4net:
                converted.append(str(ip_network(ip)))
            else:
                converted.append(ip)
        return tuple(converted)

    def _verify_lookup_answer(  # noqa: WPS211
        self,
        name: str,
        answer: List[str],
        ipv6: bool,
        ipv6net: int = 0,
        minlen: int = 1,
        ipv6net_style: str = "standard",
        ipv4net: bool = False,
    ) -> Tuple[str, ...]:
        """Return a unique list of IP source strings.

        Parameters
        ----------
        name : str
            Name of host looked up
        answer : List[str]
            List of ip address strings
        ipv6 : bool
            Lookup ipv6 flag
        ipv6net : int
            Prefix length if ipv6 addresses represent networks
        minlen : int
            Minimum number of addresses to accept
        ipv6net_style : string
            One of standard, postfix
        ipv4net : bool
            Network notation

        Returns
        -------
        Tuple[str, ...]
            Unique list of IP source strings

        Raises
        ------
        DNSException
            If lookup failed
        """
        if answer:
            if len(answer) >= minlen:
                first_set = set(answer)
                if ipv4net or ipv6net:
                    return self._to_net(
                        ipv6net,
                        list(first_set),
                        ipv6net_style,
                        ipv4net,
                    )
                return tuple(first_set)
            raise DNSException(  # type: ignore [no-untyped-call]
                "'{0}' name expected {1} addresses.!!!".format(name, minlen),
            )
        raise DNSException(  # type: ignore [no-untyped-call]
            "'{0}' name not found.!!!".format(name),
        )

    def _lookup_host(  # noqa: WPS211
        self,
        name: str,
        ipv4: bool,
        ipv6: bool,
        ipv6net: int = 0,
        ipv6net_style: str = "standard",
        ipv4net: bool = False,
    ) -> Tuple[str, ...]:
        """Return a unique list of IP source strings.

        Parameters
        ----------
        name : str
            Host name
        ipv4 : bool
            Lookup ipv4 flag
        ipv6 : bool
            Lookup ipv6 flag
        ipv6net : int
            Prefix length if ipv6 addresses represent networks
        ipv6net_style : string
            One of standard, postfix
        ipv4net : bool
            Network notation

        Returns
        -------
        Tuple[str, ...]
            Unique list of IP source strings
        """
        ips: DNSresponse
        minlen: int = 1
        self.logger.debug("ipv6net_style: {0}".format(ipv6net_style))
        if ipv4 and ipv6:
            ips = self.dns.dns_lookup_all(name)
            minlen = 2
        elif ipv4:
            ips = self.dns.dns_lookup(name)
        elif ipv6:
            ips = self.dns.dns_lookup6(name)
        return self._verify_lookup_answer(
            name,
            ips.answer,
            ipv6,
            ipv6net,
            minlen,
            ipv6net_style,
            ipv4net,
        )

    def _run_command(
        self,
        args: Tuple[str, ...],
        **kwargs: bool,
    ) -> WtfProcessResult:
        """Runs commands specified by args."""
        always = kwargs.get("always", False)
        check = kwargs.get("check", True)
        cmd_str = "{0}".format(" ".join(args))
        if not always and self._noop:
            print("noex: {0}".format(cmd_str))
            return FakedProcessResult()
        self.logger.debug("ex: {0}".format(cmd_str))
        return subprocess.run(
            args,
            check=check,
            shell=False,  # noqa: S603
            capture_output=True,
            encoding="utf-8",
        )
