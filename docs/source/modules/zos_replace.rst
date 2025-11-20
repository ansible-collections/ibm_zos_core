
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_replace.py

.. _zos_replace_module:


zos_replace -- Replace all instances of a pattern within a file or data set.
============================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The module `zos_replace. </zos_replace.html>`_ can replace all instances of a pattern in the contents of a data set.





Parameters
----------


after
  A regular expression that, if specified, determines which content will be replaced or removed **after** the match.

  Option *after* is the start position from where the module will seek to match the *regexp* pattern. When a pattern is matched, occurrences are substituted with the value set for *replace*.

  If option *after* is not set, the module will search from the beginning of the *target*.

  Option *after* is a regular expression as described in the `Python library <https://docs.python.org/3/library/re.html>`_.

  Option *after* can be used in combination with *before*. When combined with *before*, patterns are replaced or removed from *after* until the value set for *before*.

  Option *after* can be interpreted as a literal string instead of a regular expression by setting option *literal=after*.

  | **required**: False
  | **type**: str


backup
  Specifies whether a backup of the destination should be created before editing the source *target*.

  When set to ``true``, the module creates a backup file or data set.

  The backup file name will be returned if *backup* is ``true`` on either success or failure of module execution such that data can be retrieved.

  | **required**: False
  | **type**: bool
  | **default**: False


backup_name
  Specify the USS file name or data set name for the destination backup.

  If *src* is a USS file or path, backup_name must be a file or path name, and it must be an absolute path name.

  If the source is an MVS data set, *backup_name* must be an MVS data set name, and the data set must **not** be preallocated.

  If it is a Generation Data Set (GDS), use a relative positive name, e.g., *SOME.CREATION(+1*).

  If *backup_name* is not provided, a default name will be used. If the source is a USS file or path, the name of the backup file will be the source file or path name appended with a timestamp, e.g. ``/path/file_name.2020-04-23-08-32-29-bak.tar``.

  If *src* is a seq data set and backup_name is not provided, the data set will be backed up to seq data set with a randomly generated name.

  If *src* is a data set member and backup_name is not provided, the data set member will be backed up to the same partitioned data set with a randomly generated member name.

  If *src* is a Generation Data Set (GDS) and backup_name is not provided, backup will be a sequential data set.

  | **required**: False
  | **type**: str


before
  A regular expression that if, specified, determines which content will be replaced or removed **before** the match.

  Option *before* is the end position from where the module will seek to match the *regexp* pattern. When a pattern is matched, occurrences are substituted with the value set for *replace*.

  If option *before* is not set, the module will search to the end of the *target*.

  Option *before* is a regular expression as described in the `Python library <https://docs.python.org/3/library/re.html>`_.

  Option *before* can be used in combination with *after*. When combined with *after*, patterns are replaced or removed from *after* until the value set for *before*.

  Option *before* can be interpreted as a literal string instead of a regular expression by setting option *literal=before*.

  | **required**: False
  | **type**: str


encoding
  The character set for data in the *target*. Module `zos_replace <./zos_replace.html>`_ requires the encoding to correctly read the content of a USS file or data set. If this parameter is not provided, this module assumes that USS file or data set is encoded in IBM-1047.

  Supported character sets rely on the charset conversion utility (iconv) version; the most common character sets are supported.

  | **required**: False
  | **type**: str
  | **default**: IBM-1047


literal
  If specified, it enables the module to interpret options *after*, *before* and *regexp* as a literal rather than a regular expression.

  Option *literal* uses any combination of V(after), V(before) and V(regexp).

  To interpret one option as a literal, use *literal=regexp*, *literal=after* or *literal=before*.

  To interpret multiple options as a literal, use a list such as ``['after', 'before']`` or ``['regex', 'after', 'before']``

  | **required**: False
  | **type**: raw
  | **default**: []


target
  The location can be a UNIX System Services (USS) file, PS (sequential data set), PDS, PDSE, member of a PDS or PDSE.

  The USS file must be an absolute pathname.

  It is possible to use a generation data set (GDS) relative name of generation already created. e.g. *SOME.CREATION(-1*).

  | **required**: True
  | **type**: str


tmp_hlq
  Override the default High Level Qualifier (HLQ) for temporary and backup data sets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the value of ``TMPHLQ`` is used.

  | **required**: False
  | **type**: str


