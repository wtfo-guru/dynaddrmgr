"""
Top level module for dynaddrmgr application.

Classes:

    None

Functions:

    print_version
    main

Misc variables:

    CONTEXT_SETTINGS
"""

import sys
import types
from datetime import datetime
from typing import AnyStr

import click
from click.core import Context
from wtforglib.supers import requires_super_user

from dynaddrmgr import VERSION
from dynaddrmgr.foos import load_config_file
from dynaddrmgr.ufw import UfwHandler

CONTEXT_SETTINGS = types.MappingProxyType({"help_option_names": ["-h", "--help"]})


def print_version(ctx: Context, aparam: AnyStr, avalue: AnyStr) -> None:
    """Print package version and exit."""
    if not avalue or ctx.resilient_parsing:
        return
    print(VERSION)  # noqa: WPS421
    ctx.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--config",
    "-c",
    required=False,
    default="",
    help="Specify config file",
)
@click.option(
    "--debug/--no-debug",
    "-d",
    default=False,
    help="Specify debug mode, default: False",
)
@click.option(
    "--noop/--no-noop",
    "-n",
    default=False,
    help="Specify noop mode, default: False",
)
@click.option(
    "--test/--no-test",
    "-t",
    default=False,
    help="Specify test mode, default: False",
)
@click.option(
    "--verbose/--no-verbose",
    "-v",
    default=False,
    help="Specify verbose mode, default: False",
)
@click.option(
    "-V",
    "--version",
    is_flag=True,
    expose_value=False,
    callback=print_version,
    is_eager=True,
    help="Show version and exit",
)
def main(  # noqa: WPS216
    config: str,
    debug: bool,
    test: bool,
    noop: bool,
    verbose: bool,
) -> int:
    """Main function for dynamic firewall rule manager."""
    if not test:
        requires_super_user("When --no-test  dynaddrmgr")
    cfg = load_config_file(config, debug)
    fwtype = cfg.get("firewall_handler", "unspecified").lower()
    try:
        if fwtype == "ufw":
            app = UfwHandler(cfg, debug=debug, noop=noop, test=test, verbose=verbose)
        else:
            raise ValueError("firewall {0} is not supported".format(fwtype))
        rtn_val = app.manage_rules()
    except Exception as ex:
        rtn_val = 1
        print("{0} - {1}".format(datetime.now(), ex), file=sys.stderr)
    return rtn_val


if __name__ == "__main__":  # pragma no cover
    sys.exit(main())

# vim:ft=py noqa: E800
