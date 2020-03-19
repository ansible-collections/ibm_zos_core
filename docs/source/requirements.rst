.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Requirements
============

A control node is any machine with Ansible installed. From the control node,
you can run commands and playbooks from a laptop, desktop, or server machine.
However, you cannot run **IBM z/OS core collection** on a Windows machine.

A managed node is often referred to as a target node, or host, and is the node
that is managed by Ansible. Ansible does not need not need to be installed on
a managed node, but SSH must be enabled.

The following nodes require specific versions of software:

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

* `Python on z/OS`_: 3.6 or later
* `z/OS`_: V02.02.00 or later
* `IBM Z Open Automation Utilities`_ (ZOAU)
* `z/OS OpenSSH`_

.. _Python on z/OS:
   requirements.html#id1
.. _z/OS:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2/zos-v2r2-home.html

.. _IBM Z Open Automation Utilities:
   requirements.html#id1

.. _z/OS OpenSSH:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2.e0za100/ch1openssh.htm

Python on z/OS
--------------

If the Ansible target is z/OS, you must install a python distribution ported
for this platform. Rocket Software is currently the preferred version for z/OS.

**Installation**

* Visit the `Rocket Software homepage`_ and create a required account in the
  `Rocket Customer Portal`_.
* Click Downloads on the top left portion the page.
* Select the category z/OpenSource on left side panel.
* Scroll and select Python.
* Download the binaries, installations files, and the README.ZOS onto an x86
  machine.
* Transfer the zipped tarball (tar.gz) file to the target z/OS system and
  extract it according the instructions in the installation files.
* Follow the additional setup instructions as described in the README.ZOS file.

.. _Rocket Software homepage:
   https://www.rocketsoftware.com/zos-open-source
.. _Rocket Customer Portal:
   https://my.rocketsoftware.com/


ZOAU
----

IBM Z Open Automation Utilities provide support for executing automation tasks
on z/OS. With ZOAU, you can run traditional MVS commands, such as IEBCOPY,
IDCAMS, and IKJEFT01, as well as perform a number of data set operations
in the scripting language of your choice.

**Installation**

* For the ZOAU FMID, program directory, fix list, latest PTF, installation
  and configuration, refer to the ZOAU `product page`_.

.. _product page:
   https://www.ibm.com/support/knowledgecenter/en/SSKFYE_1.0.0/welcome_zoautil.html


