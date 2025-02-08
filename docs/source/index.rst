.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2021                                          .
.. ...........................................................................

========================
IBM z/OS core collection
========================

The **IBM z/OS core collection**, also represented as **ibm_zos_core**
in this document, is part of the broader offering **Red Hat® Ansible
Certified Content for IBM Z**. IBM z/OS core collection supports tasks
such as creating data sets, submitting jobs, querying jobs,
retrieving job output, encoding data sets, fetching data sets, operator
commands, TSO commands, ping and querying operator actions.

The **IBM z/OS core collection** serves as a dependency for other collections
under the **Red Hat® Ansible Certified Content for IBM Z** umbrella. The IBM z/OS
core collection works closely with offerings such as `IBM z/OS IMS collection`_
to deliver a solution that enables you to automate tasks on z/OS subsystems such
as IMS.

.. _IBM z/OS IMS collection:
   https://galaxy.ansible.com/ibm/ibm_zos_ims

Red Hat Ansible Certified Content for IBM Z
===========================================

**Red Hat® Ansible Certified Content for IBM Z** provides the ability to
connect IBM Z® to clients' wider enterprise automation strategy through the
Ansible Automation Platform ecosystem. This enables development and operations
automation on Z through a seamless, unified workflow orchestration with
configuration management, provisioning, and application deployment in one
easy-to-use platform.

IBM z/OS core collection, as part of the broader offering
**Red Hat® Ansible Certified Content for IBM Z**, will be available on both
Galaxy as a community supported offering and on Automation Hub with enterprise support.

Features
========

The IBM z/OS core collection includes `connection plugins`_,
`action plugins`_, `modules`_, `sample playbooks`_, `filters`_ and
ansible-doc to automate tasks on z/OS.

.. _connection plugins:
   https://github.com/ansible-collections/ibm_zos_core/tree/main/plugins/connection/
.. _action plugins:
   https://github.com/ansible-collections/ibm_zos_core/tree/main/plugins/action/
.. _modules:
    https://github.com/ansible-collections/ibm_zos_core/tree/main/plugins/modules/
.. _sample playbooks:
    https://github.com/ansible-collections/ibm_zos_core/tree/main/playbooks/
.. _filters:
   https://github.com/ansible-collections/ibm_zos_core/tree/main/plugins/filter/

.. toctree::
   :maxdepth: 1
   :caption: Installation & Execution
   :hidden:

   collection-requirements
   configuration

.. toctree::
   :maxdepth: 1
   :caption: Collections & content
   :hidden:

   release_notes
   life-cycle
   ansible_content

.. toctree::
   :maxdepth: 1
   :caption: Help & Troubleshooting
   :hidden:

   character_set

.. toctree::
   :maxdepth: 1
   :caption: Contribution
   :hidden:

   community_guides