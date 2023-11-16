#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2022, 2023
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
    - "Demetrios Dimatos (@ddimatos)"
short_description: Submit JCL
description:
    - Submit JCL from a data set, USS, or from the controller.
    - Submit a job and optionally monitor for completion.
    - Optionally, wait a designated time until the job finishes.
    - For an uncataloged dataset, specify the volume serial number.
version_added: "1.0.0"
options:
  src:
    required: true
    type: str
    description:
      - The source file or data set containing the JCL to submit.
      - It could be a physical sequential data set, a partitioned data set
        qualified by a member or a path. (e.g "USER.TEST","USER.JCL(TEST)")
      - Or a USS file. (e.g "/u/tester/demo/sample.jcl")
      - Or a LOCAL file in ansible control node.
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
      - The JCL location. Supported choices are ``DATA_SET``, ``USS`` or ``LOCAL``.
      - DATA_SET can be a PDS, PDSE, or sequential data set.
      - USS means the JCL location is located in UNIX System Services (USS).
      - LOCAL means locally to the ansible control node.
  wait:
    required: false
    default: false
    type: bool
    description:
      - Setting this option will yield no change, it is deprecated. There is no
        no need to set I(wait); setting I(wait_times_s) is the correct way to
        configure the amount of tme to wait for a job to execute.
      - Configuring wait used by the L(zos_job_submit,./zos_job_submit.html) module has been
        deprecated and will be removed in ibm.ibm_zos_core collection.
      - See option I(wait_time_s).
  wait_time_s:
    required: false
    default: 10
    type: int
    description:
      - Option I(wait_time_s) is the total time that module
        L(zos_job_submit,./zos_job_submit.html) will wait for a submitted job
        to complete. The time begins when the module is executed on the managed
        node.
      - I(wait_time_s) is measured in seconds and must be a value greater than 0
        and less than 86400.
  max_rc:
    required: false
    type: int
    description:
      - Specifies the maximum return code allowed for any job step for the submitted job.
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
      - The volume serial (VOLSER)is where the data set resides. The option
        is required only when the data set is not cataloged on the system.
      - When configured, the L(zos_job_submit,./zos_job_submit.html) will try to
        catalog the data set for the volume serial. If it is not able to, the
        module will fail.
      - Ignored for I(location=USS) and I(location=LOCAL).
  encoding:
    description:
      - Specifies which encoding the local JCL file should be converted from
        and to, before submitting the job.
      - This option is only supported for when I(location=LOCAL).
      - If this parameter is not provided, and the z/OS systems default encoding
        can not be identified, the JCL file will be converted from UTF-8 to
        IBM-1047 by default, otherwise the module will detect the z/OS system
        encoding.
    required: false
    type: dict
    suboptions:
      from:
        description:
          - The character set of the local JCL file; defaults to UTF-8.
          - Supported character sets rely on the target platform; the most
            common character sets are supported.
        required: false
        type: str
        default: UTF-8
      to:
        description:
          - The character set to convert the local JCL file to on the remote
            z/OS system; defaults to IBM-1047 when z/OS systems default encoding
            can not be identified.
          - If not provided, the module will attempt to identify and use the
            default encoding on the z/OS system.
          - Supported character sets rely on the target version; the most
            common character sets are supported.
        required: false
        type: str
        default: IBM-1047

extends_documentation_fragment:
  - ibm.ibm_zos_core.template

notes:
  - For supported character sets used to encode data, refer to the
    L(documentation,https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html).
