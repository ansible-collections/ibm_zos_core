# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import tempfile
import pprint

from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    DataSet,
)

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

# SHELL_EXECUTABLE = "/usr/lpp/rsusr/ported/bin/bash"
SHELL_EXECUTABLE = "/bin/sh"


def get_sysname(hosts):
    results = hosts.all.shell(
        cmd="sysvar SYSNAME",
        executable=SHELL_EXECUTABLE,
        stdin="",
    )
    response = ""
    for result in results:
        if len(result) > 2:
            response = result
            break
    return response


def populate_tmpfile():
    tmp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    tmp_file_filename = tmp_file.name
    # tmp_file.close()
    # with open(tmp_file_filename, "w") as fh:
    tmp_file.write(INITIAL_PRM_MEMBER)
    return tmp_file_filename


def create_sourcefile(hosts, volume):
    # returns un-escaped source file name, but uses escaped file name for shell commands
    # this is intentionally done to test escaping of data set names
    starter = get_sysname(hosts).split(".")[0].upper()
    if len(starter) < 2:
        starter = "IMSTESTU"
    basefile = starter + ".ATO.MNT.ZFS"
    thisfile = DataSet.escape_data_set_name(basefile)
    print(
        "\ncsf: starter={0} thisfile={1} is type {2}".format(
            starter, thisfile, str(type(thisfile))
        )
    )
    pp = pprint.PrettyPrinter(indent=4)

    mount_result = hosts.all.shell(
        cmd="zfsadm define -aggregate "
        + thisfile
        + " -volumes {0} -cylinders 200 1".format(volume),
        executable=SHELL_EXECUTABLE,
        stdin="",
    )
    for result in mount_result.values():
        print( "\ncreate mount/define result: " )
        pp.pprint( result )
        print( "\n")

    mount_result = hosts.all.shell(
        cmd="zfsadm format -aggregate " + thisfile,
        executable=SHELL_EXECUTABLE,
        stdin="",
    )
    for result in mount_result.values():
        print( "\ncreate mount/format result: " )
        pp.pprint( result )
        print( "\n")

    return basefile


def test_basic_mount(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    srcfn = create_sourcefile(hosts, volume_1)
    try:
        pp = pprint.PrettyPrinter(indent=4)
        mount_result = hosts.all.zos_mount(
            src=srcfn, path="/pythonx", fs_type="zfs", state="mounted"
        )
        for result in mount_result.values():
            print( "\nbasic mount test: " )
            pp.pprint( result )
            print( "\n")

            assert result.get("rc") == 0
            assert result.get("stdout") != ""
            assert result.get("changed") is True
    finally:
        hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="absent",
        )
        # DataSet.delete(srcfn)
        hosts.all.shell(
            cmd="drm " + srcfn,
            executable=SHELL_EXECUTABLE,
            stdin="",
        )

        hosts.all.file(path="/pythonx/", state="absent")


def test_double_mount(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    srcfn = create_sourcefile(hosts, volume_1)
    try:
        hosts.all.zos_mount(src=srcfn, path="/pythonx", fs_type="zfs", state="mounted")
        # The duplication here is intentional... want to make sure it is seen
        mount_result = hosts.all.zos_mount(
            src=srcfn, path="/pythonx", fs_type="zfs", state="mounted"
        )
        for result in mount_result.values():
            assert result.get("rc") == 0
            assert "already mounted" in result.get("stderr") or "already mounted" in result.get("stdout")
            assert result.get("changed") is False
    finally:
        hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="absent",
        )
        hosts.all.file(path="/pythonx/", state="absent")


def test_remount(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    srcfn = create_sourcefile(hosts, volume_1)
    try:
        pp = pprint.PrettyPrinter(indent=4)
        mount_results = hosts.all.zos_mount(src=srcfn, path="/pythonx", fs_type="zfs", state="mounted")
        for result in mount_results.values():
            print( "\nfirst mount of remount test: " )
            pp.pprint( result )
            print( "\n")

        hosts.all.zos_mount(src=srcfn, path="/pythonx", fs_type="zfs", state="mounted")

        mount_result = hosts.all.zos_mount(
            src=srcfn, path="/pythonx", fs_type="zfs", state="remounted"
        )
        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("changed") is True
    finally:
        mount_result = hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="absent",
        )
        for result in mount_results.values():
            print( "\nUNMount of remount test: " )
            pp.pprint( result )
            print( "\n")

        hosts.all.file(path="/pythonx/", state="absent")


