#!/usr/bin/env python

"""Unit test for `validation` package.

Use tox or py.test to run the test suite.
"""

import pytest

from ssl_certinfo import validation


@pytest.mark.parametrize("test_input", ["1.0.0.1", "255.255.255.255"])
def test_valid_ip_address(test_input):
    assert validation.is_valid_ip_address(test_input)


@pytest.mark.parametrize("test_input", ["10.0.0.-1", "10.0.0.1/33"])
def test_invalid_ip_address(test_input):
    assert not validation.is_valid_ip_address(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "github.com",
        "www." + ("abcdefghi" * 7) + ".com",  # second level domain with 63 chars
        ("abcdefghi" * 7 + ".") * 3,  # 3 labels with 63 chars plus trailing '.'
        ("a" * 49 + ".") * 5 + "com",  # total length 253 chars
        "abc.com",
    ],
)
def test_valid_hostname(test_input):
    assert validation.is_valid_hostname(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "www." + ("abcdefghi" * 7) + "x.com",  # second level domain with 64 chars
        ("a" * 49 + ".") * 5 + "xcom",  # total length 254 chars
        "-abc.com",
        "abc-.com",
        "-abc-.com",
        "abc.-com",
        "abc.com-",
        "abc.-com-",
        "10.0.0.-1",
        "10.0.0.1/33",
        "10.0.0.1",
        "255.255.255.255",
    ],
)
def test_invalid_hostname(test_input):
    assert not validation.is_valid_hostname(test_input)
