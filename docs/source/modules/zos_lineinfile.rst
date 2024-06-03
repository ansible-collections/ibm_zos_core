
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_lineinfile.py

.. _zos_lineinfile_module:


zos_lineinfile -- Manage textual data on z/OS
=============================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manage lines in z/OS UNIX System Services (USS) files, PS (sequential data set), PDS, PDSE, or member of a PDS or PDSE.
- This module ensures a particular line is in a USS file or data set, or replace an existing line using a back-referenced regular expression.
- This is primarily useful when you want to change a single line in a USS file or data set only.





Parameters
----------


src
  The location can be a UNIX System Services (USS) file, PS (sequential data set), member of a PDS or PDSE, PDS, PDSE.

  The USS file must be an absolute pathname.

  | **required**: True
  | **type**: str


regexp
  The regular expression to look for in every line of the USS file or data set.

  For \ :literal:`state=present`\ , the pattern to replace if found. Only the last line found will be replaced.

  For \ :literal:`state=absent`\ , the pattern of the line(s) to remove.

  If the regular expression is not matched, the line will be added to the USS file or data set in keeping with \ :literal:`insertbefore`\  or \ :literal:`insertafter`\  settings.

  When modifying a line the regexp should typically match both the initial state of the line as well as its state after replacement by \ :literal:`line`\  to ensure idempotence.

  | **required**: False
  | **type**: str


state
  Whether the line should be inserted/replaced(present) or removed(absent).

  | **required**: False
  | **type**: str
  | **default**: present
  | **choices**: absent, present


line
  The line to insert/replace into the USS file or data set.

  Required for \ :literal:`state=present`\ .

  If \ :literal:`backrefs`\  is set, may contain backreferences that will get expanded with the \ :literal:`regexp`\  capture groups if the regexp matches.

  | **required**: False
  | **type**: str


backrefs
  Used with \ :literal:`state=present`\ .

  If set, \ :literal:`line`\  can contain backreferences (both positional and named) that will get populated if the \ :literal:`regexp`\  matches.

  This parameter changes the operation of the module slightly; \ :literal:`insertbefore`\  and \ :literal:`insertafter`\  will be ignored, and if the \ :literal:`regexp`\  does not match anywhere in the USS file or data set, the USS file or data set will be left unchanged.

  If the \ :literal:`regexp`\  does match, the last matching line will be replaced by the expanded line parameter.

  | **required**: False
  | **type**: bool
  | **default**: False


insertafter
  Used with \ :literal:`state=present`\ .

  If specified, the line will be inserted after the last match of specified regular expression.

  If the first match is required, use(firstmatch=yes).

  A special value is available; \ :literal:`EOF`\  for inserting the line at the end of the USS file or data set.

  If the specified regular expression has no matches, EOF will be used instead.

  If \ :literal:`insertbefore`\  is set, default value \ :literal:`EOF`\  will be ignored.

  If regular expressions are passed to both \ :literal:`regexp`\  and \ :literal:`insertafter`\ , \ :literal:`insertafter`\  is only honored if no match for \ :literal:`regexp`\  is found.

  May not be used with \ :literal:`backrefs`\  or \ :literal:`insertbefore`\ .

  Choices are EOF or '\*regex\*'

  Default is EOF

  | **required**: False
  | **type**: str


insertbefore
  Used with \ :literal:`state=present`\ .

  If specified, the line will be inserted before the last match of specified regular expression.

  If the first match is required, use \ :literal:`firstmatch=yes`\ .

  A value is available; \ :literal:`BOF`\  for inserting the line at the beginning of the USS file or data set.

  If the specified regular expression has no matches, the line will be inserted at the end of the USS file or data set.

  If regular expressions are passed to both \ :literal:`regexp`\  and \ :literal:`insertbefore`\ , \ :literal:`insertbefore`\  is only honored if no match for \ :literal:`regexp`\  is found.

  May not be used with \ :literal:`backrefs`\  or \ :literal:`insertafter`\ .

  Choices are BOF or '\*regex\*'

  | **required**: False
  | **type**: str


backup
  Creates a backup file or backup data set for \ :emphasis:`src`\ , including the timestamp information to ensure that you retrieve the original file.

  \ :emphasis:`backup\_name`\  can be used to specify a backup file name if \ :emphasis:`backup=true`\ .

  The backup file name will be return on either success or failure of module execution such that data can be retrieved.

  | **required**: False
  | **type**: bool
  | **default**: False


