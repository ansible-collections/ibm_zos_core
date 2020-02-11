# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION=r'''
module: zos_job_submit
author: Xiao Yuan Ma <bjmaxy@cn.ibm.com>
short_description: The zos_job_submit module allows you to submit a job and optionally monitor for its execution.
description:
  - Submit JCL from DATS_SET , USS, or LOCAL location.
  - Optionally wait for the job output until the job finishes.
  - For the uncatalogued dataset, specify the volume serial number.
version_added: "2.9"
options:
  src:
    required: true
    description:
      - The source directory or data set containing the JCL to submit. 
      - It could be Physical sequential data set or a partitioned data set qualified 
        by a member or a path. (e.g "USER.TEST","USER.JCL(TEST)")
      - Or an USS file. (e.g "/u/tester/demo/sample.jcl")
      - Or an LOCAL file in ansible control node.(e.g "/User/tester/ansible-playbook/sample.jcl") 
  location:
    required: true
    default: DATA_SET
    choices:
      - DATA_SET
      - USS
      - LOCAL
    description:
      - The JCL location. Usually it's DATA_SET or USS or LOCAL, Default DATA_SET.
      - DATA_SET can be a PDS, PDSE, or sequential data set.
      - LOCAL means locally to the ansible control node.
  wait:
    required: false 
    choices:
      - true
      - false
    description:
      - Wait for the Job to finish and capture the output. Default is false.
      - User can specify the wait time in option duration_s, default is 60s. 
  wait_time_s:
    required: false 
    type: int
    description:
      - When wait is true, the module will wait for a maximum of 60s by default. 
      - User can set the wait time manually in this option. 
  return_output:
    required: false 
    choices:
      - true
      - false 
    description:
      - Whether to print the DD output.
      - If false, null will be returned in ddnames field.
  volume:
    required: false
    description:
      - The volume serial (VOLSER) where the data set resides. The option 
        is required only when the data set is not catalogued on the system. 
        Ignored for USS and LOCAL.
  encoding:
    required: false
    default: UTF-8 
    choices: 
      - UTF-8
      - ASCII
      - ISO-8859-1
      - EBCDIC
      - IBM-037
      - IBM-1047
    description:
      - The encoding of the local file on the ansible control node. 
      - If it is UTF-8, ASCII, ISO-8859-1, the file will be converted to EBCDIC on the z/OS platform. 
      - If it is EBCDIC, IBM-037, IBM-1047, the file will be unchanged when submitted on the z/OS platform. 
'''

RETURN = '''
zos_job_output:
    description: list of job output.
    returned: success
    type: list[dict]
    contains:
        job_id:
            description: job ID
            type: str
        job_name:
            description: job name
            type: str
        subsystem:
            description: subsystem
            type: str
        class:
            description: class
            type: str
        content-type:
            description: content type
            type: str
        ddnames:
            description: list of data definition name
            type: list[dict]
            contains:
                ddname:
                    description: data definition name
                    type: str
                record-count:
                    description: record count
                    type: int
                id:
                    description: id
                    type: str
                stepname:
                    description: step name
                    type: str
                procstep:
                    description: proc step
                    type: str
                byte-count:
                    description: byte count
                    type: int
                content:
                    description: ddname content
                    type: list[str]
'''

RETURN = r'''
jobs:
    description: The list of jobs that matches the job name or job id and optionally the owner
    returned: success
    type: list[dict]
    contains:
       job_name:
          description: job name
          type: str
       job_id:
          description: job name
          type: str
       change:
          description: change
          type: bool
       failed:
          description: failed
          type: bool
       duration:
          description: duration
          type: int
       ddnames:
           description: all ddnames
           type: list[dict]
           contains:
               ddname:
                 description: ddname
                 type: str
               step_name:
                  description: step name
                  type: str
               content:
                  description: conetent
                  type: str
               ret_code: 
                   description: return code
                   type: list[dict]
                   contains:
                      msg:
                        description: contains
                        type: str
                      code:
                        description: code
                        type: str
                      msg_details: 
                        description: message
                        type: str
changed: 
    description: Indicates if any changes were made during module operation
    type: bool  
message:
    description: The output message that the sample module generates
    returned: success
    type: str 

