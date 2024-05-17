
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_copy.py

.. _zos_copy_module:


zos_copy -- Copy data to z/OS
=============================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The \ `zos\_copy <./zos_copy.html>`__\  module copies a file or data set from a local or a remote machine to a location on the remote machine.





Parameters
----------


asa_text
  If set to \ :literal:`true`\ , indicates that either \ :literal:`src`\  or \ :literal:`dest`\  or both contain ASA control characters.

  When \ :literal:`src`\  is a USS file and \ :literal:`dest`\  is a data set, the copy will preserve ASA control characters in the destination.

  When \ :literal:`src`\  is a data set containing ASA control characters and \ :literal:`dest`\  is a USS file, the copy will put all control characters as plain text in the destination.

  If \ :literal:`dest`\  is a non-existent data set, it will be created with record format Fixed Block with ANSI format (FBA).

  If neither \ :literal:`src`\  or \ :literal:`dest`\  have record format Fixed Block with ANSI format (FBA) or Variable Block with ANSI format (VBA), the module will fail.

  This option is only valid for text files. If \ :literal:`is\_binary`\  is \ :literal:`true`\  or \ :literal:`executable`\  is \ :literal:`true`\  as well, the module will fail.

  | **required**: False
  | **type**: bool
  | **default**: False


backup
  Specifies whether a backup of the destination should be created before copying data.

  When set to \ :literal:`true`\ , the module creates a backup file or data set.

  The backup file name will be returned on either success or failure of module execution such that data can be retrieved.

  | **required**: False
  | **type**: bool
  | **default**: False


backup_name
  Specify a unique USS file name or data set name for the destination backup.

  If the destination \ :literal:`dest`\  is a USS file or path, the \ :literal:`backup\_name`\  must be an absolute path name.

  If the destination is an MVS data set name, the \ :literal:`backup\_name`\  provided must meet data set naming conventions of one or more qualifiers, each from one to eight characters long, that are delimited by periods.

  If the \ :literal:`backup\_name`\  is not provided, the default \ :literal:`backup\_name`\  will be used. If the \ :literal:`dest`\  is a USS file or USS path, the name of the backup file will be the destination file or path name appended with a timestamp, e.g. \ :literal:`/path/file\_name.2020-04-23-08-32-29-bak.tar`\ . If the \ :literal:`dest`\  is an MVS data set, it will be a data set with a randomly generated name.

  If \ :literal:`dest`\  is a data set member and \ :literal:`backup\_name`\  is not provided, the data set member will be backed up to the same partitioned data set with a randomly generated member name.

  | **required**: False
  | **type**: str


content
  When used instead of \ :literal:`src`\ , sets the contents of a file or data set directly to the specified value.

  Works only when \ :literal:`dest`\  is a USS file, sequential data set, or a partitioned data set member.

  If \ :literal:`dest`\  is a directory, then content will be copied to \ :literal:`/path/to/dest/inline\_copy`\ .

  | **required**: False
  | **type**: str


