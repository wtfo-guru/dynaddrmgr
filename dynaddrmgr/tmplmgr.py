"""
Top level module for dynaddrmgr application.

Classes:
    TemplateManager
"""
from typing import Dict, List, Optional, Tuple

from wtforglib.kinds import StrAnyDict
from wtforglib.options import basic_options
from wtforglib.tmplwrtr import TemplateWriter

from dynaddrmgr.app import DynAddrMgr

TmplVar = Dict[str, Tuple[str, ...]]


class TemplateManager(DynAddrMgr):  # noqa: WPS214
    """
    Template manager.

    This class is responsible for managing the templates specified
    in the configuration file.
    """

    def __init__(self, config: StrAnyDict, **kwargs):
        """Constructor for TemplateManager class."""
        super().__init__(config, **kwargs)
        opts = basic_options(self.debug, self.test, self.verbose)
        self.writer = TemplateWriter(opts, self)

    def manage_templates(self) -> int:
        """Manage the templates specified in the configuration file.

        Returns
        -------
        int
            exit_code

        Raises
        ------
        KeyError
            When dynamic_host_templates not in self.config
        """
        dynhosttmpls: Optional[Dict[str, StrAnyDict]] = self.config.get(
            "dynamic_host_templates",
        )
        if dynhosttmpls is None:
            raise KeyError("dynamic_host_templates key is required in configuration")
        errors = 0
        for tmpl_name, tmpl_value in dynhosttmpls.items():
            if not self._verify_template_required_keys(tmpl_name, tmpl_value):
                errors += 1
                continue
            tmpl_var: TmplVar = {}
            if not self._template_vars(tmpl_name, tmpl_value, tmpl_var):
                errors += 1
                continue
            tmpl_var["whitelist"] = self._get_white_list(tmpl_var)
            self.logger.debug("tmpl_var: {0}".format(tmpl_var))
            errors += self.writer.generate(tmpl_name, tmpl_value, tmpl_var)
        return errors

    def _unique_sorted_list(self, list_param: List[str]) -> Tuple[str, ...]:
        """Return a sorted unique tuple of strings.

        Parameters
        ----------
        list_param : List[str]
            List of strings to sort.

        Returns
        -------
        Tuple[str, ...]
            Unique, sorted list of strings
        """
        unique_sorted = list(set(list_param))
        unique_sorted.sort()
        return tuple(unique_sorted)

    def _get_white_list(self, tmpl_var: TmplVar) -> Tuple[str, ...]:
        """Return a sorted unique tuple of ip addresses.

        Parameters
        ----------
        tmpl_var : TmplVar
            Dictionary of hostname/ipaddresses

        Returns
        -------
        Tuple[str, ...]
            Unique tuple of ip addresses
        """
        addresses: List[str] = self.config.get("global_whites", [])
        for _key, addrs in tmpl_var.items():
            addresses.extend(addrs)
        return self._unique_sorted_list(addresses)

    def _template_vars(
        self,
        tmpl_name: str,
        tmpl_value: StrAnyDict,
        tmpl_var: TmplVar,
    ) -> bool:
        """Lookup ip sources for template hosts."""
        hosts: List[StrAnyDict] = tmpl_value.get("hosts", {})
        for host in hosts:
            name = host.get("name", "")
            if name:
                unsorted = self._lookup_host(
                    name,
                    host.get("ipv4", True),
                    host.get("ipv6", True),
                    host.get("ipv6net", 0),
                )
                tmpl_var[name] = self._unique_sorted_list(list(unsorted))
            else:
                self.logger.error(
                    "Template {0} hosts name not specified!!".format(tmpl_name),
                )
                return False
        return True

    def _verify_template_required_keys(
        self,
        tmpl_name: str,
        tmpl_value: StrAnyDict,
    ) -> bool:
        """Verify that the template required keys exist."""
        for key in ("src", "dest", "hosts"):
            kv = tmpl_value.get(key)
            if kv is None:
                self.logger.error(
                    "Template {0} does not have a {1} key!!".format(tmpl_name, key),
                )
                return False
        return True
