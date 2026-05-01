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

## Non-Breaking Changes

This section includes all the module options that have been renamed for consistency across the collection, but still have the old module option name available as an alias. It is recommended to switch playbook tasks to use the new moddule names. This section also includes new return values.