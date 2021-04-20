.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

========
Releases
========

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
