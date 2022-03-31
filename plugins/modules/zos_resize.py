#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import, division, print_function
from posixpath import split
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
)
from ansible.module_utils.basic import AnsibleModule
import re
import os

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["stableinterface"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: zos_resize
author:
    - "Rich Parker (@richp405)"
short_description: Resize a zfs data set.
description:
  - The module M(zos_resize) can resize a zfs aggregate data set.
  - The I(target) data set must be either:
    - A unique and a Fully Qualified Name (FQN) of a 1-OS zfs aggregate data set, or
    - A full path of a mount point, which will be used to look up the data set's FQDN.
  - The data set must be attached read-write, and contain only one Operating system.
  - I(size) in K must be provided.
options:
    target:
        description:
            - The Fully Qualified Name of zfs data set that is to be resized.
        type: str
        required: True
    size:
        description:
            - The approximate size, in Kilobytes, of the data set after the resizing is performed.
        type: int
        required: True
"""

EXAMPLES = r"""
- name: Resize an aggregate data set to 4 megabytes (4,096 Kb).
  zos_resize:
    target: SOMEUSER.VVV.ZFS
    size: 4096
"""

RETURN = r"""
target:
    description:
        - The Fully Qualified Name of zfs data set that is to be resized.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
mount_target:
    description:
        - The original share/mount name provided.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
size:
    description:
        - The approximate size, in Kilobytes, of the data set after the resizing is performed.
    returned: always
    type: int
    sample: 4024
cmd:
    description: The actual zosadm command that was attempted.
    returned: always
    type: str
    sample: zfsadm grow -aggregate SOMEUSER.VVV.ZFS -size 4096
rc:
    description: The return code of the zfsadm command.
    returned: always
    type: int
    sample: 0
oldsize:
    description:
        - The reported size, in Kilobytes, of the data set before the resizing is performed.
    returned: always
    type: int
    sample: 3096
oldfree:
    description:
        - The reported size, in 8K blocks, of the free space in the data set before the resizing is performed.
    returned: always
    type: int
    sample: 108
newsize:
    description:
        - The reported size, in Kilobytes, of the data set after the resizing is performed.
    returned: success
    type: int
    sample: 4032
newfree:
    description:
        - The reported size, in 8K blocks, of the free space in the data set after the resizing is performed.
    returned: success
    type: int
    sample: 48
"""


try:
    from zoautil_py import MVSCmd, types
except Exception:
    MVSCmd = MissingZOAUImport()
    types = MissingZOAUImport()


def get_agg_size(aggregatename):
    size = -1
    free = -1

    cmdstr = "zfsadm fsinfo -aggregate " + aggregatename

    rc, stdout, stderr = module.run_command(cmdstr)

    if rc == 0:
        searchstr = r"^\s*Size:\s*([0-9]*)K\s*Free\s8K\sBlocks:\s*([0-9]*)"
        found = re.search(searchstr, stdout, re.MULTILINE | re.DOTALL)
        if found is not None:
            size = found.group(1).strip()
            free = found.group(2).strip()

    return(size, free)

# #############################################################################
# ############## run_module: code for zos_resize module #######################
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
        module.fail_json(msg="Parameter verification failed", stderr=str(err))
    changed = False
    res_args = dict()

    target = parsed_args.get("target")
    size = parsed_args.get("size")
    res_args.update(
        dict(
            target=target,
            mount_target=target,
            size=size,
            cmd="start",
            changed=changed,
            rc=0,
            stdout="",
            stderr="",
        )
    )

    # data set to be resized must exist, but could be a mount point
    # df | grep -i /temp
    # /temp/agtest   (TESTAG.GGS.ZFS)          8576/12960     4294967292 Available

    fs_du = data_set.DataSetUtils(target)
    fs_exists = fs_du.exists()
    oldsize, oldfree = get_agg_size(target)
    oldsize = int(oldsize)
    oldfree = int(oldfree)

    if fs_exists is False or oldsize < 0 or oldfree < 0:
        cmdstr = "df"
        rc, stdout, stderr = module.run_command(cmdstr)
        found = False

        if rc == 0:
            stdout_lines = stdout.split("\n")
            for line in stdout_lines:
                if len(line) > 2:
                    columns = line.split()
                    if target in columns[0]:
                        new_target = columns[1].strip("\t\n\r\')(")
                        res_args.update(
                            dict(
                                target=new_target
                            )
                        )
                        target = new_target
                        fs_du = data_set.DataSetUtils(target)
                        fs_exists = fs_du.exists()
                        found = True
                        break
            if found is False:
                module.fail_json( msg="Resize: could not locate {0}".format(target),
                    stderr="No error reported: string not found." )
        else:
            module.fail_json( msg="Resize: df command failed",
            stderr=stderr)


    if fs_exists is False:
        module.fail_json(
            msg="Resize issue target ({0}) does not exist.".format(target),
            stderr=str(res_args)
        )

    oldsize, oldfree = get_agg_size(target)
    oldsize = int(oldsize)
    oldfree = int(oldfree)
    if oldsize < 0 or oldfree < 0:
        module.fail_json(
            msg="Resize: initial size check failed on ({0}).".format(target),
            stderr=str(res_args)
        )
    else:
        res_args.update(
            dict(
                cmd="get init size",
                oldsize=oldsize,
                oldfree=oldfree,
            )
        )

    newsize = -1
    newfree = -1
    cmdstr = "zfsadm "

    if oldsize > size:
        cmdstr = cmdstr + " shrink "
    elif oldsize < size:
        cmdstr = cmdstr + " grow "
    else:
        cmdstr = None
        changed = False
        rc = 0
        msg = "Resize: data set is already requested size: " + str(size) + "K."
        stdout = msg
        newsize = oldsize
        newfree = oldfree

    if cmdstr is not None:
        cmdstr += "-aggregate " + target + " -size " + str(size)
        rc, stdout, stderr = module.run_command(cmdstr)
        res_args.update(
            dict(
                cmd=cmdstr,
                rc=rc,
                stdout=stdout,
                stderr=stderr,
            )
        )

        if rc != 0:
            module.fail_json(
                msg="Resize: resize command returned non-zero code: rc=" +
                str(rc) + ".",
                stderr=str(res_args)
            )
        else:
            changed = True
            newsize, newfree = get_agg_size(target)
            # This may error out, as shrinking is a 'long running command'... so take whatever is returned

    res_args.update(
        dict(
            changed=changed,
            newsize=newsize,
            newfree=newfree,
            stdout=stdout,
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
            target=dict(type="str", required=True),
            size=dict(type="int", required=True),
        ),
        supports_check_mode=False,
    )

    arg_def = dict(
        target=dict(arg_type="str", default="", required=True),
        size=dict(arg_type="int", default=0, required=True),
    )

    res_args = None
    res_args = run_module(module, arg_def)
    module.exit_json(**res_args)


if __name__ == "__main__":
    main()
