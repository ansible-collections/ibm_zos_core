# 🚀 Ansible z/OS Core Collection Migration Guide: Ansible Collection `ibm.ibm_zos_core` v1.x → v2.0.0

This guide covers breaking and recommended changes for upgrading playbooks and roles to ibm.ibm_zos_core **v2.0.0**, including updates to module options and return values.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [Non-Breaking](#non-breaking_changes)

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

## 🚨 Breaking Changes

This section includes all the module options that have been renamed. It also includes any return values which have been renamed.

#### zos_archive
* module option renamed: format.name --> format.type
* module option renamed: format.format_options --> format.options
* module option renamed: format.use_adrdssu --> format.adrdssu
* module option renamed: format.format_options.terse_pack --> format.options.spack
  * the type of the option has changed from string to bool.

#### zos_bakup_restore
* TODO

#### zos_copy
* module option renamed: is_binary --> binary
* module option renamed: force --> replace
  * NOTE: option 'force' remains a valid module option with different functionality.
* module option renamed: force_lock --> force

#### zos_fetch
* module option renamed: is_binary —> binary
* return value renamed: file —> src
* return value renamed: is_binary —> binary

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

#### zos_mount
* module option renamed: persistent.data_store —> persistent.name
* module option renamed: persistent. comment —> persistent.marker

#### zos_operator
* module option renamed: wait_time_s —> wait_time
    * Use in conjunction w new option time_unit to indicate sec/centiseconds.

#### zos_operator_action_query
* module option renamed: use_regex —> literal
* return value renamed: message_text —> msg_text
* return value renamed: message_id —> msg_id

#### zos_tso_command
* return value renamed: content —> stdout
* return value renamed: lines —> line_count

#### zos_unarchive
* module option renamed: format.name —> format.type
* module option renamed: format.format_options —> format.options
* module option renamed: format.format_options.use_adrdssu -> format.options.adrdssu


## Non-Breaking Changes

This section includes all the module options that have been renamed for consistency across the collection, but still have the old module option name available as an alias. It is recommended to switch playbook tasks to use the new moddule names. This section also includes new return values.

#### zos_apf
* module option: persistent.data_set --> persistent.name. persistent.data_set_name will remain functional.
* new return value: stdout_lines
* new return value: stderr_lines

#### zos_archive
* new return value: dest

#### zos_blockinfile
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stdout_lines
* new return value: stderr_lines

#### zos_fetch
* new return value: encoding(from/to)
* new return value: stderr_lines, stdout_lines

#### zos_lineinfile
* New module option alias: insertafter can be referenced as 'after'
* New module option alias: insertbefore can be referenced as 'before'
* new return value: stdout_lines
* new return value: stderr_lines

#### zos_operator_action_query
* new module option renamed: message_filter —> msg_filter (alias remains)
* new module option renamed: message_id —> msg_id (alias remains)

#### zos_tso_command
* new return value: stdout_lines
* new return value: stderr_lines