backup_name
  Specify the USS file name or data set name for the destination backup.

  If the source \ :emphasis:`src`\  is a USS file or path, the backup\_name must be a file or path name, and the USS file or path must be an absolute path name.

  If the source is an MVS data set, the backup\_name must be an MVS data set name.

  If the backup\_name is not provided, the default backup\_name will be used. If the source is a USS file or path, the name of the backup file will be the source file or path name appended with a timestamp, e.g. \ :literal:`/path/file\_name.2020-04-23-08-32-29-bak.tar`\ .

  If the source is an MVS data set, it will be a data set with a random name generated by calling the ZOAU API. The MVS backup data set recovery can be done by renaming it.

  | **required**: False
  | **type**: str


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary and backup datasets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the value \ :literal:`TMPHLQ`\  is used.

  | **required**: False
  | **type**: str


firstmatch
  Used with \ :literal:`insertafter`\  or \ :literal:`insertbefore`\ .

  If set, \ :literal:`insertafter`\  and \ :literal:`insertbefore`\  will work with the first line that matches the given regular expression.

  | **required**: False
  | **type**: bool
  | **default**: False


encoding
  The character set of the source \ :emphasis:`src`\ . \ `zos\_lineinfile <./zos_lineinfile.html>`__\  requires to be provided with correct encoding to read the content of USS file or data set. If this parameter is not provided, this module assumes that USS file or data set is encoded in IBM-1047.

  Supported character sets rely on the charset conversion utility (iconv) version; the most common character sets are supported.

  | **required**: False
  | **type**: str
  | **default**: IBM-1047


force
  Specifies that the data set can be shared with others during an update which results in the data set you are updating to be simultaneously updated by others.

  This is helpful when a data set is being used in a long running process such as a started task and you are wanting to update or read.

  The \ :literal:`force`\  option enables sharing of data sets through the disposition \ :emphasis:`DISP=SHR`\ .

  | **required**: False
  | **type**: bool
  | **default**: False




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Ensure value of a variable in the sequential data set
     zos_lineinfile:
       src: SOME.DATA.SET
       regexp: '^VAR='
       line: VAR="some value"

   - name: Remove all comments in the USS file
     zos_lineinfile:
       src: /tmp/src/somefile
       state: absent
       regexp: '^#'

   - name: Ensure the https port is 8080
     zos_lineinfile:
       src: /tmp/src/somefile
       regexp: '^Listen '
       insertafter: '^#Listen '
       line: Listen 8080

   - name: Ensure we have our own comment added to the partitioned data set member
     zos_lineinfile:
       src: SOME.PARTITIONED.DATA.SET(DATA)
       regexp: '#^VAR='
       insertbefore: '^VAR='
       line: '# VAR default value'

   - name: Ensure the user working directory for liberty is set as needed
     zos_lineinfile:
       src: /tmp/src/somefile
       regexp: '^(.*)User(\d+)m(.*)$'
       line: '\1APPUser\3'
       backrefs: true

   - name: Add a line to a member while a task is in execution
     zos_lineinfile:
       src: SOME.PARTITIONED.DATA.SET(DATA)
       insertafter: EOF
       line: 'Should be a working test now'
       force: true




Notes
-----

.. note::
   It is the playbook author or user's responsibility to avoid files that should not be encoded, such as binary files. A user is described as the remote user, configured either for the playbook or playbook tasks, who can also obtain escalated privileges to execute as root or another user.

   All data sets are always assumed to be cataloged. If an uncataloged data set needs to be encoded, it should be cataloged first.

   For supported character sets used to encode data, refer to the \ `documentation <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html>`__\ .







Return Values
-------------


changed
  Indicates if the source was modified. Value of 1 represents \`true\`, otherwise \`false\`.

  | **returned**: success
  | **type**: bool
  | **sample**:

    .. code-block:: json

        1

found
  Number of the matching patterns

  | **returned**: success
  | **type**: int
  | **sample**: 5

cmd
  constructed dsed shell cmd based on the parameters

  | **returned**: success
  | **type**: str
  | **sample**: dsedhelper -d -en IBM-1047 /^PATH=/a\\PATH=/dir/bin:$PATH/$ /etc/profile

msg
  The module messages

  | **returned**: failure
  | **type**: str
  | **sample**: Parameter verification failed

return_content
  The error messages from ZOAU dsed

  | **returned**: failure
  | **type**: str
  | **sample**: BGYSC1311E Iconv error, cannot open converter from ISO-88955-1 to IBM-1047

backup_name
  Name of the backup file or data set that was created.

  | **returned**: if backup=true
  | **type**: str
  | **sample**: /path/to/file.txt.2015-02-03@04:15~

