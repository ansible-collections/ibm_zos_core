.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2021                                          .
.. ...........................................................................

Roles
=====

The IBM XXXX core collection contains roles that can be used in a playbook to
automate tasks on z/OS. Ansible executes each role on the target node
unless the playbook has delegated the task to localhost and
returns the result back to the controller. While different roles perform
different tasks, their interfaces and responses follow similar patterns.

Each role's variables can be configured or defaults accepted. The role's contain
a README and documentation can be accessed online.

.. toctree::
   :maxdepth: 1
   :glob:

   roles/*



