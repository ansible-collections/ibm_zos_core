Module
============
Name
-----------
zos_job_out


Description
-----------

The `zos_job_out` module is used to display z/OS job output for a given criteria (Job id/Job name/owner) with or without a data definition name as a filter.

Features
--------
* Display the z/OS job output for a given criteria (Job id/Job name/owner) with/without a data definition name as a filter.
* At least provide a job id/job name/owner.
* The job id can be specific such as "STC02560", or one that uses a pattern such as "STC*" or "*".
* The job name can be specific such as "TCPIP", or one that uses a pattern such as "TCP*" or "*".
* The owner can be specific such as "IBMUSER", or one that uses a pattern like "*".
* If there is no ddname, or if ddname="?", output of all the ddnames under the given job will be displayed.


Usage
=====

Example tasks
```
- name: Job output with ddname="JESJCL"
  zos_job_out:
    job_id: "STC02560"
    ddname: "JESJCL"
```
```
- name: Job output of all ddnames under the specific job
  zos_job_out:
    job_id: "STC02560"
    ddname: "?"
```
```
- name: Job output of all ddnames under found jobs
  zos_job_out:
    job_id: "STC*"
    job_name: "*"
    owner: "IBMUSER"
    ddname: "?"
```

Return values  
* __zos_job_out__:
  * _description_: list of job output.
  * _returned_: success
  * _type_: list[dict]
  * _dict contains_:
    * __job_id__:
      * _description_: job ID
      * _type_: str
    * __job_name__:
      * _description_: job name
      * _type_: str
    * __subsystem__:
      * _description_: subsystem
      * _type_: str
    * __class__:
      * _description_: class
      * _type_: str
    * __content-type__:
      * _description_: content type
      * _type_: str
    * __ddnames__:
      * _description_: list of data definition name
      * _type_: list[dict]
      * _dict contains_:
        * __ddname__:
          * _description_: data definition name
          * _type_: str
        * __record-count__:
          * _description_: record count
          * _type_: int
        * __id__:
          * _description_: id
          * _type_: str
        * __stepname__:
          * _description_: step name
          * _type_: str
        * __procstep__:
          * _description_: proc step
          * _type_: str
        * __byte-count__:
          * _description_: byte count
          * _type_: int
        * __content__:
          * _description_: ddname content
          * _type_: list[str]

Variables
=========
Variables available for module zos_job_out

Variable | Description | Required
-------- | ----------- | --------
`job_id` | Job ID. | no
`job_name` | Job name. | no
`owner` | Job owner. | no
`ddname` | Data definition name. | no

# Copyright
© Copyright IBM Corporation 2020  
