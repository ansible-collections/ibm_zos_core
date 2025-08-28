#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2025
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
module: zos_backup_restore
version_added: '1.3.0'
author: "Blake Becker (@blakeinate)"
short_description: Backup and restore data sets and volumes
description:
  - Create and restore from backups of data sets and volumes.
  - Data set backups are performed using logical dumps, volume backups are performed
    using physical dumps.
  - Backups are compressed using AMATERSE.
  - Backups are created by first dumping data sets with ADRDSSU, followed by compression with AMATERSE.
  - Restoration is performed by first decompressing an archive with AMATERSE, then restoring with ADRDSSU.
  - Since ADRDSSU and AMATERSE are used to create and restore backups,
    backups can be restored to systems where Ansible and ZOAU are not available.
    Conversely, dumps created with ADRDSSU and AMATERSE can be restored using this module.
options:
  operation:
    description:
      - Used to specify the operation to perform.
    required: True
    type: str
    choices:
      - backup
      - restore
  data_sets:
    description:
      - Determines which data sets to include in the backup.
    required: False
    type: dict
    suboptions:
      include:
        description:
          - When I(operation=backup), specifies a list of data sets or data set patterns
            to include in the backup.
          - When I(operation=backup) GDS relative names are supported.
          - When I(operation=restore), specifies a list of data sets or data set patterns
            to include when restoring from a backup.
          - The single asterisk, C(*), is used in place of exactly one qualifier.
            In addition, it can be used to indicate to DFSMSdss that only part of a
            qualifier has been specified.
          - When used with other qualifiers, the double asterisk, C(**),
            indicates either the nonexistence of leading, trailing,
            or middle qualifiers, or the fact that they play no role in the selection process.
          - Two asterisks are the maximum permissible in a qualifier.
            If there are two asterisks in a qualifier, they must be the first and last characters.
          - A question mark C(?) or percent sign C(%) matches a single character.
        type: raw
        required: False
      exclude:
        description:
          - When I(operation=backup), specifies a list of data sets or data set patterns
            to exclude from the backup.
          - When I(operation=backup) GDS relative names are supported.
          - When I(operation=restore), specifies a list of data sets or data set patterns
            to exclude when restoring from a backup.
          - The single asterisk, C(*), is used in place of exactly one qualifier.
            In addition, it can be used to indicate that only part of a
            qualifier has been specified."
          - When used with other qualifiers, the double asterisk, C(**),
            indicates either the nonexistence of leading, trailing,
            or middle qualifiers, or the fact that they play no role in the selection process.
          - Two asterisks are the maximum permissible in a qualifier.
            If there are two asterisks in a qualifier, they must be the first and last characters.
          - A question mark C(?) or percent sign C(%) matches a single character.
        type: raw
        required: False
  volume:
    description:
      - This applies to both data set restores and volume restores.
      - When I(operation=backup) and I(data_sets) are provided, specifies the volume
        that contains the data sets to backup.
      - When I(operation=restore), specifies the volume the backup should be restored to.
      - I(volume) is required when restoring a full volume backup.
    type: str
    required: False
  full_volume:
    description:
      - When I(operation=backup) and I(full_volume=True), specifies that the entire volume
        provided to I(volume) should be backed up.
      - When I(operation=restore) and I(full_volume=True), specifies that the volume should be
        restored (default is dataset).
      - I(volume) must be provided when I(full_volume=True).
    type: bool
    default: False
    required: False
  temp_volume:
    description:
      - Specifies a particular volume on which the temporary data sets should be
        created during the backup and restore process.
      - When I(operation=backup) and I(backup_name) is a data set, specifies the
        volume the backup should be placed in.
    type: str
    required: False
    aliases:
      - dest_volume
  backup_name:
    description:
      - When I(operation=backup), the destination data set or UNIX file to hold the backup.
      - When I(operation=restore), the destination data set or UNIX file backup to restore.
      - There are no enforced conventions for backup names.
        However, using a common extension like C(.dzp) for UNIX files and C(.DZP) for data sets will
        improve readability.
      - GDS relative names are supported when I(operation=restore).
    type: str
    required: True
  recover:
    description:
      - When I(recover=true) and I(operation=backup) then potentially recoverable errors will be ignored.
    type: bool
    default: False
  overwrite:
    description:
      - When I(operation=backup), specifies if an existing data set or UNIX file matching
        I(backup_name) should be deleted.
      - When I(operation=restore), specifies if the module should overwrite existing data sets
        with matching name on the target device.
    type: bool
    default: False
  compress:
    description:
      - When I(operation=backup), compress the dataset or file produced by ADRDSSU DUMP.
        This option can reduce the size of the temporary dataset produced before it is passed
        to AMATERSE for tersing.
      - This is only supported if I(operation=backup). By default it will compress all files.
    type: bool
    default: True
  sms_storage_class:
    description:
      - When I(operation=restore), specifies the storage class to use. The storage class will
        also be used for temporary data sets created during restore process.
      - When I(operation=backup), specifies the storage class to use for temporary data sets
        created during backup process.
      - If neither of I(sms_storage_class) or I(sms_management_class) are specified, the z/OS
        system's Automatic Class Selection (ACS) routines will be used.
    type: str
    required: False
  sms_management_class:
    description:
      - When I(operation=restore), specifies the management class to use. The management class
        will also be used for temporary data sets created during restore process.
      - When I(operation=backup), specifies the management class to use for temporary data sets
        created during backup process.
      - If neither of I(sms_storage_class) or I(sms_management_class) are specified, the z/OS
        system's Automatic Class Selection (ACS) routines will be used.
    type: str
    required: False
  space:
    description:
      - If I(operation=backup), specifies the amount of space to allocate for the backup.
        Please note that even when backing up to a UNIX file, backup contents will be temporarily
        held in a data set.
      - If I(operation=restore), specifies the amount of space to allocate for data sets temporarily
        created during the restore process.
      - The unit of space used is set using I(space_type).
      - When I(full_volume=True), I(space) defaults to C(1), otherwise default is C(25)
    type: int
    required: false
    aliases:
      - size
  space_type:
    description:
      - The unit of measurement to use when defining data set space.
      - Valid units of size are C(k), C(m), C(g), C(cyl), and C(trk).
      - When I(full_volume=True), I(space_type) defaults to C(g), otherwise default is C(m)
    type: str
    default: m
    choices:
      - k
      - m
      - g
      - cyl
      - trk
    required: false
    aliases:
      - unit
  hlq:
    description:
      - Specifies the new HLQ to use for the data sets being restored.
      - If no value is provided, the data sets will be restored with their original HLQs.
    type: str
    required: false
  tmp_hlq:
    description:
      - Override the default high level qualifier (HLQ) for temporary
        data sets used in the module's operation.
      - If I(tmp_hlq) is set, this value will be applied to all temporary
        data sets.
      - If I(tmp_hlq) is not set, the value will be the username who submits
        the ansible task, this is the default behavior. If the username can
        not be identified, the value C(TMPHLQ) is used.
    required: false
    type: str

