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

from dynaddrmgr.kinds import IPSource


class FwRule:
    """FwRule represents a firewall rule."""

    index: int
    allow: str | int
    protocol: str
    ipaddr: IPSource
    comment: str
    status: int

    def __init__(  # noqa: WPS211
        self,
        allow: str | int,
        proto: str,
        ipaddr: str,
        comment: str,
        index: str = "-1",
    ) -> None:
        """Initialize FwRule.

        Parameters
        ----------
        allow : Union[str, int]
            Port number or app
        proto : str
            Protocol
        ipaddr : str
            IP address
        comment : str
            comment string
        index : str
            status index number
        """
        self.protocol = proto
        if proto == "app":
            self.allow = allow
        else:
            self.allow = int(allow)

        self.ipaddr = self.ip_source(ipaddr)
        if comment.startswith("!!"):
            if proto:
                comment = f"{allow}/{proto}-{comment[2:]} (dynaddrmgr)"
            else:
                comment = f"{allow}-{comment[2:]} (dynaddrmgr)"
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
            return (
                f"[{self.index:2d}] {self.allow!s:>5}/{self.protocol} "  # noqa: WPS221
                f"{self.ipaddr:<40} # {self.comment} [{self.status:d}]"
            )
        return (
            f"[{self.index:2d}] {self.allow!s:>5} {self.ipaddr:<45} "  # noqa: WPS221
            f"# {self.comment} [{self.status:d}]"
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
            raise TypeError("Can only compare FwRule instances.")
        if self.ipaddr != other.ipaddr:
            return False
        if self.allow != other.allow:
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
            raise ValueError(f"Invalid ip source: {ipaddr}")
        return source

    def _ip_address(self, ipaddr: str) -> IPSource | None:
        try:
            source = ip_address(ipaddr)
        except ValueError:
            return None
        return source

    def _ip_network(self, ipaddr: str) -> IPSource | None:
        try:
            source = ip_network(ipaddr)
        except ValueError:
            return None
        return source
