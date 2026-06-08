==========================================================
Migrating Ansible z/OS Core collection from v1.x to v2.0.0
==========================================================

This guide covers breaking and recommended changes for upgrading
playbooks and roles to ibm.ibm_zos_core **v2.0.0**, including updates to
module options and return values.

Overview
========

The changes introduced in version 2.0 improve consistency and automation
reliability by using standardized naming conventions and predictable
return structures.

**Key improvements:**
---------------------

- **Consistent naming** - Module option names and return values are
  standardized across the collection.
- **Predictable returns** - Return values are standardized for automation workflows,
  rather than dynamically based on module operation results.

**Impact on existing playbooks:**
---------------------------------

To standardize naming across the collection, some module options
and return values are renamed:

- **Breaking changes** - Some module options and return values were renamed and are not
  backward compatible.
- **Aliased changes** - Other module options have new primary names,
  with old names still supported as aliases.

Modules: Breaking and non-breaking changes
==========================================

Breaking changes are all the module options that are renamed where
the old names are no longer supported. It also includes any return values
which are renamed. Ensure that any automation which relies on these values are updated.

Non-breaking changes are all the module options that are renamed
for consistency across the collection, but still have the old module
option name available as an alias. It is recommended to switch playbook
tasks to use the new module names. This section includes new return
values.

zos_apf
-------

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Sub-option renamed:

  * ``persistent.data_set_name`` → ``persistent.target`` (old name still accepted)
  * Recommendation: Use ``target`` in new playbooks

* New return value: ``stdout_lines``
* New return value: ``stderr_lines``

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Add a library (cataloged) to a persistent APF list
     zos_apf:
       library: SOME.SEQUENTIAL.DATASET
       force_dynamic: true
       persistent:
         data_set_name: SOME.PARTITIONED.DATASET(MEM)

   # After (v2.0.0)
   - name: Add a library (cataloged) to a persistent APF list
     zos_apf:
       library: SOME.SEQUENTIAL.DATASET
       force_dynamic: true
       persistent:
         target: SOME.PARTITIONED.DATASET(MEM)

.. code-block:: json

   // Before (v1.x)
   {
     "changed": true,
     "stdout": "APF list updated",
     "stderr": "",
     "rc": 0
   }

   // After (v2.0.0)
   {
     "changed": true,
     "stdout": "APF list updated",
     "stdout_lines": ["APF list updated"],
     "stderr": "",
     "stderr_lines": [],
     "rc": 0
   }

.. _zos_archive:

zos_archive
-----------

Breaking changes
^^^^^^^^^^^^^^^^

* Sub-options renamed:

  * ``format.format_options`` → ``format.options``.
  * ``format.format_options.use_adrdssu`` → ``format.options.adrdssu``.
  * ``format.format_options.terse_pack`` → ``format.options.spack``.

    * the type has changed from ``string`` to ``bool``.
    * ``spack=true`` uses 'spack' as the compression algorithm, while ``spack=false`` uses the pack algorithm.

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Sub-option renamed: ``format.name`` → ``format.type`` (old name still accepted).

  * Recommendation: Use ``name`` in new playbooks.

* New return value: ``dest``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Archive data set into a terse, specify spack algorithm and use adrdssu.
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         name: terse
         format_options:
           terse_pack: "spack"
           use_adrdssu: true

   # After (v2.0.0)
   - name: Archive data set into a terse, specify spack algorithm and use adrdssu
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         type: terse
         options:
           spack: true
           adrdssu: true

   # Before (v1.x)
   - name: Archive data set into a terse
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         name: terse

   # After (v2.0.0)
   - name: Archive data set into a terse
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         type: terse

.. code-block:: json

   // Before (v1.x)
   {
     "changed": true,
     "state": "present",
     "dest_state": "archive",
     "missing": [],
     "archived": ["USER.ARCHIVE.TEST"]
   }

   // After (v2.0.0)
   {
     "changed": true,
     "dest": "USER.ARCHIVE.RESULT.TRS",
     "state": "present",
     "dest_state": "archive",
     "missing": [],
     "archived": ["USER.ARCHIVE.TEST"]
   }

.. _zos_backup_restore:

zos_backup_restore
------------------

Breaking changes
^^^^^^^^^^^^^^^^

