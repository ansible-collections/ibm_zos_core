
:github_url: https://github.com/IBM/ibm_zosmf/tree/master/plugins/roles/job_status

.. _job_status_module:


job_status -- Roles that query a job to extract its current status and determine its execution state.
======================================================================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The **IBM z/OS core collection** provides an Ansible role, referred to as **job_status**, to query a particular job with a given job_status_id 
  and parse the response to return the job status and indicate if the job is currently running.


Variables
---------

job_status_id

  The job ID that is assigned to the job.

  Ensure that a job ID begins with `STC`, `JOB`, `TSU` and are followed by up to 5 digits.

  When a job ID is greater than 99,999, the job id format begins with `S`, `J`, `T` and followed by 7 digits.

  | **required**: True
  | **type**: str


Examples
--------

.. code-block:: yaml+jinja
   
   - name: Query the job status and if is running of the job STC00001
     hosts: sampleHost
     gather_facts: no
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: job_status
         vars:
           job_status_id: STC00001



Notes
-----

.. note::
   - The role tolerates the asterisk (`*`) as wildcard but retrieves information from the first job that returned to match the pattern.








