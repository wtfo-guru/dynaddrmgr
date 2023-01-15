"""
Top level module for dynaddrmgr application.

Classes:
    DynamicHost
"""
from ipaddress import IPv6Address, ip_address
from typing import List, Optional, Union

from nslookup import DNSresponse
from wtforglib.kinds import StrAnyDict
from wtforglib.ipaddress_foos import ipv6_to_netprefix

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
    ports_both: PortList
    ports_tcp: PortList
    ports_udp: PortList
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
        ports = hinfo["ports"]
        self._rules = []
        self.ports_both = self._init_both(ports.get("both"))
        self.ports_tcp = self._init_both(ports.get("tcp"))
        self.ports_udp = self._init_both(ports.get("udp"))

    def rules(self, ips: DNSresponse) -> list[FwRule]:
        """Get rules for dynamic host.

        Parameters
        ----------
        ips : DNSresponse
            DNS response

        Returns
        -------
        list[FwRule]
            List of rules
        """
        if not self._rules:
            prefix_len = 64
            bang_comment = "!!{0}".format(self.name)
            for ipaddr in ips.answer:
                ipaddr = ipv6_to_netprefix(ipaddr, prefix_len)
                for bport in self.ports_both:
                    self._rules.append(FwRule(bport, "", ipaddr, bang_comment))
                for tport in self.ports_tcp:
                    self._rules.append(FwRule(tport, "tcp", ipaddr, bang_comment))
                for uport in self.ports_udp:
                    self._rules.append(FwRule(uport, "udp", ipaddr, bang_comment))
        return self._rules

    def _get_ipv6_prefix(self, ipv6_addr: str, prefix_len: int) -> str:
        """Retruns prefix of ipv6 address.

        Parameters
        ----------
        ipv6_addr : str
            The ipv6 address
        prefix_len : int
            The length of the prefix

        Returns
        -------
        str
            The ipv6 network prefix
        """
        prefix = ""
        cur_prefix_len = 0
        prefix_increment = 16
        ipv6_parts = ipv6_addr.split(":")
        for part in ipv6_parts:
            if prefix:
                prefix = "{0}:{1}".format(prefix, part)
            else:
                prefix = part
            cur_prefix_len += prefix_increment
            if int(cur_prefix_len) >= int(prefix_len):
                return prefix
        return prefix

    def _six_to_netprefix(self, ipaddr: str) -> str:
        """Returns ip address or ipv6 network prefix.

        Parameters
        ----------
        ipaddr : str
            The ip address

        Returns
        -------
        str
            Either ip address or ipv6 network prefix
        """
        ipobj = ip_address(ipaddr)
        if isinstance(ipobj, IPv6Address):
            prefix_length = 64
            prefix = self._get_ipv6_prefix(ipaddr, prefix_length)
            return "{0}::/{1}".format(prefix, prefix_length)
        return ipaddr

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
                if iport not in self.ports_both:
                    self.ports_tcp.append(iport)
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
                if iport in self.ports_tcp:
                    self.ports_tcp.remove(iport)
                    self.ports_both.append(iport)
                elif iport not in self.ports_both:
                    self.ports_udp.append(iport)
        return ports_udp
