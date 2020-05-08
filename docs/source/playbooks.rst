.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Playbooks
=========

The sample playbooks that are **included** in the **IBM z/OS core collection**
demonstrate how to use the collection content.

Playbook Documentation
----------------------

An `Ansible playbook`_ consists of organized instructions that define work for
a managed node (host) to be managed with Ansible.

A `playbooks directory`_ that contains a sample playbook is included in the
**IBM z/OS core collection**. The sample playbook can be run with the
``ansible-playbook`` command with some modification to the **inventory**,
**ansible.cfg** and **group_vars**.

You can find the playbook content that is included with the collection in the
same location where the collection is installed. For more information, refer to
the `installation documentation`_. In the following examples, this document will
refer to the installation path as ``~/.ansible/collections/ibm/ibm_zos_core``.

.. _Ansible playbook:
   https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#playbooks-intro
.. _playbooks directory:
   https://github.com/ansible-collections/ibm_zos_core/tree/master/playbooks
.. _installation documentation:
   installation.html


Sample Configuration and Setup
------------------------------
Each release of Ansible provides options in addition to the ones identified in
the sample configurations that are included with this collection. These options
allow you to customize how Ansible operates in your environment. Ansible
supports several sources to configure its behavior and all sources follow the
Ansible `precedence rules`_.

The Ansible configuration file `ansible.cfg` can override almost all
``ansible-playbook`` configurations. Included in the `playbooks directory`_ is a
sample `ansible.cfg`_ that can supplement ``ansible-playbook`` with a
little modification. In the sample `ansible.cfg`_, the only required
configuration is ``pipelining = True``

You can specify the SSH port used by Ansible and instruct Ansible where to
write the temporary files on the target. This can be easily done by adding the
options to your inventory or `ansible.cfg`.

An example of adding these options to `ansible.cfg` is shown below. For more
details, see the sample `ansible.cfg`_ notes.

.. code-block:: yaml

   [defaults]
   forks = 25
   remote_tmp = /u/ansible/tmp
   remote_port = 2022

For more information about available configurations for ``ansible.cfg``, read
the Ansible documentation on `Ansible configuration settings`_.

.. _ansible.cfg:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/ansible.cfg
.. _Ansible configuration settings:
   https://docs.ansible.com/ansible/latest/reference_appendices/config.html#ansible-configuration-settings-locations
.. _precedence rules:
   https://docs.ansible.com/ansible/latest/reference_appendices/general_precedence.html#general-precedence-rules

Inventory
---------

Ansible works with multiple managed nodes (hosts) at the same time, using a
list or group of lists known as an `inventory`_. Once the inventory is defined,
you can use `patterns`_ to select the hosts or groups that you want Ansible to
run against.

Included in the `playbooks directory`_ is a `sample inventory file`_ that can be
used to manage your nodes with a little modification. This inventory file
should be included when running the sample playbook.

.. code-block:: yaml

   zsystem:
     hosts:
       zvm:
         ansible_host: zos_target_address
         ansible_user: zos_target_username
         ansible_python_interpreter: path_to_python_interpreter_binary_on_zos_target


The value for the property **ansible_host** is the hostname of the managed node;
for example, ``ansible_host: ec33017A.vmec.svl.ibm.com``

The value for the property **zos_target_username** is the user name to use when
connecting to the host; for example, ``ansible_user: omvsadm``.

The value for the property **ansible_python_interpreter** is the target host
Python path. This is useful for systems with more than one Python installation,
or when Python is not installed in the default location **/usr/bin/python**;
for example, ``ansible_python_interpreter: /usr/lpp/rsusr/python36/bin/python``

For more information on Python configuration requirements on z/OS, refer to
Ansible `FAQ`_.

Behavioral inventory parameters such as ``ansible_port`` which allows you
to set the port for a host can be reviewed in the
`behavioral inventory parameters`_.

.. _inventory:
   https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
.. _patterns:
   https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html#intro-patterns
.. _sample inventory file:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/inventory
.. _FAQ:
   https://docs.ansible.com/ansible/latest/reference_appendices/faq.html#running-on-z-os
.. _behavioral inventory parameters:
   https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters


Group_vars
----------

Although you can store variables in the inventory file, storing separate host
and group variables files may help you organize your variable values more
easily. Included with the sample playbook is a sample variables
file `all.yml`_.

