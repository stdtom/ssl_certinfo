"""Main module for SSL CertInfo."""

import sys

if __name__ == "__main__":
    import ssl_certinfo.cli

    sys.exit(ssl_certinfo.cli.main())  # pragma: no cover
