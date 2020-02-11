Module
============
Name
-----------
zos_job_submit  

Description
-----------

The `zos_job_submit` module allows you to submit a job and optionally monitor for its execution.

Features
--------
*  Submit JCL from DATS_SET , USS, or LOCAL location.
*  Optionally wait for the job output until the job finishes.
*  For the uncatalogued dataset, specify the volume serial number.
 
Usage
=====
Example playbook to TBD:
```
- name: Submit the JCL 
  zos_job_submit:
      src: TEST.UTILS(SAMPLE)
      location: DATA_SET
      wait: false
      volume:
      return_output: false
``` 
```
- name: Submit USS job
  zos_job_submit:
      src: /u/tester/demo/sample.jcl
      location: USS
      wait: false
      volume:
```
```
- name: Submit LOCAL job
  zos_job_submit:
      src: /Users/maxy/ansible-playbooks/provision/sample.jcl
      location: LOCAL
      encoding: UTF-8
      wait: false
      volume:
```
```
- name: Submit uncatalogued PDS job
  zos_job_submit:
      src: TEST.UNCATLOG.JCL(SAMPLE)
      location: DATA_SET
      wait: false
      volume: P2SS01
```
```
- name: Submit long running PDS job, and wait for the job to finish
  zos_job_submit:
      src: TEST.UTILS(LONGRUN)
      location: DATA_SET
      wait: true 
      wait_time_s: 30
```
```
Example results: 
"msg": {
         "jobs":[
      {
         "job_id":"JOB32881",
         "job_name":"TEST",
         "changed":true,
         "failed":false,
         "duration":0,
         "ddnames":[
            {
               "ddname":"JESMSGLG",
               "step_name":"JES2",
               "content":[
                  "J E S 2  J O B  L O G  --  S Y S T E M  M V 2 C  --  N O D E ...."
               ]
            },
            {
               "ddname":"JESJCL",
               "step_name":"JES2",
               "content":[
                  "1 //TEST JOB                       JOB32881"
               ]
            },
            {
               "ddname":"JESYSMSG",
               "step_name":"JES2",
               "content":[
                  "ICH70001I TESTER"
               ]
            }
         ],
         "ret_code":{
            "msg":  "CC 0000" ,
            "code": "0000" ,
            "msg_detail": "Submit JCL operation succeeded",
         },
      },
   ]
```

Variables
=========
Variables available for module zos_job_submit
-------

Variable | Description | Required
-------- | ----------- | --------
`src` | Name of the dataset. | yes
`location` | Dataset source location, e.g PDS, USS, LOCAL. | yes
`wait` | Whether to wait for the job to finish and return the output. Type bool | no
`volume` | The volume serial (VOLSER) where the data set resides. The option is required only when the data set is not catalogued on the system. Ignored for USS and LOCAL. | no
`wait_time_s` | When wait is true, the module will wait for a maximum of 60s by default. User can set the wait time manually in this option. Type int | no
`return_output` | Whether to print the DD output. If false, null will be returned in ddnames field. Type bool | no
`encoding` | The local file in ansible control node encoding format. Type str | no

Return values

* __jobs__:
  * _description_: The submitted z/OS job(s) and the current status and the output of the job(s)
  * _returned_: success
  * _type_: list[dict]
* __message__:
  * _description_: The output message that the sample module generates
  * _type_: complex
  * _returned_: success
* __changed__: 
  * _description_: Indicates if any changes were made during module operation.
  * _type_: bool

# Copyright
© Copyright IBM Corporation 2020  
