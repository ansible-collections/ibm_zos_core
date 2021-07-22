
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_job_submit.py

.. _zos_job_submit_module:


zos_job_submit -- Submit JCL
============================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Submit JCL from DATA_SET , USS, or LOCAL location.
- Submit a job and optionally monitor for its execution.
- Optionally wait for the job output until the job finishes.
- For the uncataloged dataset, specify the volume serial number.





Parameters
----------


src
  The source directory or data set containing the JCL to submit.

  It could be physical sequential data set or a partitioned data set qualified by a member or a path. (e.g "USER.TEST","USER.JCL(TEST)")

  Or an USS file. (e.g "/u/tester/demo/sample.jcl")

  Or an LOCAL file in ansible control node. (e.g "/User/tester/ansible-playbook/sample.jcl")

  | **required**: True
  | **type**: str


location
  The JCL location. Supported options are DATA_SET, USS or LOCAL.

  DATA_SET can be a PDS, PDSE, or sequential data set.

  USS means the JCL location is located in UNIX System Services (USS).

  LOCAL means locally to the ansible control node.

  | **required**: True
  | **type**: str
  | **default**: DATA_SET
  | **choices**: DATA_SET, USS, LOCAL


wait
  Wait for the Job to finish and capture the output. Default is false.

  When *wait* is false or absent, the module will wait up to 10 seconds for the job to start, but will not wait for the job to complete.

  If *wait* is true, User can specify the wait time, see option ``wait_time_s``.

  | **required**: False
  | **type**: bool


wait_time_s
  When *wait* is true, the module will wait for the number of seconds for Job completion.

  User can set the wait time manually with this option.

  | **required**: False
  | **type**: int
  | **default**: 60


max_rc
  Specifies the maximum return code for the submitted job that should be allowed without failing the module.

  The ``max_rc`` is only checked when ``wait=true``, otherwise, it is ignored.

  | **required**: False
  | **type**: int


return_output
  Whether to print the DD output.

  If false, an empty list will be returned in ddnames field.

  | **required**: False
  | **type**: bool
  | **default**: True


volume
  The volume serial (VOLSER) where the data set resides. The option is required only when the data set is not cataloged on the system. Ignored for USS and LOCAL.

  | **required**: False
  | **type**: str


encoding
  Specifies which encoding the local JCL file should be converted from and to, before submitting the job.

  If this parameter is not provided, and the z/OS systems default encoding can not be identified, the JCL file will be converted from ISO8859-1 to IBM-1047 by default.

  | **required**: False
  | **type**: dict


  from
    The character set of the local JCL file; defaults to ISO8859-1.

    Supported character sets rely on the target version; the most common character sets are supported.

    | **required**: False
    | **type**: str
    | **default**: ISO8859-1


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




Notes
-----

.. note::
   For supported character sets used to encode data, refer to the `documentation <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html>`_.







Return Values
-------------


jobs
  List of jobs output. If no job status is found, this will return an empty job code with msg=JOB NOT FOUND.

  | **returned**: success
  | **type**: list
  | **elements**: dict

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

      | **type**: list[str]
      | **sample**:

        .. code-block:: json

            [
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 1 //HELLO\u00a0\u00a0\u00a0 JOB (T043JM,JM00,1,0,0,0),\u0027HELLO WORLD - JRM\u0027,CLASS=R,\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 JOB00134",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 //\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 MSGCLASS=X",
                "MSGLEVEL=1",
                "NOTIFY=S0JM\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \u00a0\u00a0\u00a0 //*\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 //* PRINT \\\"HELLO WORLD\\\" ON JOB OUTPUT\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 //*\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 //* NOTE THAT THE EXCLAMATION POINT IS INVALID EBCDIC FOR JCL\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 //*\u00a0\u00a0 AND WILL CAUSE A JCL ERROR\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 //*\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 2 //STEP0001 EXEC PGM=IEBGENER\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 3 //SYSIN\u00a0\u00a0\u00a0 DD DUMMY\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 4 //SYSPRINT DD SYSOUT=*\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 5 //SYSUT1\u00a0\u00a0 DD *\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 6 //SYSUT2\u00a0\u00a0 DD SYSOUT=*\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \"",
                "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0    \"\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 7 //\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 \" \u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0"
            ]


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
                          "step_cc": "0000",
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
      | **sample**: JCL Error detected.  Check the data dumps for more information.

    code
      Return code converted to integer value (when possible). For JCL ERRORs, this will be None.

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

        | **type**: str
        | **sample**: 00



  sample


message
  The output message that the sample module generates.

  | **returned**: success
  | **type**: str
  | **sample**: Submit JCL operation succeeded.

