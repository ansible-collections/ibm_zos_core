#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


DOCUMENTATION = r"""
module: zos_backup_restore
author: "Blake Becker (@blakeinate)"
short_description: Backup or Restore
description:
    - Create and restore from backups of data sets and volumes.
    - Data set backups are performed using logical dumps, volume backups are performed using physical dumps.
    - Backups are compressed.
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
    required: True
    type: dict
    suboptions:
      include:
        description:
          - When I(operation=backup), specifies a list of data sets or data set patterns to include in the backup.
          - When I(operation=restore), specifies a list of data sets or data set patterns to include when restoring from a backup.
        type: str
        required: True
      exclude:
        description:
          - When I(operation=backup), specifies a list of data sets or data set patterns to exclude from the backup.
          - When I(operation=restore), specifies a list of data sets or data set patterns to exclude when restoring from a backup.
        type: str
        required: False
  volume:
    description:
      - When I(operation=backup), and I(data_sets) is provided, specifies the volume that contains the data sets to backup.
      - When I(operation=restore), specifies the volume the backup should be restored to.
      - I(volume) is required when restoring a full volume backup.
      - This applies to both data set restores and volume restores.
    type: str
    required: False
  full_volume:
    description:
      - When I(operation=backup) and I(full_volume=True), specifies the entire volume provided to I(volume) should be backed up.
      - When I(operation=restore) and I(full_volume=True), specifies volume should be restored (default is dataset).
      - I(volume) must be provided when I(full_volume=True).
    type: bool
    default: False
    required: False
  backup_name:
    description:
      - When I(operation=backup), the destination data set or UNIX file to hold the backup.
      - When I(operation=restore), the destination data set or UNIX file backup to restore.
    type: str
    required: True
  force:
    description:
      - Specifies if potentially recoverable errors should be ignored.
      - When I(operation=restore), allows an unmovable data set or a data set allocated by absolute track allocation to be moved.
    type: bool
    default: True
  sms_storage_class:
    description:
      - Specifies the storage class to use when I(operation=restore).
      - If none of I(sms_storage_class), I(sms_data_class) or I(sms_management_class) are specified, the z/OS system's Automatic Class Selection (ACS) routines will be used.
    type: str
    required: False
  sms_management_class:
    description:
      - Specifies the management class to use when I(operation=restore).
      - If none of I(sms_storage_class), I(sms_data_class) or I(sms_management_class) are specified, the z/OS system's Automatic Class Selection (ACS) routines will be used.
    type: str
    required: False
  space:
    description:
      - If I(operation=backup), specifies the amount of space to allocate for the backup.
        Please note that even when backing up to a UNIX file, backup contents will be temporarily
        held in a data set.
      - The unit of space used is set using I(space_type).
    type: int
    required: false
    default: 25
    aliases:
      - size
  space_type:
    description:
      - The unit of measurement to use when defining data set space.
      - Valid units of size are C(K), C(M), C(G), C(CYL), and C(TRK).
    type: str
    choices:
      - K
      - M
      - G
      - CYL
      - TRK
    required: false
    default: M
    aliases:
      - unit
  new_hlq:
    description:
      - Specifies the new HLQ to use for the data sets being restored.
      - Defaults to running user's username.
    type: str
    required: false
"""

RETURN = r""""""

EXAMPLES = r"""
- name: "Backup all datasets matching pattern USER.** to data set MY.BACKUP"
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    backup_name: MY.BACKUP

- name: "Backup all datasets matching patterns USER.** or PRIVATE.TEST.*
        excluding datasets matching pattern USER.PRIVATE.* to data set MY.BACKUP"
  zos_backup_restore:
    operation: backup
    data_sets:
      include:
        - user.**
        - private.test.*
      exclude: user.private.*
    backup_name: MY.BACKUP

- name: "Backup all datasets matching pattern USER.** to UNIX file /tmp/temp_backup.dzp, ignore recoverable errors."
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    backup_name: /tmp/temp_backup.dzp
    force: yes

- name: "Backup all datasets matching pattern USER.** to data set MY.BACKUP,
         allocate 100MB for data sets used in backup process."
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    backup_name: MY.BACKUP
    space: 100
    space_type: M

- name: "Backup all datasets matching pattern USER.** that are present on volume MYVOL1 to data set MY.BACKUP,
         allocate 100MB for data sets used in backup process."
  zos_backup_restore:
    operation: backup
    data_sets:
      include: user.**
    volume: MYVOL1
    backup_name: MY.BACKUP
    space: 100
    space_type: M

- name: "Backup an entire volume, MYVOL1, to UNIX file /tmp/temp_backup.dzp,
         allocate 1GB for data sets used in backup process."
  zos_backup_restore:
    operation: backup
    backup_name: /tmp/temp_backup.dzp
    volume: MYVOL1
    full_volume: yes
    space: 1
    space_type: G

- name: "Restore data sets from backup stored in UNIX file /tmp/temp_backup.dzp.
         Use z/OS username as new HLQ."
  zos_backup_restore:
    operation: restore
    backup_name: /tmp/temp_backup.dzp

- name: "Restore data sets from backup stored in UNIX file /tmp/temp_backup.dzp.
         Only restore data sets whose last, or only qualifier is TEST.
         Use MYHLQ as the new HLQ for restored data sets."
  zos_backup_restore:
    operation: restore
    data_sets:
      include: **.TEST
    backup_name: /tmp/temp_backup.dzp
    new_hlq: MYHLQ

- name: "Restore data sets from backup stored in UNIX file /tmp/temp_backup.dzp.
         Only restore data sets whose last, or only qualifier is TEST.
         Use MYHLQ as the new HLQ for restored data sets. Restore data sets to volume MYVOL2."
  zos_backup_restore:
    operation: restore
    data_sets:
      include: **.TEST
    volume: MYVOL2
    backup_name: /tmp/temp_backup.dzp
    new_hlq: MYHLQ

- name: "Restore data sets from backup stored in data set MY.BACKUP.
         Use MYHLQ as the new HLQ for restored data sets."
  zos_backup_restore:
    operation: restore
    backup_name: MY.BACKUP
    new_hlq: MYHLQ

- name: "Restore volume from backup stored in data set MY.BACKUP.
         Restore to volume MYVOL2."
  zos_backup_restore:
    operation: restore
    volume: MYVOL2
    full_volume: yes
    backup_name: MY.BACKUP
    space: 1
    space_type: G

- name: "Restore data sets from backup stored in UNIX file /tmp/temp_backup.dzp.
         Specify DB2SMS10 for the SMS storage and management classes to use for the restored
         data sets."
  zos_backup_restore:
    operation: restore
    volume: MYVOL2
    backup_name: /tmp/temp_backup.dzp
    sms_storage_class: DB2SMS10
    sms_management_class: DB2SMS10
"""

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible.module_utils.basic import AnsibleModule

