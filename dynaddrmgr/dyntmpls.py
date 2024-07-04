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

import click
from loguru import logger
from wtforglib.supers import requires_super_user

from dynaddrmgr import VERSION
from dynaddrmgr.foos import load_config_file
from dynaddrmgr.tmplmgr import TemplateManager

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
    if not debug:
        level = "INFO"
        if not verbose:
            level = "WARNING"
        logger.remove(0)
        logger.add(sys.stderr, level=level)
    app = TemplateManager(
        load_config_file(config, "dynaddrmgr", debug),
        debug=debug,
        noop=noop,
        test=test,
        verbose=verbose,
        logger=logger,
    )
    try:
        rtn_val = app.manage_templates()
    except Exception as ex:
        rtn_val = 1
        app.logger.error(str(ex))
    return rtn_val


if __name__ == "__main__":  # pragma no cover
    sys.exit(main())

# vim:ft=py noqa: E800
