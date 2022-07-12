#!/usr/bin/env python

"""Unit test for `ssl_certinfo.cli` module - tests concerning external invokation.

Use tox or py.test to run the test suite.
"""

import os
import subprocess

import pytest

from ssl_certinfo import __author__, __email__, __version__


def capture(command):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


@pytest.mark.skipif(
    ("TRAVIS_OS_NAME" in os.environ)
    and (os.environ["TRAVIS_OS_NAME"] == "windows")
    or ("AGENT_OS" in os.environ)
    and (os.environ["AGENT_OS"] == "Windows_NT"),
    reason="Skip test if running on Windows",
)
def test_cli_main_version():
    command = "python -m ssl_certinfo -V".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find(__version__) >= 0
    assert out.decode().find(__author__) >= 0
    assert out.decode().find(__email__) >= 0


@pytest.mark.skipif(
    ("TRAVIS_OS_NAME" in os.environ)
    and (os.environ["TRAVIS_OS_NAME"] == "windows")
    or ("AGENT_OS" in os.environ)
    and (os.environ["AGENT_OS"] == "Windows_NT"),
    reason="Skip test if running on Windows",
)
def test_cli_main_single_target():
    command = "python -m ssl_certinfo github.com".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find("github") >= 0
    assert (err == b"") or (err.decode().find("100%") >= 0)


@pytest.mark.skipif(
    ("TRAVIS_OS_NAME" in os.environ)
    and (os.environ["TRAVIS_OS_NAME"] == "windows")
    or ("AGENT_OS" in os.environ)
    and (os.environ["AGENT_OS"] == "Windows_NT"),
    reason="Skip test if running on Windows",
)
def test_cli_main_two_targets():
    command = "python -m ssl_certinfo github.com wikipedia.org".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find("github") >= 0
    assert out.decode().find("wikipedia") >= 0
    assert (err == b"") or (err.decode().find("100%") >= 0)


@pytest.mark.skipif(
    ("TRAVIS_OS_NAME" in os.environ)
    and (os.environ["TRAVIS_OS_NAME"] == "windows")
    or ("AGENT_OS" in os.environ)
    and (os.environ["AGENT_OS"] == "Windows_NT"),
    reason="Skip test if running on Windows",
)
def test_cli_main_hostfile():
    command = "python -m ssl_certinfo @tests/test_data/test_hostlist.txt".split(" ")
    out, err, exitcode = capture(command)
    assert exitcode == 0
    assert out.decode().find("github") >= 0
    assert out.decode().find("wikipedia") >= 0
    assert (err == b"") or (err.decode().find("100%") >= 0)
