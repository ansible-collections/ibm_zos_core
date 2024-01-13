.. ...........................................................................
.. Auto generated restructured text                                          .
.. ...........................................................................
.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

============
Requirements
============

The **IBM z/OS core collection** requires both a **control node** and
**managed node** be configured with a minimum set of requirements. The
control node is often referred to as the **controller** and the
managed node as the **host** or **target**.

Control node
============
The controller is where the Ansible engine that runs the playbook is installed.
Refer to RedHat Ansible Certified Content documentation for more on the `controllers dependencies`_.

.. _controllers dependencies:
   https://ibm.github.io/z_ansible_collections_doc/requirements/requirements.html#control-node
.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Managed node
============

The managed z/OS node is the host that is managed by Ansible, as identified in
the Ansible inventory. For the **IBM z/OS core collection** to manage the z/OS node,
some dependencies are required to be installed on z/OS such as:

* `z/OS`_
* `z/OS`_
* `z/OS OpenSSH`_
* `z/OS® shell`_
* `IBM Open Enterprise SDK for Python`_
* `IBM Z Open Automation Utilities`_


.. note::

   Each release of the IBM z/OS core collection depends on specific dependency
   versions. For information on the dependencies or the versions, review the
   `release notes`_ reference section. 

z/OS shell
----------

Currently, only the `z/OS® shell`_ is supported. Using ``ansible_shell_executable``
to change the default shell is discouraged. Shells such as ``bash`` are not supported
because it handles the reading and writing of untagged files differently. 

Open Enterprise SDK for Python
------------------------------

The **IBM z/OS core collection** requires that the **IBM Open Enterprise SDK for Python** 
be installed on z/OS. 

**Installation**

* Visit the `IBM Open Enterprise SDK for Python`_ product page for the FMID,
  program directory, fix list, latest PTF, installation and configuration
  instructions.
* For reference, the Program IDs are:

  * 5655-PYT for the base product
  * 5655-PYS for service and support
* Optionally, `download the IBM Open Enterprise SDK for Python`_ no cost
  addition for installation.

IBM Z Open Automation Utilities
-------------------------------

IBM Z Open Automation Utilities provide support for executing automation tasks
on z/OS. It can run z/OS programs such as IEBCOPY, IDCAMS and IKJEFT01, perform
data set operations and much more in the scripting language of your choice.

**Installation**

* Visit the `IBM Z Open Automation Utilities`_ product page for the FMID,
  program directory, fix list, latest PTF, installation, and configuration
  instructions.
* For reference, the Program IDs are:

  * 5698-PA1 for the base product
  * 5698-PAS for service and support
* Optionally, `download the IBM Z Open Automation Utilities`_ no cost
  addition for installation.


.. _z/OS:
   https://www.ibm.com/docs/en/zos

.. _z/OS OpenSSH:
   https://www.ibm.com/docs/en/zos/latest?topic=zbed-zos-openssh

.. _z/OS® shell:
   https://www.ibm.com/docs/en/zos/latest?topic=guide-zos-shells

.. _IBM Open Enterprise SDK for Python:
   https://www.ibm.com/products/open-enterprise-python-zos

.. _IBM Z Open Automation Utilities:
   https://www.ibm.com/docs/en/zoau

.. _release notes:
   release_notes.html

.. _download the IBM Open Enterprise SDK for Python:
   https://www.ibm.com/account/reg/us-en/signup?formid=urx-49465

.. _download the IBM Z Open Automation Utilities:
   https://ibm.github.io/mainframe-downloads/downloads.html#devops