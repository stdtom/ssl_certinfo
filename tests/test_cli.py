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

    assert args.proxy == expected


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
