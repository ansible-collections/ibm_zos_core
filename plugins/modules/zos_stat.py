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
---
module: zos_stat
version_added: '1.14.0'
author:
  - "Ivan Moreno (@rexemin)"
short_description: Retrieve facts from MVS data sets, USS files and aggregates
description:
  - The L(zos_stat,./zos_stat.html) module retrieves facts from resources
    stored in a z/OS system.
  - Resources that can be queried are files, data sets and aggregates.
options:
  name:
    description:
        - Name of a data set, aggregate, or a file path, to query.
        - Data sets can be sequential, partitioned (PDS), partitioned
          extended (PDSE), VSAMs, generation data groups (GDG) or
          generation data sets (GDS).
    type: str
    required: true
    aliases:
      - src
  volume:
    description:
        - Name of the volume where the data set will be searched on.
        - Required when getting facts from a data set. Ignored otherwise.
    type: str
    required: false
  type:
    description:
        - Type of resource to query.
    type: str
    required: false
    default: data_set
    choices:
      - data_set
      - file
      - aggregate
  sms_managed:
    description:
        - Whether the data set is managed by the Storage Management Subsystem.
        - It will cause the module to retrieve additional information, may
          take longer to query all attributes of a data set.
        - If the data set is a PDSE and the Ansible user has RACF READ authority
          on it, retrieving SMS information will update the last referenced
          date of the data set.
        - If the system finds the data set is not actually managed by SMS, the
          rest of the attributes will still be queried and this will be noted
          in the output from the task.
    type: bool
    required: false
    default: true
  tmp_hlq:
    description:
      - Override the default high level qualifier (HLQ) for temporary data
        sets.
      - The default HLQ is the Ansible user used to execute the module and
        if that is not available, then the environment variable value
        C(TMPHLQ) is used.
    type: str
    required: false
  follow:
    description:
      - Whether to follow symlinks when querying files.
    type: bool
    required: false
    default: false
  get_mime:
    description:
      - Whether to get information about the nature of a file, such as the charset
        and type of media it represents.
    type: bool
    required: false
    default: true
  get_checksum:
    description:
      - Whether to compute a file's checksum and return it. Otherwise ignored.
    type: bool
    required: false
    default: true
  checksum_algorithm:
    description:
      - Algorithm used to compute a file's checksum.
      - Will throw an error if the managed node is unable to use the
        specified algorithm.
    type: str
    required: false
    default: "sha1"
    choices:
      - "md5"
      - "sha1"
      - "sha224"
      - "sha256"
      - "sha384"
      - "sha512"

notes:
  - When querying data sets, the module will create a temporary data set
    that requires around 4 kilobytes of available space on the managed node.
    This data set will be removed before the module finishes execution.
  - Sometimes, the system could be unable to properly determine the
    organization or record format of the data set or the space units used
    to represent its allocation. When this happens, the values for these
    fields will be null.
  - When querying a partitioned data set (PDS), if the Ansible user has
    RACF READ authority on it, the last referenced date will be updated by
    the query operation.

seealso:
  - module: ansible.builtin.stat
  - module: zos_find
  - module: zos_gather_facts
"""

EXAMPLES = r"""
- name: Get the attributes of a sequential data set on volume '000000'.
  zos_stat:
    name: USER.SEQ.DATA
    type: data_set
    volume: "000000"

- name: Get the attributes of a PDSE managed by SMS.
  zos_stat:
    name: USER.PDSE.DATA
    type: data_set
    volume: "000000"
    sms_managed: true

- name: Get the attributes of a sequential data set with a non-default temporary HLQ.
  zos_stat:
    name: USER.SEQ.DATA
    type: data_set
    volume: "000000"
    tmp_hlq: "RESTRICT"

- name: Get the attributes of a generation data group.
  zos_stat:
    name: "USER.GDG.DATA"
    type: data_set
    volume: "000000"

- name: Get the attributes of a generation data set.
  zos_stat:
    name: "USER.GDG.DATA(-1)"
    type: data_set
    volume: "000000"

- name: Get the attributes of an aggregate.
  zos_stat:
    name: "HLQ.USER.ZFS.DATA"
    type: aggregate

- name: Get the attributes of a file inside Unix System Services.
  zos_stat:
    name: "/u/user/file.txt"
    type: file
