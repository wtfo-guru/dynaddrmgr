"""
Top level module for dynaddrmgr application.

Classes:
    TemplateManager
"""

from ipaddress import IPv4Address
from typing import Dict, List, Optional, Tuple, Union

from wtforglib.kinds import StrAnyDict, StrStrDict
from wtforglib.options import basic_options
from wtforglib.tmplwrtr import TemplateWriter

from dynaddrmgr.app import DynAddrMgr, FakedProcessResult, WtfProcessResult

TailscaleStatus = List[StrStrDict]

TmplVar = Dict[str, Union[Tuple[str, ...], StrStrDict]]  # noqa: WPS221

NAME = "name"
IP = "ip"

SAMPLE_TEST_DATA = """202.107.231.105 ivy                  qs5779@      linux   -
202.72.248.93   bee                  qs5779@      linux   -
202.77.204.24   elk                  qs5779@      linux   idle, tx 5628 rx 6212
202.79.151.88   google-pixel-6       qs5779@      android -
202.109.91.4    guv                  qs5779@      linux   -
202.123.213.99  hag                  qs5779@      linux   offline
202.118.119.35  ipad-pro-12-9-gen-4  qs5779@      iOS     -
202.84.179.124  mayra-xps            qs5779@      windows -
202.82.122.40   pid                  qs5779@      linux   -
202.125.17.13   yam                  qs5779@      linux   -
"""


class TemplateManager(DynAddrMgr):  # noqa: WPS214
    """
    Template manager.

    This class is responsible for managing the templates specified
    in the configuration file.
    """

    def __init__(self, config: StrAnyDict, **kwargs: bool):
        """Constructor for TemplateManager class."""
        super().__init__(config, **kwargs)
        opts = basic_options(self.debug, self.test, self.verbose)
        self.writer = TemplateWriter(opts)

    def manage_templates(self) -> int:  # noqa: WPS231
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
        dyn_host_tmpls: Optional[Dict[str, StrAnyDict]] = self.config.get(
            "dynamic_host_templates",
        )
        if dyn_host_tmpls is None:
            raise KeyError("dynamic_host_templates key is required in configuration")
        errors = 0
        for tmpl_name, tmpl_value in dyn_host_tmpls.items():
            if not self._verify_template_required_keys(tmpl_name, tmpl_value):
                errors += 1
                continue
            tmpl_var: TmplVar = {}
            if not self._template_vars(tmpl_name, tmpl_value, tmpl_var):
                errors += 1
                continue
            tmpl_var["whitelist"] = self._get_white_list(tmpl_var)
            if self.config.get("tailscale", False):
                tmpl_var["tailscale_hosts"] = self._capture_parse_tailscale_status()
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
            self.logger.debug("host: {0}".format(host))
            name = host.get(NAME, "")
            if name:
                unsorted = self._lookup_host(
                    name,
                    host.get("ipv4", True),
                    host.get("ipv6", True),
                    host.get("ipv6net", 0),
                    host.get("ipv6net_style", "standard"),
                    host.get("ipv4net", False),
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

    def _status_to_hosts(  # noqa: WPS231
        self,
        status: TailscaleStatus,
    ) -> StrStrDict:
        """Convert tailscale status to hosts."""
        hosts: StrStrDict = {}
        for ts_info in status:
            for key in (IP, NAME):
                if key not in ts_info:
                    raise KeyError("Missing key: {0}".format(key))
                valor = ts_info.get(IP, "")
                if not valor:
                    raise ValueError("Empty {0}".format(ts_info.get(key)))
            hosts[ts_info.get(IP, "1.1.1.1")] = ts_info.get(NAME, "dunno")
        return hosts

    def _capture_parse_tailscale_status(self) -> StrStrDict:
        """Capture and parse tailscale status."""
        c_res: WtfProcessResult
        if self.test:
            c_res = FakedProcessResult(SAMPLE_TEST_DATA)
        else:
            c_res = self._run_command(("tailscale", "status"), check=False)
            if self.debug:
                self.logger.debug(str(c_res))

        status = c_res.stdout.splitlines()

        ts_status: TailscaleStatus = []

        for line in status:
            self._parse_tailscale_line(ts_status, line)
        return self._status_to_hosts(ts_status)

    def _parse_tailscale_line(self, ts_status: TailscaleStatus, ts_line: str) -> bool:
        """Parse a line from tailscale status."""
        line = ts_line.strip()
        if not line:
            return False  # empty line
        if line.startswith("#"):
            self.logger.warning(line)
            return False
        if line.find("Logged out.") > -1:
            self.logger.log_message("ts-logged-out", line)
            return False
        parts = line.split(None, 2)
        if self.debug:
            self.logger.debug(str(parts))
        if len(parts) == 3:
            IPv4Address(parts[0])  # will raise AddressValueError if bad
            ts_info: StrStrDict = {}
            ts_info[IP] = parts[0]
            ts_info[NAME] = parts[1]
            ts_info["status"] = parts[2]
            ts_status.append(ts_info)
        else:
            self.logger.error("Failed to parse line: {0}".format(line))
            return False
        return True