dest
  The remote absolute path or data set where the content should be copied to.

  \ :literal:`dest`\  can be a USS file, directory or MVS data set name.

  If \ :literal:`dest`\  has missing parent directories, they will be created.

  If \ :literal:`dest`\  is a nonexistent USS file, it will be created.

  If \ :literal:`dest`\  is a new USS file or replacement, the file will be appropriately tagged with either the system's default locale or the encoding option defined. If the USS file is a replacement, the user must have write authority to the file either through ownership, group or other permissions, else the module will fail.

  If \ :literal:`dest`\  is a nonexistent data set, it will be created following the process outlined here and in the \ :literal:`volume`\  option.

  If \ :literal:`dest`\  is a nonexistent data set, the attributes assigned will depend on the type of \ :literal:`src`\ . If \ :literal:`src`\  is a USS file, \ :literal:`dest`\  will have a Fixed Block (FB) record format and the remaining attributes will be computed. If \ :emphasis:`is\_binary=true`\ , \ :literal:`dest`\  will have a Fixed Block (FB) record format with a record length of 80, block size of 32760, and the remaining attributes will be computed. If \ :emphasis:`executable=true`\ ,\ :literal:`dest`\  will have an Undefined (U) record format with a record length of 0, block size of 32760, and the remaining attributes will be computed.

  When \ :literal:`dest`\  is a data set, precedence rules apply. If \ :literal:`dest\_data\_set`\  is set, this will take precedence over an existing data set. If \ :literal:`dest`\  is an empty data set, the empty data set will be written with the expectation its attributes satisfy the copy. Lastly, if no precendent rule has been exercised, \ :literal:`dest`\  will be created with the same attributes of \ :literal:`src`\ .

  When the \ :literal:`dest`\  is an existing VSAM (KSDS) or VSAM (ESDS), then source can be an ESDS, a KSDS or an RRDS. The VSAM (KSDS) or VSAM (ESDS) \ :literal:`dest`\  will be deleted and recreated following the process outlined in the \ :literal:`volume`\  option.

  When the \ :literal:`dest`\  is an existing VSAM (RRDS), then the source must be an RRDS. The VSAM (RRDS) will be deleted and recreated following the process outlined in the \ :literal:`volume`\  option.

  When \ :literal:`dest`\  is and existing VSAM (LDS), then source must be an LDS. The VSAM (LDS) will be deleted and recreated following the process outlined in the \ :literal:`volume`\  option.

  When \ :literal:`dest`\  is a data set, you can override storage management rules by specifying \ :literal:`volume`\  if the storage class being used has GUARANTEED\_SPACE=YES specified, otherwise, the allocation will fail. See \ :literal:`volume`\  for more volume related processes.

  | **required**: True
  | **type**: str


encoding
  Specifies which encodings the destination file or data set should be converted from and to.

  If \ :literal:`encoding`\  is not provided, the module determines which local and remote charsets to convert the data from and to. Note that this is only done for text data and not binary data.

  Only valid if \ :literal:`is\_binary`\  is false.

  | **required**: False
  | **type**: dict


  from
    The encoding to be converted from

    | **required**: True
    | **type**: str


  to
    The encoding to be converted to

    | **required**: False
    | **type**: str



tmp_hlq
  Override the default high level qualifier (HLQ) for temporary and backup datasets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the value \ :literal:`TMPHLQ`\  is used.

  | **required**: False
  | **type**: str


force
  If set to \ :literal:`true`\  and the remote file or data set \ :literal:`dest`\  is empty, the \ :literal:`dest`\  will be reused.

  If set to \ :literal:`true`\  and the remote file or data set \ :literal:`dest`\  is NOT empty, the \ :literal:`dest`\  will be deleted and recreated with the \ :literal:`src`\  data set attributes, otherwise it will be recreated with the \ :literal:`dest`\  data set attributes.

  To backup data before any deletion, see parameters \ :literal:`backup`\  and \ :literal:`backup\_name`\ .

  If set to \ :literal:`false`\ , the file or data set will only be copied if the destination does not exist.

  If set to \ :literal:`false`\  and destination exists, the module exits with a note to the user.

  | **required**: False
  | **type**: bool
  | **default**: False


force_lock
  By default, when \ :literal:`dest`\  is a MVS data set and is being used by another process with DISP=SHR or DISP=OLD the module will fail. Use \ :literal:`force\_lock`\  to bypass this check and continue with copy.

  If set to \ :literal:`true`\  and destination is a MVS data set opened by another process then zos\_copy will try to copy using DISP=SHR.

  Using \ :literal:`force\_lock`\  uses operations that are subject to race conditions and can lead to data loss, use with caution.

  If a data set member has aliases, and is not a program object, copying that member to a dataset that is in use will result in the aliases not being preserved in the target dataset. When this scenario occurs the module will fail.

  | **required**: False
  | **type**: bool
  | **default**: False


