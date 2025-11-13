.. ...........................................................................
.. © Copyright IBM Corporation 2021, 2025                                    .
.. ...........................................................................
Roles
=======

An Ansible role is a primary mechanism for organizing and reusing automation
content in a modular and portable way. A role contains a set of related tasks,
handlers, variables, and other Ansible artifacts that are packaged together to
perform a specific function. Ansible executes the contents of the role when it
is called from a playbook, allowing for the automation of complex,
multi-step processes.

The **IBM z/OS core** collection provides a set of roles designed to simplify
automation on **z/OS**. These roles can be used in playbooks to identify and
recommend migration actions between version 1 and version 2, collect
diagnostic facts for support and debugging, and easily determine whether a job
is currently running.

The **IBM z/OS core** collection provides many roles.
Reference material for each role contains documentation on how to use certain
roles in your playbook.

.. toctree::
   :maxdepth: 1
   :glob:

   roles/*