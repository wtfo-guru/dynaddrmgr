"""
Top level module for dynaddrmgr application.

Classes:
    DynamicHost
"""

from typing import List, Optional, Tuple, Union

from wtforglib.kinds import StrAnyDict

from dynaddrmgr.rule import FwRule

EXAMPLES = """
#   - name: dynpr.wtforg.net
#     ipv4: true
#     ipv6: true
#     ports:
#       tcp:
#         - 22
#         - 3306
#         - 33060
#         - 5432
"""
PortList = List[int]
CfgPortList = List[Union[str, int]]


class DynamicHost(object):
    """DynamicHost is a wrapper for the dynamic host."""

    name: str
    ipv4: bool
    ipv6: bool
    ipv6net: int
    _ports_both: PortList
    _ports_tcp: PortList
    _ports_udp: PortList
    _rules: List[FwRule]
    fw_handler: object

    def __init__(self, hinfo: StrAnyDict) -> None:
        """Initialize DynamicHost.

        Parameters
        ----------
        hinfo : StrAnyDict
            Dictionary describing dynamic host information
        """
        self.name = hinfo["name"]
        self.ipv4 = hinfo["ipv4"]
        self.ipv6 = hinfo["ipv6"]
        self.ipv6net = hinfo.get("ipv6net", 0)
        ports = hinfo["ports"]
        self._rules = []
        self._ports_both = self._init_both(ports.get("both"))
        self._ports_tcp = self._init_tcp(ports.get("tcp"))
        self._ports_udp = self._init_udp(ports.get("udp"))

    def rules(self, ips: Tuple[str, ...]) -> List[FwRule]:
        """Get rules for dynamic host.

        Parameters
        ----------
        ips : Tuple[str, ...]
            List of ipaddress sources

        Returns
        -------
        List[FwRule]
            List of rules
        """
        if not self._rules:
            bang_comment = "!!{0}".format(self.name)
            for ipaddr in ips:
                for bport in self._ports_both:
                    self._rules.append(FwRule(bport, "", ipaddr, bang_comment))
                for tport in self._ports_tcp:
                    self._rules.append(FwRule(tport, "tcp", ipaddr, bang_comment))
                for uport in self._ports_udp:
                    self._rules.append(FwRule(uport, "udp", ipaddr, bang_comment))
        return self._rules

    def _init_both(self, ports: Optional[CfgPortList]) -> PortList:
        """Initialize both ports list.

        Parameters
        ----------
        ports : Optional[CfgPortList]
            Dictionary describing ports

        Returns
        -------
        PortList
            List of ports
        """
        ports_both: PortList = []
        if ports is not None:
            for port in ports:
                ports_both.append(int(port))
        return ports_both

    def _init_tcp(self, ports: Optional[CfgPortList]) -> PortList:
        """Initialize both ports list.

        Parameters
        ----------
        ports : Optional[CfgPortList]
            Dictionary describing ports

        Returns
        -------
        PortList
            List of ports
        """
        ports_tcp: PortList = []
        if ports is not None:
            for port in ports:
                iport = int(port)
                if iport not in self._ports_both:
                    ports_tcp.append(iport)
        return ports_tcp

    def _init_udp(self, ports: Optional[CfgPortList]) -> PortList:
        """Initialize both ports list.

        Parameters
        ----------
        ports : Optional[CfgPortList]
            Dictionary describing ports

        Returns
        -------
        PortList
            List of ports
        """
        ports_udp: PortList = []
        if ports is not None:
            for port in ports:
                iport = int(port)
                if iport in self._ports_tcp:
                    self._ports_tcp.remove(iport)
                    self._ports_both.append(iport)
                elif iport not in self._ports_both:
                    ports_udp.append(iport)
        return ports_udp
