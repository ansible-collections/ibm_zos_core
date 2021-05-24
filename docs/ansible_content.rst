.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

=========
z/OS Core
=========

The **IBM® z/OS® core collection**, also represented as
`ibm_zos_core`_ in this document, is  part of the broader
initiative to bring Ansible® Automation to IBM Z® through the offering
**Red Hat® Ansible Certified Content for IBM Z**.

The **IBM z/OS core collection** supports automation tasks such as
creating data sets, submitting jobs, querying jobs,
retrieving job output, encoding data sets, fetching data sets, copying data
sets, executing operator commands, executing TSO commands, ping,
querying operator actions, APF authorizing libraries,
editing textual data in data sets or Unix System Services files,
finding data sets, backing up and restoring data sets and
volumes and running z/OS programs without JCL.

The Ansible modules in this collection are written in Python and REXX and
interact with `Z Open Automation Utilities`_.

.. _ibm_zos_core:
   https://galaxy.ansible.com/ibm/ibm_zos_core
.. _Z Open Automation Utilities:
   https://www.ibm.com/support/knowledgecenter/SSKFYE

.. toctree::
   :maxdepth: 1
   :caption: Collection Content

   source/plugins
   source/modules
   source/filters
