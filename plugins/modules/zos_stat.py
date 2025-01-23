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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    DataSet,
    MVSDataSet,
    GenerationDataGroup
)

try:
    from zoautil_py import datasets
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())

try:
    from zoautil_py import exceptions as zoau_exceptions
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())


LISTDSI_SCRIPT = """/* REXX */
/***********************************************************
* © Copyright IBM Corporation 2025
***********************************************************/
parse arg data_set_name
data_set_name = "'" || data_set_name || "'"
data_set_info = LISTDSI(DATA_SET_NAME)

/* Returning an error in JSON format for the module. */
if SYSREASON > 0 then
  do
    say '{'
    say '"error":true,'
    say '"reason_code":' || SYSREASON || ','
    say '"lvl1":"' || SYSMSGLVL1 || '",'
    say '"lvl2":"' || SYSMSGLVL2 || '"'
    say '}'
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
    say '"key_length":"' || SYSKEYLEN || '",'
    say '"created":"' || SYSCREATE || '",'
    say '"last_referenced":"' || SYSREFDATE || '",'
    say '"expires":"' || SYSEXDATE || '",'
    say '"updated":"' || SYSUPDATED || '",'
    say '"creation_time":"' || SYSCREATETIME || '",'
    say '"creation_step":"' || SYSCREATESTEP || '",'
    say '"creation_job":"' || SYSCREATEJOB || '",'
    say '"sms_data_class":"' || SYSDATACLASS || '",'
    say '"sms_storage_class":"' || SYSSTORCLASS || '",'
    say '"sms_management_class":"' || SYSMGMTCLASS || '",'
    say '"has_eattr":"' || SYSEADSCB || '",'
    say '"eattr_bits":"' || SYSEATTR || '",'
    /* Allocation information */
    say '"num_volumes":"' || SYSNUMVOLS || '",'
    say '"volumes":"' || SYSVOLUMES || '",'
    say '"device_type":"' || SYSUNIT || '",'
    say '"space_units":"' || SYSUNITS || '",'
    say '"allocation":"' || SYSALLOC || '",'
    say '"allocation_used":"' || SYSUSED || '",'
    say '"primary_allocation":"' || SYSPRIMARY || '",'
    say '"secondary_allocation":"' || SYSSECONDS || '",'
    say '"extends_allocated":"' || SYSEXTENTS || '",'
    say '"extends_used":"' || SYSUSEDEXTENTS || '",'
    say '"tracks":"' || SYSTRKSCYL || '",'
    say '"blocks":"' || SYSBLKSTRK || '",'
    /* Security information */
    say '"password":"' || SYSPASSWORD || '",'
    say '"racf":"' || SYSRACFA || '",'
    say '"is_encrypted":"' || SYSENCRYPT || '",'
    say '"encryption_key_label":"' || SYSKEYLABEL || '",'
    /* PDS attributes */
    say '"dir_blocks_allocated":"' || SYSADIRBLK || '",'
    say '"dir_blocks_used":"' || SYSUDIRBLK || '",'
    say '"members":"' || SYSMEMBERS || '",'
    say '"allocation_pages_used":"' || SYSUSEDPAGES || '",'
    /* PDSE attributes */
    say '"pdse_alloc_pages":"' || SYSALLOCPAGES || '",'
    say '"pdse_percentage_used":"' || SYSUSEDPERCENT || '",'
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

    def __init__(self, name: str, volume: str, module: AnsibleModule, tmp_hlq: str):
        """Create a new handler that will contain the args given and look up
        the type of data set we'll query.
        """
        super(DataSetHandler, self).__init__(name, module)
        self.volume = volume
        self.tmp_hlq = tmp_hlq if tmp_hlq else datasets.get_hlq()
        self.data_set_type = DataSet.data_set_type(name, volume=volume)
        # Since data_set_type returns None for a non-existent data set,
        # we'll set this value now and avoid another call to the util.
        self.data_set_exists = True if self.data_set_type else False

    def exists(self):
        return self.data_set_exists

    def query(self):
        data = {}

        # TODO: get the absolute name for a GDG before using LISTDSI.
        if self.data_set_type == 'GDG':
            pass
        # TODO: Probably need to change it to use DataSet's enum.
        elif self.data_set_type == 'VSAM':
            pass
        else:
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

            try:
                datasets.write(temp_script_location, LISTDSI_SCRIPT)
            except zoau_exceptions.DatasetWriteException as exc:
                return {
                    'msg': 'decho failed',
                    'rc': exc.rc,
                    'stdout': exc.stdout_response,
                    'stderr': exc.stderr_response,
                    'temp': temp_script_location
                }

            tso_cmd = f"""tsocmd "EXEC '{temp_script_location}' '{self.name}' exec" """
            rc, stdout, stderr = self.module.run_command(tso_cmd)
            if rc != 0:
                raise QueryException('Error while running query script.')
            data = json.loads(stdout)

            try:
                datasets.delete(temp_script_location)
            except zoau_exceptions.ZOAUException as exc:
                return {
                    'msg': 'removal failed',
                    'rc': exc.rc,
                    'stdout': exc.stdout_response,
                    'stderr': exc.stderr_response
                }

        return data


class QueryException(Exception):
    """Exception class to encapsulate any error the handlers raise while
    trying to query a resource.
    """
    def __init__(self, msg, rc=None, stdout=None, stderr=None):
        self.msg = msg
        super().__init__(self.msg)

def get_facts_handler(
        name: str,
        resource_type: str,
        module: AnsibleModule,
        volume: str = None,
        tmp_hlq: str = None):
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
    except QueryException as exc:
        result['msg'] = exc.msg
        module.fail_json(**result)

    result['stat'] = data
    result['changed'] = True
    if notes:
        result['notes'] = notes

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
