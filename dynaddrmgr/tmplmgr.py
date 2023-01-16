"""
Top level module for dynaddrmgr application.

Classes:
    TemplateManager
"""
from typing import Dict, List

from wtforglib.kinds import StrAnyDict

from dynaddrmgr.app import DynAddrMgr


class TemplateManager(DynAddrMgr):
    """
    Template manager.

    This class is responsible for managing the templates specified
    in the configuration file.
    """

    def manage_templates(self) -> int:
        """Manage the templates specified in the configuration file

        Returns
        -------
        int
            exit_code

        Raises
        ------
        KeyError
            When dynamic_host_templates not in self.config
        """
        dynhosttmpls: Dict[str, StrAnyDict] = self.config.get("dynamic_host_templates")
        if dynhosttmpls is None:
            raise KeyError("dynamic_host_templates key is required in configuration")
        errors = 0
        for tmpl_name, tmpl_def in dynhosttmpls.items():
            for key in ("src", "dest", "hosts"):
                kv = tmpl_def.get(key)
                if kv is None:
                    self.logger.error("Template {0} does not have a {1} key!!".format(tmpl_name, key))
                    errors += 1
                    continue
            ip_addrs = self._lookup_host(
                host.get("name", ""),
                host.get("ipv4", True),
                host.get("ipv6", True),
                host.get("ipv6net", 0),
            )
        return errors
