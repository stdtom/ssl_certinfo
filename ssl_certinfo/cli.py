"""Console script for ssl_certinfo."""
import argparse
import ipaddress
import logging
import os
import re
import sys
from typing import Tuple

from ssl_certinfo import __author__, __email__, __version__, ssl_certinfo, validation
from ssl_certinfo.ssl_certinfo import OutputFormat

VERSION = rf"""
ssl_certinfo {__version__}
Copyright (C) 2020 {__author__} ({__email__})
License Apache-2.0: <http://www.apache.org/licenses/LICENSE-2.0>.
"""


def check_hostname_or_ip_address(value):
    """Validate argparse type hostname/ip address."""
    if (
        not validation.is_valid_hostname(value)
        and not validation.is_valid_ip_address(value)
        and not validation.is_valid_ip_network(value)
        and not validation.is_valid_ip_range(value)
    ):
        raise argparse.ArgumentTypeError(
            "%s is not a valid hostname or ip address" % value
        )
    return value


def check_proxy_url(value):
    """Validate if parameter is a valid proxy url."""
    try:
        parsed = parse_proxy_url(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s is not a valid proxy url" % value)

    return parsed


def parse_proxy_url(proxyurl) -> Tuple[str, str, int]:
    if proxyurl == "":
        return None

    proto = host = port = ""
    match = re.match(r"^((http[s]?|socks):\/\/)?([^:\/\s]+)(:(\d+))?$", proxyurl)
    if match:
        x, proto, host, x, port = match.groups(default="")
    else:
        locallogger = logging.getLogger("validate.parse_proxy_url")
        locallogger.debug("Not a valid proxy url: {}".format(proxyurl))
        raise ValueError("Not a valid proxy url: {}".format(proxyurl))

    if not proto:
        proto = "http"
    if (
        host
        and not validation.is_valid_hostname(host)
        and not validation.is_valid_ip_address(host)
    ):
        raise ValueError("Not a valid hostname or ip address: {}".format(port))
    if not port:
        port = 3128
    elif not (0 < int(port) <= 65535):
        raise ValueError("Invalid port number: {}".format(port))

    return proto, host, int(port)


def check_positive(value):
    """Validate argparse type positive integer."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s is not an int value" % value)

    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive int value" % value)
    return ivalue


def check_valid_port(value):
    """Validate argparse type TCP port number."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s is an invalid port number" % value)

    if ivalue <= 0 or ivalue > 65535:
        raise argparse.ArgumentTypeError("%s is an invalid port number" % value)
    return ivalue


def expand_hosts(hostlist):
    result = []

    for elem in hostlist:
        if validation.is_valid_hostname(elem) or validation.is_valid_ip_address(elem):
            result.append(elem)
        elif validation.is_valid_ip_range(elem):
            separator = re.compile(r" *- *")
            (start, end) = separator.split(elem)
            try:
                start_addr = ipaddress.ip_address(start)
                end_addr = ipaddress.ip_address(end)
            except ValueError:
                pass
            else:
                logging.debug("Expanding ip address range " + elem)
                current_ipaddr = start_addr
                while current_ipaddr <= end_addr:
                    result.append(str(current_ipaddr))
                    current_ipaddr = current_ipaddr + 1
        else:
            try:
                net = ipaddress.ip_network(elem, False)
            except ValueError:
                pass
            else:
                logging.debug("Expanding ip network " + elem)
                for ipaddr in net:
                    result.append(str(ipaddr))

    return result


def create_parser():
    """Create ArgParser."""
    parser = argparse.ArgumentParser(
        description="Collect information about SSL certificates from a set of hosts"
    )

    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        dest="displayVersion",
        help="display version information and exit",
    )

    verb_group = parser.add_mutually_exclusive_group()
    verb_group.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="verbose output (repeat for increased verbosity)",
    )
    verb_group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=-1,
        default=0,
        dest="verbosity",
        help="quiet output (show errors only)",
    )

    parser.add_argument(
        "host", nargs="*", type=check_hostname_or_ip_address, help="Connect to HOST",
    )

    parser.add_argument(
        "-p",
        "--port",
        default=443,
        type=check_valid_port,
        help="TCP port to connnect to [0-65535]",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        default=5,
        type=check_positive,
        help="Maximum time allowed for connection",
    )

    parser.add_argument(
        "-x",
        "--proxy",
        default=get_proxy_from_env(),
        type=check_proxy_url,
        help="Use the specified proxy",
        metavar="[protocol://]host[:port]",
    )

    output_format = parser.add_mutually_exclusive_group()
    output_format.add_argument(
        "-T",
        "--table",
        action="store_const",
        const=OutputFormat.TABLE,
        default=OutputFormat.TABLE,
        dest="outform",
        help="Print results in table format",
    )
    output_format.add_argument(
        "-j",
        "--json",
        action="store_const",
        const=OutputFormat.JSON,
        default=OutputFormat.TABLE,
        dest="outform",
        help="Print results in JSON format",
    )
    output_format.add_argument(
        "-y",
        "--yaml",
        action="store_const",
        const=OutputFormat.YAML,
        default=OutputFormat.TABLE,
        dest="outform",
        help="Print results in YAML format",
    )
    output_format.add_argument(
        "-c",
        "--csv",
        action="store_const",
        const=OutputFormat.CSV,
        default=OutputFormat.TABLE,
        dest="outform",
        help="Print results in CSV format",
    )
    output_format.add_argument(
        "-r",
        "--raw",
        action="store_const",
        const=OutputFormat.RAW,
        default=OutputFormat.TABLE,
        dest="outform",
        help="Print results in raw format",
    )

    return parser


def get_proxy_from_env():
    locallogger = logging.getLogger("cli.get_proxy_from_env")
    env_keys = [
        "http_proxy",
        "HTTP_PROXY",
        "https_proxy",
        "HTTPS_PROXY",
    ]
    env = os.environ
    for key in env_keys:
        if key in env:
            locallogger.debug(
                "Environment variable {} found with value: {}".format(key, env[key])
            )
            return env[key]

    locallogger.debug("No proxy environment variable found.")
    return ""


def setup_logging(verbosity):
    base_loglevel = 30
    verbosity = min(verbosity, 2)
    loglevel = base_loglevel - (verbosity * 10)
    logging.basicConfig(level=loglevel, format="%(levelname)s\t%(message)s")


def main():
    """Console script for ssl_certinfo."""
    args = create_parser().parse_args()
    if args.displayVersion:
        print(VERSION)
        return 0

    setup_logging(args.verbosity)

    logging.info("Arguments: " + str(args))

    ssl_certinfo.process_hosts(
        expand_hosts(args.host), args.port, args.timeout, args.outform, args.proxy
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
