.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Plugins
=======

Plugins that come with the **IBM z/OS core collection** complement Ansible's core
functionality. Ansible uses a plugin architecture to enable a rich, flexible
and expandable feature set.

Action
------

Action plugins integrate local processing and local data with module functionality.
Action plugins are executed by default when an associated module is used; no additional
user action is required, this documentation is reference only.

* `zos_copy`_: Used to copy data from the controller to the z/OS manage node.
* `zos_fetch`_: Used to fetch data from the z/OS managed node to the controller.
* `zos_job_submit`_: Used to submit a job from the controller to the z/OS manage node.
* `zos_ping`_: Used to transfer the modules REXX source to the z/OS managed node.
* `zos_script`_: Used to transfer scripts from the controller to the z/OS manage node.
* `_zos_unarchive`_: Used to transfer archives from the controller to the z/OS manage node.

.. _zos_copy:
   modules/zos_copy.html
.. _zos_fetch:
   modules/zos_fetch.html
.. _zos_job_submit:
   modules/zos_job_submit.html
.. _zos_ping:
   modules/zos_ping.html
.. _zos_script:
   modules/zos_script.html
.. _zos_unarchive:
   modules/zos_unarchive.html