from re import match, IGNORECASE

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
from os import path

try:
    from zoautil_py import datasets
except ImportError:
    datasets = MissingZOAUImport()


def run_module():
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
        space=dict(type="int", required=False, aliases=["size"], default=25),
        space_type=dict(type="str", required=False, aliases=["unit"], default="M"),
        volume=dict(type="str", required=False),
        full_volume=dict(type="bool", default=False),
        backup_name=dict(type="str", required=True),
        force=dict(type="bool", default=False),
        sms_storage_class=dict(type="str", required=False),
        sms_management_class=dict(type="str", required=False),
        new_hlq=dict(type="str", required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    try:
        params = parse_and_validate_args(module.params)
        operation = params.get("operation")
        data_sets = params.get("data_sets", {})
        space = params.get("space")
        space_type = params.get("space_type")
        volume = params.get("volume")
        full_volume = params.get("full_volume")
        backup_name = params.get("backup_name")
        force = params.get("force")
        sms_storage_class = params.get("sms_storage_class")
        sms_management_class = params.get("sms_management_class")
        new_hlq = params.get("new_hlq")

        if operation == "backup":
            backup(
                backup_name=backup_name,
                include_data_sets=data_sets.get("include"),
                exclude_data_sets=data_sets.get("exclude"),
                volume=volume,
                full_volume=full_volume,
                force=force,
                space=space,
                space_type=space_type,
            )
        else:
            restore(
                backup_name=backup_name,
                include_data_sets=data_sets.get("include"),
                exclude_data_sets=data_sets.get("exclude"),
                volume=volume,
                full_volume=full_volume,
                new_hlq=new_hlq,
                space=space,
                space_type=space_type,
                sms_storage_class=sms_storage_class,
                sms_management_class=sms_management_class,
            )
        result["changed"] = True

    except Exception as e:
        module.fail_json(msg=repr(e), **result)


def parse_and_validate_args(params):
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
        space=dict(type="int", required=False, aliases=["size"], default=25),
        space_type=dict(type=space_type, required=False, aliases=["unit"], default="M"),
        volume=dict(type="str", required=False, dependencies=["data_sets"]),
        full_volume=dict(type=full_volume_type, default=False, dependencies=["volume"]),
        backup_name=dict(type=backup_name_type, required=False),
        force=dict(type="bool", default=False),
        sms_storage_class=dict(
            type=sms_type, required=False, dependencies=["operation"]
        ),
        sms_management_class=dict(
            type=sms_type, required=False, dependencies=["operation"]
        ),
        new_hlq=dict(type=hlq_type, default=hlq_default, dependencies=["operation"]),
    )

    parsed_args = BetterArgParser(arg_defs).parse_args(params)
    return parsed_args


def backup(
    backup_name,
    include_data_sets,
    exclude_data_sets,
    volume,
    full_volume,
    force,
    space,
    space_type,
):
    args = locals()
    zoau_args = to_dzip_args(**args)
    datasets.zip(**zoau_args)


def restore(
    backup_name,
    include_data_sets,
    exclude_data_sets,
    volume,
    full_volume,
    new_hlq,
    space,
    space_type,
    sms_storage_class,
    sms_management_class,
):
    args = locals()
    zoau_args = to_dunzip_args(**args)
    datasets.unzip(**zoau_args)


