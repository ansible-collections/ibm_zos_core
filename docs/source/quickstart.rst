.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Quickstart
==========

After you have installed the collection outlined in the  `installation`_
guide, you will want to access the collection and ansible-doc covered in the
following topics.

.. _installation:
   installation.html

ibm_zos_core
------------

After the collection is installed, you can access collection content for a
playbook by referencing the namespace ``ibm`` and collection's fully qualified
name ``ibm_zos_core``, for example:

.. code-block:: yaml

    - hosts: all

    tasks:
    - name: Query submitted job 'HELLO'
        ibm.ibm_zos_core.zos_job_query:
        job_name: HELLO


In Ansible 2.9, the ``collections`` keyword was added and reduces the need
to refer to the collection repeatedly. For example, you can use the
``collections`` keyword in your playbook:

.. code-block:: yaml

    - hosts: all
      collections:
      - ibm.ibm_zos_core

      tasks:
      - name: Query submitted job 'HELLO'
        zos_job_query:
            job_name: HELLO


z/OS Connection Plugin
----------------------

Since EBCDIC encoding is used on z/OS, custom plugins are needed to determine
the correct transport method when targeting a z/OS system.

The zos_ssh.py connection plugin is a fork of the default ssh.py plugin with
added functionality for checking if a module is written in REXX.

Since REXX scripts need to be in EBCDIC encoding to run, they need to be
handled differently during transfer. If the string
``__ANSIBLE_ENCODE_EBCDIC__`` is found on the first line of the module, the
module is transferred to the target system using SCP. Otherwise, SFTP is used.
SCP treats files as text, automatically encoding as EBCDIC at transfer time.
SFTP treats files as binary, performing no encoding changes.

**REXX Module Configuration**:

* Ensure a REXX modules first line is a comment containing the case insensitive keyword ``rexx``
* Followed by the case sensitive value ``__ANSIBLE_ENCODE_EBCDIC__``


**Example REXX module**:

.. code-block:: sh

   /* rexx  __ANSIBLE_ENCODE_EBCDIC__  */
   x = 55
   SAY '{"SYSTEM_VERSION":"' x '"}'
   RETURN 0


ansible-doc
-----------

Modules included in this collection provide additional documentation that is
similar to a UNIX, or UNIX-like operating system man page (manual page). This
documentation can be accessed from the command line by using the
``ansible-doc`` command.

Here's how to use the ``ansible-doc`` command after you have installed the
**IBM z/OS core collection**: ``ansible-doc ibm.ibm_zos_core.zos_data_set``

.. code-block:: sh

    > ZOS_DATA_SET    (/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core/plugins/modules/zos_data_set.py)

            Create, delete and set attributes of data sets. When forcing data set replacement, contents will not be
            preserved.

    * This module is maintained by The Ansible Community
    OPTIONS (= is mandatory):

    - batch
            Batch can be used to perform operations on multiple data sets in a single module call.
            Each item in the list expects the same options as zos_data_set.
            [Default: (null)]
            type: list
            version_added: 2.9

    - data_class
            The data class name (required for SMS-managed data sets)
            [Default: (null)]
            type: str
            version_added: 2.9

For more information on using the ``ansible-doc`` command, refer
to `Ansible guide`_.

.. _Ansible guide:
   https://docs.ansible.com/ansible/latest/cli/ansible-doc.html#ansible-doc



