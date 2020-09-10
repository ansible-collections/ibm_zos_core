# -*- coding: utf-8 -*-
# Need all tests built out

from __future__ import absolute_import, division, print_function

import os
import shutil
import tempfile

__metaclass__ = type


INITIAL_PRM_MEMBER = """/* Initial file to look like BPXPRM */
/* some settings at the top */
something = something else
anotherthing = something I forgot

/* This mount shouldn't change */
MOUNT FILESYSTEM('IMSTESTU.ZZZ.KID.GA.ZFS')
      MOUNTPOINT('/python3')
      TYPE('zFS')
      MODE(RDWR)
      SETUID
      WAIT
      SECURITY
      AUTOMOVE
"""
tmp_file_filename = ''

# SHELL_EXECUTABLE = "/usr/lpp/rsusr/ported/bin/bash"
SHELL_EXECUTABLE = "/bin/sh"


def populate_tmpfile():
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    tmp_file_filename = tmp_file.name
    tmp_file.close()
    with open(tmp_file_filename, "w") as fh:
        fh.write(INITIAL_PRM_MEMBER)


def test_basic_mount(ansible_zos_module):
    hosts = ansible_zos_module
    populate_tmpfile()
    hosts.all.shell(
        cmd="cp " + tmp_file_filename + " \"//'IMSTESTU.BPX.PDS(AUTO1)" + "'\"",
        executable=SHELL_EXECUTABLE,
        stdin='',
    )
    try:
        mount_result = hosts.all.zos_mount(
            src='IMSTESTU.PYZ.V380.GA.ZFS',
            path='/python2',
            fstype='zFS',
            state='mounted'
        )
        hosts.all.shell(
            cmd="cp \"//'IMSTESTU.BPX.PDS(AUTO1)" + "'\" " + tmp_file_filename + "-a",
            executable=SHELL_EXECUTABLE,
            stdin='',
        )
        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""

    finally:
        hosts.all.file(path=tmp_file_filename, state="absent")


def test_basic_unmount(ansible_zos_module):
    hosts = ansible_zos_module
    populate_tmpfile()
    hosts.all.shell(
        cmd="cp " + tmp_file_filename + " \"//'IMSTESTU.BPX.PDS(AUTO1)" + "'\"",
        executable=SHELL_EXECUTABLE,
        stdin='',
    )
    try:
        mount_result = hosts.all.zos_mount(
            src='IMSTESTU.PYZ.V380.GA.ZFS',
            path='/python2',
            fstype='zFS',
            state='unmounted'
        )
        hosts.all.shell(
            cmd="cp \"//'IMSTESTU.BPX.PDS(AUTO1)" + "'\" " + tmp_file_filename + "-b",
            executable=SHELL_EXECUTABLE,
            stdin='',
        )
        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""

    finally:
        hosts.all.file(path=tmp_file_filename, state="absent")


def test_basic_absent(ansible_zos_module):
    hosts = ansible_zos_module
    populate_tmpfile()

    hosts.all.shell(
        cmd="cp " + tmp_file_filename + " \"//'IMSTESTU.BPX.PDS(AUTO1)" + "'\"",
        executable=SHELL_EXECUTABLE,
        stdin='',
    )
    try:
        mount_result = hosts.all.zos_mount(
            src='IMSTESTU.PYZ.V380.GA.ZFS',
            path='/python2',
            fstype='zFS',
            state='absent'
        )
        hosts.all.shell(
            cmd="cp \"//'IMSTESTU.BPX.PDS(AUTO1)" + "'\" " + tmp_file_filename + "-c",
            executable=SHELL_EXECUTABLE,
            stdin='',
        )
        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""

    finally:
        hosts.all.file(path=tmp_file_filename, state="absent")
