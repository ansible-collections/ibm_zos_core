IBM z/OS core collection
========================

The **IBM® z/OS® core collection**, also represented as
**ibm_zos_core** in this document, is  part of the broader
initiative to bring Ansible Automation to IBM Z® through the offering
**Red Hat® Ansible Certified Content for IBM Z®**. The
**IBM z/OS core collection** supports automation tasks such as
creating data sets, submitting jobs, querying jobs, retrieving job output,
encoding data, fetching data sets, copying data sets,
executing operator commands, executing TSO commands, ping,
querying operator actions, APF authorizing libraries,
editing textual data in data sets or Unix System Services files,
finding data sets, backing up and restoring data sets and
volumes, mounting file systems, running z/OS programs without JCL,
running local and remote scripts on z/OS, initializing volumes,
archiving, unarchiving and templating with Jinja.


Red Hat Ansible Certified Content for IBM Z
===========================================

**Red Hat® Ansible Certified Content for IBM Z** provides the ability to
connect IBM Z® to clients' wider enterprise automation strategy through the
Ansible Automation Platform ecosystem. This enables development and operations
automation on Z through a seamless, unified workflow orchestration with
configuration management, provisioning, and application deployment in
one easy-to-use platform.

The **IBM z/OS core collection** is following the
**Red Hat® Ansible Certified Content for IBM Z®** method of distributing
content. Collections will be developed in the open, and when content is ready
for use, it is released to
[Ansible Galaxy](https://galaxy.ansible.com/ui/)
for community adoption. Once contributors review community usage, feedback,
and are satisfied with the content published, the collection will then be
released to [Ansible Automation Hub](https://www.ansible.com/products/automation-hub)
as **certified** and **IBM supported** for
**Red Hat® Ansible Automation Platform subscribers**.

For guides and reference, please review the [documentation](https://ibm.github.io/z_ansible_collections_doc/index.html).

Features
========
The **IBM z/OS core collection**, includes
[connection plugins](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/plugins.html#connection),
[action plugins](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/plugins.html#action),
[modules](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/modules.html),
[filters](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/filters.html),
and ansible-doc to automate tasks on z/OS.

Ansible version compatibility
=============================
This collection has been tested against **Ansible Core** versions >=2.15.
The Ansible Core versions supported for this collection align to the
[ansible-core support matrix](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix). Review the
[Ansible community changelogs](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-community-changelogs) for corresponding **Ansible community packages**
and **ansible-core**.

For **Ansible Automation Platform** (AAP) users, review the
[Ansible Automation Platform Certified Content](https://access.redhat.com/support/articles/ansible-automation-platform-certified-content)
and [AAP Life Cycle](https://access.redhat.com/support/policy/updates/ansible-automation-platform)
for more more information on supported versions of Ansible.

Other Dependencies
==================
This release of the **IBM z/OS core collection** requires the z/OS managed node have the following:
- [z/OS](https://www.ibm.com/docs/en/zos)
- [z/OS shell](https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm).
- [IBM Open Enterprise SDK for Python](https://www.ibm.com/products/open-enterprise-python-zos)
- [IBM Z Open Automation Utilities](https://www.ibm.com/docs/en/zoau/1.2.x)
For specific dependency versions, please review the [release notes](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html) for the version of the IBM Ansible z/OS core installed.

Copyright
=========
© Copyright IBM Corporation 2020-2024.

License
=======
Some portions of this collection are licensed under [GNU General Public
License, Version 3.0](https://opensource.org/licenses/GPL-3.0), and
other portions of this collection are licensed under [Apache License,
Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

See individual files for applicable licenses.