regexp
  The regular expression to look for in the contents of the file.

  | **required**: True
  | **type**: str


replace
  The string to replace *regexp* matches with.

  If not set, matches are removed entirely.

  | **required**: False
  | **type**: str






Examples
--------

.. code-block:: yaml+jinja

   
   - name: Replace 'profile/' pattern in USS file via blank substitution.
     zos_replace:
       target: /tmp/src/somefile
       regexp: 'profile\/'

   - name: Replace regexp match with blank after line match in USS file.
     zos_replace:
       target: "/tmp/source"
       regexp: '^MOUNTPOINT*'
       after: export ZOAU_ROOT

   - name: Replace a specific line with special character on a dataset after a line, treating the text specified
       for regexp as a literal string and after as regular expression.
     zos_replace:
       target: SAMPLE.SOURCE
       regexp: //*LIB  DD UNIT=SYS,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv
       replace: //*LIB  DD UNIT=SYS,SPACE=(CYL,(1,1))
       after: '^\$source base \([^\s]+\)'
       literal: regexp

   - name: Replace a specific line with special character on a dataset after a line, treating the text specified
       for regexp and after as regular expression.
     zos_replace:
       target: SAMPLE.SOURCE
       regexp: '\ \*\*LIB\ \ DD\ UNIT=SYS,SPACE=\(TRK,\(1,1\)\),VOL=SER=vvvvvv'
       replace: //*LIB  DD UNIT=SYS,SPACE=(CYL,(1,1))
       after: '^\$source base \([^\s]+\)'
       literal: regexp

   - name: Replace a specific line before a specific sentence with backup, treating the text specified for regexp and before as literal strings.
     zos_replace:
       target: SAMPLE.SOURCE
       backup: true
       regexp: //SYSPRINT DD SYSOUT=*
       before: SAMPLES OUTPUT SYSIN *=$DSN
       literal:
         - regexp
         - before

   - name: Replace a specific line before a specific sentence with backup, treating the text specified for regexp and before as regular expression.
     zos_replace:
       target: SAMPLE.SOURCE
       backup: true
       regexp: '\ //SYSPRINT\ DD\ SYSOUT=\*'
       before: '\ SAMPLES OUTPUT SYSIN\ \*\=\$DSN'

   - name: Replace 'var' with 'vars' between matched lines after and before with backup.
     zos_replace:
       target: SAMPLE.DATASET
       tmp_hlq: ANSIBLE
       backup: true
       backup_name: BACKUP.DATASET
       regexp: var
       replace: vars
       after: ^/tmp/source*
       before: ^   if*

   - name: Replace lines on a GDS and generate a backup on the same GDG.
     zos_replace:
       target: SOURCE.GDG(0)
       regexp: ^(IEE132I|IEA989I|IEA888I|IEF196I|IEA000I)\s.*
       after: ^IEE133I PENDING *
       before: ^IEE252I DEVICE *
       backup: true
       backup_name: "SOURCE.GDG(+1)"

   - name: Delete 'SYSTEM' calls via backref between matched lines in a PDS member.
     zos_replace:
       target: PDS.SOURCE(MEM)
       regexp: '^(.*?SYSTEM.*?)SYSTEM(.*)'
       replace: '\1\2'
       after: IEE133I PENDING *
       before: IEF456I JOB12345 *




Notes
-----

.. note::
   For supported character sets used to encode data, refer to the `documentation <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html>`_.







Return Values
-------------


backup_name
  Name of the backup file or data set that was created.

  | **returned**: if backup=true
  | **type**: str
  | **sample**: /path/to/file.txt.2015-02-03@04:15

changed
  Indicates if the source was modified.

  | **returned**: always
  | **type**: bool
  | **sample**:

    .. code-block:: json

        true

found
  Number of matches found

  | **returned**: success
  | **type**: int
  | **sample**: 5

msg
  A string with a generic or error message relayed to the user.

  | **returned**: failure
  | **type**: str
  | **sample**: Parameter verification failed

replaced
  Fragment of the file that was changed

  | **returned**: always
  | **type**: str
  | **sample**: IEE134I TRACE DISABLED - MONITORING STOPPED

target
  The data set name or USS path that was modified.

  | **returned**: always
  | **type**: str
  | **sample**: ANSIBLE.USER.TEXT

