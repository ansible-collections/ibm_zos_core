
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_job_output.py

.. _zos_job_output_module:


zos_job_output -- Display job output
====================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Display the z/OS job output for a given criteria (Job id/Job name/owner) with/without a data definition name as a filter.
- At least provide a job id/job name/owner.
- The job id can be specific such as "STC02560", or one that uses a pattern such as "STC*" or "*".
- The job name can be specific such as "TCPIP", or one that uses a pattern such as "TCP*" or "*".
- The owner can be specific such as "IBMUSER", or one that uses a pattern like "*".
- If there is no ddname, or if ddname="?", output of all the ddnames under the given job will be displayed.





Parameters
----------


job_id
  The z/OS job ID of the job containing the spool file. (e.g "STC02560", "STC*")

  | **required**: False
  | **type**: str


job_name
  The name of the batch job. (e.g "TCPIP", "C*")

  | **required**: False
  | **type**: str


owner
  The owner who ran the job. (e.g "IBMUSER", "*")

  | **required**: False
  | **type**: str


ddname
  Data definition name (show only this DD on a found job). (e.g "JESJCL", "?")

  | **required**: False
  | **type**: str




Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: full
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
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










Return Values
-------------


jobs
  The output information for a list of jobs matching specified criteria. If no job status is found, this will return ret_code dictionary with parameter msg_txt = The job could not be found.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "class": "R",
                "content_type": "JOB",
                "ddnames": [
                    {
                        "byte_count": "775",
                        "content": [
                            "1                       J E S 2  J O B  L O G  --  S Y S T E M  S T L 1  --  N O D E  S T L 1            ",
                            "0 ",
                            " 10.25.48 JOB00134 ---- TUESDAY,   18 FEB 2020 ----",
                            " 10.25.48 JOB00134  IRR010I  USERID OMVSADM  IS ASSIGNED TO THIS JOB.",
                            " 10.25.48 JOB00134  $HASP375 JES2     ESTIMATED  LINES EXCEEDED",
                            " 10.25.48 JOB00134  ICH70001I OMVSADM  LAST ACCESS AT 10:25:47 ON TUESDAY, FEBRUARY 18, 2020",
                            " 10.25.48 JOB00134  $HASP375 HELLO    ESTIMATED  LINES EXCEEDED",
                            " 10.25.48 JOB00134  $HASP373 HELLO    STARTED - INIT 3    - CLASS R        - SYS STL1",
                            " 10.25.48 JOB00134  SMF000I  HELLO       STEP0001    IEBGENER    0000",
                            " 10.25.48 JOB00134  $HASP395 HELLO    ENDED - RC=0000",
                            "0------ JES2 JOB STATISTICS ------",
                            "-  18 FEB 2020 JOB EXECUTION DATE",
                            "-           16 CARDS READ",
                            "-           59 SYSOUT PRINT RECORDS",
                            "-            0 SYSOUT PUNCH RECORDS",
                            "-            6 SYSOUT SPOOL KBYTES",
                            "-         0.00 MINUTES EXECUTION TIME"
                        ],
                        "ddname": "JESMSGLG",
                        "id": "2",
                        "procstep": "",
                        "record_count": "17",
                        "stepname": "JES2"
                    },
                    {
                        "byte_count": "574",
                        "content": [
                            "         1 //HELLO    JOB (T043JM,JM00,1,0,0,0),\u0027HELLO WORLD - JRM\u0027,CLASS=R,       JOB00134",
                            "           //             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM                                ",
                            "           //*                                                                             ",
                            "           //* PRINT \"HELLO WORLD\" ON JOB OUTPUT                                           ",
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
                        ],
                        "ddname": "JESJCL",
                        "id": "3",
                        "procstep": "",
                        "record_count": "14",
                        "stepname": "JES2"
                    },
                    {
                        "byte_count": "1066",
                        "content": [
                            " ICH70001I OMVSADM  LAST ACCESS AT 10:25:47 ON TUESDAY, FEBRUARY 18, 2020",
                            " IEF236I ALLOC. FOR HELLO STEP0001",
                            " IEF237I DMY  ALLOCATED TO SYSIN",
                            " IEF237I JES2 ALLOCATED TO SYSPRINT",
                            " IEF237I JES2 ALLOCATED TO SYSUT1",
                            " IEF237I JES2 ALLOCATED TO SYSUT2",
                            " IEF142I HELLO STEP0001 - STEP WAS EXECUTED - COND CODE 0000",
                            " IEF285I   OMVSADM.HELLO.JOB00134.D0000102.?            SYSOUT        ",
                            " IEF285I   OMVSADM.HELLO.JOB00134.D0000101.?            SYSIN         ",
                            " IEF285I   OMVSADM.HELLO.JOB00134.D0000103.?            SYSOUT        ",
                            " IEF373I STEP/STEP0001/START 2020049.1025",
                            " IEF032I STEP/STEP0001/STOP  2020049.1025 ",
                            "         CPU:     0 HR  00 MIN  00.00 SEC    SRB:     0 HR  00 MIN  00.00 SEC    ",
                            "         VIRT:    60K  SYS:   240K  EXT:        0K  SYS:    11548K",
                            "         ATB- REAL:                     8K  SLOTS:                     0K",
                            "              VIRT- ALLOC:      10M SHRD:       0M",
                            " IEF375I  JOB/HELLO   /START 2020049.1025",
                            " IEF033I  JOB/HELLO   /STOP  2020049.1025 ",
                            "         CPU:     0 HR  00 MIN  00.00 SEC    SRB:     0 HR  00 MIN  00.00 SEC    "
                        ],
                        "ddname": "JESYSMSG",
                        "id": "4",
                        "procstep": "",
                        "record_count": "19",
                        "stepname": "JES2"
                    },
                    {
                        "byte_count": "251",
                        "content": [
                            "1DATA SET UTILITY - GENERATE                                                                       PAGE 0001             ",
                            "-IEB352I WARNING: ONE OR MORE OF THE OUTPUT DCB PARMS COPIED FROM INPUT                                                  ",
                            "                                                                                                                         ",
                            " PROCESSING ENDED AT EOD                                                                                                 "
                        ],
                        "ddname": "SYSPRINT",
                        "id": "102",
                        "procstep": "",
                        "record_count": "4",
                        "stepname": "STEP0001"
                    },
                    {
                        "byte_count": "49",
                        "content": [
                            " HELLO, WORLD                                                                    "
                        ],
                        "ddname": "SYSUT2",
                        "id": "103",
                        "procstep": "",
                        "record_count": "1",
                        "stepname": "STEP0001"
                    }
                ],
                "duration": 0,
                "execution_time": "00:00:03",
                "job_class": "R",
                "job_id": "JOB00134",
                "job_name": "HELLO",
                "owner": "OMVSADM",
                "priority": "1",
                "program_name": "IEBGENER",
                "queue_position": "58",
                "ret_code": {
                    "code": 0,
                    "msg": "CC 0000",
                    "msg_code": "0000",
                    "msg_txt": "",
                    "steps": [
                        {
                            "step_cc": 0,
                            "step_name": "STEP0001"
                        }
                    ]
                },
                "subsystem": "STL1"
            }
        ]

  job_id
    The z/OS job ID of the job containing the spool file.

    | **type**: str
    | **sample**: JOB00134

  job_name
    The name of the batch job.

    | **type**: str
    | **sample**: HELLO

  subsystem
    The job entry subsystem that MVS uses to do work.

    | **type**: str
    | **sample**: STL1

  class
    Identifies the data set used in a system output data set, usually called a sysout data set.

    | **type**: str

  content_type
    Type of address space used by the job, can be one of the following types. - APPC for an APPC Initiator. - JGRP for a JOBGROUP. - JOB for a Batch job. - STC for a Started task. - TSU for a Time sharing user. - \? for an unknown or pending job.

    | **type**: str
    | **sample**: JOB

  creation_date
    Date, local to the target system, when the job was created.

    | **type**: str
    | **sample**: 2023-05-04

  creation_time
    Time, local to the target system, when the job was created.

    | **type**: str
    | **sample**: 14:15:00

  execution_time
    Total duration time of the job execution, if it has finished. If the job is still running, it represents the time elapsed from the job execution start and current time.

    | **type**: str
    | **sample**: 00:00:10

  ddnames
    Data definition names.

    | **type**: list
    | **elements**: dict

    ddname
      Data definition name.

      | **type**: str
      | **sample**: JESMSGLG

    record_count
      Count of the number of lines in a print data set.

      | **type**: int
      | **sample**: 17

    id
      The file ID.

      | **type**: str
      | **sample**: 2

    stepname
      A step name is name that identifies the job step so that other JCL statements or the operating system can refer to it.

      | **type**: str
      | **sample**: JES2

    procstep
      Identifies the set of statements inside JCL grouped together to perform a particular function.

      | **type**: str
      | **sample**: PROC1

    byte_count
      Byte size in a print data set.

      | **type**: int
      | **sample**: 574

    content
      The ddname content.

      | **type**: list
      | **elements**: str
      | **sample**:

        .. code-block:: json

            [
                "         1 //HELLO    JOB (T043JM,JM00,1,0,0,0),\u0027HELLO WORLD - JRM\u0027,CLASS=R,       JOB00134",
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


  job_class
    Job class for this job.

    | **type**: str
    | **sample**: A

  svc_class
    Service class for this job.

    | **type**: str
    | **sample**: C

  priority
    A numeric indicator of the job priority assigned through JES.

    | **type**: int
    | **sample**: 4

  asid
    The address Space Identifier (ASID) that is a unique descriptor for the job address space. Zero if not active.

    | **type**: int

  queue_position
    The position within the job queue where the jobs resides.

    | **type**: int
    | **sample**: 3

  program_name
    The name of the program found in the job's last completed step found in the PGM parameter.

    | **type**: str
    | **sample**: IEBGENER

  ret_code
    Return code output collected from job log.

    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ret_code": {
                  "code": 0,
                  "msg": "CC 0000",
                  "msg_code": "0000",
                  "msg_txt": "",
                  "steps": [
                      {
                          "step_cc": 0,
                          "step_name": "STEP0001"
                      }
                  ]
              }
          }

    msg
      Return code or abend resulting from the job submission.

      | **type**: str
      | **sample**: CC 0000

    msg_code
      Return code extracted from the `msg` so that it can be evaluated. For example, ABEND(S0C4) would yield "S0C4".

      | **type**: str
      | **sample**: S0C4

    msg_txt
      Returns additional information related to the job.

      | **type**: str
      | **sample**: No job can be located with this job name: HELLO

    code
      Return code converted to integer value (when possible).

      | **type**: int

    steps
      Series of JCL steps that were executed and their return codes.

      | **type**: list
      | **elements**: dict

      step_name
        Name of the step shown as "was executed" in the DD section.

        | **type**: str
        | **sample**: STEP0001

      step_cc
        The CC returned for this step in the DD section.

        | **type**: int




changed
  Indicates if any changes were made during module operation

  | **returned**: on success
  | **type**: bool

