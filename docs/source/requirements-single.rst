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
managed node as the **host**.

Control node
============
The controller is where the Ansible engine that runs the playbook is installed.
Refer to RedHat Ansible Certified Content documentation for more on the `controllers dependencies`_.

.. _controllers dependencies:
   https://ibm.github.io/z_ansible_collections_doc/requirements/requirements_controller.html
.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Managed node
============

The managed z/OS node is the host that is managed by Ansible, as identified in
the Ansible inventory.
The managed node has dependencies that are specific to each release of the
**IBM z/OS core collection**. Review the details of the dependencies before you
proceed to install the IBM z/OS core collection.

* z/OS `V2R3`_ or `later`_
* `z/OS OpenSSH`_
* Supported by `IBM Open Enterprise SDK for Python`_
  (previously `IBM Open Enterprise Python for z/OS`_) 3.8.2 or later
* `IBM Z Open Automation Utilities`_ (ZOAU)

   .. note::

     IBM z/OS core collection is dependent on specific versions of
     Z Open Automation Utilities (ZOAU). For information about the required
     version of ZOAU, review the `release notes`_. For detailed instructions on
     installation and configuration of ZOAU,
     `Installing and Configuring ZOA Utilities`_.

* The `z/OS® shell`_

   .. note::
      Currently, only ``z/OS® shell`` is supported. Using
      ``ansible_shell_executable`` to change the default shell is discouraged.
      For more information, see `Ansible documentation`_. Shells such as ``bash``
      are not supported because they handle the reading and writing of untagged
      files differently. Please review the README.ZOS guide included with the
      ported ``bash`` shell for further configurations.

.. _Installing and Configuring ZOA Utilities:
   https://www.ibm.com/support/knowledgecenter/en/SSKFYE_1.1.0/install.html

.. _Ansible documentation:
   https://docs.ansible.com/ansible/2.7/user_guide/intro_inventory.html

.. _Python on z/OS:
   requirements-single.html#id1

.. _V2R3:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3/en/homepage.html

.. _later:
   https://www.ibm.com/support/knowledgecenter/SSLTBW

.. _IBM Z Open Automation Utilities:
   requirements-single.html#id1

.. _z/OS OpenSSH:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2.e0za100/ch1openssh.htm

.. _release notes:
   release_notes.html

.. _playbook configuration:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/docs/share/configuration_guide.md

.. _FAQs:
   https://ibm.github.io/z_ansible_collections_doc/faqs/faqs.html

.. _z/OS® shell:
   https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm

.. _Z Open Automation Utilities 1.1.0:
   https://www.ibm.com/support/knowledgecenter/SSKFYE_1.1.0/install.html

.. _configured IBM Open Enterprise Python on z/OS:
   https://www.ibm.com/support/knowledgecenter/SSCH7P_3.8.0/install.html

Python on z/OS
--------------

If the Ansible target is z/OS, you must install
**IBM Open Enterprise Python for z/OS** which is ported for the z/OS platform
and required by **IBM z/OS core collection**.

**Installation**

* Visit the `IBM Open Enterprise Python for z/OS`_ product page for FMID,
  program directory, fix list, latest PTF, installation and configuration
  instructions.
* For reference, the Program IDs are:

  * 5655-PYT for the base product
  * 5655-PYS for service and support
* Optionally, download **IBM Open Enterprise Python for z/OS**, `here`_
* For the supported Python version, refer to the `release notes`_.

.. _IBM Open Enterprise Python for z/OS:
   http://www.ibm.com/products/open-enterprise-python-zos

.. _IBM Open Enterprise SDK for Python:
   https://www.ibm.com/products/open-enterprise-python-zos

.. _here:
   https://www-01.ibm.com/marketing/iwm/platform/mrs/assets?source=swg-ibmoep

.. note::

   Currently, IBM Open Enterprise Python for z/OS is the supported and
   recommended Python distribution for use with Ansible and ZOAU. If
   Rocket Python is the only available Python on the target, review the
   `recommended environment variables`_ for Rocket Python.

.. _recommended environment variables:
   https://github.com/IBM/z_ansible_collections_samples/blob/master/docs/share/configuration_guide.md#variables

ZOAU
----

IBM Z Open Automation Utilities provide support for executing automation tasks
on z/OS. With ZOAU, you can run traditional MVS commands such as IEBCOPY,
IDCAMS, and IKJEFT01, as well as perform a number of data set operations
in the scripting language of your choice.

**Installation**

* Visit the `ZOAU`_ product page for the FMID, program directory, fix list,
  latest PTF, installation, and configuration instructions.
* For reference, the Program IDs are:

  * 5698-PA1 for the base product
  * 5698-PAS for service and support
* For ZOAU supported version, refer to the `release notes`_.

.. _ZOAU:
   https://www.ibm.com/support/knowledgecenter/en/SSKFYE

