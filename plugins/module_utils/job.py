# Copyright (c) IBM Corporation 2019, 2020
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

from tempfile import NamedTemporaryFile
from os import chmod
from stat import S_IEXEC, S_IREAD, S_IWRITE
import re
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper,
)
from zoautil_py.jobs import listing, read_output, list_dds


def job_output(job_id=None, owner=None, job_name=None, dd_name=None):
    """Get the output from a z/OS job based on various search criteria.

    Keyword Arguments:
        job_id {str} -- The job ID to search for (default: {None})
        owner {str} -- The owner of the job (default: {None})
        job_name {str} -- The job name search for (default: {None})
        dd_name {str} -- The data definition to retrieve (default: {None})

    Returns:
        list[dict] -- The output information for a list of jobs matching specified criteria.
        If no job status is found, this will return an empty job code with msg=JOB NOT FOUND
    """
    arg_defs = dict(
        job_id=dict(arg_type="qualifier_pattern"),
        owner=dict(arg_type="qualifier_pattern"),
        job_name=dict(arg_type="qualifier_pattern"),
        dd_name=dict(arg_type=_ddname_pattern),
    )

    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args(
        {"job_id": job_id, "owner": owner, "job_name": job_name, "dd_name": dd_name}
    )

    job_id = parsed_args.get("job_id") or "*"
    job_name = parsed_args.get("job_name") or "*"
    owner = parsed_args.get("owner") or "*"
    dd_name = parsed_args.get("ddname") or ""

    job_detail = _zget_job_status(job_id=job_id, owner=owner, job_name=job_name)
    if len(job_detail) == 0:
        # some systems have issues with "*" while some require it to see results
        job_id = "" if job_id == "*" else job_id
        owner = "" if owner == "*" else owner
        job_name = "" if job_name == "*" else job_name
        job_detail = _zget_job_status(job_id=job_id, owner=owner, job_name=job_name)
    return job_detail


def _job_not_found(job_id, owner, job_name, dd_name, ovrr=None):
    jobs = []

    job = {}

    job["job_id"] = job_id
    job["job_name"] = job_name
    job["subsystem"] = None
    job["system"] = None
    job["owner"] = None

    job["ret_code"] = {}
    job["ret_code"]["msg"] = "JOB NOT FOUND"
    job["ret_code"]["code"] = None
    job["ret_code"]["msg_code"] = "NOT FOUND"
    job["ret_code"]["msg_txt"] = "The job could not be found"

    job["class"] = ""
    job["content_type"] = ""

    job["ddnames"] = []
    dd = {}
    dd["ddname"] = dd_name
    dd["record_count"] = "0"
    dd["id"] = ""
    dd["stepname"] = None
    dd["procstep"] = ""
    dd["byte_count"] = "0"
    job["ddnames"].append(dd)

    if ovrr is not None:
        job["ret_code"]["msg"] = "NO JOBS FOUND"
        job["ret_code"]["msg_code"] = "NOT FOUND"
        job["ret_code"]["msg_txt"] = "No jobs returned from query"

    jobs.append(job)

    return jobs


def job_status(job_id=None, owner=None, job_name=None):
    """Get the status information of a z/OS job based on various search criteria.

    Keyword Arguments:
        job_id {str} -- The job ID to search for (default: {None})
        owner {str} -- The owner of the job (default: {None})
        job_name {str} -- The job name search for (default: {None})

    Returns:
        list[dict] -- The status information for a list of jobs matching search criteria.
        If no job status is found, this will return an empty job code with msg=JOB NOT FOUND
        new format: Job(owner=job[0], name=job[1], id=job[2], status=job[3], rc=job[4]))
    """
    arg_defs = dict(
        job_id=dict(arg_type="qualifier_pattern"),
        owner=dict(arg_type="qualifier_pattern"),
        job_name=dict(arg_type="qualifier_pattern"),
    )

    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args(
        {"job_id": job_id, "owner": owner, "job_name": job_name}
    )

    job_id = parsed_args.get("job_id") or "*"
    job_name = parsed_args.get("job_name") or "*"
    owner = parsed_args.get("owner") or "*"

    job_status = _zget_job_status(job_id, owner, job_name)
    if len(job_status) == 0:
        job_id = "" if job_id == "*" else job_id
        job_name = "" if job_name == "*" else job_name
        owner = "" if owner == "*" else owner
        job_status = _zget_job_status(job_id, owner, job_name)

    return job_status

