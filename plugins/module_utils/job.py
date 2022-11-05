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

import re
from time import sleep
from timeit import default_timer as timer
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

try:
    from zoautil_py.jobs import read_output, list_dds, listing
except Exception:
    read_output = MissingZOAUImport()
    list_dds = MissingZOAUImport()
    listing = MissingZOAUImport()

JOB_ERROR_MESSAGES = ["ABEND", "SEC ERROR", "JCL ERROR", "JCLERR"]


def job_output(job_id=None, owner=None, job_name=None, dd_name=None, duration=0, timeout=0, start_time=timer()):
    """Get the output from a z/OS job based on various search criteria.

    Keyword Arguments:
        job_id {str} -- The job ID to search for (default: {None})
        owner {str} -- The owner of the job (default: {None})
        job_name {str} -- The job name search for (default: {None})
        dd_name {str} -- The data definition to retrieve (default: {None})

    Returns:
        list[dict] -- The output information for a list of jobs matching specified criteria.
        If no job status is found it will return a ret_code diction with
        parameter 'msg_txt" = "The job could not be found.
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

    job_detail = _get_job_status(job_id=job_id, owner=owner, job_name=job_name,
                                 dd_name=dd_name, duration=duration, timeout=timeout, start_time=start_time)

    while ((job_detail is None or len(job_detail) == 0) and duration <= timeout):
        current_time = timer()
        duration = round(current_time - start_time)
        sleep(1)

    if len(job_detail) == 0:
        # some systems have issues with "*" while some require it to see results
        job_id = "" if job_id == "*" else job_id
        owner = "" if owner == "*" else owner
        job_name = "" if job_name == "*" else job_name
        job_detail = _get_job_status(job_id=job_id, owner=owner, job_name=job_name,
                                     dd_name=dd_name, duration=duration, timeout=timeout, start_time=start_time)
    return job_detail


def _job_not_found(job_id, owner, job_name, dd_name):
    # Note that the text in the msg_txt is used in test cases thus sensitive to change
    jobs = []

    job = {}

    job["job_id"] = job_id
    job["job_name"] = job_name
    job["subsystem"] = None
    job["system"] = None
    job["owner"] = owner

    job["ret_code"] = {}
    job["ret_code"]["msg"] = None
    job["ret_code"]["code"] = None
    job["ret_code"]["msg_code"] = None
    job["ret_code"]["msg_txt"] = "The job could not be found."

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
        If no job status is found it will return a ret_code diction with
        parameter 'msg_txt" = "The job could not be found."

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

    job_status_result = _get_job_status(job_id, owner, job_name, dd_name)

    if len(job_status_result) == 0:
        job_id = "" if job_id == "*" else job_id
        job_name = "" if job_name == "*" else job_name
        owner = "" if owner == "*" else owner
        job_status_result = _get_job_status(job_id, owner, job_name, dd_name)

    return job_status_result


def _parse_steps(job_str):
    """Parse the dd section of output to retrieve step-wise CC's

    Args:
        job_str (str): The content for a given dd.

    Returns:
        list[dict]: A list of step names listed as "step executed" the related CC.
    """
    stp = []
    if "STEP WAS EXECUTED" in job_str:
        steps = re.findall(
            r"(.*?)\s-\sSTEP\sWAS\sEXECUTED\s-\s(.*?)\n", job_str)
        for match in steps:
            st = {
                "step_name": match[0].split()[-1],
                "step_cc": int(match[1].split()[-1]) if match[1].split()[-1] is not None else None,
            }
            stp.append(st)

    return stp


def _get_job_status(job_id="*", owner="*", job_name="*", dd_name=None, duration=0, timeout=0, start_time=timer()):
    if job_id == "*":
        job_id_temp = None
    else:
        # Preserve the original job_id for the failure path
        job_id_temp = job_id

    # jls output: owner=job[0], name=job[1], id=job[2], status=job[3], rc=job[4]
    # e.g.: OMVSADM  HELLO    JOB00126 JCLERR   ?
    # listing(job_id, owner) in 1.2.0 has owner param, 1.1 does not

    final_entries = []
    entries = listing(job_id=job_id_temp)

    while ((entries is None or len(entries) == 0) and duration <= timeout):
        current_time = timer()
        duration = round(current_time - start_time)
        sleep(1)
        entries = listing(job_id=job_id_temp)

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
            # In the event entry.rc is in the JOB_ERROR_MESSAGES don't propagate it, its likely
            # a JCL Syntax error that should not have an RC associated (ZOAU ISSUE)
            job["ret_code"]["msg_code"] = entry.rc if entry.status not in JOB_ERROR_MESSAGES else None
            job["ret_code"]["code"] = ""
            if len(entry.rc) > 0:
                if entry.rc.isdigit():
                    job["ret_code"]["code"] = int(entry.rc) if entry.status not in JOB_ERROR_MESSAGES else None
            job["ret_code"]["msg_text"] = entry.status

            job["class"] = ""
            job["content_type"] = ""
            job["ret_code"]["steps"] = []
            job["ddnames"] = []

            list_of_dds = list_dds(entry.id)
            while ((list_of_dds is None or len(list_of_dds) == 0) and duration <= timeout):
                current_time = timer()
                duration = round(current_time - start_time)
                sleep(1)
                list_of_dds = list_dds(entry.id)

            for single_dd in list_of_dds:
                dd = {}

                # If dd_name not None, only that specific dd_name should be returned
                if dd_name is not None:
                    if dd_name not in single_dd["dataset"]:
                        continue
                    else:
                        dd["ddname"] = single_dd["dataset"]

                if "dataset" not in single_dd:
                    continue

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
                        tmpcont = read_output(
                            entry.id, single_dd["stepname"], single_dd["dataset"])

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
                        job["system"] = (tmptext.split(
                            "--", 1)[0]).replace(" ", "")

                if len(job["subsystem"]) < 1:
                    if "--  N O D E " in tmpcont:
                        tmptext = tmpcont.split("--  N O D E ")[1]
                        job["subsystem"] = (tmptext.split("\n")[
                                            0]).replace(" ", "")

                # e.g "19.49.44 JOB06848 IEFC452I DOCEASYT - JOB NOT RUN - JCL ERROR 029 "
                # we extract out 'JCL ERROR 029' after the split
                if job["ret_code"]["msg_code"] == "?":
                    if "JOB NOT RUN -" in tmpcont:
                        tmptext = tmpcont.split(
                            "JOB NOT RUN -")[1].split("\n")[0]
                        job["ret_code"]["msg"] = tmptext.strip()
                        job["ret_code"]["msg_code"] = tmptext.split(
                            " ")[-1].strip()

                        job["ret_code"]["code"] = ""
                        if len(job["ret_code"]["msg_code"]) > 0:
                            if job["ret_code"]["msg_code"].isdigit():
                                job["ret_code"]["code"] = int(
                                    job["ret_code"]["msg_code"])
            if len(list_of_dds) > 1:
                # This should really only be returned for job submit but the code
                # is used job_output as well, for now we can ignore this point unless
                # we want to offer a wait_time_s for job output which might be reasonable
                job["duration"] = duration
                final_entries.append(job)
    if not final_entries:
        final_entries = _job_not_found(job_id, owner, job_name, "unavailable")
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
