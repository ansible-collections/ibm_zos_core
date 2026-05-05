# 🚀 Ansible z/OS Core Collection Migration Guide: Ansible Collection `ibm.ibm_zos_core` v1.x → v2.0.0

This guide covers breaking and recommended changes for upgrading playbooks and roles to ibm.ibm_zos_core **v2.0.0**, including updates to module options and return values.

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Breaking and Non-Breaking Changes](#-breaking-and-non-breaking-changes)

6. Testing and Validation
7. Resources and Support

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

#### zos_archive
breaking:
* module sub-option renamed: ``format.name`` is renamed to ``format.type``.
* module sub-option renamed: ``format.format_options`` is renamed to ``format.options``.
* module sub-option renamed: ``format.use_adrdssu`` is renamed to ``format.adrdssu``.
* module sub-option renamed: ``format.format_options`` is renamed to ``format.options.spack``.
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
```yaml
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
#### zos_fetch
breaking:
* module option renamed: is_binary —> binary
* return value renamed: file —> src
* return value renamed: is_binary —> binary

non-breaking:
* new return value: encoding(from/to)
* new return value: stderr_lines, stdout_lines

#### zos_find
* module option removed: pds_patterns - need to understand impact. TODO

#### zos_job_output
* module option renamed: ddname —> dd_name
* return value renamed: ddnames —> dds
* return value renamed: ddname.ddname —> dds.dd_name
* return value renamed: ret_code.steps —> job.steps

#### zos_job_query
* return value renamed: ret_code.steps —> steps
* return value removed: message

#### zos_job_submit
* module option removed: `location` option removed.
    Use new module option `remote_src` of type bool.
* module option renamed: `force` —> `replace`
* module option renamed: wait_time_s -> wait_time
* return value renamed: ddnames —> dds
* return value renamed: ddnames.ddname —> dds.dd_name
* return value renamed: ret_code.steps —> jobs.steps
* return value removed: jobs.class, redundant to jobs.job_class


#### zos_lineinfile
non-breaking:
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stdout_lines
* new return value: stderr_lines

#### zos_mount
* module option renamed: persistent.data_store —> persistent.name
* module option renamed: persistent. comment —> persistent.marker

#### zos_operator
* module option renamed: wait_time_s —> wait_time
    * Use in conjunction w new option time_unit to indicate sec/centiseconds.

#### zos_operator_action_query
breaking:
* module option renamed: use_regex —> literal
* return value renamed: message_text —> msg_text
* return value renamed: message_id —> msg_id

non-breaking:
* new module option renamed: message_filter —> msg_filter (alias remains)
* new module option renamed: message_id —> msg_id (alias remains)

#### zos_tso_command
breaking:
* return value renamed: content —> stdout
* return value renamed: lines —> line_count

non-breaking:
* new return value: stdout_lines
* new return value: stderr_lines

#### zos_unarchive
* module option renamed: format.name —> format.type
* module option renamed: format.format_options —> format.options
* module option renamed: format.format_options.use_adrdssu -> format.options.adrdssu


