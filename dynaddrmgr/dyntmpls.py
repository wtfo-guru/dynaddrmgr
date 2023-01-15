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
from typing import AnyStr, Dict

import click
from click.core import Context
from wtforglib.supers import requires_super_user

from dynaddrmgr import VERSION
from dynaddrmgr.app import DynAddrMgr
from dynaddrmgr.foos import create_handler

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
    """Main function for dynamic template manager."""
    if not test:
        requires_super_user("When --no-test  dynaddrmgr")
    app = DynAddrMgr(config, debug, test, verbose)
    dynhosts = app.config.get("dynamic_hosts_open_ports")
    if dynhosts is None:
        raise KeyError("dynamic_hosts_open_ports key is required in configuration")
    opts: Dict[str, bool] = {}
    opts["debug"] = debug
    opts["noop"] = noop
    opts["test"] = test
    opts["verbose"] = verbose
    fw_handler = create_handler(app.logger, app.config, opts)
    return fw_handler.exec(dynhosts)


if __name__ == "__main__":  # pragma no cover
    sys.exit(main())

# vim:ft=py noqa: E800
