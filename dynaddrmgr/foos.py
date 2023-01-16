"""
Top level module for dynaddrmgr application.

Functions:
    create_handler
"""
from pathlib import Path

from wtforglib.files import load_yaml_file
from wtforglib.kinds import StrAnyDict


def load_config_file(config: str) -> StrAnyDict:
    """Load the configuration file."""
    if not config:
        config_path = Path.home() / ".config" / "dynaddrmgr.yaml"
        if config_path.is_file():
            config = str(config_path)
        else:
            config = "/etc/dynaddrmgr.yaml"
    return load_yaml_file(config, missing_ok=False)
