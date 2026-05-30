
:github_url: https://github.com/IBM/ibm_zosmf/tree/master/plugins/roles/job_status

.. _job_status_module:


job_status -- Query a job for status and execution state
========================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The **job_status** role queries a particular job with a given ``job_status_id`` and parses the response to return the job status and whether the job is currently running.






Variables
---------


 

job_status_id
  The job ID assigned to the target job.

  Expected format is ``STC``, ``JOB``, or ``TSU`` followed by up to 5 digits, or ``S``, ``J``, or ``T`` followed by 7 digits for IDs over 99,999.

  Value can include the asterisk (``*``) as a wildcard, but only job information from the first match is returned.

  | **required**: True
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Query job status of job with ID 'STC00001'
     hosts: sampleHost
     gather_facts: no
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: job_status
         vars:
           job_status_id: STC00001