"""

RETURN = r"""
jobs:
  description:
     List of jobs output.
     If no job status is found, this will return an empty ret_code with msg_txt explanation.
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
         Return code output collected from the job log.
      type: dict
      contains:
        msg:
          description:
            Return code resulting from the job submission. Jobs that take
            longer to assign a value can have a value of '?'.
          type: str
          sample: CC 0000
        msg_code:
          description:
            Return code extracted from the `msg` so that it can be evaluated
            as a string. Jobs that take longer to assign a value can have a
            value of '?'.
          type: str
          sample: 0000
        msg_txt:
          description:
             Returns additional information related to the job. Jobs that take
             longer to assign a value can have a value of '?'.
          type: str
          sample: The job completion code (CC) was not available in the job
                  output, please review the job log."
        code:
          description:
             Return code converted to an integer value (when possible).
             For JCL ERRORs, this will be None.
          type: int
          sample: 0
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
              type: int
              sample: 0
      sample:
        ret_code: {
          "code": 0,
          "msg": "CC 0000",
          "msg_code": "0000",
          "msg_txt": "",
          "steps": [
            { "step_name": "STEP0001",
              "step_cc": 0
            },
          ]
        }
    job_class:
      description:
        Job class for this job.
      type: str
      sample: A
    svc_class:
      description:
        Service class for this job.
      type: str
      sample: C
    priority:
      description:
        A numeric indicator of the job priority assigned through JES.
      type: int
      sample: 4
    asid:
      description:
        The address Space Identifier (ASID) that is a unique descriptor for the job address space.
        Zero if not active.
      type: int
      sample: 0
    creation_date:
      description:
        Date, local to the target system, when the job was created.
      type: str
      sample: "2023-05-04"
    creation_time:
      description:
        Time, local to the target system, when the job was created.
      type: str
      sample: "14:15:00"
    queue_position:
      description:
        The position within the job queue where the jobs resides.
      type: int
      sample: 3
    program_name:
      description:
        The name of the program found in the job's last completed step found in the PGM parameter.
        Returned when Z Open Automation Utilities (ZOAU) is 1.2.4 or later.
      type: str
      sample: "IEBGENER"

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
                      "step_cc": 0
                    }
                  ]
              },
              "job_class": "K",
              "svc_class": "?",
              "priority": 1,
              "program_name": "IEBGENER",
              "asid": 0,
              "creation_date": "2023-05-03",
              "creation_time": "12:13:00",
              "queue_position": 3,
              "subsystem": "STL1",
              "system": "STL1"
          }
     ]
message:
  description: This option is being deprecated
  returned: success
  type: str
  sample: Submit JCL operation succeeded.
"""

EXAMPLES = r"""
- name: Submit JCL in a PDSE member
  zos_job_submit:
    src: HLQ.DATA.LLQ(SAMPLE)
    location: DATA_SET
  register: response

- name: Submit JCL in USS with no DDs in the output.
  zos_job_submit:
    src: /u/tester/demo/sample.jcl
    location: USS
    return_output: false

- name: Convert local JCL to IBM-037 and submit the job.
  zos_job_submit:
    src: /Users/maxy/ansible-playbooks/provision/sample.jcl
    location: LOCAL
    encoding:
      from: ISO8859-1
      to: IBM-037

- name: Submit JCL in an uncataloged PDSE on volume P2SS01.
  zos_job_submit:
    src: HLQ.DATA.LLQ(SAMPLE)
    location: DATA_SET
    volume: P2SS01

- name: Submit a long running PDS job and wait up to 30 seconds for completion.
  zos_job_submit:
    src: HLQ.DATA.LLQ(LONGRUN)
    location: DATA_SET
    wait_time_s: 30

- name: Submit a long running PDS job and wait up to 30 seconds for completion.
  zos_job_submit:
    src: HLQ.DATA.LLQ(LONGRUN)
    location: DATA_SET
    wait_time_s: 30

- name: Submit JCL and set the max return code the module should fail on to 16.
  zos_job_submit:
    src: HLQ.DATA.LLQ
    location: DATA_SET
    max_rc: 16