* Module options renamed:

  * ``hlq`` → ``output.hlq``.
  * ``sms_storage_class`` → ``sms.storage_class``.
  * ``sms_management_class`` → ``sms.management_class``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Restore data sets with new HLQ
     zos_backup_restore:
       operation: restore
       data_sets:
         include: "**.TEST"
       backup_name: /tmp/temp_backup.dzp
       hlq: MYHLQ
       sms_storage_class: SCLAS1
       sms_management_class: MCLAS1

   # After (v2.0.0)
   - name: Restore data sets with new HLQ
     zos_backup_restore:
       operation: restore
       data_sets:
         include: "**.TEST"
       backup_name: /tmp/temp_backup.dzp
       output:
         hlq: MYHLQ
       sms:
         storage_class: SCLAS1
         management_class: MCLAS1

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* New module option: ``access`` (with suboptions: ``share``, ``auth``).
* New module option: ``index``.
* New SMS suboptions: ``disable_automatic_class``, ``disable_automatic_storage_class``, ``disable_automatic_management_class``.

Examples
^^^^^^^^

.. code-block:: yaml

   # New access option allows control over data set sharing
   - name: Backup with shared access
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.**
       backup_name: MY.BACKUP.DZP
       access:
         share: true
         auth: false

   # New index option for VSAM clusters
   - name: Backup VSAM with alternate indexes
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.vsam.**
       backup_name: MY.BACKUP.DZP
       index: true

   # New SMS disable options for fine-grained control
   - name: Restore without ACS routines
     zos_backup_restore:
       operation: restore
       backup_name: /tmp/temp_backup.dzp
       sms:
         storage_class: SCLAS1
         disable_automatic_class:
           - "USER.TEST.**"
           - "USER.PROD.**"

.. _zos_blockinfile:

zos_blockinfile
---------------

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Module option aliases:

  * ``insertafter`` can be referenced as ``after``.
  * ``insertbefore`` can be referenced as ``before``.

* New return value: ``stdout_lines``.
* New return value: ``stderr_lines``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Insert block after specific line
     zos_blockinfile:
       src: /etc/profile
       insertafter: "PATH="
       block: |
         ZOAU=/path/to/zoau
         export ZOAU

   # After (v2.0.0)
   - name: Insert block after specific line
     zos_blockinfile:
       src: /etc/profile
       after: "PATH="
       block: |
         ZOAU=/path/to/zoau
         export ZOAU

.. code-block:: json

   // Before (v1.x)
   {
     "changed": true,
     "found": 1,
     "cmd": "dmod -d -b -c IBM-1047...",
     "backup_name": ""
   }

   // After (v2.0.0)
   {
     "changed": true,
     "found": 1,
     "cmd": "dmod -d -b -c IBM-1047...",
     "stdout": "",
     "stdout_lines": [],
     "stderr": "",
     "stderr_lines": [],
     "backup_name": ""
   }

.. _zos_copy:

zos_copy
--------

Breaking changes
^^^^^^^^^^^^^^^^

* Module options renamed:

  * ``is_binary`` → ``binary``.
  * ``force`` → ``replace``.

    * **NOTE**: option ``force`` remains a *valid* module option with **different** functionality.

  * ``force_lock`` → ``force``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Copy a z/OS UNIX file to a sequential data set, overwriting content in the data set.
     ibm.ibm_zos_core.zos_copy:
       src: /path/to/uss/src
       dest: SAMPLE.SEQ.DATA.SET
       force: true
       remote_src: true

   # After (v2.0.0)
   - name: Copy a z/OS UNIX file to a sequential data set, overwriting content in the data set.
     ibm.ibm_zos_core.zos_copy:
       src: /path/to/uss/src
       dest: SAMPLE.SEQ.DATA.SET
       replace: true
       remote_src: true

   # Before (v1.x)
   - name: Copy binary content from a PDS member to a PDS/E member, bypassing the disposition (DISP) on the PDS/E member.
     ibm.ibm_zos_core.zos_copy:
       src: SAMPLE.PDS.DATA.SET(MEM)
       dest: SAMPLE.PDSE.DATA.SET(MEM)
       is_binary: true
       force_lock: true
       remote_src: true

   # After (v2.0.0)
   - name: Copy binary content from a PDS member to a PDS/E member, bypassing the disposition (DISP) on the PDS/E member.
     ibm.ibm_zos_core.zos_copy:
       src: SAMPLE.PDS.DATA.SET(MEM)
       dest: SAMPLE.PDSE.DATA.SET(MEM)
       binary: true
       force: true
       remote_src: true

.. _zos_data_set:

zos_data_set
------------

Breaking changes
^^^^^^^^^^^^^^^^

* Return value renamed: ``names`` → ``data_sets``.

Examples
^^^^^^^^

.. code-block:: json

   // Before (v1.x)
   {
     "changed": true,
     "names": [
       "USER.TEST.DS1",
       "USER.TEST.DS2"
     ]
   }

   // After (v2.0.0)
   {
     "changed": true,
     "data_sets": [
       "USER.TEST.DS1",
       "USER.TEST.DS2"
     ]
   }

