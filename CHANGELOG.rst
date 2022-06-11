=============================
bm.ibm_zos_core Release Notes
=============================

.. contents:: Topics


v1.3.4
======

Release Summary
---------------

Release Date: '2022-03-06'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Bugfixes
--------

- zos_job_output - fixes a bug that returned all ddname's when a specific ddname
    was provided. Now a specific ddname can be returned and all others ignored.
    (https://github.com/ansible-collections/ibm_zos_core/pull/334)
- zos_ssh - connection plugin was updated to correct a bug in Ansible that
    would result in playbook task retries overriding the SSH connection
    retries. This is resolved by renaming the zos_ssh option
    retries to reconnection_retries. The update addresses users of
    ansible-core v2.9 which continues to use retries and users of
    ansible-core v2.11 or later which uses reconnection_retries.
    This also resolves a bug in the connection that referenced a deprecated
    constant. (https://github.com/ansible-collections/ibm_zos_core/pull/328)

v1.3.3
======

Release Summary
---------------

Release Date: '2022-26-04'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Bugfixes
--------

- zos_copy was updated to correct deletion of all temporary files and unwarranted deletes. - When the module would complete, a cleanup routine did not take into account that other processes had open temporary files and thus would error when trying to remove them. - When the module would copy a directory (source) from USS to another USS directory (destination), any files currently in the destination would be deleted. The modules behavior has changed such that files are no longer deleted unless the force option is set to true. When **force=true**, copying files or a directory to a USS destination will continue if it encounters existing files or directories and overwrite any corresponding files.
- zos_job_query was updated to correct a boolean condition that always evaluated to "CANCELLED". - When querying jobs that are either **CANCELLED** or have **FAILED**, they were always treated as **CANCELLED**.

v1.3.1
======

Release Summary
---------------

Release Date: '2022-27-04'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Bugfixes
--------

- zos_ping was updated to support Automation Hub documentation generation.
- zos_ssh connection plugin was updated to prioritize the execution of modules written in REXX over other implementations such is the case for zos_ping.

Known Issues
------------

- When executing programs using zos_mvs_raw, you may encounter errors that originate in the implementation of the programs. Two such known issues are noted below of which one has been addressed with an APAR. - zos_mvs_raw module execution fails when invoking Database Image Copy 2 Utility or Database Recovery Utility in conjunction with FlashCopy or Fast Replication. - zos_mvs_raw module execution fails when invoking DFSRRC00 with parm "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is addressed by APAR PH28089.

v1.3.0
======

Release Summary
---------------

Release Date: '2021-19-04'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 

`New Playbooks <https://github.com/IBM/z_ansible_collections_samples>`__
  - Authorize and synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub
  - Automate program execution with copy, sort and fetch data sets on z/OS playbook.
  - Automate user management with add, remove, grant permission, generate
    passwords, create zFS, mount zFS and send email notifications when deployed
    to Ansible Tower or AWX with the manage z/OS Users Using Ansible playbook.
  - Use the configure Python and ZOAU Installation playbook to scan the
    **z/OS** target to find the latest supported configuration and generate
    inventory and a variables configuration.
  - Automate software management with SMP/E Playbooks


Minor Changes
-------------

- All modules support relative paths and remove choice case sensitivity.
- zos_data_set added support to allocate and format zFS data sets.
- zos_operator supports new options **wait** and **wait_time_s** such that you can specify that zos_operator wait the full **wait_time_s** or return as soon as the first operator command executes.

Bugfixes
--------

- Action plugin zos_copy was updated to support Python 2.7.
- Job utility is an internal library used by several modules. It has been updated to use a custom written parsing routine capable of handling special characters to prevent job related reading operations from failing when a special character is encountered.
- Module zos_copy was updated to fail gracefully when a it encounters a non-zero return code.
- Module zos_copy was updated to support copying data set members that are program objects to a PDSE. Prior to this update, copying data set members would yield an error; - FSUM8976 Error writing <src_data_set_member> to PDSE member <dest_data_set_member>
- Module zos_job_submit referenced a non-existent option and was corrected to **wait_time_s**.
- Module zos_job_submit was updated to remove all trailing **\r** from jobs that are submitted from the controller.
- Module zos_tso_command support was added for when the command output contained special characters.
- Playbook zos_operator_basics.yaml has been updated to use end in the WTO reply over the previous use of cancel. Using cancel is not a valid reply and results in an execution error.

Known Issues
------------

- When executing programs using zos_mvs_raw, you may encounter errors that originate in the implementation of the programs. Two such known issues are noted below of which one has been addressed with an APAR. - zos_mvs_raw module execution fails when invoking Database Image Copy 2 Utility or Database Recovery Utility in conjunction with FlashCopy or Fast Replication. - zos_mvs_raw module execution fails when invoking DFSRRC00 with parm "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is addressed by APAR PH28089.

New Modules
-----------

- ibm.ibm_zos_core.zos_apf - Add or remove libraries to Authorized Program Facility (APF)
- ibm.ibm_zos_core.zos_backup_restore - Backup and restore data sets and volumes
- ibm.ibm_zos_core.zos_blockinfile - Manage block of multi-line textual data on z/OS
- ibm.ibm_zos_core.zos_data_set - Manage data sets
- ibm.ibm_zos_core.zos_find - Find matching data sets

v1.2.1
======

Release Summary
---------------

Release Date: '2020-10-09'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__.

Beginning this release, all playbooks previously included with the collection
will be made available on the `playbook repository <https://github.com/IBM/z_ansible_collections_samples>`__.

Minor Changes
-------------

- Documentation related to configuration has been migrated to the `playbook repository <https://github.com/IBM/z_ansible_collections_samples>`__
- Python 2.x support

Bugfixes
--------

- zos_copy - fixed regex support, dictionary merge operation fix
- zos_encode - removed TemporaryDirectory usage.
- zos_fetch - fix quote import

New Modules
-----------

- ibm.ibm_zos_core.zos_lineinfile - Manage textual data on z/OS

v1.1.0
======

Release Summary
---------------

Release Date: '2020-26-01'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__


Minor Changes
-------------

- Documentation updates
- Improved error handling and messages
- New Filter that will filter a list of WTOR messages based on message text.

New Modules
-----------

- ibm.ibm_zos_core.zos_encode - Perform encoding operations.
- ibm.ibm_zos_core.zos_fetch - Fetch data from z/OS
- ibm.ibm_zos_core.zos_mvs_raw - Run a z/OS program.
- ibm.ibm_zos_core.zos_operator - Execute operator command
- ibm.ibm_zos_core.zos_operator_action_query - Display messages requiring action
- ibm.ibm_zos_core.zos_ping - Ping z/OS and check dependencies.
- ibm.ibm_zos_core.zos_tso_command - Execute TSO commands

v1.0.0
======

Release Summary
---------------

Release Date: '2020-18-03'
This changelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 

Minor Changes
-------------

- Documentation updates
- Module zos_data_set catalog support added

Security Fixes
--------------

- Improved test, security and injection coverage
- Security vulnerabilities fixed

New Modules
-----------

- ibm.ibm_zos_core.zos_copy - Copy data to z/OS
- ibm.ibm_zos_core.zos_job_output - Display job output
- ibm.ibm_zos_core.zos_job_query - Query job status
- ibm.ibm_zos_core.zos_job_submit - Submit JCL
