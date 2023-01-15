"""
Top level module for dynaddrmgr application.

Functions:
    create_handler
"""
from logging import Logger
from typing import Dict

from wtforglib.kinds import StrAnyDict

from dynaddrmgr.fwhdlr import FirewallHandler
from dynaddrmgr.ufw import UfwHandler


def create_handler(
    logger: Logger,
    cfg: StrAnyDict,
    opts: Dict[str, bool],
) -> FirewallHandler:
    """Returns firewall handler specified.

    Parameters
    ----------
    logger : Logger instance
        Application logger
    cfg : StrAnyDict
        Configuration dictionary
    opts : Dict[str,bool]
        Options dictionary

    Returns
    -------
    FirewallHandler
        The FirewallHandler

    Raises
    ------
    ValueError
        If fwtype is not supported
    """
    fwtype = cfg.get("firewall_handler", "unspecified").lower()
    if fwtype == "ufw":
        return UfwHandler(logger, cfg, opts)
    raise ValueError("firewall {0} is not supported".format(fwtype))