.. _zos_fetch:

zos_fetch
---------

Breaking changes
^^^^^^^^^^^^^^^^

* Module option renamed: ``is_binary`` → ``binary``.
* Return values renamed:

  * ``file`` → ``src``.
  * ``is_binary`` → ``binary``.
  * ``note`` → ``msg``.

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* New return value: ``encoding`` (with ``from``/``to`` suboptions).
* New return values: ``stdout``, ``stderr``, ``stdout_lines``, ``stderr_lines``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Fetch a PDS as binary
     zos_fetch:
       src: SOME.PDS.DATASET
       dest: /tmp/
       flat: true
       is_binary: true

   # After (v2.0.0)
   - name: Fetch a PDS as binary
     zos_fetch:
       src: SOME.PDS.DATASET
       dest: /tmp/
       flat: true
       binary: true

.. code-block:: json

   // Before (v1.x)
   {
     "file": "ANSIBLE.PWLZCFEB.T2417849.CICFWKBY.G0001V00",
     "dest": "/tmp/ANSIBLE.PWLZCFEB.T2417849.CICFWKBY.G0001V00",
     "is_binary": false,
     "checksum": "8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e",
     "changed": true,
     "data_set_type": "PS",
     "note": "",
     "msg": "",
     "rc": 0
   }
   // After (v2.0.0)
   {
     "src": "ANSIBLE.PWLZCFEB.T2417849.CICFWKBY.G0001V00",
     "dest": "/tmp/ANSIBLE.PWLZCFEB.T2417849.CICFWKBY.G0001V00",
     "binary": false,
     "checksum": "8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e",
     "changed": true,
     "data_set_type": "PS",
     "msg": "",
     "stdout": "",
     "stderr": "",
     "stdout_lines": [],
     "stderr_lines": [],
     "rc": 0,
     "encoding": {
         "from": "IBM-1047",
         "to": "UTF-8"
     }
   }

.. _zos_find:

zos_find
--------

Breaking changes
^^^^^^^^^^^^^^^^

* Module option removed: ``pds_patterns`` (and its aliases: ``pds_paths``, ``pds_pattern``).

  * In v1.x, this option was used to specify PDS/PDSE data sets to search for members.
  * In v2.0.0, use the ``patterns`` option with PDS member syntax: ``DATASET.NAME(MEMBER*)``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Find members in specific PDS data sets
     zos_find:
       pds_patterns:
         - "USER.*.PDS"
         - "SYS1.PROCLIB"
       patterns:
         - "MEM*"
         - "TEST*"

   # After (v2.0.0)
   - name: Find members using combined pattern syntax
     zos_find:
       patterns:
         - "USER.*.PDS(MEM*)"
         - "USER.*.PDS(TEST*)"
         - "SYS1.PROCLIB(MEM*)"
         - "SYS1.PROCLIB(TEST*)"

.. _zos_job_output:

zos_job_output
--------------

Breaking changes
^^^^^^^^^^^^^^^^

* Return values renamed:

  * ``ddnames`` → ``dds``.
  * ``ddnames[].ddname`` → ``dds[].dd_name``.

* Return value moved: ``ret_code.steps`` → ``steps`` (moved from inside ret_code to job level).

Examples
^^^^^^^^

.. code-block:: json

   // Before (v1.x)
   {
     "jobs": [
       {
         "job_id": "JOB00134",
         "job_name": "HELLO",
         "ret_code": {
           "code": 0,
           "msg": "CC 0000",
           "msg_code": "0000",
           "msg_txt": "",
           "steps": [
             {
               "step_name": "STEP0001",
               "step_cc": 0
             }
           ]
         },
         "ddnames": [
           {
             "ddname": "JESMSGLG",
             "record_count": 17,
             "id": "2",
             "content": ["..."]
           }
         ]
       }
     ]
   }

   // After (v2.0.0)
   {
     "jobs": [
       {
         "job_id": "JOB00134",
         "job_name": "HELLO",
         "ret_code": {
           "code": 0,
           "msg": "CC 0000",
           "msg_code": "0000",
           "msg_txt": ""
         },
         "steps": [
           {
             "step_name": "STEP0001",
             "step_cc": 0
           }
         ],
         "dds": [
           {
             "dd_name": "JESMSGLG",
             "record_count": 17,
             "id": "2",
             "content": ["..."]
           }
         ]
       }
     ]
   }

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Module option renamed: ``ddname`` → ``dd_name`` (old name still accepted).

  * Recommendation: Use ``dd_name`` in new playbooks.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Job output with ddname
     zos_job_output:
       job_id: "STC02560"
       ddname: "JESMSGLG"

   # After (v2.0.0)
   - name: Job output with dd_name
     zos_job_output:
       job_id: "STC02560"
       dd_name: "JESMSGLG"