def _parse_steps(job_str):
    """Parse the dd section of output to retrieve step-wise CC's

    Args:
        job_str (str): The content for a given dd.

    Returns:
        list[dict]: A list of step names listed as "step executed" the related CC.
    """
    stp = []
    if "STEP WAS EXECUTED" in job_str:
        pile = re.findall(r"(.*?)\s-\sSTEP\sWAS\sEXECUTED\s-\s(.*?)\n", job_str)
        for match in pile:
            st = {
                "step_name": match[0].split()[-1],
                "step_cc": match[1].split()[-1],
            }
            stp.append(st)

    return stp

def _zget_job_status(job_id="*", owner="*", job_name="*"):
    if job_id == "*":
        job_query = None
    else:
        job_query = job_id

    entries = listing(job_query, owner)

    final_entries = []
    if entries:
        # jls output: owner=job[0], name=job[1], id=job[2], status=job[3], rc=job[4]
        # e.g.: OMVSADM  HELLO    JOB00126 JCLERR   ?
        for entry in entries:
            if owner != "*":
                if owner != entry.owner:
                    continue
            if job_name != "*":
                if job_name != entry.name:
                    continue

            job = {}

            job["job_id"] = entry.id
            job["job_name"] = entry.name
            job["subsystem"] = ""
            job["system"] = ""
            job["owner"] = entry.owner

            job["ret_code"] = {}
            job["ret_code"]["msg"] = entry.status + " " + entry.rc
            job["ret_code"]["msg_code"] = entry.rc

            job["ret_code"]["code"] = ""
            if len(entry.rc) > 0:
                if entry.rc.isdigit():
                    job["ret_code"]["code"] = int(entry.rc)

            job["ret_code"]["msg_text"] = entry.status

            job["class"] = ""
            job["content_type"] = ""

            job["ret_code"]["steps"] = []
            job["ddnames"] = []
            list_of_dds = list_dds(entry.id)

            for single_dd in list_of_dds:
                dd = {}

                dd["ddname"] = single_dd["dataset"]
                dd["record_count"] = single_dd["recnum"]
                dd["id"] = single_dd["dsid"]
                dd["stepname"] = single_dd["stepname"]
                if "procstep" in single_dd:
                    dd["procstep"] = single_dd["procstep"]
                else:
                    dd["proctep"] = None
                dd["byte_count"] = single_dd["length"]
                tmpcont = read_output( entry.id, single_dd["stepname"], single_dd["dataset"])
                dd["content"] = tmpcont.split( "\n" )
                job["ret_code"]["steps"].extend(_parse_steps(tmpcont))

                job["ddnames"].append(dd)
                if len(job["class"]) < 1:
                    if "- CLASS " in tmpcont:
                        tmptext = tmpcont.split("- CLASS ")[1]
                        job["class"] = tmptext.split(" ")[0]

                if len(job["system"]) < 1:
                    if "- SYS " in tmpcont:
                        tmptext = tmpcont.split("- SYS ")[1]
                        job["system"] = (tmptext.split()[0]).replace(" ", "")

                if len(job["subsystem"]) < 1:
                    if "--  N O D E " in tmpcont:
                        tmptext = tmpcont.split("--  N O D E ")[1]
                        job["subsystem"] = (tmptext.split()[0]).replace(" ", "")



            final_entries.append(job)

    if not final_entries:
        final_entries = _job_not_found(job_id, owner, job_name, "notused")

    return final_entries

def _ddname_pattern(contents, resolve_dependencies):
    """Resolver for ddname_pattern type arguments

    Arguments:
        contents {bool} -- The contents of the argument.
        resolved_dependencies {dict} -- Contains all of the dependencies and their contents,
        which have already been handled,
        for use during current arguments handling operations.

    Raises:
        ValueError: When contents is invalid argument type

    Returns:
        str -- The arguments contents after any necessary operations.
    """
    if not re.fullmatch(
        r"^(?:[A-Z]{1}[A-Z0-9]{0,7})|(?:\?{1})$",
        str(contents),
        re.IGNORECASE,
    ):
        raise ValueError(
            'Invalid argument type for "{0}". expected "ddname_pattern"'.format(
                contents
            )
        )
    return str(contents)
