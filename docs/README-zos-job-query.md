Module
============
Name
-----------
zos_job_query

Description
-----------

The `zos_job_query` module allows you to list z/OS job(s) and the current status of the job(s).

Features
--------
* List z/OS job(s) and the current status of the job(s).
* Uses `owner` to filter the jobs by the job owner.
* Uses `system` to filter the jobs by system where the job is running (or ran) on.
* Uses `job_id` to filter the jobs by the job id.

Usage
====

Example task to use zos_job_query module:
```
- name: Call zos_job_query module to list jobs process
  zos_job_query:
    job_name: IYK3Z0*
    owner: *
```
```
- Sample result('jobs' field):
[
    {
        "job_id": "JOB31873",
        "job_name": "IYK3Z0IC",
        "owner": "WIWANG",
        "ret_code": "null"
    },
    {
        "job_id": "JOB40588",
        "job_name": "IYK3Z0JA",
        "owner": "SHIYUW",
        "ret_code": {
            "code": "null",
            "msg": "CANCELED"
        }
    },
    {
        "job_id": "JOB42015",
        "job_name": "IYK3Z0IH",
        "owner": "WANGD",
        "ret_code": {
            "code": "0000",
            "msg": "CC 0000"
        }
    }
]
```

Return values
* __original_message__:
  * _description_: The original list of parameters and arguments, plus any defaults used
  * _returned_: always
  * _type_: dict
* __message__:
  * _description_: The output message that the sample module generates
  * _type_: complex
  * _returned_: success
  * _contains_:
    * __stdout__:
      * _description_: The output from the module
      * _type_: str
    * __stderr__: 
      * _description_: Any error text from the module
      * _type_: str
* __changed__: 
  * _description_: Indicates if any changes were made during module operation 
  * _type_: bool
* __jobs__:
  * _description_: The list z/OS job(s) and the current status of the job(s)
  * _type_: list[dict]


Variables
=========
Variables available for module zos_job_query

Variable | Description | Required
-------- | ----------- | --------
`job_name` | The job name to query. | yes
`owner` | Identifies the owner of the job. | no
`job_id` | The job number that has been assigned to the job. These normally begin with STC, JOB, TSU and are followed by 5 digits. | no

# Copyright
© Copyright IBM Corporation 2020  
