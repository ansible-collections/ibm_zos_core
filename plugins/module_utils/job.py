# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from tempfile import NamedTemporaryFile
from os import chmod, path, remove
import json
import re

def job_output(module, job_id='', owner='', job_name='', dd_name=''):
    """Get the output from a z/OS job based on various search criteria.

    Arguments:
        module {AnsibleModule} -- The AnsibleModule object from the running module.

    Keyword Arguments:
        job_id {str} -- The job ID to search for (default: {''})
        owner {str} -- The owner of the job (default: {''})
        job_name {str} -- The job name search for (default: {''})
        dd_name {str} -- The data definition to retrieve (default: {''})

    Raises:
        RuntimeError: When job output cannot be retrieved successfully but job exists.
        RuntimeError: When no job output is found

    Returns:
        dict[str, list[dict]] -- The output information for a given job.
    """
    job_detail_json = {}
    rc, out, err = _get_job_json_str(module, job_id, owner, job_name, dd_name)
    if rc != 0:
        raise RuntimeError(
            'Failed to retrieve job output. RC: {} Error: {}'.format(str(rc), str(err)))
    if not out:
        raise RuntimeError(
            'Failed to retrieve job output. No job output found.')
    job_detail_json = json.loads(out, strict=False)
    for job in job_detail_json.get('jobs'):
        job['ret_code'] = {} if job.get('ret_code') == None else job.get('ret_code')
        job['ret_code']['code'] = _get_return_code_num(job.get('ret_code', {}).get('msg', ''))
        job['ret_code']['msg_code'] = _get_return_code_str(job.get('ret_code', {}).get('msg', ''))
        job['ret_code']['msg_txt'] = ''
    return job_detail_json


def _get_job_json_str(module, job_id='', owner='', job_name='', dd_name=''):
    """Generate JSON output string containing Job info from SDSF.
    Writes a temporary REXX script to the USS filesystem to gather output.

    Arguments:
        module {AnsibleModule} -- The AnsibleModule object from the running module.

    Keyword Arguments:
        job_id {str} -- The job ID to search for (default: {''})
        owner {str} -- The owner of the job (default: {''})
        job_name {str} -- The job name search for (default: {''})
        dd_name {str} -- The data definition to retrieve (default: {''})

    Returns:
        tuple[int, str, str] -- RC, STDOUT, and STDERR from the REXX script.
    """
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
    linecount = 0
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
    Say '"'||'content_type'||'":"'||value('JTYPE'||"."||ix)||'",'
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
        Say '"'||'record_count'||'":"'||value('JDS_RECCNT'||"."||jx)||'",'
        Say '"'||'id'||'":"'||value('JDS_DSID'||"."||jx)||'",'
        Say '"'||'stepname'||'":"'||value('JDS_STEPN'||"."||jx)||'",'
        Say '"'||'procstep'||'":"'||value('JDS_PROCS'||"."||jx)||'",'
        Say '"'||'byte_count'||'":"'||value('JDS_BYTECNT'||"."||jx)||'",'
        Say '"'||'content'||'":['
        Address SDSF "ISFBROWSE ST TOKEN('"token.ix"')"
        untilline = linecount + JDS_RECCNT.jx
        startingcount = linecount + 1
        do kx=linecount+1 to  untilline
            if kx<>startingcount then do
            Say ','
            end
            linecount = linecount + 1
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
        dirname, scriptname = _write_script(get_job_detail_json_rexx)
        if dd_name is None or dd_name == '?':
            dd_name = ''
        jobid_param = 'jobid=' + job_id
        owner_param = 'owner=' + owner
        jobname_param = 'jobname=' + job_name
        ddname_param = 'ddname=' + dd_name
        cmd = [dirname + '/' + scriptname, jobid_param, owner_param,
               jobname_param, ddname_param]

        rc, out, err = module.run_command(args=" ".join(cmd),
                                          cwd=dirname,
                                          use_unsafe_shell=True)
    except Exception:
        raise
    finally:
        remove(dirname + "/" + scriptname)
    return rc, out, err


def _write_script(content):
    """Write a script to the filesystem.
    This includes writing and setting the execute bit.

    Arguments:
        content {str} -- The contents of the script

    Returns:
        tuple[str, str] -- The directory and script names
    """
    delete_on_close = False
    try:
        tmp_file = NamedTemporaryFile(delete=delete_on_close)
        with open(tmp_file.name, 'w') as f:
            f.write(content)
        chmod(tmp_file.name, 0o755)
        dirname = path.dirname(tmp_file.name)
        scriptname = path.basename(tmp_file.name)
    except Exception:
        remove(tmp_file)
        raise
    return dirname, scriptname

def _get_return_code_num(rc_str):
    """Parse an integer return code from
    z/OS job output return code string.
    
    Arguments:
        rc_str {str} -- The return code message from z/OS job log (eg. "CC 0000")
    
    Returns:
        Union[int, NoneType] -- Returns integer RC if possible, if not returns NoneType
    """
    rc = None
    match = re.search(r'\s*CC\s*([0-9]+)', rc_str)
    if match:
        rc = int(match.group(1))
    return rc

def _get_return_code_str(rc_str):
    """Parse an intestrger return code from
    z/OS job output return code string.
    
    Arguments:
        rc_str {str} -- The return code message from z/OS job log (eg. "CC 0000" or "ABEND")
    
    Returns:
        Union[str, NoneType] -- Returns string RC or ABEND code if possible, if not returns NoneType
    """
    rc = None
    match = re.search(r'(?:\s*CC\s*([0-9]+))|(?:ABEND\s*((?:S|U)[0-9]+))', rc_str)
    if match:
        rc = match.group(1) or match.group(2)
    return rc