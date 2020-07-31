.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

============
Requirements
============

The **IBM z/OS core collection**, requires both a **control node** and
**managed node** be configured with a minimum set of requirements. The
control node is often referred to as the **controller** and the
managed node as the **host**.

Control node
============
The controller is where the Ansible engine is installed which ends up
running the playbook. Refer to our main documentation for more on
the `controllers dependencies`_.

.. _controllers dependencies:
   https://ibm.github.io/z_ansible_collections_doc/requirements/requirements_controller.html


Managed node
============

The managed z/OS node is the host that will be managed by Ansible identified in
the Ansbiel inventory. The managed node requires dependencies that are specific
to each release of the **IBM z/OS core collection**.

.. toctree::
   :maxdepth: 3

   requirements_managed

