#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r"""
---
module: zos_mount
author:
    - "Rich Parker (@richp405)"
short_description: Mount a filesystem for Unix System Services (USS)
description:
  - zos_mount connects an existing, mountable file to USS.
  - Mountable file needs a valid, unique Fully Qualified Name.
  - Target folder will be created and/or unmounted if needed
options:
    path:
        description:
            - The absolute path name onto which the file system is to be mounted
            - The path is case sensitive, and < 1023 characters long
        type: str
        required: True
    src:
        description:
            - The file in zos that is to be mounted
        type: str
        required: True
    fstype:
        description:
            - The type of file system that will perform the logical mount request.
            - The system converts the TYPE operand value to uppercase letters.
            - The value can be up to 8 characters long.
        type: str
        choices:
            - HFS
            - zFS
            - NFS
            - TFS
        required: True
    state:
        description:
            - The desired status of the described mount (choice).
            - If I(absent), this will un-mount and alse remove from fstab if provided.
            - If I(mounted), this will mount and add to the fstab if provided.
            - >
                If I(mounted) and mount source is in use, left in place.
                Will also make sure entry is in fstab, if provided.
            - >
                If I(unmounted) and mount source is in use, device will be unmounted.
                fstab is not altered, even when provided.
                Module completes successfully with I(changed=True).
            - >
                If I(unmounted) and mount source is not in use, no action taken.
                Module completes successfully with I(changed=False).
            - >
                If I(present), if makes sure device is in fstab, if provided.
                Returns I(changed) if fstab was rewritten.
            - >
                If I(remounted) the device is unmounted and mounted again.
                Always returns I(changed=True).
        type: str
        choices:
            - absent
            - mounted
            - unmounted
            - present
            - remounted
        required: False
        default: mounted
    fstab:
        description:
            - If provided, this is the full qualified name of the dataset member to change
        type: str
        required: False
        aliases:
            - bpxfile
            - bpxprm
    backup:
        description:
            - If provided, this is the name of the dataset member to copy fstab to before alteration
        type: str
        required: False
    tabcomment:
        description:
            - If provided, this is used in markers around the fstab entry
            - Only the first 21 characters are copied
        type: str
        required: False
    unmount_opts:
        description:
            - Describes how the unmount is to be performed
        type: str
        choices:
            - DRAIN
            - FORCE
            - IMMEDIATE
            - NORMAL
            - REMOUNT
            - RESET
        required: False
        default: NORMAL
    opts:
        description:
            - Options available to the mount
            - If I(ro) on a mounted/remount, mount is performed read-only.
            - If I(same) and (unmount_opts=REMOUNT), mount is opened is same mode as previously.
            - If I(nowait), mount is performed asynchronously.
            - If I(nosecurity), Security checks are not enforced for files in this file system.
        type: str
        choices:
            - ro
            - rw
            - same
            - nowait
            - nosecurity
        required: False
        default: rw
    src_params:
        description:
            - Specifies a parameter string to be passed to the file system type.
            - The parameter format and content are specified by the file system type.
        type: str
        required: False
    tag_flag:
        description:
            - If present, tags get written to any untagged file
            - When the file system is unmounted, the tags are lost.
            - If I(False) NOTEXT none of the untagged files in the file system are
                  automatically converted during file reading and writing.
            - If I(True) TEXT each untagged file is implicitly marked as
                  containing pure text data that can be converted.
            - If this flag is used, use of tag_ccsid is encouraged.
        type: str
        choices:
            - TEXT
            - NOTEXT
        required: False
    tag_ccsid:
        description:
            - CCSID for untagged files in the mounted file system
            - only required it tag_flag is present
            - ccsid
                - Identifies the coded character set identifier to be implicitly
                  set for the untagged file. ccsid is specified as a decimal value
                  from 0 to 65535. However, when TEXT is specified, the value must
                  be between 0 and 65535. Other than this, the value is not
                  checked as being valid and the corresponding code page is not
                  checked as being installed.
        type: int
        required: False
    allow_uids:
        description:
            - >
              Specifies whether the SETUID and SETGID mode bits on executables in
              this file system are considered. Also determines whether the APF
              extended attribute or the Program Control extended attribute is
              honored.
            - >
              If I(True) the SETUID and SETGID mode bits are considered when a
              program in this file system is run. SETUID is the default.
            - >
              If I(False) the SETUID and SETGID mode bits are ignored when a
              program in this file system is run. The program runs as though the
              SETUID and SETGID mode bits were not set. Also, if you specify the
              NOSETUID option on MOUNT, the APF extended attribute and the Program Control
              Bit values are ignored.
        type: bool
        required: False
        default: True
    sysname:
        description:
            - >
              For systems participating in shared file system, SYSNAME specifies
              the particular system on which a mount should be performed. This
              system will then become the owner of the file system mounted. This
              system must be IPLed with SYSPLEX(YES).
            - >
              IBM® recommends that you omit the SYSNAME parameter or specify
              system_name where system_name is the name of this system.
            - >
              sysname is a 1–8 alphanumeric name of a system participating in shared file system.
        type: str
        required: False
    automove:
        description:
            - >
              These parameters apply only in a sysplex where systems are exploiting
              the shared file system capability. They specify what is to happens to
              the ownership of a file system when a shutdown, PFS termination, dead
              system takeover, or file system move occurs. The default setting is
              AUTOMOVE where the file system will be randomly moved to another system
              (no system list used).
            - >
              I(AUTOMOVE) indicates that ownership of the file system can be
              automatically moved to another system participating in a shared file system.
            - >
              I(NOAUTOMOVE) prevents movement of the file system's ownership in some situations.
            - >
              I(UNMOUNT) allows the file system to be unmounted in some situations.
        type: str
        choices:
            - AUTOMOVE
            - NOAUTOMOVE
            - UNMOUNT
        required: False
        default: AUTOMOVE
    automove_list:
        description:
            - >
              If(automove=AUTOMOVE), this option will be checked
            - >
              This specifies the list of servers to include or exclude as destinations
            - >
              None is a valid value, meaning 'move anywhere'
            - >
              Indicator is either INCLUDE or EXCLUDE, which can also be abbreviated as I or E
        type: str
        required: False