.. _zos_job_query:

zos_job_query
-------------

Breaking changes
^^^^^^^^^^^^^^^^

* Return value moved: ``ret_code.steps`` → ``steps`` (moved from inside ret_code to job level).
* Return value removed: ``message`` (top-level return value removed).

Examples
^^^^^^^^

.. code-block:: json

   // Before (v1.x)
   {
     "changed": false,
     "jobs": [
       {
         "job_name": "LINKJOB",
         "owner": "ADMIN",
         "job_id": "JOB01427",
         "ret_code": {
           "msg": "CC 0000",
           "msg_code": "0000",
           "code": 0,
           "msg_txt": "",
           "steps": [
             {
               "step_name": "STEP0001",
               "step_cc": 0
             }
           ]
         }
       }
     ],
     "message": "Job query completed successfully"
   }

   // After (v2.0.0)
   {
     "changed": false,
     "jobs": [
       {
         "job_name": "LINKJOB",
         "owner": "ADMIN",
         "job_id": "JOB01427",
         "ret_code": {
           "msg": "CC 0000",
           "msg_code": "0000",
           "code": 0,
           "msg_txt": ""
         },
         "steps": [
           {
             "step_name": "STEP0001",
             "step_cc": 0
           }
         ]
       }
     ]
   }

.. _zos_job_submit:

zos_job_submit
--------------

Breaking changes
^^^^^^^^^^^^^^^^

* Module option removed: ``location`` (choices: data_set, uss, local).

  * Use new module option ``remote_src`` (boolean).
  * ``location=data_set`` or ``location=uss`` → ``remote_src=true``.
  * ``location=local`` → ``remote_src=false``.

* Module option renamed: ``wait_time_s`` → ``wait_time``.
* Return values renamed:

  * ``ddnames`` → ``dds``.
  * ``ddnames[].ddname`` → ``dds[].dd_name``.

* Return value moved: ``ret_code.steps`` → ``steps`` (moved from inside ret_code to job level).

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x) - Submit from data set
   - name: Submit a job from JCL stored in a PDS member and wait up to 30 seconds for completion.
     zos_job_submit:
       src: HLQ.DATA.LLQ(LONGRUN)
       location: data_set
       wait_time_s: 30

   # After (v2.0.0) - Submit from data set
   - name: Submit a job from JCL stored in a PDS member and wait up to 30 seconds for completion.
     zos_job_submit:
       src: HLQ.DATA.LLQ(LONGRUN)
       remote_src: true
       wait_time: 30

   # Before (v1.x) - Submit from local file
   - name: Submit JCL from local file
     zos_job_submit:
       src: /local/path/job.jcl
       location: local
       wait_time_s: 60

   # After (v2.0.0) - Submit from local file
   - name: Submit JCL from local file
     zos_job_submit:
       src: /local/path/job.jcl
       remote_src: false
       wait_time: 60

.. code-block:: json

   // Before (v1.x)
   {
     "changed": true,
     "jobs": [
       {
         "job_id": "JOB00361",
         "job_name": "DBDGEN00",
         "job_class": "K",
         "ret_code": {
           "msg": "CC 0000",
           "code": 0,
           "steps": [
             {
               "step_name": "STEP0001",
               "step_cc": 0
             }
           ]
         },
         "ddnames": [
           {
             "ddname": "JESMSGLG",
             "record_count": 16,
             "id": "2",
             "content": ["..."]
           }
         ]
       }
     ]
   }

   // After (v2.0.0)
   {
     "changed": true,
     "jobs": [
       {
         "job_id": "JOB00361",
         "job_name": "DBDGEN00",
         "job_class": "K",
         "ret_code": {
           "msg": "CC 0000",
           "code": 0
         },
         "steps": [
           {
             "step_name": "STEP0001",
             "step_cc": 0
           }
         ],
         "dds": [
           {
             "dd_name": "JESMSGLG",
             "record_count": 16,
             "id": "2",
             "content": ["..."]
           }
         ]
       }
     ]
   }

.. _zos_lineinfile:

zos_lineinfile
--------------

Breaking changes
^^^^^^^^^^^^^^^^

* Return value renamed: ``return_content`` → ``stdout``.

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Module option aliases:

  * ``insertafter`` can be referenced as ``after``.
  * ``insertbefore`` can be referenced as ``before``.

