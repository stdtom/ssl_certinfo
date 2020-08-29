#!/usr/bin/env python

"""Unit test for `ssl_certinfo.cli` module.

Use tox or py.test to run the test suite.
"""

import subprocess
from argparse import ArgumentTypeError

import pytest

from ssl_certinfo import __author__, __email__, __version__, cli
from ssl_certinfo.ssl_certinfo import OutputFormat


@pytest.fixture
def parser():
    return cli.create_parser()


@pytest.mark.parametrize("test_input", [1, 2, 65535, "2"])
def test_valid_positive(test_input):
    assert cli.check_positive(test_input)


@pytest.mark.parametrize("test_input", [-1, -10, "x"])
def test_invalid_positive(test_input):
    with pytest.raises(ArgumentTypeError):
        assert cli.check_positive(test_input)


@pytest.mark.parametrize(
    "args,expected,comment",
    [
        (["github.com"], 5, "default timeout 5 sec"),
        (["github.com", "-t", "2"], 2, "timeout 2 sec"),
    ],
)
def test_cli_valid_timeout(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    args = parser.parse_args(args)
    assert args.timeout == expected


@pytest.mark.parametrize(
    "args,expected,comment",
    [(["github.com", "-t", "-1"], -1, "invalid timeout -1 sec")],
)
def test_cli_invalid_timeout(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    with pytest.raises(SystemExit):
        args = parser.parse_args(args)


@pytest.mark.parametrize("test_input", [1, 2, 65535, "2"])
def test_valid_port(test_input):
    assert cli.check_valid_port(test_input)


@pytest.mark.parametrize("test_input", [-1, 65536, "x"])
def test_invalid_port(test_input):
    with pytest.raises(ArgumentTypeError):
        assert cli.check_valid_port(test_input)


@pytest.mark.parametrize(
    "args,expected,comment",
    [
        (["github.com"], 443, "default port 443"),
        (["github.com", "-p", "8443"], 8443, "port 8443"),
    ],
)
def test_cli_valid_port(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    args = parser.parse_args(args)
    assert args.port == expected


@pytest.mark.parametrize(
    "args,comment",
    [
        (["github.com", "-p", "-1"], "invalid port -1"),
        (["github.com", "-p", "65536"], "invalid port 65536"),
    ],
)
def test_cli_invalid_port(parser, args, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    with pytest.raises(SystemExit):
        args = parser.parse_args(args)


@pytest.mark.parametrize(
    "inlist,expected,comment",
    [
        (
            "github.com 1.1.1.1".split(" "),
            ["github.com", "1.1.1.1"],
            "nothing to expand",
        ),
        (
            "github.com 192.168.0.0/30 1.1.1.1".split(" "),
            [
                "github.com",
                "192.168.0.0",
                "192.168.0.1",
                "192.168.0.2",
                "192.168.0.3",
                "1.1.1.1",
            ],
            "expand /30 network",
        ),
        (
            ["github.com", "192.168.0.253 - 192.168.1.2", "1.1.1.1"],
            [
                "github.com",
                "192.168.0.253",
                "192.168.0.254",
                "192.168.0.255",
                "192.168.1.0",
                "192.168.1.1",
                "192.168.1.2",
                "1.1.1.1",
            ],
            "expand ip range across subnet boundaries",
        ),
    ],
)
def test_expand_hosts(inlist, expected, comment):
    out = cli.expand_hosts(inlist)
    assert out == expected


@pytest.mark.parametrize(
    "inlist,expected,comment",
    [
        pytest.param(
            "23.1.1.1/8".split(" "),
            256 ** 3,
            "expand class A network",
            marks=pytest.mark.skip,
        ),
        ("130.80.0.0/16".split(" "), 65536, "expand class B network",),
        ("192.168.0.0/24".split(" "), 256, "expand class C network",),
        ("192.168.0.0/30".split(" "), 4, "expand /30 network",),
        ("192.168.0.0-192.168.1.255".split(" "), 512, "range of 2 class C networks",),
    ],
)
def test_expand_hosts_large_networks(inlist, expected, comment):
    out = cli.expand_hosts(inlist)
    assert len(out) == expected


@pytest.mark.parametrize(
    "args,expected,comment",
    [
        ("github.com".split(" "), ["github.com"], "valid host github.com"),
        ("1.1.1.1".split(" "), ["1.1.1.1"], "valid ip address 1.1.1.1"),
        (
            "github.com 1.1.1.1".split(" "),
            ["github.com", "1.1.1.1"],
            "two targets: valid hostname and ip address",
        ),
        ("192.0.2.0/24".split(" "), ["192.0.2.0/24"], "valid ip network 192.0.2.0/24"),
        (
            "10.0.0.1-10.0.0.5".split(" "),
            ["10.0.0.1-10.0.0.5"],
            "valid ip range 10.0.0.1 - .5",
        ),
    ],
)
def test_cli_valid_host_or_ip(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    args = parser.parse_args(args)
    assert args.host == expected


@pytest.mark.parametrize(
    "args,comment",
    [
        (["github.com-"], "invalid hostwith trailing dash"),
        (["1.1.1.256"], "invalid ip address 1.1.1.256"),
    ],
)
def test_cli_indvalid_host_or_ip(parser, args, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    with pytest.raises(SystemExit):
        args = parser.parse_args(args)


@pytest.mark.parametrize(
    "args,expected,comment",
    [
        ("github.com".split(), OutputFormat.TABLE, "default"),
        ("github.com --table".split(), OutputFormat.TABLE, "TABLE"),
        ("github.com -T".split(), OutputFormat.TABLE, "TABLE"),
        ("github.com --json".split(), OutputFormat.JSON, "JSON"),
        ("github.com -j".split(), OutputFormat.JSON, "JSON"),
        ("github.com --yaml".split(), OutputFormat.YAML, "YAML"),
        ("github.com -y".split(), OutputFormat.YAML, "YAML"),
        ("github.com --csv".split(), OutputFormat.CSV, "CSV"),
        ("github.com -c".split(), OutputFormat.CSV, "CSV"),
        ("github.com --raw".split(), OutputFormat.RAW, "RAW"),
        ("github.com -r".split(), OutputFormat.RAW, "RAW"),
    ],
)
def test_cli_outform(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    args = parser.parse_args(args)
    assert args.outform == expected


def capture(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_cli_main_version():
    command = "python -m ssl_certinfo -V".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find(__version__) >= 0
    assert out.decode().find(__author__) >= 0
    assert out.decode().find(__email__) >= 0


def test_cli_main_single_target():
    command = "python -m ssl_certinfo github.com".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find("github") >= 0
    assert (err == b"") or (err.decode().find("100%") >= 0)


def test_cli_main_two_targets():
    command = "python -m ssl_certinfo github.com wikipedia.org".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find("github") >= 0
    assert out.decode().find("wikipedia") >= 0
    assert (err == b"") or (err.decode().find("100%") >= 0)
