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

* `IBM Open Enterprise Python for z/OS`_
* z/OS `V2R3`_ or `later`_
* `IBM Z Open Automation Utilities`_ (ZOAU)

   .. note::

     IBM z/OS core collection is dependent on specific versions of ZOAU.
     For information about the required version of ZOAU, review the
     `release notes`_.

     Before attempting to run an Ansible playbook, please review the required
     environment parameters documented in our playbook repository under the
     `playbook configuration`_ topic. In addition to the
     `playbook configuration`_, review our `FAQs`_ for additional help.

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

* `z/OS OpenSSH`_
* The `z/OS® shell`_

   .. note::
      Currently, only ``z/OS® shell`` is supported. Using
      ``ansible_shell_executable`` to change the default shell is discouraged.
      For more information, see `Ansible documentation`_.

      Shells such as ``bash`` are not supported because they handle the reading
      and writing of untagged files differently. ``bash`` added enhanced ASCII
      support in version 4.3 and thus differs from 4.2. If ``bash`` shell is the
      only shell available, you must control how the new and existing files are
      tagged and encoded. This can be controlled by setting both
      "_ENCODE_FILE_NEW" and "_ENCODE_FILE_EXISTING".

      For example,

      * _ENCODE_FILE_NEW: "IBM-1047"
      * _ENCODE_FILE_EXISTING: "IBM-1047"

      Please review the README.ZOS guide included with the ported ``bash`` shell
      for further configurations.

.. _Ansible documentation:
   https://docs.ansible.com/ansible/2.7/user_guide/intro_inventory.html

.. _Python on z/OS:
   requirements_managed.html#id1

.. _V2R3:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3/en/homepage.html

.. _later:
   https://www.ibm.com/support/knowledgecenter/SSLTBW

.. _IBM Z Open Automation Utilities:
   requirements_managed.html#zoau

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

