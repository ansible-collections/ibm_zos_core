#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2022
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


DOCUMENTATION = r"""
module: zos_job_submit
author:
    - "Xiao Yuan Ma (@bjmaxy)"
    - "Rich Parker (@richp405)"
short_description: Submit JCL
description:
    - Submit JCL from DATA_SET , USS, or LOCAL location.
    - Submit a job and optionally monitor for its execution.
    - Optionally wait for the job output until the job finishes.
    - For the uncataloged dataset, specify the volume serial number.
version_added: "1.0.0"
options:
  src:
    required: true
    type: str
    description:
      - The source file or data set containing the JCL to submit.
      - It could be physical sequential data set or a partitioned data set
        qualified by a member or a path. (e.g "USER.TEST","USER.JCL(TEST)")
      - Or an USS file. (e.g "/u/tester/demo/sample.jcl")
      - Or an LOCAL file in ansible control node.
        (e.g "/User/tester/ansible-playbook/sample.jcl")
  location:
    required: false
    default: DATA_SET
    type: str
    choices:
      - DATA_SET
      - USS
      - LOCAL
    description:
      - The JCL location. Supported options are DATA_SET, USS or LOCAL.
      - DATA_SET can be a PDS, PDSE, or sequential data set.
      - USS means the JCL location is located in UNIX System Services (USS).
      - LOCAL means locally to the ansible control node.
  wait:
    required: false
    default: false
    type: bool
    description:
      - Configuring wait used by the M(zos_operator) module has been
        deprecated and will be removed in ibm.ibm_zos_core collection.
      - Setting this option will yield no change, it is deprecated.
      - Wait for the Job to finish and capture the output. Default is false.
      - When I(wait) is false or absent, the module will wait up to 10 seconds for the job to start,
        but will not wait for the job to complete.
      - If I(wait) is true, User can specify the wait time, see option ``wait_time_s``.
  wait_time_s:
    required: false
    default: 10
    type: int
    description:
      - When I(wait) is true, the module will wait for the number of seconds for Job completion.
      - User can set the wait time manually with this option.
  max_rc:
    required: false
    type: int
    description:
      - Specifies the maximum return code for the submitted job that is allowed
        without failing the M(zos_job_submit) module.
  return_output:
    required: false
    default: true
    type: bool
    description:
      - Whether to print the DD output.
      - If false, an empty list will be returned in the ddnames field.
  volume:
    required: false
    type: str
    description:
      - The volume serial (VOLSER) where the data set resides. The option
        is required only when the data set is not cataloged on the system.
        Ignored for USS and LOCAL.
  encoding:
    description:
      - Specifies which encoding the local JCL file should be converted from
        and to, before submitting the job.
      - If this parameter is not provided, and the z/OS systems default encoding can not be identified,
        the JCL file will be converted from UTF-8 to IBM-1047 by default.
    required: false
    type: dict
    suboptions:
      from:
        description:
          - The character set of the local JCL file; defaults to UTF-8.
          - Supported character sets rely on the target version; the most
            common character sets are supported.
        required: false
        type: str
        default: UTF-8
      to:
        description:
          - The character set to convert the local JCL file to on the remote
            z/OS system; defaults to IBM-1047 when z/OS systems default encoding can not be identified.
          - If not provided, the module will attempt to identify and use the default
            encoding on the z/OS system.
          - Supported character sets rely on the target version; the most
            common character sets are supported.
        required: false
        type: str
        default: IBM-1047
notes:
  - For supported character sets used to encode data, refer to the
    L(documentation,https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html).
"""

