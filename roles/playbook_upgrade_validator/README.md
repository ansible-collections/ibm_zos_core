# ibm.ibm_zos_core.playbook_upgrade_validator

This role validates playbooks against ibm_zos_core 2.0.0 and provides migration actions.

## Role Variables

The following variables are required:

- `playbook_path`: Path to the directory containing the Ansible playbooks to be validated.
- `output_path`: Path to the output JSON file where results should be saved.
- `ignore_response_params`: Indicates whether information about response parameter changes should be included.