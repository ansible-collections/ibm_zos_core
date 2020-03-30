#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
module: zos_data_set
short_description: Manage data sets
description:
  - Create, delete and set attributes of data sets.
  - When forcing data set replacement, contents will not be preserved.
version_added: "2.9"
author: "Blake Becker (@blakeinate)"
options:
  name:
    description:
      - The name of the data set being managed. (e.g C(USER.TEST))
      - Name field is required unless using batch option
    type: str
    required: false
    version_added: "2.9"
  state:
    description:
      - The final state desired for specified data set.
      - >
        If I(state=absent) and the data set does not exist on the managed node,
        no action taken, returns successful with I(changed=False).
      - >
        If I(state=absent) and the data set does exist on the managed node,
        remove the data set, returns successful with I(changed=True).
      - >
        If I(state=present) and the data set does not exist on the managed node,
        create the data set, returns successful with I(changed=True).
      - >
        If I(state=present) and I(replace=True) and the data set is present on
        the managed node, delete the data set and create the data set with the
        desired attributes, returns successful with I(changed=True).
      - >
        If I(state=present) and I(replace=False) and the data set is present
        on the managed node, no action taken, returns successful with I(changed=False).
    required: false
    type: str
    default: present
    choices:
      - present
      - absent
      - cataloged
      - uncataloged
    version_added: "2.9"
  type:
    description:
      - The data set type to be used when creating a data set. (e.g C(pdse))
      - MEMBER expects to be used with an existing partitioned data set.
      - Choices are case-insensitive.
    required: false
    type: str
    choices:
      - ESDS
      - RRDS
      - LDS
      - SEQ
      - PDS
      - PDSE
      - MEMBER
    version_added: "2.9"
  size:
    description:
      - The size of the data set (e.g C(5M)).
      - Valid units of size are C(K), C(M), C(G), C(CYL), and C(TRK).
      - Note that C(CYL) and C(TRK) follow size conventions for 3390 disk types (56,664 bytes/TRK & 849,960 bytes/CYL).
      - The C(CYL) and C(TRK) units are converted to bytes and rounded up to the nearest C(K) measurement.
      - Ensure there is no space between the numeric size and unit.
    type: str
    required: false
    default: 5M
    version_added: "2.9"
  format:
    description:
      - The format of the data set. (e.g C(FB))
      - Choices are case-insensitive.
    required: false
    choices:
      - FB
      - VB
      - FBA
      - VBA
      - U
    default: FB
    type: str
    version_added: "2.9"
  data_class:
    description:
      - The data class name.
      - Required for SMS managed data sets.
    type: str
    required: false
    version_added: "2.9"
  record_length:
    description:
      - The logical record length (e.g C(80)).
      - For variable data sets, the length must include the 4-byte prefix area.
      - Defaults vary depending on format. If FB/FBA 80, if VB/VBA 137, if U 0
    type: int
    required: false
    version_added: "2.9"
  volume:
    description:
      - >
        The name of the volume where the data set is located.
        I(volume) is not used to specify the volume where a data set should be created.
      - >
        If I(volume) is provided when I(state=present), and the data set is not found in the catalog,
        M(zos_data_set) will check the volume table of contents to see if the data set exists.
        If the data set does exist, it will be cataloged.
      - >
        If I(volume) is provided when I(state=absent) and the data set is not found in the catalog,
        M(zos_data_set) will check the volume table of contents to see if the data set exists.
        If the data set does exist, it will be cataloged and promptly removed from the system.
      - I(volume) is required when I(state=cataloged)
    type: str
    required: false
    version_added: "2.9"
  replace:
    description:
      - When I(replace=True), and I(state=present), existing data set matching I(name) will be replaced.
      - >
        Replacement is performed by deleting the existing data set and creating a new data set with the same name and desired
        attributes. This may lead to an inconsistent state if data set creations fails.
        after the old data set is deleted.
      - If I(replace=True), all data in the original data set will be lost.
    type: bool
    required: false
    default: false
    version_added: "2.9"
  batch:
    description:
      - Batch can be used to perform operations on multiple data sets in a single module call.
    type: list
    elements: dict
    required: false
    version_added: "2.9"
    suboptions:
      name:
        description:
          - The name of the data set being managed. (e.g C(USER.TEST))
          - Name field is required unless using batch option.
        type: str
        required: true
        version_added: "2.9"
      state:
        description:
          - The final state desired for specified data set.
          - >
            If I(state=absent) and the data set does not exist on the managed node,
            no action taken, returns successful with I(changed=False).
          - >
            If I(state=absent) and the data set does exist on the managed node,
            remove the data set, returns successful with I(changed=True).
          - >
            If I(state=present) and the data set does not exist on the managed node,
            create the data set, returns successful with I(changed=True).
          - >
            If I(state=present) and I(replace=True) and the data set is present on
            the managed node, delete the data set and create the data set with the
            desired attributes, returns successful with I(changed=True).
          - >
            If I(state=present) and I(replace=False) and the data set is present
            on the managed node, no action taken, returns successful with I(changed=False).
        required: false
        type: str
        default: present
        choices:
          - present
          - absent
        version_added: "2.9"
      type:
        description:
          - The data set type to be used when creating a data set. (e.g C(pdse))
          - MEMBER expects to be used with an existing partitioned data set.
          - Choices are case-insensitive.
        required: false
        type: str
        choices:
          - ESDS
          - RRDS
          - LDS
          - SEQ
          - PDS
          - PDSE
          - MEMBER
        version_added: "2.9"
      size:
        description:
          - The size of the data set (e.g C(5M))
          - Valid units of size are C(K), C(M), C(G), C(CYL), and C(TRK)
          - Note that C(CYL) and C(TRK) follow size conventions for 3390 disk types (56,664 bytes/TRK & 849,960 bytes/CYL)
          - The C(CYL) and C(TRK) units are converted to bytes and rounded up to the nearest C(K) measurement.
          - Ensure there is no space between the numeric size and unit.
        type: str
        required: false
        default: 5M
        version_added: "2.9"
      format:
        description:
          - The format of the data set. (e.g C(FB))
          - Choices are case-insensitive.
        required: false
        choices:
          - FB
          - VB
          - FBA
          - VBA
          - U
        default: FB
        type: str
        version_added: "2.9"
      data_class:
        description:
          - The data class name.
          - Required for SMS managed data sets.
        type: str
        required: false
        version_added: "2.9"
      record_length:
        description:
          - The logical record length. (e.g C(80))
          - For variable data sets, the length must include the 4-byte prefix area.
          - Defaults vary depending on format. If FB/FBA 80, if VB/VBA 137, if U 0
        type: int
        required: false
        version_added: "2.9"
      volume:
        description:
          - >
            The name of the volume where the data set is located.
            I(volume) is not used to specify the volume where a data set should be created.
          - >
            If I(volume) is provided when I(state=present), and the data set is not found in the catalog,
            M(zos_data_set) will check the volume table of contents to see if the data set exists.
            If the data set does exist, it will be cataloged.
          - >
            If I(volume) is provided when I(state=absent) and the data set is not found in the catalog,
            M(zos_data_set) will check the volume table of contents to see if the data set exists.
            If the data set does exist, it will be cataloged and promptly removed from the system.
          - I(volume) is required when I(state=cataloged)
        type: str
        required: false
        version_added: "2.9"
      replace:
        description:
          - When I(replace=True), and I(state=present), existing data set matching I(name) will be replaced.
          - >
            Replacement is performed by deleting the existing data set and creating a new data set with
            the same name and desired attributes. This may lead to an inconsistent state if data set creations fails
            after the old data set is deleted.
          - If I(replace=True), all data in the original data set will be lost.
        type: bool
        required: false
        default: false
        version_added: "2.9"

