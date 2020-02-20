# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: zos_job_output
short_description: Display z/OS job output for a given criteria (Job id/Job name/owner) with or without a data definition name as a filter.
description:
    - Display the z/OS job output for a given criteria (Job id/Job name/owner) with/without a data definition name as a filter.
    - At least provide a job id/job name/owner.
    - The job id can be specific such as "STC02560", or one that uses a pattern such as "STC*" or "*".
    - The job name can be specific such as "TCPIP", or one that uses a pattern such as "TCP*" or "*".
    - The owner can be specific such as "IBMUSER", or one that uses a pattern like "*".
    - If there is no ddname, or if ddname="?", output of all the ddnames under the given job will be displayed.
version_added: "2.9"
author: "Jack Ho <jack.ho@ibm.com>"
options:
    job_id:
        description:
            - job Id. (e.g "STC02560", "STC*")
        type: str
        required: false
        version_added: "2.9"
    job_name:
        description:
            - job name. (e.g "TCPIP", "C*")
        required: false
        version_added: "2.9"
    owner:
        description:
            - The owner who runs job. (e.g "IBMUSER", "*")
        required: false
        version_added: "2.9"
    ddname:
        description:
            - Data definition name. (e.g "JESJCL", "?")
        type: str
        required: false
        version_added: "2.9"
'''
EXAMPLES = r'''
- name: Job output with ddname
  zos_job_output:
    job_id: "STC02560"
    ddname: "JESMSGLG"

- name: JES Job output without ddname
  zos_job_output:
    job_id: "STC02560"

- name: JES Job output with all ddnames
  zos_job_output:
    job_id: "STC*"
    job_name: "*"
    owner: "IBMUSER"
    ddname: "?"
'''
RETURN = '''
<<<<<<< HEAD
zos_job_output:
=======
jobs:
>>>>>>> master
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
<<<<<<< HEAD
        content-type:
=======
        content_type:
>>>>>>> master
            description: content type
            type: str
        ddnames:
            description: list of data definition name
            type: list[dict]
            contains:
                ddname:
                    description: data definition name
                    type: str
<<<<<<< HEAD
                record-count:
=======
                record_count:
>>>>>>> master
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
<<<<<<< HEAD
                byte-count:
=======
                byte_count:
>>>>>>> master
                    description: byte count
                    type: int
                content:
                    description: ddname content
                    type: list[str]
<<<<<<< HEAD
=======
        ret_code:
            description: return code output taken directly from job log
            type: dict
            contains:
                msg:
                    description: Holds the return code (eg. "CC 0000")
                    type: str
                msg_code: 
                    description: Holds the return code string (eg. "00", "S0C4")
                    type: str
                msg_txt: 
                    description: Holds additional information related to the job that may be useful to the user.
                    type: str
                code: 
                    description: return code converted to integer value (when possible)
                    type: int
changed:
  description: Indicates if any changes were made during module operation
  type: bool
