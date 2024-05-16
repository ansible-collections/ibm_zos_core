========================
Releases and maintenance
========================

This table describes the collections release dates, dependency versions and End of Life dates (EOL).

The ``ibm_zos_core`` collection is developed and released on a flexible release cycle; generally, each quarter
a beta is released followed by a GA version. Occasionally, the cycle may be extended to properly implement and
test larger changes before a new release is made available.

These are the component versions available when the collection was made generally available. The underlying
component version is likely to change as it reaches EOL, thus components must be a version that is
currently supported.

For example, if a collection releases with a minimum version of ``ansible-core`` of 2.11.0, and later this
enters into EOL, then a newer and supported version of ansible-core must be used.

End of Life (EOL) for this collection is generally a 2-year cycle unless a dependency reaches EOL prior to the 2 years.
For example, if a collection releases and its dependency reaches EOL 1 year later, then the collection will EOL at the
same time as the dependency, 1 year later.

Support Matrix
==============
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+
| Version | GA Release    | ansible-core | Ansible | AAP   | End of Life   | Control Node       | Managed Node                                                               |
+=========+===============+==============+=========+=======+===============+====================+============================================================================+
| 1.10.x  | In preview    | >=2.15.x     | >=8.0.x | >=2.4 | TBD           | Python 3.10 - 3.11 | - z/OS V2R4 - V2R5                                                         |
|         |               |              |         |       |               |                    | - z/OS shell                                                               |
|         |               |              |         |       |               |                    | - IBM Open Enterprise SDK for Python 3.10 - 3.11                           |
|         |               |              |         |       |               |                    | - IBM Z Open Automation Utilities 1.3.0 or later                           |
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+
| 1.9.x   | 05 Feb 2024   | >=2.14.x     | >=7.0.x | >=2.3 | 30 April 2025 | Python 3.10 - 3.11 |- z/OS V2R4 - V2R5                                                          |
|         |               |              |         |       |               |                    |- z/OS shell                                                                |
|         |               |              |         |       |               |                    |- IBM Open Enterprise SDK for Python 3.10 - 3.11                            |
|         |               |              |         |       |               |                    |- IBM Z Open Automation Utilities 1.2.5 or later, but prior to version 1.3.0|
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+
| 1.8.x   | 13 Dec 2023   | >=2.14.x     | >=7.0.x | >=2.3 | 30 April 2025 | Python 3.10 - 3.11 |- z/OS V2R4 - V2R5                                                          |
|         |               |              |         |       |               |                    |- z/OS shell                                                                |
|         |               |              |         |       |               |                    |- IBM Open Enterprise SDK for Python 3.10 - 3.11                            |
|         |               |              |         |       |               |                    |- IBM Z Open Automation Utilities 1.2.4 or later, but prior to version 1.3.0|
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+
| 1.7.x   | 10 Oct 2023   | >=2.14.x     | >=7.0.x | >=2.3 | 30 April 2025 | Python 3.10 - 3.11 |- z/OS V2R4 - V2R5                                                          |
|         |               |              |         |       |               |                    |- z/OS shell                                                                |
|         |               |              |         |       |               |                    |- IBM Open Enterprise SDK for Python 3.10 - 3.11                            |
|         |               |              |         |       |               |                    |- IBM Z Open Automation Utilities 1.2.3 or later, but prior to version 1.3.0|
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+
| 1.6.x   | 28 June 2023  | >=2.14.x     | >=7.0.x | >=2.3 | 30 April 2025 | Python 3.10 - 3.11 |- z/OS V2R4 - V2R5                                                          |
|         |               |              |         |       |               |                    |- z/OS shell                                                                |
|         |               |              |         |       |               |                    |- IBM Open Enterprise SDK for Python 3.10 - 3.11                            |
|         |               |              |         |       |               |                    |- IBM Z Open Automation Utilities 1.2.2 or later, but prior to version 1.3.0|
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+
| 1.5.x   | 25 April 2023 | >=2.14.x     | >=7.0.x | >=2.3 | 25 April 2025 | Python 3.10 - 3.11 |- z/OS V2R4 - V2R5                                                          |
|         |               |              |         |       |               |                    |- z/OS shell                                                                |
|         |               |              |         |       |               |                    |- IBM Open Enterprise SDK for Python 3.10 - 3.11                            |
|         |               |              |         |       |               |                    |- IBM Z Open Automation Utilities 1.2.4 or later, but prior to version 1.3.0|
+---------+---------------+--------------+---------+-------+---------------+--------------------+----------------------------------------------------------------------------+