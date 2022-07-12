#!/usr/bin/env python

"""Unit test for `ssl_certinfo.cli` module - tests concerning argparse.

Use tox or py.test to run the test suite.
"""

import sys

import pytest

from ssl_certinfo import cli
from ssl_certinfo.ssl_certinfo import OutputFormat


@pytest.fixture
def parser():
    return cli.create_parser()


@pytest.mark.parametrize(
    "args,expected,comment",
    [
        (["github.com"], None, "default no proxy"),
        (
            ["github.com", "-x", "http://cli.proxy.org:8080"],
            ("http", "cli.proxy.org", 8080),
            "valid proxy",
        ),
    ],
)
def test_cli_valid_proxy_url(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    args = parser.parse_args(args)
    assert args.proxy == expected


@pytest.mark.parametrize(
    "args,expected,comment",
    [(["github.com", "-x", "ftp://myproxy.domain.org:8080"], None, "invalid proxy")],
)
def test_cli_invalid_proxy_url(parser, args, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    with pytest.raises(SystemExit):
        args = parser.parse_args(args)


@pytest.mark.parametrize(
    "args,env,expected,comment",
    [
        (["github.com"], None, None, "default, no proxy set"),
        (
            ["github.com"],
            ("http_proxy", "env.proxy.org:8080"),
            ("http", "env.proxy.org", 8080),
            "http_proxy",
        ),
        (
            ["github.com"],
            ("https_proxy", "env.proxy.org:8080"),
            ("http", "env.proxy.org", 8080),
            "https_proxy",
        ),
        (
            ["github.com"],
            ("HTTP_PROXY", "env.proxy.org:8080"),
            ("http", "env.proxy.org", 8080),
            "HTTP_PROXY",
        ),
        (
            ["github.com"],
            ("HTTPS_PROXY", "env.proxy.org:8080"),
            ("http", "env.proxy.org", 8080),
            "HTTPS_PROXY",
        ),
        (
            ["github.com", "-x", "cli.proxy.org:8080"],
            ("http_proxy", "http://env.proxy.org:8080"),
            ("http", "cli.proxy.org", 8080),
            "cli overwrites http_proxy env variable",
        ),
        (
            ["github.com", "-x", "cli.proxy.org:8080"],
            ("http_proxys", "http://env.proxy.org:8080"),
            ("http", "cli.proxy.org", 8080),
            "cli overwrites http_proxys env variable",
        ),
        (
            ["github.com", "-x", "cli.proxy.org:8080"],
            ("HTTP_PROXY", "http://env.proxy.org:8080"),
            ("http", "cli.proxy.org", 8080),
            "cli overwrites HTTP_PROXY env variable",
        ),
        (
            ["github.com", "-x", "cli.proxy.org:8080"],
            ("HTTPS_PROXY", "http://env.proxy.org:8080"),
            ("http", "cli.proxy.org", 8080),
            "cli overwrites HTTPS_PROXY env variable",
        ),
        (
            ["github.com", "-x", ""],
            ("http_proxy", "http://env.proxy.org:8080"),
            None,
            "unset http_proxy env variable with option -x",
        ),
    ],
)
def test_cli_valid_proxy_url_with_env(monkeypatch, args, env, expected, comment):
    """Sample pytest test function with the pytest fixture as an argument."""
    if env:
        monkeypatch.setenv(env[0], env[1])

    # Do NOT use parser fixture here as in other test_cli_* test cases.
    # Fixture is being created before environment variable is monkeypatched.
    args = cli.create_parser().parse_args(args)

    assert args.proxy == expected


@pytest.mark.parametrize(
    "env1,prio1",
    [("http_proxy", 1), ("HTTP_PROXY", 2), ("https_proxy", 3), ("HTTPS_PROXY", 4)],
)
@pytest.mark.parametrize(
    "env2,prio2",
    [("http_proxy", 1), ("HTTP_PROXY", 2), ("https_proxy", 3), ("HTTPS_PROXY", 4)],
)
def test_cli_proxy_env_priority(monkeypatch, env1, prio1, env2, prio2):
    """Sample pytest test function with the pytest fixture as an argument."""
    args = ["github.com"]
    proxy_url1 = "{}:8080".format(env1).replace("_", "")
    proxy_url2 = "{}:8080".format(env2).replace("_", "")
    if prio1 <= prio2:
        expected = ("http", env1.replace("_", ""), 8080)
    else:
        expected = ("http", env2.replace("_", ""), 8080)

    monkeypatch.setenv(env1, proxy_url1)
    monkeypatch.setenv(env2, proxy_url2)

    # Do NOT use parser fixture here as in other test_cli_* test cases.
    # Fixture is being created before environment variable is monkeypatched.
    args = cli.create_parser().parse_args(args)

    if sys.platform == "win32":
        args.proxy = (args.proxy[0], args.proxy[1].upper(), args.proxy[2])
        expected = (expected[0], expected[1].upper(), expected[2])

    assert args.proxy == expected


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
