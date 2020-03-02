# -*- coding: utf-8 -*-
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION =r'''
---
module: zos_operator_openquestion
short_description: Display outstanding messages requiring operator action.
description:
    - Get a list of outstanding messages requiring operator action given one or more conditions.
author: "Ping Xiao (@xiaoping)"
options:
  request_number_list:
    description:
      - Parameter that specifies a question number, or a list of numbers.
    type: list
    elements: int
    required: false
    default: []
  system:
    description:
      - Filter messages for a system. If the system name is not specified, all system messages in SYSPLEX will be returned. Wild cards are not supported.
    type: str
    required: false
    default: false
  message_id:
    description:
      - The message identifier for the action message awaiting a reply.
    type: str
    required: false
    default: false
  jobname:
    description:
      - The name of the job which issued the action message.
    type: str
    required: false
    default: false
seealso: 
- module: zos_operator
notes:
  - check_mode is supported, but in the case of this module, it never changs the system state so always return false.
'''

EXAMPLES =r'''
# Task(s) is a call to an ansible module, basically an action needing to be accomplished
- name: Get all outstanding messages requiring operator action
  zos_operator_openquestion:

- name: Get outstanding messages given the question number
  zos_operator_openquestion:
    request_number_list:
        - '010'
        - '008'
        - '009'

- name: To display all outstanding messages issued on system MV2H
  zos_operator_openquestion:
      system: mv2h

- name: To display all outstanding messages whose job name begin with im5
  zos_operator_openquestion:
      jobname: im5*

- name: To display the outstanding messages whose message id begin with dsi*
  zos_operator_openquestion:
      message_id: dsi*

- name: Get outstanding messages given the various conditions
  zos_operator_openquestion:
    jobname: mq*
    message_id: dsi*
    system: mv29
'''
RETURN = '''
changed:
    description: true if the state was changed, otherwise false
    returned: always
    type: bool
    sample: 'false'
failed:
    description: true if run operator command failed, othewise false
    returned: always
    type: bool
    sample: 'true'
requests_count:
    description: The count of the outstanding messages
    returned: success
    type: int
    sample: '10'
requests:
    description: The list of the outstanding messages
    returned: success
    type: list[dict]
    sample:[
            {
                'number': '086',
                'type': 'R', 'system':
                'MV2D', 'job_id':
                'STC15120', 'message_text':
                '*086 DSI802A IYM2D    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND',
                'jobname': 'MQNVIEW',
                'message_id': 'DSI802A'
            },
            {
                'number': '070',
                'type': 'R',
                'system': 'MV29',
                'job_id': 'STC14852',
                'message_text': '*070 DSI802A IYM29    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND',
                'jobname': 'MQNVIEW',
                'message_id': 'DSI802A'
            }
          ]
'''


from ansible.module_utils.basic import AnsibleModule
import argparse
import re
from traceback import format_exc
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import BetterArgParser
from zoautil_py import OperatorCmd


