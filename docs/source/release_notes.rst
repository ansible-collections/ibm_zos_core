.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2021                                          .
.. ...........................................................................

========
Releases
========

Version 1.5.0
====================

New Modules
-----------

- ``zos_gather_facts`` - can retrieve variables from target z/OS systems that are then available to playbooks through the ansible_facts dictionary and managed using filters.

Major Changes
-------------

- ``ibm_zos_core`` - Updates the entire collection in that the collection no longer depends on the managed node having installed System Display and Search Facility (SDSF). Remove SDSF dependency from ibm_zos_core collection.

Minor Changes
-------------

- ``zos_apf`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_blockinfile``

      - fixes a bug when using double quotes in the block text of the module. When double quotes appeared in block text, the module would error differently depending on the usage of option insertafter. Examples of this error have return code 1 or 16 along with message "ZOAU dmod return content is NOT in json format" and a varying stderr.
      - updates the module with a new option named force. This allows for a user to specify that the data set can be shared with others during an update which results in the data set you are updating to be simultaneously updated by others.
      - updates the module with a new option named indentation. This allows for a user to specify a number of spaces to prepend to the content before being inserted into the destination.
      - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_copy`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_data_set`` - Ensures that temporary datasets created by zos_data_set use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_encode`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_fetch`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_job_output`` - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs.
- ``zos_job_query``

      - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs.
      - was updated to use the jobs module utility.
- ``zos_job_submit``

      - architecture changed such that the entire modules execution time now is captured in the duration time which includes job submission and log collection. If a job does not return by the default 10 sec 'wait_time_s' value, it can be increased up to 86400 seconds.
      - behavior changed when a volume is defined in the module options such that it will catalog the data set if it is not cataloged and submit the job. In the past, the function did not catalog the data set and instead performed I/O operations and then submitted the job. This behavior aligns to other module behaviors and reduces the possibility to encounter a permissions issue.
- ``zos_lineinfile`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_mount`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_mvs_raw``

      - Ensures that temporary datasets created by DD Statements use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
      - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
      - updated module documentation on how to use a multi-line string when using the content field option as well as an example.
- ``zos_operator``

      - added in the response the cmd result.
      - added in the response the elapsed time.
      - added in the response the wait_time_s set.
      - deprecated the wait option, not needed with wait_time_s minor_changes.
      - was updated to remove the usage of REXX and replaced with ZOAU python APIs. This reduces code replication and it removes the need for REXX interpretation which increases performance.


Bugfixes
--------

- ``zos_copy``

      - fixes a bug such that the module fails when copying files from a directory needing also to be encoded. The failure would also delete the `src` which was not desirable behavior. Fixes deletion of src on encoding error.
      - module was updated to correct a bug in the case when the destination (dest) is a PDSE and the source (src) is a Unix Systems File (USS). The module would fail in determining if the PDSE actually existed and try to create it when it already existed resulting in an error that would prevent the module from correctly executing.
      - fixes a bug where the computed record length for a new destination dataset would include newline characters.
      - fixes a bug where if a destination has accented characters in its content, the module would fail when trying to determine if it is empty.
      - fixes a bug where copying a member from a loadlib to another loadlib fails.
      - fixed wrongful creation of destination backups when module option `force` is true, creating emergency backups meant to restore the system to its initial state in case of a module failure only when force is false.
      - copy failed from a loadlib member to another loadlib member. Fix now looks for an error in stdout while copying to perform a fallback copy for executables.
      - fixes a bug where the module would change the mode for a directory when copying into it the contents of another.
      - fixes a bug where source files not encoded in IBM-1047 would trigger an encoding error while computing the record length for a new destination dataset.
      - fixes a bug where the code for fixing an issue with newlines in files would use the wrong encoding for normalization.
- ``zos_data_set``

      - Fixes a bug such that the module will delete a catalogued data set over an uncatalogued data set even though the volume is provided for the uncataloged data set. This is unexpected behavior and does not align to documentation; correct behavior is that when a volume is provided that is the first place the module should look for the data set, whether or not it is cataloged.
      - fixes a bug where the default record format FB was actually never enforced and when enforced it would cause VSAM creation to fail with a Dynalloc failure. This also cleans up some of the options that are set by default when they have no bearing for batch.
