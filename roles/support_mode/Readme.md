# ibm.ibm_zos_core.support_mode
This role gathers diagnostic information from target z/OS managed nodes.

## Role Variables
The following variables can be used to control the execution of the role:

**`support_mode_gather_syslog`**
Controls whether the role attempts to run the MVS operator command `D A,L` (Display Active) to gather system activity.
**Type**: `bool`
**Default**: `false`