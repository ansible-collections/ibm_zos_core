# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION=r'''
---
module: zos_data_set
short_description: Create and set attributes for data sets
description:
    - Create, delete and set attributes of data sets.
    - When forcing data set replacement, contents will not be preserved.
version_added: "2.9"
author: Blake Becker <blake.becker@ibm.com>
options:
    name:
        description:
            - The name of the data set being managed. (e.g “USER.TEST”)
        type: str
        required: true
        version_added: "2.9"
    state:
        description:
            - The final state desired for specified data set. 
            - >
              If `absent`, will ensure the data set is not present on the system.
              Note that `absent` will not cause `zos_data_set` to fail if data set does not exist as the state did not change. 
            - >
              If `present`, will ensure the data set is present on the system.
              Note that `present` will not replace an existing data set by default, even when the attributes do not match our desired data set.
              If replacement behavior is desired, see the options `replace` and `unsafe_writes`.
        required: false
        default: present
        choices:
          - present
          - absent
        version_added: "2.9"
    type:
        description:
            - The data set type to be used when creating a data set. (e.g “pdse”)
            - MEMBER expects to be used with an existing partitioned data set.
            - Choices are case-insensitive.
        required: false
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
            - The size of the data set (e.g “5M”)
            - Valid units of size are "K", "M", "G", "CYL" and "TRK"
            - Note that "CYL" and "TRK" follow size conventions for 3390 disk types (56,664 bytes/TRK & 849,960 bytes/CYL)
            - The "CYL" and "TRK" units are converted to bytes and rounded up to the nearest "K" measurement.
            - Ensure there is no space between the numeric size and unit.
        type: str
        required: false
        default: 5M
        version_added: "2.9"
    format:
        description:
            - The format of the data set. (e.g “FB”)
            - Choices are case-insensitive.
        required: false
        choices: 
          - FB
          - VB
          - FBA
          - VBA
          - U
        default: FB
        version_added: "2.9"
    data_class:
        description:
            - The data class name (required for SMS-managed data sets)
        type: str
        required: false
        version_added: "2.9"
    record_length:
        description:
            - The logical record length. (e.g 80)
            - For variable data sets, the length must include the 4-byte prefix area.
        type: int
        required: false
        default: if FB/FBA 80, if VB/VBA 137, if U 0
        version_added: "2.9"
    replace:
        description:
            - When `replace` is `true`, and `state` is `present`, existing data set matching name will be replaced.
            - > 
              Replacement is performed by deleting the existing data set and creating a new data set with the desired 
              attributes in the old data set's place. This may lead to an inconsistent state if data set creations fails 
              after the old data set is deleted.
            - If `replace` is `true`, all data in the original data set will be lost.
        type: bool
        required: false
        default: false
        version_added: "2.9"
    batch:
        description:
            - Batch can be used to perform operations on multiple data sets in a single module call.
            - Each item in the list expects the same options as zos_data_set.
        type: list
        required: false
        version_added: "2.9"

'''
EXAMPLES = r'''
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

- name: Attempt to replace a data set if it exists, allow unsafe_writes
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: fb
    record_length: 25
    replace: yes
    unsafe_writes: yes

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
      - name:  user.private.libs2
        type: PDSE
        size: 10CYL
        format: fb
        replace: yes
        unsafe_writes: yes
      - name: user.private.libs1(member1)
        type: MEMBER
      - name: user.private.libs2(member1)
        type: MEMBER
        replace: yes
      - name: user.private.libs2(member2)
        type: MEMBER
'''
RETURN='''
original_message:
    description: The original list of parameters and arguments, plus any defaults used.
    type: dict
message:
    description: The output message that the sample module generates
    type: dict
    stdout:
        description: The output from the module
        type: str
    stderr: 
        description: Any error text from the module
        type: str
changed: 
    description: Indicates if any changes were made during module operation.
    type: bool
