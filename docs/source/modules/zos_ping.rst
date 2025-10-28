
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_ping.py

.. _zos_ping_module:


zos_ping -- Ping z/OS and check dependencies.
=============================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- `zos_ping <./zos_ping.html>`_ verifies the presence of z/OS Web Client Enablement Toolkit, iconv, and Python.
- `zos_ping <./zos_ping.html>`_ returns ``pong`` when the target host is not missing any required dependencies.
- If the target host is missing optional dependencies, the `zos_ping <./zos_ping.html>`_ will return one or more warning messages.
- If a required dependency is missing from the target host, an explanatory message will be returned with the module failure.







Attributes
----------
action
  | **support**: full
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: none
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Ping the z/OS host and perform resource checks
     zos_ping:
     register: result




Notes
-----

.. note::
   This module is written in REXX and relies on the SCP protocol to transfer the source to the managed z/OS node and encode it in the managed nodes default encoding, eg IBM-1047. Starting with OpenSSH 9.0, it switches from SCP to use SFTP by default, meaning transfers are no longer treated as text and are transferred as binary preserving the source files encoding resulting in a module failure. If you are using OpenSSH 9.0 (ssh -V) or later, you can instruct SSH to use SCP by adding the entry ``scp_extra_args="-O"`` into the ini file named ``ansible.cfg``.

   For more information, review the `ansible.builtin.ssh <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ssh_connection.html>`_ module.







Return Values
-------------


ping
  Should contain the value "pong" on success.

  | **returned**: always
  | **type**: str
  | **sample**: pong

warnings
  List of warnings returned from stderr when performing resource checks.

  | **returned**: failure
  | **type**: list
  | **elements**: str

