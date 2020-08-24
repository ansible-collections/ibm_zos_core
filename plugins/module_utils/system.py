# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from platform import platform
from os import name as OS_NAME
from sys import platform as SYS_PLATFORM


NIX_PLATFORMS = frozenset({
    "linux",
    "linux2",
    "darwin",
    "freebsd",
    "openbsd",
    "sunos",
    "netbsd"
})


def is_posix():
    """ Determine if the system is POSIX certified or compliant

    Returns:
        bool -- Whether the system is POSIX
    """
    return OS_NAME == "posix"


def is_nix():
    """ Determine if the system is a variant of Unix, supported by Python.

    Returns:
        bool -- Whether the system is Unix-based
    """
    if not is_posix():
        return False
    system_platform = platform()
    for p_name in NIX_PLATFORMS:
        if p_name in system_platform:
            return True
    return False


def is_win():
    """ Determine if the system is a Windows platform

    Returns:
        bool -- Whether the system is Windows
    """
    return "win32" in platform() or OS_NAME == "nt"


def is_zos():
    """ Determine if the system is a z/OS distribution

    Returns:
        bool -- Whether the system is z/OS
    """
    is_zos_unix = is_posix() and not is_nix()
    return is_zos_unix and SYS_PLATFORM == "zos"
