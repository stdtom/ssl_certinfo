#!/usr/bin/env python

"""Unit test for `ssl_certinfo` package.

Use tox or py.test to run the test suite.
"""
import os
import re
import socket
import threading
import time
from datetime import datetime

import proxy
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from OpenSSL import SSL

from ssl_certinfo import ssl_certinfo
from ssl_certinfo.ssl_certinfo import OutputFormat

global_sock = None
proxydaemon = None
stop_proxy = False


def start_web_server(port):
    global global_sock
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        global_sock = s

        while True:
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                conn.close()


def start_proxy(port):
    global stop_proxy
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)

    with proxy.start(["--hostname", HOST, "--port", str(port), "--num-workers", "1"]):
        while not stop_proxy:
            time.sleep(2)


def setup_module(module):
    global proxydaemon
    webserver_port = 12345
    proxy_port = 8899

    webdaemon = threading.Thread(
        name="webdaemon_server",
        target=start_web_server,
        args=[webserver_port],
        daemon=True,
    )  # Set as a daemon so it will be killed once the main thread is dead.
    webdaemon.start()

    proxydaemon = threading.Thread(
        name="proxydaemon_server", target=start_proxy, args=[proxy_port], daemon=True
    )  # Set as a daemon so it will be killed once the main thread is dead.
    proxydaemon.start()

    time.sleep(5)


def teardown_module(module):
    global global_sock
    global proxydaemon
    global stop_proxy

    try:
        global_sock.shutdown(socket.SHUT_RDWR)
    except (socket.error, OSError, ValueError):
        pass
    global_sock.close()

    stop_proxy = True
    proxydaemon.join()


@pytest.fixture
def sample_result():
    certinfo = {
        "CN": "github.com",
        "SAN": "github.com;www.github.com",
        "valid_from": "2018-05-08T00:00:00",
        "valid_to": "2020-06-03T12:00:00",
        "expire_in_days": (datetime(2020, 6, 3, 12, 0, 0) - datetime.now()).days,
        "peername": "github.com",
        "peerport": 443,
    }

    return {"github.com": certinfo}


