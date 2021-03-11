.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

========
Releases
========

Version 1.3.0-beta.2
====================

What's New
----------

* Modules

  * Utility ``better_arg_parser`` - supports relative paths and removes the
    choice case sensitivity.
  * ``zos_operator`` - supports new options **wait** and **wait_time_s** such
    that you can specify that ``zos_operator`` wait the full **wait_time_s** or
    return as soon as the first operator command executes.

* Bug Fixes

  * Modules

    * Module ``zos_job_submit`` was updated to remove all trailing **\r** from
      jobs that are submitted from the controller.
    * Module ``zos_copy`` was updated to support copying data set members that
      are program objects to a PDSE. Prior to this update, copying data set members would
      yield an error:
      **FSUM8976 Error writing <src_data_set_member> to PDSE member
      <dest_data_set_member>**
    * Job utility is an internal library used by several modules. It has been
      updated to use a custom written parsing routine capable of handling
      special characters to prevent job related reading operations from failing
      when a special character is encountered.

  * Playbooks

    * Playbook `zos_operator_basics.yaml`_
      has been updated to use `end` in the WTO reply over the previous use of
      `cancel`. Using `cancel` is not a valid reply and results in an execution
      error.

Availability
------------

* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by `z/OS V2R3`_ or later
* Supported by the `z/OS® shell`_
* Supported by `IBM Open Enterprise SDK for Python`_
  (previously `IBM Open Enterprise Python for z/OS`_) 3.8.2 or later
* Supported by IBM `Z Open Automation Utilities 1.1.0`_

.. _zos_operator_basics.yaml:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/zos_concepts/zos_operator/zos_operator_basics/zos_operator_basics.yaml
   
Version 1.3.0-beta.1
====================

What's New
----------

* Modules

  * ``zos_apf`` - Add or remove libraries to and from Authorized Program Facility (APF).
  * ``zos_backup_restore`` - Backup and restore data sets and volumes.
  * ``zos_blockinfile`` - Manage block of multi-line textual data on z/OS.
  * ``zos_find`` - Find matching data sets.
  * ``zos_data_set`` - added support to allocate and format zFS data sets

* Playbooks

  * In each release, we continue to expand on the use cases and deliver
    several new playbooks in the `playbook repository`_ that can be easily
    tailored to any system.

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
    * All playbooks have been updated to use our temporary data set feature
      to avoid any concurrent data set name problems.
    * In the prior release, all sample playbooks previously included with the
      collection were migrated to the `playbook repository`_. The
      `playbook repository`_ categorizes playbooks into **z/OS concepts** and
      **topics**, it also covers `playbook configuration`_ as well as provide
      additional community content such as **blogs** and where to open
      `support tickets`_ for the playbooks.

* Bug Fixes

  * Modules

    * Module ``zos_copy`` was updated to fail gracefully when a it
      encounters a non-zero return code.
    * Action plugin ``zos_copy`` was updated to support Python 2.7.
    * Module ``zos_tso_command`` support was added for when the command output
      contained special characters.
    * Module ``zos_job_submit`` referenced a non-existent option and was
      corrected to **wait_time_s**.

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

* Supported by `IBM Open Enterprise Python for z/OS`_ 3.8.2 or later
* Supported by IBM `Z Open Automation Utilities 1.1.0`_

  .. note::
     There is an additional step for `Z Open Automation Utilities 1.1.0`_ (ZOAU)
     over prior installations of ZOAU on the target z/OS. After you have
     `configured IBM Open Enterprise Python on z/OS`_ **environment variables**
     on the z/OS target and have installed ZOAU from a PAX archive or through
     SMPe, you will need to perform a PIP installation of the ZOAU Python
     libraries and ensure you have either exported or added these environment
     variables to your **z/OS** host **.profile**.

     **Variables**:

     | ``export ZOAU_HOME=/usr/lpp/IBM/zoautil``
     | ``export PATH=${ZOAU_HOME}/bin:$PATH``
     | ``export LIBPATH=${ZOAU_HOME}/lib:${LIBPATH}``

     **PIP installation command**:

     | ``pip install zoautil_py-1.1.0.tar.gz``.

     This will install the ZOAU Python libraries on the **z/OS** target for use
     by **z/OS Ansible core** and other collections.

     However, the Python installation may not have the the symbolic link for
     ``pip`` in which case you can use ``pip3`` to install the libraries:

     | ``pip3 install zoautil_py-1.1.0.tar.gz``.

     If the Python installation has not installed the ``wheel`` packaging
     standard and not updated the ``pip`` version to the latest, the warning
     messages can be ignored.

     **Example output**:

      | Processing ./zoautil_py-1.1.0.tar.gz
      | Using legacy setup.py install for zoautil-py, since package 'wheel' is
       not installed.
      | Installing collected packages: zoautil-py
      | Running setup.py install for zoautil-py ... done
      | Successfully installed zoautil-py-1.1.0
      | WARNING: You are using pip version 20.1.1; however, version 20.2.4 is
       available.
      | You should consider upgrading via the
       '<python_path>/pyz_3_8_2/usr/lpp/IBM/cyp/v3r8/pyz/bin/python3.8 -m pip install --upgrade pip' command.

