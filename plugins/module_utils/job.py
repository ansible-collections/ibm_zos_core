# Copyright (c) IBM Corporation 2019, 2020, 2023
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

import fnmatch
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

try:
    from zoautil_py import ZOAU_API_VERSION
except Exception:
    ZOAU_API_VERSION = "1.2.0"


def job_output(job_id=None, owner=None, job_name=None, dd_name=None, duration=0, timeout=0, start_time=timer()):
    """Get the output from a z/OS job based on various search criteria.

    Keyword Arguments:
        job_id (str) -- The job ID to search for (default: {None})
        owner (str) -- The owner of the job (default: {None})
        job_name (str) -- The job name search for (default: {None})
        dd_name (str) -- The data definition to retrieve (default: {None})
        duration (int) -- The time the submitted job ran for
        timeout (int) - how long to wait in seconds for a job to complete
        start_time (int) - time the JCL started its submission

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

    # while ((job_detail is None or len(job_detail) == 0) and duration <= timeout):
    #     current_time = timer()
    #     duration = round(current_time - start_time)
    #     sleep(1)

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
    if job_id != '*' and job_name != '*':
        job_not_found_msg = "{0} with the job_id {1}".format(job_name.upper(), job_id.upper())
    elif job_id != '*':
        job_not_found_msg = "with the job_id {0}".format(job_id.upper())
    else:
        job_not_found_msg = "with the name {0}".format(job_name.upper())
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
    job["ret_code"]["msg_txt"] = "The job {0} could not be found.".format(job_not_found_msg)

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
            note: no routines call job_status with dd_name, so we are speeding this routine with
            'dd_scan=False'

    Returns:
        list[dict] -- The status information for a list of jobs matching search criteria.
        If no job status is found it will return a ret_code diction with
        parameter 'msg_txt" = "The job could not be found."

    """
    arg_defs = dict(
        job_id=dict(arg_type="str"),
        owner=dict(arg_type="qualifier_pattern"),
        job_name=dict(arg_type="str"),
    )

    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args(
        {"job_id": job_id, "owner": owner, "job_name": job_name}
    )

    job_id = parsed_args.get("job_id") or "*"
    job_name = parsed_args.get("job_name") or "*"
    owner = parsed_args.get("owner") or "*"

    job_status_result = _get_job_status(job_id=job_id, owner=owner, job_name=job_name, dd_scan=False)

    if len(job_status_result) == 0:
        job_id = "" if job_id == "*" else job_id
        job_name = "" if job_name == "*" else job_name
        owner = "" if owner == "*" else owner
        job_status_result = _get_job_status(job_id=job_id, owner=owner, job_name=job_name, dd_scan=False)

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


def _get_job_status(job_id="*", owner="*", job_name="*", dd_name=None, dd_scan=True, duration=0, timeout=0, start_time=timer()):
    if job_id == "*":
        job_id_temp = None
    else:
        # Preserve the original job_id for the failure path
        job_id_temp = job_id

    # jls output: owner=job[0], name=job[1], id=job[2], status=job[3], rc=job[4]
    # e.g.: OMVSADM  HELLO    JOB00126 JCLERR   ?
    # listing(job_id, owner) in 1.2.0 has owner param, 1.1 does not
    # jls output has expanded in zoau 1.2.3 and later: jls -l -v shows headers
    # jobclass=job[5] serviceclass=job[6] priority=job[7] asid=job[8]
    # creationdatetime=job[9] queueposition=job[10]
    # starting in zoau 1.2.4, program_name[11] was added.

    # Testing has shown that the program_name impact is minor, so we're removing that option
    # This will also help maintain compatibility with 1.2.3

    final_entries = []
    kwargs = {
        "job_id": job_id_temp,
    }
    entries = listing(**kwargs)

    while ((entries is None or len(entries) == 0) and duration <= timeout):
        current_time = timer()
        duration = round(current_time - start_time)
        sleep(1)
        entries = listing(**kwargs)

    if entries:
        for entry in entries:
            if owner != "*":
                if owner != entry.owner:
                    continue
            if job_name != "*":
                if not fnmatch.fnmatch(entry.name, job_name):
                    continue
            if job_id_temp is not None:
                if not fnmatch.fnmatch(entry.id, job_id):
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
            job["ret_code"]["code"] = None
            if len(entry.rc) > 0:
                if entry.rc.isdigit():
                    job["ret_code"]["code"] = int(entry.rc)
            job["ret_code"]["msg_text"] = entry.status

            # this section only works on zoau 1.2.3/+ vvv

            if ZOAU_API_VERSION > "1.2.2":
                job["job_class"] = entry.job_class
                job["svc_class"] = entry.svc_class
                job["priority"] = entry.priority
                job["asid"] = entry.asid
                job["creation_date"] = str(entry.creation_datetime)[0:10]
                job["creation_time"] = str(entry.creation_datetime)[12:]
                job["queue_position"] = entry.queue_position
            if ZOAU_API_VERSION >= "1.2.4":
                job["program_name"] = entry.program_name

            # this section only works on zoau 1.2.3/+ ^^^

            job["class"] = ""
            job["content_type"] = ""
            job["ret_code"]["steps"] = []
            job["ddnames"] = []

            if dd_scan:
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

                    # Extract similar: "19.49.44 JOB06848 IEFC452I DOCEASYT - JOB NOT RUN - JCL ERROR 029 "
                    # then further reduce down to: 'JCL ERROR 029'
                    if job["ret_code"]["msg_code"] == "?":
                        if "JOB NOT RUN -" in tmpcont:
                            tmptext = tmpcont.split(
                                "JOB NOT RUN -")[1].split("\n")[0]
                            job["ret_code"]["msg"] = tmptext.strip()
                            job["ret_code"]["msg_code"] = None
                            job["ret_code"]["code"] = None
                if len(list_of_dds) > 0:
                    # The duration should really only be returned for job submit but the code
                    # is used job_output as well, for now we can ignore this point unless
                    # we want to offer a wait_time_s for job output which might be reasonable.
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
