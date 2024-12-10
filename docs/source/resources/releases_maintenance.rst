.. ...........................................................................
.. © Copyright IBM Corporation 2024                                          .
.. ...........................................................................

========================
Releases and maintenance
========================

This section describes the collections release dates, dependency versions and End of Life dates (EOL)
and support coverage.

The ``ibm_zos_core`` collection is developed and released on a flexible release cycle; generally, each quarter
a beta is released followed by a GA version. Occasionally, the cycle may be extended to properly implement and
test larger changes before a new release is made available.

End of Life for this collection is generally a 2-year cycle unless a dependency reaches EOL prior to the 2 years.
For example, if a collection has released and a dependency reaches EOL 1 year later, then the collection will EOL
at the same time as the dependency, 1 year later.

Life Cycle Phase
================

To encourage the adoption of new features while keeping the high standard of stability inherent,
support is divided into life cycle phases; **full support** which covers the first year
and **maintenance support** which covers the second year.

+--------------------------+------------------------------------+---------------------------+
| Life Cycle Phase         | Full Support                       | Maintenance Support       |
+==========================+====================================+===========================+
| Critical security fixes  | Yes                                | Yes                       |
+--------------------------+------------------------------------+---------------------------+
| Bug fixes by severity    | Critical and high severity issues  | Critical severity issues  |
+--------------------------+------------------------------------+---------------------------+

Severities
==========

Severity 1 (Critical):
A problem that severely impacts your use of the software in a production environment (such as loss
of production data or in which your production systems are not functioning). The situation halts
your business operations and no procedural workaround exists.

Severity 2 (high):
A problem where the software is functioning but your use in a production environment is severely
reduced. The situation is causing a high impact to portions of your business operations and no
procedural workaround exists.

Severity 3 (medium):
A problem that involves partial, non-critical loss of use of the software in a production environment
or development environment and your business continues to function, including by using a procedural
workaround.

Severity 4 (low):
A general usage question, reporting of a documentation error, or recommendation for a future product
enhancement or modification.

Severities 3 and 4 are generally addressed in subsequent releases to ensure a high standard of stability
remains available for production environments.

Support Matrix
==============

These are the component versions available when the collection was made generally available (GA). The underlying
component version is likely to change as it reaches EOL, thus components must be a version that is
currently supported.

For example, if a collection releases with a minimum version of ``ansible-core`` 2.14.0 (Ansible 7.0) and later this
enters into EOL, then a newer supported version of ``ansible-core`` (Ansible) must be selected. When choosing a newer
``ansible-core`` (Ansible) version, review the `ansible-core support matrix`_ to select the appropriate dependencies.
This is important to note, different releases of ``ansible-core`` can require newer control node and managed node
dependencies such as is the case with Python.

If the control node is Ansible Automation Platform (AAP), review the `Red Hat Ansible Automation Platform Life Cycle`_
to select a supported AAP version.

For IBM product lifecycle information, you can search for products using a product name, version or ID. For example,
to view IBM's `Open Enterprise SDK for Python lifecycle`_, search on product ID `5655-PYT`_, and for
`Z Open Automation Utilities lifecycle`_, search on product ID `5698-PA1`_.

The z/OS managed node includes several shells, currently the only supported shell is the z/OS Shell located in path
`/bin/sh`_. To configure which shell the ansible control node will use on the target machine, set inventory variable
**ansible_shell_executable**.

.. code-block:: sh

   ansible_shell_executable: /bin/sh


+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| Version | Controller                 | Managed Node                                      | GA            | End of Life   |
+=========+============================+===================================================+===============+===============+
| 1.12.x  |- `ansible-core`_ >=2.15.x  |- `z/OS`_ V2R5 - V3Rx                              | 6 Dec 2024    | 6 Dec 2026    |
|         |- `Ansible`_ >=8.0.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=2.4              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ >=1.3.2       |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.11.x  |- `ansible-core`_ >=2.15.x  |- `z/OS`_ V2R4 - V2Rx                              | 1 Oct 2024    | 1 Oct 2026    |
|         |- `Ansible`_ >=8.0.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=2.4              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ >=1.3.1       |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.10.x  |- `ansible-core`_ >=2.15.x  |- `z/OS`_ V2R4 - V2Rx                              | 21 June 2024  | 21 June 2026  |
|         |- `Ansible`_ >=8.0.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=2.4              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ >=1.3.0       |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.9.x   |- `ansible-core`_ >=2.14    |- `z/OS`_ V2R4 - V2Rx                              | 05 Feb 2024   | 30 April 2025 |
|         |- `Ansible`_ >=7.0.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=2.3              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ 1.2.5 - 1.2.x |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.8.x   |- `ansible-core`_ >=2.14    |- `z/OS`_ V2R4 - V2Rx                              | 13 Dec 2023   | 30 April 2025 |
|         |- `Ansible`_ >=7.0.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=2.3              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ 1.2.4 - 1.2.x |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.7.x   |- `ansible-core`_ >=2.14    |- `z/OS`_ V2R4 - V2Rx                              | 10 Oct 2023   | 30 April 2025 |
|         |- `Ansible`_ >=7.0.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=2.3              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ 1.2.3 - 1.2.x |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.6.x   |- `ansible-core`_ >=2.9.x   |- `z/OS`_ V2R3 - V2Rx                              | 28 June 2023  | 30 April 2025 |
|         |- `Ansible`_ >=2.9.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=1.2              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ 1.2.2 - 1.2.x |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+
| 1.5.x   |- `ansible-core`_ >=2.9.x   |- `z/OS`_ V2R3 - V2Rx                              | 25 April 2023 | 25 April 2025 |
|         |- `Ansible`_ >=2.9.x        |- `z/OS shell`_                                    |               |               |
|         |- `AAP`_ >=1.2              |- IBM `Open Enterprise SDK for Python`_            |               |               |
|         |                            |- IBM `Z Open Automation Utilities`_ 1.2.2 - 1.2.x |               |               |
+---------+----------------------------+---------------------------------------------------+---------------+---------------+

.. .............................................................................
.. Global Links
.. .............................................................................
.. _ansible-core support matrix:
   https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix
.. _AAP:
   https://access.redhat.com/support/policy/updates/ansible-automation-platform
.. _Red Hat Ansible Automation Platform Life Cycle:
   https://access.redhat.com/support/policy/updates/ansible-automation-platform
.. _Automation Hub:
   https://www.ansible.com/products/automation-hub
.. _Open Enterprise SDK for Python:
   https://www.ibm.com/products/open-enterprise-python-zos
.. _Z Open Automation Utilities:
   https://www.ibm.com/docs/en/zoau/latest
.. _z/OS shell:
   https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm
.. _z/OS:
   https://www.ibm.com/docs/en/zos
.. _Open Enterprise SDK for Python lifecycle:
   https://www.ibm.com/support/pages/lifecycle/search?q=5655-PYT
.. _5655-PYT:
   https://www.ibm.com/support/pages/lifecycle/search?q=5655-PYT
.. _Z Open Automation Utilities lifecycle:
   https://www.ibm.com/support/pages/lifecycle/search?q=5698-PA1
.. _5698-PA1:
   https://www.ibm.com/support/pages/lifecycle/search?q=5698-PA1
.. _ansible-core:
   https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix
.. _Ansible:
   https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix
.. _/bin/sh:
   https://www.ibm.com/docs/en/zos/3.1.0?topic=descriptions-sh-invoke-shell
