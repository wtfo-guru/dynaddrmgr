"""
Top level module for dynaddrmgr application.

Classes:
    DynAddrMgr

Misc variables:
    APPNM
"""
from typing import List, Tuple

from nslookup import DNSresponse, Nslookup
from wtforglib.ipaddress_foos import ipv6_to_netprefix
from wtforglib.kinds import StrAnyDict
from wtforglib.scribe import Scribe

APPNM = "dynaddrmgr"


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
            level = "warning"
        super().__init__(
            name=APPNM,
            level=level,
            logfn=logfn,
            syslognm=syslognm,
            screen=screen,
        )

    def _lookup_host(
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
        """
        ips: DNSresponse
        if ipv4 and ipv6:
            ips = self.dns.dns_lookup_all(name)
        elif ipv4:
            ips = self.dns.dns_lookup(name)
        elif ipv6:
            ips = self.dns.dns_lookup(name)
        first_set = set(ips.answer)
        if ipv6net and ipv6:
            second_set: List[str] = []
            for ip in first_set:
                second_set.append(ipv6_to_netprefix(ip, ipv6net))
            return tuple(second_set)
        return tuple(first_set)
