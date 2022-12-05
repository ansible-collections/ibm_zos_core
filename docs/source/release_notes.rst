.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2021, 2021                                          .
.. ...........................................................................

========
Releases
========

Version 1.4.0
=============

New
---

* ``zos_mount``

    * can manage mount operations for a z/OS UNIX System Services (USS) file
      system data set.

Bug fixes and enhancements
--------------------------

* ``zos_copy``

    * enhanced the force option when `force=true` and the remote file or
      data set `dest` is NOT empty, the `dest` will be deleted and recreated
      with the `src` data set attributes, otherwise it will be recreated
      with the `dest` data set attributes.
    * enhanced to optimize how it captures the permission bits state for
      the `dest`. This change now reviews the source files instead of
      traversing the entire `dest` path.
    * enhanced to support creating a parent directory when it does not exist
      in the `dest` path. Prior to this change, if a parent directory
      anywhere in the path did not exist the task would fail as it was
      stated in documentation.
    * enhanced to support system symbols in PARMLIB. System symbols are
      elements that allow different z/OS® systems to share PARMLIB definitions
      while retaining unique values in those definitions. This was fixed in a
      future release through the use of one of the ZOAU dependency but this
      version of `ibm_zos_core` does not support that dependency version so
      this support was added.
    * fixes a bug that when a directory is copied from the controller to the
      managed node and a mode is set, the mode is applied to the directory
      on the managed node. If the directory being copied contains files and
      mode is set, mode will only be applied to the files being copied not
      the pre-existing files.
    * fixes a bug where options were not defined in the module argument spec
      that will result in error when running `ansible-core` v2.11 and using
      options `force` or `mode`.
    * introduced an updated creation policy referred to as precedence rules
      such that if `dest_data_set` is set, this will take precedence.
      If `dest` is an empty data set, the empty data set will be written with
      the expectation its attributes satisfy the copy. If no precedent rule
      has been exercised, `dest` will be created with the same attributes of `src`.
    * introduced new computation capabilities such that if `dest` is a
      nonexistent data set, the attributes assigned will depend on the type
      of `src`. If `src` is a USS file, `dest` will have a Fixed Block (FB)
      record format and the remaining attributes will be computed. If `src`
      is binary, `dest` will have a Fixed Block (FB) record format with a
      record length of 80, block size of 32760, and the remaining attributes
      will be computed.
    * was enhanced for when `src` is a directory and ends with "/", the
      contents of it will be copied into the root of `dest`. It it doesn't
      end with `/`, the directory itself will be copied.
    * was updated to support the ansible.builtin.ssh connection options; for
      further reference refer to the SSH plugin documentation.
    * was updated to take into account the record length when the source is
      a USS file and the destination is a data set with a record length.
      This is done by inspecting the destination data set attributes and
      using these attributes to create a new data set.
    * was updated with the capabilities to define destination data sets
      from within the module. In the case where you are copying to
      a data set destination that does not exist, you can now do so using
      the new module option `dest_data_set`.
    * fixes a bug that did not create a data set on the specified volume.
    * fixes a bug where a number of attributes were not an option when
      using `dest_data_set`.

* ``zos_fetch``

    * was updated to support the  ansible.builtin.ssh   connection options;
      for further reference refer to the SSH plugin documentation.

* ``zos_job_output``

    * was updated to to include the completion code (CC) for each individual
      job step as part of the ret_code response.
    * fixes a bug that returned all ddname's when a specific ddname was
      provided. Now a specific ddname can be returned and all others ignored.
    * was updated to correct possible truncated responses for the ddname
      content. This would occur for jobs with very large amounts of content
      from a ddname.

* ``zos_job_query``

    * was updated to handle when an invalid job ID or job name is used with
      the module and returns a proper response.
    * was updated to support a 7 digit job number ID for when there are
      greater than 99,999 jobs in the history.

* ``zos_job_submit``

    * was enhanced to check for 'JCL ERROR' when jobs are submitted and
      result in a proper module response.
    * was updated to fail fast when a submitted job fails instead of
      waiting a predetermined time.

* ``zos_operator_action_query``

    * response messages were improved with more diagnostic information in
      the event an error is encountered.

* ``zos_ping``

    * was updated to remove the need for the ``zos_ssh`` connection plugin
      dependency.

* ``zos_mount``

    * fixed option `tag_ccsid` to correctly allow for type int.

* ``zos_operator``

    * enhanced to allow for MVS operator `SET` command, `SET` is equivalent
      to the abbreviated `T` command.

Deprecated Features
-------------------

* ``zos_copy``

    * option sftp_port has been deprecated. To set the SFTP port, use the
      supported options in the ansible.builtin.ssh plugin. Refer to
      the `SSH port <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ssh_connection.html#parameter-port>`__
      option to configure the port used during the modules SFTP transport.
    * module option model_ds has been removed. The model_ds logic is now
      automatically managed and data sets are either created based on the
      src data set or overridden by the new option destination_dataset.
    * option `dest_dataset` has been deprecated and removed in favor of the
      new option `dest_data_set`.

* ``zos_fetch``

    * option sftp_port has been deprecated. To set the SFTP port, use the
      supported options in the ansible.builtin.ssh plugin. Refer to
      the `SSH port <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ssh_connection.html#parameter-port>`__
      option to configure the port used during the modules SFTP transport.

* ``zos_ssh``

    * connection plugin has been removed, it is no longer required. You must
      remove all playbook references to connection ibm.ibm_zos_core.zos_ssh.

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
   https://www.ibm.com/docs/en/zoau/1.1.0
.. _Z Open Automation Utilities 1.1.1:
   https://www.ibm.com/docs/en/zoau/1.1.1
.. _Z Open Automation Utilities 1.2.x:
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
