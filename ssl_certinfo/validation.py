"""Validate ip address and hostname."""
import ipaddress
import re


def is_valid_ip_address(value):
    """Validate if parameter is a valid ip address."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_ip_network(value):
    """Validate if parameter is a valid ip network."""
    try:
        net = ipaddress.ip_network(value, False)
    except ValueError:
        return False
    else:
        if net.prefixlen < 32:
            return True
        else:
            return False


def is_valid_ip_range(value):
    """Validate if parameter is a valid ip address range."""
    separator = re.compile(r" *- *")
    try:
        (start, end) = separator.split(value)
        start_addr = ipaddress.ip_address(start)
        end_addr = ipaddress.ip_address(end)
    except ValueError:
        return False
    else:
        if start_addr < end_addr:
            return True
        else:
            return False


def is_valid_hostname(hostname):
    """Validate if parameter is a valid fqdn as defined in RFC-1035."""
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        return False

    labels = hostname.split(".")

    # the TLD must be not all-numeric
    if re.match(r"[0-9]+$", labels[-1]):
        return False

    allowed = re.compile("^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
    return all(allowed.match(label) for label in labels)
