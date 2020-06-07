"""Console script for ssl_certinfo."""
import argparse
import ipaddress
import logging
import re
import sys

from ssl_certinfo import ssl_certinfo, validation
from ssl_certinfo.ssl_certinfo import OutputFormat


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
        "host",
        nargs="*",
        type=check_hostname_or_ip_address,
        help="Connect to HOST[:PORT]",
    )

    parser.add_argument(
        "-p",
        "--port",
        default=443,
        type=check_valid_port,
        help="Default TCP port to connnect to [0-65535]",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        default=5,
        type=check_positive,
        help="Maximum time allowed for connection",
    )

    output_format = parser.add_mutually_exclusive_group()
    output_format.add_argument(
        "-j",
        "--json",
        action="store_const",
        const=OutputFormat.JSON,
        default=OutputFormat.JSON,
        dest="outform",
        help="Print results in JSON format",
    )
    output_format.add_argument(
        "-y",
        "--yaml",
        action="store_const",
        const=OutputFormat.YAML,
        default=OutputFormat.JSON,
        dest="outform",
        help="Print results in YAML format",
    )

    return parser


def setup_logging(verbosity):
    base_loglevel = 30
    verbosity = min(verbosity, 2)
    loglevel = base_loglevel - (verbosity * 10)
    logging.basicConfig(level=loglevel, format="%(levelname)s\t%(message)s")


def main():
    """Console script for ssl_certinfo."""
    args = create_parser().parse_args()
    setup_logging(args.verbosity)

    logging.info("Arguments: " + str(args))

    ssl_certinfo.process_hosts(
        expand_hosts(args.host), args.port, args.timeout, args.outform
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