attributes:
  action:
    support: none
    description: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
  async:
    support: full
    description: Supports being used with the ``async`` keyword.
  check_mode:
    support: none
    description: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.

notes:
    - It is the playbook author or user's responsibility to ensure they have
      appropriate authority to the RACF FACILITY resource class. A user is
      described as the remote user, configured to run either the playbook or
      playbook tasks, who can also obtain escalated privileges to execute as
      root or another user.
    - When using this module, if the RACF FACILITY class
      profile B(STGADMIN.ADR.DUMP.TOLERATE.ENQF) is active, you must
      have READ access authority to use the module option I(recover=true).
      If the RACF FACILITY class checking is not set up, any user can use
      the module option without access to the class.
    - If your system uses a different security product, consult that product's
      documentation to configure the required security classes.
"""

EXAMPLES = r"""
- name: Backup all data sets matching the pattern USER.** to data set MY.BACKUP.DZP
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    backup_name: MY.BACKUP.DZP

- name: Backup all data sets matching the patterns USER.** or PRIVATE.TEST.*
    excluding data sets matching the pattern USER.PRIVATE.* to data set MY.BACKUP.DZP
  zos_backup_restore:
    operation: backup
    data_sets:
      include:
        - user.**
        - private.test.*
      exclude: user.private.*
    backup_name: MY.BACKUP.DZP