"""

RETURN = r"""
stat:
  description:
    - Dictionary containing information about the resource.
    - Attributes that don't apply to the current resource will still be
      present on the dictionary with null values, so as to not break
      automation that relies on certain fields to be available.
  returned: success
  type: dict
  contains:
    name:
      description:
        - Name of the resource queried.
        - For Generation Data Sets (GDSs), this will be the absolute name.
      returned: success
      type: str
      sample: USER.SEQ.DATA.SET
    resource_type:
      description: One of 'data_set', 'file' or 'aggregate'.
      returned: success
      type: str
      sample: data_set
    attributes:
      description: Dictionary containing all the stat data.
      returned: success
      type: dict
      contains:
        dsorg:
          description: Data set organization.
          returned: success
          type: str
          sample: ps
        type:
          description: Type of the data set.
          returned: success
          type: str
          sample: library
        record_format:
          description: Record format of a data set.
          returned: success
          type: str
          sample: vb
        record_length:
          description: Record length of a data set.
          returned: success
          type: int
          sample: 80
        block_size:
          description: Block size of a data set.
          returned: success
          type: int
          sample: 27920
        has_extended_attrs:
          description: Whether a data set has extended attributes set.
          returned: success
          type: bool
          sample: true
        extended_attrs_bits:
          description: 
            - Current values of the EATTR bits for a data set.
            - For files, it shows the current values of the extended
              attributes bits as a group of 4 characters.
          returned: success
          type: str
          sample: opt
        creation_date:
          description: Date a data set was created.
          returned: success
          type: str
          sample: "2025-01-27"
        creation_time:
          description:
            - Time at which a data set was created.
            - Only available when a data set has extended attributes.
          returned: success
          type: str
          sample: "11:25:52"
        expiration_date:
          description: Expiration date of a data set.
          returned: success
          type: str
          sample: "2030-12-31"
        last_reference:
          description: Date where the data set was last referenced.
          returned: success
          type: str
          sample: "2025-01-28"
        updated_since_backup:
          description: Whether the data set has been updated since its last backup.
          returned: success
          type: bool
          sample: false
        jcl_attrs:
          description:
            - Dictionary containing the names of the JCL job and step that
              created a data set.
            - Only available for data sets with extended attributes.
          returned: success
          type: dict
          contains:
            creation_job:
              description: JCL job that created the data set.
              returned: success
              type: str
              sample: DSALLOC
            creation_step:
              description: JCL job step that created the data set.
              returned: success
              type: str
              sample: ALLOC
        volser:
          description: Name of the volume containing the data set.
          returned: success
          type: str
          sample: "000000"
        num_volumes:
          description: Number of volumes where the data set resides.
          returned: success
          type: int
          sample: 1
        volumes:
          description: Names of the volumes where the data set resides.
          returned: success
          type: list
          elements: str
          sample: ["000000", "SCR03"]
        device_type:
          description: Generic device type where the data set resides.
          returned: success
          type: str
          sample: "3390"
        space_units:
          description: Units used to describe sizes for the data set.
          returned: success
          type: str
          sample: track
        primary_space:
          description:
            - Primary allocation.
            - Uses the space units defined in space_units.
          returned: success
          type: int
          sample: 93
        secondary_space:
          description:
            - Secondary allocation.
            - Uses the space units defined in space_units.
          returned: success
          type: int
          sample: 56
        allocation_available:
          description:
            - Total allocation of the data set.
            - Uses the space units defined in space_units.
          returned: success
          type: int
          sample: 93
        allocation_used:
          description:
            - Total allocation used by the data set.
            - Uses the space units defined in space_units.
          returned: success
          type: int
          sample: 0
        extents_allocated:
          description: Number of extents allocated for the data set.
          returned: success
          type: int
          sample: 1
        extents_used:
          description:
            - Number of extents used by the data set.
            - For PDSEs, this value will be null. See instead pages_used and
              perc_pages_used.
          returned: success
          type: int
          sample: 1
        blocks_per_track:
          description: Blocks per track for the unit contained in space_units.
          returned: success
          type: int
          sample: 2
        tracks_per_cylinder:
          description: Tracks per cylinder for the unit contained in space_units.
          returned: success
          type: int
          sample: 15
        sms_data_class:
          description:
            - The SMS data class name.
            - Only returned when the data set is managed by SMS and sms_managed
              is set to true.
          returned: success
          type: str
          sample: standard
        sms_mgmt_class:
          description:
            - The SMS management class name.
            - Only returned when the data set is managed by SMS and sms_managed
              is set to true.
          returned: success
          type: str
          sample: vsam
        sms_storage_class:
          description:
            - The SMS storage class name.
            - Only returned when the data set is managed by SMS and sms_managed
              is set to true.
          returned: success
          type: str
          sample: fast
        encrypted:
          description: Whether the data set is encrypted.
          returned: success
          type: bool
          sample: false
        password:
          description:
            - Whether the data set has a password set to read/write.
            - Value can be either one of 'none', 'read' or 'write'.
            - For VSAMs, the value can also be 'supp', when the module
              is unable to query its security attributes.
          returned: success
          type: str
          sample: none
        racf:
          description:
            - Whether there is RACF protection set on the data set.
            - Value can be either one of 'none', 'generic' or 'discrete'
              for non-VSAM data sets.
            - For VSAMs, the value can be either 'yes' or 'no'.
          returned: success
          type: str
          sample: none
        key_label:
          description: The encryption key label for an encrypted data set.
          returned: success
          type: str
          sample: keydsn
        dir_blocks_allocated:
          description:
            - Number of directory blocks allocated for a PDS.
            - For PDSEs, this value will be null. See instead pages_used
              and perc_pages_used.
          returned: success
          type: int
          sample: 5
        dir_blocks_used:
          description:
            - Number of directory blocks used by a PDS.
            - For PDSEs, this value will be null. See instead pages_used
              and perc_pages_used.
          returned: success
          type: int
          sample: 2
        members:
          description: Number of members inside a partitioned data set.
          returned: success
          type: int
          sample: 3
        pages_allocated:
          description: Number of pages allocated to a PDSE.
          returned: success
          type: int
          sample: 1116
        pages_used:
          description:
            - Number of pages used by a PDSE. The pages are 4K in size.
          returned: success
          type: int
          sample: 5
        perc_pages_used:
          description:
            - Percentage of pages used by a PDSE.
            - Gets rounded down to the nearest integer value.
          returned: success
          type: int
          sample: 10
        pdse_version:
          description: PDSE data set version.
          returned: success
          type: int
          sample: 1
        max_pdse_generation:
          description:
            - Maximum number of generations of a member that can be
              maintained in a PDSE.
          returned: success
          type: int
          sample: 0
        seq_type:
          description:
            - Type of sequential data set (when it applies).
            - Value can be either one of 'basic', 'large' or 'extended'.
          returned: success
          type: str
          sample: basic
        data:
          description:
            - Dictionary containing attributes for the DATA component of a VSAM. 
            - For the rest of the attributes of this data set, query it
              directly with this module.
          returned: success
          type: dict
          contains:
            key_length:
              description: Key length for data records, in bytes.
              returned: success
              type: int
              sample: 4
            key_offset:
              description: Key offset for data records.
              returned: success
              type: int
              sample: 3
            max_record_length:
              description: Maximum length of data records, in bytes.
              returned: success
              type: int
              sample: 80
            avg_record_length:
              description: Average length of data records, in bytes.
              returned: success
              type: int
              sample: 80
            bufspace:
              description:
                - Minimum buffer space in bytes to be provided by a
                  processing program.
              returned: success
              type: int
              sample: 37376
            total_records:
              description: Total number of records.
              returned: success
              type: int
              sample: 50
            spanned:
              description:
                - Whether the data set allows records to be spanned
                  across control intervals.
              returned: success
              type: bool
              sample: false
        index:
          description:
            - Dictionary containing attributes for the INDEX component of a VSAM. 
            - For the rest of the attributes of this data set, query it
              directly with this module.
          returned: success
          type: dict
          contains:
            key_length:
              description: Key length for index records, in bytes.
              returned: success
              type: int
              sample: 4
            key_offset:
              description: Key offset for index records.
              returned: success
              type: int
              sample: 3
            max_record_length:
              description: Maximum length of index records, in bytes.
              returned: success
              type: int
              sample: 0
            avg_record_length:
              description: Average length of index records, in bytes.
              returned: success
              type: int
              sample: 505
            bufspace:
              description:
                - Minimum buffer space in bytes to be provided by a
                  processing program.
              returned: success
              type: int
              sample: 0
            total_records:
              description: Total number of records.
              returned: success
              type: int
              sample: 0
        limit:
          description: Maximum amount of active generations allowed in a GDG.
          returned: success
          type: int
          sample: 10
        scratch:
          description: Whether the GDG has the SCRATCH attribute set.
          returned: success
          type: bool
          sample: false
        empty:
          description: Whether the GDG has the EMPTY attribute set.
          returned: success
          type: bool
          sample: false
        order:
          description:
            - Allocation order of new Generation Data Sets for a GDG.
            - Value can be either 'lifo' or 'fifo'.
          returned: success
          type: str
          sample: lifo
        purge:
          description: Whether the GDG has the PURGE attribute set.
          returned: success
          type: bool
          sample: false
        extended:
          description: Whether the GDG has the EXTENDED attribute set.
          returned: success
          type: bool
          sample: false
        active_gens:
          description: List of the names of the currently active generations of a GDG.
          returned: success
          type: list
          elements: str
          sample: ["USER.GDG.G0001V00", "USER.GDG.G0002V00"]
        auditfid:
          description: File system identification string for an aggregate.
          returned: success
          type: str
          sample: "C3C6C3F0 F0F3000E 0000"
        bitmap_file_size:
          description: Size in K of an aggregate's bitmap file.
          returned: success
          type: int
          sample: 8
        converttov5:
          description: Value of the converttov5 flag of an aggregate.
          returned: success
          type: bool
          sample: false
        filesystem_table_size:
          description: Size in K of an aggregate's filesystem table.
          returned: success
          type: int
          sample: 16
        free:
          description: Kilobytes still free in an aggregate.
          returned: success
          type: int
          sample: 559
        free_1k_fragments:
          description: Number of free 1-KB fragments in an aggregate.
          returned: success
          type: int
          sample: 7
        free_8k_blocks:
          description: Number of free 8-KB blocks in an aggregate.
          returned: success
          type: int
          sample: 69
        log_file_size:
          description: Size in K of an aggregate's log file.
          returned: success
          type: int
          sample: 112
        sysplex_aware:
          description: Value of the sysplex_aware flag of an aggregate.
          returned: success
          type: bool
          sample: true
        total_size:
          description: Total K available in an aggregate.
          returned: success
          type: int
          sample: 648000
        version:
          description: Version of an aggregate.
          returned: success
          type: str
          sample: "1.5"
        quiesced:
          description: Attributes available when an aggregate has been quiesced.
          returned: success
          type: dict
          contains:
            job:
              description: Name of the job that quiesced the aggregate.
              returned: success
              type: str
              sample: USERJOB
            system:
              description: Name of the system that quiesced the aggregate.
              returned: success
              type: str
              sample: GENSYS
            timestamp:
              description: Timestamp of the quiesce operation.
              returned: success
              type: str
              sample: "2025-02-01T18:02:05"
        mode:
          description: Octal representation of a file's permissions.
          returned: success
          type: str
          sample: "0755"
        atime:
          description: Time of last access for a file.
          returned: success
          type: str
          sample: "2025-02-23T13:03:45"
        mtime:
          description: Time of last modification of a file.
          returned: success
          type: str
          sample: "2025-02-23T13:03:45"
        ctime:
          description: Time of last metadata update or creation for a file.
          returned: success
          type: str
          sample: "2025-02-23T13:03:45"
        uid:
          description: ID of the file's owner.
          returned: success
          type: int
          sample: 0
        gid:
          description: ID of the file's group.
          returned: success
          type: int
          sample: 1
        size:
          description: Size of the file in bytes.
          returned: success
          type: int
          sample: 9840
        inode:
          description: Inode number of the path.
          returned: success
          type: int
          sample: 1671
        dev:
          description: Device the inode resides on.
          returned: success
          type: int
          sample: 1
        nlink:
          description: Number of links to the inode.
          returned: success
          type: int
          sample: 1
        isdir:
          description: Whether the path is a directory.
          returned: success
          type: bool
          sample: false
        ischr:
          description: Whether the path is a character device.
          returned: success
          type: bool
          sample: false
        isblk:
          description: Whether the path is a block device.
          returned: success
          type: bool
          sample: false
        isreg:
          description: Whether the path is a regular file.
          returned: success
          type: bool
          sample: true
        isfifo:
          description: Whether the path is a named pipe.
          returned: success
          type: bool
          sample: false
        islnk:
          description: Whether the file is a symbolic link.
          returned: success
          type: bool
          sample: false
        issock:
          description: Whether the file is a Unix domain socket.
          returned: success
          type: bool
          sample: false
        isuid:
          description: Whether the Ansible user's ID matches the owner's ID.
          returned: success
          type: bool
          sample: false
        isgid:
          description: Whether the Ansible user's group matches the owner's group.
          returned: success
          type: bool
          sample: false
        wusr:
          description: Whether the file's owner has write permission.
          returned: success
          type: bool
          sample: true
        rusr:
          description: Whether the file's owner has read permission.
          returned: success
          type: bool
          sample: true
        xusr:
          description: Whether the file's owner has execute permission.
          returned: success
          type: bool
          sample: true
        wgrp:
          description: Whether the file's group has write permission.
          returned: success
          type: bool
          sample: false
        rgrp:
          description: Whether the file's group has read permission.
          returned: success
          type: bool
          sample: true
        xgrp:
          description: Whether the file's group has execute permission.
          returned: success
          type: bool
          sample: true
        woth:
          description: Whether others have write permission over the file.
          returned: success
          type: bool
          sample: false
        roth:
          description: Whether others have read permission over the file.
          returned: success
          type: bool
          sample: true
        xoth:
          description: Whether others have execute permission over the file.
          returned: success
          type: bool
          sample: false
        writeable:
          description: Whether the Ansible user can write to the path.
          returned: success
          type: bool
          sample: true
        readable:
          description: Whether the Ansible user can read the path.
          returned: success
          type: bool
          sample: true
        executable:
          description: Whether the Ansible user can execute the path.
          returned: success
          type: bool
          sample: true
        pw_name:
          description: User name of the file's owner.
          returned: success
          type: str
          sample: username
        gr_name:
          description: Group name of the file's owner.
          returned: success
          type: str
          sample: group
        lnk_source:
          description: Absolute path to the target of a symlink.
          returned: success
          type: str
          sample: "/etc/foobar/file"
        lnk_target:
          description:
            - Target of a symlink.
            - Preserves relative paths.
          returned: success
          type: str
          sample: "../foobar/file"
        charset:
          description:
            - Current encoding tag associated with the file.
            - This tag does not necessarily correspond with the actual
              encoding of the file.
          returned: success
          type: str
          sample: "IBM-1047"
        mimetype:
          description:
            - Output from the file utility describing the content.
          returned: success
          type: str
          sample: "commands text"
        audit_bits:
          description:
            - Audit bits for the file. Contains two sets of 3 bits.
            - First 3 bits describe the user-requested audit information.
            - Last 3 bits describe the auditor-requested audit information.
            - For each set, the bits represent read, write and execute/search
              audit options.
            - An 's' means to audit successful access attempts.
            - An 'f' means to audit failed access attempts.
            - An 'a' means to audit all access attempts.
            - An '-' means to not audit accesses.
          returned: success
          type: str
          sample: "fff---"
        file_format:
          description:
            - File format (for regular files). One of "null", "bin" or "rec".
            - Text data delimiter for a file. One of "nl", "cr", "lf", "crlf", "lfcr" or "crnl".
          returned: success
          type: str
          sample: "bin"