* New return values: ``stderr``, ``stdout_lines``, ``stderr_lines``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Insert a line in a data set
     zos_lineinfile:
       src: USER.TEST.DS
       line: "export PATH=/new/path:$PATH"
       insertafter: "^export"
     register: result

   - debug:
       msg: "{{ result.return_content }}"

   # After (v2.0.0)
   - name: Insert a line in a data set
     zos_lineinfile:
       src: USER.TEST.DS
       line: "export PATH=/new/path:$PATH"
       insertafter: "^export"  # Can also use 'after' alias
     register: result

   - debug:
       msg: "{{ result.stdout }}"

.. code-block:: json

   // Before (v1.x)
   {
   "changed": true,
   "cmd": "",
   "found": 1,
   "return_content": "{ \"cmd\": \"dsedhelper -d -c IBM-1047 -s -e /ZOAU_ROOT=/a\\\\\\\\ZOAU_ROOT=/mvsutil-develop_dsed/$ -e $ a\\\\\\\\ZOAU_ROOT=/mvsutil-develop_dsed ANSIBLE.PQWQE2RW.T4619709.CUEB9A5Q \", \"found\": 1, \"changed\": true }",
   "stderr": "",
   "rc": 0,
   "backup_name": ""
   }
   // After (v2.0.0)
   {
   "changed": true,
   "cmd": "",
   "found": 1,
   "stdout": "{ \"cmd\": \"dsedhelper -d -c IBM-1047 -s -e /ZOAU_ROOT=/a\\\\\\\\ZOAU_ROOT=/mvsutil-develop_dsed/$ -e $ a\\\\\\\\ZOAU_ROOT=/mvsutil-develop_dsed ANSIBLE.PQWQE2RW.T4619709.CUEB9A5Q \", \"found\": 1, \"changed\": true }",
   "stdout_lines": ["{ \"cmd\": \"dsedhelper -d -c IBM-1047 -s -e /ZOAU_ROOT=/a\\\\\\\\ZOAU_ROOT=/mvsutil-develop_dsed/$ -e $ a\\\\\\\\ZOAU_ROOT=/mvsutil-develop_dsed ANSIBLE.PQWQE2RW.T4619709.CUEB9A5Q \", \"found\": 1, \"changed\": true }"],
   "stderr": "",
   "stderr_lines": [],
   "rc": 0,
   "backup_name": ""
   }

.. _zos_mount:

zos_mount
---------

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Sub-options renamed:

  * ``persistent.data_store`` → ``persistent.name`` (old name still accepted).
  * ``persistent.comment`` → ``persistent.marker`` (old name still accepted).
  * Recommendation: Use new names in new playbooks.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Mount a filesystem with persistent configuration
     zos_mount:
       path: /mnt/myfs
       src: USER.ZFS.DATASET
       fs_type: zfs
       state: mounted
       persistent:
         data_store: SYS1.PARMLIB(BPXPRM00)
         comment:
           - "# Managed by Ansible"
           - "# Do not modify manually"

   # After (v2.0.0) - Recommended to use new names
   - name: Mount a filesystem with persistent configuration
     zos_mount:
       path: /mnt/myfs
       src: USER.ZFS.DATASET
       fs_type: zfs
       state: mounted
       persistent:
         name: SYS1.PARMLIB(BPXPRM00)  # Can still use data_store
         marker:  # Can still use comment
           - "# Managed by Ansible"
           - "# Do not modify manually"

.. _zos_operator:

zos_operator
------------

Breaking changes
^^^^^^^^^^^^^^^^

* Module option renamed: ``wait_time_s`` → ``wait_time``.

  * Use in conjunction with new option ``time_unit`` to indicate seconds/centiseconds.

* Return value removed: ``content`` (replaced by ``stdout``, ``stderr``, ``stdout_lines`` and ``stderr_lines``).
* Return value renamed: ``wait_time_s`` → ``wait_time``.

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* New module option: ``time_unit`` (choices: ``s``, ``cs``).
* New return values: ``stdout``, ``stdout_lines``, ``stderr``, ``stderr_lines``, ``time_unit``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Execute operator command with 5 second wait
     zos_operator:
       cmd: 'd a,all'
       wait_time_s: 5
     register: result

   - debug:
       msg: "{{ result.content }}"

   # After (v2.0.0) - Default time_unit is 's' (seconds)
   - name: Execute operator command with 5 second wait
     zos_operator:
       cmd: 'd a,all'
       wait_time: 5
       time_unit: s  # Optional, 's' is default
     register: result

   - debug:
       msg: "{{ result.stdout_lines }}"  # Use stdout_lines instead of content

   # After (v2.0.0) - Using centiseconds
   - name: Execute operator command with 500 centisecond (5 second) wait
     zos_operator:
       cmd: 'd a,all'
       wait_time: 500
       time_unit: cs
     register: result

