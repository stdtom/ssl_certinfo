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
        "1.0.0.1/8",
        "1.0.0.1/255.0.0.0",
        "4.4.0.0/16",
        "4.4.0.0/255.255.0.0",
        "192.0.2.0/24",
        "192.0.2.0/255.255.255.0",
    ],
)
def test_valid_ip_network(test_input):
    assert validation.is_valid_ip_network(test_input)


@pytest.mark.parametrize("test_input", ["10.0.0.1", "10.0.0.1/33"])
def test_invalid_ip_network(test_input):
    assert not validation.is_valid_ip_network(test_input)


@pytest.mark.parametrize(
    "test_input", ["10.0.0.1 - 10.0.0.5", "192.168.0.1-192.168.1.255"]
)
def test_valid_ip_range(test_input):
    assert validation.is_valid_ip_range(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "10.0.0.1",  # single ip address, no range
        "10.0.0.0/24",  # ip network in cidr
        "10.0.0.5 - 10.0.0.1",  # start ip greater than end ip
        "192.168.0.1-192.168.0.1",  # range of only one ip address
        "10.0.0.1/32 - 10.0.0.5",  # start ip is cidr
        "a.b.c - 1.1.1.1",  # start is not a valid ip
        "abcdexx",  # characters
    ],
)
def test_invalid_ip_range(test_input):
    assert not validation.is_valid_ip_range(test_input)


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
