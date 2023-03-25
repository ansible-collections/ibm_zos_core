
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_job_submit.py

.. _zos_job_submit_module:


zos_job_submit -- Submit JCL
============================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Submit JCL from a data set, USS, or from the controller.
- Submit a job and optionally monitor for completion.
- Optionally, wait a designated time until the job finishes.
- For an uncataloged dataset, specify the volume serial number.





Parameters
----------


src
  The source file or data set containing the JCL to submit.

  It could be a physical sequential data set, a partitioned data set qualified by a member or a path. (e.g "USER.TEST","USER.JCL(TEST)")

  Or a USS file. (e.g "/u/tester/demo/sample.jcl")

  Or a LOCAL file in ansible control node. (e.g "/User/tester/ansible-playbook/sample.jcl")

  | **required**: True
  | **type**: str


location
  The JCL location. Supported choices are ``DATA_SET``, ``USS`` or ``LOCAL``.

  DATA_SET can be a PDS, PDSE, or sequential data set.

  USS means the JCL location is located in UNIX System Services (USS).

  LOCAL means locally to the ansible control node.

  | **required**: False
  | **type**: str
  | **default**: DATA_SET
  | **choices**: DATA_SET, USS, LOCAL


wait
  Setting this option will yield no change, it is deprecated. There is no no need to set *wait*; setting *wait_times_s* is the correct way to configure the amount of tme to wait for a job to execute.

  Configuring wait used by the `zos_job_submit <./zos_job_submit.html>`_ module has been deprecated and will be removed in ibm.ibm_zos_core collection.

  See option *wait_time_s*.

  | **required**: False
  | **type**: bool


wait_time_s
  Option *wait_time_s* is the total time that module `zos_job_submit <./zos_job_submit.html>`_ will wait for a submitted job to complete. The time begins when the module is executed on the managed node.

  *wait_time_s* is measured in seconds and must be a value greater than 0 and less than 86400.

  | **required**: False
  | **type**: int
  | **default**: 10


max_rc
  Specifies the maximum return code allowed for any job step for the submitted job.

  | **required**: False
  | **type**: int


return_output
  Whether to print the DD output.

  If false, an empty list will be returned in the ddnames field.

  | **required**: False
  | **type**: bool
  | **default**: True


volume
  The volume serial (VOLSER)is where the data set resides. The option is required only when the data set is not cataloged on the system.

  When configured, the `zos_job_submit <./zos_job_submit.html>`_ will try to catalog the data set for the volume serial. If it is not able to, the module will fail.

  Ignored for *location=USS* and *location=LOCAL*.

  | **required**: False
  | **type**: str


encoding
  Specifies which encoding the local JCL file should be converted from and to, before submitting the job.

  This option is only supported for when *location=LOCAL*.

  If this parameter is not provided, and the z/OS systems default encoding can not be identified, the JCL file will be converted from UTF-8 to IBM-1047 by default, otherwise the module will detect the z/OS system encoding.

  | **required**: False
  | **type**: dict


  from
    The character set of the local JCL file; defaults to UTF-8.

    Supported character sets rely on the target platform; the most common character sets are supported.

    | **required**: False
    | **type**: str
    | **default**: UTF-8


  to
    The character set to convert the local JCL file to on the remote z/OS system; defaults to IBM-1047 when z/OS systems default encoding can not be identified.

    If not provided, the module will attempt to identify and use the default encoding on the z/OS system.

    Supported character sets rely on the target version; the most common character sets are supported.

    | **required**: False
    | **type**: str
    | **default**: IBM-1047





Examples
--------

.. code-block:: yaml+jinja

   
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




Notes
-----

.. note::
   For supported character sets used to encode data, refer to the `documentation <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html>`_.







Return Values
-------------


jobs
  List of jobs output. If no job status is found, this will return an empty ret_code with msg_txt explanation.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

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
                            "           //             PARM=\u0027OBJECT,NODECK,NOLIST\u0027                                      ",
                            "           //SYSLIB   DD DISP=SHR,                                                         ",
                            "           //      DSN=IMSBLD.I15RTSMM.SDFSMAC                                             ",
                            "           //SYSLIN   DD DISP=(NEW,PASS),RECFM=F,LRECL=80,BLKSIZE=80,                      ",
                            "           //         UNIT=SYSDA,SPACE=(CYL,(10,5),RLSE,,)                                 ",
                            "           //SYSUT1   DD DISP=(NEW,DELETE),UNIT=SYSDA,SPACE=(CYL,                          ",
                            "           //         (10,5),,,)                                                           ",
                            "           //SYSPRINT DD SYSOUT=*                                                          ",
                            "           //L        EXEC PGM=IEWL,                                                       ",
                            "           //             PARM=\u0027XREF,NOLIST\u0027,                                              ",
                            "           //             COND=(0,LT,C)                                                    ",
                            "           //SYSLMOD  DD DISP=SHR,                                                         ",
                            "           //      DSN=IMSTESTL.IMS1.DBDLIB(\u0026MBR)                                          ",
                            "           //SYSLIN   DD DSN=*.C.SYSLIN,DISP=(OLD,DELETE)                                  ",
                            "           //SYSPRINT DD SYSOUT=*                                                          ",
                            "           //*                                                                             ",
                            "           //         PEND                                                                 ",
                            "         4 //DLORD6   EXEC DBDGEN,                                                         ",
                            "           //             MBR=DLORD6                                                       ",
                            "         5 ++DBDGEN   PROC MBR=TEMPNAME                                                    ",
                            "         6 ++C        EXEC PGM=ASMA90,                                                     ",
                            "           ++             PARM=\u0027OBJECT,NODECK,NOLIST\u0027                                      ",
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
                            "           ++             PARM=\u0027XREF,NOLIST\u0027,                                              ",
                            "           ++             COND=(0,LT,C)                                                    ",
                            "        13 ++SYSLMOD  DD DISP=SHR,                                                         ",
                            "           ++      DSN=IMSTESTL.IMS1.DBDLIB(\u0026MBR)                                          ",
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
                        {
                            "step_cc": 0,
                            "step_name": "DLORD6"
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

  duration
    The total lapsed time the JCL ran for.

    | **type**: int

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


  ret_code
    Return code output collected from the job log.

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
      Return code resulting from the job submission. Jobs that take longer to assign a value can have a value of '?'.

      | **type**: str
      | **sample**: CC 0000

    msg_code
      Return code extracted from the `msg` so that it can be evaluated as a string. Jobs that take longer to assign a value can have a value of '?'.

      | **type**: str

    msg_txt
      Returns additional information related to the job. Jobs that take longer to assign a value can have a value of '?'.

      | **type**: str
      | **sample**: The job completion code (CC) was not available in the job output, please review the job log."

    code
      Return code converted to an integer value (when possible). For JCL ERRORs, this will be None.

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




message
  This option is being deprecated

  | **returned**: success
  | **type**: str
  | **sample**: Submit JCL operation succeeded.

