============
SSL CertInfo
============

.. start-badges

.. list-table::
    :stub-columns: 1

    * - build
      - |travis|
    * - quality
      - |codacy| |codeclimate| |sonar-qg| |sonar-rel|
    * - coverage
      - |coveralls| |codecov| |codeclimate-cov|
    * - dependencies
      - |pyup| |pyup-p3| |requires|
    * - package
      - |version| |pyversions| |downloads|


.. |travis| image:: https://img.shields.io/travis/stdtom/ssl_certinfo/master.svg?logo=travis
   :target: https://travis-ci.com/stdtom/ssl_certinfo
   :alt: Travis Build Status

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/589c03a215ec4ddbb0085b523a857e55
   :target: https://www.codacy.com/manual/stdtom/ssl_certinfo
   :alt: Codacy Grade

.. |codeclimate| image:: https://api.codeclimate.com/v1/badges/1ed86e874b3c68672c5c/maintainability
   :target: https://codeclimate.com/github/stdtom/ssl_certinfo/maintainability
   :alt: Code Climate Maintainability

.. |sonar-qg| image:: https://sonarcloud.io/api/project_badges/measure?project=stdtom_ssl_certinfo&metric=alert_status
   :target: https://sonarcloud.io/dashboard?id=stdtom_ssl_certinfo
   :alt: Sonar Quality Gate Status

.. |sonar-rel| image:: https://sonarcloud.io/api/project_badges/measure?project=stdtom_ssl_certinfo&metric=reliability_rating
   :target: https://sonarcloud.io/dashboard?id=stdtom_ssl_certinfo
   :alt: Sonar Reliability Rating

.. |coveralls| image:: https://coveralls.io/repos/github/stdtom/ssl_certinfo/badge.svg?branch=master
   :target: https://coveralls.io/github/stdtom/ssl_certinfo?branch=master
   :alt: Coveralls Test Coverage

.. |codecov| image:: https://codecov.io/gh/stdtom/ssl_certinfo/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stdtom/ssl_certinfo
   :alt: CodeCov

.. |codeclimate-cov| image:: https://api.codeclimate.com/v1/badges/1ed86e874b3c68672c5c/test_coverage
   :target: https://codeclimate.com/github/stdtom/ssl_certinfo/test_coverage
   :alt: Code Climate Test Coverage

.. |pyup| image:: https://pyup.io/repos/github/stdtom/ssl_certinfo/shield.svg
   :target: https://pyup.io/repos/github/stdtom/ssl_certinfo/
   :alt: Updates

.. |pyup-p3| image:: https://pyup.io/repos/github/stdtom/ssl_certinfo/python-3-shield.svg
   :target: https://pyup.io/repos/github/stdtom/ssl_certinfo/
   :alt: Python 3

.. |requires| image:: https://requires.io/github/stdtom/ssl_certinfo/requirements.svg?branch=master
   :target: https://requires.io/github/stdtom/ssl_certinfo/requirements/?branch=master
   :alt: Requirements Status

.. |version| image:: https://img.shields.io/pypi/v/ssl-certinfo.svg
   :target: https://pypi.org/project/ssl-certinfo/
   :alt: Version

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/ssl-certinfo.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/ssl-certinfo/
    :alt: Python versions supported

.. |downloads| image:: https://pepy.tech/badge/ssl-certinfo
    :target: https://pepy.tech/project/ssl-certinfo
    :alt: PyPI downloads

.. end-badges


SSL CertInfo collects information about SSL certificates from a set of hosts.


Features
--------

* Hosts to be scanned can be specified as a list of

  * hostnames (fully qualified domain names), e.g. ``github.com``,
  * ip addresses, e.g. ``1.1.1.1``,
  * ip networks in CIDR format, e.g. ``10.0.0.0/24``,
  * ip ranges, e.g. ``10.0.0.1-10.0.0.10``,
  * or any combination of the previous.

* Connect to target hosts via an http proxy (optional).

* Results will be presented in various output formats: ``--table``, ``--json``, ``--yaml``, ``--csv``, ``--raw``.


Installation
------------
You can download and install the latest version of this software from the Python package index (PyPI) as follows::

  $ pip install ssl_certinfo


Usage
-----

When you install ssl_certinfo, a command-line script called ``ssl_certinfo`` is
placed on your path. You can invoke ssl_certinfo directly via this script from the command line::

  $ ssl_certinfo [...]


You can also invoke it through the Python interpreter from the command line::

  $ python -m ssl_certinfo [...]


Help is available with the ``--help`` or ``-h`` switch::

  $ ssl_certinfo -h
  usage: ssl_certinfo [-h] [-V] [-v | -q] [-p PORT] [-t TIMEOUT] [-x [protocol://]host[:port]] [-T | -j | -y | -c | -r] [host [host ...]]

  Collect information about SSL certificates from a set of hosts

  positional arguments:
  host                  Connect to HOST

  optional arguments:
  -h, --help            show this help message and exit
  -V, --version         display version information and exit
  -v, --verbose         verbose output (repeat for increased verbosity)
  -q, --quiet           quiet output (show errors only)
  -p PORT, --port PORT  TCP port to connnect to [0-65535]
  -t TIMEOUT, --timeout TIMEOUT
                        Maximum time allowed for connection
  -x [protocol://]host[:port], --proxy [protocol://]host[:port]
                        Use the specified proxy
  -T, --table           Print results in table format
  -j, --json            Print results in JSON format
  -y, --yaml            Print results in YAML format
  -c, --csv             Print results in CSV format
  -r, --raw             Print results in raw format


Proxy
-----

Optionally an http proxy can be specified which will be used to connect to the target hosts. The proxy can be
specified using the ``-x, --proxy`` option or using one of the following environment variables:

* ``http_proxy``
* ``HTTP_PROXY``
* ``https_proxy``
* ``HTTPS_PROXY``

The environment variables can be specified in lower case or upper case. The lower case version has precedence.

The ``-x, --proxy`` option overrides existing environment variables that set the proxy to use.
If there's an environment variable setting a proxy, you can use  ``-x ""`` to override it.


Credits
-------

This package was created with Cookiecutter_ and the `stdtom/cookiecutter-pypackage-pipenv`_ project template, based on `audreyr/cookiecutter-pypackage`_.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`stdtom/cookiecutter-pypackage-pipenv`: https://github.com/stdtom/cookiecutter-pypackage-pipenv
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
