#!/usr/bin/env python

"""Unit test for `ssl_certinfo.cli` module.

Use tox or py.test to run the test suite.
"""

import subprocess
from argparse import ArgumentTypeError

import pytest

from ssl_certinfo import cli


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
    "args,expected,comment",
    [
        (["github.com"], "github.com", "valid host github.com"),
        (["1.1.1.1"], "1.1.1.1", "valid ip address 1.1.1.1"),
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


def capture(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_cli_main():
    command = "python3 -m ssl_certinfo github.com".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find("github") >= 0
    assert err == b""
