.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2021                                          .
.. ...........................................................................

========
Releases
========

Version 1.5.0-beta.1
====================

What's New
----------

The collection no longer depends on the managed node having installed
System Display and Search Facility (SDSF).

* Modules

  * ``zos_gather_fact`` can ......


* Bug fixes and enhancements

  * Modules

    * ``zos_copy``

        * Fixes a bug such that the module fails when copying files
          from a directory needing also to be encoded. The failure would also delete
          the `src` which was not desirable behavior. Fixes deletion of src on
          encoding error. (https://github.com/ansible-collections/ibm_zos_core/pull/321).
        * updates the module with a new option named tmp_hlq. This allows
          for a user to specify the data set high level qualifier (HLQ) used in any
          temporary data set created by the module. Often, the defaults are not
          permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
        * module was updated to correct a bug in the case when the
          destination (dest) is a PDSE and the source (src) is a Unix Systems
          File (USS). The module would fail in determining if the PDSE actually
          existed and try to create it when it already existed resulting in an
          error that would prevent the module from correctly executing. (https://github.com/ansible-collections/ibm_zos_core/pull/327)
    * ``zos_operator``

        * added in the response the cmd result (https://github.com/ansible-collections/ibm_zos_core/issues/389)
        * added in the response the elapsed time (https://github.com/ansible-collections/ibm_zos_core/issues/389).
        * added in the response the wait_time_s set (https://github.com/ansible-collections/ibm_zos_core/issues/389)
        * was updated to remove the usage of REXX and replaced with ZOAU python
          APIs. This reduces code replication and it removes the need for REXX
          interpretation which increases performance. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
        * fixed error checking so that case sensitive error checks, invalid, error & unidentifiable would function properly (https://github.com/ansible-collections/ibm_zos_core/issues/389).
        * fixed the TypeError that would appear when **wait_time_s** was used with specific ZOAU versions.(https://github.com/ansible-collections/ibm_zos_core/issues/389).
        * fixed the **wait_time_s** to default to 1 second as it is stated in documentation (https://github.com/ansible-collections/ibm_zos_core/issues/389).
        * fixed the missing verbosity content that would occur when verbose was set to True. (https://github.com/ansible-collections/ibm_zos_core/pull/400)
        * fixed the excessive trailing lines that would appear in the result content. (https://github.com/ansible-collections/ibm_zos_core/pull/400)

      * ibm_zos_job_output - was updated to leverage the latest changes that 
        removes the REXX code by calling the module utility jobs. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
      * ibm_zos_job_query - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
      * ibm_zos_job_query - was updated to use the jobs module utility. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
   
      * module utility jobs - was updated to remove the useage of REXX and replaced with ZOAU python APIs. This reduces code replication and it removes the need for REXX intepretretion which increases performance. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
      * module utils backup - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * module utils dd_statement- updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * module utils encode - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_apf - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_blockinfile - fixes a bug when using double quotes in the block text of the module. When double quotes appeared in block text, the module would error differently depending on the usage of option insertafter. Examples of this error have return code 1 or 16 along with message "ZOAU dmod return content is NOT in json format" and a varying stderr. (https://github.com/ansible-collections/ibm_zos_core/pull/303).
      * zos_blockinfile - updates the module with a new option named force. This allows for a user to specifiy that the data set can be shared with others during an update which results in the data set you are updating to be simultaneously updated by others. (https://github.com/ansible-collections/ibm_zos_core/pull/316).
      * zos_blockinfile - updates the module with a new option named indentation. This allows for a user to specifiy a number of spaces to prepend to the content before being inserted into the destiation. (https://github.com/ansible-collections/ibm_zos_core/pull/317).
      * zos_blockinfile - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_data_set - Ensures that temporary datasets created by zos_data_set use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/491).
      * zos_encode - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_fetch - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_gather_facts - is a new module that can discover facts about the managed z/OS target. This module leverages the zinfo utility offered by ZOAU. (https://github.com/ansible-collections/ibm_zos_core/pull/322).
      * zos_job_submit - was updated to include an additional error code condition JCLERR. (https://github.com/ansible-collections/ibm_zos_core/pull/312)
      * zos_lineinfile- updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_mount - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
      * zos_mvs_raw - Ensures that temporary datasets created by DD Statements use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/414).
      * zos_mvs_raw - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
  

      * ibm_zos_data_set - Fixes a bug such that the module will delete a catalogued data set over an uncatalogued data set even though the volume is provided for the uncataloged data set. This is unexpected behavior and does not align to documentaiton; correct behavior is that when a volume is provided that is the first place the module should look for the data set, whether or not it is cataloged. (https://github.com/ansible-collections/ibm_zos_core/pull/325).

      * zos_fetch - Updates the modules behavior when fetching VSAM data sets such that the maximum record length is now determined when creating a temporary data set to copy the VSAM data into and a variable-length (VB) data set is used. (https://github.com/ansible-collections/ibm_zos_core/pull/350)
      * zos_job_output - fixes a bug that returned all ddname's when a specific ddnamae was provided. Now a specific ddname can be returned and all others ignored. (https://github.com/ansible-collections/ibm_zos_core/pull/334)
      * zos_job_query - was updated to correct a boolean condition that always evaluated to "CANCELLED". (https://github.com/ansible-collections/ibm_zos_core/pull/312).
      * zos_mount - fixed option `tag_ccsid` to correctly allow for type int. (https://github.com/ansible-collections/ibm_zos_core/pull/511)
      * zos_mvs_raw - module was upd.0ated to correct a bug when no DD statements were provided. The module when no option was provided for `dds` would error, a default was provided to correct this behavior. (https://github.com/ansible-collections/ibm_zos_core/pull/327)


* Deprecated or removed

  * ``zos_operator`` option **wait** has been deprecated, it is not needed with
    the updates to **wait_time_s** (https://github.com/ansible-collections/ibm_zos_core/issues/389)
  * ``zos_copy`` and ``zos_fetch`` option **sftp_port** has been removed. To
    set the SFTP port, use the supported options in the ``ansible.builtin.ssh``
    plugin. Refer to the `SSH port`_ option to configure the port used during
    the modules SFTP transport.
  * ``zos_encode`` deprecates the module options **from_encoding** and **to_encoding**
    to use suboptions **from** and **to** in order to remain consistent with all
    other modules.

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

Version 1.4.0
=============
NOTE: There will be a 1.4.0 GA before 1.5.0.x so this must be updated and remove the beta entries.
      Likely 1.4.0-beta.2 will be promoted to GA and we can reuse the release notes below.

Version 1.4.0-beta.2
====================

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

    * ``zos_operator``

      * enhanced to allow for MVS operator `SET` command, `SET` is
        equivalent to the abbreviated `T` command.

    * ``zos_mount``

      * fixed option `tag_ccsid` to correctly allow for type int.

    * ``module_utils``

      * jobs.py - fixes a utility used by module `zos_job_output` that would
        truncate the DD content.

  * Documentation

    * Review :ref:`version 1.4.0-beta.1<my-reference-label>` release notes for additional content.

* Deprecated or removed

  * ``zos_copy`` module option **destination_dataset** has been renamed to
    **dest_data_set**.

    * Review :ref:`version 1.4.0-beta.1<my-reference-label>` release notes for additional content.


Availability
------------

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

Known Issues
------------

* Review :ref:`version 1.4.0-beta.1<my-reference-label>` release notes for additional content.

Deprecation Notices
-------------------
* Review :ref:`version 1.4.0-beta.1<my-reference-label>` release notes for additional content.

.. _my-reference-label:

Version 1.4.0-beta.1
====================

What's New
----------

* Modules

  * ``zos_mount`` can manage mount operations for a
    z/OS UNIX System Services (USS) file system data set.

* Plugins

  * ``zos_ssh`` connection plugin has been removed from this release and is no
    longer a dependency for the ``zos_ping`` module.

* Bug fixes and enhancements

  * Modules

    * ``zos_ping`` was enhanced to remove the need for the ``zos_ssh``
      connection plugin dependency.

    * ``zos_copy``

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

    * ``zos_fetch`` was enhanced to support the ``ansible.builtin.ssh``
      connection options; for further reference refer to the
      `SSH plugin`_ documentation.

    * ``zos_job_output``

      * was updated to correct possible truncated responses for
        the **ddname** content. This would occur for jobs with very large amounts
        of content from a **ddname**.
      * was enhanced to to include the completion code (CC) for each individual
        job step as part of the ``ret_code`` response.

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

  * Documentation

    * Noteworthy documentation updates have been made to:

      * ``zos_copy`` and ``zos_fetch`` about Co:Z SFTP support.
      * ``zos_mvs_raw`` to remove a duplicate example.
      * include documentation for all action plugins.
      * update hyperlinks embedded in documentation.
      * ``zos_operator`` to explain how to use single quotes in operator commands.


* Deprecated or removed

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
   https://github.com/IBM/z_ansible_collections_samples/blob/master/README.md

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
.. _IBM Open Enterprise Python for z/OS:
   https://www.ibm.com/products/open-enterprise-python-zos
.. _IBM Open Enterprise SDK for Python:
   https://www.ibm.com/products/open-enterprise-python-zos
.. _Z Open Automation Utilities 1.1.0:
   https://www.ibm.com/docs/en/zoau/1.1.0?topic=installing-configuring-zoa-utilities
.. _Z Open Automation Utilities 1.1.1:
   https://www.ibm.com/docs/en/zoau/1.1.1?topic=installing-configuring-zoa-utilities
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
   https://github.com/IBM/z_ansible_collections_samples/blob/master/README.md
.. _synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/program_authorization/git_apf
.. _copy, sort and fetch data sets on z/OS playbook:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/data_transfer/copy_sort_fetch
.. _manage z/OS Users Using Ansible:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/user_management/add_remove_user
.. _zos_operator_basics.yaml:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/zos_concepts/zos_operator/zos_operator_basics/zos_operator_basics.yaml
.. _SMP/E Playbooks:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/software_management

.. .............................................................................
.. Configuration Links
.. .............................................................................
.. _playbook configuration:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/docs/share/configuration_guide.md
.. _configure Python and ZOAU Installation:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_administration/host_setup
.. _inventory:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/docs/share/configuration_guide.md#inventory
.. _variables:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/docs/share/configuration_guide.md#variables
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