'''

EXAMPLES = r'''
  - name: Submit the JCL 
    zos_job_submit:
       src: TEST.UTILs(SAMPLE)
       location: DATA_SET
       wait: false
       volume:
    register: response
  
  - name: Submit USS job
    zos_job_submit:
        src: /u/tester/demo/sample.jcl
        location: USS
        wait: false
        volume:
        return_output: false
  
  - name: Submit LOCAL job
    zos_job_submit:
      src: /Users/maxy/ansible-playbooks/provision/sample.jcl
      location: LOCAL
      wait: false
      encoding: UTF-8
      volume:
  
  - name: Submit uncatalogued PDS job
    zos_job_submit:
       src: TEST.UNCATLOG.JCL(SAMPLE)
       location: DATA_SET
       wait: false
       volume: P2SS01
  
  - name: Submit long running PDS job, and wait for the job to finish
    zos_job_submit:
       src: TEST.UTILs(LONGRUN)
       location: DATA_SET
       wait: true  
       wait_time_s: 30    

EXAMPLE RESULTS:
     "msg": {
         "jobs":[
      {
         "job_id":"JOB32881",
         "job_name":"TEST",
         "changed":true,
         "failed":false,
         "duration":0,
         "ddnames":[
            {
               "ddname":"JESMSGLG",
               "step_name":"JES2",
               "content":[
                  "J E S 2  J O B  L O G  --  S Y S T E M  M V 2 C  --  N O D E ...."
               ]
            },
            {
               "ddname":"JESJCL",
               "step_name":"JES2",
               "content":[
                  "1 //TEST JOB                       JOB32881"
               ]
            },
            {
               "ddname":"JESYSMSG",
               "step_name":"JES2",
               "content":[
                  "ICH70001I TESTER"
               ]
            }
         ],
         "ret_code":{
            "msg":  "CC 0000" ,
            "code": "0000" ,
            "msg_detail": "Submit JCL operation succeeded",
         },
      },
   ]
'''

from ansible.module_utils.basic import *
from zoautil_py import Jobs
from time import sleep
from os import chmod, path
from tempfile import NamedTemporaryFile
import re

ZOAUTIL_TEMP_USS = "/tmp/ansible-temp-1"
ZOAUTIL_TEMP_USS2 = "/tmp/ansible-temp-2"

"""time between job query checks to see if a job has completed, default 1 second"""
POLLING_INTERVAL = 1
POLLING_COUNT = 60
POLLING_THRESHOLD = 60

def submit_pds_jcl(src):
    """ A wrapper around zoautil_py Jobs submit to raise exceptions on failure. """
    jobId = Jobs.submit(src)
    if jobId == None:
        raise SubmitJCLError('SUBMIT JOB FAILED: ' + 'NO JOB ID IS RETURNED. PLEASE CHECK THE JCL.')
    return jobId


def submit_uss_jcl(src,module):
    """ Submit uss jcl. Use uss command submit -j jclfile. """
    rc, stdout, stderr = module.run_command(['submit', '-j', src])
    if rc != 0:
        raise SubmitJCLError('SUBMIT JOB FAILED:  Stderr :' + stderr)
    if 'Error' in stderr:
        raise SubmitJCLError('SUBMIT JOB FAILED: ' + stderr)
    if 'Not accepted by JES' in stderr:
        raise SubmitJCLError('SUBMIT JOB FAILED: ' + stderr)
    if stdout !=  '':
        jobId = stdout.replace("\n", "").strip()
    else:
        raise SubmitJCLError('SUBMIT JOB FAILED: ' + 'NO JOB ID IS RETURNED. PLEASE CHECK THE JCL.')
    return jobId

def submit_jcl_in_volume(src,vol,module):
    script = """/*REXX*/                                     
ARG P1 P2                                              
ADDRESS TSO                                            
CALL BPXWDYN "ALLOC DA('"P1"') FI(TEST) SHR VOL("P2")" 
ADDRESS MVS "EXECIO * DISKR TEST (STEM A."             
X = SUBMIT('A.')                                       
SAY X                                                  
"""
    rc, stdout, stderr = copy_rexx_and_run(script, src, vol, module)
    if 'Error' in stdout:
        raise SubmitJCLError('SUBMIT JOB FAILED: ' + stdout)
    elif '' == stdout:
        raise SubmitJCLError('SUBMIT JOB FAILED, NO JOB ID IS RETURNED : ' + stdout)
    jobId = stdout.replace("\n", "").strip()
    return jobId

def copy_rexx_and_run(script,src,vol,module):
    delete_on_close = True
    tmp_file = NamedTemporaryFile(delete=delete_on_close)
    with open(tmp_file.name, 'w') as f:
        f.write(script)
    chmod(tmp_file.name, 0o755)
    pathName = path.dirname(tmp_file.name)
    scriptName = path.basename(tmp_file.name)
    rc, stdout, stderr = module.run_command(['./' + scriptName, src, vol], cwd=pathName)
    return rc, stdout, stderr

def get_job_info(jobId, return_output):
    result = dict()
    try:
        output = query_jobs_status(jobId)
    except SubmitJCLError as e:
        raise SubmitJCLError(e.msg)
    dds = Jobs.list_dds(job_id=jobId)
    joboutput = []
    if return_output is True:
        for item in dds:
            dataset = item.get("dataset")
            stepname = item.get("stepname")
            content = Jobs.read_output(jobId, stepname, dataset)
            joboutput.append({
                'stepname': stepname,
                'ddname': dataset,
                'content': content,
            })
        result['ddnames'] = joboutput
    else:
        result['ddnames'] = None

    ret_code = parsing_job(output[0])

    result['job_id'] = jobId
    result['changed'] = True
    result['job_name'] = output[0].get("name")
    result['ret_code'] = ret_code

    return result

def query_jobs_status(jobId):
    timeout = 10
    output = None
    while output == None and timeout > 0:
        try:
            output = Jobs.list(job_id=jobId)
            sleep(1)
            timeout = timeout - 1
        except IndexError:
            pass
        except Exception as e:
            raise SubmitJCLError(str(e) +'''
            The output is ''' + output)
    if output == None and timeout == 0:
        raise SubmitJCLError('THE JOB CAN NOT BE QUERIED FROM JES (TIMEOUT=10s). PLEASE CHECK THE ZOS SYSTEM. IT IS SLOW TO RESPONSE.')
    return output

def parsing_job(job_raw):
    ret_code = {}
    status_raw = job_raw.get('status')
    if 'AC' in status_raw:
        # the job is active
        ret_code = {
            'msg': 'ACTIVE',
            'code': 'null',
            'msg_detail': 'Submit JCL operation succeeded.The job is still running.'
        }
    elif 'CC' in status_raw:
        # status = 'Completed normally'
        ret_code = {
            'msg': status_raw + ' ' + job_raw.get('return'),
            'code': job_raw.get('return'),
            'msg_detail': 'Submit JCL operation succeeded.'
        }
    elif status_raw == 'ABEND':
        # status = 'Ended abnormally'
        ret_code = {
            'msg': status_raw + ' ' + job_raw.get('return'),
            'code': job_raw.get('return'),
            'msg_detail': 'Submit JCL operation succeeded. But the job is ended abnormally.'
        }
    elif 'ABENDU' in status_raw:
        # status = 'Ended abnormally'
        if job_raw.get('return') == '?':
            ret_code = {
                'msg': status_raw,
                'code': status_raw[5:],
                'msg_detail': 'Submit JCL operation succeeded but the job is ended abnormally'
            }
        else:
            ret_code = {
                'msg': status_raw,
                'code': job_raw.get('return'),
                'msg_detail': 'Submit JCL operation succeeded but the job is ended abnormally.'
            }
    elif 'CANCELED' in status_raw:
        # status = status_raw
        ret_code = {
            'msg': status_raw,
            'code': 'null',
            'msg_detail': 'Submit JCL operation succeeded but the job was canceled.'
        }
    elif 'JCLERR' in status_raw:
        ret_code = {
            'msg': 'JCL ERROR',
            'code': 'null',
            'msg_detail': 'Submit JCL operation succeeded but the job has a JCL ERROR.'
        }
    else:
        # status = 'Unknown'
        ret_code = {
            'msg': status_raw,
            'code': job_raw.get('return'),
            'msg_detail': 'Submit JCL operation succeeded. Please check the job status.'
        }

    return ret_code

def run_module():
    location_type = {'DATA_SET', 'USS', 'LOCAL', None}

    module_args = dict(
        src=dict(type='str', required=True),
        wait=dict(type='bool', required=False),
        location=dict(type='str', required=True),
        encoding=dict(type='str', required=False, default='UTF-8'),
        volume=dict(type='str', required=False),
        return_output=dict(type='bool', required=False, default='True'),
        wait_time_s=dict(type='int', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(
        changed=False,
        job_id='',
        job_name='',
        return_code=8,
        ddnames='This is a default job output.',
        duration=0,
        job_status='',
        message=''
    )
    results = dict(
        jobs=[]
    )
    jobs = []

    location = module.params.get("location")
    volume = module.params.get("volume")
    wait = module.params.get("wait")
    src = module.params.get('src')
    return_output = module.params.get('return_output')
    wait_time_s = module.params.get('wait_time_s')

    if wait_time_s is None:
        wait_time_s = POLLING_THRESHOLD
    else:
        if wait_time_s <= 0:
            module.fail_json(msg='The option wait_time_s is not valid it just be greater than 0.', **result)

    DSN_REGEX = r'^(([A-Z]{1}[A-Z0-9]{0,7})([.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}([(]([A-Z]{1}[A-Z0-9]{0,7})[)]){0,1}?$'

    # calculate the job elapse time
    duration = 0
    try:

        if location in location_type:
            if location == 'DATA_SET' or location == None:
                data_set_name_pattern = re.compile(DSN_REGEX, re.IGNORECASE)
                check = data_set_name_pattern.search(src)
                if check:
                    if volume == None or volume == '':
                        jobId = submit_pds_jcl(src)
                    else:
                        jobId = submit_jcl_in_volume(src, volume, module)
                else:
                    module.fail_json(msg='The parameter src for data set is not a valid name pattern. Please check the src input.', **result)
            elif location == 'USS':
                jobId = submit_uss_jcl(src, module)
            else:
                # For local file, it has been copied to the temp directory in action plugin.
                encoding = module.params.get('encoding')
                if encoding == 'EBCDIC' or encoding == 'IBM-037' or encoding == 'IBM-1047':
                    jobId = submit_uss_jcl(ZOAUTIL_TEMP_USS, module)
                elif encoding == 'UTF-8' or encoding == 'ISO-8859-1' or encoding == 'ASCII' or encoding == None:  ## 'UTF-8' 'ASCII' encoding will be converted.
                    (conv_rc, stdout, stderr) = module.run_command('iconv -f ISO8859-1 -t IBM-1047 %s > %s' % (ZOAUTIL_TEMP_USS, ZOAUTIL_TEMP_USS2),
                                                               use_unsafe_shell=True)
                    if conv_rc == 0:
                        jobId = submit_uss_jcl(ZOAUTIL_TEMP_USS2, module)
                    else:
                        module.fail_json(msg='The Local file encoding conversion failed. Please check the source file.'+ stderr, **result)
                else:
                    module.fail_json(msg='The Local file encoding format is not supported. The supported encoding is UTF-8, ASCII, ISO-8859-1, EBCDIC, IBM-037, IBM-1047. Default is UTF-8. ', **result)
        else:
            module.fail_json(msg='Location is not valid. DATA_SET, USS, and LOCAL is supported.', **result)

    except SubmitJCLError as e:
        module.fail_json(msg=e.msg, **result)
    if jobId == None or jobId == '':
        result['job_id'] = jobId
        module.fail_json(msg='JOB ID RETURNED IS None. PLEASE CHECK WHETHER THE JCL IS CORRECT.', **result)

    result['job_id'] = jobId
    if wait==True:
        try:
            waitJob = query_jobs_status(jobId)
        except SubmitJCLError as e:
            module.fail_json(msg=e.msg, **result)
        while waitJob[0].get('status') == "AC":  # AC means in progress
            sleep(1)
            duration = duration + 1
            waitJob = Jobs.list(job_id=jobId)
            if waitJob[0].get('status') == "CC":   # CC means completed
                break
            if duration == wait_time_s:    # Long running task. timeout return
                break

    try:
        result = get_job_info(jobId, return_output)
    except SubmitJCLError as e:
        module.fail_json(msg=e.msg, **result)

    result['duration'] = duration
    if duration == wait_time_s:
        results['message'] = {'msg': 'Submit JCL operation succeeded but it is a long running job. Timeout is '+ str(wait_time_s)+' seconds.'}

    jobs.append(result)
    results['changed'] = True
    results['jobs'] = jobs
    module.exit_json(**results)


class Error(Exception):
    pass


class SubmitJCLError(Error):
    def __init__(self, jobs):
        self.msg = 'An error occurred during submission of jobs "{0}"'.format(jobs)


def main():
    run_module()


if __name__ == '__main__':
    main()
