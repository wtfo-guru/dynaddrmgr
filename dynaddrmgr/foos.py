"""
Top level module for dynaddrmgr application.

Functions:
    load_config_file
"""

from pathlib import Path

import click
from wtforglib.files import load_yaml_file
from wtforglib.kinds import StrAnyDict


def load_config_file(config: str, base: str, debug: bool) -> StrAnyDict:
    """Load the configuration file."""
    if not config:
        config_path = Path.home() / ".config" / f"{base}.yaml"
        if config_path.is_file():
            config = str(config_path)
        else:
            config = f"/etc/{base}.yaml"
    if debug:
        click.echo(f"DEBUG: config file => {config}")
    return load_yaml_file(config, missing_ok=False)
