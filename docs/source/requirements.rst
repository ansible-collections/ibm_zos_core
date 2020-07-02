.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Requirements
============

A control node is any machine with Ansible installed. From the control node,
you can run commands and playbooks from a laptop, desktop, or server.
However, you cannot run **IBM z/OS core collection** on a Windows system.

A managed node is often referred to as a target node, or host, and it is managed
by Ansible. Ansible need not be installed on a managed node, but SSH must be
enabled.

The nodes listed below require these specific versions of software:

Control node
------------

* `Ansible version`_: 2.9 or later
* `Python`_: 2.7 or later
* `OpenSSH`_

.. _Ansible version:
   https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
.. _Python:
   https://www.python.org/downloads/release/latest
.. _OpenSSH:
   https://www.openssh.com/


Managed node
------------

* `IBM Open Enterprise Python for z/OS`_
* z/OS `V2R3`_ or `later`_
* `IBM Z Open Automation Utilities`_ (ZOAU)
* The z/OS® shell

   * IBM z/OS core collections are dependent on specific versions of ZOAU.
     For information about the required version of ZOAU, review the
     `release notes`_.
* `z/OS OpenSSH`_

.. note::
   Currently, the only supported shell is the ``z/OS® shell``; this is because
   shells such as ``bash`` handle the reading and writing of untagged files
   differently. ``bash`` added enhanced ASCII support in 4.3 and thus differs
   from 4.2; we encourage users avoid using ``ansible_shell_executable`` to
   change the default shell as does `Ansible documentation`_. Should the
   ``bash`` shell be the only shell available, you will need to control how
   new and existing files are tagged and encoded, this can be controlled by
   setting both "_ENCODE_FILE_NEW" and "_ENCODE_FILE_EXISTING"; for example,

   * _ENCODE_FILE_NEW: "IBM-1047"
   * _ENCODE_FILE_EXISTING: "IBM-1047"

   Please review the README.ZOS guide included with the ported ``bash`` shell
   for further configurations.

.. _Ansible documentation:
   https://docs.ansible.com/ansible/2.7/user_guide/intro_inventory.html

.. _Python on z/OS:
   requirements.html#id1

.. _V2R3:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3/en/homepage.html

.. _later:
   https://www.ibm.com/support/knowledgecenter/SSLTBW

.. _IBM Z Open Automation Utilities:
   requirements.html#id1

.. _z/OS OpenSSH:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2.e0za100/ch1openssh.htm

.. _release notes:
   release_notes.html

Python on z/OS
--------------

If the Ansible target is z/OS, you must install
**IBM Open Enterprise Python for z/OS** which is ported for the z/OS platform
and required by **IBM z/OS core Collection**.

**Installation**

* Visit the `IBM Open Enterprise Python for z/OS`_ product page for FMID,
  program directory, fix list, latest PTF, installation and configuration
  instructions.
* For reference, the Program IDs are:

  * 5655-PYT for the base product
  * 5655-PYS for service and support
* Optionally download **IBM Open Enterprise Python for z/OS**, `here`_
* For the Python supported version, refer to the `release notes`_.

.. _IBM Open Enterprise Python for z/OS:
   http://www.ibm.com/products/open-enterprise-python-zos

.. _here:
   https://www-01.ibm.com/marketing/iwm/platform/mrs/assets?source=swg-ibmoep

ZOAU
----

IBM Z Open Automation Utilities provide support for executing automation tasks
on z/OS. With ZOAU, you can run traditional MVS commands, such as IEBCOPY,
IDCAMS, and IKJEFT01, as well as perform a number of data set operations
in the scripting language of your choice.

**Installation**

* Visit the `ZOAU`_ product page for the FMID, program directory, fix list,
  latest PTF, installation and configuration instructions.
* For reference, the Program IDs are:

  * 5698-PA1 for the base product
  * 5698-PAS for service and support
* For ZOAU supported version, refer to the `release notes`_.

.. _ZOAU:
   https://www.ibm.com/support/knowledgecenter/en/SSKFYE

