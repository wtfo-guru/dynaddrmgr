"""
Top level module for dynaddrmgr application.

Classes:

    FwRule

Functions:

    None

Misc variables:

    None
"""

from ipaddress import ip_address, ip_network
from typing import Optional, Union

from dynaddrmgr.kinds import IPSource


class FwRule(object):
    """FwRule represents a firewall rule."""

    index: int
    port: int
    protocol: str
    ipaddr: IPSource
    comment: str
    status: int

    def __init__(  # noqa: WPS211
        self,
        port: Union[str, int],
        proto: str,
        ipaddr: str,
        comment: str,
        index: str = "-1",
    ) -> None:
        """Initialize FwRule.

        Parameters
        ----------
        port : Union[str, int]
            Port number
        proto : str
            Protocal
        ipaddr : str
            IP address
        comment : str
            comment string
        index : str
            status index number
        """
        self.port = int(port)
        self.protocol = proto
        self.ipaddr = self.ip_source(ipaddr)
        if comment.startswith("!!"):
            if proto:
                comment = "{0}/{1}-{2} (dynaddrmgr)".format(port, proto, comment[2:])
            else:
                comment = "{0}-{1} (dynaddrmgr)".format(port, comment[2:])
        self.comment = comment
        self.index = int(index)
        self.status = 0

    def __str__(self) -> str:
        """Returns a string representation of this instance.

        Returns
        -------
        str
            representation of this instance
        """
        if self.protocol:
            return "[%2s] %5s/%s %-40s # %s [%d]" % (  # noqa: WPS323
                str(self.index),
                str(self.port),
                self.protocol,
                str(self.ipaddr),
                self.comment,
                self.status,
            )
        return "[%2s] %5s %-45s # %s [%d]" % (  # noqa: WPS323
            str(self.index),
            str(self.port),
            str(self.ipaddr),
            self.comment,
            self.status,
        )

    def __eq__(self, other: object) -> bool:
        """Compare FwRule objects.

        Parameters
        ----------
        other : object
            other object

        Raises
        ------
        ValueError
            if other is not a FwRule object

        Returns
        -------
        bool
            True if equal
        """
        if not isinstance(other, FwRule):
            # don't attempt to compare against unrelated types
            raise ValueError("Can only compare FwRule instances.")
        if self.ipaddr != other.ipaddr:
            return False
        if self.port != other.port:
            return False
        if self.protocol != other.protocol:
            return False
        return self.comment == other.comment

    def ip_source(self, ipaddr: str) -> IPSource:
        """Convert string representation to IPSource object.

        Parameters
        ----------
        ipaddr : str
            String representation of ip source

        Returns
        -------
        IPSource
            The IP source to allow

        Raises
        ------
        ValueError
            ipaddr parameter is not a valid IP address or IP network
        """
        source = self._ip_address(ipaddr)
        if source is None:
            source = self._ip_network(ipaddr)
        if source is None:
            raise ValueError("Invalid ip source: {0}".format(ipaddr))
        return source

    def _ip_address(self, ipaddr) -> Optional[IPSource]:
        try:
            source = ip_address(ipaddr)
        except ValueError:
            return None
        return source

    def _ip_network(self, ipaddr) -> Optional[IPSource]:
        try:
            source = ip_network(ipaddr)
        except ValueError:
            return None
        return source