"""

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
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    DataSet,
)
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import PY3
from timeit import default_timer as timer
from tempfile import NamedTemporaryFile
from os import remove
from time import sleep
import re

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


JOB_COMPLETION_MESSAGES = frozenset(["CC", "ABEND", "SEC ERROR", "JCL ERROR", "JCLERR"])
JOB_ERROR_MESSAGES = frozenset(["ABEND", "SEC ERROR", "SEC", "JCL ERROR", "JCLERR"])
MAX_WAIT_TIME_S = 86400


def submit_src_jcl(module, src, src_name=None, timeout=0, hfs=True, volume=None, start_time=timer()):
    """ Submit src JCL whether JCL is local (Ansible Controller), USS or in a data set.

        Arguments:
            module - module instnace to access the module api
            src (str)       - JCL, can be relative or absolute paths either on controller or USS
                            - Data set, can be PS, PDS, PDSE Member
            src_name (str)  - the src name that was provided in the module because through
                              the runtime src could be replace with a temporary file name
            timeout (int)   - how long to wait in seconds for a job to complete
            hfs (boolean)   - True if JCL is a file in USS, otherwise False; Note that all
                              JCL local to a controller is transfered to USS thus would be
                              True
            volume (str)    - volume the data set JCL is located on that will be cataloged before
                              being submitted
            start_time      - time the JCL started its submission

        Returns:
            job_submitted_id  - the JCL job ID returned from submitting a job, else if no
                                job submits, None will be returned
            duration          - how long the job ran for in this method
    """

    kwargs = {
        "timeout": timeout,
        "hfs": hfs,
    }

    wait = True  # Wait is always true because the module requires wait_time_s > 0
    present = False
    duration = 0
    job_submitted = None
    result = {}

    try:
        if volume is not None:
            volumes = [volume]
            # Get the PDS name to catalog it
            src_ds_name = data_set.extract_dsname(src)
            present, changed = DataSet.attempt_catalog_if_necessary(
                src_ds_name, volumes)

            if not present:
                result["changed"] = False
                result["failed"] = True
                result["msg"] = ("Unable to submit job {0} because the data set could "
                                 "not be cataloged on the volume {1}.".format(src, volume))
                module.fail_json(**result)

        job_submitted = jobs.submit(src, wait, None, **kwargs)

        # Introducing a sleep to ensure we have the result of job sumbit carrying the job id
        while (job_submitted is None and duration <= timeout):
            current_time = timer()
            duration = round(current_time - start_time)
            sleep(0.5)

        # Second sleep is to wait long enough for the job rc to not equal a `?`
        # which is what ZOAU sends back, opitonally we can check the 'status' as
        # that is sent back as `AC` when the job is not complete but the problem
        # with monitoring 'AC' is that STARTED tasks never exit the AC status.
        if job_submitted:
            job_listing_rc = jobs.listing(job_submitted.id)[0].rc
            job_listing_status = jobs.listing(job_submitted.id)[0].status

            # Before moving forward lets ensure our job has completed but if we see
            # status that matches one in JOB_ERROR_MESSAGES, don't wait, let the code
            # drop through and get analyzed in the main as it will scan the job ouput
            # Any match to JOB_ERROR_MESSAGES ends our processing and wait times
            while (job_listing_status not in JOB_ERROR_MESSAGES and
                    job_listing_status == 'AC' and
                    ((job_listing_rc is None or len(job_listing_rc) == 0 or
                      job_listing_rc == '?') and duration < timeout)):
                current_time = timer()
                duration = round(current_time - start_time)
                sleep(1)
                job_listing_rc = jobs.listing(job_submitted.id)[0].rc
                job_listing_status = jobs.listing(job_submitted.id)[0].status

    # ZOAU throws a ZOAUException when the job sumbission fails thus there is no
    # JCL RC to share with the user, if there is a RC, that will be processed
    # in the job_output parser.
    except ZOAUException as err:
        result["changed"] = False
        result["failed"] = True
        result["stderr"] = str(err)
        result["duration"] = duration
        result["job_id"] = job_submitted.id if job_submitted else None
        result["msg"] = ("Unable to submit job {0}, the job submission has failed. "
                         "Without the job id, the error can not be determined. "
                         "Consider using module `zos_job_query` to poll for the "
                         "job by name or review the system log for purged jobs "
                         "resulting from an abend.".format(src_name))
        module.fail_json(**result)

    # ZOAU throws a JobSubmitException when timeout has execeeded in that no job_id
    # has been returned within the allocated time.
    except JobSubmitException as err:
        result["changed"] = False
        result["failed"] = False
        result["stderr"] = str(err)
        result["duration"] = duration
        result["job_id"] = job_submitted.id if job_submitted else None
        result["msg"] = ("The JCL has been submitted {0} and no job id was returned "
                         "within the allocated time of {1} seconds. Consider using "
                         " module zos_job_query to poll for a long running "
                         "jobs or increasing the value for "
                         "`wait_times_s`.".format(src_name, str(timeout)))
        module.fail_json(**result)

    # Between getting a job_submitted and the jobs.listing(job_submitted.id)[0].rc
    # is enough time for the system to purge an invalid job, so catch it and let
    # it fall through to the catchall.
    except IndexError:
        job_submitted = None

    # There appears to be a small fraction of time when ZOAU has a handle on the
    # job and and suddenly its purged, this check is to ensure the job is there
    # long after the purge else we throw an error here if its been purged.
    if job_submitted is None:
        result["changed"] = False
        result["failed"] = True
        result["duration"] = duration
        result["job_id"] = job_submitted.id if job_submitted else None
        result["msg"] = ("The job {0} has been submitted and no job id was returned "
                         "within the allocated time of {1} seconds. Without the "
                         "job id, the error can not be determined, consider using "
                         "module `zos_job_query` to poll for the job by name or "
                         "review the system log for purged jobs resulting from an "
                         "abend.".format(src_name, str(timeout)))
        module.fail_json(**result)

    return job_submitted.id if job_submitted else None, duration


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
        use_template=dict(type='bool', default=False),
        template_parameters=dict(
            type='dict',
            required=False,
            options=dict(
                variable_start_string=dict(type='str', default='{{'),
                variable_end_string=dict(type='str', default='}}'),
                block_start_string=dict(type='str', default='{%'),
                block_end_string=dict(type='str', default='%}'),
                comment_start_string=dict(type='str', default='{#'),
                comment_end_string=dict(type='str', default='#}'),
                line_statement_prefix=dict(type='str', required=False),
                line_comment_prefix=dict(type='str', required=False),
                lstrip_blocks=dict(type='bool', default=False),
                trim_blocks=dict(type='bool', default=True),
                keep_trailing_newline=dict(type='bool', default=False),
                newline_sequence=dict(
                    type='str',
                    default='\n',
                    choices=['\n', '\r', '\r\n']
                ),
                auto_reload=dict(type='bool', default=False),
            )
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.params.get("encoding"):
        module.params.update(
            dict(
                from_encoding=module.params.get("encoding").get("from"),
                to_encoding=module.params.get("encoding").get("to"),
            )
        )
    else:
        module.params.update(
            dict(
                from_encoding=Defaults.DEFAULT_ASCII_CHARSET,
                to_encoding=Defaults.get_default_system_charset(),
            )
        )

    arg_defs = dict(
        src=dict(arg_type="data_set_or_path", required=True),
        wait=dict(arg_type="bool", required=False, removed_at_date='2022-11-30',
                  removed_from_collection='ibm.ibm_zos_core'),
        location=dict(
            arg_type="str",
            default="DATA_SET",
            choices=["DATA_SET", "USS", "LOCAL"],
        ),
        from_encoding=dict(
            arg_type="encoding", default=Defaults.DEFAULT_ASCII_CHARSET, required=False),
        to_encoding=dict(
            arg_type="encoding", default=Defaults.get_default_system_charset(), required=False
        ),
        volume=dict(arg_type="volume", required=False),
        return_output=dict(arg_type="bool", default=True),
        wait_time_s=dict(arg_type="int", required=False, default=10),
        max_rc=dict(arg_type="int", required=False),
        temp_file=dict(arg_type="path", required=False),
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

    # Default 'changed' is False in case the module is not able to execute
    result = dict(changed=False)

    if wait_time_s <= 0 or wait_time_s > MAX_WAIT_TIME_S:
        result["failed"] = True
        result["msg"] = ("The value for option `wait_time_s` is not valid, it must "
                         "be greater than 0 and less than {0}.".format(str(MAX_WAIT_TIME_S)))
        module.fail_json(**result)

    if temp_file:
        temp_file_encoded = NamedTemporaryFile(delete=True)

    job_submitted_id = None
    duration = 0
    start_time = timer()

    if location == "DATA_SET":
        job_submitted_id, duration = submit_src_jcl(
            module, src, src_name=src, timeout=wait_time_s, hfs=False, volume=volume, start_time=start_time)
    elif location == "USS":
        job_submitted_id, duration = submit_src_jcl(module, src, src_name=src, timeout=wait_time_s, hfs=True)
    else:
        # added -c to iconv to prevent '\r' from erroring as invalid chars to EBCDIC
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
            job_submitted_id, duration = submit_src_jcl(
                module, temp_file_encoded.name, src_name=src, timeout=wait_time_s, hfs=True)
        else:
            result["failed"] = True
            result["stdout"] = stdout
            result["stderr"] = stderr
            result["msg"] = ("Failed to convert the src {0} from encoding {1} to "
                             "encoding {2}, unable to submit job."
                             .format(src, from_encoding, to_encoding))
            module.fail_json(**result)

    try:
        # Explictly pass None for the unused args else a default of '*' will be
        # used and return undersirable results
        job_output_txt = None

        job_output_txt = job_output(
            job_id=job_submitted_id, owner=None, job_name=None, dd_name=None,
            dd_scan=return_output, duration=duration, timeout=wait_time_s, start_time=start_time)

        result["duration"] = duration

        if duration >= wait_time_s:
            result["failed"] = True
            result["changed"] = False
            if job_output_txt is not None:
                result["jobs"] = job_output_txt
            result["msg"] = (
                "The JCL submitted with job id {0} but appears to be a long "
                "running job that exceeded its maximum wait time of {1} "
                "second(s). Consider using module zos_job_query to poll for "
                "a long running job or increase option 'wait_times_s` to a value "
                "greater than {2}.".format(
                    str(job_submitted_id), str(wait_time_s), str(duration)))
            module.exit_json(**result)

        # Job has submitted, the module changed the managed node
        is_changed = True

        if job_output_txt:
            result["jobs"] = job_output_txt
            job_ret_code = job_output_txt[0].get("ret_code")

            if job_ret_code:
                job_msg = job_ret_code.get("msg")
                job_code = job_ret_code.get("code")

                # retcode["msg"] should never be empty where a retcode["code"] can be None,
                # "msg" could  be an ABEND which has no corresponding "code"
                if job_msg is None:
                    _msg = ("Unable to find a 'msg' in the 'ret_code' dictionary, "
                            "please review the job log.")
                    result["stderr"] = _msg
                    raise Exception(_msg)

                if return_output is True and max_rc is not None:
                    is_changed = assert_valid_return_code(max_rc, job_code, job_ret_code)

                if re.search("^(?:{0})".format("|".join(JOB_COMPLETION_MESSAGES)), job_msg):
                    # If the job_msg doesn't have a CC, it is an improper completion (error/abend)
                    if re.search("^(?:CC)", job_msg) is None:
                        _msg = ("The job completion code (CC) was not in the job log. "
                                "Please review the error {0} and the job log.".format(job_msg))
                        result["stderr"] = _msg
                        raise Exception(_msg)

                if job_code is None:
                    raise Exception("The job return code was not available in the job log, "
                                    "please review the job log and error {0}.".format(job_msg))

                if job_code != 0 and max_rc is None:
                    raise Exception("The job return code {0} was non-zero in the "
                                    "job output, this job has failed.".format(str(job_code)))

                if not return_output:
                    for job in result.get("jobs", []):
                        job["ddnames"] = []
            else:
                _msg = "The 'ret_code' dictionary was unavailable in the job log."
                result["ret_code"] = None
                result["stderr"] = _msg
                raise Exception(_msg)
        else:
            _msg = "The job output log is unavailable."
            result["stderr"] = _msg
            result["jobs"] = None
            raise Exception(_msg)

    except Exception as err:
        result["failed"] = True
        result["changed"] = False
        result["msg"] = ("The JCL submitted with job id {0} but "
                         "there was an error, please review "
                         "the error for further details: {1}".format
                         (str(job_submitted_id), str(err)))
        module.exit_json(**result)

    finally:
        if temp_file:
            remove(temp_file)

    # If max_rc is set, we don't want to default to changed=True, rely on 'is_changed'
    result["changed"] = True if is_changed else False
    result["failed"] = False
    module.exit_json(**result)


def assert_valid_return_code(max_rc, job_rc, ret_code):
    if job_rc is None:
        raise Exception(
            "The job return code (ret_code[code]) was not available in the jobs output, "
            "this job has failed.")

    if job_rc > max_rc:
        raise Exception("The job return code, 'ret_code[code]' {0} for the submitted job is "
                        "greater than the value set for option 'max_rc' {1}. "
                        "Increase the value for 'max_rc' otherwise this job submission "
                        "has failed.".format(str(job_rc), str(max_rc)))

    for step in ret_code["steps"]:
        step_cc_rc = int(step["step_cc"])
        step_name_for_rc = step["step_name"]
        if step_cc_rc > max_rc:
            raise Exception("The step name {0} with return code {1} for the submitted job is "
                            "greater than the value set for option 'max_rc' {2}. "
                            "Increase the value for 'max_rc' otherwise this job submission "
                            "has failed.".format(step_name_for_rc, str(step_cc_rc), str(max_rc)))

    # If there is NO exception rasied it means that max_rc is larger than the
    # actual RC from the submitted job. In this case, the ansible changed status
    # should NOT be 'changed=true' even though the user did override the return code,
    # a non-zero return code means the job did not change anything, so set it as
    # result["chagned"]=False,
    if job_rc != 0:
        return False

    return True


def main():
    run_module()


if __name__ == "__main__":
    main()
