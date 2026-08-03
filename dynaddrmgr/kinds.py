"""
Top level module for dynaddrmgr application.

Types:

    IPAddress

Functions:

    None

Misc variables:

    None
"""

from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

IPSource = IPv4Address | IPv4Network | IPv6Address | IPv6Network
