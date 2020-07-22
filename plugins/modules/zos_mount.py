#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: zos_mount
version_added: '2.9.1'
short_description: Mount a filesystem for omvs
description:
  - zos_mount connects an existing, mountable file to an omvs system.
  - mountable file needs a valid, unique FQDN, target folder will be 
      unmounted if needed
author: "Rich Parker (@richp405)"

options:
    Overview:
        This will attach(mount) or detach (unmount) a data set to the omvs file system
    
    unmount
        description:
            - if true, the file_system dataset is UNMOUNTED.  Other values are ignored
            - if false (default), the file_system is mounted to the mount_point
        type: bool
        required: false
        default: false

    file_system
        description:
            - The name of the file system to be added to the file system hierarchy. 
            - Should be FQDN of a mountable file.
            - Cannot be a PDS member.
            - The file system name that is specified must be unique among.
               previously mounted file systems. 
            - The file system name that is supplied is changed to all uppercase characters.
        type: str
        required: true

    mount_point
        description:
            - Specifies the path name of the mount point directory, the place 
            within the file hierarchy where the file system is to be mounted.
            - Specifies the path name of the mount point. The path name must
            be enclosed in single quotation marks. 
            - The name can be a relative path name or an absolute path name. 
                - A relative path name is relative to the working directory of 
                the TSO/E session 
                - You should usually specify an absolute path name. 
                - It can be up to 1023 characters long. 
                - Path names are case-sensitive.
                - Mount point must be a directory
                - Only one file system can be mounted to a mount point at a time.
        type: str
        required: true

    file_system_type
        description:
            - The type of file system that will perform the logical mount request.
            - The system converts the TYPE operand value to uppercase letters. 
        
            - This name must match the TYPE operand of the FILESYSTYPE statement 
            that activates this physical file system in the BPXPRMxx parmlib member. 
            - The file_system_type value can be up to 8 characters long. 
        type: str
        required: true

    open_read_only
        description:
            - Specifies the type of access the file system is to be opened for.
                - FALSE
                    -The file system is to be mounted for read and write access.
                - TRUE
                    - The file system is to be mounted for read-only access.
            - The z/OS UNIX file system allows a file system that is mounted using 
                the MODE(READ) option to be shared as read-only with other systems 
                that share the same DASD.
        type: bool
        required: false
        default: false

    file_system_params
        description:
            - Specifies a parameter string to be passed to the file system type. 
            - The parameter format and content are specified by the file system type. 
        type: string
        required: false
        default: blank

    settag_flag
        description:
            - Specifies whether the file tags for untagged files in the mounted
            file system are implicitly set. 
            - File tagging controls the ability to convert a file's data during 
            file reading and writing. 
            - Implicit, in this case, means that the tag is not permanently 
            stored with the file. Rather, the tag is associated with the file 
            during reading or writing, or when stat() type functions are issued.
            - Either TEXT or NOTEXT, and ccsid must be specified when TAG is specified.
            - When the file system is unmounted, the tags are lost.
            false: NOTEXT
                - Specifies that none of the untagged files in the file system are 
                automatically converted during file reading and writing.
            true: TEXT
                - Specifies that each untagged file is implicitly marked as 
                containing pure text data that can be converted.
        type: bool
        required: false
        default: blank

    settag_ccsid
        description:
            - CCSID for untagged files in the mounted file system
            - only required it settag_flag is present
            ccsid
                Identifies the coded character set identifier to be implicitly 
                set for the untagged file. ccsid is specified as a decimal value
                from 0 to 65535. However, when TEXT is specified, the value must
                be between 0 and 65535. Other than this, the value is not
                checked as being valid and the corresponding code page is not 
                checked as being installed.
        type: numeric value 0-65535
        required: only if settag_flag is non-blank
        default: blank

    respect_uids
        description:
            Specifies whether the SETUID and SETGID mode bits on executables in 
            this file system are respected. Also determines whether the APF 
            extended attribute or the Program Control extended attribute is 
            honored.
        true
            Specifies that the SETUID and SETGID mode bits be respected when a program 
            in this file system is run. SETUID is the default.
        false
            Specifies that the SETUID and SETGID mode bits not be respected when a
            program in this file system is run. The program runs as though the 
            SETUID and SETGID mode bits were not set. Also, if you specify the 
            NOSETUID option on MOUNT, the APF extended attribute and the Program Control 
        type: bool
        required: false
        default: true

    wait_until_done
        description: 
            Specifies whether to wait for an asynchronous mount to complete before returning.
        true:
            Specifies that MOUNT is to wait for the mount to complete before returning. 
        false:
            Specifies that if the file system cannot be mounted immediately (for example, 
            a network mount must be done), then the command will return with a return code 
            indicating that an asynchronous mount is in progress. 
        type: bool
        required: false
        default: true

    normal_security
        description:
            Specifies whether security checks are to be enforced for files in this 
            file system. When a z/OS UNIX file system is mounted with the 
            NOSECURITY option enabled, any new files or directories that are
            created are assigned an owner of UID 0, 
            no matter what UID issued the request.
        true:
            Specifies that normal security checking is done.
        false:
            Specifies that security checking will not be enforced for files in 
            this file system. 
            A user can access or change any file or directory in any way.
            Security auditing will still be performed if the installation is auditing successes.
            The SETUID, SETGID, APF, and Program Control attributes may be turned
            on in files in this file system, but they are not honored while it is 
            mounted with NOSECURITY.
        type: bool
        required: false
        default: true

    sysname
        description:
            For systems participating in shared file system, SYSNAME specifies 
            the particular system on which a mount should be performed. This 
            system will then become the owner of the file system mounted. This 
            system must be IPLed with SYSPLEX(YES).

            IBM® recommends that you omit the SYSNAME parameter or specify 
            system_name where system_name is the name of this system.
        sysname
            sysname is a 1–8 alphanumeric name of a system participating in 
            shared file system. 
        type: string
        required: false
        default: blank
      
    automove(mode)
        description:
            These parameters apply only in a sysplex where systems are exploiting 
            the shared file system capability. They specify what is to happens to 
            the ownership of a file system when a shutdown, PFS termination, dead 
            system takeover, or file system move occurs. The default setting is 
            AUTOMOVE where the file system will be randomly moved to another system (no system list used).


        AUTOMOVE
            AUTOMOVE indicates that ownership of the file system can be 
            automatically moved to another system participating in a shared file 
            system. 
        AUTOMOVE(INCLUDE,sysname1,sysname2,...,sysnameN) 
        or AUTOMOVE(I,sysname1,sysname2,...,sysnameN)
            The INCLUDE indicator with a system list provides an ordered list of 
            systems to which the file system's ownership could be moved. sysnameN
            may be a system name, or an asterisk (*). The asterisk acts as a 
            wildcard to allow ownership to move to any other participating 
            system and is only permitted in place of a system name as the last 
            entry of a system list.
        AUTOMOVE(EXCLUDE,sysname1,sysname2,...,sysnameN) 
        or AUTOMOVE(E,sysname1,sysname2,...,sysnameN)
            The EXCLUDE indicator with a system list provides a list of systems to 
            which the file system's ownership should not be moved.
        NOAUTOMOVE
            NOAUTOMOVE prevents movement of the file system's ownership in 
            some situations.
        UNMOUNT
            UNMOUNT allows the file system to be unmounted in some situations. 
        type: type, optional list with indicator and string
        required: false
        default: AUTOMOVE

    automove_list(indicator,listofdevices)
        description:
            - If automove is set to AUTOMOVE, this will be checked
            - This specifies the list of servers to include or exclude
            - Blank is a valid value, meaning 'move anywhere'
            - Indicator is either INCLUDE or EXCLUDE, which can also be abbreviated as I or E
        type: str
        required: false
        default: blank

    unmount_extension()
        description:
            - unmount only: this is the optional, secondary command
            - DRAIN, FORCE, IMMEDIATE, NORMAL, REMOUNT or RESET
            - In the case of REMOUNT, there is an optional sub-value: (READ),(RDWR),(SAMEMODE)
        type: str
        required: false
        default: NORMAL