- ``zos_fetch`` - Updates the modules behavior when fetching VSAM data sets such that the maximum record length is now determined when creating a temporary data set to copy the VSAM data into and a variable-length (VB) data set is used.
- ``zos_job_output`` - fixes a bug that returned all ddname's when a specific ddnamae was provided. Now a specific ddname can be returned and all others ignored.
- ``zos_job_query`` - was updated to correct a boolean condition that always evaluated to "CANCELLED".
- ``zos_job_submit``

      - fixes the issue when `wait_time_s` was set to 0 that would result in a `type` error and the response would be a stack trace.
      - fixes the issue when a job encounters a security exception, no job log would would result in the response.
      - fixes the issue when a job is configured for a syntax check using TYPRUN=SCAN that it would wait the full duration set by `wait_time_s` to return a response.
      - fixes the issue when a job is configured for a syntax check using TYPRUN=SCAN that no job log would result in the response.
      - fixes the issue when a job is purged by the system that the response would result in a stack trace.
      - fixes the issue when invalid JCL syntax is submitted such that the response would result in a stack trace.
      - fixes the issue when resources (data sets) identified in JCL did not exist such that a response would result in a stack trace.
      - fixes the issue where the response did not include the job log when a non-zero return code would occur.
- ``zos_mount`` - fixed option `tag_ccsid` to correctly allow for type int.
- ``zos_mvs_raw`` - module was updated to correct a bug when no DD statements were provided. The module when no option was provided for `dds` would error, a default was provided to correct this behavior.
- ``zos_operator``

      - fixed case sensitive error checks, invalid, error & unidentifiable.
      - fixed such that specifying wait_time_s would throw an error.
      - fixed the wait_time_s to default to 1 second.
      - was updated to correct missing verbosity content when the option verbose was set to True. zos_operator - was updated to correct the trailing lines that would appear in the result content.
      - fixed incorrect example descriptions and updated the doc to highlight the deprecated option `wait`.

Deprecated Features
-------------------

- ``zos_encode`` - deprecates the module options `from_encoding` and `to_encoding` to use suboptions `from` and `to` in order to remain consistent with all other modules.
- ``zos_job_submit`` - Response 'message' property has been deprecated, all responses are now in response property 'msg'.
- ``zos_job_submit`` - The 'wait' option has been deprecated because using option 'wait_time_s' implies the job is going to wait.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ `3.9`_ - `3.11`_
* Supported by IBM `Z Open Automation Utilities 1.2.2`_ (or later) but prior to version 1.3.

Version 1.4.1
=============

Bug fixes

--------------------------

* ``zos_copy``

    * Copy failed from a loadlib member to another loadlib member. Fix
      now looks for error in stdout in the if statement to use -X option.
    * Fixes a bug where files not encoded in IBM-1047 would trigger an
      error while computing the record length for a new destination dataset.
    * Fixes a bug where the code for fixing an issue with newlines in
      files.
    * fixed wrongful creation of destination backups when module option
      `force` is true, creating emergency backups meant to restore the system to
      its initial state in case of a module failure only when force is false.
    * fixes a bug where the computed record length for a new destination
      dataset would include newline characters.

* ``zos_job_query``

    * fixes a bug where a boolean was not being properly compared.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ `3.9`_
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Version 1.4.0
=============

* Modules

  * ``zos_mount`` can manage mount operations for a
    z/OS UNIX System Services (USS) file system data set.

* Plugins

  * ``zos_ssh`` connection plugin has been removed from this release and is no
    longer a dependency for the ``zos_ping`` module.

