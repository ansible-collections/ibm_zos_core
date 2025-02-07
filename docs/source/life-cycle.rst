.. ...........................................................................
.. © Copyright IBM Corporation 2025                                          .
.. File needs to be contributed by a collection, likely the ref's won't work
.. since the source will be in another, so need to create an external link.
.. ...........................................................................

==========
Life cycle
==========

The IBM z/OS® core (``ibm_zos_core``) collection is developed and released on
a flexible release cycle; generally, each quarter a beta is released followed
by a GA version. Occasionally, the cycle may be extended to properly implement
and test larger changes before a new release is made available.

**End of Life** (EOL) for this collection is generally a 2-year cycle unless a
dependency reaches EOL prior to the 2 years. For example, if a collection has
released and its dependency reaches EOL 1 year later, then the collection will
EOL at the same time as the dependency, 1 year later.

Product life cycle
==================

Review this matrix for the status of the IBM z/OS core collection version,
its critical dates, and which type of support it's currently eligible for.

+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| Version    | Status         | Changelogs            | GA Date          | EOL Date          | Life Cycle Phase                                          |
+============+================+=======================+==================+===================+===========================================================+
| 1.14.x     | In Development | N/A                   | TBD              | TBD               | N/A                                                       |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.13.x     | Current        | `1.13.x changelogs`_  | TBD              | TBD               | N/A                                                       |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.12.x     | Released       | `1.12.x changelogs`_  | 06 December 2024 | 06 December 2024  | :ref:`Full support<Ansible Z life cycles - phase>`        |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.11.x     | Released       | `1.11.x changelogs`_  | 01 October 2024  | 01 October 2026   | :ref:`Full support<Ansible Z life cycles - phase>`        |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.10.x     | Released       | `1.10.x changelogs`_  | 21 June 2024     | 21 June 2026      | :ref:`Full support<Ansible Z life cycles - phase>`        |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.9.x      | Released       | `1.9.x changelogs`_   | 05 Feb 2024      | 30 April 2025     | :ref:`Full support<Ansible Z life cycles - phase>`        |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.8.x      | Released       | `1.8.x changelogs`_   | 13 Dec 2023      | 30 April 2025     | :ref:`Maintenance support<Ansible Z life cycles - phase>` |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.7.x      | Released       | `1.7.x changelogs`_   | 10 Oct 2023      | 30 April 2025     | :ref:`Maintenance support<Ansible Z life cycles - phase>` |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.6.x      | Released       | `1.6.x changelogs`_   | 28 June 2023     | 30 April 2025     | :ref:`Maintenance support<Ansible Z life cycles - phase>` |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+
| 1.5.x      | Released       | `1.5.x changelogs`_   | 25 April 2023    | 30 April 2025     | :ref:`Maintenance support<Ansible Z life cycles - phase>` |
+------------+----------------+-----------------------+------------------+-------------------+-----------------------------------------------------------+

.. .............................................................................
.. Global Links
.. .............................................................................
.. _1.13.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.13.0/CHANGELOG.rst
.. _1.12.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.12.0/CHANGELOG.rst
.. _1.11.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.11.0/CHANGELOG.rst
.. _1.10.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.10.0/CHANGELOG.rst
.. _1.9.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.9.0/CHANGELOG.rst
.. _1.8.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.8.0/CHANGELOG.rst
.. _1.7.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.7.0/CHANGELOG.rst
.. _1.6.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.6.0/CHANGELOG.rst
.. _1.5.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.5.0/CHANGELOG.rst