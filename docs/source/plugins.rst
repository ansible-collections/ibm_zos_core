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

* ``zos_ping``: A fork of Ansible `normal`_ action plugin that is modified to
  support modules written in REXX such as `zos_ping`_.
* ``zos_copy``: Used to `copy data`_ from the controller to the z/OS managed
  node.
* ``zos_fetch``: Used to `fetch data`_ from the z/OS managed node to the
  controller.
* ``zos_job_submit``: Used to `submit a job`_ from the controller and optionally
  monitor the job completion.

.. _normal:
   https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py
.. _zos_ping:
   modules/zos_ping.html
.. _copy data:
   modules/zos_copy.html
.. _fetch data:
   modules/zos_fetch.html
.. _submit a job:
   modules/zos_job_submit.html

