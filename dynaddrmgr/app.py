"""
Top level module for dynaddrmgr application.

Classes:
    DynFwMgr

Misc variables:
    APPNM
"""
from pathlib import Path

from wtforglib.files import load_yaml_file
from wtforglib.kinds import StrAnyDict
from wtforglib.scribe import Scribe

APPNM = "dynaddrmgr"


class DynFwMgr(Scribe):
    """App class represents the main dynaddrmgr application."""

    config: StrAnyDict
    debug: bool
    test: bool
    verbose: bool

    def __init__(  # noqa: WPS210
        self,
        config: str,
        debug: bool,
        test: bool,
        verbose: bool,
    ) -> None:
        """Initialize DynFwMgr application object.

        Parameters
        ----------
        config : str
            Path to configuration file.
        debug : bool
            Enable debug mode.
        test : bool
            Enable test mode.
        verbose : bool
            Enable verbose mode.
        """
        if not config:
            config_path = Path.home() / ".config" / "dynaddrmgr.yaml"
            if config_path.is_file():
                config = str(config_path)
            else:
                config = "/etc/dynaddrmgr.yaml"
        self.config = load_yaml_file(config, missing_ok=False)
        self.debug = debug
        self.test = test
        self.verbose = verbose
        logfn = self.config.get("logfile", "")
        syslognm = APPNM if self.config.get("syslog", False) else ""
        screen = debug or test or verbose
        if not logfn and not syslognm and not screen:
            syslognm = APPNM
        if debug or test:
            level = "debug"
        elif verbose:
            level = "info"
        else:
            level = "warning"
        super().__init__(
            name=APPNM,
            level=level,
            logfn=logfn,
            syslognm=syslognm,
            screen=screen,
        )
