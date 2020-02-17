# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from tempfile import NamedTemporaryFile
from os import chmod, path, remove
import json


def job_output(module, job_id='', owner='', job_name='', dd_name=''):
    job_detail_json = {}
    rc, out, err = _get_job_json_str(module, job_id, owner, job_name, dd_name)
    if rc != 0:
        raise RuntimeError(
            'Failed to retrieve job output. RC: {} Error: {}'.format(str(rc), str(err)))
    if not out:
        raise RuntimeError(
            'Failed to retrieve job output. No job output found.')
    job_detail_json = json.loads(out, strict=False)
    return job_detail_json


def _get_job_json_str(module, job_id='', owner='', job_name='', dd_name=''):
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