- name: Backup a list of GDDs to data set my.backup.dzp
  zos_backup_restore:
    operation: backup
    data_sets:
      include:
        - user.gdg(-1)
        - user.gdg(0)
    backup_name: my.backup.dzp

- name: Backup datasets bypassing compress
  zos_backup_restore:
    operation: backup
    compress: false
    data_sets:
      include: someds.name.here
    backup_name: my.backup.dzp

- name: Backup all datasets matching the pattern USER.** to UNIX file /tmp/temp_backup.dzp, ignore recoverable errors.
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    backup_name: /tmp/temp_backup.dzp
    recover: true

- name: Backup all datasets matching the pattern USER.** to data set MY.BACKUP.DZP,
    allocate 100MB for data sets used in backup process.
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    backup_name: MY.BACKUP.DZP
    space: 100
    space_type: m

- name:
    Backup all datasets matching the pattern USER.** that are present on the volume MYVOL1 to data set MY.BACKUP.DZP,
    allocate 100MB for data sets used in the backup process.
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    volume: MYVOL1
    backup_name: MY.BACKUP.DZP
    space: 100
    space_type: m

- name: Backup an entire volume, MYVOL1, to the UNIX file /tmp/temp_backup.dzp,
    allocate 1GB for data sets used in backup process.
  zos_backup_restore:
    operation: backup
    backup_name: /tmp/temp_backup.dzp
    volume: MYVOL1
    full_volume: true
    space: 1
    space_type: g

- name: Restore data sets from a backup stored in the UNIX file /tmp/temp_backup.dzp.
    Restore the data sets with the original high level qualifiers.
  zos_backup_restore:
    operation: restore
    backup_name: /tmp/temp_backup.dzp

- name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
    Only restore data sets whose last, or only qualifier is TEST.
    Use MYHLQ as the new HLQ for restored data sets.
  zos_backup_restore:
    operation: restore
    data_sets:
      include: "**.TEST"
    backup_name: /tmp/temp_backup.dzp
    hlq: MYHLQ

- name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
    Only restore data sets whose last, or only qualifier is TEST.
    Use MYHLQ as the new HLQ for restored data sets. Restore data sets to volume MYVOL2.
  zos_backup_restore:
    operation: restore
    data_sets:
      include: "**.TEST"
    volume: MYVOL2
    backup_name: /tmp/temp_backup.dzp
    hlq: MYHLQ

- name: Restore data sets from backup stored in the data set MY.BACKUP.DZP.
    Use MYHLQ as the new HLQ for restored data sets.
  zos_backup_restore:
    operation: restore
    backup_name: MY.BACKUP.DZP
    hlq: MYHLQ

- name: Restore volume from backup stored in the data set MY.BACKUP.DZP.
    Restore to volume MYVOL2.
  zos_backup_restore:
    operation: restore
    volume: MYVOL2
    full_volume: true
    backup_name: MY.BACKUP.DZP
    space: 1
    space_type: g

- name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
    Specify DB2SMS10 for the SMS storage and management classes to use for the restored
    data sets.
  zos_backup_restore:
    operation: restore
    volume: MYVOL2
    backup_name: /tmp/temp_backup.dzp
    sms_storage_class: DB2SMS10
    sms_management_class: DB2SMS10