"""
EXAMPLES = r"""
- name: Create a sequential data set if it does not exist
  zos_data_set:
    name: user.private.libs
    type: seq
    state: present

- name: Create a PDS data set if it does not exist
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: fba
    record_length: 25

- name: Attempt to replace a data set if it exists
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: u
    record_length: 25
    replace: yes

- name: Attempt to replace a data set if it exists. If not found in catalog, check if on volume 222222 and catalog if found.
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: u
    record_length: 25
    volume: "222222"
    replace: yes

- name: Create an ESDS data set is it does not exist
  zos_data_set:
    name: user.private.libs
    type: esds

- name: Create an RRDS data set with data class MYDATA if it does not exist
  zos_data_set:
    name: user.private.libs
    type: rrds
    data_class: mydata

- name: Delete a data set if it exists
  zos_data_set:
    name: user.private.libs
    state: absent

- name: Delete a data set if it exists. If data set not cataloged, check on volume 222222 for the data set, then catalog and delete if found.
  zos_data_set:
    name: user.private.libs
    state: absent
    volume: "222222"

- name: Write a member to existing PDS, replace if member exists
  zos_data_set:
    name: user.private.libs(mydata)
    type: MEMBER
    replace: yes

- name: Write a member to existing PDS, do not replace if member exists
  zos_data_set:
    name: user.private.libs(mydata)
    type: MEMBER

- name: Remove a member from existing PDS if it exists
  zos_data_set:
    name: user.private.libs(mydata)
    state: absent
    type: MEMBER

- name: Create multiple partitioned data sets and add one or more members to each
  zos_data_set:
    batch:
      - name:  user.private.libs1
        type: PDS
        size: 5M
        format: fb
        replace: yes
      - name: user.private.libs1(member1)
        type: MEMBER
      - name: user.private.libs2(member1)
        type: MEMBER
        replace: yes
      - name: user.private.libs2(member2)
        type: MEMBER

- name: Catalog a data set present on volume 222222 if it is uncataloged.
  zos_data_set:
    name: user.private.libs
    state: cataloged
    volume: "222222"

- name: Uncatalog a data set if it is cataloged.
  zos_data_set:
    name: user.private.libs
    state: uncataloged
"""
RETURN = r"""

"""

import tempfile
from math import ceil
from collections import OrderedDict
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.vtoc import (
    VolumeTableOfContents,
)

try:
    from zoautil_py import Datasets, types, MVSCmd
except Exception:
    Datasets = ""
import re
from ansible.module_utils.basic import AnsibleModule

# CONSTANTS
DATA_SET_TYPES = [
    # 'KSDS',
    "ESDS",
    "RRDS",
    "LDS",
    "SEQ",
    "PDS",
    "PDSE",
    "MEMBER",
]

DATA_SET_FORMATS = [
    "FB",
    "VB",
    "FBA",
    "VBA",
    "U",
]

DEFAULT_RECORD_LENGTHS = {
    "FB": 80,
    "FBA": 80,
    "VB": 137,
    "VBA": 137,
    "U": 0,
}

# Module args mapped to equivalent ZOAU data set create args
ZOAU_DS_CREATE_ARGS = {
    "name": "name",
    "type": "type",
    "size": "size",
    "format": "format",
    "data_class": "class_name",
    "record_length": "length",
    "key_offset": "offset",
}

VSAM_CATALOG_COMMAND_NOT_INDEXED = """ DEFINE CLUSTER -
    (NAME('{0}') -
    VOLUMES({1}) -
    RECATALOG -
    {2}) -
  DATA( -
    NAME('{0}.DATA'))
