#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
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
__metaclass__ = type

DOCUMENTATION = r"""
---
module: zos_resize
author:
    - "Rich Parker (@richp405)"
    - "Marcel Gutierrez (@andre.marcel.gutierre)"
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
    required: true
  size:
    description:
      - The approximate size, of the data set after the resizing is performed.
    type: int
    required: True
    size_type:
  size_type:
    description:
      - The unit of measurement to use when defining the size.
      - Valid units of size are C(k), C(m), C(g), C(cyl), and C(trk).
    type: str
    choices:
      - k
      - m
      - g
      - cyl
      - trk
    required: false
    default: k
  no_auto_increment:
    description:
      - Option to not allow automatic increase on shrinking process.
      - If set to C(true), in the process of shrinking a zfs data set if a new file or
        folder is create or added to the point and its over the new size the process will fail.
    type: bool
    required: false
    default: false
  verbose:
    description:
      - Determines if verbose output should be returned from the underlying utility used by this module.
      - When I(verbose=true) verbose output is returned on module failure.
    required: false
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Resize an aggregate data set to 4 megabytes (4,096 Kb).
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500
"""

RETURN = r"""
cmd:
    description: The actual zosadm command that was attempted.
    returned: always
    type: str
    sample: zfsadm grow -aggregate SOMEUSER.VVV.ZFS -size 4096
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
    sample: /tmp/zfs_agg
size:
    description:
        - The approximate size, in Kilobytes, of the data set after the resizing is performed.
    returned: always
    type: int
    sample: 4024
rc:
    description: The return code of the zfsadm command.
    returned: always
    type: int
    sample: 0
old_size:
    description:
        - The reported size, in Kilobytes, of the data set before the resizing is performed.
    returned: always
    type: int
    sample: 3096
old_free:
    description:
        - The reported size, in Kilobytes, of the free space in the data set before the resizing is performed.
    returned: always
    type: int
    sample: 108
new_size:
    description:
        - The reported size, in Kilobytes, of the data set after the resizing is performed.
    returned: success
    type: int
    sample: 4032
new_free:
    description:
        - The reported size, in Kilobytes, of the free space in the data set after the resizing is performed.
    returned: success
    type: int
    sample: 48
verbose_output:
    description:
        - If C(verbose=true) the full traceback of operation will show on this variable.
    returned: C(verbose=true) and success
    type: str
    sample: 6FB2F8 print_trace_table: printing contents of table: Main Trace Table\nStart Record found in trace, total records 700,
    30204 bytes to format\n*** Timestamp: Wed Oct 23 16:52:50 2024\n*** Thread assignment: thread=0001 asid=004A tcb=006FB2F8\n(001 .000000)
    signal_initialization: recovery_function = 00000000\n(001 .000000) osi_Alloc: a1=x0DDAEE40 s1=x2F0 a2=x0DDAEE48 s2=x2E0 total=752 off=x00000096
    subr=osi_lock_initialization\n(001 .000000) osi_Alloc: a1=x0DDAF138 s1=x1780 a2=x0DDAF140 s2=x1770 total=6768 off=x000000CC subr=osi_lock_initialization\n(001 .000000)
    osi_Alloc: a1=x0DDB08C0 s1=x20E0 a2=x0DDB08C8 s2=x20D0 total=15184 off=x00000140 subr=osi_lock_initialization\n(001 .000000) fp_pool_create: cachesize=0 eyecatch=WAITPOOL\n(001 .000000)
    osi_Alloc: a1=x0DDB29A8 s1=x60 a2=x0DDB29B0 s2=x50 total=15280 off=x00000138 subr=fp_pool_create\n(001 .000000) fp_pool_create: tablep=0DDB29B0 cachesize=0\n(001 .000000)
    osi_lock_init: pool = 0DDB29B0 nonauth\n(001 .000000) osi_Alloc: a1=x0DDB2A10 s1=x40 a2=x0DDB2A18
"""

import os
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zfsadm import zfsadm
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
)


def calculate_size_on_k(size, size_type):
    if size_type == "m":
        size *= 1024
    if size_type == "g":
        size *= 1048576
    if size_type == "cyl":
        size *= 720
    if size_type == "trk":
        size *= 48
    return size