"""
RETURN = r"""
changed:
  description:
    - Indicates if the operation made changes.
    - C(true) when backup/restore was successful, C(false) otherwise.
  returned: always
  type: bool
  sample: true
backup_name:
  description:
    - The USS file name or data set name that was used as a backup.
    - Matches the I(backup_name) parameter provided as input.
  returned: always
  type: str
  sample: "/u/oeusr03/my_backup.dzp"
message:
  description:
    - Returns any important messages about the modules execution, if any.
  returned: always
  type: str
  sample: ""
"""

import traceback
from os import path
from re import IGNORECASE, match, search

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import \
    BetterArgParser
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import \
    DataSet
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import \
    ZOAUImportError

try:
    from zoautil_py import datasets
    from zoautil_py import exceptions as zoau_exceptions
except ImportError:
    datasets = ZOAUImportError(traceback.format_exc())
    zoau_exceptions = ZOAUImportError(traceback.format_exc())


def main():
    """Run the zos_backup_restore module core functions.

    Raises
    ------
    fail_json
        Any error ocurred during execution.
    """
    result = dict(changed=False, message="", backup_name="")
    module_args = dict(
        operation=dict(type="str", required=True, choices=["backup", "restore"]),
        data_sets=dict(
            required=False,
            type="dict",
            options=dict(
                include=dict(type="raw", required=False),
                exclude=dict(type="raw", required=False),
            ),
        ),
        space=dict(type="int", required=False, aliases=["size"]),
        space_type=dict(type="str", required=False, aliases=["unit"], choices=["k", "m", "g", "cyl", "trk"], default="m"),
        volume=dict(type="str", required=False),
        full_volume=dict(type="bool", default=False),
        temp_volume=dict(type="str", required=False, aliases=["dest_volume"]),
        backup_name=dict(type="str", required=True),
        recover=dict(type="bool", default=False),
        overwrite=dict(type="bool", default=False),
        compress=dict(type="bool", default=True),
        sms_storage_class=dict(type="str", required=False),
        sms_management_class=dict(type="str", required=False),
        hlq=dict(type="str", required=False),
        tmp_hlq=dict(type="str", required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    try:
        params = parse_and_validate_args(module.params)
        operation = params.get("operation")
        data_sets = params.get("data_sets", {})
        space = params.get("space")
        space_type = params.get("space_type", "m")
        volume = params.get("volume")
        full_volume = params.get("full_volume")
        temp_volume = params.get("temp_volume")
        backup_name = params.get("backup_name")
        recover = params.get("recover")
        overwrite = params.get("overwrite")
        compress = params.get("compress")
        sms_storage_class = params.get("sms_storage_class")
        sms_management_class = params.get("sms_management_class")
        hlq = params.get("hlq")
        tmp_hlq = params.get("tmp_hlq")

        if operation == "backup":
            backup(
                backup_name=backup_name,
                include_data_sets=resolve_gds_name_if_any(data_sets.get("include")),
                exclude_data_sets=resolve_gds_name_if_any(data_sets.get("exclude")),
                volume=volume,
                full_volume=full_volume,
                temp_volume=temp_volume,
                overwrite=overwrite,
                compress=compress,
                recover=recover,
                space=space,
                space_type=space_type,
                sms_storage_class=sms_storage_class,
                sms_management_class=sms_management_class,
                tmp_hlq=tmp_hlq,
            )
        else:
            restore(
                backup_name=backup_name,
                include_data_sets=data_sets.get("include"),
                exclude_data_sets=data_sets.get("exclude"),
                volume=volume,
                full_volume=full_volume,
                temp_volume=temp_volume,
                overwrite=overwrite,
                recover=recover,
                hlq=hlq,
                space=space,
                space_type=space_type,
                sms_storage_class=sms_storage_class,
                sms_management_class=sms_management_class,
                tmp_hlq=tmp_hlq,
            )
        result["backup_name"] = backup_name
        result["changed"] = True

    except Exception as e:
        module.fail_json(msg=repr(e), **result)
    module.exit_json(**result)


def resolve_gds_name_if_any(data_set_list):
    """Resolve all gds names in a list, if no gds relative name is found then
    the original name will be kept.
    Parameters
    ----------
    data_set_list : list
        List of data set names.

    Returns
    -------
    list
        List of data set names with resolved gds names.
    """
    if isinstance(data_set_list, list):
        for index, name in enumerate(data_set_list):
            if DataSet.is_gds_relative_name(name):
                data_set_list[index] = DataSet.resolve_gds_absolute_name(name)
    return data_set_list


def parse_and_validate_args(params):
    """Parse and validate arguments to be used by remainder of module.

    Parameters
    ----------
    params : dict
        The params as returned from AnsibleModule instantiation.

    Returns
    -------
    dict
        The updated params after additional parsing and validation.
    """
    arg_defs = dict(
        operation=dict(type="str", required=True, choices=["backup", "restore"]),
        data_sets=dict(
            required=False,
            type="dict",
            options=dict(
                include=dict(type=data_set_pattern_type, required=False),
                exclude=dict(type=data_set_pattern_type, required=False),
            ),
        ),
        space=dict(
            type=space_type,
            required=False,
            aliases=["size"],
            dependencies=["full_volume"],
        ),
        space_type=dict(
            type=space_type_type,
            required=False,
            aliases=["unit"],
            dependencies=["full_volume"],
        ),
        volume=dict(type="volume", required=False, dependencies=["data_sets"]),
        full_volume=dict(type=full_volume_type, default=False, dependencies=["volume"]),
        temp_volume=dict(type="volume", required=False, aliases=["dest_volume"]),
        backup_name=dict(type=backup_name_type, required=False),
        recover=dict(type="bool", default=False),
        overwrite=dict(type="bool", default=False),
        compress=dict(type="bool", default=True),
        sms_storage_class=dict(type=sms_type, required=False),
        sms_management_class=dict(type=sms_type, required=False),
        hlq=dict(type=hlq_type, default=None, dependencies=["operation"]),
        tmp_hlq=dict(type=hlq_type, required=False),
    )

    parsed_args = BetterArgParser(arg_defs).parse_args(params)
    parsed_args = {
        key: value for key, value in parsed_args.items() if value is not None
    }
    return parsed_args


def backup(
    backup_name,
    include_data_sets,
    exclude_data_sets,
    volume,
    full_volume,
    temp_volume,
    overwrite,
    compress,
    recover,
    space,
    space_type,
    sms_storage_class,
    sms_management_class,
    tmp_hlq,
):
    """Backup data sets or a volume to a new data set or unix file.

    Parameters
    ----------
    backup_name : str
        The data set or UNIX path to place the backup.
    compress : bool
        Compress the dataset or file produced by ADRDSSU before taking backup.
    include_data_sets : list
        A list of data set patterns to include in the backup.
    exclude_data_sets : list
        A list of data set patterns to exclude from the backup.
    volume : str
        The volume that contains the data sets to backup.
    full_volume : bool
        Specifies if a backup will be made of the entire volume.
    temp_volume : bool
        Specifies the volume that should be used to store temporary files.
    overwrite : bool
        Specifies if existing data set or UNIX file matching I(backup_name) should be deleted.
    recover : bool
        Specifies if potentially recoverable errors should be ignored.
    space : int
        Specifies the amount of space to allocate for the backup.
    space_type : str
        The unit of measurement to use when defining data set space.
    sms_storage_class : str
        Specifies the storage class to use.
    sms_management_class : str
        Specifies the management class to use.
    tmp_hlq : str
        Specifies the tmp hlq to temporary datasets.

    """
    args = locals()
    zoau_args = to_dzip_args(**args)
    datasets.dzip(**zoau_args)


def restore(
    backup_name,
    include_data_sets,
    exclude_data_sets,
    volume,
    full_volume,
    temp_volume,
    overwrite,
    recover,
    hlq,
    space,
    space_type,
    sms_storage_class,
    sms_management_class,
    tmp_hlq,
):
    """Restore data sets or a volume from the backup.

    Parameters
    ----------
    backup_name : str
        The data set or UNIX path containing the backup.
    include_data_sets : list
        A list of data set patterns to include in the restore
        that are present in the backup.
    exclude_data_sets : list
        A list of data set patterns to exclude from the restore
        that are present in the backup.
    volume : str
        The volume that contains the data sets to backup.
    full_volume : bool
        Specifies if a backup will be made of the entire volume.
    temp_volume : bool
        Specifies the volume that should be used to store temporary files.
    overwrite : bool
        Specifies if module should overwrite existing data sets with
        matching name on the target device.
    recover : bool
        Specifies if potentially recoverable errors should be ignored.
    hlq : str
        Specifies the new HLQ to use for the data sets being restored.
    space : int
        Specifies the amount of space to allocate for data sets temporarily
        created during the restore process.
    space_type : str
        The unit of measurement to use when defining data set space.
    sms_storage_class : str
        Specifies the storage class to use.
    sms_management_class : str
        Specifies the management class to use.
    tmp_hlq : str
        Specifies the tmp hlq to temporary datasets.

    Raises
    ------
    ZOAUException
        When any exception is raised during the data set allocation.
    """
    args = locals()
    zoau_args = to_dunzip_args(**args)
    output = ""
    try:
        rc = datasets.dunzip(**zoau_args)
    except zoau_exceptions.ZOAUException as dunzip_exception:
        output = dunzip_exception.response.stdout_response
        output = output + dunzip_exception.response.stderr_response
        rc = get_real_rc(output)
    failed = False
    if rc > 0 and rc <= 4:
        if recover is not True:
            failed = True
    elif rc > 4:
        failed = True
    if failed:
        raise zoau_exceptions.ZOAUException(
            "{0}, RC={1}".format(output, rc)
        )


def get_real_rc(output):
    """Parse out the final RC from MVS program output.

    Parameters
    ----------
    output : str
        The MVS program output.

    Returns
    -------
    int
        The true program RC.
    """
    true_rc = None
    match = search(
        r"HIGHEST\sRETURN\sCODE\sIS\s([0-9]+)",
        output,
    )
    if match:
        true_rc = int(match.group(1))
    return true_rc


def data_set_pattern_type(contents, dependencies):
    """Validates provided data set patterns.

    Parameters
    ----------
    contents : Union[str, list[str]
        One or more data set patterns.
    dependencies : dict
        Any dependent arguments.

    Returns
    -------
    Union[str]
        A list of uppercase data set patterns.

    Raises
    ------
    ValueError
        When provided argument is not a string or a list.
    ValueError
        When provided argument is an invalid data set pattern.
    """
    if contents is None:
        return None
    if isinstance(contents, str):
        contents = [contents]
    elif not isinstance(contents, list):
        raise ValueError(
            "Invalid argument for data set pattern, expected string or list."
        )
    for pattern in contents:
        if not match(
            r"^(?:(?:[A-Za-z$#@\?\*]{1}[A-Za-z0-9$#@\-\?\*]{0,7})(?:[.]{1})){1,21}[A-Za-z$#@\*\?]{1}[A-Za-z0-9$#@\-\*\?]{0,7}(?:\(([-+]?[0-9]+)\)){0,1}$",
            str(pattern),
            IGNORECASE,
        ):
            raise ValueError(
                "Invalid argument {0} for data set pattern.".format(contents)
            )
    return [x.upper() for x in contents]


def hlq_type(contents, dependencies):
    """Validates provided HLQ is valid and is not specified for a backup operation.

    Parameters
    ----------
    contents : str
        The HLQ to use.
    dependencies : dict
        Any dependent arguments.

    Returns
    -------
    str
        The HLQ to use.

    Raises
    ------
    ValueError
        When operation is restore and HLQ is provided.
    ValueError
        When an invalid HLQ is provided.
    """
    if contents is None:
        return None
    if dependencies.get("operation") == "backup":
        raise ValueError("hlq_type is only valid when operation=restore.")
    if not match(r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})$", contents, IGNORECASE):
        raise ValueError("Invalid argument {0} for hlq_type.".format(contents))
    return contents


def sms_type(contents, dependencies):
    """Validates the SMS class provided matches a valid format.

    Parameters
    ----------
    contents : str
        The SMS class name.
    dependencies : dict
        Any dependent arguments.

    Returns
    -------
    str
        The uppercase SMS class name.

    Raises
    ------
    ValueError
        When invalid argument provided for SMS class.
    """
    if contents is None:
        return None
    if not match(r"^[A-Z\$\*\@\#\%]{1}[A-Z0-9\$\*\@\#\%]{0,7}$", contents, IGNORECASE):
        raise ValueError("Invalid argument {0} for SMS class.".format(contents))
    return str(contents).upper()


def space_type(contents, dependencies):
    """Validates amount of space provided.

    Parameters
    ----------
    contents : str
        The amount of space.
    dependencies : dict
        Any dependent arguments.

    Returns
    -------
    int
        The amount of space.
    """
    if contents is None:
        if dependencies.get("full_volume"):
            return 1
        else:
            return 25
    return contents


def space_type_type(contents, dependencies):
    """Validates provided data set unit of space.
    Returns the unit of space.

    Parameters
    ----------
    contents : str
        The space type to use.
    dependencies : dict
        Any dependent arguments.

    Returns
    -------
    str
        The unit of space.

    Raises
    ------
    ValueError
        When an invalid space unit is provided.
    """
    if contents is None:
        if dependencies.get("full_volume"):
            return "g"
        else:
            return "m"
    if not match(r"^(m|g|k|trk|cyl)$", contents, IGNORECASE):
        raise ValueError(
            'Value {0} is invalid for space_type argument. Valid space types are "k", "m", "g", "trk" or "cyl".'.format(
                contents
            )
        )
    return contents


def backup_name_type(contents, dependencies):
    """Validates provided backup name.

    Parameters
    ----------
        contents : str
            The backup name to use
        dependencies : dict
            Any dependent arguments

    Returns
    -------
        str
            The backup name to use

    Raises
    ------
        ValueError
            When an invalid backup name is provided
    """
    if contents is None:
        return None
    if not match(
        r"^(?:(?:[A-Za-z$#@\?\*]{1}[A-Za-z0-9$#@\-\?\*]{0,7})(?:[.]{1})){1,21}[A-Za-z$#@\*\?]{1}[A-Za-z0-9$#@\-\*\?]{0,7}(?:\(([-+]?[0-9]+)\)){0,1}$",
        str(contents),
        IGNORECASE,
    ):
        if not path.isabs(str(contents)):
            raise ValueError(
                'Invalid argument "{0}" for type "data_set" or "path".'.format(contents)
            )
    return str(contents)


def full_volume_type(contents, dependencies):
    """Validates dependent arguments are also specified for full_volume argument.

    Parameters
    ----------
    contents : bool
        Whether we are making a full volume backup or not.
    dependencies : dict
        Any dependent arguments.

    Returns
    -------
    bool
        Whether we are making a full volume backup or not.

    Raises
    ------
    ValueError
        When volume argument is not provided.
    """
    if contents is True and dependencies.get("volume") is None:
        raise ValueError("full_volume=True is only valid when volume is specified.")
    return contents


def to_dzip_args(**kwargs):
    """API adapter for ZOAU dzip method.

    Returns
    -------
    dict
        The arguments for ZOAU dzip method translated from module arguments.
    """
    zoau_args = {}
    if kwargs.get("backup_name"):
        zoau_args["file"] = kwargs.get("backup_name")
        if not kwargs.get("backup_name").startswith("/"):
            zoau_args["dataset"] = True

    if kwargs.get("include_data_sets"):
        zoau_args["target"] = ",".join(kwargs.get("include_data_sets"))

    if kwargs.get("volume"):
        if kwargs.get("full_volume"):
            zoau_args["volume"] = True
            zoau_args["target"] = kwargs.get("volume")
        else:
            zoau_args["src_volume"] = kwargs.get("volume")

    if kwargs.get("temp_volume"):
        zoau_args["dest_volume"] = kwargs.get("temp_volume")

    if kwargs.get("exclude_data_sets"):
        zoau_args["exclude"] = ",".join(kwargs.get("exclude_data_sets"))

    if kwargs.get("recover"):
        zoau_args["force"] = kwargs.get("recover")

    if kwargs.get("overwrite"):
        zoau_args["overwrite"] = kwargs.get("overwrite")

    if kwargs.get("compress"):
        zoau_args["compress"] = kwargs.get("compress")

    if kwargs.get("sms_storage_class"):
        zoau_args["storage_class_name"] = kwargs.get("sms_storage_class")

    if kwargs.get("sms_management_class"):
        zoau_args["management_class_name"] = kwargs.get("sms_management_class")

    if kwargs.get("space"):
        size = str(kwargs.get("space"))
        if kwargs.get("space_type"):
            size += kwargs.get("space_type")
        zoau_args["size"] = size

    if kwargs.get("tmp_hlq"):
        zoau_args["tmphlq"] = str(kwargs.get("tmp_hlq"))

    return zoau_args


def to_dunzip_args(**kwargs):
    """API adapter for ZOAU dunzip method.

    Returns
    -------
    dict
        The arguments for ZOAU dunzip method translated from module arguments.
    """
    zoau_args = {}
    if kwargs.get("backup_name"):
        zoau_args["file"] = kwargs.get("backup_name")
        if not kwargs.get("backup_name").startswith("/"):
            zoau_args["dataset"] = True

    if kwargs.get("include_data_sets"):
        zoau_args["include"] = ",".join(kwargs.get("include_data_sets"))

    if kwargs.get("volume"):
        if kwargs.get("full_volume"):
            zoau_args["volume"] = kwargs.get("volume")
        else:
            zoau_args["src_volume"] = kwargs.get("volume")

    if kwargs.get("temp_volume"):
        zoau_args["dest_volume"] = kwargs.get("temp_volume")

    if kwargs.get("exclude_data_sets"):
        zoau_args["exclude"] = ",".join(kwargs.get("exclude_data_sets"))

    if kwargs.get("recover"):
        zoau_args["force"] = kwargs.get("recover")

    if kwargs.get("overwrite"):
        zoau_args["overwrite"] = kwargs.get("overwrite")

    sms_specified = False
    if kwargs.get("sms_storage_class"):
        zoau_args["storage_class_name"] = kwargs.get("sms_storage_class")

    if kwargs.get("sms_management_class"):
        zoau_args["management_class_name"] = kwargs.get("sms_management_class")

    if sms_specified:
        zoau_args["sms_for_tmp"] = True

    if kwargs.get("space"):
        size = str(kwargs.get("space"))
        if kwargs.get("space_type"):
            size += kwargs.get("space_type")
        zoau_args["size"] = size

    if kwargs.get("hlq") is None:
        zoau_args["keep_original_hlq"] = True
    else:
        zoau_args["high_level_qualifier"] = kwargs.get("hlq")

    if kwargs.get("tmp_hlq"):
        zoau_args["high_level_qualifier"] = str(kwargs.get("tmp_hlq"))
        zoau_args["keep_original_hlq"] = False

    return zoau_args


if __name__ == "__main__":
    main()
