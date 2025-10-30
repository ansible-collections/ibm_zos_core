# support_mode role
This role gathers diagnostic information from target z/OS managed nodes.

## Role Variables
The following variables can be used to control the execution of the role:

* **`support_mode_gather_syslog`**
    * **Description**: Controls whether the role attempts to run the MVS operator command `D A,L` (Display Active) to gather system activity.
    * **Type**: `bool`
    * **Default**: `false`

* **`create_log_file`**
    * **Description**: Controls whether the role creates a YAML report file (`support_mode_report_<hostname>.yml`) in the user's home directory on the controller.
    * If `true` (default), the report file is created, and sensitive data is hidden from the console (`no_log: true`).
    * If `false`, no report file is created, and all gathered data, including sensitive information, is printed to the console (`no_log: false`).
    * **Type**: `bool`
    * **Default**: `true`