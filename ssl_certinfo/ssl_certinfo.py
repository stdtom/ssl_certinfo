"""Main module."""
import json
import logging
from datetime import datetime
from socket import socket

from cryptography import x509
from cryptography.x509.oid import NameOID
from OpenSSL import SSL
from tqdm import tqdm


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


def get_certificate(hostname, port, timeout=5):
    sock = socket()
    sock.settimeout(timeout)
    sock.connect((hostname, port))
    sock.setblocking(True)

    context = SSL.Context(SSL.SSLv23_METHOD)

    context.check_hostname = False
    context.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(context, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname.encode())
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()

    sock_ssl.close()
    sock.close()

    return cert.to_cryptography()


def process_hosts(hosts, default_port, timeout=5):
    results = []

    progbar = tqdm(hosts)

    for host in progbar:
        progbar.set_description(f"Checking {host}...")
        try:
            logging.info("Trying to fetch certificate for " + host)
            cert = get_certificate(host, default_port, timeout)
        except (OSError, SSL.Error):
            logging.info("Could not fetch certificate for " + host)
        else:
            certinfo = get_cert_info(cert)

            results.append({"peername": host, "cert": certinfo})

    print(json.dumps(results, indent=4))
