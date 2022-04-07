.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2021                                          .
.. ...........................................................................

Modules
=======

The **IBM z/OS core** collection contains modules that can be used in a playbook
to automate tasks on **z/OS**. Ansible executes each module on the target node
and returns the result back to the controller. While different modules perform
different tasks, their interfaces and responses follow similar patterns.

You can also access the documentation of each module from the command line by
using the `ansible-doc`_ command, for example:

.. code-block:: sh

   $ ansible-doc ibm.ibm_zos_core.zos_data_set

.. _ansible-doc:
   https://docs.ansible.com/ansible/latest/cli/ansible-doc.html#ansible-doc

.. toctree::
   :maxdepth: 1
   :glob:

   modules/*



