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

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

try:
    from zoautil_py.jobs import listing, read_output, list_dds
except Exception:
    pass


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
    dd_name = parsed_args.get("dd_name") or ""

    job_detail = _zget_job_status(job_id, owner, job_name, dd_name)
    if len(job_detail) == 0:
        # some systems have issues with "*" while some require it to see results
        job_id = "" if job_id == "*" else job_id
        owner = "" if owner == "*" else owner
        job_name = "" if job_name == "*" else job_name
        job_detail = _zget_job_status(job_id, owner, job_name, dd_name)
    return job_detail


def _job_not_found(job_id, owner, job_name, dd_name, ovrr=None):
    jobs = []

    job = {}

    job["job_id"] = job_id
    job["job_name"] = job_name
    job["subsystem"] = None
    job["system"] = None
    job["owner"] = owner

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


def job_status(job_id=None, owner=None, job_name=None, dd_name=None):
    """Get the status information of a z/OS job based on various search criteria.

    Keyword Arguments:
        job_id {str} -- The job ID to search for (default: {None})
        owner {str} -- The owner of the job (default: {None})
        job_name {str} -- The job name search for (default: {None})
        dd_name {str} -- If populated, return ONLY this DD in the job list (default: {None})

    Returns:
        list[dict] -- The status information for a list of jobs matching search criteria.
        If no job status is found, this will return an empty job code with msg=JOB NOT FOUND
    """
    arg_defs = dict(
        job_id=dict(arg_type="qualifier_pattern"),
        owner=dict(arg_type="qualifier_pattern"),
        job_name=dict(arg_type="qualifier_pattern"),
        dd_name=dict(arg_type="str"),
    )

    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args(
        {"job_id": job_id, "owner": owner, "job_name": job_name, "dd_name": dd_name}
    )

    job_id = parsed_args.get("job_id") or "*"
    job_name = parsed_args.get("job_name") or "*"
    owner = parsed_args.get("owner") or "*"
    dd_name = parsed_args.get("dd_name")

    job_status = _zget_job_status(job_id, owner, job_name, dd_name)
    if len(job_status) == 0:
        job_id = "" if job_id == "*" else job_id
        job_name = "" if job_name == "*" else job_name
        owner = "" if owner == "*" else owner
        job_status = _zget_job_status(job_id, owner, job_name, dd_name)

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
        steps = re.findall(r"(.*?)\s-\sSTEP\sWAS\sEXECUTED\s-\s(.*?)\n", job_str)
        for match in steps:
            st = {
                "step_name": match[0].split()[-1],
                "step_cc": match[1].split()[-1],
            }
            stp.append(st)

    return stp


def _zget_job_status(job_id="*", owner="*", job_name="*", dd_name=None):
    if job_id == "*":
        job_query = None
    else:
        job_query = job_id

    # entries = listing(job_query, owner)   1.2.0 has owner paramn, 1.1 does not
    entries = listing(job_query)

    final_entries = []
    if entries:
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
                if dd_name is not None:
                    if dd_name not in single_dd["dataset"]:
                        continue

                if "dataset" not in single_dd:
                    continue

                dd["ddname"] = single_dd["dataset"]
                if "recnum" in single_dd:
                    dd["record_count"] = single_dd["recnum"]
                else:
                    dd["record_count"] = None

                if "dsid" in single_dd:
                    dd["id"] = single_dd["dsid"]
                else:
                    dd["id"] = "?"

                if "stepname" in single_dd:
                    dd["stepname"] = single_dd["stepname"]
                else:
                    dd["stepname"] = None

                if "procstep" in single_dd:
                    dd["procstep"] = single_dd["procstep"]
                else:
                    dd["proctep"] = None

                if "length" in single_dd:
                    dd["byte_count"] = single_dd["length"]
                else:
                    dd["byte_count"] = 0

                tmpcont = None
                if "stepname" in single_dd:
                    if "dataset" in single_dd:
                        tmpcont = read_output(entry.id, single_dd["stepname"], single_dd["dataset"])

                dd["content"] = tmpcont.split("\n")
                job["ret_code"]["steps"].extend(_parse_steps(tmpcont))

                job["ddnames"].append(dd)
                if len(job["class"]) < 1:
                    if "- CLASS " in tmpcont:
                        tmptext = tmpcont.split("- CLASS ")[1]
                        job["class"] = tmptext.split(" ")[0]

                if len(job["system"]) < 1:
                    if "--  S Y S T E M  " in tmpcont:
                        tmptext = tmpcont.split("--  S Y S T E M  ")[1]
                        job["system"] = (tmptext.split("--", 1)[0]).replace(" ", "")

                if len(job["subsystem"]) < 1:
                    if "--  N O D E " in tmpcont:
                        tmptext = tmpcont.split("--  N O D E ")[1]
                        job["subsystem"] = (tmptext.split("\n")[0]).replace(" ", "")

                if job["ret_code"]["msg_code"] == "?":
                    if "JOB NOT RUN -" in tmpcont:
                        tmptext = tmpcont.split("JOB NOT RUN -")[1].split("\n")[0]
                        job["ret_code"]["msg"] = tmptext.strip()
                        job["ret_code"]["msg_code"] = tmptext.split(" ")[-1].strip()

                        job["ret_code"]["code"] = ""
                        if len(job["ret_code"]["msg_code"]) > 0:
                            if job["ret_code"]["msg_code"].isdigit():
                                job["ret_code"]["code"] = int(job["ret_code"]["msg_code"])
            if len(list_of_dds) > 1:
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
