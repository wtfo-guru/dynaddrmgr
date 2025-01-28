#!/usr/bin/env python

import pprint
from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
    ip_address,
    ip_network,
)
from typing import Any, Dict, List, Tuple, Union

StrAnyDict = Dict[str, Any]
TmplVar = Dict[str, Tuple[str, ...]]
IPAddress = Union[IPv4Address, IPv6Address]
IPNetwork = Union[IPv4Network, IPv6Network]
IPAddressList = List[IPAddress]
IPNetworkList = List[IPNetwork]


class Scratch:
    variables: TmplVar
    config: StrAnyDict

    def __init__(self, vars: TmplVar) -> None:
        self.ignore = True
        self.config = {}
        self.variables = self._reconcile_template_vars(vars)
        pprint.pp(self.variables)

    def _check_address_in_networks(self, adr: IPAddress, nets: IPNetworkList) -> bool:
        four = isinstance(adr, IPv4Address)
        for net in nets:
            if isinstance(net, IPv4Network):
                if four:
                    if adr in net:
                        return True
            elif isinstance(net, IPv6Network):
                if not four:
                    if adr in net:
                        return True
        return False

    def _reconcile_dynamics(self, dyn: Tuple[str, ...]) -> Tuple[str, ...]:
        for ad in dyn:
            if ad.find("/") == -1:
                self.variables["whitelist"].append(ip_address(ad))
            else:
                self.variables["whitelist"].append(ip_network(ad))

    def _reconcile_whitelist(
        self, whites: Tuple[str, ...]
    ) -> Tuple[IPAddressList, IPNetworkList, List[str]]:
        networks: IPNetworkList = []
        addresses: IPAddressList = []
        reconciled: List[str] = []
        for ip in whites:
            if ip.find("/") == -1:
                addresses.append(ip_address(ip))
            else:
                networks.append(ip_network(ip))
                reconciled.append(ip)
        for adr in addresses:
            if not self._check_address_in_networks(adr, networks):
                reconciled.append(str(adr))
        return addresses, networks, reconciled

    def _reconcile_dynamics(self, vars: TmplVar, pruned: TmplVar) -> None:
        for kk, vv in vars.items():
            if kk == "whitelist":
                continue

    def _reconcile_template_vars(self, vars: TmplVar) -> TmplVar:
        if self.config.get("prune_duplicates", True):
            if "whitelist" in vars:
                ads, nets, whites = self._reconcile_whitelist(vars.get("whitelist"))
                reconciled: TmplVar = {
                    "whitelist": self._reconcile_whitelist(whites),
                }
                self._reconcile_dynamics(vars, reconciled)
                return reconciled
        return vars


scratch = Scratch(
    {
        "dynpr.wtforg.net": ("24.50.225.183", "2605:ba00:6208:2d55::/64"),
        "cosprings.teknofile.net": ("184.99.49.131",),
        "jimphone.mywire.org": (
            "24.50.225.183",
            "2605:ba00:6208:2d55:5462:bf8f:9f87:c1a4",
        ),
        "jimipad.mywire.org": (
            "24.50.225.183",
            "2605:ba00:6208:2d55:d400:cbdf:982:fa36",
        ),
        "whitelist": (
            "184.99.49.131",
            "2001:19f0:5401:88e:5400:5ff:fe40:41b3",
            "24.50.225.183",
            "2605:ba00:6208:2d55:5462:bf8f:9f87:c1a4",
            "2605:ba00:6208:2d55::/64",
            "2605:ba00:6208:2d55:d400:cbdf:982:fa36",
        ),
    },
)
