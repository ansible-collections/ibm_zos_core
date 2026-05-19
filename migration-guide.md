# 🚀 Ansible z/OS Core Collection Migration Guide: Ansible Collection `ibm.ibm_zos_core` v1.x → v2.0.0

This guide covers breaking and recommended changes for upgrading playbooks and roles to ibm.ibm_zos_core **v2.0.0**, including updates to module options and return values.

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Breaking and Non-Breaking Changes](#-breaking-and-non-breaking-changes)

* [zos_apf](#zos_apf)
* [zos_archive](#zos_archive)
* [zos_backup_restore](#zos_bakup_restore)
* [zos_blockinfile](#zos_blockinfile)
* [zos_copy](#zos_copy)
* [zos_data_set](#zos_data_set)
* [zos_fetch](#zos_fetch)
* [zos_find](#zos_find)
* [zos_job_output](#zos_job_output)
* [zos_job_query](#zos_job_query)
* [zos_job_submit](#zos_job_submit)
* [zos_lineinfile](#zos_lineinfile)
* [zos_mount](#zos_mount)
* [zos_operator](#zos_operator)
* [zos_operator_action_query](#zos_operator_action_query)
* [zos_tso_command](#zos_tso_command)
* [zos_unarchive](#zos_unarchive)

---

## 🧭 Overview

The changes introduced in version 2.0 enhance consistency and automation reliability through
standardized naming conventions and predictable return structures.

**Key Improvements:**

* **Consistent naming** - Module option names and return values are standardized across the collection.
* **Predictable returns** - Return values are always present and tailored for automation, rather than being dynamically created based on module operation results.

**Impact on Existing Playbooks:**

To achieve consistent naming across the collection, some module options and return values have been renamed:

* **Breaking changes** - Some module options and return values have new names with no backward compatibility.
* **Aliased changes** - Other module options have new primary names, with old names still supported as aliases.


---

## 🚨 Breaking and Non-Breaking Changes

Breaking changes are all the module options that have been renamed where the old names will no longer work. It also includes any return values which have been renamed. Any automation which relies on these value will need to be updated.

Non-breaking changes are all the module options that have been renamed for consistency across the collection, but still have the old module option name available as an alias. It is recommended to switch playbook tasks to use the new module names. This section also includes new return values.



#### zos_apf

non-breaking:
* Primary name changed: persistent.data_set_name → persistent.target
  * In v1.x: data_set_name was primary, target was alias
  * In v2.0.0: target is primary, data_set_name is alias
  * Both names continue to work (non-breaking change)
  * Recommended: Use 'target' in new playbooks
* new return value: stdout_lines
* new return value: stderr_lines

Recommended actions:
```yaml
# Before
- name: Add a library (cataloged) to the APF list and persistence
  zos_apf:
    library: SOME.SEQUENTIAL.DATASET
    force_dynamic: true
    persistent:
      data_set_name: SOME.PARTITIONED.DATASET(MEM)

# After
- name: Add a library (cataloged) to the APF list and persistence
  zos_apf:
    library: SOME.SEQUENTIAL.DATASET
    force_dynamic: true
    persistent:
      target: SOME.PARTITIONED.DATASET(MEM)
```

```json
// Before
{
  "changed": true,
  "stdout": "APF list updated",
  "stderr": "",
  "rc": 0
}

// After
{
  "changed": true,
  "stdout": "APF list updated",
  "stdout_lines": ["APF list updated"],
  "stderr": "",
  "stderr_lines": [],
  "rc": 0
}
```


#### zos_archive
breaking:
* module sub-option renamed: ``format.format_options`` is renamed to ``format.options``.
* module sub-option renamed: ``format.format_options.use_adrdssu`` is renamed to ``format.options.adrdssu``.
* module sub-option renamed: ``format.format_options.terse_pack`` is renamed to ``format.options.spack``.
  * the type has changed from ``string`` to ``bool``.
  * ``spack=True`` uses 'spack' as the compression algorithm, while ``spack=False`` uses the pack algorithm.

Required actions:
```yaml
# Before
- name: Archive data set into a terse, specify pack algorithm and use adrdssu.
  zos_archive:
    src: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      name: terse
      format_options:
        terse_pack: "spack"
        use_adrdssu: true

# After
- name: Archive data set into a terse, specify pack algorithm and use adrdssu
  zos_archive:
    src: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      type: terse
      options:
        spack: true
        adrdssu: true
```

non-breaking:
* module option renamed: format.name ↔ format.type (aliases preserved - both names work in v2.0.0)
* new return value: dest

Recommended actions:
```yaml
# Before
- name: Archive data set into a terse
  zos_archive:
    src: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      name: terse

# After
- name: Archive data set into a terse
  zos_archive:
    src: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      type: terse
```

```json
// Before
{
  "changed": true,
  "state": "present",
  "dest_state": "archive",
  "missing": [],
  "archived": ["USER.ARCHIVE.TEST"]
}

// After
{
  "changed": true,
  "dest": "USER.ARCHIVE.RESULT.TRS",
  "state": "present",
  "dest_state": "archive",
  "missing": [],
  "archived": ["USER.ARCHIVE.TEST"]
}
```

#### zos_backup_restore
breaking:
* module option renamed: ``hlq`` is renamed to ``output.hlq``.
* module option renamed: ``sms_storage_class`` is renamed to ``sms.storage_class``.
* module option renamed: ``sms_management_class`` is renamed to ``sms.management_class``.

Required actions:
```yaml
# Before
- name: Restore data sets with new HLQ
  zos_backup_restore:
    operation: restore
    data_sets:
      include: "**.TEST"
    backup_name: /tmp/temp_backup.dzp
    hlq: MYHLQ
    sms_storage_class: SCLAS1
    sms_management_class: MCLAS1

# After
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
```

non-breaking:
* new module option: access (with suboptions: share, auth)
* new module option: index
* new sms suboptions: disable_automatic_class, disable_automatic_storage_class, disable_automatic_management_class

Recommended actions:
```yaml
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
```

#### zos_blockinfile
non-breaking:
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stdout_lines
* new return value: stderr_lines

Recommended actions:
```yaml
# Before
- name: Insert block after specific line
  zos_blockinfile:
    src: /etc/profile
    insertafter: "PATH="
    block: |
      ZOAU=/path/to/zoau
      export ZOAU

# After
- name: Insert block after specific line
  zos_blockinfile:
    src: /etc/profile
    after: "PATH="
    block: |
      ZOAU=/path/to/zoau
      export ZOAU
```

```json
// Before
{
  "changed": true,
  "found": 1,
  "cmd": "dmod -d -b -c IBM-1047...",
  "backup_name": ""
}

// After
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
```

#### zos_copy
breaking:
* module option renamed: ``is_binary`` is renamed to ``binary``.
* module option renamed: ``force`` is renamed to ``replace``.
  * **NOTE**: option ``force`` remains a _valid_ module option with **different** functionality.
* module option renamed: ``force_lock`` is renamed to ``force``.

Required actions:
```yaml
  # Before
  - name: Copy a z/OS UNIX file to a sequential data set, overwriting content in the data set.
    ibm.ibm_zos_core.zos_copy:
      src: /path/to/uss/src
      dest: SAMPLE.SEQ.DATA.SET
      force: true
      remote_src: true

  # After
  - name: Copy a z/OS UNIX file to a sequential data set, overwriting content in the data set.
    ibm.ibm_zos_core.zos_copy:
      src: /path/to/uss/src
      dest: SAMPLE.SEQ.DATA.SET
      replace: true
      remote_src: true

  # Before
  - name: Copy binary content from a PDS member to a PDS/E member, bypassing the disposition (DISP) on the PDS/E member.
    ibm.ibm_zos_core.zos_copy:
      src: SAMPLE.PDS.DATA.SET(MEM)
      dest: SAMPLE.PDSE.DATA.SET(MEM)
      is_binary: true
      force_lock: true
      remote_src: true

  # After
  - name: Copy binary content from a PDS member to a PDS/E member, bypassing the disposition (DISP) on the PDS/E member.
    ibm.ibm_zos_core.zos_copy:
      src: SAMPLE.PDS.DATA.SET(MEM)
      dest: SAMPLE.PDSE.DATA.SET(MEM)
      binary: true
      force: true
      remote_src: true
```

#### zos_data_set
breaking:
* return value renamed: names -> data_sets

Recommended actions:
```json
// Before
{
  "changed": true,
  "names": [
    "USER.TEST.DS1",
    "USER.TEST.DS2"
  ]
}

// After
{
  "changed": true,
  "data_sets": [
    "USER.TEST.DS1",
    "USER.TEST.DS2"
  ]
}
```

#### zos_fetch
breaking:
* module option renamed: is_binary —> binary (NO alias in v2.0.0)
* return value renamed: file —> src
* return value renamed: is_binary —> binary
* return value renamed: note -> msg

Required actions:
```yaml
# Before
- name: Fetch a PDS as binary
  zos_fetch:
    src: SOME.PDS.DATASET
    dest: /tmp/
    flat: true
    is_binary: true

# After
- name: Fetch a PDS as binary
  zos_fetch:
    src: SOME.PDS.DATASET
    dest: /tmp/
    flat: true
    binary: true
```

```json
// Before
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
// After
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
```

non-breaking:
* new return value: encoding (with from/to suboptions)
* new return value: stdout, stderr, stdout_lines, stderr_lines

Recommended actions:
```json
// The JSON example above demonstrates the new return values.
// Update your playbooks to reference 'src' instead of 'file',
// 'binary' instead of 'is_binary', and 'msg' instead of 'note'.
```

#### zos_find
breaking:
* module option removed: pds_patterns (and its aliases: pds_paths, pds_pattern)
  - In v1.x, this option was used to specify PDS/PDSE data sets to search for members
  - In v2.0.0, use the `patterns` option with PDS member syntax: `DATASET.NAME(MEMBER*)`

Required actions:
```yaml
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
```

#### zos_job_output
breaking:
* return value renamed: ddnames —> dds
* return value renamed: ddnames[].ddname —> dds[].dd_name
* return value moved: ret_code.steps —> steps (moved from inside ret_code to job level)

Required actions:
```json
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
```

non-breaking:
* module option renamed: ddname —> dd_name (alias remains)

Recommended actions:
```yaml
# Before
- name: Job output with ddname
  zos_job_output:
    job_id: "STC02560"
    ddname: "JESMSGLG"

# After
- name: Job output with dd_name
  zos_job_output:
    job_id: "STC02560"
    dd_name: "JESMSGLG"
```

#### zos_job_query
breaking:
* return value moved: ret_code.steps —> steps (moved from inside ret_code to job level)
* return value removed: message (top-level return value removed)

Required actions:
```json
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
```

#### zos_job_submit
breaking:
* module option removed: `location` (choices: data_set, uss, local)
  - Use new module option `remote_src` (boolean)
  - `location=data_set` or `location=uss` → `remote_src=true`
  - `location=local` → `remote_src=false`
* module option renamed: wait_time_s → wait_time (NO alias in v2.0.0)
* return value renamed: ddnames → dds
* return value renamed: ddnames[].ddname → dds[].dd_name
* return value moved: ret_code.steps → steps (moved from inside ret_code to job level)

Required actions:
```yaml
# Before (v1.x) - Submit from data set
- name: Submit a long running PDS job and wait up to 30 seconds for completion.
  zos_job_submit:
    src: HLQ.DATA.LLQ(LONGRUN)
    location: data_set
    wait_time_s: 30

# After (v2.0.0) - Submit from data set
- name: Submit a long running PDS job and wait up to 30 seconds for completion.
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
```

```json
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
```

#### zos_lineinfile
breaking:
* return value renamed: return_content → stdout

non-breaking:
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stderr
* new return value: stdout_lines
* new return value: stderr_lines

Recommended actions:
```yaml
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
```

```json
// Before
{
"changed": True,
"cmd": "",
"found": 1,
"return_content": '{
    "cmd": "dsedhelper -d -c IBM-1047 -s -e /ZOAU_ROOT=/a\\\\ZOAU_ROOT=/mvsutil-develop_dsed/$ -e $ a\\\\ZOAU_ROOT=/mvsutil-develop_dsed ANSIBLE.PQWQE2RW.T4619709.CUEB9A5Q ",
    "found": 1,
    "changed": true
}',
"stderr": "",
"rc": 0,
"backup_name": ""
}
// After
{
"changed": True,
"cmd": "",
"found": 1,
"stdout": '{
    "cmd": "dsedhelper -d -c IBM-1047 -s -e /ZOAU_ROOT=/a\\\\ZOAU_ROOT=/mvsutil-develop_dsed/$ -e $ a\\\\ZOAU_ROOT=/mvsutil-develop_dsed ANSIBLE.PQWQE2RW.T4619709.CUEB9A5Q ",
    "found": 1,
    "changed": true
}',
"stdout_lines": ['{
    "cmd": "dsedhelper -d -c IBM-1047 -s -e /ZOAU_ROOT=/a\\\\ZOAU_ROOT=/mvsutil-develop_dsed/$ -e $ a\\\\ZOAU_ROOT=/mvsutil-develop_dsed ANSIBLE.PQWQE2RW.T4619709.CUEB9A5Q ",
    "found": 1,
    "changed": true
    }'
],
"stderr": "",
"stderr_lines": [],
"rc": 0,
"backup_name": ""
}
```

#### zos_mount
non-breaking:
* module option renamed: persistent.data_store → persistent.name (alias preserved)
* module option renamed: persistent.comment → persistent.marker (alias preserved)

Recommended actions:
```yaml
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
```

#### zos_operator
breaking:
* module option renamed: wait_time_s —> wait_time (NO alias in v2.0.0)
    * Use in conjunction with new option time_unit to indicate seconds/centiseconds.
* return value removed: content (replaced by stdout, stderr, stdout_lines and stderr_lines)
* return value renamed: wait_time_s —> wait_time

Required actions:
```yaml
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
```

```json
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
```

non-breaking:
* new module option: time_unit (choices: 's', 'cs')
* new return value: stdout (string version of output)
* new return value: stdout_lines (list version, replaces content)
* new return value: stderr
* new return value: stderr_lines
* new return value: time_unit

Recommended actions:
```yaml
# The new time_unit option provides flexibility for timing precision
# Default is 's' (seconds), so existing behavior is maintained when migrating
# Update playbooks to use stdout_lines instead of content for output processing
```

#### zos_operator_action_query
breaking:
* module option renamed: use_regex —> literal
* return value renamed: message_text —> msg_text
* return value renamed: message_id —> msg_id

Required actions:
```yaml
# Before
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
# After
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
```

```json
// Before
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
// After
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
```
non-breaking:
* module option renamed: message_filter —> msg_filter (alias remains)
* module option renamed: message_id —> msg_id (alias remains)

Recommended actions:
```yaml
# TODO - the recommended stuff is present in the required example.
```

#### zos_tso_command
breaking:
* return value renamed: content —> stdout
* return value renamed: lines —> line_count

Required actions:
```json
// Before
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
// After
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
```

non-breaking:
* new return value: stdout (string version of content)
* new return value: stdout_lines (replaces content list)
* new return value: stderr_lines

Recommended actions:
```yaml
# The migration guide examples above show the correct usage.
# Update your playbooks to use:
# - output[].stdout or output[].stdout_lines instead of output[].content
# - output[].line_count instead of output[].lines
```
#### zos_unarchive
breaking:
* module option renamed: format.name → format.type (NO alias in v2.0.0)
* module option renamed: format.format_options → format.options (NO alias in v2.0.0)
* module option renamed: format.format_options.use_adrdssu → format.options.adrdssu (NO alias in v2.0.0)

Required actions:
```yaml
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
```