* Bug fixes and enhancements

  * Modules

    * ``zos_copy``

      * introduced an updated creation policy referred to as precedence rules
        that if `dest_data_set` is set, it will take precedence. If
        `dest` is an empty data set, the empty data set will be written with the
        expectation its attributes satisfy the copy. If no precedent rule
        has been exercised, `dest` will be created with the same attributes of
        `src`.
      * introduced new computation capabilities that if `dest` is a nonexistent
        data set, the attributes assigned will depend on the type of `src`. If
        `src` is a USS file, `dest` will have a Fixed Block (FB) record format
        and the remaining attributes will be computed. If `src` is binary,
        `dest` will have a Fixed Block (FB) record format with a record length
        of 80, block size of 32760, and the remaining attributes will be
        computed.
      * enhanced the force option when `force=true` and the remote file or
        data set `dest`` is NOT empty, the `dest` will be deleted and recreated
        with the `src` data set attributes, otherwise it will be recreated with
        the `dest` data set attributes.
      * was enhanced for when `src` is a directory and ends with "/",
        the contents of it will be copied into the root of `dest`. It it doesn't
        end with "/", the directory itself will be copied.
      * option `dest_dataset` has been deprecated and removed in favor
        of the new option `dest_data_set`.
      * fixes a bug that when a directory is copied from the controller to the
        managed node and a mode is set, the mode is applied to the directory
        on the managed node. If the directory being copied contains files and
        mode is set, mode will only be applied to the files being copied not the
        pre-existing files.
      * fixes a bug that did not create a data set on the specified volume.
      * fixes a bug where a number of attributes were not an option when using
        `dest_data_set`.
      * fixes a bug where options were not defined in the module
        argument spec that will result in error when running `ansible-core`
        v2.11 and using options `force` or `mode`.
      * was enhanced to support the ``ansible.builtin.ssh`` connection options;
        for further reference refer to the `SSH plugin`_ documentation.
      * was enhanced to take into account the record length when the
        source is a USS file and the destination is a data set with a record
        length. This is done by inspecting the destination data set attributes
        and using these attributes to create a new data set.
      * was updated with the capabilities to define destination data sets from
        within the ``zos_copy`` module. In the case where you are copying to
        data set destination that does not exist, you can now do so using the
        new ``zos_copy`` module option ``destination_dataset``.

    * ``zos_operator``

      * enhanced to allow for MVS operator `SET` command, `SET` is
        equivalent to the abbreviated `T` command.

    * ``zos_mount`` fixed option `tag_ccsid` to correctly allow for type int.

    * ``module_utils``

      * jobs.py - fixes a utility used by module `zos_job_output` that would
        truncate the DD content.

    * ``zos_ping`` was enhanced to remove the need for the ``zos_ssh``
      connection plugin dependency.

    * ``zos_fetch`` was enhanced to support the ``ansible.builtin.ssh``
      connection options; for further reference refer to the
      `SSH plugin`_ documentation.

    * ``zos_job_output``

      * was updated to correct possible truncated responses for
        the **ddname** content. This would occur for jobs with very large amounts
        of content from a **ddname**.
      * was enhanced to to include the completion code (CC) for each individual
        jop step as part of the ``ret_code`` response.

    * ``zos_job_query``

      * was enhanced to support a 7 digit job number ID for when there are
        greater than 99,999 jobs in the history.
      * was enhanced to handle when an invalid job ID or job name is used with
        the module and returns a proper response.

    * ``zos_job_submit``

      * was enhanced to fail fast when a submitted job fails instead of waiting
        a predetermined time.
      * was enhanced to check for 'JCL ERROR' when jobs are submitted and result
        in a proper module response.

    * ``zos_operator_action_query`` response messages were improved with more
      diagnostic information in the event an error is encountered.

* Deprecated or removed

  * ``zos_copy`` module option **destination_dataset** has been renamed to
    **dest_data_set**.
  * ``zos_ssh`` connection plugin has been removed, it is no longer required.
    Remove all playbook references, ie ``connection: ibm.ibm_zos_core.zos_ssh``.
  * ``zos_ssh`` connection plugin has been removed, it is no longer required.
    You must remove the zos_ssh connection plugin from all playbooks that
    reference the plugin, for example connection: ibm.ibm_zos_core.zos_ssh.
  * ``zos_copy`` module option **model_ds** has been removed. The model_ds logic
    is now automatically managed and data sets are either created based on the
    ``src`` data set or overridden by the new option ``destination_dataset``.
  * ``zos_copy`` and ``zos_fetch`` option **sftp_port** has been deprecated. To
    set the SFTP port, use the supported options in the ``ansible.builtin.ssh``
    plugin. Refer to the `SSH port`_ option to configure the port used during
    the modules SFTP transport.

* Documentation

  * Noteworthy documentation updates have been made to:

    * ``zos_copy`` and ``zos_fetch`` about Co:Z SFTP support.
    * ``zos_mvs_raw`` removed a duplicate example.
    * all action plugins are documented
    * update hyperlinks embedded in documentation.
    * ``zos_operator`` to explains how to use single quotes in operator commands.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ `3.8`_` - `3.9`_
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Known Issues
------------