def test_get_cert_info():
    """Test that get_cert_info returns expected attributes for a given certificate."""
    github_cert_str = """\
-----BEGIN CERTIFICATE-----
MIIHQjCCBiqgAwIBAgIQCgYwQn9bvO1pVzllk7ZFHzANBgkqhkiG9w0BAQsFADB1
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMTQwMgYDVQQDEytEaWdpQ2VydCBTSEEyIEV4dGVuZGVk
IFZhbGlkYXRpb24gU2VydmVyIENBMB4XDTE4MDUwODAwMDAwMFoXDTIwMDYwMzEy
MDAwMFowgccxHTAbBgNVBA8MFFByaXZhdGUgT3JnYW5pemF0aW9uMRMwEQYLKwYB
BAGCNzwCAQMTAlVTMRkwFwYLKwYBBAGCNzwCAQITCERlbGF3YXJlMRAwDgYDVQQF
Ewc1MTU3NTUwMQswCQYDVQQGEwJVUzETMBEGA1UECBMKQ2FsaWZvcm5pYTEWMBQG
A1UEBxMNU2FuIEZyYW5jaXNjbzEVMBMGA1UEChMMR2l0SHViLCBJbmMuMRMwEQYD
VQQDEwpnaXRodWIuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
xjyq8jyXDDrBTyitcnB90865tWBzpHSbindG/XqYQkzFMBlXmqkzC+FdTRBYyneZ
w5Pz+XWQvL+74JW6LsWNc2EF0xCEqLOJuC9zjPAqbr7uroNLghGxYf13YdqbG5oj
/4x+ogEG3dF/U5YIwVr658DKyESMV6eoYV9mDVfTuJastkqcwero+5ZAKfYVMLUE
sMwFtoTDJFmVf6JlkOWwsxp1WcQ/MRQK1cyqOoUFUgYylgdh3yeCDPeF22Ax8AlQ
xbcaI+GwfQL1FB7Jy+h+KjME9lE/UpgV6Qt2R1xNSmvFCBWu+NFX6epwFP/JRbkM
fLz0beYFUvmMgLtwVpEPSwIDAQABo4IDeTCCA3UwHwYDVR0jBBgwFoAUPdNQpdag
re7zSmAKZdMh1Pj41g8wHQYDVR0OBBYEFMnCU2FmnV+rJfQmzQ84mqhJ6kipMCUG
A1UdEQQeMByCCmdpdGh1Yi5jb22CDnd3dy5naXRodWIuY29tMA4GA1UdDwEB/wQE
AwIFoDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwdQYDVR0fBG4wbDA0
oDKgMIYuaHR0cDovL2NybDMuZGlnaWNlcnQuY29tL3NoYTItZXYtc2VydmVyLWcy
LmNybDA0oDKgMIYuaHR0cDovL2NybDQuZGlnaWNlcnQuY29tL3NoYTItZXYtc2Vy
dmVyLWcyLmNybDBLBgNVHSAERDBCMDcGCWCGSAGG/WwCATAqMCgGCCsGAQUFBwIB
FhxodHRwczovL3d3dy5kaWdpY2VydC5jb20vQ1BTMAcGBWeBDAEBMIGIBggrBgEF
BQcBAQR8MHowJAYIKwYBBQUHMAGGGGh0dHA6Ly9vY3NwLmRpZ2ljZXJ0LmNvbTBS
BggrBgEFBQcwAoZGaHR0cDovL2NhY2VydHMuZGlnaWNlcnQuY29tL0RpZ2lDZXJ0
U0hBMkV4dGVuZGVkVmFsaWRhdGlvblNlcnZlckNBLmNydDAMBgNVHRMBAf8EAjAA
MIIBfgYKKwYBBAHWeQIEAgSCAW4EggFqAWgAdgCkuQmQtBhYFIe7E6LMZ3AKPDWY
BPkb37jjd80OyA3cEAAAAWNBYm0KAAAEAwBHMEUCIQDRZp38cTWsWH2GdBpe/uPT
Wnsu/m4BEC2+dIcvSykZYgIgCP5gGv6yzaazxBK2NwGdmmyuEFNSg2pARbMJlUFg
U5UAdgBWFAaaL9fC7NP14b1Esj7HRna5vJkRXMDvlJhV1onQ3QAAAWNBYm0tAAAE
AwBHMEUCIQCi7omUvYLm0b2LobtEeRAYnlIo7n6JxbYdrtYdmPUWJQIgVgw1AZ51
vK9ENinBg22FPxb82TvNDO05T17hxXRC2IYAdgC72d+8H4pxtZOUI5eqkntHOFeV
CqtS6BqQlmQ2jh7RhQAAAWNBYm3fAAAEAwBHMEUCIQChzdTKUU2N+XcqcK0OJYrN
8EYynloVxho4yPk6Dq3EPgIgdNH5u8rC3UcslQV4B9o0a0w204omDREGKTVuEpxG
eOQwDQYJKoZIhvcNAQELBQADggEBAHAPWpanWOW/ip2oJ5grAH8mqQfaunuCVE+v
ac+88lkDK/LVdFgl2B6kIHZiYClzKtfczG93hWvKbST4NRNHP9LiaQqdNC17e5vN
HnXVUGw+yxyjMLGqkgepOnZ2Rb14kcTOGp4i5AuJuuaMwXmCo7jUwPwfLe1NUlVB
Kqg6LK0Hcq4K0sZnxE8HFxiZ92WpV2AVWjRMEc/2z2shNoDvxvFUYyY1Oe67xINk
myQKc+ygSBZzyLnXSFVWmHr3u5dcaaQGGAR42v6Ydr4iL38Hd4dOiBma+FXsXBIq
WUjbST4VXmdaol7uzFMojA4zkxQDZAvF5XgJlAFadfySna/teik=
-----END CERTIFICATE-----
"""

    github_cert_obj = load_pem_x509_certificate(
        str.encode(github_cert_str), default_backend()
    )

    expected = {
        "CN": "github.com",
        "SAN": "github.com;www.github.com",
        "valid_from": "2018-05-08T00:00:00",
        "valid_to": "2020-06-03T12:00:00",
    }
    expected["expire_in_days"] = (datetime(2020, 6, 3, 12, 0, 0) - datetime.now()).days

    cert_info = ssl_certinfo.get_cert_info(github_cert_obj)

    assert cert_info["SAN"] == expected["SAN"]
    assert cert_info == expected


