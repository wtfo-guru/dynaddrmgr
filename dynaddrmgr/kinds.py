"""
Top level module for dynaddrmgr application.

Types:

    IPAddress

Functions:

    None

Misc variables:

    None
"""

import logging
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Union

from loguru._logger import Logger
from wtforglib.options import SimpleScribe

IPSource = Union[IPv4Address, IPv4Network, IPv6Address, IPv6Network]

LoggingClass = Union[SimpleScribe, Logger, logging.Logger]
