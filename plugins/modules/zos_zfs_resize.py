#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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
module: zos_zfs_resize
version_added: '1.13.0'
short_description: Resize a zfs data set.
description:
  - The module L(zos_zfs_resize.,/zos_zfs_resize.html) can resize a zFS aggregate data set.
  - The I(target) data set must be a unique and a Fully Qualified Name (FQN) of a 1-OS zFS aggregate data set.
  - The data set must be attached as read-write, and contain only one operating system.
  - I(size) must be provided.
author:
  - "Rich Parker (@richp405)"
  - "Marcel Gutierrez (@AndreMarcel99)"
options:
  target:
    description:
      - The Fully Qualified Name of the zFS data set that will be resized.
    required: true
    type: str
  size:
    description:
      - The desired size of the data set after the resizing is performed.
    required: True
    type: int
  space_type:
    description:
      - The unit of measurement to use when defining the size.
      - Valid units are C(k) (kilobytes), C(m) (megabytes), C(g) (gigabytes), C(cyl) (cylinders), and C(trk) (tracks).
    required: false
    type: str
    choices:
      - k
      - m
      - g
      - cyl
      - trk
    default: k
  no_auto_increment:
    description:
      - Option to not allow auto increase of a data set when performing a shrink operation.
      - When set to C(true), if during the shrinking process of a zfs aggregate more space is needed,
        the new total size will not be increased and the module will fail.
    required: false
    type: bool
    default: false
  verbose:
    description:
      - Return diagnostic messages that describe the module's execution.
      - When I(verbose=true), verbose output is returned on module failure.
      - Verbose includes the stdout of the command execution which is very large, to avoid dumping this
        into the logs you can provide a trace_destination instead.
    required: false
    type: bool
    default: false
  trace_destination:
    description:
      - File path or data set name where the full trace of the module's execution will be dumped into.
    required: false
    type: str

