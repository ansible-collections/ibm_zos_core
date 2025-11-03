# gather_diagnostics role
This role gathers diagnostic information from the Ansible controller and target z/OS managed nodes.

It is designed to be run against z/OS hosts, and it will:
1.  Gather data from the Ansible controller (localhost).
2.  Gather data from each z/OS managed node in the play.

## Role Variables
The following variables, typically defined in `default/main.yml`, control the execution of the role:

* **`controller_node`**
    * **Description**: Controls whether to run the diagnostic tasks on the Ansible controller (localhost).
    * **Type**: `bool`
    * **Default**: `true`

* **`managed_node`**
    * **Description**: Controls whether to run the diagnostic tasks on the z/OS managed nodes.
    * **Type**: `bool`
    * **Default**: `true`

* **`controller_node_log_file`**
    * **Description**: Controls whether the role creates a YAML report file (`gather_diagnostics_report_controller.yml`) in the user's home directory on the controller.
    * If `true` (default), the report file is created, and sensitive data is hidden from the console (`no_log: true`).
    * If `false`, no report file is created, and all gathered data is printed to the console.
    * **Type**: `bool`
    * **Default**: `true`

* **`managed_node_log_file`**
    * **Description**: Controls whether the role creates a YAML report file for each managed node (`gather_diagnostics_report_managed_node.yml`) in the user's home directory on the controller.
    * If `true` (default), the report file is created, and sensitive data is hidden from the console (`no_log: true`).
    * If `false`, no report file is created, and all gathered data is printed to the console.
    * **Type**: `bool`
    * **Default**: `true`

* **`gather_diagnostics_gather_syslog`**
    * **Description**: Controls whether the role attempts to run authorized MVS operator commands (e.g., `D A,L`, `D OMVS,LIMITS`) to gather system activity.
    * **Type**: `bool`
    * **Default**: `true`

* **`gather_diagnostics_output_dir`**
    * **Description**: Controls where the role creates a YAML reports from managed node and controller.
    * **Type**: `str`