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
import traceback
import types
from datetime import datetime

import click
from loguru import logger
from wtforglib.supers import requires_super_user

from dynaddrmgr import VERSION
from dynaddrmgr.foos import load_config_file
from dynaddrmgr.ufw import UfwHandler

CONTEXT_SETTINGS = types.MappingProxyType({"help_option_names": ["-h", "--help"]})


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
@click.version_option(VERSION)
def main(  # noqa: WPS216, C901
    config: str,
    debug: bool,
    test: bool,
    noop: bool,
    verbose: bool,
) -> int:
    """Main function for dynamic firewall rule manager."""
    if not test:
        requires_super_user("When --no-test  dynaddrmgr")
    cfg = load_config_file(config, "dynaddrmgr", debug)
    fwtype = cfg.get("firewall_handler", "unspecified").lower()
    if not debug:
        level = "INFO"
        if not verbose:
            level = "WARNING"
        logger.remove(0)
        logger.add(sys.stderr, level=level)
    try:
        if fwtype == "ufw":
            app = UfwHandler(
                cfg,
                debug=debug,
                noop=noop,
                test=test,
                verbose=verbose,
                logger=logger,
            )
        else:
            raise ValueError("firewall {0} is not supported".format(fwtype))
        rtn_val = app.manage_rules()
    except Exception as ex:
        rtn_val = 1
        print("{0} - {1}".format(datetime.now(), ex), file=sys.stderr)
        if debug:
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)

    return rtn_val


if __name__ == "__main__":  # pragma no cover
    sys.exit(main())

# vim:ft=py noqa: E800
