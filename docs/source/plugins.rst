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
  allow a conditional shebang line in REXX modules.
* ``zos_copy``: Used to `copy data`_ from the controller to the z/OS managed
  node.
* ``zos_fetch``: Used to `fetch data`_ from the z/OS managed node to the
  controller.
* ``zos_job_submit``: Used to `submit a job`_ from the controller and optionally
  monitor the job completion.

.. _normal:
   https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py
.. _copy data:
   modules/zos_copy.html
.. _fetch data:
   modules/zos_fetch.html
.. _submit a job:
   modules/zos_job_submit.html

Connection
----------

* ``zos_ssh``: Enables the Ansible controller to communicate with a z/OS managed
  node using SSH, SFTP and SCP. The ``zos_ssh`` connection plugin adds support
  to transfer ASCII as EBCDIC when transferring REXX modules. This connection
  plugin extends the Ansible `ssh`_ connection plugin.
* For further reference, see **z/OS Connection Plugin**.

.. _ssh:
        https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/connection/ssh.py

z/OS Connection Plugin
----------------------

Since EBCDIC encoding is used on z/OS, custom plugins are required to determine
the correct transport method when targeting a z/OS system. The ``zos_ssh``
connection plugin is a fork of the default ``ssh`` plugin with the added
functionality to check if a module is written in REXX.

Since REXX scripts are required be in EBCDIC encoding to run, they must be
handled differently during transfer. If the string
``__ANSIBLE_ENCODE_EBCDIC__`` is found in the first line of the module, the
module is transferred to the target system using SCP. Otherwise, SFTP is used.
SCP treats files as text, automatically encoding as EBCDIC at transfer time.
SFTP treats files as binary, performing no encoding changes.

**REXX Module Configuration**:

* Ensure a REXX modules first line is a comment containing the case insensitive
  keyword ``rexx`` followed by the case sensitive value
  ``__ANSIBLE_ENCODE_EBCDIC__``


**Example REXX module**:

.. code-block:: sh

   /* rexx  __ANSIBLE_ENCODE_EBCDIC__  */
   x = 55
   SAY '{"SYSTEM_VERSION":"' x '"}'
   RETURN 0


