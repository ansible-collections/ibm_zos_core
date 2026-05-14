.. ...........................................................................
.. © Copyright IBM Corporation 2025, 2026                                    .
.. File needs to be contributed by a collection, likely the ref's won't work .
.. since the source will be in another, so need to create an external link.  .
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

+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| Version    | Status         | Changelogs            | GA Date          | EOL Date          | Life Cycle Phase        |
+============+================+=======================+==================+===================+=========================+
| 1.16.x     | Released       | `1.16.x changelogs`_  | February 2026    | February 2028     | `Full support`_         |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| 1.15.x     | Released       | `1.15.x changelogs`_  | September 2025   | September 2027    | `Full support`_         |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| 1.14.x     | Released       | `1.14.x changelogs`_  | June 2025        | June 2027         | `Full support`_         |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| 1.13.x     | Released       | `1.13.x changelogs`_  | March 2025       | March 2027        | `Full support`_         |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| 1.12.x     | Released       | `1.12.x changelogs`_  | December 2024    | December 2026     | `Maintenance support`_  |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| 1.11.x     | Released       | `1.11.x changelogs`_  | October 2024     | October 2026      | `Maintenance support`_  |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+
| 1.10.x     | Released       | `1.10.x changelogs`_  | June 2024        | June 2026         | `Maintenance support`_  |
+------------+----------------+-----------------------+------------------+-------------------+-------------------------+

.. .............................................................................
.. Global Links
.. .............................................................................
.. _1.16.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.16.0/CHANGELOG.rst
.. _1.15.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.15.0/CHANGELOG.rst
.. _1.14.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.14.0/CHANGELOG.rst
.. _1.13.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.13.0/CHANGELOG.rst
.. _1.12.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.12.1/CHANGELOG.rst
.. _1.11.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.11.1/CHANGELOG.rst
.. _1.10.x changelogs:
    https://github.com/ansible-collections/ibm_zos_core/blob/v1.10.0/CHANGELOG.rst
.. _Full support:
    ../../../collections_content/collection-life-cycles.html#life-cycle-phase
.. _Maintenance support:
    ../../../collections_content/collection-life-cycles.html#life-cycle-phase
.. _End of Life:
    ../../../collections_content/collection-life-cycles.html#life-cycle-phase