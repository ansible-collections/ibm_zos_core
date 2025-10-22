# ibm.ibm_zos_core.support_mode

This role gathers diagnostic information from both the Ansible controller and the target z/OS managed nodes.

## Role Variables

The following variables can be used to control the execution of the role:

- `run_controller_diagnostics`: A boolean that controls whether to gather facts from the Ansible controller. Defaults to `True`.
- `run_managed_diagnostics`: A boolean that controls whether to gather facts from the z/OS managed node. Defaults to `True`.