RETURN = r"""
jobs:
  description:
     List of jobs output.
     If no job status is found, this will return an empty job code with msg=JOB NOT FOUND.
  returned: success
  type: list
  elements: dict
  contains:
    job_id:
      description:
         The z/OS job ID of the job containing the spool file.
      type: str
      sample: JOB00134
    job_name:
      description:
         The name of the batch job.
      type: str
      sample: HELLO
    duration:
      description: The total lapsed time the JCL ran for.
      type: int
      sample: 0
    ddnames:
      description:
         Data definition names.
      type: list
      elements: dict
      contains:
        ddname:
          description:
             Data definition name.
          type: str
          sample: JESMSGLG
        record_count:
          description:
              Count of the number of lines in a print data set.
          type: int
          sample: 17
        id:
          description:
             The file ID.
          type: str
          sample: 2
        stepname:
          description:
              A step name is name that identifies the job step so that other
              JCL statements or the operating system can refer to it.
          type: str
          sample: JES2
        procstep:
          description:
             Identifies the set of statements inside JCL grouped together to
             perform a particular function.
          type: str
          sample: PROC1
        byte_count:
          description:
              Byte size in a print data set.
          type: int
          sample: 574
        content:
          description:
             The ddname content.
          type: list
          elements: str
          sample:
             [ "         1 //HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,       JOB00134",
               "           //             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM                                ",
               "           //*                                                                             ",
               "           //* PRINT \"HELLO WORLD\" ON JOB OUTPUT                                         ",
               "           //*                                                                             ",
               "           //* NOTE THAT THE EXCLAMATION POINT IS INVALID EBCDIC FOR JCL                   ",
               "           //*   AND WILL CAUSE A JCL ERROR                                                ",
               "           //*                                                                             ",
               "         2 //STEP0001 EXEC PGM=IEBGENER                                                    ",
               "         3 //SYSIN    DD DUMMY                                                             ",
               "         4 //SYSPRINT DD SYSOUT=*                                                          ",
               "         5 //SYSUT1   DD *                                                                 ",
               "         6 //SYSUT2   DD SYSOUT=*                                                          ",
               "         7 //                                                                              "
             ]
    ret_code:
      description:
         Return code output collected from job log.
      type: dict
      contains:
        msg:
          description:
            Return code or abend resulting from the job submission.
          type: str
          sample: CC 0000
        msg_code:
          description:
            Return code extracted from the `msg` so that it can be evaluated.
            For example, ABEND(S0C4) would yield "S0C4".
          type: str
          sample: S0C4
        msg_txt:
          description:
             Returns additional information related to the job.
          type: str
          sample: "JCL Error detected.  Check the data dumps for more information."
        code:
          description:
             Return code converted to integer value (when possible).
             For JCL ERRORs, this will be None.
          type: int
          sample: 00
        steps:
          description:
            Series of JCL steps that were executed and their return codes.
          type: list
          elements: dict
          contains:
            step_name:
              description:
                Name of the step shown as "was executed" in the DD section.
              type: str
              sample: "STEP0001"
            step_cc:
              description:
                The CC returned for this step in the DD section.
              type: str
              sample: "00"
      sample:
        ret_code: {
          "code": 0,
          "msg": "CC 0000",
          "msg_code": "0000",
          "msg_txt": "",
          "steps": [
            { "step_name": "STEP0001",
              "step_cc": "0000"
            },
          ]
        }
  sample:
     [
          {
              "class": "K",
              "content_type": "JOB",
              "ddnames": [
                  {
                      "byte_count": "677",
                      "content": [
                          "1                       J E S 2  J O B  L O G  --  S Y S T E M  S T L 1  --  N O D E  S T L 1            ",
                          "0 ",
                          " 12.50.08 JOB00361 ---- FRIDAY,    13 MAR 2020 ----",
                          " 12.50.08 JOB00361  IRR010I  USERID OMVSADM  IS ASSIGNED TO THIS JOB.",
                          " 12.50.08 JOB00361  ICH70001I OMVSADM  LAST ACCESS AT 12:50:03 ON FRIDAY, MARCH 13, 2020",
                          " 12.50.08 JOB00361  $HASP373 DBDGEN00 STARTED - INIT 15   - CLASS K        - SYS STL1",
                          " 12.50.08 JOB00361  SMF000I  DBDGEN00    C           ASMA90      0000",
                          " 12.50.09 JOB00361  SMF000I  DBDGEN00    L           IEWL        0000",
                          " 12.50.09 JOB00361  $HASP395 DBDGEN00 ENDED - RC=0000",
                          "0------ JES2 JOB STATISTICS ------",
                          "-  13 MAR 2020 JOB EXECUTION DATE",
                          "-           28 CARDS READ",
                          "-          158 SYSOUT PRINT RECORDS",
                          "-            0 SYSOUT PUNCH RECORDS",
                          "-           12 SYSOUT SPOOL KBYTES",
                          "-         0.00 MINUTES EXECUTION TIME"
                      ],
                      "ddname": "JESMSGLG",
                      "id": "2",
                      "procstep": "",
                      "record_count": "16",
                      "stepname": "JES2"
                  },
                  {
                      "byte_count": "2136",
                      "content": [
                          "         1 //DBDGEN00 JOB MSGLEVEL=1,MSGCLASS=E,CLASS=K,                           JOB00361",
                          "           //   LINES=999999,TIME=1440,REGION=0M,                                          ",
                          "           //   MEMLIMIT=NOLIMIT                                                           ",
                          "         2 /*JOBPARM  SYSAFF=*                                                             ",
                          "           //*                                                                             ",
                          "         3 //DBDGEN   PROC MBR=TEMPNAME                                                    ",
                          "           //C        EXEC PGM=ASMA90,                                                     ",
                          "           //             PARM='OBJECT,NODECK,NOLIST'                                      ",
                          "           //SYSLIB   DD DISP=SHR,                                                         ",
                          "           //      DSN=IMSBLD.I15RTSMM.SDFSMAC                                             ",
                          "           //SYSLIN   DD DISP=(NEW,PASS),RECFM=F,LRECL=80,BLKSIZE=80,                      ",
                          "           //         UNIT=SYSDA,SPACE=(CYL,(10,5),RLSE,,)                                 ",
                          "           //SYSUT1   DD DISP=(NEW,DELETE),UNIT=SYSDA,SPACE=(CYL,                          ",
                          "           //         (10,5),,,)                                                           ",
                          "           //SYSPRINT DD SYSOUT=*                                                          ",
                          "           //L        EXEC PGM=IEWL,                                                       ",
                          "           //             PARM='XREF,NOLIST',                                              ",
                          "           //             COND=(0,LT,C)                                                    ",
                          "           //SYSLMOD  DD DISP=SHR,                                                         ",
                          "           //      DSN=IMSTESTL.IMS1.DBDLIB(&MBR)                                          ",
                          "           //SYSLIN   DD DSN=*.C.SYSLIN,DISP=(OLD,DELETE)                                  ",
                          "           //SYSPRINT DD SYSOUT=*                                                          ",
                          "           //*                                                                             ",
                          "           //         PEND                                                                 ",
                          "         4 //DLORD6   EXEC DBDGEN,                                                         ",
                          "           //             MBR=DLORD6                                                       ",
                          "         5 ++DBDGEN   PROC MBR=TEMPNAME                                                    ",
                          "         6 ++C        EXEC PGM=ASMA90,                                                     ",
                          "           ++             PARM='OBJECT,NODECK,NOLIST'                                      ",
                          "         7 ++SYSLIB   DD DISP=SHR,                                                         ",
                          "           ++      DSN=IMSBLD.I15RTSMM.SDFSMAC                                             ",
                          "         8 ++SYSLIN   DD DISP=(NEW,PASS),RECFM=F,LRECL=80,BLKSIZE=80,                      ",
                          "           ++         UNIT=SYSDA,SPACE=(CYL,(10,5),RLSE,,)                                 ",
                          "         9 ++SYSUT1   DD DISP=(NEW,DELETE),UNIT=SYSDA,SPACE=(CYL,                          ",
                          "           ++         (10,5),,,)                                                           ",
                          "        10 ++SYSPRINT DD SYSOUT=*                                                          ",
                          "        11 //SYSIN    DD DISP=SHR,                                                         ",
                          "           //      DSN=IMSTESTL.IMS1.DBDSRC(DLORD6)                                        ",
                          "        12 ++L        EXEC PGM=IEWL,                                                       ",
                          "           ++             PARM='XREF,NOLIST',                                              ",
                          "           ++             COND=(0,LT,C)                                                    ",
                          "        13 ++SYSLMOD  DD DISP=SHR,                                                         ",
                          "           ++      DSN=IMSTESTL.IMS1.DBDLIB(&MBR)                                          ",
                          "           IEFC653I SUBSTITUTION JCL - DISP=SHR,DSN=IMSTESTL.IMS1.DBDLIB(DLORD6)",
                          "        14 ++SYSLIN   DD DSN=*.C.SYSLIN,DISP=(OLD,DELETE)                                  ",
                          "        15 ++SYSPRINT DD SYSOUT=*                                                          ",
                          "           ++*                                                                             "
                      ],
                      "ddname": "JESJCL",
                      "id": "3",
                      "procstep": "",
                      "record_count": "47",
                      "stepname": "JES2"
                  },
                  {
                      "byte_count": "2414",
                      "content": [
                          "  STMT NO. MESSAGE",
                          "         4 IEFC001I PROCEDURE DBDGEN WAS EXPANDED USING INSTREAM PROCEDURE DEFINITION",
                          " ICH70001I OMVSADM  LAST ACCESS AT 12:50:03 ON FRIDAY, MARCH 13, 2020",
                          " IEF236I ALLOC. FOR DBDGEN00 C DLORD6",
                          " IEF237I 083C ALLOCATED TO SYSLIB",
                          " IGD100I 0940 ALLOCATED TO DDNAME SYSLIN   DATACLAS (        )",
                          " IGD100I 0942 ALLOCATED TO DDNAME SYSUT1   DATACLAS (        )",
                          " IEF237I JES2 ALLOCATED TO SYSPRINT",
                          " IEF237I 01A0 ALLOCATED TO SYSIN",
                          " IEF142I DBDGEN00 C DLORD6 - STEP WAS EXECUTED - COND CODE 0000",
                          " IEF285I   IMSBLD.I15RTSMM.SDFSMAC                      KEPT          ",
                          " IEF285I   VOL SER NOS= IMSBG2.                            ",
                          " IEF285I   SYS20073.T125008.RA000.DBDGEN00.R0101894     PASSED        ",
                          " IEF285I   VOL SER NOS= 000000.                            ",
                          " IEF285I   SYS20073.T125008.RA000.DBDGEN00.R0101895     DELETED       ",
                          " IEF285I   VOL SER NOS= 333333.                            ",
                          " IEF285I   OMVSADM.DBDGEN00.JOB00361.D0000101.?         SYSOUT        ",
                          " IEF285I   IMSTESTL.IMS1.DBDSRC                         KEPT          ",
                          " IEF285I   VOL SER NOS= USER03.                            ",
                          " IEF373I STEP/C       /START 2020073.1250",
                          " IEF032I STEP/C       /STOP  2020073.1250 ",
                          "         CPU:     0 HR  00 MIN  00.03 SEC    SRB:     0 HR  00 MIN  00.00 SEC    ",
                          "         VIRT:   252K  SYS:   240K  EXT:  1876480K  SYS:    11896K",
                          "         ATB- REAL:                  1048K  SLOTS:                     0K",
                          "              VIRT- ALLOC:      14M SHRD:       0M",
                          " IEF236I ALLOC. FOR DBDGEN00 L DLORD6",
                          " IEF237I 01A0 ALLOCATED TO SYSLMOD",
                          " IEF237I 0940 ALLOCATED TO SYSLIN",
                          " IEF237I JES2 ALLOCATED TO SYSPRINT",
                          " IEF142I DBDGEN00 L DLORD6 - STEP WAS EXECUTED - COND CODE 0000",
                          " IEF285I   IMSTESTL.IMS1.DBDLIB                         KEPT          ",
                          " IEF285I   VOL SER NOS= USER03.                            ",
                          " IEF285I   SYS20073.T125008.RA000.DBDGEN00.R0101894     DELETED       ",
                          " IEF285I   VOL SER NOS= 000000.                            ",
                          " IEF285I   OMVSADM.DBDGEN00.JOB00361.D0000102.?         SYSOUT        ",
                          " IEF373I STEP/L       /START 2020073.1250",
                          " IEF032I STEP/L       /STOP  2020073.1250 ",
                          "         CPU:     0 HR  00 MIN  00.00 SEC    SRB:     0 HR  00 MIN  00.00 SEC    ",
                          "         VIRT:    92K  SYS:   256K  EXT:     1768K  SYS:    11740K",
                          "         ATB- REAL:                  1036K  SLOTS:                     0K",
                          "              VIRT- ALLOC:      11M SHRD:       0M",
                          " IEF375I  JOB/DBDGEN00/START 2020073.1250",
                          " IEF033I  JOB/DBDGEN00/STOP  2020073.1250 ",
                          "         CPU:     0 HR  00 MIN  00.03 SEC    SRB:     0 HR  00 MIN  00.00 SEC    "
                      ],
                      "ddname": "JESYSMSG",
                      "id": "4",
                      "procstep": "",
                      "record_count": "44",
                      "stepname": "JES2"
                  },
                  {
                      "byte_count": "1896",
                      "content": [
                          "1z/OS V2 R2 BINDER     12:50:08 FRIDAY MARCH 13, 2020                                                                    ",
                          " BATCH EMULATOR  JOB(DBDGEN00) STEP(DLORD6  ) PGM= IEWL      PROCEDURE(L       )                                         ",
                          " IEW2278I B352 INVOCATION PARAMETERS - XREF,NOLIST                                                                       ",
                          " IEW2650I 5102 MODULE ENTRY NOT PROVIDED.  ENTRY DEFAULTS TO SECTION DLORD6.                                             ",
                          "                                                                                                                         ",
                          "                                                                                                                         ",
                          "1                                       C R O S S - R E F E R E N C E  T A B L E                                         ",
                          "                                        _________________________________________                                        ",
                          "                                                                                                                         ",
                          " TEXT CLASS = B_TEXT                                                                                                     ",
                          "                                                                                                                         ",
                          " ---------------  R E F E R E N C E  --------------------------  T A R G E T  -------------------------------------------",
                          "   CLASS                            ELEMENT       |                                            ELEMENT                  |",
                          "   OFFSET SECT/PART(ABBREV)          OFFSET  TYPE | SYMBOL(ABBREV)   SECTION (ABBREV)           OFFSET CLASS NAME       |",
                          "                                                  |                                                                     |",
                          "                                        *** E N D  O F  C R O S S  R E F E R E N C E ***                                 ",
                          "1z/OS V2 R2 BINDER     12:50:08 FRIDAY MARCH 13, 2020                                                                    ",
                          " BATCH EMULATOR  JOB(DBDGEN00) STEP(DLORD6  ) PGM= IEWL      PROCEDURE(L       )                                         ",
                          " IEW2850I F920 DLORD6 HAS BEEN SAVED WITH AMODE  24 AND RMODE    24.  ENTRY POINT NAME IS DLORD6.                        ",
                          " IEW2231I 0481 END OF SAVE PROCESSING.                                                                                   ",
                          " IEW2008I 0F03 PROCESSING COMPLETED.  RETURN CODE =  0.                                                                  ",
                          "                                                                                                                         ",
                          "                                                                                                                         ",
                          "                                                                                                                         ",
                          "1----------------------                                                                                                  ",
                          " MESSAGE SUMMARY REPORT                                                                                                  ",
                          " ----------------------                                                                                                  ",
                          "  TERMINAL MESSAGES      (SEVERITY = 16)                                                                                 ",
                          "  NONE                                                                                                                   ",
                          "                                                                                                                         ",
                          "  SEVERE MESSAGES        (SEVERITY = 12)                                                                                 ",
                          "  NONE                                                                                                                   ",
                          "                                                                                                                         ",
                          "  ERROR MESSAGES         (SEVERITY = 08)                                                                                 ",
                          "  NONE                                                                                                                   ",
                          "                                                                                                                         ",
                          "  WARNING MESSAGES       (SEVERITY = 04)                                                                                 ",
                          "  NONE                                                                                                                   ",
                          "                                                                                                                         ",
                          "  INFORMATIONAL MESSAGES (SEVERITY = 00)                                                                                 ",
                          "  2008  2231  2278  2650  2850                                                                                           ",
                          "                                                                                                                         ",
                          "                                                                                                                         ",
                          "  **** END OF MESSAGE SUMMARY REPORT ****                                                                                ",
                          "                                                                                                                         "
                      ],
                      "ddname": "SYSPRINT",
                      "id": "102",
                      "procstep": "L",
                      "record_count": "45",
                      "stepname": "DLORD6"
                  }
              ],
              "job_id": "JOB00361",
              "job_name": "DBDGEN00",
              "owner": "OMVSADM",
              "ret_code": {
                  "code": 0,
                  "msg": "CC 0000",
                  "msg_code": "0000",
                  "msg_txt": "",
                  "steps": [
                    { "step_name": "DLORD6",
                      "step_cc": "0000"
                    }
                  ]
              },
              "subsystem": "STL1"
          }
     ]
message:
  description: The output message that the module generates.
  returned: success
  type: str
  sample: Submit JCL operation succeeded.
"""