"""

EXAMPLES = r"""
- name: Mount a filesystem.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted

- name: Unmount a filesystem.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /dontcare
    fstype: ZFS
    state: unmounted
    unmount_opts: REMOUNT
    opts: same

- name: Mount a filesystem readonly.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    opts: ro

- name: Mount a filesystem and record change in BPXPRMAA.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    fstab: SYS1.PARMLIB(BPXPRMAA)
    tabcomment: For Tape2 project

- name: Mount a filesystem and record change in BPXPRMAA after backing up to BPXPRMAB.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    fstab: SYS1.PARMLIB(BPXPRMAA)
    backup: SYS1.PARMLIB(BPXPRMAB)
    tabcomment: For Tape2 project

- name: Mount a filesystem ignoring uid/gid values.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    allow_uids: no

- name: Mount a filesystem asynchronously (don't wait for completion).
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    opts: nowait

- name: Mount a filesystem with no security checks.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    opts: nosecurity

- name: Mount a filesystem, limiting automove to 4 devices.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    automove: AUTOMOVE
    automove_list: I,DEV1,DEV2,DEV3,DEV9

- name: Mount a filesystem, limiting automove to all except 4 devices.
  zos_mount:
    src: SOMEUSER.VVV.ZFS
    path: /u/omvsadm/core
    fstype: ZFS
    state: mounted
    automove: AUTOMOVE
    automove_list: EXCLUDE,DEV4,DEV5,DEV6,DEV7

"""

RETURN = r"""
path:
    description: The absolute path name onto which the file system is to be mounted
    returned: always
    type: str
    sample: /u/omvsadm/core
src:
    description: The file in zos that is to be mounted
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
fstype:
    description: The type of file system that will perform the logical mount request.
    returned: always
    type: str
    sample: ZFS
state:
    description: The desired status of the described mount
    returned: always
    type: str
    sample: mounted
fstab:
    description: This is the full qualified name of the dataset member to change
    returned: always
    type: str
    sample: SYS1.FILESYS(BPXPRMAA)
backup:
    description: This is the name of the dataset member to copy fstab to before alteration
    returned: always
    type: str
    sample: SYS1.FILESYS(BPXPRMAB)
tabcomment:
    description: The text that was used in markers around the fstab entry
    returned: always
    type: str
    sample: I did this because
unmount_opts:
    description: Describes how the unmount it to be performed
    returned: changed and if state=unmounted
    type: str
    sample: DRAIN
opts:
    description: Options available to the mount
    returned: whenever non-None
    type: str
    sample: rw,nosecurity
src_params:
    description: Specifies a parameter string to be passed to the file system type.
    returned: whenever non-None
    type: str
    sample: D(101)
tag_flag:
    description: Indicates if tags should be written to untagged files
    returned: whenever Non-None
    type: str
    sample: TEXT
tag_ccsid:
    description: CCSID for untagged files in the mounted file system
    returned: when tag_flag is defined
    type: int
    sample: 819
allow_uids:
    description: Whether the SETUID and SETGID mode bits on executables in this file system are considered.
    returned: always
    type: bool
    sample: yes
sysname:
    description: SYSNAME specifies the particular system on which a mount should be performed.
    returned: if Non-None
    type: str
    sample: MVSSYS01
automove:
    description:
        - >
          Specifies what is to happens to the ownership of a file system during
          a shutdown, PFS termination, dead system takeover, or file system move occurs.
    returned: if Non-None
    type: str
    sample: AUTOMOVE
automove_list:
    description: This specifies the list of servers to include or exclude as destinations.
    returned: if Non-None
    type: str
    sample: I,SERV01,SERV02,SERV03,SERV04
msg:
    description: Failure message returned by the module.
    returned: failure
    type: str
    sample: Error while gathering information
stdout:
    description: The stdout from the tso mount command.
    returned: always
    type: str
    sample: Copying local file /tmp/foo/src to remote path /tmp/foo/dest
stderr:
    description: The stderr from the tso mount command.
    returned: failure
    type: str
    sample: No such file or directory "/tmp/foo"
stdout_lines:
    description: List of strings containing individual lines from stdout.
    returned: failure
    type: list
    sample: [u"Copying local file /tmp/foo/src to remote path /tmp/foo/dest.."]
stderr_lines:
    description: List of strings containing individual lines from stderr.
    returned: failure
    type: list
    sample: [u"FileNotFoundError: No such file or directory '/tmp/foo'"]
cmd:
    description: The actual tso command that was attempted.
    returned: failure
    type: str
    sample: MOUNT EXAMPLE.DATA.SET /u/omvsadm/sample 3380
rc:
    description: The return code of the mount command, if applicable.
    returned: failure
    type: int
    sample: 8

"""
import os
import math
import stat
import shutil
import glob
import time
import re
from datetime import datetime
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
    encode,
    vtoc,
    #    backup,
    copy,
    mvs_cmd,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

try:
    from zoautil_py import Datasets, MVSCmd, types
except Exception:
    Datasets = MissingZOAUImport()
    MVSCmd = MissingZOAUImport()
    types = MissingZOAUImport()


def cleanup(src_list):
    pass


def swap_text(original, adding, removing):
    """
    swap_text returns original after removing blocks matching removing,
    and adding the adding param
    original now should be a list of lines without newlines
    return is the consolidated file value
    """
    # content_lines = original.split('\n')
    content_lines = original

    remove_starting_at_index = None
    remove_ending_at_index = None

    ms = re.compile(r"^\s*MOUNT\s+FILESYSTEM\('" + removing.upper() + r"'\)")
    print(ms)
    boneyard = dict()

    for index, line in enumerate(content_lines):
        if remove_starting_at_index is None:
            if ms.match(line) is not None:
                remove_starting_at_index = index
                continue
        if remove_starting_at_index is not None:
            remove_ending_at_index = index
            doit = False
            if len(line) > 0:
                if line[0] != ' ' and line[0] != "\t" and line[0:6] != '/* AAA':
                    doit = True
            else:
                doit = True
            if doit:
                if content_lines[remove_starting_at_index - 1][0:6] == '/* VVV':
                    remove_starting_at_index -= 1
                    if remove_starting_at_index > 0:
                        if len(content_lines[remove_starting_at_index - 1]) < 1:
                            remove_starting_at_index -= 1

                boneyard[remove_starting_at_index] = remove_ending_at_index
                remove_starting_at_index = None
                remove_ending_at_index = None

    if remove_starting_at_index is not None:
        if remove_ending_at_index is not None:
            if remove_starting_at_index != remove_ending_at_index:
                if content_lines[remove_starting_at_index - 1][0:6] == '/* VVV':
                    remove_starting_at_index -= 1
                if remove_starting_at_index > 0:
                    if len(content_lines[remove_starting_at_index - 1]) < 1:
                        remove_starting_at_index -= 1
                boneyard[remove_starting_at_index] = remove_ending_at_index

    for startidx in reversed(boneyard.keys()):
        endidx = boneyard[startidx]
        del(content_lines[startidx:endidx])

    if(len(adding) > 0):
        content_lines.extend(adding.split('\n'))

    return "\n".join(content_lines)

# #############################################################################
# ############## run_module: code for zos_mount module ########################
# #############################################################################


def run_module(module, arg_def):
    # ********************************************************************
    # Verify the validity of module args. BetterArgParser raises ValueError
    # when a parameter fails its validation check
    # ********************************************************************

    try:
        parser = better_arg_parser.BetterArgParser(arg_def)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(
            msg="Parameter verification failed",
            stderr=str(err)
        )
    changed = False
    res_args = dict()

    src = parsed_args.get('src')
    path = parsed_args.get('path')
    fstype = parsed_args.get('fstype')
    state = parsed_args.get('state')
    fstab = parsed_args.get('fstab')
    backup = parsed_args.get('backup')
    tabcomment = parsed_args.get('tabcomment')
    unmount_opts = parsed_args.get('unmount_opts')
    opts = parsed_args.get('opts')
    src_params = parsed_args.get('src_params')
    tag_flag = parsed_args.get('tag_flag')
    tag_ccsid = parsed_args.get('tag_ccsid')
    allow_uids = parsed_args.get('allow_uids')
    sysname = parsed_args.get('sysname')
    automove = parsed_args.get('automove')
    automove_list = parsed_args.get('automove_list')

    write_fstab = False
    if('mounted' in state or 'present' in state or 'absent' in state):
        if(len(fstab) > 0):
            write_fstab = True

    gonna_mount = True
    if('unmounted' in state or 'absent' in state):
        gonna_mount = False

    gonna_unmount = False
    if('unmounted' in state or 'remounted' in state or 'absent' in state):
        gonna_unmount = True

    res_args.update(
        dict(
            src=src,
            path=path,
            fstype=fstype,
            state=state,
            fstab=fstab,
            backup=backup,
            tabcomment=tabcomment,
            unmount_opts=unmount_opts,
            opts=opts,
            src_params=src_params,
            tag_flag=tag_flag,
            tag_ccsid=tag_ccsid,
            allow_uids=allow_uids,
            sysname=sysname,
            automove=automove,
            automove_list=automove_list,
            cmd='not built',
            changed=changed,
            comment='starting',
            rc=0,
            stdout='',
            stderr=''
        )
    )

# data set to be mounted/unmounted must exist
    fs_du = data_set.DataSetUtils(src)
    fs_exists = fs_du.exists()
    if fs_exists is False:
        module.fail_json(
            msg="Mount source (" + src + ") doesn't exist",
            stderr=str(res_args)
        )

# Validate mountpoint exists if mounting
    if gonna_mount:
        mp_exists = os.path.exists(path)
        if mp_exists is False:
            os.mkdir(path)
        mp_exists = os.path.exists(path)
        if mp_exists is False:
            module.fail_json(
                msg="Mount destination (" + path + ") doesn't exist",
                stderr=str(res_args)
            )

# Need to see if mountpoint is in use for idempotence
    currently_mounted = False
    rc, stdout, stderr = module.run_command(
        'df | grep ' + src + ' | wc -m', use_unsafe_shell=True)
    if rc != 0:
        module.fail_json(
            msg="Checking for source (" + src + ") failed with error",
            stderr=str(res_args)
        )
    tmpint = int(stdout)
    if tmpint != 0:  # zero bytes means not found
        currently_mounted = True


# can type be validated?

    # ##########################################
    # Assemble the mount command

    parmtext = '/* VVV zos_mount VVV '
    if(len(tabcomment) > 2):
        parmtext = parmtext + tabcomment[:21]
    d = datetime.today()
    parmtext = parmtext + d.ctime()[4:] + " VVV */\n"
    parmtail = "\n" + parmtext.replace('V', 'A')

    fullcmd = ''
    fullumcmd = ''

    if gonna_mount:
        fullcmd = "tsocmd MOUNT FILESYSTEM\\( \\'{0}\\' \\) MOUNTPOINT\\( \\'{1}\\' \\) TYPE\\( '{2}' \\)".format(
            src, path, fstype)
        parmtext = parmtext + \
            "MOUNT FILESYSTEM('{0}')\n      MOUNTPOINT('{1}')\n      TYPE('{2}')".format(
                src, path, fstype)
        if 'ro' in opts or 'RO' in opts:
            subcmd = 'READ'
        else:
            subcmd = 'RDWR'
        fullcmd = "{0} MODE\\({1}\\)".format(fullcmd, subcmd)
        parmtext = "{0}\n      MODE({1})".format(parmtext, subcmd)

        if len(src_params) > 1:
            fullcmd = "{0} PARM\\(\\'{1}\\'\\)".format(fullcmd, src_params)
            parmtext = "{0}\n      PARM('{1}')".format(parmtext, src_params)

        if len(tag_flag) > 0:
            fullcmd = "{0} TAG\\({1},{2}\\)".format(
                fullcmd, tag_flag, tag_ccsid)
            parmtext = "{0}\n      TAG({1},{2})".format(
                parmtext, tag_flag, tag_ccsid)

        if allow_uids:
            fullcmd = fullcmd + ' SETUID'
            parmtext = parmtext + '\n      SETUID'
        else:
            fullcmd = fullcmd + ' NOSETUID'
            parmtext = parmtext + '\n      NOSETUID'

        if 'NOWAIT' in opts or 'nowait' in opts:
            fullcmd = fullcmd + ' NOWAIT'
            parmtext = parmtext + '\n      NOWAIT'
        else:
            fullcmd = fullcmd + ' WAIT'
            parmtext = parmtext + '\n      WAIT'

        if 'NOSECURITY' in opts or 'nosecurity' in opts:
            fullcmd = fullcmd + ' NOSECURITY'
            parmtext = parmtext + '\n      NOSECURITY'
        else:
            fullcmd = fullcmd + ' SECURITY'
            parmtext = parmtext + '\n      SECURITY'

        if len(sysname) > 1:
            fullcmd = "{0} SYSNAME\\({1}\\)".format(fullcmd, sysname)
            parmtext = "{0}\n      SYSNAME({1})".format(parmtext, sysname)

        if len(automove) > 1:
            fullcmd = fullcmd + ' ' + automove
            parmtext = parmtext + '\n      ' + automove
            if(len(automove_list) > 1):
                fullcmd = fullcmd + '(' + automove_list + ')'
                parmtext = parmtext + '(' + automove_list + ')'
        parmtext = parmtext + parmtail

    if gonna_unmount:     # unmount/remount
        fullumcmd = "tsocmd UNMOUNT FILESYSTEM\\(\\'{0}\\'\\)".format(src)
        if len(unmount_opts) < 2:
            unmount_opts = "NORMAL"
            fullumcmd = fullcmd + ' ' + unmount_opts

    comment = ''

    if gonna_unmount:
        if currently_mounted:
            changed = True
            if module.check_mode is False:
                try:
                    (rc, stdout, stderr) = module.run_command(
                        fullumcmd, use_unsafe_shell=True)
                    comment += "ran unmount command\n"
                    currently_mounted = False
                except Exception as err:
                    module.fail_json(msg=str(err), stderr=str(res_args))
            else:
                comment += "(unmount) NO Action taken: ANSIBLE CHECK MODE\n"
                stdout = 'ANSIBLE CHECK MODE'
        else:
            comment += "Unmount called on data set that is not mounted.\n"

    if gonna_mount:
        if currently_mounted is False:
            changed = True
            if module.check_mode is False:
                try:
                    (rc, stdout, stderr) = module.run_command(
                        fullcmd, use_unsafe_shell=True)
                    comment = "ran command\n"
                except Exception as err:
                    module.fail_json(msg=str(err), stderr=str(res_args))
            else:
                comment += "(mount) NO Action taken: ANSIBLE CHECK MODE\n"
                stdout = 'ANSIBLE CHECK MODE'
        else:
            comment += "Mount called on data set that is already mounted.\n"

    rc = 0
    stdout = stderr = None

    if write_fstab and module.check_mode is False:
        fst_du = data_set.DataSetUtils(fstab)
        fst_exists = fst_du.exists()
        if fst_exists is False:
            module.fail_json(
                msg="fstab set member (" + fstab + ") doesn't exist",
                stderr=str(res_args)
            )

        fullcmd = "cp \"//'" + fstab + "'\" /tmp/txtentry"
        try:
            (rc, stdout, stderr) = module.run_command(
                fullcmd, use_unsafe_shell=True)
        except Exception as err:
            module.fail_json(msg=str(err), stderr=str(res_args))

        if len(backup) > 0:
            fullcmd = "cp /tmp/txtentry \"//'" + backup + "'\""
            try:
                (rc, stdout, stderr) = module.run_command(
                    fullcmd, use_unsafe_shell=True)
            except Exception as err:
                module.fail_json(msg=str(err), stderr=str(res_args))
            comment += "Wrote backup to " + backup + "\n"

        with open('/tmp/txtentry', 'r') as fh:
            content = fh.read().replace('/n', '')

        newtext = swap_text(content, parmtext, src)
        if(newtext != content):
            fh = open('/tmp/txtentry', 'w')
            fh.write(newtext)
            fh.close()
            fullcmd = "cp /tmp/txtentry \"//'" + fstab + "'\""
            try:
                (rc, stdout, stderr) = module.run_command(
                    fullcmd, use_unsafe_shell=True)
            except Exception as err:
                module.fail_json(msg=str(err), stderr=str(res_args))
            comment += "Modified " + fstab + " in place\n"

    res_args.update(
        dict(
            changed=changed,
            comment=comment,
            cmd=fullcmd,
            rc=rc,
            stdout=stdout,
            stderr=stderr
        )
    )

    return res_args

# #############################################################################
# ####################### Main                     ############################
# #############################################################################


def main():
    global module

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='str', required=True),
            path=dict(type='str', required=True),
            fstype=dict(type='str', choices=[
                        'HFS', 'zFS', 'NFS', 'TFS'], required=True),
            state=dict(type='str', default='mounted', choices=[
                       'absent', 'mounted', 'unmounted', 'present', 'remounted'], required=False),
            fstab=dict(type='str', required=False, aliases=["bpxfile", "bpxprm"]),
            backup=dict(type='str', required=False),
            tabcomment=dict(type='str', required=False),
            unmount_opts=dict(type='str', default='NORMAL', choices=[
                              'DRAIN', 'FORCE', 'IMMEDIATE', 'NORMAL', 'REMOUNT', 'RESET'], required=False),
            opts=dict(type='str', default='rw', choices=[
                      'ro', 'rw', 'same', 'nowait', 'nosecurity'], required=False),
            src_params=dict(type='str', required=False),
            tag_flag=dict(type='str', default='', choices=[
                          'TEXT', 'NOTEXT'], required=False),
            tag_ccsid=dict(type='int', required=False),
            allow_uids=dict(type='bool', default=True, required=False),
            sysname=dict(type='str', required=False),
            automove=dict(type='str', default='AUTOMOVE', choices=[
                          "AUTOMOVE", "NOAUTOMOVE", "UNMOUNT"], required=False),
            automove_list=dict(type='str', required=False)
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )

    arg_def = dict(
        src=dict(arg_type='data_set', required=True),
        path=dict(arg_type='path', required=True),
        fstype=dict(arg_type='str', choices=[
                    "HFS", "zFS", "NFS", "TFS"], required=True),
        state=dict(arg_type='str', default='mounted', choices=[
                   'absent', 'mounted', 'unmounted', 'present', 'remounted'], required=False),
        fstab=dict(arg_type='str', default='', required=False, aliases=["bpxfile", "bpxprm"]),
        backup=dict(arg_type='str', default='', required=False),
        tabcomment=dict(arg_type='str', default='', required=False),
        unmount_opts=dict(arg_type='str', default='NORMAL', choices=[
                          'DRAIN', 'FORCE', 'IMMEDIATE', 'NORMAL', 'REMOUNT', 'RESET'], required=False),
        opts=dict(arg_type='str', default='rw', choices=[
                  'ro', 'rw', 'same', 'nowait', 'nosecurity'], required=False),
        src_params=dict(arg_type='str', default='', required=False),
        tag_flag=dict(arg_type='str', default='', choices=[
                      'TEXT', 'NOTEXT'], required=False),
        tag_ccsid=dict(arg_type='str', required=False),
        allow_uids=dict(arg_type='bool', default=True, required=False),
        sysname=dict(arg_type='str', default='', required=False),
        automove=dict(arg_type='str', default='AUTOMOVE', choices=[
                      "AUTOMOVE", "NOAUTOMOVE", "UNMOUNT"], required=False),
        automove_list=dict(arg_type='str', default='', required=False)
    )

    try:
        res_args = None
        res_args = run_module(module, arg_def)
        module.exit_json(**res_args)
    finally:
        pass


if __name__ == '__main__':
    main()
