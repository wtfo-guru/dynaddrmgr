import re
import sys
from random import randrange
from typing import Tuple

STATUS = """Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    192.168.66.0/24
[ 2] DNS                        ALLOW IN    192.168.66.0/24
[ 3] DNS (v6)                   ALLOW IN    2605:ba00:6208:681::/64  # DNS/app-dynpr.wtforg.net (dynaddrmgr)
[ 4] DNS (v6)                   ALLOW IN    2605:ba00:6208:4c2::/64  # DNS/app-dynpr.wtforg.net (dynaddrmgr)
[ 5] 22/tcp                     ALLOW IN    2605:ba00:6208:2d55::/64   # 22/tcp-dynpr.wtforg.net (dynaddrmgr)
[ 6] DNS (v6)                   ALLOW IN    2605:ba00:6208:2d55::/64   # DNS/app-dynpr.wtforg.net (dynaddrmgr)
"""

regex_port_proto = re.compile(r"(\d+)\/([a-z]+)")
regex_app = re.compile(r"([ a-zA-Z]+)")
regex_status = re.compile(r"Status:\s+([a-zA-Z]+)")
regex_app_line = re.compile(
    r"\[\s*([0-9]+)\]\s+([ /0-9a-zA-Z()]+)\s+ALLOW IN\s+([.:/a-f0-9]+)\s+#(.*)$",
)


def _parse_port_protocol(field: str) -> Tuple[str, str]:
    """
    Parse a port/protocol field.

    :param field: The port/protocol field.
    :return: A tuple containing the port and protocol.
    """
    port = ""
    proto = ""
    mm = re.match(regex_port_proto, field)
    if mm:
        port = mm.group(1)
        proto = mm.group(2)
        if not re.match("tcp|udp$", proto):
            raise ValueError("Invalid protocol: {0}".format(proto))
    else:
        field = field.replace("(v6)", "").strip()
        mm = re.match(regex_app, field)
        if mm:
            port = mm.group(1)
            proto = "app"
    return (port, proto)


def _parse_status(ufwstatus: str) -> int:  # noqa: WPS231 C901
    """Parse ufw status output."""
    status = False
    for line in ufwstatus.splitlines():
        line = line.strip()
        if not line:
            continue
        if not status:
            mm = re.match(regex_status, line)
            if mm:
                status = True
            continue
        if "(dynaddrmgr)" not in line:  # we only care about our rules
            continue
        mm = re.match(regex_app_line, line)
        if not mm:
            continue
        port, protocol = _parse_port_protocol(mm.group(2).strip())
        print("port: {0}, protocol: {1}".format(port, protocol))
    #     self.before_rules.append(
    #         FwRule(
    #             port,
    #             protocol,
    #             mm.group(3).strip(),
    #             mm.group(4).strip(),
    #             mm.group(1).strip(),
    #         ),
    #     )
    # self.logger.debug("Before rules: {0}".format(len(self.before_rules)))
    return 0


def _test_expressions(**kwargs) -> int:
    status = kwargs.get("status", False)
    if status:
        return _parse_status(STATUS)
    fmt = """[ {0}] {4}/tcp                     ALLOW IN    2605:ba00:6208:2d55::/64   # 22/tcp-dynpr.wtforg.net (dynaddrmgr)
[ {1}] {5} (v6)                   ALLOW IN    2605:ba00:6208:2d55::/64   # {5}/app-dynpr.wtforg.net (dynaddrmgr)
[ {2}] {5}                        ALLOW IN    192.168.2.0/24   # {5}/app-dynpr.wtforg.net (dynaddrmgr)
[ {3}] {6}/udp                     ALLOW IN    2605:ba00:6208:2d55::/64   # 22/tcp-dynpr.wtforg.net (dynaddrmgr)
"""
    with open("/home/jim/tmp/list.txt", "r") as fd:
        for line in fd:
            idx = randrange(1, 96)
            port = randrange(1, 65534)
            t_str = fmt.format(
                idx, idx + 1, idx + 2, idx + 3, port, line.strip(), port + 1
            )
            print(t_str)
            for ll in t_str.splitlines():
                stripped = ll.strip()
                if stripped.find("DNS") != -1:
                    pass
                mm = re.match(regex_app_line, stripped)
                if mm:
                    # print(ll)
                    print(mm.group(1))
                    print(mm.group(2))


if __name__ == "__main__":  # pragma no cover
    sys.exit(_test_expressions(status=True))
