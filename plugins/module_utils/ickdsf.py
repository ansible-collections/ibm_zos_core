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

# from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
#     MissingZOAUImport,
#     MissingImport,
# )

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zos_mvs_raw import MVSCmd  # pylint: disable=import-error
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dd_statement import (  # pylint: disable=import-error
    DDStatement,
    StdoutDefinition,
    StdinDefinition,
)


def convert(module, args):

    # Get parameters from playbooks
    volume_address = args.get('volume_address')
    verify_existing_volid = args.get('verify_existing_volid')
    verify_offline = args.get('verify_offline')
    volid = args.get('volid')
    vtoc_tracks = args.get('vtoc_tracks')
    index = args.get('index')
    verify_no_data_sets_exist = args.get('verify_no_data_sets_exist')
    sms_managed = args.get('sms_managed')
    addr_range = args.get('addr_range')
    volid_prefix = args.get('volid_prefix')

    # validate parameters
    if volume_address is None:
        msg = 'Volume address must be defined'
        # raise Exception(msg)
        module.fail_json(msg) # TODO - fail with result -- do i want an init class so i can self.fail_json?

    try:
        int(volume_address, 16)
    except ValueError:
        msg = 'Volume address must be a valid 64-bit hex value'
        # raise Exception(msg)
        module.fail_json(msg) # TODO - fail with result -- do i want an init class so i can self.fail_json?

    # convert playbook args to JCL parameters
    cmd_args = {
        'volume_address': 'unit({0})'.format(volume_address)
    }

    if vtoc_tracks:
        cmd_args['vtoc_tracks'] = 'vtoc(0, 1, {0})'.format(vtoc_tracks)
    else:
        cmd_args['vtoc_tracks'] = ''
    if volid:
        cmd_args['volid'] = 'volid({0})'.format(volid)
    else:
        cmd_args['volid'] = ''
    if not verify_existing_volid:
        cmd_args['verify_existing_volid'] = 'noverify'
    else:
        cmd_args['verify_existing_volid'] = 'verify({0})'.format(verify_existing_volid)
    if verify_offline:
        cmd_args['verify_offline'] = 'verifyoffline'
    else:
        cmd_args['verify_offline'] = 'noverifyoffline'
    if verify_no_data_sets_exist:
        cmd_args['verify_no_data_sets_exist'] = 'nods'
    else:
        cmd_args['verify_no_data_sets_exist'] = 'ds'
    if index:
        cmd_args['index'] = ''
    else:
        cmd_args['index'] = 'noindex'
    if sms_managed:
        cmd_args['sms_managed'] = 'storagegroup'
    else:
        cmd_args['sms_managed'] = ''

    # Format into JCL strings for zos_mvs_raw
    cmd = [
        ' init {0} {1} {2} {3} - '.format(
            cmd_args['volume_address'],
            cmd_args['verify_existing_volid'],
            cmd_args['verify_offline'],
            cmd_args['volid']),
        ' {0} {1} {2} {3}'.format(
            cmd_args['vtoc_tracks'],
            cmd_args['sms_managed'],
            cmd_args['verify_no_data_sets_exist'],
            cmd_args['index'])]

    # Check if Playbook wants to INIT a range of volumes
    if addr_range and volid_prefix:
        if not verify_no_data_sets_exist:
            msg = 'You are not allowed to initialize a range of volumes without checking for data sets.'
            raise Exception(msg)
        start = int(str(volume_address), 16)
        end = start + addr_range
        for i in range(start + 1, end + 1):
            next_addr = '{0:x}'.format(i)
            next_vol_id = str(volid_prefix) + next_addr
            formatted_next_addr = 'unit({0})'.format(next_addr)
            formatted_next_vol_id = 'volid({0})'.format(next_vol_id)
            cmd.append(' init {0} {1} {2} {3} - '.format(
                formatted_next_addr,
                cmd_args['verify_existing_volid'],
                cmd_args['verify_offline'],
                formatted_next_vol_id))
            cmd.append(' {0} {1} {2} {3}'.format(
                cmd_args['vtoc_tracks'],
                cmd_args['sms_managed'],
                cmd_args['verify_no_data_sets_exist'],
                cmd_args['index']))

    return cmd


def init(module, result, parsed_args):
    # Convert args parsed from module to ickdsf INIT command
    cmd = convert(module, parsed_args)

    # TODO - add error handling here and in convert() for "bad" cmd
    
    result['command'] = cmd # add raw command to result -- good for debugging

    # format into MVS Command
    sysprintDDStatement = DDStatement("SYSPRINT", StdoutDefinition())
    sysInDDStatement = DDStatement("SYSIN", StdinDefinition(cmd))

    dds = []
    dds.append(sysprintDDStatement)
    dds.append(sysInDDStatement)

    
    # invoke MVS Command
    response = MVSCmd.execute_authorized("ICKDSF", dds, parm='NOREPLYU,FORCE')

    result['mvs-response-stdout'] = response.stdout
    result['mvs-response-stderr'] = response.stderr
    result['rc'] = response.rc
    
    rc = response.rc

    if rc != 0:
        result['failed'] = True
        result['msg'] = "INIT Failed with return code {}".format(rc)
    else:
        result['changed'] = True

    return dict(result)