@pytest.mark.parametrize(
    "hostname,port,expected",
    [
        ("github.com", 443, "github.com"),
        ("google.com", 443, "google.com"),
        ("1.1.1.1", 443, "cloudflare"),
        ("imap.gmail.com", 993, "gmail.com"),
        ("pop.gmail.com", 995, "gmail.com"),
    ],
)
def test_get_certificate_success(hostname, port, expected):
    cert = ssl_certinfo.get_certificate(hostname, port)

    assert cert
    assert (
        cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value.find(expected)
        >= 0
    )


@pytest.mark.timeout(15)
@pytest.mark.parametrize(
    "hostname,port,comment",
    [
        ("localhost", 2, "connection rejected"),
        ("github.com", 2, "connection timeout"),
        ("github.com", 80, "no ssl on target port"),
        ("github.nodomain", 443, "dns lookup failure"),
        pytest.param(
            "localhost", 12345, "timeout on ssl handshake"  # , marks=pytest.mark.xfail
        ),
    ],
)
def test_get_certificate_fail(hostname, port, comment):
    with pytest.raises((ConnectionRefusedError, OSError, SSL.Error)):
        assert ssl_certinfo.get_certificate(hostname, port, 5)


@pytest.mark.parametrize(
    "hostname,port,proxy,expected",
    [
        (
            "github.com",
            443,
            ("http", "localhost", 8899),
            "github.com",
        ),
        (
            "1.1.1.1",
            443,
            ("http", "localhost", 8899),
            "cloudflare",
        ),
    ],
)
def test_get_certificate_with_proxy_success(hostname, port, proxy, expected):
    cert = ssl_certinfo.get_certificate(hostname, port, proxy=proxy)

    assert cert
    assert (
        cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value.find(expected)
        >= 0
    )


@pytest.mark.parametrize(
    "hostname,port,proxy,comment",
    [
        (
            "github.com",
            443,
            ("http", "localhost", 12345),
            "github.com",
        ),
        (
            "1.1.1.1",
            443,
            ("http", "localhost", 12345),
            "cloudflare",
        ),
    ],
)
def test_get_certificate_with_proxy_fail(hostname, port, proxy, comment):
    with pytest.raises((ConnectionRefusedError, OSError, SSL.Error)):
        assert ssl_certinfo.get_certificate(hostname, port, 5, proxy)


@pytest.mark.skipif(
    ("TRAVIS" not in os.environ) or (os.environ["TRAVIS"] != "true"),
    reason="Skip test if not running on travis-ci.com",
)
@pytest.mark.parametrize("timeout", [2, 5, 8])
def test_get_certificate_valid_timeout(timeout):
    start = datetime.now()
    try:
        ssl_certinfo.get_certificate("github.com", 2, timeout)
    except (ConnectionRefusedError, OSError):
        pass
    finally:
        end = datetime.now()
        delta = end - start

        assert abs(delta.seconds - timeout) < 1


def test_process_hosts(capsys):
    hosts = ["github.com", "wikipedia.org"]
    ssl_certinfo.process_hosts(hosts, 443)

    out, err = capsys.readouterr()

    assert out.find("github") >= 0
    assert out.find("wikipedia") >= 0