'''
from ansible.module_utils.basic import AnsibleModule
from traceback import format_exc
import re
from zoautil_py import Datasets
from collections import OrderedDict
from math import ceil
import tempfile
import os

# * Make AnsibleModule module object global to
# * simplify use of run_command in functions
run_command = None

# CONSTANTS
DATA_SET_TYPES = [
    # 'KSDS',
    'ESDS',
    'RRDS',
    'LDS',
    'SEQ',
    'PDS',
    'PDSE',
    'MEMBER',
]

DATA_SET_FORMATS = [
    'FB',
    'VB',
    'FBA',
    'VBA',
    'U',
]

DEFAULT_RECORD_LENGTHS = {
    'FB': 80,
    'FBA': 80,
    'VB': 137,
    'VBA': 137,
    'U': 0,
}

# Module args mapped to equivalent ZOAU data set create args 
ZOAU_DS_CREATE_ARGS = {
    'name': 'name',
    'type': 'type',
    'size': 'size',
    'format': 'format',
    'data_class': 'class_name',
    'record_length': 'length',
    'key_offset': 'offset'
}

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
    if params.get('name') and params.get('batch'):
        raise ValueError('Top-level parameters "name" and "batch" are mutually exclusive.')
    elif not params.get('name') and not params.get('batch'):
        raise ValueError('One of the following parameters is required: "name", "batch".')
    if params.get('name'):
        data_sets_parameter_list = [params]
    else:
        data_sets_parameter_list = params.get('batch')
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
        based on their ordering in param_handlers. If a parameter is dependent on the 
        final value of another parameter, make sure they are ordered accordingly.
        
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
            if not re.match(r'[1-9][0-9]*', arg_val) or (value < 1 or value > 32768):
                raise ValueError('Value {0} is invalid for record_length argument. record_length must be between 1 and 32768 bytes.'.format(arg_val))
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
        parameters[key] = value(original_params.get(key), parameters)
    for key, value in original_params.items():
        if key not in parameters:
            parameters[key] = value
    return parameters

def data_set_name(arg_val, params):
    """Validates provided data set name(s) are valid.
    Returns a list containing the name(s) of data sets."""
    dsnames = generate_name_list(arg_val)
    for dsname in dsnames: 
        if not re.match(r'^(?:(?:[A-Z]{1}[A-Z0-9]{0,7})(?:[.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}$', dsname, re.IGNORECASE):
            if not (re.match(r'^(?:(?:[A-Z]{1}[A-Z0-9]{0,7})(?:[.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}\([A-Z]{1}[A-Z0-9]{0,7}\)$', dsname, re.IGNORECASE) and params.get('type') == 'MEMBER'):
                raise ValueError('Value {0} is invalid for data set argument.'.format(dsname))
    return dsnames

def data_set_size(arg_val, params):
    """Validates provided data set size is valid.
    Returns the data set size. """
    if params.get('state') == 'absent':
        return None
    if arg_val == None:
        return None
    match = re.match(r'([1-9][0-9]*)(M|G|K|TRK|CYL)', arg_val, re.IGNORECASE)
    if not match:
        raise ValueError('Value {0} is invalid for size argument. Valid size measurements are "K", "M", "G", "TRK" or "CYL".'.format(arg_val))
    if re.match(r'TRK|CYL', match.group(2), re.IGNORECASE):
        arg_val = str(convert_size_to_kilobytes(int(match.group(1)), match.group(2).upper())) + 'K'
    return arg_val

def data_class(arg_val, params):
    """Validates provided data class is of valid length.
    Returns the data class. """
    if params.get('state') == 'absent' or not arg_val:
        return None
    if len(arg_val) < 1 or len(arg_val) > 8:
        raise ValueError('Value {0} is invalid for data_class argument. data_class must be at least 1 and at most 8 characters.'.format(arg_val))
    return arg_val

def record_length(arg_val, params):
    """Validates provided record length is valid.
    Returns the record length as integer."""
    if params.get('state') == 'absent':
        return None
    arg_val = DEFAULT_RECORD_LENGTHS.get(params.get('format'), None) if not arg_val else int(arg_val)
    if arg_val == None:
        return None
    if not re.match(r'[0-9]*', str(arg_val)) or (arg_val < 0 or arg_val > 32768):
        raise ValueError('Value {0} is invalid for record_length argument. record_length must be between 0 and 32768 bytes.'.format(arg_val))
    return arg_val

def data_set_format(arg_val, params):
    """Validates data set format is valid.
    Returns uppercase data set format."""
    if params.get('state') == 'absent':
        return None
    if arg_val == None and params.get('record_length') != None:
        raise ValueError('format must be provided when providing record_length.')
    if arg_val == None:
        return None
    formats = '|'.join(DATA_SET_FORMATS)
    if not re.match(formats, arg_val, re.IGNORECASE):
        raise ValueError('Value {0} is invalid for format argument. format must be of of the following: {1}.'.format(arg_val, ', '.join(DATA_SET_FORMATS)))
    return arg_val.upper()

def key_offset(arg_val, params):
    """Validates data set offset is valid.
    Returns data set offset as integer."""
    if params.get('state') == 'absent':
        return None
    if params.get('type') == 'KSDS' and arg_val == None:
        raise ValueError('key_offset is required when requesting KSDS data set.')
    if arg_val == None:
        return None
    arg_val = int(arg_val)
    if not re.match(r'[0-9]+', str(arg_val)):
        raise ValueError('Value {0} is invalid for offset argument. offset must be between 0 and length of object - 1.'.format(arg_val))
    return arg_val

def data_set_type(arg_val, params):
    """Validates data set type is valid.
    Returns uppercase data set type."""
    if params.get('state') == 'absent':
        return None
    if arg_val == None:
        return None
    types = '|'.join(DATA_SET_TYPES)
    if not re.match(types, arg_val, re.IGNORECASE):
        raise ValueError('Value {0} is invalid for type argument. type must be of of the following: {1}.'.format(arg_val, ', '.join(DATA_SET_TYPES)))
    return arg_val.upper()


# ------ Functions to determine default arguments based on provided args ----- #
def perform_data_set_operations(name, state, **extra_args):
    """ Calls functions to perform desired operations on 
    one or more data sets. Returns boolean indicating if changes were made. """
    changed = False
    for dsname in name:
        if state == 'present' and extra_args.get('type') != 'MEMBER':
            changed = ensure_data_set_present(dsname, **extra_args) or changed
        elif state == 'present' and extra_args.get('type') == 'MEMBER':
            changed = ensure_data_set_member_present(dsname, **extra_args) or changed
        elif extra_args.get('type') != 'MEMBER':
            changed = ensure_data_set_absent(dsname) or changed
        else:
            changed = ensure_data_set_member_absent(dsname) or changed
    return changed

def generate_name_list(name):
    """ Generate a list of data set names to perform operation on.
    Will remove empty arguments and convert arguments to strings. """
    if not isinstance(name, list):
        name = [name]
    name = [str(x) for x in name if len(str(x)) > 0]
    return name
        
def ensure_data_set_present(name, replace, **extra_args):
    """Creates data set if it does not already exist.
    The replace argument is used to determine behavior when data set already
    exists. Returns a boolean indicating if changes were made. """
    ds_create_args = rename_args_for_zoau(extra_args)
    if data_set_exists(name):
        if not replace:
            return False
        replace_data_set(name, ds_create_args)
    else:
        create_data_set(name, ds_create_args)
    return True

def ensure_data_set_absent(name):
    """Deletes provided data set if it exists.
    Returns a boolean indicating if changes were made. """
    if data_set_exists(name):
        delete_data_set(name)
        return True
    return False

# ? should we do additional check to ensure member was actually created?
def ensure_data_set_member_present(name, replace, **extra_args):
    """Creates data set member if it does not already exist.
    The replace argument is used to determine behavior when data set already
    exists. Returns a boolean indicating if changes were made."""
    if data_set_member_exists(name):
        if not replace:
            return False
        delete_data_set_member(name)
    create_data_set_member(name)
    return True

def ensure_data_set_member_absent(name):
    """Deletes provided data set member if it exists.
    Returns a boolean indicating if changes were made."""
    if data_set_member_exists(name):
        delete_data_set_member(name)
        return True
    return False

def data_set_exists(name):
    rc, stdout, stderr = run_command('head "//\'{}\'"'.format(name))
    if stderr and 'EDC5049I' in stderr:
        return False
    return True

def data_set_member_exists(name):
    """Checks for existence of data set member."""
    # parsed_data_set = re.match(r'^((?:(?:[A-Z]{1}[A-Z0-9]{0,7})(?:[.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7})\(([A-Z]{1}[A-Z0-9]{0,7})\)$', name, re.IGNORECASE)
    rc, stdout, stderr = run_command('head "//\'{}\'"'.format(name))
    if rc != 0 or (stderr and 'EDC5067I' in stderr):
        return False
    return True

    # response = Datasets.list_members(parsed_data_set.group(1))
    # member_name = parsed_data_set.group(2)
    # members = response.split('\\n') if response else []
    # for member in members:
    #     if member.strip().upper() == member_name.upper():
    #         return True
    # return False

# TODO: determine if better to move original to new name and create in place instead of deleting and moving
def replace_data_set(name, extra_args):
    """ Attempt to replace an existing data set. """
    delete_data_set(name)
    create_data_set(name, extra_args)
    return

def rename_args_for_zoau(args = {}):
    """ Renames module arguments to match those desired by zoautil_py data set create method. 
    Returns a dictionary with renamed args. """
    ds_create_args = {}
    for module_arg_name, zoau_arg_name in ZOAU_DS_CREATE_ARGS.items():
        if args.get(module_arg_name):
            ds_create_args[zoau_arg_name] = args.get(module_arg_name)
    return ds_create_args

def create_data_set(name, extra_args = {}):
    """ A wrapper around zoautil_py data set create to raise exceptions on failure. """
    rc = Datasets.create(name, **extra_args)
    if rc > 0:
        raise DatasetCreateError(name, rc)
    return

def delete_data_set(name):
    """ A wrapper around zoautil_py data set delete to raise exceptions on failure. """
    rc = Datasets.delete(name)
    if rc > 0:
        raise DatasetDeleteError(name, rc)
    return

def create_data_set_member(name):
    """Create a data set member if the partitioned data set exists.
    Also used to overwrite a data set member if empty replacement is desired.
    Raises DatasetNotFoundError if data set cannot be found."""
    try:
        base_dsname = name.split('(')[0]
        if not base_dsname or not data_set_exists(base_dsname):
            raise DatasetNotFoundError(name)
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        rc, stdout, stderr = run_command('cp {} "//\'{}\'"'.format(tmp_file.name, name))
        if rc != 0:
            raise DatasetMemberCreateError(name, rc)
    except Exception:
        raise
    finally:
        os.remove(tmp_file.name)
    return

def delete_data_set_member(name):
    """ A wrapper around zoautil_py data set delete_members to raise exceptions on failure. """
    rc = Datasets.delete_members(name)
    if rc > 0:
        raise DatasetMemberDeleteError(name, rc)
    return
    
def convert_size_to_kilobytes(old_size, old_size_unit):
    """Convert unsupported size unit to KB.
    Assumes 3390 disk type."""
    # Size measurements in bytes
    KB = 1024
    TRK = 56664
    CYL = 849960
    old_size = int(old_size)
    if old_size_unit == 'TRK':
        new_size = ceil((old_size*TRK)/KB)
    elif old_size_unit == 'CYL':
        new_size = ceil((old_size*CYL)/KB) 
    return new_size

# TODO: Add back safe data set replacement when issues are resolved
def run_module():    
    # TODO: add logic to handle aliases during parsing
    module_args = dict(
        # Used for batch data set args
        batch=dict(
            type='list',
            elements='dict',
            options=dict(
                name=dict(
                    required=True,
                ),
                state=dict(
                    type='str',
                    default='present',
                    choices=['present','absent']
                ),
                type=dict(
                    type='str',
                    required=False,
                ),
                size=dict(
                    type='str',
                    required=False
                ),
                format=dict(
                    type='str',
                    required=False,
                ),
                data_class=dict(
                    type='str', 
                    required=False, 
                ),
                record_length=dict(
                    type='int', 
                ),
                # NEEDS FIX FROM ZOAUTIL
                
                # key_offset=dict(
                #     type='int',
                #     required=False,
                #     aliases=['offset']
                # ),
                replace=dict(
                    type='bool',
                    default=False,
                ),
                # unsafe_writes=dict(
                #     type='bool',
                #     default=False
                # )
            )
        ),
        # For individual data set args
        name=dict(
            type='str'
        ),
        state=dict(
            type='str',
            default='present',
            choices=['present','absent']
        ),
        type=dict(
            type='str',
            required=False,
        ),
        size=dict(
            type='str',
            required=False
        ),
        format=dict(
            type='str',
            required=False,
        ),
        data_class=dict(
            type='str', 
            required=False, 
        ),
        record_length=dict(
            type='int', 
        ),
        # NEEDS FIX FROM ZOAUTIL
        
        # key_offset=dict(
        #     type='int',
        #     required=False,
        #     aliases=['offset']
        # ),
        replace=dict(
            type='bool',
            default=False,
        ),
        # unsafe_writes=dict(
        #     type='bool',
        #     default=False
        # )
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # * Make module object global to avoid passing 
    # * through multiple functions
    global run_command
    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    run_command = module.run_command
    
    result['original_message'] = module.params

    if module.check_mode:
        if module.params.get('replace'):
            result['changed'] = True
        return result
    
    parameter_handlers = OrderedDict()
    parameter_handlers['type'] = data_set_type
    parameter_handlers['data_class'] = data_class
    parameter_handlers['format'] = data_set_format
    parameter_handlers['name'] = data_set_name
    parameter_handlers['size'] = data_set_size
    # parameter_handlers['key_offset'] = key_offset
    parameter_handlers['record_length'] = record_length
    
    try:
        data_set_param_list = get_individual_data_set_parameters(module.params)
        
        for data_set_params in data_set_param_list:
            parameters = process_special_parameters(data_set_params, parameter_handlers)
            result['changed'] = perform_data_set_operations(**parameters) or result.get('changed', False)
    except Error as e:
        module.fail_json(msg=e.msg, **result)
    except Exception as e:
        trace = format_exc()
        module.fail_json(msg='An unexpected error occurred: {0}'.format(trace), **result)

    result['message'] = {'stdout': 'Desired data set operation(s) succeeded.', 'stderr': ''}
    
    module.exit_json(**result)

class Error(Exception):
    pass

class DatasetDeleteError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during deletion of data set "{0}". RC={1}'.format(data_set, rc)

class DatasetCreateError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during creation of data set "{0}". RC={1}'.format(data_set, rc)
        
class DatasetMemberDeleteError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during deletion of data set member"{0}". RC={1}'.format(data_set, rc)
        
class DatasetMemberCreateError(Error):
    def __init__(self, data_set, rc):
        self.msg = 'An error occurred during creation of data set member"{0}". RC={1}'.format(data_set, rc)
        
class DatasetNotFoundError(Error):
    def __init__(self, dataset):
        self.msg = 'The data set "{0}" could not be located.'.format(dataset)
        
def main():
    run_module()

if __name__ == '__main__':
    main()
