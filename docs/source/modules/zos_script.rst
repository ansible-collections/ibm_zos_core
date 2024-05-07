
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_script.py

.. _zos_script_module:


zos_script -- Run scripts in z/OS
=================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The `zos_script <./zos_script.html>`_ module runs a local or remote script in the remote machine.





Parameters
----------


chdir
  Change the script's working directory to this path.

  When not specified, the script will run in the user's home directory on the remote machine.

  | **required**: False
  | **type**: str


cmd
  Path to the local or remote script followed by optional arguments.

  If the script path contains spaces, make sure to enclose it in two pairs of quotes.

  Arguments may need to be escaped so the shell in the remote machine handles them correctly.

  | **required**: True
  | **type**: str


creates
  Path to a file in the remote machine. If it exists, the script will not be executed.

  | **required**: False
  | **type**: str


encoding
  Specifies which encodings the script should be converted from and to.

  If ``encoding`` is not provided, the module determines which local and remote charsets to convert the data from and to.

  | **required**: False
  | **type**: dict


  from
    The encoding to be converted from.

    | **required**: True
    | **type**: str


  to
    The encoding to be converted to.

    | **required**: True
    | **type**: str



executable
  Path of an executable in the remote machine to invoke the script with.

  When not specified, the system will assume the script is interpreted REXX and try to run it as such. Make sure to include a comment identifying the script as REXX at the start of the file in this case.

  | **required**: False
  | **type**: str


remote_src
  If set to ``false``, the module will search the script in the controller.

  If set to ``true``, the module will search the script in the remote machine.

  | **required**: False
  | **type**: bool


removes
  Path to a file in the remote machine. If it does not exist, the script will not be executed.

  | **required**: False
  | **type**: str


use_template
  Whether the module should treat ``src`` as a Jinja2 template and render it before continuing with the rest of the module.

  Only valid when ``src`` is a local file or directory.

  All variables defined in inventory files, vars files and the playbook will be passed to the template engine, as well as `Ansible special variables <https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html#special-variables>`_, such as ``playbook_dir``, ``ansible_version``, etc.

  If variables defined in different scopes share the same name, Ansible will apply variable precedence to them. You can see the complete precedence order `in Ansible's documentation <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence>`_

  | **required**: False
  | **type**: bool
  | **default**: False