* Supported by `z/OS V2R3`_ or later
* The `z/OS® shell`_

Known issues
------------

* Modules

  * When executing programs using ``zos_mvs_raw``, you may encounter errors
    that originate in the implementation of the programs. Two such known issues are
    noted below of which one has been addressed with an APAR.

    #. ``zos_mvs_raw`` module execution fails when invoking
       Database Image Copy 2 Utility or Database Recovery Utility in conjunction
       with FlashCopy or Fast Replication.
    #. ``zos_mvs_raw`` module execution fails when invoking DFSRRC00 with parm
       "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is
       addressed by APAR PH28089.


.. .............................................................................
.. Playbook Links
.. .............................................................................

.. _synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/program_authorization/git_apf
.. _copy, sort and fetch data sets on z/OS playbook:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/data_transfer/copy_sort_fetch
.. _manage z/OS Users Using Ansible:
   https://github.com/IBM/z_ansible_collections_samples/tree/master/zos_concepts/user_management/add_remove_user

.. .............................................................................
.. Configuration Links
.. .............................................................................

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


Version 1.2.0
=============

Notes
-----

* Update recommended
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

* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities 1.0.3 PTF UI70435
* Supported by z/OS V2R3
* The z/OS® shell


Version 1.2.0-beta.4
====================

Notes
-----

* Update recommended
* Bugfix

  * Fixes a bug for `zos_data_set` module where some parameters were not
    getting passed correctly because python considers integer value of 0
    to be false.
  * Fixes documentation in module `zos_job_submit` where **wait_time_s** should
    have been written as **duration_s**.
  * Fixes requirements version in sample playbook hosts-setup.yaml

* Module changes

  * Module ``zos_copy`` can now use wildcards to copy multiple PDS/PDSE members
    to another PDS/PDSE

Availability
------------

* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities 1.0.3 PTF UI70435
* Supported by z/OS V2R3
* The z/OS® shell

Known issues
------------

* Modules

  * When executing programs using ``zos_mvs_raw``, you may encounter errors
    that originate in the programs implementation. Two such known issues are
    noted below of which one has been addressed with an APAR.

    #. ``zos_mvs_raw`` module execution fails when invoking
       Database Image Copy 2 Utility or Database Recovery Utility in conjunction
       with FlashCopy or Fast Replication.
    #. ``zos_mvs_raw`` module execution fails when invoking DFSRRC00 with parm
       "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is
       addressed by APAR PH28089.

Version 1.2.0-beta.3
====================

Notes
-----

* Update recommended
* Bugfix

  * Fixes a bug which causes action plugins to fail when collections are
    referenced using fully qualified collection names instead of playbook
    level imports

Availability
------------

* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities 1.0.3 PTF UI70435
* Supported by z/OS V2R3
* The z/OS® shell

Known issues
------------

* Modules

  * When executing programs using ``zos_mvs_raw``, you may encounter errors
    that originate in the programs implementation. Two such known issues are
    noted below of which one has been addressed with an APAR.

    #. ``zos_mvs_raw`` module execution fails when invoking
       Database Image Copy 2 Utility or Database Recovery Utility in conjunction
       with FlashCopy or Fast Replication.
    #. ``zos_mvs_raw`` module execution fails when invoking DFSRRC00 with parm
       "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is
       addressed by APAR PH28089.

Version 1.2.0-beta.2
====================

Notes
-----

* Update recommended
* Module changes

  * Update zos_fetch and zos_copy to allow for user specified SFTP transfer
    port.
  * Refactor module option **backup_file** to **backup_name** in modules
    ``zos_copy``, ``zos_lineinfile``, ``zos_encode``.
  * Fix ``zos_copy`` record format.
  * Fix ``zos_job_submit`` allowable characters for data sets.
  * Update ``zos_fetch`` and ``zos_copy`` with option **ignore_sftp_stderr**
    to alter module behavior.
  * Fix ``zos_operator_action_query`` so that all outstanding messages are
    returned.
  * Update ``zos_mvs_raw`` with verbose option.