EXAMPLES = r"""
- name: Submit the JCL
  zos_job_submit:
    src: TEST.UTILs(SAMPLE)
    location: DATA_SET
    wait: false
  register: response

- name: Submit USS job
  zos_job_submit:
    src: /u/tester/demo/sample.jcl
    location: USS
    wait: false
    return_output: false

- name: Convert a local JCL file to IBM-037 and submit the job
  zos_job_submit:
    src: /Users/maxy/ansible-playbooks/provision/sample.jcl
    location: LOCAL
    wait: false
    encoding:
      from: ISO8859-1
      to: IBM-037

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
"""

from ansible.module_utils.six import PY3

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.encode import (
    Defaults,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.job import (
    job_output,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    data_set,
)

from timeit import default_timer as timer
import re
from tempfile import NamedTemporaryFile
from os import remove
from time import sleep
from ansible.module_utils.basic import AnsibleModule

try:
    from zoautil_py.exceptions import ZOAUException, JobSubmitException
except ImportError:
    ZOAUException = MissingZOAUImport()
    JobSubmitException = MissingZOAUImport()

try:
    from zoautil_py import jobs
except Exception:
    jobs = MissingZOAUImport()

if PY3:
    from shlex import quote
else:
    from pipes import quote


JOB_COMPLETION_MESSAGES = ["CC", "ABEND", "SEC ERROR", "JCL ERROR", "JCLERR"]
MAX_WAIT_TIME_S = 86400


def submit_src_jcl(src, module, timeout=0, hfs=True, volume=None):
    """ Submit the src JCL whether local, USS or in a data set """

    kwargs = {
        "timeout": timeout,
        "hfs": hfs,
    }

    job_id_result = None
    wait = True  # Wait is always true because we require wait_time_s > 0
    changed = False
    present = False

    try:
        if volume is not None:
            volumes = [volume]
            present, changed = data_set.attempt_catalog_if_necessary(src, volumes)

            if not present:
                result = dict(changed=changed)
                result["job_id"] = ""
                result["msg"] = ("Unable to submit job {0} because the data set could "
                                 "not be cataloged on the volume {1}.".format(src, volume))
                module.fail_json(**result)

        starttime = timer()
        duration = 0

        # Calling ZOAU submit with a wait=true is non-blocking,we must insert
        # a wait routine of our own after this call
        job_listing = jobs.submit(src, wait, None, **kwargs)

        # Introducing a sleep to ensure we wait at most timeout
        while(job_listing is None or duration < timeout):
            checktime = timer()
            duration = round(checktime - starttime)
            sleep(0.5)

        if job_listing:
            job_id_result = job_listing.id

    # ZOAU throws a ZOAUException when RC !=0
    except ZOAUException as err:
        result = dict(changed=False)
        result["job_id"] = ""
        result["msg"] = ("Unable to submit job {0}, a non-zero return code has "
                         "returned with error: {1}. Please review the job log for futher "
                         "details.".format(src, str(err)))
        module.fail_json(**result)

    # ZOAU throws a JobSubmitException when timeout is execeeded
    except JobSubmitException as err:
        result = dict(changed=False)
        result["job_id"] = job_id_result
        result["msg"] = ("The JCL submitted with job id {0} but "
                         "appears to be a long running job that exceeded its "
                         "maximum wait time of {1} second(s). Consider using module "
                         "zos_job_query to poll for long running "
                         "jobs and review {2} for futher details.".format(
                             str(job_id_result), str(timeout), str(err)))
        module.exit_json(**result)

    return job_id_result, duration


def run_module():
    module_args = dict(
        src=dict(type="str", required=True),
        wait=dict(type="bool", required=False, default=False,
                  removed_at_date='2022-11-30',
                  removed_from_collection='ibm.ibm_zos_core'),
        location=dict(
            type="str",
            default="DATA_SET",
            choices=["DATA_SET", "USS", "LOCAL"],
        ),
        encoding=dict(
            type="dict",
            required=False,
            options={
                "from": dict(
                    type="str",
                    required=False,
                    default=Defaults.DEFAULT_ASCII_CHARSET
                ),
                "to": dict(
                    type="str",
                    required=False,
                    default=Defaults.DEFAULT_EBCDIC_USS_CHARSET
                )
            }
        ),
        volume=dict(type="str", required=False),
        return_output=dict(type="bool", required=False, default=True),
        wait_time_s=dict(type="int", default=10),
        max_rc=dict(type="int", required=False),
        temp_file=dict(type="path", required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    encoding = module.params.get("encoding")
    if encoding is None:
        encoding = {
            "from": Defaults.DEFAULT_ASCII_CHARSET,
            "to": Defaults.get_default_system_charset(),
        }

    arg_defs = dict(
        src=dict(arg_type="data_set_or_path", required=True),
        wait=dict(arg_type="bool", required=False, removed_at_date='2022-11-30',
                  removed_from_collection='ibm.ibm_zos_core'),
        location=dict(
            arg_type="str",
            default="DATA_SET",
            choices=["DATA_SET", "USS", "LOCAL"],
        ),
        from_encoding=dict(arg_type="encoding", default=Defaults.DEFAULT_ASCII_CHARSET),
        to_encoding=dict(
            arg_type="encoding", default=Defaults.get_default_system_charset()
        ),
        volume=dict(arg_type="volume", required=False),
        return_output=dict(arg_type="bool", default=True),
        wait_time_s=dict(arg_type="int", required=False, default=10),
        max_rc=dict(arg_type="int", required=False),
        temp_file=dict(arg_type="path", required=False),
    )

    # Default changed to False in case the module is not able to execute
    result = dict(changed=False)
    module.params.update(
        dict(
            from_encoding=encoding.get("from"),
            to_encoding=encoding.get("to"),
        )
    )

    # ********************************************************************
    # Verify the validity of module args. BetterArgParser raises ValueError
    # when a parameter fails its validation check
    # ********************************************************************
    try:
        parser = BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(
            msg="Parameter verification failed", stderr=str(err))

    # Extract values from set module options
    location = parsed_args.get("location")
    volume = parsed_args.get("volume")
    parsed_args.get("wait")
    src = parsed_args.get("src")
    return_output = parsed_args.get("return_output")
    wait_time_s = parsed_args.get("wait_time_s")
    max_rc = parsed_args.get("max_rc")
    from_encoding = parsed_args.get("from_encoding")
    to_encoding = parsed_args.get("to_encoding")
    # temporary file names for copied files when user sets location to LOCAL
    temp_file = parsed_args.get("temp_file")
    temp_file_encoded = None
    if temp_file:
        temp_file_encoded = NamedTemporaryFile(delete=True)

    if wait_time_s <= 0 or wait_time_s > MAX_WAIT_TIME_S:
        module.fail_json(
            msg="The value for option wait_time_s is not valid, it must be \
                    greater than 0 and less than " + MAX_WAIT_TIME_S,
            **result
        )

    job_id_result = None
    duration = 0

    if location == "DATA_SET":
        job_id_result, duration = submit_src_jcl(src, module, wait_time_s, False, volume)
    elif location == "USS":
        job_id_result, duration = submit_src_jcl(src, module, wait_time_s, True)
    else:
        # added -c to iconv to prevent \r from erroring as invalid chars to EBCDIC
        conv_str = "iconv -c -f {0} -t {1} {2} > {3}".format(
            from_encoding,
            to_encoding,
            quote(temp_file),
            quote(temp_file_encoded.name),
        )

        conv_rc, stdout, stderr = module.run_command(
            conv_str,
            use_unsafe_shell=True,
        )

        if conv_rc == 0:
            job_id_result, duration = submit_src_jcl(temp_file_encoded.name, module, wait_time_s, True)
        else:
            module.fail_json(
                msg="Failed to convert the src {0} from encoding {1} to \
                    encoding {2}, unable to submit job.".format(src, from_encoding, to_encoding),
                stderr=str(stderr),
                stdout=str(stdout),
                **result
            )

    result["job_id"] = job_id_result
    result["duration"] = duration
    result["changed"] = True
    try:
        job_output_txt = job_output(job_id=job_id_result)

        if job_output_txt:
            job_retcode = job_output_txt[0].get("ret_code")

            if job_retcode:
                job_msg = job_retcode.get("msg")

                if re.search(
                    "^(?:{0})".format("|".join(JOB_COMPLETION_MESSAGES)), job_msg
                ):
                    # If the job_msg doesn't have a CC, it is an improper completion (error/abend)
                    if re.search("^(?:CC)", job_msg) is None:
                        result["changed"] = False
                        result["ret_code"] = job_retcode
                        raise Exception("Unable to find a job completion code (CC) in job output")

                result["jobs"] = job_output_txt

                if not return_output:
                    for job in result.get("jobs", []):
                        job["ddnames"] = []

                if return_output is True and max_rc is not None:
                    ret_code = job_output_txt[0].get("ret_code")
                    job_rc = result.get("jobs")[0].get("ret_code").get("code")
                    assert_valid_return_code(max_rc, job_rc, ret_code)

    except Exception as err:
        result["msg"] = "The JCL submitted with job id {0} but \
                        there was an error obtaining the job output. Review \
                        the error for furhter details {1}.".format(str(job_id_result), str(err))
        module.exit_json(**result)
    finally:
        if temp_file:
            remove(temp_file)

    module.exit_json(**result)


def assert_valid_return_code(max_rc, job_rc, ret_code):
    if job_rc is None:
        raise Exception("Unable to find a job return code (ret_code[code]) in the job output.")

    if max_rc < job_rc:
        raise Exception("Maximum return code {0} for job steps must be less than \
            job return code {1}.".format(str(max_rc), str(job_rc)))

    for step in ret_code["steps"]:
        step_cc_rc = int(step["step_cc"])
        step_name_for_rc = step["step_name"]
        if max_rc > step_cc_rc:
            raise Exception("Step name {0} exceeded maximum return code (max_rc) {1} \
                with recturn code of {2}.".format(step_name_for_rc, str(max_rc), str(step_cc_rc)))


class Error(Exception):
    pass


class SubmitJCLError(Error):
    def __init__(self, jobs):
        self.msg = 'An error occurred during submission of jobs "{0}"'.format(jobs)


def main():
    run_module()


if __name__ == "__main__":
    main()