ignore_sftp_stderr
  During data transfer through SFTP, the module fails if the SFTP command directs any content to stderr. The user is able to override this behavior by setting this parameter to \ :literal:`true`\ . By doing so, the module would essentially ignore the stderr stream produced by SFTP and continue execution.

  When Ansible verbosity is set to greater than 3, either through the command line interface (CLI) using \ :strong:`-vvvv`\  or through environment variables such as \ :strong:`verbosity = 4`\ , then this parameter will automatically be set to \ :literal:`true`\ .

  | **required**: False
  | **type**: bool
  | **default**: False


is_binary
  If set to \ :literal:`true`\ , indicates that the file or data set to be copied is a binary file or data set.

  When \ :emphasis:`is\_binary=true`\ , no encoding conversion is applied to the content, all content transferred retains the original state.

  Use \ :emphasis:`is\_binary=true`\  when copying a Database Request Module (DBRM) to retain the original state of the serialized SQL statements of a program.

  | **required**: False
  | **type**: bool
  | **default**: False


executable
  If set to \ :literal:`true`\ , indicates that the file or library to be copied is an executable.

  If the \ :literal:`src`\  executable has an alias, the alias information is also copied. If the \ :literal:`dest`\  is Unix, the alias is not visible in Unix, even though the information is there and will be visible if copied to a library.

  If \ :emphasis:`executable=true`\ , and \ :literal:`dest`\  is a data set, it must be a PDS or PDSE (library).

  If \ :literal:`dest`\  is a nonexistent data set, the library attributes assigned will be Undefined (U) record format with a record length of 0, block size of 32760 and the remaining attributes will be computed.

  If \ :literal:`dest`\  is a file, execute permission for the user will be added to the file (\`\`u+x\`\`).

  | **required**: False
  | **type**: bool
  | **default**: False


aliases
  If set to \ :literal:`true`\ , indicates that any aliases found in the source (USS file, USS dir, PDS/E library or member) are to be preserved during the copy operation.

  Aliases are implicitly preserved when libraries are copied over to USS destinations. That is, when \ :literal:`executable=True`\  and \ :literal:`dest`\  is a USS file or directory, this option will be ignored.

  Copying of aliases for text-based data sets from USS sources or to USS destinations is not currently supported.

  | **required**: False
  | **type**: bool
  | **default**: False


local_follow
  This flag indicates that any existing filesystem links in the source tree should be followed.

  | **required**: False
  | **type**: bool
  | **default**: True


group
  Name of the group that will own the file system objects.

  When left unspecified, it uses the current group of the current user unless you are root, in which case it can preserve the previous ownership.

  This option is only applicable if \ :literal:`dest`\  is USS, otherwise ignored.

  | **required**: False
  | **type**: str


mode
  The permission of the destination file or directory.

  If \ :literal:`dest`\  is USS, this will act as Unix file mode, otherwise ignored.

  It should be noted that modes are octal numbers. The user must either add a leading zero so that Ansible's YAML parser knows it is an octal number (like \ :literal:`0644`\  or \ :literal:`01777`\ )or quote it (like \ :literal:`'644'`\  or \ :literal:`'1777'`\ ) so Ansible receives a string and can do its own conversion from string into number. Giving Ansible a number without following one of these rules will end up with a decimal number which will have unexpected results.

  The mode may also be specified as a symbolic mode (for example, \`\`u+rwx\`\` or \`\`u=rw,g=r,o=r\`\`) or a special string \`preserve\`.

  \ :emphasis:`mode=preserve`\  means that the file will be given the same permissions as the source file.

  | **required**: False
  | **type**: str


owner
  Name of the user that should own the filesystem object, as would be passed to the chown command.

  When left unspecified, it uses the current user unless you are root, in which case it can preserve the previous ownership.

  This option is only applicable if \ :literal:`dest`\  is USS, otherwise ignored.

  | **required**: False
  | **type**: str


remote_src
  If set to \ :literal:`false`\ , the module searches for \ :literal:`src`\  at the local machine.

  If set to \ :literal:`true`\ , the module goes to the remote/target machine for \ :literal:`src`\ .

  | **required**: False
  | **type**: bool
  | **default**: False


src
  Path to a file/directory or name of a data set to copy to remote z/OS system.

  If \ :literal:`remote\_src`\  is true, then \ :literal:`src`\  must be the path to a Unix System Services (USS) file, name of a data set, or data set member.

  If \ :literal:`src`\  is a local path or a USS path, it can be absolute or relative.

  If \ :literal:`src`\  is a directory, \ :literal:`dest`\  must be a partitioned data set or a USS directory.

  If \ :literal:`src`\  is a file and \ :literal:`dest`\  ends with "/" or is a directory, the file is copied to the directory with the same filename as \ :literal:`src`\ .

  If \ :literal:`src`\  is a directory and ends with "/", the contents of it will be copied into the root of \ :literal:`dest`\ . If it doesn't end with "/", the directory itself will be copied.

  If \ :literal:`src`\  is a directory or a file, file names will be truncated and/or modified to ensure a valid name for a data set or member.

  If \ :literal:`src`\  is a VSAM data set, \ :literal:`dest`\  must also be a VSAM.

  Wildcards can be used to copy multiple PDS/PDSE members to another PDS/PDSE.

  Required unless using \ :literal:`content`\ .

  | **required**: False
  | **type**: str


validate
  Specifies whether to perform checksum validation for source and destination files.

  Valid only for USS destination, otherwise ignored.

  | **required**: False
  | **type**: bool
  | **default**: False


volume
  If \ :literal:`dest`\  does not exist, specify which volume \ :literal:`dest`\  should be allocated to.

  Only valid when the destination is an MVS data set.

  The volume must already be present on the device.

  If no volume is specified, storage management rules will be used to determine the volume where \ :literal:`dest`\  will be allocated.

  If the storage administrator has specified a system default unit name and you do not set a \ :literal:`volume`\  name for non-system-managed data sets, then the system uses the volumes associated with the default unit name. Check with your storage administrator to determine whether a default unit name has been specified.

  | **required**: False
  | **type**: str


dest_data_set
  Data set attributes to customize a \ :literal:`dest`\  data set to be copied into.

  | **required**: False
  | **type**: dict


  type
    Organization of the destination

    | **required**: True
    | **type**: str
    | **choices**: ksds, esds, rrds, lds, seq, pds, pdse, member, basic, library


  space_primary
    If the destination \ :emphasis:`dest`\  data set does not exist , this sets the primary space allocated for the data set.

    The unit of space used is set using \ :emphasis:`space\_type`\ .

    | **required**: False
    | **type**: int


  space_secondary
    If the destination \ :emphasis:`dest`\  data set does not exist , this sets the secondary space allocated for the data set.

    The unit of space used is set using \ :emphasis:`space\_type`\ .

    | **required**: False
    | **type**: int


  space_type
    If the destination data set does not exist, this sets the unit of measurement to use when defining primary and secondary space.

    Valid units of size are \ :literal:`k`\ , \ :literal:`m`\ , \ :literal:`g`\ , \ :literal:`cyl`\ , and \ :literal:`trk`\ .

    | **required**: False
    | **type**: str
    | **choices**: k, m, g, cyl, trk


  record_format
    If the destination data set does not exist, this sets the format of the data set. (e.g \ :literal:`fb`\ )

    Choices are case-sensitive.

    | **required**: False
    | **type**: str
    | **choices**: fb, vb, fba, vba, u


  record_length
    The length of each record in the data set, in bytes.

    For variable data sets, the length must include the 4-byte prefix area.

    Defaults vary depending on format: If FB/FBA 80, if VB/VBA 137, if U 0.

    | **required**: False
    | **type**: int


  block_size
    The block size to use for the data set.

    | **required**: False
    | **type**: int


  directory_blocks
    The number of directory blocks to allocate to the data set.

    | **required**: False
    | **type**: int


  key_offset
    The key offset to use when creating a KSDS data set.

    \ :emphasis:`key\_offset`\  is required when \ :emphasis:`type=ksds`\ .

    \ :emphasis:`key\_offset`\  should only be provided when \ :emphasis:`type=ksds`\ 

    | **required**: False
    | **type**: int


  key_length
    The key length to use when creating a KSDS data set.

    \ :emphasis:`key\_length`\  is required when \ :emphasis:`type=ksds`\ .

    \ :emphasis:`key\_length`\  should only be provided when \ :emphasis:`type=ksds`\ 

    | **required**: False
    | **type**: int


  sms_storage_class
    The storage class for an SMS-managed dataset.

    Required for SMS-managed datasets that do not match an SMS-rule.

    Not valid for datasets that are not SMS-managed.

    Note that all non-linear VSAM datasets are SMS-managed.

    | **required**: False
    | **type**: str


  sms_data_class
    The data class for an SMS-managed dataset.

    Optional for SMS-managed datasets that do not match an SMS-rule.

    Not valid for datasets that are not SMS-managed.

    Note that all non-linear VSAM datasets are SMS-managed.

    | **required**: False
    | **type**: str


  sms_management_class
    The management class for an SMS-managed dataset.

    Optional for SMS-managed datasets that do not match an SMS-rule.

    Not valid for datasets that are not SMS-managed.

    Note that all non-linear VSAM datasets are SMS-managed.

    | **required**: False
    | **type**: str



use_template
  Whether the module should treat \ :literal:`src`\  as a Jinja2 template and render it before continuing with the rest of the module.

  Only valid when \ :literal:`src`\  is a local file or directory.

  All variables defined in inventory files, vars files and the playbook will be passed to the template engine, as well as \ `Ansible special variables <https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html#special-variables>`__\ , such as \ :literal:`playbook\_dir`\ , \ :literal:`ansible\_version`\ , etc.

  If variables defined in different scopes share the same name, Ansible will apply variable precedence to them. You can see the complete precedence order \ `in Ansible's documentation <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence>`__\ 

  | **required**: False
  | **type**: bool
  | **default**: False


template_parameters
  Options to set the way Jinja2 will process templates.

  Jinja2 already sets defaults for the markers it uses, you can find more information at its \ `official documentation <https://jinja.palletsprojects.com/en/latest/templates/>`__\ .

  These options are ignored unless \ :literal:`use\_template`\  is true.

  | **required**: False
  | **type**: dict


  variable_start_string
    Marker for the beginning of a statement to print a variable in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: {{


  variable_end_string
    Marker for the end of a statement to print a variable in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: }}


  block_start_string
    Marker for the beginning of a block in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: {%


  block_end_string
    Marker for the end of a block in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: %}


  comment_start_string
    Marker for the beginning of a comment in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: {#


  comment_end_string
    Marker for the end of a comment in Jinja2.

    | **required**: False
    | **type**: str
    | **default**: #}


  line_statement_prefix
    Prefix used by Jinja2 to identify line-based statements.

    | **required**: False
    | **type**: str


  line_comment_prefix
    Prefix used by Jinja2 to identify comment lines.

    | **required**: False
    | **type**: str


  lstrip_blocks
    Whether Jinja2 should strip leading spaces from the start of a line to a block.

    | **required**: False
    | **type**: bool
    | **default**: False


  trim_blocks
    Whether Jinja2 should remove the first newline after a block is removed.

    Setting this option to \ :literal:`False`\  will result in newlines being added to the rendered template. This could create invalid code when working with JCL templates or empty records in destination data sets.

    | **required**: False
    | **type**: bool
    | **default**: True


  keep_trailing_newline
    Whether Jinja2 should keep the first trailing newline at the end of a template after rendering.

    | **required**: False
    | **type**: bool
    | **default**: False


  newline_sequence
    Sequence that starts a newline in a template.

    | **required**: False
    | **type**: str
    | **default**: \\n
    | **choices**: \\n, \\r, \\r\\n


  auto_reload
    Whether to reload a template file when it has changed after the task has started.

    | **required**: False
    | **type**: bool
    | **default**: False





Examples
--------

.. code-block:: yaml+jinja

   
   - name: Copy a local file to a sequential data set
     zos_copy:
       src: /path/to/sample_seq_data_set
       dest: SAMPLE.SEQ.DATA.SET

   - name: Copy a local file to a USS location and validate checksum
     zos_copy:
       src: /path/to/test.log
       dest: /tmp/test.log
       validate: true

   - name: Copy a local ASCII encoded file and convert to IBM-1047
     zos_copy:
       src: /path/to/file.txt
       dest: /tmp/file.txt

   - name: Copy a local directory to a PDSE
     zos_copy:
       src: /path/to/local/dir/
       dest: HLQ.DEST.PDSE

   - name: Copy file with permission details
     zos_copy:
       src: /path/to/foo.conf
       dest: /etc/foo.conf
       mode: "0644"
       group: foo
       owner: bar

   - name: Module will follow the symbolic link specified in src
     zos_copy:
       src: /path/to/link
       dest: /path/to/uss/location
       local_follow: true

   - name: Copy a local file to a PDS member and convert encoding
     zos_copy:
       src: /path/to/local/file
       dest: HLQ.SAMPLE.PDSE(MEMBER)
       encoding:
         from: UTF-8
         to: IBM-037

   - name: Copy a VSAM  (KSDS) to a VSAM  (KSDS)
     zos_copy:
       src: SAMPLE.SRC.VSAM
       dest: SAMPLE.DEST.VSAM
       remote_src: true

   - name: Copy inline content to a sequential dataset and replace existing data
     zos_copy:
       content: 'Inline content to be copied'
       dest: SAMPLE.SEQ.DATA.SET

   - name: Copy a USS file to sequential data set and convert encoding beforehand
     zos_copy:
       src: /path/to/remote/uss/file
       dest: SAMPLE.SEQ.DATA.SET
       remote_src: true

   - name: Copy a USS directory to another USS directory
     zos_copy:
       src: /path/to/uss/dir
       dest: /path/to/dest/dir
       remote_src: true

   - name: Copy a local binary file to a PDSE member
     zos_copy:
       src: /path/to/binary/file
       dest: HLQ.SAMPLE.PDSE(MEMBER)
       is_binary: true

   - name: Copy a sequential data set to a PDS member
     zos_copy:
       src: SAMPLE.SEQ.DATA.SET
       dest: HLQ.SAMPLE.PDSE(MEMBER)
       remote_src: true

   - name: Copy a local file and take a backup of the existing file
     zos_copy:
       src: /path/to/local/file
       dest: /path/to/dest
       backup: true
       backup_name: /tmp/local_file_backup

   - name: Copy a PDS on remote system to a new PDS
     zos_copy:
       src: HLQ.SRC.PDS
       dest: HLQ.NEW.PDS
       remote_src: true

   - name: Copy a PDS on remote system to a PDS, replacing the original
     zos_copy:
       src: HLQ.SAMPLE.PDSE
       dest: HLQ.EXISTING.PDSE
       remote_src: true
       force: true

   - name: Copy PDS member to a new PDS member. Replace if it already exists
     zos_copy:
       src: HLQ.SAMPLE.PDSE(SRCMEM)
       dest: HLQ.NEW.PDSE(DESTMEM)
       remote_src: true
       force: true

   - name: Copy a USS file to a PDSE member. If PDSE does not exist, allocate it
     zos_copy:
       src: /path/to/uss/src
       dest: DEST.PDSE.DATA.SET(MEMBER)
       remote_src: true

   - name: Copy a sequential data set to a USS file
     zos_copy:
       src: SRC.SEQ.DATA.SET
       dest: /tmp/
       remote_src: true

   - name: Copy a PDSE member to USS file
     zos_copy:
       src: SRC.PDSE(MEMBER)
       dest: /tmp/member
       remote_src: true

   - name: Copy a PDS to a USS directory (/tmp/SRC.PDS)
     zos_copy:
       src: SRC.PDS
       dest: /tmp
       remote_src: true

   - name: Copy all members inside a PDS to another PDS
     zos_copy:
       src: SOME.SRC.PDS(*)
       dest: SOME.DEST.PDS
       remote_src: true

   - name: Copy all members starting with 'ABC' inside a PDS to another PDS
     zos_copy:
       src: SOME.SRC.PDS(ABC*)
       dest: SOME.DEST.PDS
       remote_src: true

   - name: Allocate destination in a specific volume
     zos_copy:
       src: SOME.SRC.PDS
       dest: SOME.DEST.PDS
       volume: 'VOL033'
       remote_src: true

   - name: Copy a USS file to a fully customized sequential data set
     zos_copy:
       src: /path/to/uss/src
       dest: SOME.SEQ.DEST
       remote_src: true
       volume: '222222'
       dest_data_set:
         type: seq
         space_primary: 10
         space_secondary: 3
         space_type: k
         record_format: vb
         record_length: 150

   - name: Copy a Program Object and its aliases on a remote system to a new PDSE member MYCOBOL
     zos_copy:
       src: HLQ.COBOLSRC.PDSE(TESTPGM)
       dest: HLQ.NEW.PDSE(MYCOBOL)
       remote_src: true
       executable: true
       aliases: true

   - name: Copy a Load Library from a USS directory /home/loadlib to a new PDSE
     zos_copy:
       src: '/home/loadlib/'
       dest: HLQ.LOADLIB.NEW
       remote_src: true
       executable: true
       aliases: true

   - name: Copy a file with ASA characters to a new sequential data set.
     zos_copy:
       src: ./files/print.txt
       dest: HLQ.PRINT.NEW
       asa_text: true




Notes
-----

.. note::
   Destination data sets are assumed to be in catalog. When trying to copy to an uncataloged data set, the module assumes that the data set does not exist and will create it.

   Destination will be backed up if either \ :literal:`backup`\  is \ :literal:`true`\  or \ :literal:`backup\_name`\  is provided. If \ :literal:`backup`\  is \ :literal:`false`\  but \ :literal:`backup\_name`\  is provided, task will fail.

   When copying local files or directories, temporary storage will be used on the remote z/OS system. The size of the temporary storage will correspond to the size of the file or directory being copied. Temporary files will always be deleted, regardless of success or failure of the copy task.

   VSAM data sets can only be copied to other VSAM data sets.

   For supported character sets used to encode data, refer to the \ `documentation <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html>`__\ .

   This module uses SFTP (Secure File Transfer Protocol) for the underlying transfer protocol; SCP (secure copy protocol) and Co:Z SFTP are not supported. In the case of Co:z SFTP, you can exempt the Ansible user id on z/OS from using Co:Z thus falling back to using standard SFTP. If the module detects SCP, it will temporarily use SFTP for transfers, if not available, the module will fail.

   Beginning in version 1.8.x, zos\_copy will no longer attempt to correct a copy of a data type member into a PDSE that contains program objects. You can control this behavior using module option \ :literal:`executable`\  that will signify an executable is being copied into a PDSE with other executables. Mixing data type members with program objects will result in a (FSUM8976,./zos\_copy.html) error.



See Also
--------

.. seealso::

   - :ref:`zos_fetch_module`
   - :ref:`zos_data_set_module`




Return Values
-------------


src
  Source file or data set being copied.

  | **returned**: changed
  | **type**: str
  | **sample**: /path/to/source.log

dest
  Destination file/path or data set name.

  | **returned**: success
  | **type**: str
  | **sample**: SAMPLE.SEQ.DATA.SET

dest_created
  Indicates whether the module created the destination.

  | **returned**: success and if dest was created by the module.
  | **type**: bool
  | **sample**:

    .. code-block:: json

        true

destination_attributes
  Attributes of a dest created by the module.

  | **returned**: success and destination was created by the module.
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "block_size": 32760,
            "record_format": "fb",
            "record_length": 45,
            "space_primary": 2,
            "space_secondary": 1,
            "space_type": "k",
            "type": "pdse"
        }

  block_size
    Block size of the dataset.

    | **type**: int
    | **sample**: 32760

  record_format
    Record format of the dataset.

    | **type**: str
    | **sample**: fb

  record_length
    Record length of the dataset.

    | **type**: int
    | **sample**: 45

  space_primary
    Allocated primary space for the dataset.

    | **type**: int
    | **sample**: 2

  space_secondary
    Allocated secondary space for the dataset.

    | **type**: int
    | **sample**: 1

  space_type
    Unit of measurement for space.

    | **type**: str
    | **sample**: k

  type
    Type of dataset allocated.

    | **type**: str
    | **sample**: pdse


checksum
  SHA256 checksum of the file after running zos\_copy.

  | **returned**: When ``validate=true`` and if ``dest`` is USS
  | **type**: str
  | **sample**: 8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e

backup_name
  Name of the backup file or data set that was created.

  | **returned**: if backup=true or backup_name=true
  | **type**: str
  | **sample**: /path/to/file.txt.2015-02-03@04:15~

gid
  Group id of the file, after execution.

  | **returned**: success and if dest is USS
  | **type**: int
  | **sample**: 100

group
  Group of the file, after execution.

  | **returned**: success and if dest is USS
  | **type**: str
  | **sample**: httpd

owner
  Owner of the file, after execution.

  | **returned**: success and if dest is USS
  | **type**: str
  | **sample**: httpd

uid
  Owner id of the file, after execution.

  | **returned**: success and if dest is USS
  | **type**: int
  | **sample**: 100

mode
  Permissions of the target, after execution.

  | **returned**: success and if dest is USS
  | **type**: str
  | **sample**: 420

size
  Size(in bytes) of the target, after execution.

  | **returned**: success and dest is USS
  | **type**: int
  | **sample**: 1220

state
  State of the target, after execution.

  | **returned**: success and if dest is USS
  | **type**: str
  | **sample**: file

note
  A note to the user after module terminates.

  | **returned**: When ``force=true`` and ``dest`` exists
  | **type**: str
  | **sample**: No data was copied

msg
  Failure message returned by the module.

  | **returned**: failure
  | **type**: str
  | **sample**: Error while gathering data set information

stdout
  The stdout from a USS command or MVS command, if applicable.

  | **returned**: failure
  | **type**: str
  | **sample**: Copying local file /tmp/foo/src to remote path /tmp/foo/dest

stderr
  The stderr of a USS command or MVS command, if applicable.

  | **returned**: failure
  | **type**: str
  | **sample**: No such file or directory "/tmp/foo"

stdout_lines
  List of strings containing individual lines from stdout.

  | **returned**: failure
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "u\"Copying local file /tmp/foo/src to remote path /tmp/foo/dest..\""
        ]

stderr_lines
  List of strings containing individual lines from stderr.

  | **returned**: failure
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            {
                "u\"FileNotFoundError": "No such file or directory \u0027/tmp/foo\u0027\""
            }
        ]

rc
  The return code of a USS or MVS command, if applicable.

  | **returned**: failure
  | **type**: int
  | **sample**: 8

cmd
  The MVS command issued, if applicable.

  | **returned**: failure
  | **type**: str
  | **sample**: REPRO INDATASET(SAMPLE.DATA.SET) OUTDATASET(SAMPLE.DEST.DATA.SET)

