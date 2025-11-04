# ibm.ibm_zos_core.playbook_upgrade_validator

This role validates playbooks against ibm_zos_core 2.0 and provides migration actions.

## Role Variables

The only variable required is:

- `playbook_path`: The path to the directory containing one or more Ansible playbooks.
- `output_path`: File path where validation results should be written in JSON format.
- `ignore_response_params`: Indicates whether information about response parameter changes should be included.