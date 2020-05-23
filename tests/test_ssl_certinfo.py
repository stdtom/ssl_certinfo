#!/usr/bin/env python

"""Unit test for `ssl_certinfo` package.

Use tox or py.test to run the test suite.
"""
import os
import socket
import threading
import time
from datetime import datetime

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from OpenSSL import SSL

from ssl_certinfo import ssl_certinfo

global_sock = None


def start_tcp_server(port):
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


def setup_module(module):
    port = 12345
    daemon = threading.Thread(
        name="daemon_server", target=start_tcp_server, args=[port]
    )
    daemon.setDaemon(
        True
    )  # Set as a daemon so it will be killed once the main thread is dead.
    daemon.start()

    time.sleep(5)


def teardown_module(module):
    global_sock.shutdown(socket.SHUT_RDWR)
    global_sock.close()


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
        pytest.param(
            "localhost", 12345, "timeout on ssl handshake"  # , marks=pytest.mark.xfail
        ),
    ],
)
def test_get_certificate_fail(hostname, port, comment):
    with pytest.raises((ConnectionRefusedError, OSError, SSL.Error)):
        assert ssl_certinfo.get_certificate(hostname, port, 5)


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
    "hostname,port,comment",
    [
        ("localhost", 2, "connection rejected"),
        ("github.com", 2, "connection timeout"),
        ("github.com", 80, "no ssl on target port"),
        pytest.param(
            "localhost", 12345, "timeout on ssl handshake"  # , marks=pytest.mark.xfail
        ),
    ],
)
def test_process_hosts_timeout(capsys, hostname, port, comment):
    ssl_certinfo.process_hosts([hostname], port)

    out, err = capsys.readouterr()

    assert out == "{}\n"
