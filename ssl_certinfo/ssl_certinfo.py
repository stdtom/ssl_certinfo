"""Main module."""
from datetime import datetime

from cryptography import x509
from cryptography.x509.oid import NameOID


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