template_parameters
  Options to set the way Jinja2 will process templates.

  Jinja2 already sets defaults for the markers it uses, you can find more information at its `official documentation <https://jinja.palletsprojects.com/en/latest/templates/>`_.

  These options are ignored unless ``use_template`` is true.

  | **required**: False
  | **type**: dict


  variable_start_string
    Marker for the beginning of a statement to print a variable in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: {{


  variable_end_string
    Marker for the end of a statement to print a variable in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: }}


  block_start_string
    Marker for the beginning of a block in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: {%


  block_end_string
    Marker for the end of a block in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: %}


  comment_start_string
    Marker for the beginning of a comment in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: {#


  comment_end_string
    Marker for the end of a comment in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: #}


  line_statement_prefix
    Prefix used by Jinja2 to identify line-based statements.

    | **required**: False
    | **type**: str


  line_comment_prefix
    Prefix used by Jinja2 to identify comment lines.

    | **required**: False
    | **type**: str


  lstrip_blocks
    Whether Jinja2 should strip leading spaces from the start of a line to a block.

    | **required**: False
    | **type**: bool
    | **default**: False


  trim_blocks
    Whether Jinja2 should remove the first newline after a block is removed.

    Setting this option to ``False`` will result in newlines being added to the rendered template. This could create invalid code when working with JCL templates or empty records in destination data sets.

    | **required**: False
    | **type**: bool
    | **default**: True


  keep_trailing_newline
    Whether Jinja2 should keep the first trailing newline at the end of a template after rendering.

    | **required**: False
    | **type**: bool
    | **default**: False


  newline_sequence
    Sequence that starts a newline in a template.

    | **required**: False
    | **type**: str
    | **default**: \\n
    | **choices**: \\n, \\r, \\r\\n


  auto_reload
    Whether to reload a template file when it has changed after the task has started.

    | **required**: False
    | **type**: bool
    | **default**: False





Examples
--------

.. code-block:: yaml+jinja

   
   - name: Run a local REXX script on the managed z/OS node.
     zos_script:
       cmd: ./scripts/HELLO

   - name: Run a local REXX script with args on the managed z/OS node.
     zos_script:
       cmd: ./scripts/ARGS "1,2"

   - name: Run a remote REXX script while changing its working directory.
     zos_script:
       cmd: /u/user/scripts/ARGS "1,2"
       remote_src: true
       chdir: /u/user/output_dir

   - name: Run a local Python script in the temporary directory specified in the Ansible environment variable 'remote_tmp'.
     zos_script:
       cmd: ./scripts/program.py
       executable: /usr/bin/python3

   - name: Run a local script made from a template.
     zos_script:
       cmd: ./templates/PROGRAM
       use_template: true

   - name: Run a script only when a file is not present.
     zos_script:
       cmd: ./scripts/PROGRAM
       creates: /u/user/pgm_result.txt

   - name: Run a script only when a file is already present on the remote machine.
     zos_script:
       cmd: ./scripts/PROGRAM
       removes: /u/user/pgm_input.txt




Notes
-----

.. note::
   When executing local scripts, temporary storage will be used on the remote z/OS system. The size of the temporary storage will correspond to the size of the file being copied.

   The location in the z/OS system where local scripts will be copied to can be configured through Ansible's ``remote_tmp`` option. Refer to `Ansible's documentation <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/sh_shell.html#parameter-remote_tmp>`_ for more information.

   All local scripts copied to a remote z/OS system  will be removed from the managed node before the module finishes executing.

   Execution permissions for the group assigned to the script will be added to remote scripts. The original permissions for remote scripts will be restored by the module before the task ends.

   The module will only add execution permissions for the file owner.

   If executing REXX scripts, make sure to include a newline character on each line of the file. Otherwise, the interpreter may fail and return error ``BPXW0003I``.

   For supported character sets used to encode data, refer to the `documentation <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html>`_.

   This module uses `zos_copy <./zos_copy.html>`_ to copy local scripts to the remote machine which uses SFTP (Secure File Transfer Protocol) for the underlying transfer protocol; SCP (secure copy protocol) and Co:Z SFTP are not supported. In the case of Co:z SFTP, you can exempt the Ansible user id on z/OS from using Co:Z thus falling back to using standard SFTP. If the module detects SCP, it will temporarily use SFTP for transfers, if not available, the module will fail.

   This module executes scripts inside z/OS UNIX System Services. For running REXX scripts contained in data sets or CLISTs, consider issuing a TSO command with `zos_tso_command <./zos_tso_command.html>`_.

   The community script module does not rely on Python to execute scripts on a managed node, while this module does. Python must be present on the remote machine.



See Also
--------

.. seealso::

   - :ref:`zos_copy_module`
   - :ref:`zos_tso_command_module`




Return Values
-------------


cmd
  Original command issued by the user.

  | **returned**: changed
  | **type**: str
  | **sample**: ./scripts/PROGRAM

remote_cmd
  Command executed on the remote machine. Will show the executable path used, and when running local scripts, will also show the temporary file used.

  | **returned**: changed
  | **type**: str
  | **sample**: /tmp/zos_script.jycqqfny.ARGS 1,2

msg
  Failure or skip message returned by the module.

  | **returned**: failure or skipped
  | **type**: str
  | **sample**: File /u/user/file.txt is already missing on the system, skipping script

rc
  Return code of the script.

  | **returned**: changed
  | **type**: int
  | **sample**: 16

stdout
  The STDOUT from the script, may be empty.

  | **returned**: changed
  | **type**: str
  | **sample**: Allocation to SYSEXEC completed.

stderr
  The STDERR from the script, may be empty.

  | **returned**: changed
  | **type**: str
  | **sample**: An error has ocurred.

stdout_lines
  List of strings containing individual lines from STDOUT.

  | **returned**: changed
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "Allocation to SYSEXEC completed."
        ]

stderr_lines
  List of strings containing individual lines from STDERR.

  | **returned**: changed
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "An error has ocurred"
        ]

