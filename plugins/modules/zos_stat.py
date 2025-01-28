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

seealso:
  - module: ansible.builtin.stat
  - module: zos_find
"""

EXAMPLES = r"""
- name:
  zos_stat:
"""

RETURN = r"""
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
    DatasetCreateError
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

    def __init__(self, name: str, module: AnsibleModule):
        """For now, the only attribute the different classes will share it's
        the name of the resource they are trying to query. They will also all
        require access to an AnsibleModule object to run shell commands.
        """
        self.name = name
        self.module = module

    @abc.abstractmethod
    def exists(self):
        pass

    @abc.abstractmethod
    def query(self):
        pass

    @abc.abstractmethod
    def get_extra_data(self):
        """Extra data will be treated as any information that should be returned
        to the user as part of the 'notes' section of the final JSON object.
        """
        pass


class DataSetHandler(FactsHandler):
    """Class that can query facts from a sequential, partitioned (PDS), partitioned
    extended (PDSE), VSAM or generation data sets.
    """

    # TODO: missing: block_count, owner, last_updated, creation_program
    # TODO: add gdgs and gdss
    # TODO: add option for sms-managed data sets
    # TODO: handle multivol
    # TODO: add notes about how DIRECTORY and SMSINFO could affect last ref

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

    def __init__(self, name: str, volume: str, module: AnsibleModule, tmp_hlq: str):
        """Create a new handler that will contain the args given and look up
        the type of data set we'll query.
        """
        super(DataSetHandler, self).__init__(name, module)
        self.volume = volume
        self.tmp_hlq = tmp_hlq if tmp_hlq else datasets.get_hlq()
        self.data_set_type = DataSet.data_set_type(name, volume=volume, tmphlq=self.tmp_hlq)
        # Since data_set_type returns None for a non-existent data set,
        # we'll set this value now and avoid another call to the util.
        self.data_set_exists = True if self.data_set_type else False
        # TODO: add name resolution for GDSs.
        self.is_gds = False

    def exists(self):
        return self.data_set_exists

    def query(self):
        data = {
            'resource_type': 'data_set',
            'name': self.name
        }

        if self.data_set_type in DataSet.MVS_VSAM:
            data['attributes'] = self._query_vsam()
        else:
            data['attributes'] = self._query_non_vsam()

            # if self.is_gds:
            #     data['absolute_name'] = self.absolute_name

        data['attributes'] = self._parse_attributes(data['attributes'])
        return data

    def _query_non_vsam(self):
        """Uses LISTDSI to query facts about a data set."""
        attributes = {}

        try:
            extra_args = ""
            if self.data_set_type in DataSet.MVS_PARTITIONED:
                extra_args = "DIRECTORY"

            # First creating a temp data set to hold the LISTDSI script.
            # All options are meant to allocate just enough space for it.
            # TODO: review whether the record length is still correct.
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
            tso_cmd = f"""tsocmd "EXEC '{temp_script_location}' '{self.name} {self.volume} {extra_args}' exec" """
            rc, stdout, stderr = self.module.run_command(tso_cmd)

            if rc != 0:
                raise QueryException(
                    f'An error ocurred while querying information for {self.name}.',
                    rc=rc,
                    stdout=stdout,
                    stderr=stderr
                )

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

    def _parse_attributes(self, attrs: dict):
        """Since all attributes returned by running commands return strings,
        this method ensures numerical and boolean values are returned as such.
        It also makes sure datetimes are better formatted and replaces '?'
        with more user-friendly values."""
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
        return value != '' and '?' not in value and value != 'N/A' and value != 'NO_LIM'

    def _parse_values(self, attrs, keys, true_function):
        for key in keys:
            try:
                attrs[key] = true_function(attrs[key]) if attrs[key] else None
            except ValueError:
                pass

        return attrs

    def _replace_values(self, attrs, keys, true_value, false_value, condition):
        for key in keys:
            attrs[key] = true_value if attrs[key] == condition else false_value

        return attrs

    def _parse_datetimes(self, attrs, keys):
        for key in keys:
            try:
                attrs[key] = datetime.strptime(attrs[key], '%Y/%j').strftime('%Y-%m-%d')
            except ValueError:
                # z/OS returns 0 when a date is not set.
                if attrs[key] == "0":
                    attrs[key] = None

        return attrs


class QueryException(Exception):
    """Exception class to encapsulate any error the handlers raise while
    trying to query a resource.
    """
    def __init__(
        self,
        msg,
        rc=None,
        stdout=None,
        stderr=None
    ):
        self.json_args = {
            'msg': msg,
            'rc': rc,
            'stdout': stdout,
            'stderr': stderr
        }
        super().__init__(msg)

def get_facts_handler(
    name: str,
    resource_type: str,
    module: AnsibleModule,
    volume: str = None,
    tmp_hlq: str = None
):
    """Returns the correct handler needed depending on the type of resource
    we will query.
    """
    if resource_type == 'data_set':
        return DataSetHandler(name, volume, module, tmp_hlq)
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

    facts_handler = get_facts_handler(name, resource_type, module, volume, tmp_hlq)
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