def test_basic_mount_with_bpx_nocomment_nobackup(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    srcfn = create_sourcefile(hosts, volume_1)

    tmp_file_filename = "/tmp/testfile.txt"

    hosts.all.zos_copy(
        content=INITIAL_PRM_MEMBER,
        dest=tmp_file_filename,
        is_binary=True,
    )
    hosts.all.shell(
        cmd="chtag -t -c ISO8859-1 " + tmp_file_filename,
        executable=SHELL_EXECUTABLE,
        stdin="",
    )

    dest = get_tmp_ds_name()
    dest_path = dest + "(AUTO1)"

    hosts.all.zos_data_set(
        name=dest,
        type="pdse",
        space_primary=5,
        space_type="m",
        record_format="fba",
        record_length=80,
    )
    print("\nbnn-Copying {0} to {1}\n".format(tmp_file_filename, dest_path))
    hosts.all.zos_copy(
        src=tmp_file_filename,
        dest=dest_path,
        is_binary=True,
        remote_src=True,
    )

    try:
        mount_result = hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="mounted",
            persistent=dict(data_store=dest_path),
        )

        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("changed") is True

    finally:
        hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="absent",
        )
        hosts.all.file(path=tmp_file_filename, state="absent")
        hosts.all.file(path="/pythonx/", state="absent")
        hosts.all.zos_data_set(
            name=dest,
            state="absent",
            type="pdse",
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=80,
        )


def test_basic_mount_with_bpx_comment_backup(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    srcfn = create_sourcefile(hosts, volume_1)

    tmp_file_filename = "/tmp/testfile.txt"

    hosts.all.zos_copy(
        content=INITIAL_PRM_MEMBER,
        dest=tmp_file_filename,
        is_binary=True,
    )
    # Make it readable at console
    hosts.all.shell(
        cmd="chtag -t -c ISO8859-1 " + tmp_file_filename,
        executable=SHELL_EXECUTABLE,
        stdin="",
    )

    # Dump the values of the file once copied to the target(s)
    results = hosts.all.shell(
        cmd="cat " + tmp_file_filename,
        executable=SHELL_EXECUTABLE,
        stdin="",
    )
    for result in results.values():
        print("\nbcb-destination result: {0}\n".format(result.get("stdout")))

    print("\n====================================================\n")

    dest = get_tmp_ds_name()
    dest_path = dest + "(AUTO2)"
    back_dest_path = dest + "(AUTO2BAK)"

    hosts.all.zos_data_set(
        name=dest,
        type="pdse",
        space_primary=5,
        space_type="m",
        record_format="fba",
        record_length=80,
    )

    print("\nbcb-Copying {0} to {1}\n".format(tmp_file_filename, dest_path))
    hosts.all.zos_copy(
        src=tmp_file_filename,
        dest=dest_path,
        is_binary=True,
        remote_src=True,
    )

    data = ""

    try:
        mount_result = hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="mounted",
            persistent=dict(
                data_store=dest_path,
                backup="Yes",
                backup_name=back_dest_path,
                comment=["bpxtablecomment - try this", "second line of comment"],
            ),
        )
        # copying from dataset to make editable copy on target
        test_tmp_file_filename = tmp_file_filename + "-a"

        hosts.all.zos_copy(
            src=dest_path,
            dest=test_tmp_file_filename,
            is_binary=True,
            remote_src=True,
        )
        hosts.all.shell(
            cmd="chtag -t -c ISO8859-1 " + test_tmp_file_filename,
            executable=SHELL_EXECUTABLE,
            stdin="",
        )
        results = hosts.all.shell(
            cmd="cat " + test_tmp_file_filename, executable=SHELL_EXECUTABLE, stdin=""
        )
        data = ""
        for result in results.values():
            print("\nbcb-postmount result: {0}\n".format(result.get("stdout")))
            data += result.get("stdout")

        print("\n====================================================\n")

        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("changed") is True

        assert srcfn in data
        assert "bpxtablecomment - try this" in data
    finally:
        hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="absent",
        )
        hosts.all.file(path=tmp_file_filename, state="absent")
        hosts.all.file(path=test_tmp_file_filename, state="absent")
        hosts.all.file(path="/pythonx/", state="absent")
        hosts.all.zos_data_set(
            name=dest,
            state="absent",
            type="pdse",
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=80,
        )

def test_basic_mount_with_tmp_hlq_option(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    srcfn = create_sourcefile(hosts, volume_1)
    try:
        mount_result = hosts.all.zos_mount(
            src=srcfn, path="/pythonx", fs_type="zfs", state="mounted"
        )
        for result in mount_result.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
            assert result.get("changed") is True
    finally:
        tmphlq = "TMPHLQ"
        persist_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=persist_data_set, state="present", type="seq")
        unmount_result = hosts.all.zos_mount(
            src=srcfn,
            path="/pythonx",
            fs_type="zfs",
            state="absent",
            tmp_hlq=tmphlq,
            persistent=dict(data_store=persist_data_set, backup=True)
        )
        hosts.all.zos_data_set(name=persist_data_set, state="absent")
        for result in unmount_result.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
            assert result.get("changed") is True
            assert result.get("backup_name")[:6] == tmphlq

        hosts.all.file(path="/pythonx/", state="absent")