.. code-block:: json

   // Before (v1.x)
   {
     "changed": true,
     "rc": 0,
     "cmd": "d u,all",
     "elapsed": 0.52,
     "wait_time_s": 5,
     "content": [
       "EC33017A   2022244  16:00:49.00             ISF031I CONSOLE OMVS0000 ACTIVATED",
       "EC33017A   2022244  16:00:49.00            -D U,ALL ",
       "EC33017A   2022244  16:00:49.00             IEE457I 16.00.49 UNIT STATUS 645"
     ]
   }

   // After (v2.0.0)
   {
     "changed": true,
     "rc": 0,
     "cmd": "d u,all",
     "elapsed": 0.52,
     "wait_time": 5,
     "time_unit": "s",
     "stdout": "EC33017A   2022244  16:00:49.00             ISF031I CONSOLE OMVS0000 ACTIVATED\nEC33017A   2022244  16:00:49.00            -D U,ALL \nEC33017A   2022244  16:00:49.00             IEE457I 16.00.49 UNIT STATUS 645",
     "stdout_lines": [
       "EC33017A   2022244  16:00:49.00             ISF031I CONSOLE OMVS0000 ACTIVATED",
       "EC33017A   2022244  16:00:49.00            -D U,ALL ",
       "EC33017A   2022244  16:00:49.00             IEE457I 16.00.49 UNIT STATUS 645"
     ],
     "stderr": "",
     "stderr_lines": []
   }

.. _zos_operator_action_query:

zos_operator_action_query
--------------------------

Breaking changes
^^^^^^^^^^^^^^^^

* Module option renamed: ``use_regex`` → ``literal``.

  * **Note:** ``literal`` is the inverse of ``use_regex`` (behavior is reversed).

* Return values renamed:

  * ``message_text`` → ``msg_text``.
  * ``message_id`` → ``msg_id``.

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* Module options renamed:

  * ``message_filter`` → ``msg_filter`` (old name still accepted).
  * ``message_id`` → ``msg_id`` (old name still accepted).
  * Recommendation: Use new names in new playbooks.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Display all outstanding messages where the job name begins with 'mq',
         message ID begins with 'dsi', on system 'mv29' and which contain the
         pattern 'IMS'
     zos_operator_action_query:
       job_name: mq*
       message_id: dsi*
       system: mv29
       message_filter:
           filter: ^.*IMS.*$
           use_regex: true
   # After (v2.0.0)
   - name: Display all outstanding messages where the job name begins with 'mq',
         message ID begins with 'dsi', on system 'mv29' and which contain the
         pattern 'IMS'
     zos_operator_action_query:
       job_name: mq*
       msg_id: dsi*
       system: mv29
       msg_filter:
           filter: ^.*IMS.*$
           literal: false

.. code-block:: json

   // Before (v1.x)
   {
       "changed": false,
       "count": 2,
       "actions": [
           {
               "number": "89",
               "type": "R",
               "system": "EC01133A",
               "message_text": "IEE094D SPECIFY OPERAND(S) FOR DUMP",
               "message_id": "IEE094D"
           },
           {
               "number": "88",
               "type": "R",
               "system": "EC01133A",
               "message_text": "IEE094D SPECIFY OPERAND(S) FOR DUMP",
               "message_id": "IEE094D"
           }
       ]
   }
   // After (v2.0.0)
   {
     "changed": false,
     "count": 2,
     "actions": [
         {
             "number": "89",
             "type": "R",
             "system": "EC01133A",
             "msg_text": "IEE094D SPECIFY OPERAND(S) FOR DUMP",
             "msg_id": "IEE094D"
         },
         {
             "number": "88",
             "type": "R",
             "system": "EC01133A",
             "msg_text": "IEE094D SPECIFY OPERAND(S) FOR DUMP",
             "msg_id": "IEE094D"
         }
     ]
   }

.. _zos_tso_command:

zos_tso_command
---------------

Breaking changes
^^^^^^^^^^^^^^^^

* Return values renamed:

  * ``content`` → ``stdout``.
  * ``lines`` → ``line_count``.

Non-breaking changes
^^^^^^^^^^^^^^^^^^^^

* New return values: ``stdout`` (string version), ``stdout_lines`` (replaces ``content`` list), ``stderr_lines``.

Examples
^^^^^^^^

