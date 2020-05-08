.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

IBM z/OS core collection
========================

The **IBM z/OS core collection**, also represented as **ibm\_zos\_core**
in this document, is part of the broader offering **Red Hat® Ansible
Certified Content for IBM Z**. IBM z/OS core collection supports tasks
such as creating data sets, submitting jobs, querying jobs,
retrieving job output, encoding data sets, fetching data sets, operator
commands, TSO commands, ping and querying operator actions.

The **IBM z/OS core collection** serves as a dependency for other collections
under the **Red Hat® Ansible Certified Content for IBM Z** umbrella and
works closely with offerings such as `IBM z/OS IMS collection`_ to deliver
a solution that will enable you to automate tasks on z/OS subsystems such
as IMS.

.. _IBM z/OS IMS collection:
   https://github.com/ansible-collections/ibm_zos_ims

Red Hat Ansible Certified Content for IBM Z
===========================================

**Red Hat® Ansible Certified Content for IBM Z** provides the ability to
connect IBM Z® to clients' wider enterprise automation strategy through the
Ansible Automation Platform ecosystem. This enables development and operations
automation on Z through a seamless, unified workflow orchestration with
configuration management, provisioning, and application deployment in one
easy-to-use platform.

IBM z/OS core collection, as part of the broader offering
**Red Hat® Ansible Certified Content for IBM Z**, will be available on both,
Galaxy as community supported and Automation Hub with enterprise support.

Features
========

The IBM z/OS core collection includes `connection plugins`_,
`action plugins`_, `modules`_, `sample playbooks`_, `filters`_ and
ansible-doc to automate tasks on z/OS.

.. _connection plugins:
   https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/connection/
.. _action plugins:
   https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/action/
.. _modules:
    https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/modules/
.. _sample playbooks:
    https://github.com/ansible-collections/ibm_zos_core/tree/master/playbooks/
.. _filters:
   https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/filter/


Copyright
=========

© Copyright IBM Corporation 2020

License
=======

Some portions of this collection are licensed under
`GNU General Public License, Version 3.0`_, and other portions of this
collection are licensed under `Apache License, Version 2.0`_.

See individual files for applicable licenses.

.. _GNU General Public License, Version 3.0:
    https://opensource.org/licenses/GPL-3.0

.. _Apache License, Version 2.0:
    https://opensource.org/licenses/Apache-2.0

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 3
   :caption: Reference

   plugins
   modules
   filters
   playbooks
   supplementary

.. toctree::
   :maxdepth: 1
   :caption: Community guides

   community_guides

.. toctree::
   :maxdepth: 1
   :caption: Requirements

   requirements

.. toctree::
   :maxdepth: 1
   :caption: Appendices

   release_notes
