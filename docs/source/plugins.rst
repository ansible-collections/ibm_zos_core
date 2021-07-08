.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Plugins
=======

Plugins that come with the **IBM z/OS core collection** augment Ansible's core
functionality. Ansible uses a plugin architecture to enable a rich, flexible
and expandable feature set.

Action
------

* ``zos_ping``: A fork of Ansible `normal.py`_ action plugin that is modified to allow a conditional shebang line in REXX modules.

* ``zos_job_submit``: Used to `submit a job`_ from the controller and optionally monitor the job completion.

.. _normal.py:
   https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py
.. _submit a job:
   modules/zos_job_submit.html