def data_set_pattern_type(contents, dependencies):
    if not contents:
        return None
    if isinstance(contents, str):
        contents = [contents]
    elif not isinstance(contents, list):
        raise ValueError(
            "Invalid argument for data set pattern, expected string or list."
        )
    for pattern in contents:
        if not match(
            r"^(?:(?:[A-Za-z$#@\?]{1}[A-Za-z0-9$#@\-\?]{0,7})(?:[.]{1})){1,21}[A-Za-z$#@\*\?]{1}[A-Za-z0-9$#@\-\*\?]{0,7}$",
            str(pattern),
            IGNORECASE,
        ):
            raise ValueError(
                "Invalid argument {0} for data set pattern.".format(contents)
            )
    return [x.upper() for x in contents]


def hlq_type(contents, dependencies):
    if not contents:
        return None
    if dependencies.get("operation") == "backup":
        raise ValueError("hlq_type is only valid when operation=restore.")
    if not match(r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})$", contents, IGNORECASE):
        raise ValueError("Invalid argument {0} for hlq_type.".format(contents))
    return contents.upper()


def hlq_default(contents, dependencies):
    hlq = None
    if dependencies.get("operation") == "restore":
        hlq = datasets.hlq()
    return hlq


def sms_type(contents, dependencies):
    if not contents:
        return None
    if dependencies.get("operation") == "backup":
        raise ValueError("SMS parameters are only valid when operation=restore.")
    if not match(r"^[A-Z\$\*\@\#\%]{1}[A-Z0-9\$\*\@\#\%]{0,7}$", contents, IGNORECASE):
        raise ValueError("Invalid argument {0} for SMS class.".format(contents))
    return str(contents).upper()


def space_type(contents, dependencies):
    """Validates provided data set unit of space is valid.
    Returns the unit of space."""
    if contents is None:
        return None
    if not match(r"^(M|G|K|TRK|CYL)$", contents, IGNORECASE):
        raise ValueError(
            'Value {0} is invalid for space_type argument. Valid space types are "K", "M", "G", "TRK" or "CYL".'.format(
                contents
            )
        )
    return contents


def backup_name_type(contents, dependencies):
    if not contents:
        return None
    if not match(
        r"^(?:(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})(?:[.]{1})){1,21}[A-Z$#@]{1}[A-Z0-9$#@-]{0,7}(?:\([A-Z$#@]{1}[A-Z0-9$#@]{0,7}\)){0,1}$",
        str(contents),
        IGNORECASE,
    ):
        if not path.isabs(str(contents)):
            raise ValueError('Invalid argument "{0}" for type "data_set" or "path".')
    return str(contents)


def full_volume_type(contents, dependencies):
    if contents is True and dependencies.get("volume") is None:
        raise ValueError("full_volume=True is only valid when volume is specified.")
    return contents


def to_dzip_args(**kwargs):
    zoau_args = {}
    if kwargs.get("backup_name"):
        zoau_args["file"] = kwargs.get("backup_name")
        if not kwargs.get("backup_name").startswith("/"):
            zoau_args["dataset"] = True

    if kwargs.get("include_data_sets"):
        zoau_args["target"] = ",".join(kwargs.get("include_data_sets"))

    if kwargs.get("volume"):
        if kwargs.get("full_volume"):
            zoau_args["src_volume"] = kwargs.get("volume")
        else:
            zoau_args["volume"] = True
            zoau_args["target"] = kwargs.get("volume")

    if kwargs.get("exclude_data_sets"):
        zoau_args["exclude"] = ",".join(kwargs.get("exclude_data_sets"))

    if kwargs.get("force"):
        zoau_args["force"] = kwargs.get("force")

    if kwargs.get("space"):
        size = str(kwargs.get("space"))
        if kwargs.get("space_type"):
            size += space_type
        zoau_args["size"] = size
    return zoau_args


def to_dunzip_args(**kwargs):
    zoau_args = {}
    if kwargs.get("backup_name"):
        zoau_args["file"] = kwargs.get("backup_name")
        if not kwargs.get("backup_name").startswith("/"):
            zoau_args["dataset"] = True

    if kwargs.get("include_data_sets"):
        zoau_args["include"] = ",".join(kwargs.get("include_data_sets"))

    if kwargs.get("volume"):
        if kwargs.get("full_volume"):
            zoau_args["src_volume"] = kwargs.get("volume")
        else:
            zoau_args["volume"] = True
            zoau_args["file"] = kwargs.get("volume")

    if kwargs.get("exclude_data_sets"):
        zoau_args["exclude"] = ",".join(kwargs.get("exclude_data_sets"))

    if kwargs.get("force"):
        zoau_args["force"] = kwargs.get("force")

    if kwargs.get("sms_storage_class"):
        zoau_args["storage_class_name"] = kwargs.get("sms_storage_class")

    if kwargs.get("sms_management_class"):
        zoau_args["management_class_name"] = kwargs.get("sms_management_class")

    if kwargs.get("space"):
        size = str(kwargs.get("space"))
        if kwargs.get("space_type"):
            size += space_type
        zoau_args["size"] = size
    return zoau_args


if __name__ == "__main__":
    run_module()
