.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Playbooks
=========

The sample playbooks that are **included** demonstrate how to use the
collection content in the IBM z/OS core collection.

Playbook Documentation
----------------------

An `Ansible playbook`_ consists of organized instructions that define work for
a managed node (hosts) to be managed with Ansible.

Included in the **IBM z/OS core collection** is a `playbooks directory`_ that
contains a sample playbook that with some modification to the **inventory**,
**ansible.cfg** and **group_vars** can be run with the ``ansible-playbook``
command.

You can find the playbook content that is included with the collection where
the collection was installed, please refer back to the
`installation documentation`_. In the following examples, this document will
refer to the installation path as ``~/.ansible/collections/ibm/ibm_zos_core``.

.. _Ansible playbook:
   https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#playbooks-intro
.. _playbooks directory:
   https://github.com/ansible-collections/ibm_zos_core/tree/master/playbooks
.. _installation documentation:
   installation.html


Sample Configuration and Setup
---------------------------------------

Ansible config file `ansible.cfg` can override nearly all
``ansible-playbook`` configurations. Also included in the
`playbooks directory`_ is a sample `ansible.cfg`_ that with little
modification can supplement ``ansible-playbook``.

In the sample `ansible.cfg`_, the only required configuration is:
``pipelining = True``

For more information about available configurations for ``ansible.cfg``, read
the Ansible documentation on `Ansible configuration settings`_.

.. _ansible.cfg:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/ansible.cfg
.. _Ansible configuration settings:
   https://docs.ansible.com/ansible/latest/reference_appendices/config.html#ansible-configuration-settings-locations

Inventory
---------

Ansible works with multiple managed nodes (hosts) at the same time, using a
list or group of lists know as an `inventory`_. Once the inventory is defined,
you can use `patterns`_ to select the hosts, or groups, you want Ansible to run
against.

Included in the `playbooks directory`_ is a `sample inventory file`_ that with
little modification can be used to manage your nodes. This inventory file
should be included when running the sample playbook.

.. code-block:: yaml

   zsystem:
     hosts:
       zvm:
         ansible_host: zos_target_address
         ansible_user: zos_target_username
         ansible_python_interpreter: path_to_python_interpreter_binary_on_zos_target


The value for property **ansible_host** is the hostname of the manage node, for
example, ``ansible_host: ec33017A.vmec.svl.ibm.com``

The value for property **zos_target_username** is the user name to use when
connecting to the host, for example, ``ansible_user: omvsadm``.

The value for property **ansible_python_interpreter** is the target host python
path. This is useful for systems with more than one Python installation, or
when Python is not located at in the default location **/usr/bin/python**, for
example, ``ansible_python_interpreter: /usr/lpp/rsusr/python36/bin/python``

For more information on python configuration requirements on z/OS, refer to
Ansible `FAQ`_.

.. _inventory:
   https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
.. _patterns:
   https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html#intro-patterns
.. _sample inventory file:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/inventory
.. _FAQ:
   https://docs.ansible.com/ansible/latest/reference_appendices/faq.html#running-on-z-os


Group_vars
----------

Although you can store variables in the inventory file, storing separate host
and group variables files may help you organize your variable values more
easily. Included with the sample playbook is a sample variables
file `all.yml`_.

The value for property **BPXK_AUTOCVT** must be configured to ``ON``.

The value for property **ZOAU_ROOT** is the ZOA Utilities install root path,
for example, ``/usr/lpp/IBM/zoautil``.

The value for property **PYTHONPATH** is the ZOA Utilities Python library path,
for example, ``/usr/lpp/IBM/zoautil/lib/``.

The value for property **LIBPATH** is both the path to the python libraries on
the target and the ZOA Utilities Python library path separated by
semi-colons ``:``, for example,
``/usr/lpp/IBM/zoautil/lib/:/usr/lpp/rsusr/python36/lib:/lib:/usr/lib:.``.

The value for property **PATH** is the ZOA utilities BIN path and Python
interpreter path, for example,
``/usr/lpp/IBM/zoautil/bin;/usr/lpp/rsusr/python36/bin/python``.

.. code-block:: yaml

   environment_vars:
      _BPXK_AUTOCVT: ON
      ZOAU_ROOT: '/usr/lpp/IBM/zoautil'
      PYTHONPATH: '/usr/lpp/IBM/zoautil/lib'
      LIBPATH: '/usr/lpp/IBM/zoautil/lib/:/usr/lpp/rsusr/python36/lib:/usr/lib:/lib:.'
      PATH: '/usr/lpp/IBM/zoautil/bin;/usr/lpp/rsusr/python36/bin/python'

.. _all.yml:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/group_vars/all.yml


Run the playbook
----------------

Access the sample Ansible playbook and ensure you are within the collection
playbooks directory where the sample files are included,
``~/.ansible/collections/ibm/ibm_zos_core/playbooks/``.

Use the Ansible command ``ansible-playbook`` to run the sample playbook.  The
command syntax is ``ansible-playbook -i <inventory> <playbook>``, for example,
``ansible-playbook -i inventory zos-collection-sample.yaml``.

This command assumes the controllers public SSH key has been shared with the
managed node. If you want to avoid entering a username and password each time,
copy the SSH public key to the managed node using the ``ssh-copy-id`` command,
for example, ``ssh-copy-id -i ~/.ssh/mykey.pub user@<hostname>``.

Alternatively, you can use the ``--ask-pass`` option to be prompted for the
users password each time a playbook is run, for example,
``ansible-playbook -i inventory zos-collection-sample.yaml --ask-pass``.

.. note::
   * Using ``--ask-pass`` is not recommended because it will hinder performance.
   * Using ``--ask-pass`` requires ``sshpass`` be installed on the controller,
     for further reference, see the `ask-pass documentation`_.

Optionally, during playbook execution, console logging verbosity can be
configured. This is helpful in situations where communication is failing and
you want more detail. To adjust logging verbosity, append more letter `v`'s,
for example, `-v`, `-vv`, `-vvv`, or `-vvvv`.

Each letter `v` increases logging verbosity similar to traditional logging
levels INFO, WARN, ERROR, DEBUG.

.. _ask-pass documentation:
   https://linux.die.net/man/1/sshpass





