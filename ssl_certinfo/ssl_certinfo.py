"""Main module."""
import enum
import json
import logging
import time
from datetime import datetime
from socket import socket

import pandas as pd
import yaml
from cryptography import x509
from cryptography.x509.oid import NameOID
from OpenSSL import SSL
from OpenSSL.SSL import WantReadError, WantWriteError
from tabulate import tabulate
from tqdm import tqdm


class OutputFormat(enum.Enum):
    TABLE = 1
    JSON = 2
    YAML = 3
    CSV = 4
    RAW = 5


def get_cert_info(cert):
    """Get all information about SSL certificate ."""
    certinfo = {}

    certinfo["CN"] = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

    ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    san_list = ext.value.get_values_for_type(x509.DNSName)
    certinfo["SAN"] = ";".join(san_list)

    certinfo["valid_from"] = cert.not_valid_before.isoformat()
    certinfo["valid_to"] = cert.not_valid_after.isoformat()

    delta = cert.not_valid_after - datetime.now()
    certinfo["expire_in_days"] = delta.days

    return certinfo


def ssl_handshake_helper(sock_ssl):
    timeout = sock_ssl.gettimeout()
    if timeout is not None:
        start = time.time()
    while True:
        try:
            return sock_ssl.do_handshake()
        except (WantReadError, WantWriteError):
            if start + timeout <= time.time():
                raise TimeoutError


def get_certificate(hostname, port, timeout=5, proxy=None):
    loglocal = logging.getLogger("ssl_certinfo.get_certificate")
    loglocal.debug("Start get_certificate")
    sock = socket()
    loglocal.debug("Setting socket timeout to {}".format(timeout))
    sock.settimeout(timeout)
    if proxy:
        PROXY_ADDR = proxy[1:]

        CONNECT = "CONNECT {}:{} HTTP/1.0\r\nConnection: close\r\n\r\n".format(
            hostname, port,
        )

        loglocal.debug("Connecting to proxy {}".format(PROXY_ADDR))
        sock.connect(PROXY_ADDR)
        loglocal.debug("Connected to proxy")

        loglocal.debug("Sending '{}'".format(CONNECT.encode()))
        sock.send(CONNECT.encode())
        response = sock.recv(4096)
        loglocal.debug("Proxy responds '{}'".format(response))
    else:
        TARGET_ADDR = (hostname, port)
        loglocal.debug("Connecting to target {}".format(TARGET_ADDR))
        sock.connect(TARGET_ADDR)
        loglocal.debug("Connected to target")

    loglocal.debug("Create SSL context")
    context = SSL.Context(SSL.SSLv23_METHOD)

    context.check_hostname = False
    context.verify_mode = SSL.VERIFY_NONE

    loglocal.debug("Starting SSL handshake")
    sock_ssl = SSL.Connection(context, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname.encode())
    ssl_handshake_helper(sock_ssl)
    loglocal.debug("SSL handshake completed")

    cert = sock_ssl.get_peer_certificate()
    loglocal.debug("Certificate received. Closing socckets")

    sock_ssl.close()
    sock.close()
    loglocal.debug("Sockets closed")

    loglocal.debug("get_certificate completed")
    return cert.to_cryptography()


def result_to_dataframe(result_dict):
    column_names = [
        "CN",
        "SAN",
        "valid_from",
        "valid_to",
        "expire_in_days",
        "peername",
        "peerport",
    ]
    df = pd.DataFrame(result_dict).T.rename_axis("peer", axis=1)
    df = df.reindex(columns=column_names)

    return df


def process_hosts(
    hosts, default_port, timeout=5, outform=OutputFormat.TABLE, proxy=None
):
    results = {}

    progbar = tqdm(hosts)

    for host in progbar:
        progbar.set_description(f"Checking {host}...")
        try:
            logging.info("Trying to fetch certificate for " + host)
            cert = get_certificate(host, default_port, timeout, proxy)
        except (OSError, SSL.Error):
            logging.info("Could not fetch certificate for " + host)
        else:
            certinfo = get_cert_info(cert)
            certinfo["peername"] = host
            certinfo["peerport"] = default_port

            results[host] = certinfo
    print(format_results(results, outform))


def format_results(results, outform):
    if results == {}:
        return ""

    elif outform == OutputFormat.TABLE:
        df = result_to_dataframe(results)
        df.index.name = "peer"
        return tabulate(df, headers="keys", tablefmt="pretty")

    elif outform == OutputFormat.JSON:
        return json.dumps(results, indent=4)

    elif outform == OutputFormat.YAML:
        return yaml.dump(results)

    elif outform == OutputFormat.CSV:
        df = result_to_dataframe(results)
        df.index.name = "peer"
        return df.to_csv()

    elif outform == OutputFormat.RAW:
        df = result_to_dataframe(results)
        return df.to_string()
