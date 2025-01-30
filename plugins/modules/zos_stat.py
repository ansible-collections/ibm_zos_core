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
short_description: Retrieve facts from z/OS
description:
  - The L(zos_stat,./zos_stat.html) module retrieves facts from resources
    stored in a z/OS system.
  - Resources that can be queried are files, data sets and aggregates.
options:
  name:
    description:
        - Name of a data set or aggregate, or a file path, to query.
        - Data sets can be sequential, partitioned (PDS), partitioned
          extended (PDSE), VSAMs or generation data sets (GDGs).
    type: str
    required: true
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

notes:
  - When querying data sets, the module will create a temporary data set
    that requires around 4 kilobytes of available space on the remote host.
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
"""

# TODO: get samples for creation_job and creation_step.
# TODO: check whether 'success' is the correct value for returned.
RETURN = r"""
stat:
  description: Dictionary containing information about the resource.
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
          sample: PS
        type:
          description: Type of the data set.
          returned: success
          type: str
          sample: LIBRARY
        record_format:
          description: Record format of a data set.
          returned: success
          type: str
          sample: VB
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
          description: Current values of the EATTR bits for a data set.
          returned: success
          type: str
          sample: OPT
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
              sample:
            creation_step:
              description: JCL job step that created the data set.
              returned: success
              type: str
              sample:
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
          sample: TRACK
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
          sample: STANDARD
        sms_mgmt_class:
          description:
            - The SMS management class name.
            - Only returned when the data set is managed by SMS and sms_managed
              is set to true.
          returned: success
          type: str
          sample: VSAM
        sms_storage_class:
          description:
            - The SMS storage class name.
            - Only returned when the data set is managed by SMS and sms_managed
              is set to true.
          returned: success
          type: str
          sample: FAST
        encrypted:
          description: Whether the data set is encrypted.
          returned: success
          type: bool
          sample: false
        password:
          description:
            - Whether the data set has a password set to read/write.
            - Value can be either one of 'NONE', 'READ' or 'WRITE'.
          returned: success
          type: str
          sample: NONE
        racf:
          description:
            - Whether there is RACF protection set on the data set.
            - Value can be either one of 'NONE', 'GENERIC' or 'DISCRETE'.
          returned: success
          type: str
          sample: NONE
        key_label:
          description: The encryption key label for an encrypted data set.
          returned: success
          type: str
          sample: KEYDSN
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
            - Value can be either one of 'BASIC', 'LARGE' or 'EXTENDED'.
          returned: success
          type: str
          sample: BASIC