notes:
  - When using data set for trace_destination option required record_length equal or over 200 to avoid lost of information.
  - Some record_length for datasets and datasets could generate lost of information and false negative with the message in
    stderr Could not open trace output dataset.
  - L(zfsadm documentation,https://www.ibm.com/docs/en/zos/3.1.0?topic=commands-zfsadm).
"""

EXAMPLES = r"""
- name: Resize an aggregate data set to 2500 Kilobytes.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500

- name: Resize an aggregate data set to 20 Tracks.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    space_type: trk
    size: 20

- name: Resize an aggregate data set to 4 Megabytes.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    space_type: m
    size: 4

- name: Resize an aggregate data set to 1000 Kilobytes and set no auto increment if it's shrinking.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 1000
    no_auto_increment: True

- name: Resize an aggregate data set and get verbose output.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500
    verbose: True

- name: Resize an aggregate data set and get the full trace on a file.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500
    trace_destination: /tmp/helper.txt

- name: Resize an aggregate data set and get the full trace on a member of a PDS.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500
    trace_destination: "TEMP.HELPER.STORAGE(RESIZE)"

- name: Resize an aggregate data set and get the full trace on a file with verbose output.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500
    verbose: True
    trace_destination: /tmp/helper.txt
"""

RETURN = r"""
cmd:
    description: The zfsadm command executed on the remote node.
    returned: always
    type: str
    sample: zfsadm grow -aggregate SOMEUSER.VVV.ZFS -size 4096
target:
    description: The Fully Qualified Name of the resized zFS data set.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
mount_target:
    description: The original share/mount of the data set.
    returned: always
    type: str
    sample: /tmp/zfs_agg
size:
    description: The approximate size of the data set after the resizing is performed.
    returned: always
    type: int
    sample: 4024
rc:
    description: The return code of the zfsadm command.
    returned: always
    type: int
    sample: 0
old_size:
    description: The reported size, in space_type, of the data set before the resizing was performed.
    returned: always
    type: float
    sample: 3096
old_free_space:
    description: The reported size, in space_type, of the free space in the data set before the resizing was performed.
    returned: always
    type: float
    sample: 108
new_size:
    description: The reported size, in space_type, of the data set after the resizing was performed.
    returned: success
    type: float
    sample: 4032
new_free_space:
    description: The reported size, in space_type, of the free space in the data set after the resizing was performed.
    returned: success
    type: float
    sample: 48
space_type:
    description: The measurement unit of space used to report all size values.
    returned: always
    type: str
    sample: k
stdout:
    description: The STDOUT from command.
    returned: always
    type: str
    sample: IOEZ00173I Aggregate TEST.ZFS.DATA.USER successfully grown.
stderr:
    description: The STDERR from the command, may be empty.
    returned: always
    type: str
    sample: IOEZ00181E Could not open trace output dataset.
stdout_lines:
    description: List of strings containing individual lines from STDOUT.
    returned: always
    type: list
    sample: ["IOEZ00173I Aggregate TEST.ZFS.DATA.USER successfully grown."]
stderr_lines:
    description: List of strings containing individual lines from STDERR.
    returned: always
    type: list
    sample: ["IOEZ00181E Could not open trace output dataset."]
verbose_output:
    description: If C(verbose=true), the operation's full traceback will show on this variable. If C(trace) will return the data set or path name.
    returned: always
    type: str
    sample: 6FB2F8 print_trace_table printing contents of table Main Trace Table...
"""

import os
import tempfile
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zfsadm import zfsadm


def calculate_size_on_k(size, space_type):
    """Function to convert size depending on the space_type.

    Parameters
    ----------
        size : int
            Size to grow or shrink the zfs
        space_type : str
            Type of space to be use

    Returns
    -------
        size : int
            Size on kilobytes
    """
    if space_type == "m":
        size *= 1024
    if space_type == "g":
        size *= 1048576
    if space_type == "cyl":
        size *= 830
    if space_type == "trk":
        size *= 55
    return size


def get_full_output(file, module):
    """Function to get the verbose output and delete the tmp file

    Parameters
    ----------
        file : str
            Name of the tmp file where the full verbose output is store
        module : object
            Ansible object to execute commands.

    Returns
    -------
        output : str
            Verbose output
    """
    output = ""

    if "/" in file:
        cmd = "cat {0}".format(file)
    else:
        cmd = "dcat '{0}'".format(file)

    rc, output, stderr = module.run_command(cmd)

    if rc != 0:
        output = "Unable to obtain full output for verbose mode."

    return output


def get_size_and_free(line):
    """Function to parsing the response of get aggregation size.

    Parameters
    ----------
        line : str
            stout of the get aggregation size function

    Returns
    -------
        numbers[1] : int
            Size on kilobytes of the zfs

        numbers[0] : int
            Total free on kilobytes of the zfs
    """
    numbers = [int(word) for word in line.split() if word.isdigit()]
    return numbers[1], numbers[0]


def find_mount_target(module, target, results):
    """Execute df command to access the information of mount points.

    Parameters
    ----------
        module : object
            Ansible object to execute commands.
        target : str
            ZFS to check.

    Returns
    -------
        mount_point : str
            The folder where the zfs is mount
    """
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
            module.fail_json(msg="No mount points were found in the following output: {0}".format(stdout), **results)
    return mount_point


def convert_size(size, space_type):
    """Function to convert size from kb to the space_type.

    Parameters
    ----------
        size : int
            Size to grow or shrink the zfs
        space_type : str
            Type of space to be use

    Returns
    -------
        size : int
            Size on kilobytes
    """
    if space_type == "m":
        size /= 1024
    if space_type == "g":
        size /= 1048576
    if space_type == "cyl":
        size /= 830
    if space_type == "trk":
        size /= 55
    return size


def proper_size_str(size, space_type):
    """Function to convert size to a proper response for output.

    Parameters
    ----------
        size : int
            Size to grow or shrink the zfs
        space_type : str
            Type of space to be use

    Returns
    -------
        size : int or float
            Size on specific space_type notation 2 if is 2.0 or 1.5
    """
    if space_type == "k" or space_type == "trk" or space_type == "cyl":
        return int(size)
    else:
        split_size = str(size).split(".")
        if split_size[1].startswith("0"):
            return int(size)
        else:
            return float("{:.1f}".format(size))


def create_trace_dataset(name, member=False):
    """Function to create data sets for traceback if is not created.

    Parameters
    ----------
        name : str
            Full size of the dataset
        member : bool
            If the dataset include a member to create

    Returns
    -------
        rc : bool
            Indicates if datasets were made.
    """
    if member:
        dataset_name = data_set.extract_dsname(name)
        data_set.DataSet.ensure_present(name=dataset_name, replace=False, type="PDS", record_length=200)
        rc = data_set.DataSet.ensure_member_present(name)
    else:
        rc = data_set.DataSet.ensure_present(name=name, replace=False, type="SEQ", record_length=200)

    return rc


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            target=dict(type="str", required=True),
            size=dict(type="int", required=True),
            space_type=dict(
                type="str",
                required=False,
                choices=["k", "m", "g", "cyl", "trk"],
                default="k",
            ),
            no_auto_increment=dict(type="bool", required=False, default=False),
            verbose=dict(type="bool", required=False, default=False),
            trace_destination=dict(type="str", required=False),
        ),
        supports_check_mode=False
    )
    args_def = dict(
        target=dict(type="data_set", required=True),
        size=dict(type="int", required=True),
        space_type=dict(
            type="str",
            required=False,
            choices=["k", "m", "g", "cyl", "trk"],
            default="k",
        ),
        no_auto_increment=dict(type="bool", required=False, default=False),
        verbose=dict(type="bool", required=False, default=False),
        trace_destination=dict(type="data_set_or_path", required=False),
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

    result = dict()
    target = module.params.get("target")
    size = module.params.get("size")
    space_type = module.params.get("space_type")
    noai = module.params.get("no_auto_increment")
    verbose = module.params.get("verbose")
    trace_destination = module.params.get("trace_destination")

    changed = False
    # Variables to return the value on the space_type by the user
    size_on_type = ""
    free_on_type = ""

    result.update(
        dict(
            target=target,
            size=size,
            space_type=space_type,
            cmd="",
            changed=changed,
            rc=1,
            stdout="",
            stderr="",
            verbose_output="",
        )
    )

    if module.check_mode:
        module.exit_json(**result)

    # Validate if the target ZFS exist
    if not (data_set.DataSet.data_set_exists(target)):
        module.fail_json(msg="ZFS Target {0} does not exist".format(target), **result)

    # Validation to found target on the system and also get the mount_point
    mount_target = find_mount_target(module=module, target=target, results=result)

    if size <= 0:
        module.fail_json(msg="Can not resize ZFS Target {0} to 0".format(target), **result)

    # Initialize the class with the target
    zfsadm_obj = zfsadm(aggregate_name=target, module=module)

    rc, stdout, stderr = zfsadm.get_aggregate_size(zfsadm_obj.aggregate_name, module)

    if rc == 0:
        old_size, old_free = get_size_and_free(line=stdout)

    if space_type != "k":
        space = calculate_size_on_k(size=size, space_type=space_type)
    else:
        space = size

    # Validations to know witch function will be execute
    operation = ""
    minimum_size_t_shrink = old_size - old_free

    if space_type != "k":
        size_on_type = convert_size(size=old_size, space_type=space_type)
        free_on_type = convert_size(size=old_free, space_type=space_type)

    str_old_size = old_size if space_type == "k" else size_on_type
    str_old_size = proper_size_str(str_old_size, space_type)
    str_old_free = old_free if space_type == "k" else free_on_type
    str_old_free = proper_size_str(str_old_free, space_type)

    result.update(
        dict(
            mount_target=mount_target,
            old_size=str_old_size,
            old_free_space=str_old_free,
        )
    )

    if space == old_size:
        result.update(
            dict(
                cmd="",
                rc=0,
                stdout="Size provided is the current size of the ZFS {0}".format(target),
                stderr="",
                changed=False,
                size=size,
                new_size=str_old_size,
                new_free_space=str_old_free,
            )
        )
        module.exit_json(**result)

    elif space < minimum_size_t_shrink:
        module.fail_json(msg="Not enough free space in the ZFS to shrink.", **result)

    elif space > old_size:
        operation = "grow"

    elif space >= minimum_size_t_shrink and space < old_size:
        operation = "shrink"

    noai = " -noai " if noai else ""
    noai = "" if operation == "grow" else noai

    # Variables for the verbose output or trace destination
    trace = ""
    tmp_file = ""
    trace_uss = True
    trace_destination_created = True

    if trace_destination is not None:
        if "/" in trace_destination:
            trace_uss = True
        else:
            if data_set.is_member(trace_destination):
                if not data_set.DataSet.data_set_exists(data_set.extract_dsname(trace_destination)):
                    trace_destination_created = create_trace_dataset(name=trace_destination, member=True)
            else:
                if not (data_set.DataSet.data_set_exists(trace_destination)):
                    trace_destination_created = create_trace_dataset(name=trace_destination, member=False)
            trace_uss = False
        tmp_file = trace_destination

    if not trace_destination_created:
        stderr_trace = "\nUnable to create trace_destination {0}.".format(trace_destination)
    else:
        stderr_trace = ""

    if verbose and trace_destination is None:
        home_folder = Path.home()
        tmp_fld = module._remote_tmp.replace("~", str(home_folder))
        tmp_fld = tmp_fld.replace("//", "/")
        temp = tempfile.NamedTemporaryFile(dir=tmp_fld, delete=False)
        tmp_file = temp.name
        trace_uss = True

    if verbose or trace_destination is not None:
        trace = " -trace '{0}'".format(tmp_file) if trace_uss else " -trace \"//'{0}'\" ".format(trace_destination)

    # Execute the function
    rc, stdout, stderr, cmd = zfsadm_obj.execute_resizing(operation=operation, size=space, noai=noai, verbose=trace)

    # Get the output, calculate size and verbose if required
    if rc == 0:
        changed = True

        rc_size, stdout_size, stderr_size = zfsadm.get_aggregate_size(zfsadm_obj.aggregate_name, module)
        if rc_size == 0:
            new_size, new_free = get_size_and_free(line=stdout_size)

        if space_type != "k":
            size_on_type = convert_size(size=new_size, space_type=space_type)
            free_on_type = convert_size(size=new_free, space_type=space_type)

        if verbose:
            if trace_destination is None:
                output = get_full_output(file=tmp_file, module=module)
                result.update(
                    verbose_output=output,
                )
                os.remove(tmp_file)
            else:
                output = get_full_output(file=tmp_file, module=module)
                result.update(
                    verbose_output=output,
                )

    else:
        if verbose and trace_destination is None:
            os.remove(tmp_file)

        msg = "No enough space on device to grow." if operation == 'grow' else "No space to properly shrink."

        raise ResizingOperationError(
            msg="Resize: resize command returned non-zero code. {0}".format(msg),
            target=target,
            mount_target=mount_target,
            cmd=cmd,
            rc=rc,
            size=size,
            stdout=stdout,
            stderr=stderr + stderr_trace,
            changed=False,
            old_size=str_old_size,
            old_free=str_old_free,
            verbose_output="",
        )

    str_new_size = new_size if space_type == "k" else size_on_type
    str_new_size = proper_size_str(str_new_size, space_type)
    str_new_free = new_free if space_type == "k" else free_on_type
    str_new_free = proper_size_str(str_new_free, space_type)

    result.update(
        dict(
            cmd=cmd,
            rc=rc,
            stdout=stdout,
            stderr=stderr + stderr_trace,
            changed=changed,
            new_size=str_new_size,
            new_free_space=str_new_free,
        )
    )

    module.exit_json(**result)


class ResizingOperationError(Exception):
    def __init__(
            self,
            msg,
            target="",
            mount_target="",
            size="",
            cmd="",
            rc="",
            stdout="",
            stderr="",
            changed=False,
            old_size="",
            old_free="",
            verbose_output="",
    ):
        """Error in a copy operation.

        Parameters
        ----------
        msg : str
            Human readable string describing the exception.
        target : str
            The Fully Qualified Name of the resized zfs data set
        mount_target : str
            The original share/mount
        size : str
            The approximate size of the target
        rc : int
            Result code.
        stdout : str
            Standart output.
        stderr : str
            Standart error.
        cmd : str
            The zfsadm command try to execute on the remote node.
        changed : bool
            If the operation was executed.
        old_size : float or int
            The reported size, of the data set before the resizing is performed.
        old_free : float or int
            The reported size, of the free space in the data set before the resizing is performed.
        """
        self.json_args = dict(
            msg=msg,
            target=target,
            mount_target=mount_target,
            cmd=cmd,
            rc=rc,
            size=size,
            stdout=stdout,
            stderr=stderr,
            changed=changed,
            old_size=old_size,
            old_free_space=old_free,
            verbose_output=verbose_output,
        )
        super().__init__(msg)


def main():
    run_module()


if __name__ == '__main__':
    main()