"""

import abc
import json
import re
import os
import stat
import pwd
import grp
from datetime import datetime, timezone, timedelta
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    DataSet,
    MVSDataSet,
    GenerationDataGroup,
    DatasetCreateError,
    GDSNameResolveError
)

try:
    from zoautil_py import datasets, gdgs
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())
    gdgs = ZOAUImportError(traceback.format_exc())

try:
    from zoautil_py import exceptions as zoau_exceptions
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())


# TODO: add method/decorator that adds all missing attributes so we can keep the
# return interface consistent across resource types.
class FactsHandler():
    """Base class for every other handler that will query resources on
    a z/OS system.
    """

    def __init__(self, name, module=None):
        """Setting up the three common attributes for each handler (resource name,
        module and extra_data.

        Arguments:
            name (str) -- Resource name.
            module (AnsibleModule, optional) -- Ansible object with the task's context.
        """
        self.name = name
        self.module = module
        self.extra_data = ''

    @abc.abstractmethod
    def exists(self):
        pass

    @abc.abstractmethod
    def query(self):
        pass

    def get_extra_data(self):
        """Extra data will be treated as any information that should be returned
        to the user as part of the 'notes' section of the final JSON object.

        Returns:
            str -- Any extra data found while querying.
        """
        return self.extra_data


class AggregateHandler(FactsHandler):
    """Class in charge of dealing with queries of aggregates via zfsadm.
    """

    def __init__(self, name, module=None):
        """Creates a new handler.

        Arguments:
            name (str) -- Aggregate's name.
            module (AnsibleModule, optional) -- Ansible object with the task's context.
        """
        super(AggregateHandler, self).__init__(name, module)
        self.has_been_queried = False
        self.raw_attributes = None

    def exists(self):
        """Returns whether or not zfsadm found the aggregate.
        """
        if not self.has_been_queried:
            self._run_zfsadm()

        return self.raw_attributes is not None

    def query(self):
        """Calls zfsadm aggrinfo to get information about an aggregate.

        Returns
        -------
            dict -- Attributes from an aggregate.
        """
        if not self.has_been_queried:
            self._run_zfsadm()

        size_search = re.search('([0-9]+)( K free out of total )([0-9]+)', self.raw_attributes)
        version_search = re.search('(version )([0-9]+\.[0-9]+)', self.raw_attributes)
        auditfid_search = re.search('(auditfid )([0-9A-Z]{8} [0-9A-Z]{8} [0-9A-Z]{4})', self.raw_attributes)
        free_8k_blocks_search = re.search('([0-9]+)( free 8k blocks)', self.raw_attributes)
        free_fragments_search = re.search('([0-9]+)( free 1K fragments)', self.raw_attributes)
        log_file_search = re.search('([0-9]+)( K log file)', self.raw_attributes)
        filesystem_table_search = re.search('([0-9]+)( K filesystem table)', self.raw_attributes)
        bitmap_search = re.search('([0-9]+)( K bitmap file)', self.raw_attributes)
        quiesced_search = re.search('(Quiesced by job )([0-9a-zA-Z]+)( on system )([0-9a-zA-Z]+)( on )(.+)', self.raw_attributes)

        try:
            attributes = {
                'name': self.name,
                'resource_type': 'aggregate',
                'attributes': {
                    'total_size': int(size_search.group(3)),
                    'free': int(size_search.group(1)),
                    'version': version_search.group(2),
                    'auditfid': auditfid_search.group(2),
                    'free_8k_blocks': int(free_8k_blocks_search.group(1)),
                    'free_1k_fragments': int(free_fragments_search.group(1)),
                    'log_file_size': int(log_file_search.group(1)),
                    'filesystem_table_size': int(filesystem_table_search.group(1)),
                    'bitmap_file_size': int(bitmap_search.group(1)),
                    'sysplex_aware': True if 'sysplex_aware' in self.raw_attributes else False,
                    'converttov5': True if 'converttov5' in self.raw_attributes else False,
                    'quiesced': {
                        'job': None,
                        'system': None,
                        'timestamp': None
                    }
                }
            }

            if quiesced_search:
                attributes['attributes']['quiesced']['job'] = quiesced_search.group(2)
                attributes['attributes']['quiesced']['system'] = quiesced_search.group(4)

                quiesced_timestamp = datetime.strptime(
                    quiesced_search.group(6),
                    '%a %b %d %H:%M:%S %Y'
                ).strftime('%Y-%m-%dT%H:%M:%S')

                attributes['attributes']['quiesced']['timestamp'] = quiesced_timestamp
        except Exception as err:
            raise QueryException(f"An error ocurred while parsing an aggregate's information: {str(err)}.")

        return attributes

    def _run_zfsadm(self):
        """Runs zfsadm and stores the result in self.raw_attributes.
        """
        zfsadm_cmd = f'zfsadm aggrinfo -aggregate {self.name} -long'
        rc, stdout, stderr = self.module.run_command(zfsadm_cmd)
        self.has_been_queried = True

        if rc == 0:
            self.raw_attributes = stdout
        else:
            # We raise an exception when the error is something other than the aggregate
            # was not found.
            if rc > 0 and '624E' not in stderr:
                raise QueryException(
                    f"An error ocurred while querying information about {self.name}",
                    rc=rc,
                    stdout=stdout,
                    stderr=stderr
                )


class FileHandler(FactsHandler):
    """Class in charge of dealing with queries of files via os.stat and ls.
    """

    def __init__(self, name, module=None, file_args=None):
        """Creates a new handler.

        Arguments:
            name (str) -- File path.
            module (AnsibleModule, optional) -- Ansible object with the task's context.
            file_args (dict, optional) -- Dictionary containing whether to follow symlinks,
                get MIME information, and how to compute a file's checksum.
        """
        super(FileHandler, self).__init__(name, module)
        self.follow = file_args.get('follow', False)
        self.get_mime = file_args.get('get_mime', True)
        self.get_checksum = file_args.get('get_checksum', True)
        self.checksum_algorithm = file_args.get('checksum_algorithm', 'sha1')

        try:
            current_time = time.localtime()
            utc_offset = current_time.tm_gmtoff
            current_tz = current_time.tm_zone
            self.tz_info = timezone(timedelta(seconds=utc_offset), current_tz)
        except (OverflowError, OSError) as err:
            raise QueryException(f"An error ocurred while trying to get information about the system's time: {str(err)}.")

    def exists(self):
        """Returns whether or not the file path exists on the system.
        """
        return os.path.exists(self.name)

    def query(self):
        """Calls os.stat and ls to obtain the file path's attributes.

        Returns
        -------
            dict -- Attributes from a file path.
        """
        try:
            raw_attributes = os.stat(self.name, follow_symlinks=self.follow)
            mode = raw_attributes.st_mode

            attributes = {
                'name': self.name,
                'resource_type': 'file',
                'attributes': {
                    'mode': "%04o" % stat.S_IMODE(mode),
                    'atime': raw_attributes.st_atime,
                    'mtime': raw_attributes.st_mtime,
                    'ctime': raw_attributes.st_ctime,
                    'uid': raw_attributes.st_uid,
                    'gid': raw_attributes.st_gid,
                    'size': raw_attributes.st_size,
                    'inode': raw_attributes.st_ino,
                    'dev': raw_attributes.st_dev,
                    'nlink': raw_attributes.st_nlink,
                    'isdir': stat.S_ISDIR(mode),
                    'ischr': stat.S_ISCHR(mode),
                    'isblk': stat.S_ISBLK(mode),
                    'isreg': stat.S_ISREG(mode),
                    'isfifo': stat.S_ISFIFO(mode),
                    'islnk': stat.S_ISLNK(mode),
                    'issock': stat.S_ISSOCK(mode),
                    'isuid': bool(mode & stat.S_ISUID),
                    'isgid': bool(mode & stat.S_ISGID),
                    'wusr': bool(mode & stat.S_IWUSR),
                    'rusr': bool(mode & stat.S_IRUSR),
                    'xusr': bool(mode & stat.S_IXUSR),
                    'wgrp': bool(mode & stat.S_IWGRP),
                    'rgrp': bool(mode & stat.S_IRGRP),
                    'xgrp': bool(mode & stat.S_IXGRP),
                    'woth': bool(mode & stat.S_IWOTH),
                    'roth': bool(mode & stat.S_IROTH),
                    'xoth': bool(mode & stat.S_IXOTH)
                }
            }

            attributes['attributes']['writeable'] = os.access(self.name, os.W_OK)
            attributes['attributes']['readable'] = os.access(self.name, os.R_OK)
            attributes['attributes']['executable'] = os.access(self.name, os.X_OK)

            try:
                attributes['attributes']['pw_name'] = pwd.getpwuid(raw_attributes.st_uid).pw_name
                attributes['attributes']['gr_name'] = grp.getgrgid(raw_attributes.st_gid).gr_name
            except (TypeError, KeyError, ValueError, OverflowError):
                attributes['attributes']['pw_name'] = None
                attributes['attributes']['gr_name'] = None

            datetime_keys = ['atime', 'mtime', 'ctime']
            attributes['attributes'] = self._parse_datetimes(attributes['attributes'], datetime_keys)

            if attributes['attributes']['islnk']:
                attributes['attributes']['lnk_source'] = os.path.realpath(self.name)
                attributes['attributes']['lnk_target'] = os.readlink(self.name)
            else:
                attributes['attributes']['lnk_source'] = None
                attributes['attributes']['lnk_target'] = None

            self._run_ls()
            attributes['attributes']['charset'] = self.z_attributes[1]
            attributes['attributes']['audit_bits'] = self.z_attributes[4]
            attributes['attributes']['extended_attrs_bits'] = self.z_attributes[5]

            if self.z_attributes[6] != '----':
                attributes['attributes']['file_format'] = self.z_attributes[6]
            else:
                attributes['attributes']['file_format'] = None

            if self.get_checksum:
                attributes['attributes']['checksum'] = self.module.digest_from_file(
                    self.name,
                    self.checksum_algorithm
                )

            if self.get_mime:
                attributes['attributes']['mimetype'] = self._run_file()
        except Exception as err:
            raise QueryException(f"An error ocurred while querying a file path's information: {str(err)}.")

        return attributes

    def _run_ls(self):
        """Runs ls and stores the result in self.z_attributes.
        """
        # Turning on 'long' mode (l) and setting unprintable chars to ? (q).
        # Asking for extended attributes (E), file format (H),
        # to follow links (L), tag information (T) and audit bits (W).
        ls_cmd = f'ls -lqEHLTW {self.name}'
        rc, stdout, stderr = self.module.run_command(ls_cmd)

        if rc == 0:
            self.z_attributes = stdout.split()
        else:
            raise QueryException(
                f"An error ocurred while querying information about {self.name}",
                rc=rc,
                stdout=stdout,
                stderr=stderr
            )

    def _run_file(self):
        """Runs file and returns the result.
        """
        file_cmd = f'file {self.name}'
        rc, stdout, stderr = self.module.run_command(file_cmd)

        if rc == 0:
            # file's output comes in three parts:
            # file_path: filetype - description of the filetype.
            # So we extract the middle part for the module.
            file_type_complete = stdout.split(':')[1]
            file_type_simplified = file_type_complete.split('-')[0]

            return file_type_simplified.strip()
        else:
            return None

    def _parse_datetimes(self, attrs, keys):
        """Converts timestamps to date times (YYYY-MM-DDTHH:MM:SS).
        
        Arguments:
            attrs (dict) -- Raw dictionary gotten from a stat call.
            keys (list) -- List of keys from attrs to convert.
        """
        for key in keys:
            try:
                if key in attrs:
                    attrs[key] = datetime.fromtimestamp(attrs[key], tz=self.tz_info).strftime('%Y-%m-%dT%H:%M:%S')
            except (OverflowError, ValueError):
                pass

        return attrs


class DataSetHandler(FactsHandler):
    """Base class that can query facts from a sequential, partitioned (PDS), partitioned
    extended (PDSE), VSAM or generation data sets. It provides generic utility methods
    for parsing values.
    """

    # Attributes all data set types share.
    bool_attrs = ['has_extended_attrs', 'updated_since_backup', 'encrypted']
    datetime_attrs = ['creation_date', 'expiration_date', 'last_reference']
    # This list should be overwritten by a subclass.
    num_attrs = []

    # TODO: handle multivol
    def __init__(
        self, 
        name,
        volume=None,
        module=None,
        tmp_hlq=None,
        sms_managed=False,
        exists=False,
        ds_type=None
    ):
        """Create a new handler that will handle the query of an MVS data set.
        Creating this object directly should only be used when wanting to represent
        a non-existent data set. All subclasses should be preferred in every
        other case.

        Arguments:
            name (str) -- Name of the data set.
            volume (str, optional) -- Volume where the data set is allocated.
            module (AnsibleModule, optional) -- Ansible object with the task's context.
            tmp_hlq (str, optional) -- Temporary HLQ to be used in some operations.
            sms_managed (bool, optional) -- Whether the data set is managed by SMS.
            exists (bool, optional) -- Whether the data set is present on the given volume.
            ds_type (str, optional) -- Type of the data set.
        """
        super(DataSetHandler, self).__init__(name, module)
        self.volume = volume
        self.tmp_hlq = tmp_hlq if tmp_hlq else datasets.get_hlq()
        self.sms_managed = sms_managed
        self.data_set_exists = exists
        self.data_set_type = ds_type


    def exists(self):
        """Returns whether the given data set was found on the system.
        """
        return self.data_set_exists

    def query(self):
        """Return a minimal attributes dictionary.

        Returns:
            dict -- Skeleton of the attributes dictionary for a data set.
        """
        data = {
            'resource_type': 'data_set',
            'name': self.name
        }
        return data

    def _parse_attributes(self, attrs):
        """Since all attributes returned by running commands return strings,
        this method ensures numerical and boolean values are returned as such.
        It also makes sure datetimes are better formatted and replaces '?', 'N/A',
        'NO_LIM', with more user-friendly values.

        Arguments:
            attrs (dict) -- Raw dictionary processed from a command call.

        Returns:
            dict -- Attributes dictionary with parsed values.
        """
        attrs = {
            key: attrs[key] if self._is_value_valid(attrs[key]) else None
            for key in attrs
        }

        # Numerical values.
        attrs = self._parse_values(attrs, self.num_attrs, int)

        # Boolean values.
        attrs = self._replace_values(attrs, self.bool_attrs, True, False, 'YES')

        # Datetime values.
        attrs = self._parse_datetimes(attrs, self.datetime_attrs)

        # Switching strings to lowercase.
        for key in attrs.keys():
            if isinstance(attrs[key], str):
                attrs[key] = attrs[key].lower()

        return attrs

    def _is_value_valid(self, value):
        """Returns whether the value should be replaced for None.

        Arguments:
            value (str) -- Raw value of an attribute for a data set.

        Returns:
            bool -- Whether the value should stay as is or be replace with None.
        """
        # Getting rid of values that basically say the value doesn't matter in
        # context or is unknown. Every value that is not a string we'll assume is
        # valid.
        if not isinstance(value, str):
            return True
        return value is not None and value != '' and '?' not in value and value != 'N/A' and value != 'NO_LIM'

    def _parse_values(self, attrs, keys, true_function):
        """Tries to parse attributes with a given function.

        Arguments:
            attrs (dict) -- Raw dictionary processed from a LISTDSI script.
            keys (list) -- List of keys from attrs to parse.
            true_function (function) -- Parsing function to use (like 'int').

        Returns:
            dict -- Updated attributes with parsed values.
        """
        for key in keys:
            try:
                if key in attrs:
                    attrs[key] = true_function(attrs[key]) if attrs[key] else None
            # If we fail to parse something, we just leave it be to avoid
            # losing information.
            except ValueError:
                pass

        return attrs

    def _replace_values(self, attrs, keys, true_value, false_value, condition):
        """Replace strings for the given values depending on the result of a
        condition.

        Arguments:
            attrs (dict) -- Raw dictionary processed from a LISTDSI script.
            keys (list) -- List of keys from attrs to test and replace.
            true_value (any) -- Value to use when condition is true (like True).
            false_value (any) -- Value to use when condition is false (like False).
            condition (any) -- Value to compare each attribute against.

        Returns:
            dict -- Updated attributes with replaced values.
        """
        for key in keys:
            if key in attrs:
                attrs[key] = true_value if attrs[key] == condition else false_value

        return attrs

    def _parse_datetimes(self, attrs, keys):
        """Converts ordinal dates (YYYY/DDD) to more common ones (YYYY-MM-DD).
        
        Arguments:
            attrs (dict) -- Raw dictionary processed from a LISTDSI script.
            keys (list) -- List of keys from attrs to convert.
        """
        for key in keys:
            try:
                if key in attrs:
                    attrs[key] = attrs[key].replace('.', '/')
                    attrs[key] = datetime.strptime(attrs[key], '%Y/%j').strftime('%Y-%m-%d')
            except ValueError:
                # z/OS returns 0 or 0000/000 when a date is not set, so we set it to None.
                if attrs[key] == "0" or "0000/000" in attrs[key]:
                    attrs[key] = None

        return attrs


class NonVSAMDataSetHandler(DataSetHandler):
    """Class that can query sequential or partitioned data sets using LISTDSI.
    """

    num_attrs = [
        'record_length',
        'block_size',
        'num_volumes',
        'primary_space',
        'secondary_space',
        'allocation_available',
        'allocation_used',
        'extents_allocated',
        'extents_used',
        'blocks_per_track',
        'tracks_per_cylinder',
        'dir_blocks_allocated',
        'dir_blocks_used',
        'members',
        'pages_allocated',
        'pages_used',
        'perc_pages_used',
        'pdse_version',
        'max_pdse_generation'
    ]

    LISTDSI_SCRIPT = """/* REXX */
/***********************************************************
* © Copyright IBM Corporation 2025
***********************************************************/
arg data_set_name volume extra_args
listdsi_args = "'" || data_set_name || "'"
listdsi_args = listdsi_args "VOLUME(" || volume || ")"
listdsi_args = listdsi_args extra_args
data_set_info = LISTDSI(LISTDSI_ARGS)

if SYSREASON > 0 then
  do
    say SYSREASON SYSMSGLVL1 SYSMSGLVL2
    return 1
  end

if data_set_info == 0 then
  do
    say '{'
    /* General information */
    say '"dsorg":"' || SYSDSORG || '",'
    say '"type":"' || SYSDSSMS || '",'
    say '"record_format":"' || SYSRECFM || '",'
    say '"record_length":"' || SYSLRECL || '",'
    say '"block_size":"' || SYSBLKSIZE || '",'
    say '"has_extended_attrs":"' || SYSEADSCB || '",'
    say '"extended_attrs_bits":"' || SYSEATTR || '",'
    say '"creation_date":"' || SYSCREATE || '",'
    say '"creation_time":"' || SYSCREATETIME || '",'
    say '"expiration_date":"' || SYSEXDATE || '",'
    say '"last_reference":"' || SYSREFDATE || '",'
    say '"updated_since_backup":"' || SYSUPDATED || '",'
    say '"jcl_attrs":{'
    say '"creation_step":"' || SYSCREATESTEP || '",'
    say '"creation_job":"' || SYSCREATEJOB || '"'
    say '},'
    /* Allocation information */
    say '"volser":"' || SYSVOLUME || '",'
    say '"num_volumes":"' || SYSNUMVOLS || '",'
    say '"volumes":"' || SYSVOLUMES || '",'
    say '"device_type":"' || SYSUNIT || '",'
    say '"space_units":"' || SYSUNITS || '",'
    say '"primary_space":"' || SYSPRIMARY || '",'
    say '"secondary_space":"' || SYSSECONDS || '",'
    say '"allocation_available":"' || SYSALLOC || '",'
    say '"allocation_used":"' || SYSUSED || '",'
    say '"extents_allocated":"' || SYSEXTENTS || '",'
    say '"extents_used":"' || SYSUSEDEXTENTS || '",'
    say '"blocks_per_track":"' || SYSBLKSTRK || '",'
    say '"tracks_per_cylinder":"' || SYSTRKSCYL || '",'
    say '"sms_mgmt_class":"' || SYSMGMTCLASS || '",'
    say '"sms_storage_class":"' || SYSSTORCLASS || '",'
    say '"sms_data_class":"' || SYSDATACLASS || '",'
    /* Security information */
    say '"encrypted":"' || SYSENCRYPT || '",'
    say '"password":"' || SYSPASSWORD || '",'
    say '"racf":"' || SYSRACFA || '",'
    say '"key_label":"' || SYSKEYLABEL || '",'
    /* PDS/E attributes */
    say '"dir_blocks_allocated":"' || SYSADIRBLK || '",'
    say '"dir_blocks_used":"' || SYSUDIRBLK || '",'
    say '"members":"' || SYSMEMBERS || '",'
    say '"pages_allocated":"' || SYSALLOCPAGES || '",'
    say '"pages_used":"' || SYSUSEDPAGES || '",'
    say '"perc_pages_used":"' || SYSUSEDPERCENT || '",'
    say '"pdse_version":"' || SYSDSVERSION || '",'
    say '"max_pdse_generation":"' || SYSMAXGENS || '",'
    /* Sequential attributes */
    say '"seq_type":"' || SYSSEQDSNTYPE || '"'
    say '}'
  end
else
  do
    say '{'
    say '"error":true'
    say '"msg":"Data set was not found"'
    say '}'
    return 1
  end

return 0"""

    def __init__(self, name, volume, module, sms_managed, ds_type, tmp_hlq=None):
        """Create a new handler that will handle the query of a sequential or
        partitioned data set. This subclass should only be instantiated by
        get_data_set_handler.

        Arguments:
            name (str) -- Name of the data set.
            volume (str) -- Volume where the data set is allocated.
            module (AnsibleModule) -- Ansible object with the task's context.
            sms_managed (bool) -- Whether the data set is managed by SMS.
            ds_type (str) -- Type of the data set.
            tmp_hlq (str, optional) -- Temporary HLQ to be used in some operations.
        """
        super(NonVSAMDataSetHandler, self).__init__(
            name,
            volume=volume,
            module=module,
            tmp_hlq=tmp_hlq,
            sms_managed=sms_managed,
            exists=True,
            ds_type=ds_type
        )

    def query(self):
        """Uses LISTDSI to query facts about a data set, while also handling
        specific arguments needed depending on data set type.

        Returns:
            dict -- Data set attributes.

        Raises:
            QueryException: When the script's data set's allocation fails.
            QueryException: When ZOAU fails to write the script to its data set.
        """
        data = super().query()
        attributes = {}

        try:
            # First creating a temp data set to hold the LISTDSI script.
            # All options are meant to allocate just enough space for it.
            temp_script_location = DataSet.create_temp(
                hlq=self.tmp_hlq,
                type='SEQ',
                record_format='FB',
                space_primary=4,
                space_secondary=0,
                space_type='K',
                record_length=60
            )

            datasets.write(temp_script_location, self.LISTDSI_SCRIPT)
            rc, stdout, stderr = self._run_listdsi_command(temp_script_location)

            attributes = json.loads(stdout)

        except DatasetCreateError as err:
            raise QueryException(err.msg)
        except zoau_exceptions.DatasetWriteException as err:
            raise QueryException(
                'An error ocurred while creating the temporary query script.',
                rc=err.rc,
                stdout=err.stdout_response,
                stderr=err.stderr_response
            )
        finally:
            datasets.delete(temp_script_location)

        data['attributes'] = self._parse_attributes(attributes)

        return data

    def _run_listdsi_command(self, temp_script_location):
        """Runs the LISTDSI script defined in this class and checks for errors
        when requesting SMS information that doesn't exist.

        Arguments:
            temp_script_location (str) -- Name of the script's temporary data set.

        Returns:
            tuple -- Tuple containing the RC, standard out and standard err of the
                     query script.

        Raises:
            QueryException: When the script fails for any reason other than requesting
                            SMS information from a data set not managed by SMS.
        """
        extra_args = ''
        # Asking for PDS/PDSE-specific attributes.
        if self.data_set_type in DataSet.MVS_PARTITIONED:
            extra_args = 'DIRECTORY'
        if self.sms_managed:
            extra_args = f'{extra_args} SMSINFO'

        tso_cmd = f"""tsocmd "EXEC '{temp_script_location}' '{self.name} {self.volume} {extra_args}' exec" """
        rc, stdout, stderr = self.module.run_command(tso_cmd)

        # Retrying the query without asking for SMS information.
        # This error code is specifically the code for when a data set is not
        # SMS-managed.
        if rc != 0 and 'IKJ58430I' in stdout:
            tso_cmd = tso_cmd.replace('SMSINFO', '')
            rc, stdout, stderr = self.module.run_command(tso_cmd)
            self.extra_data  = f'{self.extra_data}The data set is not managed by SMS.\n'

        if rc != 0:
            raise QueryException(
                f'An error ocurred while querying information for {self.name}.',
                rc=rc,
                stdout=stdout,
                stderr=stderr
            )

        return rc, stdout, stderr

    def _parse_attributes(self, attrs):
        """Calls the generic _parse_attributes method and then handles the JCL
        attributes nested dictionary.

        Arguments:
            attrs (dict) -- Raw dictionary processed from a LISTDSI call.

        Returns:
            dict -- Attributes dictionary with parsed values.
        """
        attrs = super()._parse_attributes(attrs)

        if 'jcl_attrs' in attrs and attrs['jcl_attrs']['creation_job'] == '':
            attrs['jcl_attrs']['creation_job'] = None
        if 'jcl_attrs' in attrs and attrs['jcl_attrs']['creation_step'] == '':
            attrs['jcl_attrs']['creation_step'] = None

        return attrs


class VSAMDataSetHandler(DataSetHandler):
    """Class that can query VSAM data sets using LISTCAT.
    """

    num_attrs = [
        'avg_record_length',
        'max_record_length',
        'bufspace',
        'key_length',
        'key_offset',
        'total_records'
    ]

    dev_type_translation_table = {
        '3010200E': '3380',
        '3010200F': '3390',
        '30102004': '9345',
        '30C08003': '3400-2',
        '32008003': '3400-5',
        '32108003': '3400-6',
        '33008003': '3400-9',
        '34008003': '3400-3',
        '78008080': '3480',
        '78048080': '3480X',
        '78048081': '3490',
        '78048083': '3590-1',
    }

    def __init__(self, name, volume, module, sms_managed, ds_type, tmp_hlq=None):
        """Create a new handler that will handle the query of a VSAM.
        This subclass should only be instantiated by get_data_set_handler.

        Arguments:
            name (str) -- Name of the data set.
            volume (str) -- Volume where the data set is allocated.
            module (AnsibleModule) -- Ansible object with the task's context.
            sms_managed (bool) -- Whether the data set is managed by SMS.
            ds_type (str) -- Type of the data set.
            tmp_hlq (str, optional) -- Temporary HLQ to be used in some operations.
        """
        super(VSAMDataSetHandler, self).__init__(
            name,
            volume=volume,
            module=module,
            tmp_hlq=tmp_hlq,
            sms_managed=sms_managed,
            exists=True,
            ds_type=ds_type
        )

    def query(self):
        """Uses LISTCAT to query facts about a VSAM."""
        data = super().query()

        listcat_cmd = f" LISTCAT ENTRIES('{self.name}') ALL"
        mvs_cmd = f'mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin -Q={self.tmp_hlq}'

        rc, stdout, stderr = self.module.run_command(mvs_cmd, data=listcat_cmd, errors='replace')

        if rc > 0:
            raise QueryException(
                'An error ocurred while querying a VSAM data set.',
                rc=rc,
                stdout=stdout,
                stderr=stderr
            )

        listcat_lines = stdout.split('\n')
        gen_info_limit = data_info_limit = 0

        for index in range(len(listcat_lines)):
            if gen_info_limit == 0:
                if 'DATA -' in listcat_lines[index]:
                    gen_info_limit = index
            else:
                if data_info_limit == 0 and 'INDEX -' in listcat_lines[index]:
                    data_info_limit = index
                    break

        vsam_general_info = ' '.join(listcat_lines[0:gen_info_limit])
        data_info = ' '.join(listcat_lines[gen_info_limit:data_info_limit])
        index_info = ' '.join(listcat_lines[data_info_limit:])
        attributes = {
            'volser': self.volume,
            'dsorg': 'VSAM',
            'type': self.data_set_type,
            'device_type': re.search("(DEVTYPE-+X')(\d{7}[0-9A-F])", data_info).group(2)
        }
        attributes['device_type'] = self.dev_type_translation_table[attributes['device_type']]

        general_info_regex_searches = [
            ('extended_attrs_bits', '(EATTR-+\(?)([0-9a-zA-Z]+)'),
            ('creation_date', '(CREATION-+)(\d{4}\.\d{3})'),
            ('expiration_date', '(EXPIRATION-+)(\d{4}\.\d{3})'),
            ('sms_mgmt_class', '(MANAGEMENTCLASS-+)([0-9a-zA-Z]+)'),
            ('sms_storage_class', '(STORAGECLASS-+)([0-9a-zA-Z]+)'),
            ('sms_data_class', '(DATACLASS-+)([0-9a-zA-Z]+)'),
            ('encrypted', '(DATA SET ENCRYPTION-+\()([a-zA-Z]{2,3})'),
            ('key_label', '(DATA SET KEY LABEL-+)([a-zA-Z]+)'),
            ('password', '(PROTECTION-PSWD-+\(?)([a-zA-Z]+)'),
            ('racf', '(RACF-+\()([a-zA-Z]{2,3})')
        ]

        attributes.update(self._find_attributes_from_liscat(vsam_general_info, general_info_regex_searches))
        if 'extended_attrs_bits' in attributes:
            attributes['has_extended_attrs'] = 'YES' if attributes['extended_attrs_bits'] != 'NULL' else 'NO'
            if attributes['extended_attrs_bits'] == 'NULL':
                attributes['extended_attrs_bits'] = None

        if attributes['password'] == 'NULL':
            attributes['password'] = 'none'
        elif attributes['password'] == 'SUPP':
            self.extra_data = f'{self.extra_data}\nUnable to get security attributes.'


        if 'ASSOCIATIONS' in vsam_general_info:
            attributes['data'] = {
                'name': re.search('(DATA-+)([0-9a-zA-Z\.@\$#-]+)', vsam_general_info).group(2),
                'spanned': True if re.search('\bSPANNED\b', data_info) else False
            }
            attributes['index'] = {
                'name': re.search('(INDEX-+)([0-9a-zA-Z\.@\$#-]+)', vsam_general_info).group(2)
            }

            assoc_regex_searches = [
                ('key_length', '(KEYLEN-+)(\d+)'),
                ('key_offset', '(RKP-+)(\d+)'),
                ('max_record_length', '(AVGLRECL-+)(\d+)'),
                ('avg_record_length', '(MAXLRECL-+)(\d+)'),
                ('bufspace', '(BUFSPACE-+)(\d+)'),
                ('total_records', '(REC-TOTAL-+)(\d+)')
            ]

            attributes['data'].update(self._find_attributes_from_liscat(data_info, assoc_regex_searches))
            attributes['index'].update(self._find_attributes_from_liscat(index_info, assoc_regex_searches))

        data['attributes'] = self._parse_attributes(attributes)
        return data

    def _find_attributes_from_liscat(self, output, regex_list):
        """Looks up attributes in the output of LISTCAT.

        Arguments
        ---------
            output (str) -- Output taken from LISTCAT.
            regex_list (list) -- List of strings containing all the REGEX used for lookup.

        Returns
        -------
            dict -- Dictionary containing all the attributes found.
        """
        attributes = {}

        for (key, search) in regex_list:
            search_result = re.search(search, output)
            if search_result:
                attributes[key] = search_result.group(2)
            else:
                attributes[key] = ''

        return attributes

    def _parse_attributes(self, attrs):
        """Calls the generic _parse_attributes method and then handles the data and
        index attributes dictionaries.

        Arguments:
            attrs (dict) -- Raw dictionary processed from a LISTCAT call.

        Returns:
            dict -- Attributes dictionary with parsed values.
        """
        attrs = super()._parse_attributes(attrs)

        if 'data' in attrs:
            attrs['data'] = super()._parse_attributes(attrs['data'])
        if 'index' in attrs:
            attrs['index'] = super()._parse_attributes(attrs['index'])

        return attrs


class GenerationDataGroupHandler(DataSetHandler):
    """Class that can query Generation Data Groups.
    """

    def __init__(
        self,
        name,
        volume,
        module,
        sms_managed,
        ds_type,
        gdg_view,
        tmp_hlq=None
    ):
        """Create a new handler that will handle the query of a GDG.
        This subclass should only be instantiated by get_data_set_handler.

        Arguments:
            name (str) -- Name of the data set.
            volume (str) -- Volume where the data set is allocated.
            module (AnsibleModule) -- Ansible object with the task's context.
            sms_managed (bool) -- Whether the data set is managed by SMS.
            ds_type (str) -- Type of the data set.
            gdg_view (GenerationDataGroupView) -- Object containing a view of the GDG.
            tmp_hlq (str, optional) -- Temporary HLQ to be used in some operations.
        """
        super(GenerationDataGroupHandler, self).__init__(
            name,
            volume=volume,
            module=module,
            tmp_hlq=tmp_hlq,
            sms_managed=sms_managed,
            exists=True,
            ds_type=ds_type
        )
        self.gdg_view = gdg_view

    def query(self):
        """Uses the methods defined in our GenerationDataGroupView object to query
        a GDG's attributes and current active generations."""
        data = super().query()

        attributes = {
            'type': 'GDG',
            'limit': self.gdg_view.limit,
            'scratch': self.gdg_view.scratch,
            'empty': self.gdg_view.empty,
            'order': self.gdg_view.order,
            'purge': self.gdg_view.purge,
            'extended': self.gdg_view.extended,
            'active_gens': [generation.name for generation in self.gdg_view.generations()]
        }

        # Now we call LISTCAT to get the creation time.
        listcat_cmd = f" LISTCAT ENTRIES('{self.name}') ALL"
        mvs_cmd = f'mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin -Q={self.tmp_hlq}'
        rc, stdout, stderr = self.module.run_command(mvs_cmd, data=listcat_cmd, errors='replace')
        if rc > 0:
            raise QueryException(
                'An error ocurred while querying a Generation Data Group.',
                rc=rc,
                stdout=stdout,
                stderr=stderr
            )

        listcat_lines = stdout.split('\n')
        gdg_base_info_limit = 0

        for index in range(len(listcat_lines)):
            if gdg_base_info_limit == 0:
                if 'NONVSAM -' in listcat_lines[index]:
                    gdg_base_info_limit = index
                    break

        gdg_base_info = ' '.join(listcat_lines[0:gdg_base_info_limit])
        attributes['creation_date'] = re.search("(CREATION-+)(\d{4}\.\d{3})", gdg_base_info).group(2)
        data['attributes'] = self._parse_attributes(attributes)

        return data


class QueryException(Exception):
    """Exception class to encapsulate any error the handlers raise while
    trying to query a resource.
    """
    def __init__(self, msg, rc=None, stdout=None, stderr=None):
        """Initialized a new QueryException with relevant context for a failure
        JSON.

        Arguments:
            msg (str) -- Message describing the failure.
            rc (int, optional) -- RC from the command that failed (when available).
            stdout (int, optional) -- Standard out from the command that failed (when available).
            stderr (int, optional) -- Standar err from the command that failed (when available).
        """
        # This will be used to from the returned JSON by Ansible.
        self.json_args = {
            'msg': msg,
            'rc': rc,
            'stdout': stdout,
            'stderr': stderr
        }
        super().__init__(msg)


def get_data_set_handler(
    name,
    volume,
    module,
    tmp_hlq=None,
    sms_managed=False
):
    """Returns the correct handler needed depending on the type of data set
    we will query.

    Arguments:
        name (str) -- Name of the data set.
        volume (str) -- Volume where the data set is allocated.
        module (AnsibleModule) -- Ansible object with the task's context.
        tmp_hlq (str, optional) -- Temp HLQ for certain data set operations.
        sms_managed (bool, optional) -- Whether the data set is managed by SMS.

    Returns:
        DataSetHandler: Handler for data sets.
    """
    try:
        if DataSet.is_gds_relative_name(name):
            # Replacing the relative name because _is_in_vtoc, data_set_type and
            # LISTDSI need the absolute name to locate the data set.
            name = DataSet.resolve_gds_absolute_name(name)
    except (GDSNameResolveError, Exception):
        return DataSetHandler(name, exists=False)

    # For non-GDGs.
    if DataSet._is_in_vtoc(name, volume, tmphlq=tmp_hlq):
        ds_type = DataSet.data_set_type(name, volume=volume, tmphlq=tmp_hlq)
    # We try to create a GDG view if possible, if not, we know for sure the data set just
    # does not exist.
    else:
        try:
            gdg_view = gdgs.GenerationDataGroupView(name)
            ds_type = 'GDG'
        except zoau_exceptions.GenerationDataGroupFetchException:
            return DataSetHandler(name, exists=False)

    # Now instantiating a concrete handler based on the data set's type.
    if ds_type in DataSet.MVS_SEQ or ds_type in DataSet.MVS_PARTITIONED:
        return NonVSAMDataSetHandler(name, volume, module, sms_managed, ds_type, tmp_hlq)
    elif ds_type in DataSet.MVS_VSAM:
        return VSAMDataSetHandler(name, volume, module, sms_managed, ds_type, tmp_hlq)
    else:
        return GenerationDataGroupHandler(name, volume, module, sms_managed, ds_type, gdg_view, tmp_hlq)


def get_facts_handler(
    name,
    resource_type,
    module,
    volume=None,
    tmp_hlq=None,
    sms_managed=False,
    file_args=None
):
    """Returns the correct handler needed depending on the type of resource
    we will query.

    Arguments:
        name (str) -- Name of the resource.
        resource_type (str) -- One of 'data_set', 'aggregate' or 'file'.
        module (AnsibleModule) -- Ansible object with the task's context.
        volume (str, optional) -- Volume where a data set is allocated.
        tmp_hlq (str, optional) -- Temp HLQ for certain data set operations.
        sms_managed (bool, optional) -- Whether a data set is managed by SMS.
        file_args (dict, optional) -- Options affecting how a file is query.

    Returns:
        FactsHandler: Handler for data sets/aggregates/files.
    """
    if resource_type == 'data_set':
        return get_data_set_handler(name, volume, module, tmp_hlq, sms_managed)
    elif resource_type == 'file':
        return FileHandler(name, module, file_args)
    elif resource_type == 'aggregate':
        return AggregateHandler(name, module)


def run_module():
    """Parses the module's options and retrieves facts accordingly.
    """
    module = AnsibleModule(
        argument_spec={
            'name': {
                'type': 'str',
                'required': True,
                'aliases': ['src']
            },
            'volume': {
                'type': 'str',
                'required': False
            },
            'type': {
                'type': 'str',
                'required': False,
                'default': 'data_set',
                'choices': ['data_set', 'file', 'aggregate']
            },
            'sms_managed': {
                'type': 'bool',
                'required': False,
                'default': False
            },
            'tmp_hlq': {
                'type': 'str',
                'required': False
            },
            'follow': {
                'type': 'bool',
                'required': False,
                'default': False
            },
            'get_mime': {
                'type': 'bool',
                'required': False,
                'default': True
            },
            'get_checksum': {
                'type': 'bool',
                'required': False,
                'default': True
            },
            'checksum_algorithm': {
                'type': 'str',
                'required': False,
                'default': 'sha1',
                'choices': ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
            }
        },
        required_if=[
            # Forcing a volume when querying data sets.
            ('type', 'data_set', ('volume',))
        ],
        supports_check_mode=True,
    )

    args_def = {
        'name': {
            'arg_type': 'data_set_or_path',
            'required': True,
            'aliases': ['src']
        },
        'volume': {
            'arg_type': 'str',
            'required': False
        },
        'type': {
            'arg_type': 'str',
            'required': False
        },
        'sms_managed': {
            'arg_type': 'bool',
            'required': False
        },
        'tmp_hlq': {
            'arg_type': 'str',
            'required': False
        },
        'follow': {
            'arg_type': 'bool',
            'required': False
        },
        'get_mime': {
            'arg_type': 'bool',
            'required': False
        },
        'get_checksum': {
            'arg_type': 'bool',
            'required': False
        },
        'checksum_algorithm': {
            'arg_type': 'str',
            'required': False
        }
    }

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    name = module.params.get('name')
    volume = module.params.get('volume')
    resource_type = module.params.get('type')
    tmp_hlq = module.params.get('tmp_hlq')
    sms_managed = module.params.get('sms_managed')
    file_args = {
        'follow': module.params.get('follow'),
        'get_mime': module.params.get('get_mime'),
        'get_checksum': module.params.get('get_checksum'),
        'checksum_algorithm': module.params.get('checksum_algorithm'),
    }

    facts_handler = get_facts_handler(
        name,
        resource_type,
        module,
        volume,
        tmp_hlq,
        sms_managed,
        file_args
    )
    result = {}

    if not facts_handler.exists():
        result['msg'] = f'{name} could not be found on the system.'
        module.fail_json(**result)

    try:
        data = facts_handler.query()
        notes = facts_handler.get_extra_data()
    except QueryException as err:
        module.fail_json(**err.json_args)
    except zoau_exceptions.ZOAUException as err:
        result['msg'] = 'An error ocurred during removal of a temp data set.'
        result['rc'] = err.rc
        result['stdout'] = err.stdout_response
        result['stderr'] = err.stderr_response
        module.fail_json(**result)
    except Exception as err:
        result['msg'] = f'An unexpected error ocurred while querying a resource: {str(err)}.'
        module.fail_json(**result)

    result['stat'] = data
    result['changed'] = True
    if notes:
        result['notes'] = notes

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