.. code-block:: json

   // Before (v1.x)
   {
       "changed": true,
       "output":
           [
               {
                   "command": "help",
                   "rc": 0,
                   "content": [
                       "LANGUAGE PROCESSING COMMANDS: ",
                       " ",
                       "ASM        INVOKE ASSEMBLER PROMPTER AND ASSEMBLER F COMPILER. ",
                       "CALC       INVOKE ITF:PL/1 PROCESSOR FOR DESK CALCULATOR MODE. ",
                       "COBOL      INVOKE COBOL PROMPTER AND ANS COBOL COMPILER. ",
                       "FORT       INVOKE FORTRAN PROMPTER AND FORTRAN IV G1 COMPILER. ",
                       " ",
                       "PROGRAM CONTROL COMMANDS: "
                   ],
                   "lines": 87,
                   "stderr": "",
                   "failed": false,
               }
           ],
       "max_rc": 0
   }
   // After (v2.0.0)
   {
       "changed": true,
       "output":
           [
               {
                   "command": "help",
                   "rc": 0,
                   "stdout": "LANGUAGE PROCESSING COMMANDS: \nASM        INVOKE ASSEMBLER PROMPTER AND ASSEMBLER F COMPILER. \nCALC       INVOKE ITF:PL/1 PROCESSOR FOR DESK CALCULATOR MODE. \nCOBOL      INVOKE COBOL PROMPTER AND ANS COBOL COMPILER. \nFORT       INVOKE FORTRAN PROMPTER AND FORTRAN IV G1 COMPILER. \n \nPROGRAM CONTROL COMMANDS:",
                   "stdout_lines": [
                       "LANGUAGE PROCESSING COMMANDS: ",
                       " ",
                       "ASM        INVOKE ASSEMBLER PROMPTER AND ASSEMBLER F COMPILER. ",
                       "CALC       INVOKE ITF:PL/1 PROCESSOR FOR DESK CALCULATOR MODE. ",
                       "COBOL      INVOKE COBOL PROMPTER AND ANS COBOL COMPILER. ",
                       "FORT       INVOKE FORTRAN PROMPTER AND FORTRAN IV G1 COMPILER. ",
                       " ",
                       "PROGRAM CONTROL COMMANDS: "
                   ],
                   "line_count": 87,
                   "stderr": "",
                   "stderr_lines": [],
                   "failed": false,
               }
           ],
       "max_rc": 0
   }

.. _zos_unarchive:

zos_unarchive
-------------

Breaking changes
^^^^^^^^^^^^^^^^

* Sub-options renamed:

  * ``format.name`` → ``format.type``.
  * ``format.format_options`` → ``format.options``.
  * ``format.format_options.use_adrdssu`` → ``format.options.adrdssu``.

Examples
^^^^^^^^

.. code-block:: yaml

   # Before (v1.x)
   - name: Unarchive a terse data set with ADRDSSU
     zos_unarchive:
       src: USER.ARCHIVE.TERSE
       format:
         name: terse
         format_options:
           use_adrdssu: true
           dest_volumes:
             - VOL001
       dest: USER.RESTORED.DATA

   # After (v2.0.0)
   - name: Unarchive a terse data set with ADRDSSU
     zos_unarchive:
       src: USER.ARCHIVE.TERSE
       format:
         type: terse
         options:
           adrdssu: true
           dest_volumes:
             - VOL001
       dest: USER.RESTORED.DATA

   # Before (v1.x) - XMIT format
   - name: Unarchive an XMIT archive
     zos_unarchive:
       src: USER.ARCHIVE.XMIT
       format:
         name: xmit
         format_options:
           xmit_log_data_set: USER.XMIT.LOG
       dest: USER.RESTORED.DATA

   # After (v2.0.0) - XMIT format
   - name: Unarchive an XMIT archive
     zos_unarchive:
       src: USER.ARCHIVE.XMIT
       format:
         type: xmit
         options:
           xmit_log_data_set: USER.XMIT.LOG
       dest: USER.RESTORED.DATA


Using the playbook upgrade validator role
=========================================

The ``playbook_upgrade_validator`` role helps automate the process of
identifying migration changes needed in your playbooks when upgrading
from ibm_zos_core v1.x to v2.0.0. This role analyzes your playbooks and
generates a detailed report of all breaking and non-breaking changes
that need attention.

Importance of role
------------------

The role validates one or more Ansible playbooks against IBM z/OS Core
migration rules and generates a detailed report of required changes. For
each task using an ibm_zos_core module, it identifies:

- **Renamed parameters** - Module options that have new names (reported
  as ``[MUST_FIX]``).
- **Type-changed parameters** - Module options with modified data types
  (reported as ``[MUST_FIX]``).
