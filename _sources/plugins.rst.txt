Plugins
=======

Plugins that come with **IBM Z Core Collection** augment Ansible’s core
functionality. Ansible uses a plugin architecture to enable a rich, flexible
and expandable feature set.

Action
------

* `normal`_: A fork of Ansible `normal.py`_ action plugin that is modified to allow a conditional shebang line in REXX modules.
* `zos_job_submit`_: Used to submit a job from the controller and optionally monitor for job completion.

.. _normal:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-rexx-connection-plugin.md
.. _normal.py:
   https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py
.. _zos_job_submit:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-job-submit.md

Connection
----------

* `zos_ssh`_: Enables the Ansible controller to communicate to a Z target machine by using ssh, with the added support to transfer ASCII as EBCDIC when transferring REXX modules. This connection plugin was forked from the Ansible `ssh.py`_ connection plugin.
* For further reference, see the `zos_ssh quickstart`_ guide.

.. _zos_ssh:
   https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-rexx-connection-plugin.md
.. _ssh.py:
        https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/connection/ssh.py
.. _zos_ssh quickstart:
   quickstart.html#z-os-connection-plugin

.. ....................................
.. Copyright                          .
.. © Copyright IBM Corporation 2020   .
.. ....................................