* If a playbook includes the deprecated ``zos_ssh`` connection plugin, for
  example ``connection: ibm.ibm_zos_core.zos_ssh``, it will
  encounter this error which can corrected by safely removing the plugin:

  .. code-block::

      "msg": "the connection plugin 'ibm.ibm_zos_core.zos_ssh' was not found"

* When using the ``zos_ssh`` plugin with **Ansible 2.11** and earlier versions
  of this collection, you will encounter the exception:

  .. code-block::

     AttributeError: module 'ansible.constants' has no attribute 'ANSIBLE_SSH_CONTROL_PATH_DIR'.

  This is resolved in this release by deprecating the ``zos_ssh`` connection
  plugin and removing all ``connection: ibm.ibm_zos_core.zos_ssh`` references
  from playbooks.
* When using module ``zos_copy`` and option ``force`` with ansible versions
  greater than **Ansbile 2.10** and earlier versions of this collection, an
  unsupported option exception would occur. This is resolved in this release.
* When using the ``zos_copy`` or ``zos_fetch`` modules in earlier versions of
  this collection without 'passwordless' SSH configured such that you are using
  ``--ask-pass`` or passing an ``ansible_password`` in a configuration; during
  the playbook execution a second password prompt for SFTP would appear pausing
  the playbook execution. This is resolved in this release.
* When using the ``zos_copy`` or ``zos_fetch`` modules, if you tried to use
  Ansible connection options such as ``host_key_checking`` or ``port``, they
  were not included as part of the modules execution. This is resolved in this
  release by ensuring compatibility with the ``ansible.builtin.ssh`` plugin
  options. Refer to the `SSH plugin`_ documentation to enable supported options.
* Known issues for modules can be found in the **Notes** section of a modules
  documentation.


Deprecation Notices
-------------------
Features and functions are marked as deprecated when they are enhanced and an
alternative is available. In most cases, the deprecated item will remain
available unless the deprecated function interferes with the offering.
Deprecated functions are no longer supported, and will be removed in a future
release.

.. _SSH plugin:
   https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ssh_connection.html

.. _SSH port:
   https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ssh_connection.html#parameter-port

Version 1.3.6
=============

What's New
----------

* Bug Fixes

  * Modules

    * ``zos_copy`` fixes a bug that when a directory is copied from the
      controller to the managed node and a mode is set, the mode is now applied
      to the directory on the controller. If the directory being copied contains
      files and mode is set, mode will only be applied to the files being copied
      not the pre-existing files.
    * ``zos_copy`` - fixes a bug where options were not defined in the module
      argument spec that will result in error when running `ansible-core` v2.11
      and using options `force` or `mode`.
    * ``zos_copy`` - was enhanced for when `src` is a directory and ends with "/",
      the contents of it will be copied into the root of `dest`. It it doesn't
      end with "/", the directory itself will be copied.
    * ``zos_fetch`` - fixes a bug where an option was not defined in the module
      argument spec that will result in error when running `ansible-core` v2.11
      and using option `encoding`.
    * ``zos_job_submit`` - fixes a bug where an option was not defined in the
      module argument spec that will result in error when running
      `ansible-core` v2.11 and using option `encoding`.
    * ``jobs.py`` - fixes a utility used by module `zos_job_output` that would
      truncate the DD content.
    * ``zos_ssh`` connection plugin was updated to correct a bug that causes
      an `ANSIBLE_SSH_CONTROL_PATH_DIR` attribute error only when using
      ansible-core v2.11.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ v3.8.2 -
  `IBM Open Enterprise SDK for Python`_ v3.9.5
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Version 1.3.5
=============