def run_module():
    module_args = dict(
        request_number_list=dict(type='list', required=False,default=[]),
        system=dict(type='str',required=False),
        message_id=dict(type='str',required=False),
        jobname=dict(type='str',required=False)
    )

    arg_defs=dict(
        request_number_list = dict(
            arg_type=request_number_list_type,
            required=False,
            default=[]
        ),
        system=dict(
            arg_type=system_type,
            required=False
        ),
        message_id=dict(
            arg_type=message_id_type,
            required=False
        ),
        jobname=dict(
            arg_type=jobname_type,
            required=False
        )
    )

    result = dict(
        changed=False,
        original_message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result['original_message'] = module.params
    if module.check_mode:
        return result
    try:
        parser = BetterArgParser(arg_defs)
        new_params = parser.parse_args(module.params)
        requests = find_required_request(new_params)
        if requests:
            result['requests_count'] = len(requests)
    except Error as e:
        module.fail_json(msg=e.msg, **result)
    except Exception as e:
        trace = format_exc()
        module.fail_json(msg='An unexpected error occurred: {0}'.format(trace), **result)
    result['requests'] = requests
    module.exit_json(**result)

def request_number_list_type(arg_val, params):
    for value in arg_val:
        if value :
            validate_parameters_based_on_regex(str(value),'^[0-9]{2,}$')
    return arg_val

def system_type(arg_val, params):
    if arg_val and arg_val!='*':
        arg_val = arg_val.strip('*')
    value=arg_val
    regex='^[a-zA-Z0-9]{1,8}$'
    validate_parameters_based_on_regex(value,regex)
    return arg_val

def message_id_type(arg_val, params):
    if arg_val and arg_val!='*':
        arg_val = arg_val.strip('*')
    value=arg_val
    regex='^[a-zA-Z0-9]{1,8}$'
    validate_parameters_based_on_regex(value,regex)
    return arg_val

def jobname_type(arg_val, params):
    if arg_val and arg_val!='*':
        arg_val = arg_val.strip('*')
    value=arg_val
    regex='^[a-zA-Z0-9]{1,8}$'
    validate_parameters_based_on_regex(value,regex)
    return arg_val


def validate_parameters_based_on_regex(value,regex):
    pattern = re.compile(regex)
    if pattern.search(value):
        pass
    else:
        raise ValidationError(str(value))
    return value



def find_required_request(params):
    merged_list = create_merge_list()
    requests = filter_requests(merged_list,params)
    if requests:
        pass
    else:
        message='There is no such request given the condition, check your command or update your filter'
        raise OperatorCmdError(message)
    return requests

def create_merge_list():
    operator_cmd_a = 'd r,a,s'
    operator_cmd_b = 'd r,a,jn'
    message_a = execute_command(operator_cmd_a)
    message_b = execute_command(operator_cmd_b)
    list_a = parse_result_a(message_a)
    list_b = parse_result_b(message_b)
    merged_list = merge_list(list_a,list_b)
    return merged_list

def filter_requests(merged_list,params):
    request_number_list = params.get('request_number_list')
    system = params.get('system')
    message_id = params.get('message_id')
    jobname = params.get('jobname')
    newlist=[]
    if request_number_list:
        for number in request_number_list:
            for dict in merged_list:
                if dict.get('number') == str(number):
                    newlist.append(dict)
                    break
    else:
        newlist = merged_list
    if system:
        newlist = handle_conditions(newlist,'system',system.upper().strip('*'))
    if jobname:
        newlist = handle_conditions(newlist,'jobname',jobname.upper().strip('*'))
    if message_id:
        newlist = handle_conditions(newlist,'message_id',message_id.upper().strip('*'))
    return newlist

def handle_conditions(list,condition_type,condition_values):
    regex = re.compile(condition_values)
    newlist = []
    for dict in list:
        exist = regex.search(dict.get(condition_type))
        if exist:
            newlist.append(dict)
    return newlist

def execute_command(operator_cmd):
    rc_message = OperatorCmd.execute(operator_cmd)
    rc = rc_message.get('rc')
    message = rc_message.get('message')
    if rc > 0:
        raise OperatorCmdError(message.split('\n'))
    return message

def parse_result_a(result):
    dict_temp = {}
    list = []
    request_temp=''
    end_flag = False
    lines = result.split('\n')
    regex = re.compile(r'\s+')

    for index,line in enumerate(lines):
        line = line.strip()
        pattern_without_job_id = re.compile(r'\s*[0-9]{2,}\s[A-Z]{1}\s[a-zA-Z0-9]{1,8}')
        pattern_with_job_id = re.compile(r'\s*[0-9]{2,}\s[A-Z]{1}\s[A-Z0-9]{1,8}\s+[A-Z0-9]{1,8}\s')
        m = pattern_without_job_id.search(line)
        n = pattern_with_job_id.search(line)

        if index == (len(lines)-1):
            endflag = True
        if n or m or end_flag:
            if request_temp:
                dict_temp['message_text']=request_temp
                list.append(dict_temp)
                request_temp=''
                dict_temp = {}
            if n:
                elements = regex.split(line,4)
                dict_temp = {'number':elements[0],'type':elements[1],'system':elements[2],'job_id':elements[3]}
                request_temp = elements[4].strip()
                continue
            if m:
                elements = line.split(' ',3)
                dict_temp = {'number':elements[0],'type':elements[1],'system':elements[2]}
                request_temp = elements[3].strip()
                continue
        else:
            if request_temp:
                request_temp = request_temp +' '+line
    return list


def parse_result_b(result):
    # using d r,a,jn
    dict_temp = {}
    list = []
    lines = result.split('\n')
    regex = re.compile(r'\s+')
    for index,line in enumerate(lines):
        line = line.strip()
        pattern_with_jobname = re.compile(r'\s*[0-9]{2,}\s[A-Z]{1}\s[A-Z0-9]{1,8}\s+')
        m = pattern_with_jobname.search(line)
        if m:
            elements = regex.split(line,5)
            # 215 R IM5GCONN *215 HWSC0000I *IMS CONNECT READY*  IM5GCONN
            dict_temp = {'number':elements[0],'jobname':elements[2],'message_id':elements[4]}
            list.append(dict_temp)
            continue
    return list

def merge_list(list_a,list_b):
    merged_list = []
    for dict_a in list_a:
        for dict_b in list_b:
            if dict_a.get('number') == dict_b.get('number'):
                dict_z = dict_a.copy()
                dict_z.update(dict_b)
                merged_list.append(dict_z)
    return merged_list


class Error(Exception):
    pass

class ValidationError(Error):
    def __init__(self, message):
        self.msg = 'An error occurred during validate the input parameters: "{0}"'.format(message)

class OperatorCmdError(Error):
    def __init__(self, message):
        self.msg = 'An error occurred during issue the operator command, the response is "{0}"'.format(message)


def main():
    run_module()

if __name__ == '__main__':
    main()