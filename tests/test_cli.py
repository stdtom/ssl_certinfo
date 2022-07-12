#!/usr/bin/env python

"""Unit test for `ssl_certinfo.cli` module.

Use tox or py.test to run the test suite.
"""

from argparse import ArgumentTypeError

import pytest

from ssl_certinfo import cli


@pytest.mark.parametrize(
    "proxyurl, expected",
    [
        ("http://myproxy.domain.org:8080", ("http", "myproxy.domain.org", 8080)),
        ("http://100.100.100.100:8080", ("http", "100.100.100.100", 8080)),
        ("http://myproxy.domain.org", ("http", "myproxy.domain.org", 3128)),
        ("http://100.100.100.100", ("http", "100.100.100.100", 3128)),
        ("myproxy.domain.org:8080", ("http", "myproxy.domain.org", 8080)),
        ("100.100.100.100:8080", ("http", "100.100.100.100", 8080)),
        ("myproxy.domain.org", ("http", "myproxy.domain.org", 3128)),
        ("100.100.100.100", ("http", "100.100.100.100", 3128)),
    ],
)
def test_parse_proxy_url(proxyurl, expected):
    assert expected == cli.parse_proxy_url(proxyurl)


@pytest.mark.parametrize(
    "proxyurl, expected",
    [
        ("", None),
        ("http://myproxy.domain.org:8080", ("http", "myproxy.domain.org", 8080)),
        ("http://100.100.100.100:8080", ("http", "100.100.100.100", 8080)),
        ("http://myproxy.domain.org", ("http", "myproxy.domain.org", 3128)),
        ("http://100.100.100.100", ("http", "100.100.100.100", 3128)),
        ("myproxy.domain.org:8080", ("http", "myproxy.domain.org", 8080)),
        ("100.100.100.100:8080", ("http", "100.100.100.100", 8080)),
        ("myproxy.domain.org", ("http", "myproxy.domain.org", 3128)),
        ("100.100.100.100", ("http", "100.100.100.100", 3128)),
    ],
)
def test_valid_proxy_url(proxyurl, expected):
    assert expected == cli.check_proxy_url(proxyurl)


@pytest.mark.parametrize(
    "test_input",
    [
        "ftp://myproxy.domain.org:8080",
        "http://100.100.100.100.1:8080",
        "ftp://myproxy.domain.org",
        "myproxy.domain.org:0",
        "myproxy.domain.org:65536",
        "myproxy.domain.org:port",
        "myproxy.domain.org:_",
    ],
)
def test_invalid_proxy_url(test_input):
    with pytest.raises((ArgumentTypeError)):
        assert not cli.check_proxy_url(test_input)


@pytest.mark.parametrize("test_input", [1, 2, 65535, "2"])
def test_valid_positive(test_input):
    assert cli.check_positive(test_input)


@pytest.mark.parametrize("test_input", [-1, -10, "x"])
def test_invalid_positive(test_input):
    with pytest.raises(ArgumentTypeError):
        assert cli.check_positive(test_input)


@pytest.mark.parametrize("test_input", [1, 2, 65535, "2"])
def test_valid_port(test_input):
    assert cli.check_valid_port(test_input)


@pytest.mark.parametrize("test_input", [-1, 65536, "x"])
def test_invalid_port(test_input):
    with pytest.raises(ArgumentTypeError):
        assert cli.check_valid_port(test_input)


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
        (
            "@tests/test_data/test_hostlist.txt".split(" "),
            ["github.com", "wikipedia.org"],
            "expand from file",
        ),
        (
            "@tests/test_data/test_hostlist.txt 1.1.1.1".split(" "),
            ["github.com", "wikipedia.org", "1.1.1.1"],
            "expand from file and hostlist",
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
            256**3,
            "expand class A network",
            marks=pytest.mark.skip,
        ),
        (
            "130.80.0.0/16".split(" "),
            65536,
            "expand class B network",
        ),
        (
            "192.168.0.0/24".split(" "),
            256,
            "expand class C network",
        ),
        (
            "192.168.0.0/30".split(" "),
            4,
            "expand /30 network",
        ),
        (
            "192.168.0.0-192.168.1.255".split(" "),
            512,
            "range of 2 class C networks",
        ),
    ],
)
def test_expand_hosts_large_networks(inlist, expected, comment):
    out = cli.expand_hosts(inlist)
    assert len(out) == expected