What's New
----------

* Bug Fixes

  * Modules

    * ``zos_ssh`` connection plugin was updated to correct a bug in Ansible that
      would result in playbook task ``retries`` overriding the SSH connection
      ``retries``. This is resolved by renaming the ``zos_ssh`` option
      ``retries`` to ``reconnection_retries``. The update addresses users of
      ``ansible-core`` v2.9 which continues to use ``retries`` and users of
      ``ansible-core`` v2.11 or later which uses ``reconnection_retries``. This
      also resolves a bug in the connection that referenced a deprecated
      constant.
    * ``zos_job_output`` fixes a bug that returned all ddname's when a specific
      ddname was provided. Now a specific ddname can be returned and all others
      ignored.
    * ``zos_copy`` fixes a bug that would not copy subdirectories. If the source
      is a directory with sub directories, all sub directories will now be copied.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ 3.8.2 or later
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Version 1.3.3
=============

What's New
----------

* Bug Fixes

  * Modules

    * ``zos_copy`` was updated to correct deletion of all temporary files and
      unwarranted deletes.

        * When the module would complete, a cleanup routine did not take into
          account that other processes had open temporary files and thus would
          error when trying to remove them.
        * When the module would copy a directory (source) from USS to another
          USS directory (destination), any files currently in the destination
          would be deleted.
          The modules behavior has changed such that files are no longer deleted
          unless the ``force`` option is set to ``true``. When ``force=true``,
          copying files or a directory to a USS destination will continue if it
          encounters existing files or directories and overwrite any
          corresponding files.
    * ``zos_job_query`` was updated to correct a boolean condition that always
      evaluated to "CANCELLED".

        * When querying jobs that are either **CANCELLED** or have **FAILED**,
          they were always treated as **CANCELLED**.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ 3.8.2 or later
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Version 1.3.1
=============

What's New
----------

* Bug Fixes

  * Modules

    * Connection plugin ``zos_ssh`` was updated to prioritize the execution of
      modules written in REXX over other implementations such is the case for
      ``zos_ping``.
    * ``zos_ping`` was updated to support Automation Hub documentation
      generation.

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ 3.8.2 or later
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Known issues
------------

* Modules

  * When executing programs using ``zos_mvs_raw``, you may encounter errors
    that originate in the implementation of the programs. Two such known issues
    are noted below of which one has been addressed with an APAR.

    #. ``zos_mvs_raw`` module execution fails when invoking
       Database Image Copy 2 Utility or Database Recovery Utility in conjunction
       with FlashCopy or Fast Replication.
    #. ``zos_mvs_raw`` module execution fails when invoking DFSRRC00 with parm
       "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is
       addressed by APAR PH28089.

Version 1.3.0
=============

What's New
----------

* Modules

  * ``zos_apf`` - Add or remove libraries to and from Authorized Program Facility (APF).
  * ``zos_backup_restore`` - Backup and restore data sets and volumes.
  * ``zos_blockinfile`` - Manage block of multi-line textual data on z/OS.
  * ``zos_find`` - Find matching data sets.
  * ``zos_data_set`` - added support to allocate and format zFS data sets
  * ``zos_operator`` - supports new options **wait** and **wait_time_s** such
    that you can specify that ``zos_operator`` wait the full **wait_time_s** or
    return as soon as the first operator command executes.
  * All modules support relative paths and remove choice case sensitivity.