def get_full_output(file, module):
    output = ""
    cmd = "cat {0}".format(file)
    rc, output, stderr = module.run_command(cmd)
    if rc != 0:
        output = "Unable to obtain full output for verbose mode."

    os.unlink(file)

    return output


def create_command(size, noai=False, verbose=False):
    noai = "-noai" if noai else ""

    if verbose:
        temp = tempfile.NamedTemporaryFile(delete=False)
        trace = "-trace {0}".format(temp.name)
    else:
        trace = ""

    cmd_str = "-size {0} {1} {2}".format(size, noai, trace)

    return cmd_str, temp.name


def get_size_and_free(string):
    numbers = [int(word) for word in string.split() if word.isdigit()]
    return numbers[1], numbers[0]


def found_mount_target(module, target):
    rc, stdout, stderr = module.run_command("df")
    found = False
    if rc == 0:
        stdout_lines = stdout.split("\n")
        for line in stdout_lines:
            if len(line) > 2:
                columns = line.split()
                if target in columns[1]:
                    mount_point = columns[0]
                    found = True
                    break
        if found is False:
            module.fail_json(msg="Resize: could not locate {0}".format(target),
                stderr="No error reported: string not found." )
    return target, mount_point


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            target=dict(type="str", required=True),
            size=dict(type="int", required=True),
            size_type=dict(
                    type="str",
                    required=False,
                    choices=["k", "m", "g", "cyl", "trk"],
                    default="k",
                ),
            no_auto_increment=dict(type="bool", required=False, default=False),
            verbose=dict(type="bool", required=False, default=False),
        ),
        supports_check_mode=False
    )
    args_def = dict(
        target=dict(type="data_set", required=True),
        size=dict(type="int", required=True),
        size_type=dict(
                type="str",
                required=False,
                choices=["k", "m", "g", "cyl", "trk"],
                default="k",
            ),
        no_auto_increment=dict(type="bool", required=False, default=False),
        verbose=dict(type="bool", required=False, default=False),
    )

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    res_args = dict()
    target = module.params.get("target")
    size = module.params.get("size")
    size_type = module.params.get("size_type")
    noai = module.params.get("no_auto_increment")
    verbose = module.params.get("verbose")
    changed = False

    target, mount_target = found_mount_target(module=module, target=target)

    aggregate_name = zfsadm(target, module)

    rc, stdout, stderr = aggregate_name.get_agg_size()

    if rc == 0:
        old_size, old_free = get_size_and_free(string=stdout)

    res_args.update(
        dict(
            target=target,
            mount_target=mount_target,
            old_size=old_size,
            old_free=old_free,
            size=size,
            cmd="",
            changed=changed,
            rc=0,
            stdout="",
            stderr="",
        )
    )

    if size_type != "k":
        size = calculate_size_on_k(size=size, size_type=size_type)

    grow, shrink = False, False
    minimum_size_t_shrink = old_size - old_free

    if size == old_size:
        module.fail_json(msg="Same size declared with the size of the zfz")
    elif size > old_size:
        grow = True
    elif size >= minimum_size_t_shrink and size < old_size:
        shrink = True
    else:
        module.fail_json(msg="Error code 119 not enough space to shrink")

    cmd, tmp_file = create_command(size=size, noai=noai, verbose=verbose)

    rc, stdout, stderr, cmd = aggregate_name.grow_shrink(grow, shrink, cmd)

    if rc == 0:
        changed = True

        rc_size, stdout_size, stderr_size = aggregate_name.get_agg_size()
        if rc_size == 0:
            new_size, new_free = get_size_and_free(string=stdout_size)

        if verbose:
            output = get_full_output(file=tmp_file, module=module)
            res_args.update(
                verbose_output=output,
            )
    else:
        module.fail_json(
            msg="Resize: resize command returned non-zero code: rc=" +
            str(rc) + ".",
            stderr=str(res_args)
        )

    res_args.update(
        dict(
            cmd=cmd,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            changed=changed,
            new_size=new_size,
            new_free=new_free,
        )
    )

    module.exit_json(**res_args)

def main():
    run_module()


if __name__ == '__main__':
    main()
