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

* ``normal``: A fork of Ansible `normal.py`_ action plugin that is modified to allow a conditional shebang line in REXX modules.

* ``zos_job_submit``: Used to `submit a job`_ from the controller and optionally monitor for job completion.

.. _normal.py:
   https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py
.. _submit a job:
   modules/zos_job_submit.html

Connection
----------

* ``zos_ssh``: Enables the Ansible controller to communicate to a z/OS target machine by using ssh, with the added support to transfer ASCII as EBCDIC when transferring REXX modules. This connection plugin was forked from the Ansible `ssh.py`_ connection plugin.
* For further reference, see the `zos_ssh quickstart`_ guide.

.. _ssh.py:
        https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/connection/ssh.py
.. _zos_ssh quickstart:
   quickstart.html#z-os-connection-plugin