* Documentation

  * Update documentation in support of `centralized content`_.
* New playbook to aid in generating **group_vars**

Availability
------------

* `Galaxy`_
* `GitHub`_

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities 1.0.3 PTF UI70435
* Supported by z/OS V2R3
* The z/OS® shell

Known issues
------------

* Modules

  * When executing programs using ``zos_mvs_raw``, you may encounter errors
    that originate in the programs implementation. Two such known issues are
    noted below of which one has been addressed with an APAR.

    #. ``zos_mvs_raw`` module execution fails when invoking
       Database Image Copy 2 Utility or Database Recovery Utility in conjunction
       with FlashCopy or Fast Replication.
    #. ``zos_mvs_raw`` module execution fails when invoking DFSRRC00 with parm
       "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is
       addressed by APAR PH28089.

.. _centralized content:
   https://ibm.github.io/z_ansible_collections_doc/index.html


Version 1.2.0-beta.1
====================

Notes
-----

* Update recommended
* New modules

  * zos_copy
  * zos_lineinfile
  * zos_mvs_raw

* Bug fixes
* Documentation updates
* New samples
* Module enhancements:

  * zos_data_set - includes full multi-volume support for data set creation,
    addition of secondary space option, improved SMS support with storage,
    data, and management classes

Availability
------------

* Galaxy
* GitHub

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities 1.0.3 PTF UI70435
* Supported by z/OS V2R3
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

* Automation Hub
* Galaxy
* GitHub

Reference
---------

* Supported by IBM Open Enterprise Python for z/OS: 3.8.2 or later
* Supported by IBM Z Open Automation Utilities: 1.0.3 PTF UI70435
* Supported by z/OS V2R3
* The z/OS® shell


Version 1.1.0-beta1
===================

Notes
-----

* Update recommended
* New modules

  * zos_fetch, zos_encode, zos_operator_action_query, zos_operator,
    zos_tso_command, zos_ping
* New filter
* Improved error handling and messages
* Bug fixes
* Documentation updates
* New samples

Availability
------------

* Galaxy
* GitHub

Reference
---------

* Supported by IBM Z Open Automation Utilities: 1.0.2 or 1.0.3 PTF UI70435

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

* Automation Hub
* Galaxy
* GitHub

Reference
---------

* Supported by IBM Z Open Automation Utilities: 1.0.1 PTF UI66957 through
  1.0.3 PTF UI70435


Version 0.0.4
=============

Notes
-----

* Update recommended
* Includes fixes to modules zos_job_output and zos_job_submit
* Improved buffer utilization
* Optimized JSON response
* Functional test cases for all modules
* Updated document references

Availability
------------

* Galaxy
* GitHub

Reference
---------

* Supported by IBM Z Open Automation Utilities: 1.0.1 PTF UI66957 through
  1.0.3 PTF UI70435


Version 0.0.3
=============

Notes
-----

* Update recommended
* Includes updates to README.md for a malformed URL and product direction
* Includes fixes for zos_data_set module

Availability
------------

* Galaxy
* GitHub

Reference
---------

* Supported by IBM Z Open Automation Utilities: 1.0.1 PTF UI66957 through
  1.0.3 PTF UI70435

Version 0.0.2
=============

Notes
-----

* Update not required
* Updates to the README and included docs

Availability
------------

* Galaxy
* GitHub

Reference
---------

* Supported by IBM Z Open Automation Utilities: 1.0.1 PTF UI66957 through
  1.0.3 PTF UI70435


Version 0.0.1
=============

Notes
-----

* Initial beta release of IBM Z core collection, referred to as ibm_zos_core
  which is part of the broader offering
  Red Hat® Ansible Certified Content for IBM Z.

Availability
------------

* Galaxy
* GitHub

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
   https://www.ibm.com/support/knowledgecenter/SSKFYE_1.1.0/install.html

.. _z/OS® shell:
   https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm

.. _z/OS V2R3:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3/en/homepage.html

.. _playbook repository:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/README.md

.. _FAQs:
   https://ibm.github.io/z_ansible_collections_doc/faqs/faqs.html

.. _playbook configuration:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/docs/share/configuration_guide.md



