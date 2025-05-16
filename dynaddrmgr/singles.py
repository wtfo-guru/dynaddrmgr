"""Singles module for package wtftools."""

from dailylog_lib.logger import Logger
from wtforglib.singles import r_singleton


@r_singleton
class DailyLogger(Logger):
    """Singleton logger class."""
