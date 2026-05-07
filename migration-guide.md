# 🚀 Ansible z/OS Core Collection Migration Guide: Ansible Collection `ibm.ibm_zos_core` v1.x → v2.0.0

This guide covers breaking and recommended changes for upgrading playbooks and roles to ibm.ibm_zos_core **v2.0.0**, including updates to module options and return values.

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Breaking and Non-Breaking Changes](#-breaking-and-non-breaking-changes)

* [zos_apf](#zos_apf)
* [zos_archive](#zos_archive)
* [zos_bakup_restore](#zos_bakup_restore)
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

Non-breaking changes are all the module options that have been renamed for consistency across the collection, but still have the old module option name available as an alias. It is recommended to switch playbook tasks to use the new moddule names. This section also includes new return values.



#### zos_apf
non-breaking:
* module sub-option: ``persistent.data_set`` is renamed to ``persistent.name``.
    * ``persistent.data_set_name`` will remain functional.
* new return value: ``stdout_lines``.
* new return value: ``stderr_lines``.

Recommended actions:
```yaml
# TODO
```

```json
// TODO
```


#### zos_archive
breaking:
* module sub-option renamed: ``format.name`` is renamed to ``format.type``.
* module sub-option renamed: ``format.format_options`` is renamed to ``format.options``.
* module sub-option renamed: ``format.use_adrdssu`` is renamed to ``format.adrdssu``.
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
* new return value: ``dest``.

Recommended actions:
```json
// Before
// After
```

#### zos_bakup_restore
* TODO

#### zos_blockinfile
non-breaking:
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stdout_lines
* new return value: stderr_lines

Recommended actions:
```yaml
# TODO
```

```json
// TODO
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
// TODO
```

#### zos_fetch
breaking:
* module option renamed: is_binary —> binary
* return value renamed: file —> src
* return value renamed: is_binary —> binary
* return value renamed: note -> msg

Required actions:
```yaml
# TODO
```

```json
// Before
{
  "file": "ANSIBLE.PWLZCFEB.T2417849.CICFWKBY.G0001V00",
  "dest": "", // TODO - why's this blank??!?!
  "is_binary": false,
  "checksum": "",
  "changed": false,
  "data_set_type": "",
  "note": "",
  "msg": "",
  "rc": 0,
  "ds_type": "PS"
}
// After
{
  "src": "ANSIBLE.PWLZCFEB.T2417849.CICFWKBY.G0001V00",
  "dest": "",
  "is_binary": false,
  "checksum": "",
  "changed": false,
  "data_set_type": "",
  "msg": "",
  "stdout": "",
  "stderr": "",
  "stdout_lines": [],
  "stderr_lines": [],
  "rc": 0,
  "encoding": {
      "from": "IBM-1047",
      "to": "UTF-8"
  },
  "ds_type": "PS"
}
```

non-breaking:
* new return value: encoding(from/to)
* new return value: stdout, stderr, stdout_lines, stderr_lines

Recommended actions:
```json
// TODO - example above is applicable here.
```

#### zos_find
* module option removed: pds_patterns - need to understand impact. TODO

Required actions:
```yaml
# TODO
```

#### zos_job_output
breaking:
* return value renamed: ddnames —> dds
* return value renamed: ddname.ddname —> dds.dd_name
* return value renamed: ret_code.steps —> job.steps

Required actions:
```json
// TODO
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
* return value renamed: ret_code.steps —> steps
* return value removed: message

Required actions:
```json
// TODO
```

#### zos_job_submit
breaking:
* module option removed: `location` option removed.
    Use new module option `remote_src` of type bool.
* module option renamed: wait_time_s -> wait_time
* return value renamed: ddnames —> dds
* return value renamed: ddnames.ddname —> dds.dd_name
* return value renamed: ret_code.steps —> jobs.steps
* return value removed: jobs.class, redundant to jobs.job_class

Required actions:
```yaml
# Before
- name: Submit a long running PDS job and wait up to 30 seconds for completion.
  zos_job_submit:
    src: HLQ.DATA.LLQ(LONGRUN)
    location: data_set
    wait_time_s: 30

# After
- name: Submit a long running PDS job and wait up to 30 seconds for completion.
  zos_job_submit:
    src: HLQ.DATA.LLQ(LONGRUN)
    remote_src: true
    wait_time: 30
```

```json
// TODO
```

#### zos_lineinfile
breaking:
* return value renamed: return_content -> stdout
non-breaking:
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stdout_lines
* new return value: stderr_lines

Recommended actions:
```yaml
# TODO
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
breaking:
* module option renamed: persistent.data_store —> persistent.name
* module option renamed: persistent. comment —> persistent.marker

Required actions:
```yaml
# TODO
```

#### zos_operator
breaking:
* module option renamed: wait_time_s —> wait_time
    * Use in conjunction w new option time_unit to indicate sec/centiseconds.

Required actions:
```yaml
# TODO
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
* new return value: stdout_lines
* new return value: stderr_lines

Recommended actions:
```json
// TODO
```
#### zos_unarchive
breaking:
* module option renamed: format.name —> format.type
* module option renamed: format.format_options —> format.options
* module option renamed: format.format_options.use_adrdssu -> format.options.adrdssu

Required actions:
```yaml
# TODO
```