"""

VSAM_CATALOG_COMMAND_INDEXED = """ DEFINE CLUSTER -
    (NAME('{0}') -
    VOLUMES({1}) -
    RECATALOG -
    {2}) -
  DATA( -
    NAME('{0}.DATA')) -
  INDEX( -
    NAME('{0}.INDEX'))
"""

NON_VSAM_UNCATALOG_COMMAND = " UNCATLG DSNAME={0}"

VSAM_UNCATALOG_COMMAND = " DELETE '{0}' NOSCRATCH"

# ------------- Functions to validate arguments ------------- #


def get_individual_data_set_parameters(params):
    """Builds a list of data set parameters
    to be used in future operations.

    Arguments:
        params {dict} -- The parameters from
        Ansible's AnsibleModule object module.params.

    Raises:
        ValueError: Raised if top-level parameters "name"
        and "batch" are both provided.
        ValueError: Raised if neither top-level parameters "name"
        or "batch" are provided.

    Returns:
        [list] -- A list of dicts where each list item
        represents one data set. Each dictionary holds the parameters
        (passed to the zos_data_set module) for the data set which it represents.
    """
    if params.get("name") and params.get("batch"):
        raise ValueError(
            'Top-level parameters "name" and "batch" are mutually exclusive.'
        )
    elif not params.get("name") and not params.get("batch"):
        raise ValueError(
            'One of the following parameters is required: "name", "batch".'
        )
    if params.get("name"):
        data_sets_parameter_list = [params]
    else:
        data_sets_parameter_list = params.get("batch")
    return data_sets_parameter_list


def process_special_parameters(original_params, param_handlers):
    """Perform checks, validation, and value modification
    on parameters.

    Arguments:
        original_params {Dict} -- The parameters from
        Ansible's AnsibleModule object module.params.
        param_handlers {OrderedDict} -- Contains key:value pairs
        where the key is a parameter name as returned by Ansible's
        argument parser and the value is the function to call to perform
        the validation. The function passed for the value should take
        two arguments: 1) the param value 2) a dictionary containing
        all parameters that have already been processed by
        process_special_parameters. Handlers are ran sequentially
        based on their ordering in param_handlers. If a parameter is dependent
        on the final value of another parameter, make sure they are ordered
        accordingly.

        Example of param_handlers::

        def record_length(arg_val, params):
            lengths = {
                'VB': 80,
                'U': 0
            }
            if not arg_val:
                value = lengths.get(params.get('format'), 80)
            else:
                value = int(arg_val)
            if not re.fullmatch(r'[1-9][0-9]*', arg_val) or (value < 1 or value > 32768):
                raise ValueError(('Value {0} is invalid for record_length argument.'
                 'record_length must be between 1 and 32768 bytes.').format(arg_val))
            return value

        module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
        )

        parameter_handlers = OrderedDict()
        parameter_handlers['format'] = data_set_format
        parameter_handlers['record_length'] = record_length

        process_special_parameters(module.params, parameter_handlers)
    Returns:
        Dict -- A dictionary containing the updated parameters.
    """
    parameters = {}
    for key, value in param_handlers.items():
        parameters[key] = value(original_params.get(key), parameters, original_params)
    for key, value in original_params.items():
        if key not in parameters:
            parameters[key] = value
    return parameters


def data_set_name(arg_val, params, original_params):
    """Validates provided data set name(s) are valid.
    Returns a list containing the name(s) of data sets."""
    dsname = arg_val
    if not re.fullmatch(
        r"^(?:(?:[A-Z]{1}[A-Z0-9]{0,7})(?:[.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}$",
        dsname,
        re.IGNORECASE,
    ):
        if not (
            re.fullmatch(
                r"^(?:(?:[A-Z]{1}[A-Z0-9]{0,7})(?:[.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}\([A-Z]{1}[A-Z0-9]{0,7}\)$",
                dsname,
                re.IGNORECASE,
            )
            and params.get("type") == "MEMBER"
        ):
            raise ValueError(
                "Value {0} is invalid for data set argument.".format(dsname)
            )
    return dsname.upper()


def data_set_size(arg_val, params, original_params):
    """Validates provided data set size is valid.
    Returns the data set size. """
    if params.get("state") == "absent":
        return None
    if arg_val is None:
        return None
    match = re.fullmatch(r"([1-9][0-9]*)(M|G|K|TRK|CYL)", arg_val, re.IGNORECASE)
    if not match:
        raise ValueError(
            'Value {0} is invalid for size argument. Valid size measurements are "K", "M", "G", "TRK" or "CYL".'.format(
                arg_val
            )
        )
    if re.fullmatch(r"TRK|CYL", match.group(2), re.IGNORECASE):
        arg_val = (
            str(convert_size_to_kilobytes(int(match.group(1)), match.group(2).upper()))
            + "K"
        )
    return arg_val


def data_class(arg_val, params, original_params):
    """Validates provided data class is of valid length.
    Returns the data class. """
    if params.get("state") == "absent" or not arg_val:
        return None
    if len(arg_val) < 1 or len(arg_val) > 8:
        raise ValueError(
            (
                "Value {0} is invalid for data_class argument. "
                "data_class must be at least 1 and at most 8 characters."
            ).format(arg_val)
        )
    return arg_val


def record_length(arg_val, params, original_params):
    """Validates provided record length is valid.
    Returns the record length as integer."""
    if params.get("state") == "absent":
        return None
    arg_val = (
        DEFAULT_RECORD_LENGTHS.get(params.get("format"), None)
        if not arg_val
        else int(arg_val)
    )
    if arg_val is None:
        return None
    if not re.fullmatch(r"[0-9]*", str(arg_val)) or (arg_val < 0 or arg_val > 32768):
        raise ValueError(
            "Value {0} is invalid for record_length argument. record_length must be between 0 and 32768 bytes.".format(
                arg_val
            )
        )
    return arg_val


def data_set_format(arg_val, params, original_params):
    """Validates data set format is valid.
    Returns uppercase data set format."""
    if params.get("state") == "absent":
        return None
    if arg_val is None and params.get("record_length") is not None:
        raise ValueError("format must be provided when providing record_length.")
    if arg_val is None:
        return None
    formats = "|".join(DATA_SET_FORMATS)
    if not re.fullmatch(formats, arg_val, re.IGNORECASE):
        raise ValueError(
            "Value {0} is invalid for format argument. format must be of of the following: {1}.".format(
                arg_val, ", ".join(DATA_SET_FORMATS)
            )
        )
    return arg_val.upper()


def key_offset(arg_val, params, original_params):
    """Validates data set offset is valid.
    Returns data set offset as integer."""
    if params.get("state") == "absent":
        return None
    if params.get("type") == "KSDS" and arg_val is None:
        raise ValueError("key_offset is required when requesting KSDS data set.")
    if arg_val is None:
        return None
    arg_val = int(arg_val)
    if not re.fullmatch(r"[0-9]+", str(arg_val)):
        raise ValueError(
            "Value {0} is invalid for offset argument. offset must be between 0 and length of object - 1.".format(
                arg_val
            )
        )
    return arg_val


def data_set_type(arg_val, params, original_params):
    """Validates data set type is valid.
    Returns uppercase data set type."""
    if params.get("state") == "absent":
        return None
    if arg_val is None:
        return None
    types = "|".join(DATA_SET_TYPES)
    if not re.fullmatch(types, arg_val, re.IGNORECASE):
        raise ValueError(
            "Value {0} is invalid for type argument. type must be of of the following: {1}.".format(
                arg_val, ", ".join(DATA_SET_TYPES)
            )
        )
    return arg_val.upper()


def volume(arg_val, params, original_params):
    """Validates volume is valid.
    Returns uppercase volume."""
    if arg_val is None:
        if original_params.get("state") == "cataloged":
            raise ValueError("Volume is required when state==cataloged.")
        return None
    if not re.fullmatch(r"^[A-Z0-9]{1,6}$", str(arg_val), re.IGNORECASE,):
        raise ValueError(
            'Invalid argument type for "{0}". expected "volume"'.format(arg_val)
        )
    return arg_val.upper()


def convert_size_to_kilobytes(old_size, old_size_unit):
    """Convert unsupported size unit to KB.
    Assumes 3390 disk type."""
    # Size measurements in bytes
    KB = 1024
    TRK = 56664
    CYL = 849960
    old_size = int(old_size)
    if old_size_unit == "TRK":
        new_size = ceil((old_size * TRK) / KB)
    elif old_size_unit == "CYL":
        new_size = ceil((old_size * CYL) / KB)
    return new_size


class DataSetHandler(object):
    def __init__(self, module):
        """Handles various data set operations.

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object created in the module.
        """

        self.module = module

    def perform_data_set_operations(self, name, state, **extra_args):
        """ Calls functions to perform desired operations on
        one or more data sets. Returns boolean indicating if changes were made. """
        changed = False
        if state == "present" and extra_args.get("type") != "MEMBER":
            changed = self._ensure_data_set_present(name, **extra_args)
        elif state == "present" and extra_args.get("type") == "MEMBER":
            changed = self._ensure_data_set_member_present(name, **extra_args)
        elif state == "absent" and extra_args.get("type") != "MEMBER":
            changed = self._ensure_data_set_absent(name, **extra_args)
        elif state == "absent" and extra_args.get("type") == "MEMBER":
            changed = self._ensure_data_set_member_absent(name)
        elif state == "cataloged":
            changed = self._ensure_data_set_cataloged(name, extra_args.get("volume"))
        elif state == "uncataloged":
            changed = self._ensure_data_set_uncataloged(name)
        return changed

    def _ensure_data_set_present(self, name, replace, **extra_args):
        """Creates data set if it does not already exist.

        Arguments:
            name {str} -- The name of the data set to ensure is present.
            replace {bool} -- Used to determine behavior when data set already exists.

        Returns:
            bool -- Indicates if changes were made.
        """
        ds_create_args = self._rename_args_for_zoau(extra_args)
        present, changed = self._attempt_catalog_if_necessary(
            name, extra_args.get("volume")
        )
        if present:
            if not replace:
                return changed
            self._replace_data_set(name, ds_create_args)
        else:
            self._create_data_set(name, ds_create_args)
        return True

    def _ensure_data_set_absent(self, name, **extra_args):
        """Deletes provided data set if it exists.

        Arguments:
            name {str} -- The name of the data set to ensure is absent.

        Returns:
            bool -- Indicates if changes were made.
        """
        present, changed = self._attempt_catalog_if_necessary(
            name, extra_args.get("volume")
        )
        if present:
            self._delete_data_set(name)
            return True
        return False

    # ? should we do additional check to ensure member was actually created?

    def _ensure_data_set_member_present(self, name, replace, **extra_args):
        """Creates data set member if it does not already exist.

        Arguments:
            name {str} -- The name of the data set to ensure is present.
            replace {bool} -- Used to determine behavior when data set already
        exists.

        Returns:
            bool -- Indicates if changes were made.
        """
        if self._data_set_member_exists(name):
            if not replace:
                return False
            self._delete_data_set_member(name)
        self._create_data_set_member(name)
        return True

    def _ensure_data_set_member_absent(self, name):
        """Deletes provided data set member if it exists.
        Returns a boolean indicating if changes were made."""
        if self._data_set_member_exists(name):
            self._delete_data_set_member(name)
            return True
        return False

    def _ensure_data_set_cataloged(self, name, volume):
        """Ensure a data set is cataloged. Data set can initially
        be in cataloged or uncataloged state when this function is called.

        Arguments:
            name {str} -- The data set name to ensure is cataloged.
            volume {str} -- The volume on which the data set should exist.

        Returns:
            bool -- If changes were made.
        """
        if self._data_set_cataloged(name):
            return False
        try:
            self._catalog_data_set(name, volume)
        except DatasetCatalogError:
            raise DatasetCatalogError(
                name, volume, "-1", "Data set was not found. Unable to catalog."
            )
        return True

    def _ensure_data_set_uncataloged(self, name):
        """Ensure a data set is uncataloged. Data set can initially
        be in cataloged or uncataloged state when this function is called.

        Arguments:
            name {str} -- The data set name to ensure is uncataloged.

        Returns:
            bool -- If changes were made.
        """
        if self._data_set_cataloged(name):
            self._uncatalog_data_set(name)
            return True
        return False

    def _data_set_cataloged(self, name):
        """Determine if a data set is in catalog.

        Arguments:
            name {str} -- The data set name to check if cataloged.

        Returns:
            bool -- If data is is cataloged.
        """
        stdin = " LISTCAT ENTRIES('{0}')".format(name)
        rc, stdout, stderr = self.module.run_command(
            "mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin", data=stdin
        )
        if re.search(r"-\s" + name + r"\s*\n\s+IN-CAT", stdout):
            return True
        return False

    def _data_set_exists(self, name, volume=None):
        """Determine if a data set exists.
        This will check the catalog in addition to
        the volume table of contents.

        Arguments:
            name {str} -- The data set name to check if exists.
            volume {str} -- The volume the data set may reside on.

        Returns:
            bool -- If data is found.
        """
        if self._data_set_cataloged(name):
            return True
        elif volume is not None:
            return self._is_in_vtoc(name, volume)
        return False

    def _data_set_member_exists(self, name):
        """Checks for existence of data set member.

        Arguments:
            name {str} -- The data set name including member.

        Returns:
            bool -- If data set member exists.
        """
        rc, stdout, stderr = self.module.run_command("head \"//'{0}'\"".format(name))
        if rc != 0 or (stderr and "EDC5067I" in stderr):
            return False
        return True

    def _attempt_catalog_if_necessary(self, name, volume):
        """Attempts to catalog a data set if not already cataloged.

        Arguments:
            name {str} -- The name of the data set.
            volume {str} -- The volume the data set may reside on.

        Returns:
            bool -- Whether the data set is now present.
            bool -- Whether changes were made.
        """
        changed = False
        present = False
        if self._data_set_cataloged(name):
            present = True
        elif volume is not None:
            errors = False
            try:
                self._catalog_data_set(name, volume)
            except DatasetCatalogError:
                errors = True
            if not errors:
                changed = True
                present = True
        return present, changed

    def _is_in_vtoc(self, name, volume):
        """Determines if data set is in a volume's table of contents.

        Arguments:
            name {str} -- The name of the data set to search for.
            volume {str} -- The volume to search the table of contents of.

        Returns:
            bool -- If data set was found in table of contents for volume.
        """
        vtoc = VolumeTableOfContents(self.module)
        data_sets = vtoc.get_volume_entry(volume)
        data_set = VolumeTableOfContents.find_data_set_in_volume_output(name, data_sets)
        if data_set is not None:
            return True
        vsam_name = name + ".data"
        vsam_data_set = VolumeTableOfContents.find_data_set_in_volume_output(
            vsam_name, data_sets
        )
        if vsam_data_set is not None:
            return True
        return False

    def _replace_data_set(self, name, extra_args):
        """Attempts to replace an existing data set.

        Arguments:
            name {str} -- The name of the data set to replace.
            extra_args {dict} -- Any additional arguments.
        """
        self._delete_data_set(name)
        self._create_data_set(name, extra_args)
        return

    def _rename_args_for_zoau(self, args=None):
        """Renames module arguments to match those desired by
        zoautil_py data set create method.

        Keyword Arguments:
            args {dict} -- The arguments for data set operations. (default: {None})

        Returns:
            dict -- The original dictionary with keys replaced to match ZOAU requirements.
        """
        if args is None:
            args = {}
        ds_create_args = {}
        for module_arg_name, zoau_arg_name in ZOAU_DS_CREATE_ARGS.items():
            if args.get(module_arg_name):
                ds_create_args[zoau_arg_name] = args.get(module_arg_name)
        return ds_create_args

    def _create_data_set(self, name, extra_args=None):
        """A wrapper around zoautil_py
        Dataset.create() to raise exceptions on failure.

        Arguments:
            name {str} -- The name of the data set to create.

        Raises:
            DatasetCreateError: When data set creation fails.
        """
        if extra_args is None:
            extra_args = {}
        rc = Datasets.create(name, **extra_args)
        if rc > 0:
            raise DatasetCreateError(name, rc)
        return

    def _delete_data_set(self, name):
        """A wrapper around zoautil_py
        Dataset.delete() to raise exceptions on failure.

        Arguments:
            name {str} -- The name of the data set to delete.

        Raises:
            DatasetDeleteError: When data set deletion fails.
        """
        rc = Datasets.delete(name)
        if rc > 0:
            raise DatasetDeleteError(name, rc)
        return

    def _create_data_set_member(self, name):
        """Create a data set member if the partitioned data set exists.
        Also used to overwrite a data set member if empty replacement is desired.

        Arguments:
            name {str} -- The data set name, including member name, to create.

        Raises:
            DatasetNotFoundError: If data set cannot be found.
            DatasetMemberCreateError: If member creation fails.
        """
        base_dsname = name.split("(")[0]
        if not base_dsname or not self._data_set_cataloged(base_dsname):
            raise DatasetNotFoundError(name)
        tmp_file = tempfile.NamedTemporaryFile(delete=True)
        rc, stdout, stderr = self.module.run_command(
            "cp {0} \"//'{1}'\"".format(tmp_file.name, name)
        )
        if rc != 0:
            raise DatasetMemberCreateError(name, rc)
        return

    def _delete_data_set_member(self, name):
        """A wrapper around zoautil_py
        Dataset.delete_members() to raise exceptions on failure.

        Arguments:
            name {str} -- The name of the data set, including member name, to delete.

        Raises:
            DatasetMemberDeleteError: When data set member deletion fails.
        """
        rc = Datasets.delete_members(name)
        if rc > 0:
            raise DatasetMemberDeleteError(name, rc)
        return

    def _catalog_data_set(self, name, volume):
        """Catalog an uncataloged data set

        Arguments:
            name {str} -- The name of the data set to catalog
            volume {str} -- The volume the data set resides on
        """
        if self._is_data_set_vsam(name, volume):
            self._catalog_vsam_data_set(name, volume)
        else:
            self._catalog_non_vsam_data_set(name, volume)

    def _catalog_non_vsam_data_set(self, name, volume):
        """Catalog a non-VSAM data set.

        Arguments:
            name {str} -- The data set to catalog.
            volume {str} -- The volume the data set resides on.

        Raises:
            DatasetCatalogError: When attempt at catalog fails.
        """
        iehprogm_input = self._build_non_vsam_catalog_command(name, volume)
        try:
            temp_data_set_name = self._create_temp_data_set(name.split(".")[0])
            self._write_data_set(temp_data_set_name, iehprogm_input)
            rc, stdout, stderr = self.module.run_command(
                "mvscmdauth --pgm=iehprogm --sysprint=* --sysin={0}".format(
                    temp_data_set_name
                )
            )
            if rc != 0 or "NORMAL END OF TASK RETURNED" not in stdout:
                raise DatasetCatalogError(name, volume, rc)
        except Exception:
            raise
        finally:
            Datasets.delete(temp_data_set_name)
        return

    def _catalog_vsam_data_set(self, name, volume):
        """Catalog a VSAM data set.

        Arguments:
            name {str} -- The data set to catalog.
            volume {str} -- The volume the data set resides on.

        Raises:
            DatasetCatalogError: When attempt at catalog fails.
        """
        data_set_name = name.upper()
        data_set_volume = volume.upper()
        success = False
        try:
            temp_data_set_name = self._create_temp_data_set(name.split(".")[0])
            command_rc = 0
            for data_set_type in ["", "LINEAR", "INDEXED", "NONINDEXED", "NUMBERED"]:
                if data_set_type != "INDEXED":
                    command = VSAM_CATALOG_COMMAND_NOT_INDEXED.format(
                        data_set_name, data_set_volume, data_set_type
                    )
                else:
                    command = VSAM_CATALOG_COMMAND_INDEXED.format(
                        data_set_name, data_set_volume, data_set_type
                    )

                self._write_data_set(temp_data_set_name, command)
                dd_statements = []
                dd_statements.append(
                    types.DDStatement(ddName="sysin", dataset=temp_data_set_name)
                )
                dd_statements.append(types.DDStatement(ddName="sysprint", dataset="*"))
                command_rc = MVSCmd.execute_authorized(
                    pgm="idcams", args="", dds=dd_statements
                )
                if command_rc == 0:
                    success = True
                    break
            if not success:
                raise DatasetCatalogError(
                    name, volume, command_rc, "Attempt to catalog VSAM data set failed."
                )
        except Exception:
            raise
        finally:
            Datasets.delete(temp_data_set_name)
        return

    def _uncatalog_data_set(self, name):
        """Uncatalog a data set.

        Arguments:
            name {str} -- The name of the data set to uncatalog.
        """
        if self._is_data_set_vsam(name):
            self._uncatalog_vsam_data_set(name)
        else:
            self._uncatalog_non_vsam_data_set(name)
        return

    def _uncatalog_non_vsam_data_set(self, name):
        """Uncatalog a non-VSAM data set.

        Arguments:
            name {str} -- The name of the data set to uncatalog.

        Raises:
            DatasetUncatalogError: When uncataloging fails.
        """
        iehprogm_input = NON_VSAM_UNCATALOG_COMMAND.format(name)
        try:
            temp_data_set_name = self._create_temp_data_set(name.split(".")[0])
            self._write_data_set(temp_data_set_name, iehprogm_input)
            rc, stdout, stderr = self.module.run_command(
                "mvscmdauth --pgm=iehprogm --sysprint=* --sysin={0}".format(
                    temp_data_set_name
                )
            )
            if rc != 0 or "NORMAL END OF TASK RETURNED" not in stdout:
                raise DatasetUncatalogError(name, rc)
        except Exception:
            raise
        finally:
            Datasets.delete(temp_data_set_name)
        return

    def _uncatalog_vsam_data_set(self, name):
        """Uncatalog a VSAM data set.

        Arguments:
            name {str} -- The name of the data set to uncatalog.

        Raises:
            DatasetUncatalogError: When uncataloging fails.
        """
        idcams_input = VSAM_UNCATALOG_COMMAND.format(name)
        try:
            temp_data_set_name = self._create_temp_data_set(name.split(".")[0])
            self._write_data_set(temp_data_set_name, idcams_input)
            dd_statements = []
            dd_statements.append(
                types.DDStatement(ddName="sysin", dataset=temp_data_set_name)
            )
            dd_statements.append(types.DDStatement(ddName="sysprint", dataset="*"))
            rc = MVSCmd.execute_authorized(pgm="idcams", args="", dds=dd_statements)
            if rc != 0:
                raise DatasetUncatalogError(name, rc)
        except Exception:
            raise
        finally:
            Datasets.delete(temp_data_set_name)
        return

    def _is_data_set_vsam(self, name, volume=None):
        """Determine a given data set is VSAM. If volume is not provided,
        then LISTCAT will be used to check data set info. If volume is provided,
        then VTOC will be used to check data set info. If not in VTOC
        may not return accurate information.

        Arguments:
            name {str} -- The name of the data set.

        Keyword Arguments:
            volume {str} -- The name of the volume. (default: {None})

        Returns:
            bool -- If the data set is VSAM.
        """
        if not volume:
            return self._is_data_set_vsam_from_listcat(name)
        return self._is_data_set_vsam_from_vtoc(name, volume)

    def _is_data_set_vsam_from_vtoc(self, name, volume):
        """Use VTOC to determine if a given data set is VSAM.

        Arguments:
            name {str} -- The name of the data set.
            volume {str} -- The volume name whose table of contents will be searched.

        Returns:
            bool -- If the data set is VSAM.
        """
        vtoc = VolumeTableOfContents(self.module)
        data_sets = vtoc.get_volume_entry(volume)
        vsam_name = name + ".DATA"
        data_set = VolumeTableOfContents.find_data_set_in_volume_output(
            vsam_name, data_sets
        )
        if data_set is None:
            data_set = VolumeTableOfContents.find_data_set_in_volume_output(
                name, data_sets
            )
        if data_set is not None:
            if data_set.get("data_set_organization", "") == "VS":
                return True
        return False

    def _is_data_set_vsam_from_listcat(self, name):
        """Use LISTCAT command to determine if a given data set is VSAM.

        Arguments:
            name {str} -- The name of the data set.

        Returns:
            bool -- If the data set is VSAM.
        """
        stdin = " LISTCAT ENTRIES('{0}')".format(name)
        rc, stdout, stderr = self.module.run_command(
            "mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin", data=stdin
        )
        if re.search(r"^0CLUSTER[ ]+-+[ ]+" + name + r"[ ]*$", stdout, re.MULTILINE):
            return True
        return False

    def _create_temp_data_set(self, hlq):
        """Create a temporary data set.

        Arguments:
            hlq {str} -- The HLQ to use for the temporary data set's name.

        Returns:
            str -- The name of the temporary data set.
        """
        temp_data_set_name = Datasets.temp_name(hlq)
        self._create_data_set(
            temp_data_set_name,
            {"type": "SEQ", "size": "5M", "format": "FB", "length": 80},
        )
        return temp_data_set_name

    def _write_data_set(self, name, contents):
        """Write text to a data set.

        Arguments:
            name {str} -- The name of the data set.
            contents {str} -- The text to write to the data set.

        Raises:
            DatasetWriteError: When write to the data set fails.
        """
        # rc = Datasets.write(name, contents)
        temp = tempfile.NamedTemporaryFile(delete=False)
        with open(temp.name, "w") as f:
            f.write(contents)
        rc, stdout, stderr = self.module.run_command(
            "cp -O u {0} \"//'{1}'\"".format(temp.name, name)
        )
        if rc != 0:
            raise DatasetWriteError(name, rc, stderr)
        return

    def _build_non_vsam_catalog_command(self, name, volume):
        """Build the command string to use
        for non-VSAM data set catalog operation.
        This is necessary because IEHPROGM required
        strict formatting when spanning multiple lines.

        Arguments:
            name {str} -- The data set to catalog.
            volume {str} -- The volume the data set resides on.

        Returns:
            str -- The command string formatted for use with IEHPROGM.
        """
        command_part_1 = "    CATLG DSNAME={0},".format(name)
        command_part_2 = "               VOL=3390=({0})".format(volume)
        command_part_1 = "{line: <{max_len}}".format(line=command_part_1, max_len=71)
        command_part_1 += "X"
        return command_part_1 + "\n" + command_part_2


# TODO: Add back safe data set replacement when issues are resolved
# TODO: switch argument parsing over to BetterArgParser


def run_module():
    # TODO: add logic to handle aliases during parsing
    module_args = dict(
        # Used for batch data set args
        batch=dict(
            type="list",
            elements="dict",
            options=dict(
                name=dict(type="str", required=True,),
                state=dict(
                    type="str",
                    default="present",
                    choices=["present", "absent", "cataloged", "uncataloged"],
                ),
                type=dict(type="str", required=False,),
                size=dict(type="str", required=False),
                format=dict(type="str", required=False,),
                data_class=dict(type="str", required=False,),
                record_length=dict(type="int",),
                # NEEDS FIX FROM ZOAUTIL
                # key_offset=dict(
                #     type='int',
                #     required=False,
                #     aliases=['offset']
                # ),
                replace=dict(type="bool", default=False,),
                volume=dict(type="str", required=False)
                # unsafe_writes=dict(
                #     type='bool',
                #     default=False
                # )
            ),
        ),
        # For individual data set args
        name=dict(type="str"),
        state=dict(
            type="str",
            default="present",
            choices=["present", "absent", "cataloged", "uncataloged"],
        ),
        type=dict(type="str", required=False,),
        size=dict(type="str", required=False),
        format=dict(type="str", required=False,),
        data_class=dict(type="str", required=False,),
        record_length=dict(type="int",),
        # NEEDS FIX FROM ZOAUTIL
        # key_offset=dict(
        #     type='int',
        #     required=False,
        #     aliases=['offset']
        # ),
        replace=dict(type="bool", default=False,),
        volume=dict(type="str", required=False),
        # unsafe_writes=dict(
        #     type='bool',
        #     default=False
        # )
    )

    result = dict(changed=False, message="")

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        if module.params.get("replace"):
            result["changed"] = True
        return result

    parameter_handlers = OrderedDict()
    parameter_handlers["type"] = data_set_type
    parameter_handlers["data_class"] = data_class
    parameter_handlers["format"] = data_set_format
    parameter_handlers["name"] = data_set_name
    parameter_handlers["size"] = data_set_size
    # parameter_handlers['key_offset'] = key_offset
    parameter_handlers["record_length"] = record_length
    parameter_handlers["volume"] = volume

    try:
        data_set_param_list = get_individual_data_set_parameters(module.params)

        for data_set_params in data_set_param_list:
            parameters = process_special_parameters(data_set_params, parameter_handlers)
            data_set_handler = DataSetHandler(module)
            result["changed"] = data_set_handler.perform_data_set_operations(
                **parameters
            ) or result.get("changed", False)
    except Error as e:
        module.fail_json(msg=repr(e), **result)
    except Exception as e:
        module.fail_json(msg=repr(e), **result)

    module.exit_json(**result)


class Error(Exception):
    def __init__(self, *args):
        super(Error, self).__init__(*args)


class DatasetDeleteError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during deletion of data set "{0}". RC={1}'.format(
            data_set, rc
        )
        super(DatasetDeleteError, self).__init__(self.msg)


class DatasetCreateError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during creation of data set "{0}". RC={1}'.format(
            data_set, rc
        )
        super(DatasetCreateError, self).__init__(self.msg)


class DatasetMemberDeleteError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during deletion of data set member"{0}". RC={1}'.format(
            data_set, rc
        )
        super(DatasetMemberDeleteError, self).__init__(self.msg)


class DatasetMemberCreateError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during creation of data set member"{0}". RC={1}'.format(
            data_set, rc
        )
        super(DatasetMemberCreateError, self).__init__(self.msg)


class DatasetNotFoundError(Error):
    def __init__(self, data_set):
        self.msg = 'The data set "{0}" could not be located.'.format(data_set)
        super(DatasetNotFoundError, self).__init__(self.msg)


class DatasetCatalogError(Error):
    def __init__(self, data_set, volume, rc, message=""):
        self.msg = 'An error occurred during cataloging of data set "{0}" on volume "{1}". RC={2}. {3}'.format(
            data_set, volume, rc, message
        )
        super(DatasetCatalogError, self).__init__(self.msg)


class DatasetUncatalogError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during uncatalog of data set "{0}". RC={1}'.format(
            data_set, rc
        )
        super(DatasetUncatalogError, self).__init__(self.msg)


class DatasetWriteError(Error):
    def __init__(self, data_set, rc, message=""):
        self.msg = 'An error occurred during write of data set "{0}". RC={1}. {2}'.format(
            data_set, rc, message
        )
        super(DatasetWriteError, self).__init__(self.msg)


def main():
    run_module()


if __name__ == "__main__":
    main()
