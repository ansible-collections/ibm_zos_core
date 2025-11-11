
:github_url: https://github.com/IBM/ibm_zosmf/tree/master/plugins/roles/job_status

.. _job_status_module:


job_status -- Role that query, extract job status and if is running.
====================================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The **IBM z/ibm_zos_core collection** provides an Ansible role, referred to as **job_status**, to query a particular job with a given job_id and parse the response to return as a msg the job status and if the job is currently running or not.







Variables
---------


 

job_id
  The job id that has been assigned to the job.

  A job id must begin with `STC`, `JOB`, `TSU` and are followed by up to 5 digits.

  When a job id is greater than 99,999, the job id format will begin with `S`, `J`, `T` and are followed by 7 digits.

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
           job_oid: STC00001




Notes
-----

.. note::
   - The role tolerate the asterisk (`*`) as wildcard but only retrieve information from the first job returned that math the patter.