@pytest.mark.timeout(15)
@pytest.mark.parametrize(
    "hostname,port,error,comment",
    [
        ("localhost", 2, "Connection refused", "connection rejected"),
        ("github.com", 2, "Timeout", "connection timeout"),
        ("github.com", 80, "Timeout", "no ssl on target port"),
        ("github.nodomain", 443, "Cannot resolve hostname", "dns resolution error"),
        pytest.param(
            "localhost",
            12345,
            "Timeout",
            "timeout on ssl handshake",  # , marks=pytest.mark.xfail
        ),
    ],
)
def test_process_hosts_timeout(capsys, hostname, port, error, comment):
    ssl_certinfo.process_hosts([hostname], port)

    out, err = capsys.readouterr()

    assert out.find(error) >= 0


@pytest.mark.parametrize(
    "outform,expected",
    [
        (
            OutputFormat.TABLE,
            r"\+-[\+-]+-\+(\r)?\n"
            r"\| +peer +\| +CN +\| +SAN +\| +valid_from +\| +valid_to +\| +"
            r"expire_in_days +\| +peername +\| +peerport +\| +error +\|(\r)?\n"
            r"\+-[\+-]+-\+(\r)?\n"
            r"\| +github.com +\| +github.com +\| +github.com;www.github.com +\| +"
            r"2018-05-08T00:00:00 +\| +"
            r"2020-06-03T12:00:00 +\| +"
            r"-?[0-9]+ +\| +github.com +\| +443 +\| +. +\|(\r)?\n"
            r"\+-[\+-]+-\+",
        ),
        (
            OutputFormat.JSON,
            "{(\r)?\n"
            ' +"github.com": {(\r)?\n'
            ' +"CN": "github.com",(\r)?\n'
            ' +"SAN": "github.com;www.github.com",(\r)?\n'
            ' +"valid_from": "2018-05-08T00:00:00",(\r)?\n'
            ' +"valid_to": "2020-06-03T12:00:00",(\r)?\n'
            ' +"expire_in_days": -?[0-9]+,(\r)?\n'
            ' +"peername": "github.com",(\r)?\n'
            ' +"peerport": 443(\r)?\n'
            " +}(\r)?\n"
            "}",
        ),
        (
            OutputFormat.YAML,
            "github.com:(\r)?\n"
            "  CN: github.com(\r)?\n"
            "  SAN: github.com;www.github.com(\r)?\n"
            "  expire_in_days: -?[0-9]+(\r)?\n"
            "  peername: github.com(\r)?\n"
            "  peerport: 443(\r)?\n"
            "  valid_from: '2018-05-08T00:00:00'(\r)?\n"
            "  valid_to: '2020-06-03T12:00:00'(\r)?\n",
        ),
        (
            OutputFormat.CSV,
            "peer,CN,SAN,valid_from,valid_to,expire_in_days,"
            "peername,peerport,error(\r)?\n"
            "github.com,github.com,github.com;www.github.com,2018-05-08T00:00:00,"
            "2020-06-03T12:00:00,-?[0-9]+,github.com,443,-",
        ),
        (
            OutputFormat.RAW,
            "peer +CN +SAN +valid_from +valid_to +expire_in_days +"
            "peername +peerport +error"
            "(\r)?\n"
            "github.com +github.com +github.com;www.github.com +2018-05-08T00:00:00 +"
            "2020-06-03T12:00:00 +-?[0-9]+ +github.com +443 +-",
        ),
    ],
)
def test_format_results(sample_result, outform, expected):
    outstr = ssl_certinfo.format_results(sample_result, outform)
    assert re.match(expected, outstr)


@pytest.mark.parametrize(
    "outform,expected",
    [
        (OutputFormat.TABLE, ""),
        (OutputFormat.JSON, ""),
        (OutputFormat.YAML, ""),
        (OutputFormat.CSV, ""),
        (OutputFormat.RAW, ""),
    ],
)
def test_format_results_empty(outform, expected):
    outstr = ssl_certinfo.format_results({}, outform)
    assert outstr == ""
