.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Modules
=======

The **IBM z/OS core** collection contains modules that can be used in a playbook
to automate tasks on **z/OS**. Ansible executes each module on the target node
and returns the result back to the controller. While different modules perform
different tasks, their interfaces and responses follow similar patterns.

Modules include documentation, samples and return values similar to UNIX,
or UNIX-like operating system man page (manual page). This documentation can
be accessed from the command line by using the ``ansible-doc`` command
documented in the `Ansible guide`_.

Here's how to use the ``ansible-doc`` command after you install the
**IBM z/OS core collection**: ``ansible-doc ibm.ibm_zos_core.zos_data_set``

.. code-block:: sh

   $ansible-doc ibm.ibm_zos_core.zos_data_set

   > ZOS_DATA_SET    (/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core/plugins/modules/zos_data_set.py)

      Create, delete and set attributes of data sets. When forcing data set replacement, contents will not be preserved.

    OPTIONS (= is mandatory):

    - batch
            Batch can be used to perform operations on multiple data sets in a single module call.
            Each item in the list expects the same options as zos_data_set.
            type: list

    - data_class
            The data class name (required for SMS-managed data sets)
            type: str

.. _Ansible guide:
   https://docs.ansible.com/ansible/latest/cli/ansible-doc.html#ansible-doc

.. toctree::
   :maxdepth: 1
   :glob:

   modules/*