* Bug Fixes

  * Modules

    * Action plugin ``zos_copy`` was updated to support Python 2.7.
    * Module ``zos_copy`` was updated to fail gracefully when a it
      encounters a non-zero return code.
    * Module ``zos_copy`` was updated to support copying data set members that
      are program objects to a PDSE. Prior to this update, copying data set
      members would yield an error:
      **FSUM8976 Error writing <src_data_set_member> to PDSE member
      <dest_data_set_member>**
    * Job utility is an internal library used by several modules. It has been
      updated to use a custom written parsing routine capable of handling
      special characters to prevent job related reading operations from failing
      when a special character is encountered.
    * Module ``zos_job_submit`` was updated to remove all trailing **\r** from
      jobs that are submitted from the controller.
    * Module ``zos_job_submit`` referenced a non-existent option and was
      corrected to **wait_time_s**.
    * Module ``zos_tso_command`` support was added for when the command output
      contained special characters.

  * Playbooks

    * Playbook `zos_operator_basics.yaml`_
      has been updated to use `end` in the WTO reply over the previous use of
      `cancel`. Using `cancel` is not a valid reply and results in an execution
      error.

* Playbooks

  * In each release, we continue to expand on use cases and deliver them as
    playbooks in the `playbook repository`_ that can be easily tailored to any
    system.

    * Authorize and
      `synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub`_
    * Automate program execution with
      `copy, sort and fetch data sets on z/OS playbook`_.
    * Automate user management with add, remove, grant permission,
      generate passwords, create zFS, mount zFS and send email
      notifications when deployed to Ansible Tower or AWX with the
      `manage z/OS Users Using Ansible`_ playbook.
    * Use the `configure Python and ZOAU Installation`_ playbook to scan the
      **z/OS** target to find the latest supported configuration and generate
      `inventory`_ and a `variables`_ configuration.
    * Automate software management with `SMP/E Playbooks`_
    * All playbooks have been updated to use our temporary data set feature
      to avoid any concurrent data set name problems.
    * In the prior release, all sample playbooks previously included with the
      collection were migrated to the `playbook repository`_. The
      `playbook repository`_ categorizes playbooks into **z/OS concepts** and
      **topics**, it also covers `playbook configuration`_ as well as provide
      additional community content such as **blogs** and where to open
      `support tickets`_ for the playbooks.

* Documentation

  * All documentation related to `playbook configuration`_ has been
    migrated to the `playbook repository`_. Each playbook contains a README
    that explains what configurations must be made to run a sample playbook.
  * We have been carefully reviewing our users feedback and over time we have
    compiled a list of information that we feel would help everyone and have
    released this information in our new `FAQs`_.
  * Learn about the latest features and experience them before you try
    them through the blogs that discuss playbooks, modules, and use cases:

    * `Running Batch Jobs on z/OS using Ansible`_ details how
      to write and execute batch jobs without having to deal with JCL.

    * `z/OS User Management With Ansible`_ explains all about the user management
      playbook and its optional integration into AWX.

Availability
------------

* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_ 3.8.2 or later
* Supported by IBM `Z Open Automation Utilities 1.1.0`_ and
  `Z Open Automation Utilities 1.1.1`_

Known issues
------------

* Modules

  * When executing programs using ``zos_mvs_raw``, you may encounter errors
    that originate in the implementation of the programs. Two such known issues
    are noted below of which one has been addressed with an APAR.

    #. ``zos_mvs_raw`` module execution fails when invoking
       Database Image Copy 2 Utility or Database Recovery Utility in conjunction
       with FlashCopy or Fast Replication.
    #. ``zos_mvs_raw`` module execution fails when invoking DFSRRC00 with parm
       "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is
       addressed by APAR PH28089.

Version 1.2.1
=============

Notes
-----

* Update required
* Module changes

  * Noteworthy Python 2.x support

    * encode - removed TemporaryDirectory usage.
    * zos_copy - fixed regex support, dictionary merge operation fix
    * zos_fetch - fix quote import

* Collection changes

  * Beginning this release, all sample playbooks previously included with the
    collection will be made available on the `samples repository`_. The
    `samples repository`_ explains the playbook concepts,
    discusses z/OS administration, provides links to the samples support site,
    blogs and other community resources.