>>>>>>> master
'''

import json
from ansible.module_utils.basic import AnsibleModule
<<<<<<< HEAD
=======
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.job import job_output
>>>>>>> master
from os import chmod, path, remove
from tempfile import NamedTemporaryFile


<<<<<<< HEAD
def get_job_json(jobid, owner, jobname, ddname, module):
    get_job_detail_json_rexx = """/* REXX */
arg options
parse var options param
upper param
parse var param 'JOBID=' jobid ' OWNER=' owner,
  ' JOBNAME=' jobname ' DDNAME=' ddname

rc=isfcalls('ON')

jobid = strip(jobid,'L')
if (jobid <> '') then do
  ISFFILTER='JobID EQ '||jobid
end
owner = strip(owner,'L')
if (owner <> '') then do
  ISFOWNER=owner
end
jobname = strip(jobname,'L')
if (jobname <> '') then do
  ISFPREFIX=jobname
end
ddname = strip(ddname,'L')
if (ddname == '?') then do
  ddname = ''
end

Address SDSF "ISFEXEC ST (ALTERNATE DELAYED)"
if rc<>0 then do
  Say '{"jobs":[]}'
  Exit 0
end

if isfrows == 0 then do
  Say '{"jobs":[]}'
end
else do
  Say '{"jobs":['
  do ix=1 to isfrows
    if ix<>1 then do
      Say ','
    end
    Say '{'
    Say '"'||'job_id'||'":"'||value('JOBID'||"."||ix)||'",'
    Say '"'||'job_name'||'":"'||value('JNAME'||"."||ix)||'",'
    Say '"'||'subsystem'||'":"'||value('ESYSID'||"."||ix)||'",'
    Say '"'||'owner'||'":"'||value('OWNERID'||"."||ix)||'",'
    Say '"'||'ret_code'||'":{"'||'msg'||'":"'||value('RETCODE'||"."||ix)||'"},'
    Say '"'||'class'||'":"'||value('JCLASS'||"."||ix)||'",'
    Say '"'||'content-type'||'":"'||value('JTYPE'||"."||ix)||'",'
    Say '"'||'changed'||'":"'||'false'||'",'
    Say '"'||'failed'||'":"'||'false'||'",'
    Address SDSF "ISFACT ST TOKEN('"TOKEN.ix"') PARM(NP ?)",
"("prefix JDS_
    lrc=rc
    if lrc<>0 | JDS_DDNAME.0 == 0 then do
      Say '"ddnames":[]'
    end
    else do
      Say '"ddnames":['
      do jx=1 to JDS_DDNAME.0
        if jx<>1 & ddname == '' then do
          Say ','
        end
        if ddname == '' | ddname == value('JDS_DDNAME'||"."||jx) then do
          Say '{'
          Say '"'||'ddname'||'":"'||value('JDS_DDNAME'||"."||jx)||'",'
          Say '"'||'record-count'||'":"'||value('JDS_RECCNT'||"."||jx)||'",'
          Say '"'||'id'||'":"'||value('JDS_DSID'||"."||jx)||'",'
          Say '"'||'stepname'||'":"'||value('JDS_STEPN'||"."||jx)||'",'
          Say '"'||'procstep'||'":"'||value('JDS_PROCS'||"."||jx)||'",'
          Say '"'||'byte-count'||'":"'||value('JDS_BYTECNT'||"."||jx)||'",'
          Say '"'||'content'||'":['
          Address SDSF "ISFBROWSE ST TOKEN('"TOKEN.ix"')"
          do kx=1 to isfline.0
            if kx<>1 then do
              Say ','
            end
            Say '"'||escapeNewLine(escapeDoubleQuote(isfline.kx))||'"'
          end
          Say ']'
          Say '}'
        end
      end
      Say ']'
    end
    Say '}'
  end
  Say ']}'
end

rc=isfcalls('OFF')

return 0

escapeDoubleQuote: Procedure
Parse Arg string
out=''
Do While Pos('"',string)<>0
   Parse Var string prefix '"' string
   out=out||prefix||'\\"'
End
Return out||string

escapeNewLine: Procedure
Parse Arg string
Return translate(string, '4040'x, '1525'x)
"""
    try:
        dirname, scriptname = _copy_temp_file(get_job_detail_json_rexx)
        if jobid is None:
            jobid = ''
        if owner is None:
            owner = ''
        if jobname is None:
            jobname = ''
        if ddname is None or ddname == '?':
            ddname = ''
        jobid_param = 'jobid=' + jobid
        owner_param = 'owner=' + owner
        jobname_param = 'jobname=' + jobname
        ddname_param = 'ddname=' + ddname
        cmd = [dirname + '/' + scriptname, jobid_param, owner_param,
               jobname_param, ddname_param]

        rc, out, err = module.run_command(args=_list_to_string(cmd),
                                          cwd=dirname,
                                          use_unsafe_shell=True)
    except Exception:
        raise
    finally:
        remove(dirname + "/" + scriptname)
    return rc, out, err


def _list_to_string(s):
    str1 = " "
    return str1.join(s)


def _copy_temp_file(content):
    delete_on_close = False
    try:
        tmp_file = NamedTemporaryFile(delete=delete_on_close)
        with open(tmp_file.name, 'w') as f:
            f.write(content)
        f.close()
        chmod(tmp_file.name, 0o755)
        dirname = path.dirname(tmp_file.name)
        scriptname = path.basename(tmp_file.name)
    except Exception:
        remove(tmp_file)
        raise
    return dirname, scriptname


=======
>>>>>>> master
def run_module():
    module_args = dict(
        job_id=dict(type='str', required=False),
        job_name=dict(type='str', required=False),
        owner=dict(type='str', required=False),
        ddname=dict(type='str', required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

<<<<<<< HEAD
    job_id = module.params.get("job_id")
    job_name = module.params.get("job_name")
    owner = module.params.get("owner")
    ddname = module.params.get("ddname")

    if job_id is None and job_name is None and owner is None:
        module.fail_json(msg="Please provide a job_id or job_name or owner")

    job_detail_json = {}
    rc, out, err = get_job_json(job_id, owner,
                                job_name, ddname, module)
    if rc != 0:
        module.fail_json(msg=err, rc=rc)
    if not out:
        module.fail_json(msg="No job output was found.")
    else:
        job_detail_json = json.loads(out, strict=False)

    module.exit_json(zos_job_output=job_detail_json)


class Error(Exception):
    pass
=======
    job_id = module.params.get("job_id") or ""
    job_name = module.params.get("job_name") or ""
    owner = module.params.get("owner") or ""
    ddname = module.params.get("ddname") or ""

    if not job_id and not job_name and not owner:
        module.fail_json(msg="Please provide a job_id or job_name or owner")

    try:
        results = job_output(module, job_id, owner, job_name, ddname)
        results['changed'] = False
    except Exception as e:
        module.fail_json(msg=str(e))
    module.exit_json(**results)
>>>>>>> master


def main():
    run_module()


if __name__ == '__main__':
    main()