- **Response parameter changes** - Return values that are renamed
  or restructured (reported as ``[WARNING]``).

The report includes the exact playbook path, play name, task name, line
number, and specific migration actions needed for each affected task.

Role variables
--------------

The following variables can be configured:

- **``playbook_path``** (required): Path to a single Ansible playbook
  file or a directory that has playbooks to validate.
- **``output_path``** (optional): Path to the output JSON file where
  validation results are saved. If the path is not provided then it defaults to
  ``{{ playbook_dir }}/logs/migration_report.json``.
- **``ignore_response_params``** (optional): Boolean flag to omit
  response parameter changes from the report. Defaults to ``false``.

Usage example
-------------

Create a playbook (e.g., ``validate_migration.yml``) to run the
validator role:

.. code:: yaml

   ---
   - name: Validate playbooks for migration to ibm_zos_core v2.0.0
     hosts: localhost
     gather_facts: false
     roles:
       - role: ibm.ibm_zos_core.playbook_upgrade_validator
         vars:
           playbook_path: "/path/to/your/playbooks"
           output_path: "/path/to/migration_report.json"
           ignore_response_params: false

Running the validator
---------------------

Execute the playbook from above:

.. code:: bash

   ansible-playbook validate_migration.yml

Understanding the output
-------------------------

The role generates a JSON report that has detailed information about
required changes. The report includes:

- **File path and line numbers** - Exact locations of tasks that need
  updates.
- **Module name** - The name of z/OS Core module which is affected.
- **Parameter details** - Old and new parameter names, types, and
  descriptions.
- **Migration actions** - Specific steps needed to update your playbooks.

Example for output structure
-----------------------------

The validator generates a JSON array where each element represents a
task that requires migration changes:

.. code:: json

   [
     {
       "playbook": "/path/to/playbook.yml",
       "play_name": "My Play Name",
       "task_name": "Submit batch job",
       "module": "ibm.ibm_zos_core.zos_job_submit",
       "task_line": 110,
       "migration_actions": [
         "[MUST_FIX] Param 'location' is renamed to 'remote_src' in ibm.ibm_zos_core.zos_job_submit",
         "[MUST_FIX] Param 'wait_time_s' is renamed to 'wait_time' in ibm.ibm_zos_core.zos_job_submit",
         "[MUST_FIX] Param 'location' type changed from 'string' to 'boolean' in ibm.ibm_zos_core.zos_job_submit",
         "[WARNING] Response param 'ddnames' is renamed to 'dds' in ibm.ibm_zos_core.zos_job_submit",
         "[WARNING] Response param 'ddnames.ddname' is renamed to 'dds.dd_name' in ibm.ibm_zos_core.zos_job_submit",
         "[WARNING] Response param 'ret_code.steps' is renamed to 'jobs.steps' in ibm.ibm_zos_core.zos_job_submit"
       ]
     },
     {
       "playbook": "/path/to/playbook.yml",
       "play_name": "My Play Name",
       "task_name": "Execute operator command",
       "module": "ibm.ibm_zos_core.zos_operator",
       "task_line": 136,
       "migration_actions": [
         "[MUST_FIX] Param 'wait_time_s' is renamed to 'wait_time' in ibm.ibm_zos_core.zos_operator",
         "[WARNING] Response param 'wait_time_s' is renamed to 'wait_time' in ibm.ibm_zos_core.zos_operator"
       ]
     }
   ]

Each entry includes:
 - **playbook**: Full path to the playbook file.
 - **play_name**: Name of the play containing the task. 
 - **task_name**: Name of the task that needs changes. 
 - **module**: Fully qualified module name. 
 - **task_line**: Line number where the task appears in the playbook.
 - **migration_actions**: Array of required changes, prefixed with:

   - ``[MUST_FIX]``- Breaking changes that must be addressed.
   - ``[WARNING]`` - Response parameter changes (if ``ignore_response_params`` is false).

Best Practices
--------------

1. **Run early** - Before you start your migration, run the validator
   to understand the scope of changes.
2. **Review thoroughly** - Examine the generated report to prioritize
   breaking changes.
3. **Test incrementally** - Update and test playbooks in small batches.
4. **Keep reports** - Save validation reports for documentation and
   audit purposes.
5. **Re-validate** - To ensure all the issues are addressed, 
   run the validator again after making changes.

Notes
-----

- Task line numbers in the report rely on task names and can be
  ambiguous when duplicate task names exist within a playbook.
- The role runs on the control node (localhost) and does not require
  internet connection to z/OS systems.
- Ensure that Python 3 is available on the control node for the validator to
  run.