The value for the property **BPXK_AUTOCVT** must be configured to ``ON``.

The value for the property **ZOAU_HOME** is the ZOA Utilities install root path;
for example, ``/usr/lpp/IBM/zoautil``.

The value for the property **PYTHONPATH** is the ZOA Utilities Python library
path; for example, ``/usr/lpp/IBM/zoautil/lib/``.

The value for the property **LIBPATH** is both the path to the Python libraries
on the target and the ZOA Utilities Python library path separated by
colons ``:``; for example,
``/usr/lpp/IBM/zoautil/lib/:/usr/lpp/rsusr/python36/lib:/lib:/usr/lib:.``.

The value for the property **PATH** is the ZOA utilities BIN path and the Python
interpreter path; for example,
``/usr/lpp/IBM/zoautil/bin:/usr/lpp/rsusr/python36/bin/python:/bin``.

.. code-block:: yaml

   environment_vars:
      _BPXK_AUTOCVT: ON
      ZOAU_HOME: '/usr/lpp/IBM/zoautil'
      PYTHONPATH: '/usr/lpp/IBM/zoautil/lib'
      LIBPATH: '/usr/lpp/IBM/zoautil/lib/:/usr/lpp/rsusr/python36/lib:/usr/lib:/lib:.'
      PATH: '/usr/lpp/IBM/zoautil/bin:/usr/lpp/rsusr/python36/bin/python:/bin'

.. note::
   In ZOAU 1.0.2 and later, the property **ZOAU_ROOT** is no longer supported
   and can be replaced with the property **ZOAU_HOME**. If you are using ZOAU
   version 1.0.1 or lower, you must continue to use the property
   **ZOAU_ROOT** which is the ZOA Utilities install root path required for
   ZOAU; for example, ``/usr/lpp/IBM/zoautil``.

.. _all.yml:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/group_vars/all.yml



Run the playbook
----------------

Access the sample Ansible playbook and ensure that you are within the collection
playbooks directory where the sample files are included:
``~/.ansible/collections/ibm/ibm_zos_core/playbooks/``.

Use the Ansible command ``ansible-playbook`` to run the sample playbook.  The
command syntax is ``ansible-playbook -i <inventory> <playbook>``; for example,
``ansible-playbook -i inventory zos-collection-sample.yaml``.

This command assumes that the controller's public SSH key has been shared with
the managed node. If you want to avoid entering a username and password each
time, copy the SSH public key to the managed node using the ``ssh-copy-id``
command; for example, ``ssh-copy-id -i ~/.ssh/mykey.pub user@<hostname>``.

Alternatively, you can use the ``--ask-pass`` option to be prompted for the
user's password each time a playbook is run; for example,
``ansible-playbook -i inventory zos-collection-sample.yaml --ask-pass``.

.. note::
   * Using ``--ask-pass`` is not recommended because it will hinder performance.
   * Using ``--ask-pass`` requires ``sshpass`` be installed on the controller.
     For further reference, see the `ask-pass documentation`_.

Optionally, you can configure the console logging verbosity during playbook
execution. This is helpful in situations where communication is failing and
you want to obtain more details. To adjust the logging verbosity, append more
letter `v`'s; for example, `-v`, `-vv`, `-vvv`, or `-vvvv`. Each letter `v`
increases logging verbosity similar to traditional logging levels INFO, WARN,
ERROR, DEBUG.

.. note::
   It is a good practice to review the playbook samples before executing them.
   It will help you understand what requirements in terms of space, location,
   names, authority, and artifacts will be created and cleaned up. Although
   samples are always written to operate without the need for the user's
   configuration, flexibility is written into the samples because it is not
   easy to determine if a sample has access to the host's resources.
   Review the playbook notes sections for additional details and
   configuration.

   Sample playbooks often submit JCL that is included with this collection
   under the `files directory`_. Review the sample JCL for necessary edits to
   allow for submission on the target system. The most common changes are to
   add a CLASS parameter and change the NOTIFY user parameter. For more details,
   see the JCL notes section included in the collection.

.. _ask-pass documentation:
   https://linux.die.net/man/1/sshpass

.. _files directory:
   https://github.com/ansible-collections/ibm_zos_core/tree/dev/playbooks/files