"""

import abc
import json
from datetime import datetime

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
    from zoautil_py import datasets
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())

try:
    from zoautil_py import exceptions as zoau_exceptions
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())


class FactsHandler():
    """Base class for every other handler that will query resources on
    a z/OS system.
    """

    def __init__(self, name, module):
        """Setting up the three common attributes for each handler (resource name,
        module and extra_data.

        Arguments:
            name (str) -- Resource name.
            module (AnsibleModule) -- Ansible object with the task's context.
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


class DataSetHandler(FactsHandler):
    """Class that can query facts from a sequential, partitioned (PDS), partitioned
    extended (PDSE), VSAM or generation data sets.
    """

    # TODO: missing: block_count, owner, last_updated, creation_program
    # TODO: add gdgs (using LISTCAT) and gdss
    # TODO: add vsams
    # TODO: handle multivol

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

    def __init__(self, name, volume, module, tmp_hlq, sms_managed):
        """Create a new handler that will handle the query of an MVS data set.

        Arguments:
            name (str) -- Name of the data set.
            volume (str) -- Volume where the data set is allocated.
            module (AnsibleModule) -- Ansible object with the task's context.
            tmp_hlq (str) -- Temporary HLQ to be used in some operations.
            sms_managed (bool) -- Whether the data set is managed by SMS.
        """
        super(DataSetHandler, self).__init__(name, module)
        self.volume = volume
        self.tmp_hlq = tmp_hlq if tmp_hlq else datasets.get_hlq()
        self.sms_managed = sms_managed
        self.data_set_exists = False
        self.data_set_type = None

        try:
            if DataSet.is_gds_relative_name(self.name):
                # Replacing the relative name because _is_in_vtoc, data_set_type and
                # LISTDSI need the absolute name to locate the data set.
                self.name = DataSet.resolve_gds_absolute_name(self.name)
        except (GDSNameResolveError, Exception):
            # Don't need to do anything in this case since we already set data_set_exists
            # and data_set_type to their negative values.
            pass

        if DataSet._is_in_vtoc(self.name, self.volume, tmphlq=self.tmp_hlq):
                self.data_set_type = DataSet.data_set_type(self.name, volume=self.volume, tmphlq=self.tmp_hlq)
                self.data_set_exists = True

    def exists(self):
        """Returns whether the given data set was found on the system.
        """
        return self.data_set_exists

    def query(self):
        """Query a non-VSAM or VSAM data set and parse the output taken from
        the query commands.

        Returns:
            dict -- Attributes queried for a data set.
        """
        data = {
            'resource_type': 'data_set',
            'name': self.name
        }

        if self.data_set_type in DataSet.MVS_VSAM:
            data['attributes'] = self._query_vsam()
        else:
            data['attributes'] = self._query_non_vsam()

        data['attributes'] = self._parse_attributes(data['attributes'])
        return data

    def _query_non_vsam(self):
        """Uses LISTDSI to query facts about a data set, while also handling
        specific arguments needed depending on data set type.

        Returns:
            dict -- Data set attributes.

        Raises:
            QueryException: When the script's data set's allocation fails.
            QueryException: When ZOAU fails to write the script to its data set.
        """
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

        return attributes

    def _query_vsam(self):
        """Uses LISTCAT to query facts about a VSAM."""
        pass

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
        """Since all attributes returned by running commands return strings,
        this method ensures numerical and boolean values are returned as such.
        It also makes sure datetimes are better formatted and replaces '?', 'N/A',
        'NO_LIM', with more user-friendly values.

        Arguments:
            attrs (dict) -- Raw dictionary processed from a LISTDSI call.

        Returns:
            dict -- Attributes' dictionary with parsed values.
        """
        attrs = {
            key: attrs[key] if self._is_value_valid(attrs[key]) else None
            for key in attrs
        }

        if attrs['jcl_attrs']['creation_job'] == '':
            attrs['jcl_attrs']['creation_job'] = None
        if attrs['jcl_attrs']['creation_step'] == '':
            attrs['jcl_attrs']['creation_step'] = None

        # Numerical values.
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
        attrs = self._parse_values(attrs, num_attrs, int)

        # Boolean values.
        bool_attrs = ['has_extended_attrs', 'updated_since_backup', 'encrypted']
        attrs = self._replace_values(attrs, bool_attrs, True, False, 'YES')

        # Datetime values.
        datetime_attrs = ['creation_date', 'expiration_date', 'last_reference']
        attrs = self._parse_datetimes(attrs, datetime_attrs)

        return attrs

    def _is_value_valid(self, value):
        """Returns whether the value should be replaced for None.

        Arguments:
            value (str) -- Raw value of an attribute for a data set.

        Returns:
            bool -- Whether the value should stay as is or be replace with None.
        """
        # Getting rid of values that basically say the value doesn't matter in
        # context or is unknown.
        return value != '' and '?' not in value and value != 'N/A' and value != 'NO_LIM'

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
                attrs[key] = datetime.strptime(attrs[key], '%Y/%j').strftime('%Y-%m-%d')
            except ValueError:
                # z/OS returns 0 when a date is not set, so we set it to None.
                if attrs[key] == "0":
                    attrs[key] = None

        return attrs


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


def get_facts_handler(
    name,
    resource_type,
    module,
    volume = None,
    tmp_hlq = None,
    sms_managed = False
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

    Returns:
        DataSetHandler: Handler for data sets.
    """
    if resource_type == 'data_set':
        return DataSetHandler(name, volume, module, tmp_hlq, sms_managed)
    elif resource_type == 'file':
        pass
    elif resource_type == 'aggregate':
        pass


def run_module():
    """Parses the module's options and retrieves facts accordingly.
    """
    module = AnsibleModule(
        argument_spec={
            'name': {
                'type': 'str',
                'required': True
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
            'required': True
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

    facts_handler = get_facts_handler(
        name,
        resource_type,
        module,
        volume,
        tmp_hlq,
        sms_managed
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
