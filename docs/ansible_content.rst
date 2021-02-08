.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

=========
z/OS Core
=========

The **IBM z/OS core collection**, also represented as
**ibm_zos_core** in this document, is  part of the broader
initiative to bring Ansible Automation to IBM Z® through the offering
**Red Hat® Ansible Certified Content for IBM Z®**. The
**IBM z/OS core collection** supports automation tasks such as
creating data sets, submitting jobs, querying jobs,
retrieving job output, encoding data sets, fetching data sets, copying data
sets, executing operator commands, executing TSO commands, ping,
querying operator actions, APF authorizing libraries,
editing textual data in data sets or Unix System Services files,
finding data sets, backing up and restoring data sets and
volumes and running z/OS programs without JCL.

The **IBM z/OS core collection** is a dependency for other collections
under the **Red Hat® Ansible Certified Content for IBM Z** offering and
works closely with collections such as `IBM z/OS IMS collection`_ to deliver
a solution that will enable you to automate tasks on z/OS subsystems such
as IMS.

.. _IBM z/OS IMS collection:
   https://github.com/ansible-collections/ibm_zos_ims

.. toctree::
   :maxdepth: 1
   :caption: Reference

   source/plugins
   source/modules
   source/filters