* Documentation changes

  * In this release, documentation related to playbook configuration has been
    migrated to the `samples repository`_. Each sample contains a README that
    explains what configurations must be made to run the sample playbook.

.. _samples repository:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/README.md

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities 1.0.3 PTF UI70435
* Supported by z/OS V2R3 or later
* The z/OS® shell

Version 1.1.0
=============

Notes
-----
* Update recommended
* New modules

  * zos_fetch
  * zos_encode
  * zos_operator_action_query
  * zos_operator
  * zos_tso_command
  * zos_ping

* New filter
* Improved error handling and messages
* Bug fixes
* Documentation updates
* New samples

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities: 1.0.3 PTF UI70435
* Supported by z/OS V2R3
* The z/OS® shell


Version 1.0.0
=============

Notes
-----

* Update recommended
* Security vulnerabilities fixed
* Improved test, security and injection coverage
* Module zos_data_set catalog support added
* Documentation updates

Availability
------------

* `Automation Hub`_
* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Z Open Automation Utilities: 1.0.1 PTF UI66957 through
  1.0.3 PTF UI70435

.. .............................................................................
.. Global Links
.. .............................................................................
.. _GitHub:
   https://github.com/ansible-collections/ibm_zos_core
.. _Galaxy:
   https://galaxy.ansible.com/ibm/ibm_zos_core
.. _Automation Hub:
   https://www.ansible.com/products/automation-hub
.. _IBM Open Enterprise SDK for Python:
   https://www.ibm.com/products/open-enterprise-python-zos
.. _3.8:
   https://www.ibm.com/docs/en/python-zos/3.8
.. _3.9:
   https://www.ibm.com/docs/en/python-zos/3.9
.. _3.10:
   https://www.ibm.com/docs/en/python-zos/3.10
.. _3.11:
   https://www.ibm.com/docs/en/python-zos/3.11
.. _Z Open Automation Utilities 1.1.0:
   https://www.ibm.com/docs/en/zoau/1.1.x
.. _Z Open Automation Utilities 1.1.1:
   https://www.ibm.com/docs/en/zoau/1.1.1
.. _Z Open Automation Utilities 1.2.2:
   https://www.ibm.com/docs/en/zoau/1.2.x
.. _z/OS® shell:
   https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm
.. _z/OS V2R3:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3/en/homepage.html
.. _FAQs:
   https://ibm.github.io/z_ansible_collections_doc/faqs/faqs.html

.. .............................................................................
.. Playbook Links
.. .............................................................................
.. _playbook repository:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/README.md
.. _synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/program_authorization/git_apf
.. _copy, sort and fetch data sets on z/OS playbook:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/data_transfer/copy_sort_fetch
.. _manage z/OS Users Using Ansible:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/user_management/add_remove_user
.. _zos_operator_basics.yaml:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/zos_concepts/zos_operator/zos_operator_basics/zos_operator_basics.yaml
.. _SMP/E Playbooks:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/software_management

.. .............................................................................
.. Configuration Links
.. .............................................................................
.. _playbook configuration:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/configuration_guide.md
.. _configure Python and ZOAU Installation:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_administration/host_setup
.. _inventory:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/configuration_guide.md#inventory
.. _variables:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/configuration_guide.md#variables
.. _support tickets:
   https://github.com/IBM/z_ansible_collections_samples/issues
.. _configured IBM Open Enterprise Python on z/OS:
   https://www.ibm.com/support/knowledgecenter/SSCH7P_3.8.0/install.html

.. .............................................................................
.. Blog Links
.. .............................................................................
.. _Running Batch Jobs on z/OS using Ansible:
   https://community.ibm.com/community/user/ibmz-and-linuxone/blogs/asif-mahmud1/2020/08/04/how-to-run-batch-jobs-on-zos-without-jcl-using-ans
.. _z/OS User Management With Ansible:
   https://community.ibm.com/community/user/ibmz-and-linuxone/blogs/blake-becker1/2020/09/03/zos-user-management-with-ansible
