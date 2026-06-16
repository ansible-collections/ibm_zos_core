
:github_url: https://github.com/IBM/ibm_zosmf/tree/master/plugins/roles/playbook_upgrade_validator

.. _playbook_upgrade_validator_module:


playbook_upgrade_validator -- Build a report to migrate playbooks to v2.0.0
===========================================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Scans one or more Ansible playbooks to identify removed or renamed parameters based on migration rules for IBM z/OS Core collection version 2.0.0.
- Provides line numbers, affected modules, and suggested corrective actions.






Variables
---------


 

playbook_upgrade_validator_ignore_response_params
  Indicates whether information about response parameter changes should be included.

  | **required**: False
  | **type**: bool
  | **default**: False


 

playbook_upgrade_validator_migration_map
  A structured set of migration rules that specifies removed, renamed, and modified parameters to help upgrade playbooks from ibm_zos_core 1.x.x to 2.0.0.

  | **required**: True
  | **type**: dict


 

playbook_upgrade_validator_output_path
  Path to the output JSON file where results should be saved.

  Default path is <<playbook_dir>>/logs/migration_report.json

  | **required**: False
  | **type**: str


 

playbook_upgrade_validator_playbook_path
  Path to an Ansible playbook or a directory containing playbooks to validate.

  | **required**: True
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Run playbook_upgrade_validator role to generate migration changes report for a playbook
     include_role:
       name: ibm.ibm_zos_core.playbook_upgrade_validator
     vars:
       playbook_upgrade_validator_playbook_path: "/path/to/playbooks/dataset.yml"
       playbook_upgrade_validator_output_path: "/path/to/reports/validation_report.json"
       playbook_upgrade_validator_ignore_response_params: false

   - name: Run playbook_upgrade_validator role to generate a migration changes report for playbooks within a directory
     include_role:
       name: ibm.ibm_zos_core.playbook_upgrade_validator
     vars:
       playbook_upgrade_validator_playbook_path: "/path/to/playbooks/"
       playbook_upgrade_validator_output_path: "/path/to/reports/validation_report.json"
       playbook_upgrade_validator_ignore_response_params: false



Notes
-----

.. note::
   - Designed to assist migration of playbooks from older IBM z/OS core collection versions to 2.0.0.

   - Supports reading tasks, blocks, and nested includes.

   - Reported task line numbers rely on task names and may be ambiguous when duplicate task names are used within a playbook.