original cmd source: 
https://www.ibm.com/support/knowledgecenter/SSLTBW_2.1.0/com.ibm.zos.v2r1.bpxa500/tsomount.htm

"""

EXAMPLES = r"""
- name: Mount a filesystem.
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380

- name: Unmount a filesystem.
  zos_mount:
    unmount: true
    file_system: SOMEUSER.VVV.ZFS
    unmount_extension: REMOUNT(SAMEMODE)

- name: Mount a filesystem readonly.
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380
    open_read_only: yes

- name: Mount a filesystem ignoring uid/gid values.
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380
    respect_uids: no

- name: Mount a filesystem asynchronously (don't wait for completion).
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380
    wait_until_done: no

- name: Mount a filesystem with no security checks.
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380
    normal_security: no

- name: Mount a filesystem, limiting automove to 4 devices.
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380
    automove: AUTOMOVE
    automove_list: I,DEV1,DEV2,DEV3,DEV9

- name: Mount a filesystem, limiting automove to all except 4 devices.
  zos_mount:
    file_system: SOMEUSER.VVV.ZFS
    mount_point: /u/omvsadm/core
    file_system_type: 3380
    automove: AUTOMOVE
    automove_list: E,DEV4,DEV5,DEV6,DEV7
"""

RETURN = r"""
unmount:
    description: Indicates if this was an unmount request
    returned: always
    type: bool
    sample: no
file_system:
    description: Source file or data set being mounted.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
mount_point:
    description: Destination folder of mount.
    returned: success
    type: str
    sample: /u/omvsadm/core
file_system_type:
    description: The device type passed to the command.
    returned: always
    type: str
    sample: 3380
open_read_only:
    description: Indicator of whether readonly was requested.
    returned: success
    type: bool
    sample: yes
file_system_params:
    description: Indicator of parameters passed to the command.
    returned: always
    type: str
    sample: (FSACK=TRUE,ITEM=DEVIDNO)
settag_flag:
    description: Indicates if tag values were set. 
    returned: success
    type: bool
    sample: yes
settag_ccsid:
    description: Indicator of ccsid value set.
    returned: success
    type: str
    sample: 8515
respect_uids:
    description: Specifies whether the SETUID and SETGID mode bits on 
        executables in this file system are respected
    returned: success
    type: bool
    sample: yes
wait_until_done:
    description: Indicates if mount was called (yes) sych or (no) asynchronously
    returned: always
    type: bool
    sample: yes
normal_security:
    description: Indicates if mount was given (yes) normal or (no) non-secure
    returned: success
    type: bool
    sample: yes
sysname:
    description: System name, if provided
    returned: success
    type: str
    sample: MYSYS01
automove:
    description: AUTOMOVE parameter for this mount
    returned: success
    type: list [AUTOMOVE,NOAUTOMOVE,UNMOUNT]
    sample: AUTOMOVE
automove_list:
    description: Lis of devices to include or exclude from automove action
    returned: success
    type: str
    sample: I,DEV1,DEV2,DEV3
size:
    description: Size(in bytes) of the target, after execution.
    returned: success and dest is USS
    type: int
    sample: 1220
msg:
    description: Failure message returned by the module.
    returned: failure
    type: str
    sample: Error while gathering data set information
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
rc:
    description: The return code of the mount command, if applicable.
    returned: failure
    type: int
    sample: 8
cmd:
    description: The actual tso command that was attempted.
    returned: failure
    type: str
    sample: MOUNT EXAMPLE.DATA.SET /u/omvsadm/sample 3380
"""

import os
import math
import stat
import shutil
import glob

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
    backup,
    copy,
    mvs_cmd
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport
)

try:
    from zoautil_py import Datasets, MVSCmd, types
except Exception:
    Datasets = MissingZOAUImport()
    MVSCmd = MissingZOAUImport()
    types = MissingZOAUImport()


def cleanup(src_list):
    pass

###############################################################################
################ run_module: code for zos_mount module ########################
###############################################################################

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

    unmount = parsed_args.get('unmount')
    file_system = parsed_args.get('file_system')
    mount_point = parsed_args.get('mount_point')
    file_system_type = parsed_args.get('file_system_type')
    open_read_only = parsed_args.get('open_read_only')
    file_system_params = parsed_args.get('file_system_params')
    settag_flag = parsed_args.get('settag_flag')
    settag_ccsid = parsed_args.get('settag_ccsid')
    respect_uids = parsed_args.get('respect_uids')
    wait_until_done = parsed_args.get('wait_until_done')
    normal_security = parsed_args.get('normal_security')
    sysname = parsed_args.get('sysname')
    automove = parsed_args.get('automove')
    automove_list = parsed_args.get('automove_list')
    unmount_extension = parsed_args.get('unmount_extension')

    res_args.update(
        dict(
            unmount = unmount,
            file_system = file_system,
            mount_point = mount_point,
            file_system_type = file_system_type,
            open_read_only = open_read_only,
            file_system_params = file_system_params,
            settag_flag = settag_flag,
            settag_ccsid = settag_ccsid,
            respect_uids = respect_uids,
            wait_until_done = wait_until_done,
            normal_security = normal_security,
            sysname = sysname,
            automove = automove,
            automove_list = automove_list,
            cmd = 'not built',
            changed = changed
            unmount_extension = unmount_extension
        )
    )

# file_system to be mounted must exist, unless this is an unmount
    if( !unmount ):
        fs_du = data_set.DataSetUtils(file_system)
        fs_exists = fs_du.exists()
        if( !fs_exists):
            module.fail_json (
                msg = "Mount source (" + file_system + ") doesn't exist",
                res_args
            )

# Validate mountpoint exists
    mp_exists = os.path.exists(mount_point)
    if( !mp_exists):
        module.fail_json (
            msg = "Mount destination (" + mount_point + ") doesn't exist",
            res_args
        )

# Need to see if mountpoint is in use for idempotence (how?)
## df | grep file_system will do the trick
## this can also be used as validation for unmount
    currently_mounted = False
    rc, stdout, stderr = module.run_command( 'sh df | grep ' + file_system )
    if rc != 0:
        module.fail_json (
            msg = "Checking for file_system (" + file_system +") failed with error",
            res_args
        )
    if stdout != "":    ## blank means not found
        currently_mounted = True


# can type be validated?


    ############################################
    # Assemble the mount command - icky part

    if( !unmount ):
        fullcmd = 'tsocmd MOUNT FILESYSTEM(' + file_system + ') MOUNTPOINT(' + mount_point +
        ') TYPE(' + file_system_type + ') MODE('
        if( open_read_only ):
            fullcmd = fullcmd + 'READ'
        else:
            fullcmd = fullcmd + 'RDWR'
        fullcmd = fullcmd + ')'
        if( file_system_params.size() > 1 ):
            fullcmd = fullcmd + ' PARM(' + file_system_params + ')'
        if( settag_ccsid.size() > 0):
            fullcmd = fullcmd + ' TAG('
            if( settag_flag ):
                fullcmd = fullcmd + 'NOTEXT'
            else: 
                fullcmd = fullcmd + 'TEXT'
            fullcmd = fullcmd + ',' + settag_ccsid + ')'
        if( respect_uids ):
            fullcmd = fullcmd + ' SETUID'
        else:
            fullcmd = fullcmd + ' NOSETUID'
        if( wait_until_done):
            fullcmd = fullcmd + ' WAIT'
        else:
            fullcmd = fullcmd + ' NOWAIT'
        if( normal_security):
            fullcmd = fullcmd + ' SECURITY'
        else:
            fullcmd = fullcmd + ' NOSECURITY'
        if( sysname.size() > 1 ):
            fullcmd = fullcmd + ' SYSNAME(' + sysname + ')'
        if( automove.size() > 1):
            fullcmd = fullcmd + ' ' + automove
            if( automove_list.size() > 1):
                fullcmd = fullcmd + '(' + automove_list + ')'
    else:       # unmount
        fullcmd = 'tsocmd UNMOUNT FILESYSTEM(' + file_system + ') 
        if( unmount_extension.size() < 2 ):
            unmount_extension = "NORMAL"
        fullcmd = fullcmd + ' ' + unmount_extension

    conv_path = None
    src_ds_vol = None

    if( unmount ):
        if( currently_mounted ):
            changed = True
    else:
        if( !currently_mounted ):
            changed = True

    if( changed ):  ## got something to do
        if( !module.check_mode ):
            ### do the thing


    res_args.update(
        dict(
            changed = changed
        )
    )

    # ********************************************************************
    # 1. Use DataSetUtils to determine the src and dest data set type.
    # 2. For source data sets, find its volume, which will be used later.
    # ********************************************************************
    try:
        if is_uss:
            dest_ds_type = "USS"
            dest_exists = os.path.exists(dest)
        else:
            dest_du = data_set.DataSetUtils(dest_name)
            dest_exists = dest_du.exists()
            if copy_member:
                dest_exists = dest_exists and dest_du.member_exists(dest_member)
            dest_ds_type = dest_du.ds_type()
        if temp_path or '/' in src:
            src_ds_type = "USS"
        else:
            src_du = data_set.DataSetUtils(src_name)
            if src_du.exists():
                if src_member and not src_du.member_exists(member_name):
                    raise NonExistentSourceError(src)
                src_ds_type = src_du.ds_type()
                src_ds_vol = src_du.volume()
            else:
                raise NonExistentSourceError(src)

    except Exception as err:
        module.fail_json(msg=str(err),res_args)


## this is the key return pile

    return res_args, temp_path, conv_path

###############################################################################
######################### Main                     ############################
###############################################################################
def main():
    module = AnsibleModule(
        argument_spec=dict(
            unmount = dict(type='bool', required=False),
            file_system=dict(type='str', required=True),
            mount_point=dict(type='str', required=True),
            file_system_type=dict(type='str', required=True),
            open_read_only=dict(type='bool', required=False),
            file_system_params=dict(type='str', required=False),
            settag_flag = dict(type='bool', default=False, required=False),
            settag_ccsid = dict(type='str', required=False),
            respect_uids = dict(type='bool', default=True, required=False),
            wait_until_done = dict(type='bool', default=True, required=False),
            normal_security = dict(type='bool', default=True, required=False),
            sysname = dict(type='str', required=False),
            automove = dict(type='str', default='AUTOMOVE', required=False),
            automove_list = dict(type='str', required=False),
            unmount_extension = dict(type='str', required=False)
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )

    arg_def = dict(
        unmount=dict(arg_type='bool', required=False),
        file_system=dict(arg_type='data_set', required=True),
        mount_point=dict(arg_type='path', required=True),
        file_system_type=dict(arg_type='str', required=True),
        open_read_only=dict(arg_type='bool', required=False),
        file_system_params=dict(arg_type='str', required=False),
        settag_flag = dict(arg_type='bool', default=False, required=False),
        settag_ccsid = dict(arg_type='str', required=False),
        respect_uids = dict(arg_type='bool', default=True, required=False),
        wait_until_done = dict(arg_type='bool', default=True, required=False),
        normal_security = dict(arg_type='bool', default=True, required=False),
        sysname = dict(arg_type='str', required=False),
        automove = dict(arg_type='str', default='AUTOMOVE', required=False),
        automove_list = dict(arg_type='str', required=False),
        unmount_extension = dict(arg_type='str', required=False)
    )

    try:
        res_args = temp_path = conv_path = None
        res_args, temp_path, conv_path = run_module(module, arg_def)
        module.exit_json(**res_args)
    finally:
        pass
#        cleanup([temp_path, conv_path])


if __name__ == '__main__':
    main()
