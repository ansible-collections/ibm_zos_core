.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2025                                    .
.. ...........................................................................

========
Releases
========

Version 1.13.0
==============

Minor Changes
-------------

- ``zos_copy``

   - Added new option ``autoescape`` to ``template_parameters``, allowing users to disable autoescaping of common XML/HTML characters when working with Jinja templates.
   - Adds error message when a PDS/E source member does not exist or is not cataloged.

- ``zos_job_submit``

   - Add deploy and forget capability. Now when wait_time_s is 0, the module will submit the job and will not wait to get the job details or content, returning only the job id.
   - Added new option ``autoescape`` to ``template_parameters``, allowing users to disable autoescaping of common XML/HTML characters when working with Jinja templates.
   - Added support to run zos_job_submit tasks in async mode inside playbooks.

- ``zos_mvs_raw`` - Added ``max_rc`` option. Now when the user sets ``max_rc``, the module tolerates the failure if the return code is smaller than the ``max_rc`` specified, however, return value ``changed`` will be False if the program return code is not 0.
- ``zos_script`` - Added new option ``autoescape`` to ``template_parameters``, allowing users to disable autoescaping of common XML/HTML characters when working with Jinja templates.

Bugfixes
--------

- ``zos_copy``

   - Improve module zos_copy error handling when the user does not have universal access authority set to UACC(READ) for SAF Profile 'MVS.MCSOPER.ZOAU' and SAF Class OPERCMDS. The module now handles the exception and returns an informative message.
   - Previously, if the dataset name included special characters such as $, validation would fail when force_lock was false. This has been changed to allow the use of special characters when force_lock option is false.
   - Previously, if the dataset name included special characters such as ``$`` and ``asa_text`` option is true, the module would fail. Fix now allows the use of special characters in the data set name when ``asa_text`` option is true.
   - When ``asa_text`` was set to true at the same time as ``force_lock``, a copy would fail saying the destination was already in use. Fix now opens destination data sets up with disposition SHR when ``force_lock`` and ``asa_text`` are set to true.

- ``zos_fetch`` - Some relative paths were not accepted as a parameter e.g. C(files/fetched_file). Change now allows the user to use different types of relative paths as a parameter.
- ``zos_find``

   - Module would not find VSAM data and index resource types. Fix now finds the data and index resource types.
   - Module would not find a VSAM cluster resource type if it was in use with DISP=OLD. Fix now finds the VSAM cluster.

- ``zos_job_query`` - Module was not returning values for system and subsystem. Fix now returns these values.
- ``zos_mvs_raw``

   - If a program failed with a non-zero return code and verbose was false, the module would succeed. Whereas, if the program failed and verbose was true the module would fail. Fix now has a consistent behavior and fails in both cases.
   - Module would not populate stderr return value. Fix now populates stderr in return values.
   - Module would obfuscate the return code from the program when failing returning 8 instead. Fix now returns the proper return code from the program.
   - Module would return the stderr content in stdout when verbose was true and return code was 0. Fix now does not replace stdout content with stderr.
   - Option ``tmp_hlq`` was not being used as HLQ when creating backup data sets. Fix now uses ``tmp_hlq`` as HLQ for backup data sets.

- ``zos_script`` - When the user trying to run a remote script had execute permissions but wasn't owner of the file, the module would fail while trying to change permissions on it. Fix now ensures the module first checks if the user can execute the script and only try to change permissions when necessary.

New Modules
-----------

- ibm.ibm_zos_core.zos_zfs_resize - Resize a zfs data set.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.
- ``zos_apf`` - When trying to remove a library that contains the '$' character in the name for an APF(authorized program facility), the operation might fail.
- ``zos_copy`` - Copying from a sequential data set that is in use will result in a false positive and destination data set will be empty. The same is true when ``type=gdg`` and source GDS is a sequential data set in use.

Version 1.12.1
==============

Bugfixes
--------

-  ``zos_copy``

   - Previously, if the dataset name included special characters such as ``$`` and ``asa_text`` option is true, the module would fail. Fix now allows the use of special characters in the data set name when ``asa_text`` option is true.
   - Previously, if the dataset name included special characters such as $, validation would fail when force_lock was false. This has been changed to allow the use of special characters when force_lock option is false.
   - When ``asa_text`` was set to true at the same time as ``force_lock``,  a copy would fail saying the destination was already in use. Fix now opens destination data sets up with disposition SHR when ``force_lock`` and ``asa_text`` are set to true.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_


Known Issues
------------
- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.
- ``zos_apf`` - When trying to remove a library that contains the '$' character in the name for an APF(authorized program facility), the operation will fail.
- ``zos_find`` - When trying to find a VSAM data set that is allocated with DISP=OLD using age filter the module will not find it.

Version 1.12.0
==============

Minor Changes
-------------

- ``zos_backup_restore`` - default behavior for module option **hlq** changed. When option **operation** is set to **restore** and the **hlq** is not provided, the original high level qualifiers in a backup will be used for a restore.

- ``zos_job_output`` - has added the address space type for a job returned as **content_type** in the module response.

- ``zos_job_query`` - has added the address space type for a job returned as **content_type** in the module response.

- ``zos_job_submit`` - has added the address space type for a job returned as **content_type** in the module response.

- ``zos_mvs_raw`` - updates the stdout and stderr when an unknown, unrecognized, or unrepresentable characters with the 'replacement character' (�), found in the Unicode standard at code point U+FFFD.

- ``zos_operator`` - has added the option **case_sensitive**, allowing the module to control the commands case.

- ``zos_script`` - updates the stdout and stderr when an unknown, unrecognized, or unrepresentable characters with the 'replacement character' (�), found in the Unicode standard at code point U+FFFD.

- ``zos_tso_command`` - updates the stdout and stderr when an unknown, unrecognized, or unrepresentable characters with the 'replacement character' (�), found in the Unicode standard at code point U+FFFD.

Bugfixes
--------

- ``zos_apf`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_archive`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_backup_restore`` - when a recoverable error was encountered and **recover = True**, the module would fail. The change now allows the module to recover.

- ``zos_blockinfile``

   - when the modules **marker_begin** and **marker_end** were set to the same value, the module would not delete the block. Now the module requires the **marker_begin** and **marker_end** to have different values.
   - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option..

- ``zos_copy``

   - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.
   - module would fail if the user did not have Universal Access Authority for SAF Profile **MVS.MCSOPER.ZOAU** and SAF Class **OPERCMDS**. Now the module handles the exception and returns an informative message.
   - module would ignore the value set for **remote_tmp** in the Ansible configuration file. Now the module uses the value of **remote_tmp** or the default value **~/.ansible/tmp** if none is given.

- ``zos_data_set`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_encode`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_fetch`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_find``

   - Module would not find VSAM data and index resource types. Fix now finds the data and index resource types.
   - Module would not find a VSAM cluster resource type if it was in use with DISP=OLD. Fix now finds the VSAM cluster.

- ``zos_job_output`` - module would raise an invalid argument error for a user ID that contained **@**, **$**, or **#**. Now the module supports RACF user naming conventions.

- ``zos_job_query``

   - module did not return values for properties **system** and **subsystem**. Now the module returns these values.
   - module would raise an invalid argument error for a user ID that contained **@**, **$**, or **#**. Now the module supports RACF user naming conventions.

- ``zos_lineinfile`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_mount`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

- ``zos_mvs_raw``

   - Module sub-option **base64** for **return_content** did not retrieve DD output as Base64. Now the module returns Base64 encoded contents for the DD.
   - Module would return the stderr content in stdout when verbose was true and return code was 0. Fix now does not replace stdout content with stderr.
   - Module would obfuscate the return code from the program when failing returning 8 instead. Fix now returns the proper return code from the program.
   - If a program failed with a non-zero return code and verbose was false, the module would succeed (false positive). Fix now fails the module for all instances where a program has a non-zero return code.

- ``zos_script`` - module would only read the first command line argument if more than one was used. Now the module passes all arguments to the remote command.

- ``zos_unarchive`` - module option **tmp_hlq** was previously ignored and default values were used. Now the module uses the value set in the option.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.
- ``zos_apf`` - When trying to remove a library that contains the '$' character in the name for an APF(authorized program facility), the operation will fail.
- ``zos_find`` - When trying to find a VSAM data set that is allocated with DISP=OLD using age filter the module will not find it.

Version 1.11.1
==============

Bugfixes
--------

- ``zos_mvs_raw``

   - If a program failed with a non-zero return code and verbose was false, the module would succeed. Whereas, if the program failed and verbose was true the module would fail(false positive). Fix now has a consistent behavior and fails in both cases.
   - Module would obfuscate the return code from the program when failing returning 8 instead. Fix now returns the proper return code from the program.
   - Module would return the stderr content in stdout when verbose was true and return code was 0. Fix now does not replace stdout content with stderr.


Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.
- ``zos_apf`` - When trying to remove a library that contains the '$' character in the name from APF(authorized program facility), operation will fail.

Version 1.11.0
==============

Minor Changes
-------------

- ``zos_apf`` - Added support for data set names (libraries) with special characters ($, /#, /- and @).
- ``zos_archive``

   - Added support for GDG and GDS relative name notation to archive data sets.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_backup_restore``

   - Added support for GDS relative name notation to include or exclude data sets when operation is backup.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_blockinfile``

   - Added support for GDG and GDS relative name notation to specify a data set. And backup in new generations.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_copy``

   - Added support for copying from and to generation data sets (GDS) and generation data groups (GDG) including using a GDS for backup.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_data_set``

   - Added support for GDG and GDS relative name notation to create, delete, catalog and uncatalog a data set.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_encode``

   - Added support for converting the encodings of generation data sets (GDS).
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_fetch``

   - Added support for fetching generation data groups (GDG) and generation data sets (GDS).
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_find``

   - Added support for finding generation data groups (GDG) and generation data sets (GDS).
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_job_submit``

   - Improved the mechanism for copying to remote systems by removing the use of deepcopy, which had previously resulted in the module failing on some systems.
   - Added support for running JCL stored in generation data groups (GDG) and generation data sets (GDS).
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_lineinfile``

   - Added support for GDG and GDS relative name notation to specify the target data set and to backup into new generations.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_mount`` - Added support for data set names with special characters ($, /#, /- and @).
- ``zos_mvs_raw``

   - Added support for GDG and GDS relative name notation to specify data set names.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_script`` - Improved the mechanism for copying to remote systems by removing the use of deepcopy, which had previously resulted in the module failing on some systems.
- ``zos_tso_command``

   - Added support for using GDG and GDS relative name notation in running TSO commands.
   - Added support for data set names with special characters ($, /#, /- and @).

- ``zos_unarchive``

   - Improved the mechanism for copying to remote systems by removing the use of deepcopy, which had previously resulted in the module failing on some systems.
   - Added support for data set names with special characters ($, /#, /- and @).

Bugfixes
--------

- ``zos_copy``

   - Fixes the issue that prevents the module from automatically computing member names when copying a file into a PDS/E. The module now computes the member name when copying into a PDS/E.
   - Fixes an issue that would perform an unnecessary check if a destination data set is locked for data sets the module created. The module only performs this check for destinations that are present.

- ``zos_data_set`` - When checking if a data set is cataloged, module failed to account for exceptions which occurred during the LISTCAT. The module now raises an MVSCmdExecError if the return code from LISTCAT exceeds the determined threshold.
- ``zos_job_submit`` - Was not propagating any error types including UnicodeDecodeError, JSONDecodeError, TypeError, KeyError when encountered. The module now shares the error type (UnicodeDecodeError, JSONDecodeError, TypeError, KeyError) in the error message.
- ``zos_mvs_raw`` - The first character of each line in dd_output was missing. The module now includes the first character of each line.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.
- ``zos_apf`` - When trying to remove a library that contains the '$' character in the name for an APF(authorized program facility), the operation will fail.

Version 1.10.0
==============

Major Changes
-------------

- Starting with IBM Ansible z/OS core version 1.10.x, ZOAU version 1.3.0 will be required.
- Starting with IBM Ansible z/OS core version 1.10.x, all module options are case sensitive,
  review the porting guide for specifics.
- The README has been updated with a new template.
- The **Reference** section has been renamed to **Requirements** and now includes a support matrix.

Minor Changes
-------------

- ``zos_apf`` - Enhanced error messages when an exception is caught.
- ``zos_backup_restore`` - Added option **tmp_hlq** to the user module to override the default high level qualifier (HLQ) for temporary and backup data sets.
- ``zos_copy`` - Documented module options `group` and `owner`.

Bugfixes
--------

- ``zos_apf`` - Option **list** previously only returned one data set, now it returns a list of retrieved data sets.
- ``zos_blockinfile`` - Option **block** when containing double double quotation marks results in a task failure (failed=True); now the module handles this case to avoid failure.
- ``zos_find`` - Option **size** failed if a PDS/E matched the pattern, now filtering on utilized size for a PDS/E is supported.

- ``zos_job_submit``

  - Did not default to **location=DATA_SET** when no location was defined, now the location defaults to DATA_SET.
  - Option **max_rc** previously did not influence a modules status, now the option value influences the tasks failure status.

- ``zos_mvs_raw`` - Option **tmp_hlq** when creating temporary data sets was previously ignored, now the option honors the High Level Qualifier for temporary data sets created during the module execution.

Porting Guide
-------------

This section discusses the behavioral changes between ``ibm_zos_core`` v1.9.0 and ``ibm_zos_core`` v1.10.0-beta.1.
It is intended to assist in updating your playbooks so this collection will continue to work.

- ``zos_archive``

  - option **terse_pack** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **record_format** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **space_type** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **type** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.

- ``zos_backup_restore`` - option **space_type** no longer accepts uppercase choices, users should replace them with lowercase ones.

- ``zos_copy``

  - suboption **record_format** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **space_type** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **type** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.

- ``zos_data_set``

  - option **record_format** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - option **space_type** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - option **type** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - options inside **batch** no longer accept uppercase choices, users should replace them with lowercase ones.

- ``zos_job_submit`` - option **location** no longer accepts uppercase choices, users should replace them with lowercase ones.

- ``zos_mount``

  - option **automove** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - option **fs_type** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - option **mount_opts** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - option **tag_untagged** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - option **unmount_opts** no longer accepts uppercase choices, users should replace them with lowercase ones.

- ``zos_mvs_raw``

  - options inside **dd_concat** no longer accept uppercase choices, users should replace them with lowercase ones.
  - suboption **record_format** of **dd_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **record_format** of **dd_unix** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **space_type** of **dd_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **type** of **dd_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboptions **disposition_normal** and **disposition_abnormal** of **dd_data_set** no longer accept **catlg** and **uncatlg** as choices. This also applies when defining a **dd_data_set** inside **dd_concat**.

- ``zos_unarchive``

  - suboption **record_format** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **space_type** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.
  - suboption **type** of **dest_data_set** no longer accepts uppercase choices, users should replace them with lowercase ones.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.
- ``zos_data_set`` - When data set creation fails, exception can throw a bad import error instead of data set creation error.
- ``zos_copy`` - To use this module, you must define the RACF FACILITY class profile and allow READ access to RACF FACILITY profile MVS.MCSOPER.ZOAU. If your system uses a different security product, consult that product's documentation to configure the required security classes.
- ``zos_job_submit``, ``zos_job_output``, ``zos_operator_action_query`` - encounters JSON decoding (DecodeError, TypeError, KeyError) errors when interacting with results that contain non-printable UTF-8 characters in the response. This will be addressed in **ZOAU version 1.3.2** and later.

   - Some options to work around this known issue are:

      - Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
      - Ignore module errors by using  **ignore_errors:true** for a specific playbook task.
      - If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a registered variable to extract the
        job ID with a regular expression. Then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.
      - If the error is the result of a batch job, set option **return_output** to false so that no DDs are read which could contain the non-printable UTF-8 characters.

- In the past, choices could be defined in either lower or upper case. Now, only the case that is identified in the docs can be set, this is so that the collection can continue to maintain certified status.
- Use of special characters (#, @, $, \- ) in different options like data set names and commands is not fully supported, some modules support them but is the user responsibility to escape them. Read each module documentation for further details.

Version 1.9.4
=============

Bugfixes
--------

- ``zos_mvs_raw`` - If verbose was true, even if the program return code was 0, the module would fail. Fix now ensures the module fails on non-zero return code only.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------

- ``zos_job_submit`` - when setting 'location' to 'LOCAL' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.

- ``zos_job_submit``, ``zos_job_output``, ``zos_operator_action_query`` - encounters UTF-8 decoding errors when interacting with results that contain non-printable UTF-8 characters in the response. This has been addressed in this release and corrected with **ZOAU version 1.2.5.6** or later.

   - If the appropriate level of ZOAU can not be installed, some options are to:

      - Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
      - Ignore module errors by using  **ignore_errors:true** for a specific playbook task.
      - If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a registered variable to extract the
        job ID with a regular expression. Then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.
      - If the error is the result of a batch job, set option **return_output** to false so that no DDs are read which could contain the non-printable UTF-8 characters.

- ``zos_data_set`` - An undocumented option **size** was defined in module **zos_data_set**, this has been removed to satisfy collection certification, use the intended and documented **space_primary** option.

- In the past, choices could be defined in either lower or upper case. Now, only the case that is identified in the docs can be set, this is so that the collection can continue to maintain certified status.

Version 1.9.3
=============

Bugfixes
--------

- ``zos_job_submit`` - module did not return values for properties **system** and **subsystem**. Now the module returns these values.
- ``zos_mvs_raw``

    - If a program failed with a non-zero return code and verbose was false, the module would succeed. Whereas, if the program failed and verbose was true the module would fail. Fix now has a consistent behavior and fails in both cases.
    - Module would obfuscate the return code from the program when failing returning 8 instead. Fix now returns the proper return code from the program.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------

- ``zos_job_submit`` - when setting 'location' to 'LOCAL' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.

- ``zos_job_submit``, ``zos_job_output``, ``zos_operator_action_query`` - encounters UTF-8 decoding errors when interacting with results that contain non-printable UTF-8 characters in the response. This has been addressed in this release and corrected with **ZOAU version 1.2.5.6** or later.

   - If the appropriate level of ZOAU can not be installed, some options are to:

      - Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
      - Ignore module errors by using  **ignore_errors:true** for a specific playbook task.
      - If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a registered variable to extract the
        job ID with a regular expression. Then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.
      - If the error is the result of a batch job, set option **return_output** to false so that no DDs are read which could contain the non-printable UTF-8 characters.

- ``zos_data_set`` - An undocumented option **size** was defined in module **zos_data_set**, this has been removed to satisfy collection certification, use the intended and documented **space_primary** option.

- In the past, choices could be defined in either lower or upper case. Now, only the case that is identified in the docs can be set, this is so that the collection can continue to maintain certified status.


Version 1.9.2
=============

Bugfixes
--------

- ``zos_copy`` - when creating the destination data set, the module would unnecessarily check if a data set is locked by another process. The module no longer performs this check when it creates the data set.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------

- ``zos_job_submit`` - when setting 'location' to 'LOCAL' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.

- ``zos_job_submit``, ``zos_job_output``, ``zos_operator_action_query`` - encounters UTF-8 decoding errors when interacting with results that contain non-printable UTF-8 characters in the response. This has been addressed in this release and corrected with **ZOAU version 1.2.5.6** or later.

   - If the appropriate level of ZOAU can not be installed, some options are to:

      - Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
      - Ignore module errors by using  **ignore_errors:true** for a specific playbook task.
      - If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a registered variable to extract the
        job ID with a regular expression. Then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.
      - If the error is the result of a batch job, set option **return_output** to false so that no DDs are read which could contain the non-printable UTF-8 characters.

- ``zos_data_set`` - An undocumented option **size** was defined in module **zos_data_set**, this has been removed to satisfy collection certification, use the intended and documented **space_primary** option.

- In the past, choices could be defined in either lower or upper case. Now, only the case that is identified in the docs can be set, this is so that the collection can continue to maintain certified status.

Version 1.9.1
=============

Bugfixes
--------

- ``zos_find`` - Option size failed if a PDS/E matched the pattern, now filtering on utilized size for a PDS/E is supported.
- ``zos_mvs_raw`` - Option **tmp_hlq** when creating temporary data sets was previously ignored, now the option honors the High Level Qualifier for temporary data sets created during the module execution.

Known Issues
------------

- ``zos_job_submit`` - when setting 'location' to 'local' and not specifying the from and to encoding, the modules defaults are not read leaving the file in its original encoding; explicitly set the encodings instead of relying on the default.
- ``zos_job_submit`` - when submitting JCL, the response value returned for **byte_count** is incorrect.

- ``zos_job_submit``, ``zos_job_output``, ``zos_operator_action_query`` - encounters UTF-8 decoding errors when interacting with results that contain non-printable UTF-8 characters in the response. This has been addressed in this release and corrected with **ZOAU version 1.2.5.6** or later.

   - If the appropriate level of ZOAU can not be installed, some options are to:

      - Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
      - Ignore module errors by using  **ignore_errors:true** for a specific playbook task.
      - If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a registered variable to extract the
        job ID with a regular expression. Then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.
      - If the error is the result of a batch job, set option **return_output** to false so that no DDs are read which could contain the non-printable UTF-8 characters.

- ``zos_data_set`` - An undocumented option **size** was defined in module **zos_data_set**, this has been removed to satisfy collection certification, use the intended and documented **space_primary** option.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Version 1.9.0
=============

Major Changes
-------------
  - IBM Ansible z/OS core collection (**ibm_zos_core**) version 1.9.0 will be the last release to support ZOAU 1.2.x.

    - IBM Ansible z/OS core version 1.9.0 will continue to receive security updates and bug fixes.

  - Starting with IBM Ansible z/OS core version 1.10.0, ZOAU version 1.3.0 will be required.
  - IBM Open Enterprise SDK for Python version 3.9.x is no longer supported.

Minor Changes
-------------
- ``zos_apf`` - Improved exception handling when the module is unable to process a response originating as a batch update.
- ``zos_copy`` - Improved performance when copying multiple members from one PDS/E to another PDS/E.
- ``zos_job_output`` - Has been enhanced to allow for both a job ID and owner to be selected when obtaining job output, removing the prior mutual exclusivity.
- ``zos_operator`` - Improved the modules handling of ZOAU import errors allowing for the traceback to flow back to the source.
- ``zos_job_query`` - Improved the modules handling of ZOAU import errors allowing for the traceback to flow back to the source.
- ``zos_job_submit``

    - Improved messages in the action plugin.
    - Improved the action plugin performance, flow and use of undocumented variables.
    - Improved the modules handling of ZOAU import errors allowing for the traceback to flow back to the source.
    - Improved job status support, now the supported statuses for property **ret_code[msg]** are:

      - Job status **ABEND** indicates the job ended abnormally.
      - Job status **AC** indicates the job is active, often a started task or job taking long.
      - Job status **CAB** indicates a converter abend.
      - Job status **CANCELED** indicates the job was canceled.
      - Job status **CNV** indicates a converter error.
      - Job status **FLU** indicates the job was flushed.
      - Job status **JCLERR** or **JCL ERROR** indicates the JCL has an error.
      - Job status **SEC** or **SEC ERROR** indicates the job as encountered a security error.
      - Job status **SYS** indicates a system failure.
      - Job status **?** indicates status can not be determined.

- ``zos_tso_command``

    - Has been updated with a new example demonstrating how to explicitly execute a REXX script in a data set.
    - Has been updated with a new example demonstrating how to chain multiple TSO commands into one invocation using semicolons.

- ``zos_mvs_raw``

    - Has been enhanced to ensure that **instream-data** for option **dd_input** contain blanks in columns 1 and 2 while retaining a maximum length
      of 80 columns for strings and a list of strings. This is generally the requirement for most z/OS programs.
    - Has been updated with new examples demonstrating a YAML block indicator, often helpful when wanting to control the
      **instream-data** formatting.


Bugfixes
--------

- ``zos_apf`` - Fixed an issue that when **operation=list** was selected and more than one data set entry was fetched, only one
  data set was returned, now the complete list is returned.

- ``zos_copy``

    - Fixed an issue that when copying an aliased executable from a data set to a non-existent data set, the destination
      datasets primary and secondary extents would not match the source data set extent sizes.
    - Fixed an issue when performing a copy operation to an existing file, the copied file resulted in having corrupted contents.

- ``zos_job_submit``

    - Fixed an issue that when no **location** is set, the default is not correctly configured to **location=DATA_SET**.
    - Fixed an issue that when a JCL error is encountered, the **ret_code[msg_code]** no longer will contain the multi line marker used to coordinate errors.
    - Fixed an issue that when a response was returned, the property **ret_code[msg_text]** was incorrectly returned over **ret_code[msg_txt]**.
    - Fixed an issue that when JCL contained **TYPRUN=SCAN**, the module would fail. The module no longer fails and an appropriate message and response is returned.
    - Fixed an issue that when JCL contained either **TYPRUN=COPY**, **TYPRUN=HOLD**, or **TYPRUN=JCLHOLD** an improper message was returned and the job submission failed.
      Now the job will fail under the condition that the module has exceeded its wait time and return a proper message.
    - Fixed an issue where when option **wait_time_s** was used, the duration would be approximately 5 seconds longer than what was reported in the duration.
      Now the duration is from when the job is submitted to when the module reads the job output.

- ``zos_job_output`` - Fixed an issue that when using a job ID with less than 8 characters, would result in a traceback. The fix
  supports shorter job IDs as well as the use of wildcards.

- ``zos_job_query`` - Fixed an issue that when using a job ID with less than 8 characters, would result in a traceback. The fix
  supports shorter job IDs as well as the use of wildcards.

- ``zos_unarchive``

    - Fixed an issue that when using a local file with the USS format option, the module would fail to send the archive to the managed node.
    - Fixed an issue that occurred when unarchiving USS files, the module would leave temporary files behind on the managed node.

- ``module_utils``

    - ``job.py`` - Improved exception handling and added a message inside the **content** of the **ddname** when a non-printable
      character (character that can not be converted to UTF-8) is encountered.
    - ``data_set.py`` - Fixed an issue that when a volser name less than 6 characters was encountered, the volser name was padded with hyphens to have length 6.


Known Issues
------------

Several modules have reported UTF-8 decoding errors when interacting with results that contain non-printable UTF-8 characters in the response.

- This occurs when a module receives content that does not correspond to a UTF-8 value. These include modules ``zos_job_submit``, ``zos_job_output``,
  ``zos_operator_action_query``` but are not limited to this list. This has been addressed in this release and corrected with **ZOAU version 1.2.5.6**.
- If the appropriate level of ZOAU can not be installed, some options are to:

  - Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
  - Ignore module errors by using  **ignore_errors:true** for a specific playbook task.
  - If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a registered variable to extract the
    job ID with a regular expression. Then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.
  - If the error is the result of a batch job, set option **return_output** to false so that no DDs are read which could contain the non-printable UTF-8 characters.

An undocumented option **size** was defined in module **zos_data_set**, this has been removed to satisfy collection certification, use the intended
and documented **space_primary** option.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Version 1.8.0
=============

New Modules
-----------

- ``zos_script`` - Run scripts in z/OS

Minor Changes
-------------
- ``zos_archive``

    - Add validation into path joins to detect unauthorized path traversals.
    - Enhanced test cases to use test lines the same length of the record length.
- ``zos_copy``

    - Add validation into path joins to detect unauthorized path traversals.
    - Add new option `force_lock` that can copy into data sets that are already in use by other processes (DISP=SHR). User needs to use with caution because this is subject to race conditions and can lead to data loss.
    - Includes a new option `executable` that enables copying of executables such as load modules or program objects to both USS and partitioned data sets. When the `dest` option contains a non-existent data set, `zos_copy` will create a data set with the appropriate attributes for an executable.
    - Introduces a new option 'aliases' to enable preservation of member aliases when copying data to partitioned data sets (PDS) destinations from USS or other PDS sources. Copying aliases of text based members to/from USS is not supported.
    - Add support in zos_copy for text files and data sets containing ASA control characters.
- ``zos_fetch`` - Add validation into path joins to detect unauthorized path traversals.
- ``zos_job_submit``

    - Change action plugin call from copy to zos_copy.
    - Previous code did not return output, but still requested job data from the target system. This changes to honor `return_output=false` by not querying the job dd segments at all.
- ``zos_operator`` - Changed system to call `wait=true` parameter to zoau call. Requires zoau 1.2.5 or later.
- ``zos_operator_action_query`` - Add a max delay of 5 seconds on each part of the operator_action_query. Requires zoau 1.2.5 or later.
- ``zos_unarchive``

    - Add validation into path joins to detect unauthorized path traversals.
    - Enhanced test cases to use test lines the same length of the record length.
- ``module_utils/template`` - Add validation into path joins to detect unauthorized path traversals.
- ``zos_tso_command`` - Add example for executing explicitly a REXX script from a data set.
- ``zos_script`` - Add support for remote_tmp from the Ansible configuration to setup where temporary files will be created, replacing the module option tmp_path.

Bugfixes
--------

- ``zos_copy``

    - Update option to include `LIBRARY` as dest_dataset/suboption value. Documentation updated to reflect this change.
    - When copying an executable data set from controller to managed node, copy operation failed with an encoding error. Fix now avoids encoding when `executable` option is selected.
    - When copying an executable data set with aliases and destination did not exist, destination data set was created with wrong attributes. Fix now creates destination data set with the same attributes as the source.
    - When performing a copy operation to an existing file, the copied file resulted in having corrupted contents. Fix now implements a workaround to not use the specific copy routine that corrupts the file contents.
- ``zos_job_submit``

    - Temporary files were created in tmp directory. Fix now ensures the deletion of files every time the module run.
    - The last line of the jcl was missing in the input. Fix now ensures the presence of the full input in job_submit.
- ``zos_lineinfile`` - A duplicate entry was made even if line was already present in the target file. Fix now prevents a duplicate entry if the line already exists in the target file.
- ``zos_operator``

    - The last line of the operator was missing in the response of the module. The fix now ensures the presence of the full output of the operator.
    - The module was ignoring the wait time argument. The module now passes the wait time argument to ZOAU.
- ``zos_operator_action_query`` - The module was ignoring the wait time argument. The module now passes the wait time argument to ZOAU.
- ``zos_unarchive`` - When zos_unarchive fails during unpack either with xmit or terse it does not clean the temporary data sets created. Fix now removes the temporary data sets.

Known Issues
------------

Several modules have reported UTF-8 decoding errors when interacting with results that contain non-printable UTF-8 characters in the response.

This occurs when a module receives content that does not correspond to a UTF-8 value. These include modules ``zos_job_submit``, ``zos_job_output``,
``zos_operator_action_query``` but are not limited to this list. This will be addressed in **ibm_zos_core** version 1.10.0-beta.1. Each case is
unique, some options to work around the error are below.

- Specify that the ASA assembler option be enabled to instruct the assembler to use ANSI control characters instead of machine code control characters.
- Add **ignore_errors:true** to the playbook task so the task error will not fail the playbook.
- If the error is resulting from a batch job, add **ignore_errors:true** to the task and capture the output into a variable and extract the job ID with
  a regular expression and then use ``zos_job_output`` to display the DD without the non-printable character such as the DD **JESMSGLG**.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Version 1.7.0
=============

New Modules
-----------

- ``zos_archive`` - archive files, data sets and extend archives on z/OS. Formats include, *bz2*, *gz*, *tar*, *zip*, *terse*, *xmit* and *pax*.
- ``zos_unarchive`` - unarchive files and data sets on z/OS. Formats include, *bz2*, *gz*, *tar*, *zip*, *terse*, *xmit* and *pax*.

Major Changes
-------------

-- ``zos_copy`` and ``zos_job_submit`` - supports Jinja2 templating which is essential for handling tasks that require advanced file modifications such as JCL.

Minor Changes
-------------
- ``zos_copy``

      - displays the data set attributes when the destination does not exist and was created by the module.
      - reverts the logic that would automatically create backups in the event of a module failure leaving it up to the user to decide if a backup is needed.
- ``zos_data_set`` - supports record format *F* (fixed) where one physical block on disk is one logical record and all the blocks and records are the same size.
- ``zos_job_output`` - displays job information *asid*, *creation date*, *creation time*, *job class*, *priority*, *queue position*, *service class* and conditionally *program name* (when ZOAU is v1.2.4 or later).
- ``zos_job_query``

      - displays job information *asid*, *creation date*, *creation time*, *job class*, *priority*, *queue position*, *service class* and conditionally *program name* (when ZOAU is v 1.2.4 or later).
      - removes unnecessary queries to find DDs improving the modules performance.
- ``zos_job_submit`` - displays job information *asid*, *creation date*, *creation time*, *job class*, *priority*, *queue position*, *service class* and conditionally *program name* (when ZOAU is v1.2.4 or later).
- ``zos_archive``

      - When XMIT encounters a space error because of the destination (dest) or log data set has reached capacity, the module raises an appropriate error message.
      - When the destination (dest) data set space is not provided, then the module computes it using the source (src) given the pattern provided.

- ``zos_unarchive``

      - When copying to the z/OS managed node (remote_src) results in a failure, a proper error message is displayed
      - When copying to the z/OS managed node (remote_src), if the option *primary_space* is not defined, then it is defaulted to 5M.

Bugfixes
--------
- ``zos_data_set`` - fixes occasionally occurring orphaned VSAM cluster components such as INDEX when *present=absent*.
- ``zos_fetch`` - fixes the warning that appeared about the use of *_play_context.verbosity*.
- ``zos_copy``

      - fixes the warning that appeared about the use of *_play_context.verbosity*.
      - fixes an issue where subdirectories would not be encoded.
      - fixes an issue where when mode was set, the mode was not applied to existing directories and files.
      - displays a error message when copying into a data set that is being accessed by another process and no longer returns with *changed=true*.

- ``zos_job_output`` - displays an appropriate error message for a job is not found in the spool.
- ``zos_operator`` - fixes the false reports that a command failed when keywords such as *error* were seen, the module now acts as a passthrough.
- ``zos_archive`` - Module did not return the proper src state after archiving. Fix now displays the status of the src after the operation.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Version 1.6.0
=============

New Modules
-----------

- ``zos_volume_init`` - Can initialize volumes or minidisks on target z/OS systems which includes creating a volume label and an entry into the volume table of contents (VTOC).

Minor Changes
-------------

- ``zos_blockinfile`` - Adds an enhancement to allow double quotes within a block.
- ``zos_copy``

      - Updates the behavior of the `mode` option so that permissions are applied to existing directories and contents.
      - Adds an enhancement to option `restore_backup` to track modified members in a data set in the event of an error, restoring them to their previous state without reallocating the data set.
- ``zos_data_set`` - Adds a new option named *force* to enable deletion of a data member in a PDSE that is simultaneously in use by others.
- ``zos_job_query`` - Enables embedded positional wild card placement throughout *job_name* and *job_id* parameters.
- ``zos_lineinfile`` - Adds a new option named *force* to enable modification of a data member in a data set that is simultaneously in use by others.
- ``zos_tso_command`` - Adds a new option named *max_rc* to enable non-zero return codes lower than the specified maximum return as succeeded.
- ``module_utils``

      - job - Adds support for positional wild card placement for `job_name`` and `job_id`.
      - Adds support for import *common.text.converters* over the deprecated *_text* import.

Bugfixes
--------

- ``zos_copy``

      - Fixes a bug where files not encoded in IBM-1047 would trigger an error while computing the record length for a new destination dataset.
      - Fixes a bug where the module would change the mode for a directory when copying in the contents of another directory.
      - Fixes a bug where the incorrect encoding would be used during normalization, particularly when processing newlines in files.
      - Fixes a bug where binary files were not excluded when normalizing data to remove newlines.
      - Fixes a bug where a *_play_context.verbosity* deprecation warning would appear.
- ``zos_fetch`` - Fixes a bug where a *_play_context.verbosity* deprecation warning would appear.
- ``zos_encode`` - Fixes a bug where converted files were not tagged with the new code set afterwards.
- ``zos_find`` - Fixes a bug where the module would stop searching and exit after the first value in a list was not found.
- ``zos_lineinfile``

      - Removes use of Python f-string to ensure support for Python 2.7 on the controller.
      - Fixes a bug where an incorrect error message would be raised when a USS source was not found.
- ``module_utils``

      - data_set - Fixes an failure caused by cataloging a VSAM data set when the data set is not cataloged.
- ``zos_data_set`` - Fixes a bug that will leave VSAM data set cluster components behind when instructed to delete the data set (`present=absent`).
- ``zos_gather_facts`` - Fixes a bug that prevented the module from executing with newer versions of ZOAU.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Version 1.5.0
=============

New Modules
-----------

- ``zos_gather_facts`` - can retrieve variables from target z/OS systems that are then available to playbooks through the ansible_facts dictionary and managed using filters.

Major Changes
-------------

- ``ibm_zos_core`` - Updates the entire collection in that the collection no longer depends on the managed node having installed System Display and Search Facility (SDSF). Remove SDSF dependency from ibm_zos_core collection.

Minor Changes
-------------

- ``zos_apf`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_blockinfile``

      - fixes a bug when using double quotes in the block text of the module. When double quotes appeared in block text, the module would error differently depending on the usage of option insertafter. Examples of this error have return code 1 or 16 along with message "ZOAU dmod return content is NOT in json format" and a varying stderr.
      - updates the module with a new option named force. This allows for a user to specify that the data set can be shared with others during an update which results in the data set you are updating to be simultaneously updated by others.
      - updates the module with a new option named indentation. This allows for a user to specify a number of spaces to prepend to the content before being inserted into the destination.
      - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_copy`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_data_set`` - Ensures that temporary datasets created by zos_data_set use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_encode`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_fetch`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_job_output`` - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs.
- ``zos_job_query``

      - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs.
      - was updated to use the jobs module utility.
- ``zos_job_submit``

      - architecture changed such that the entire modules execution time now is captured in the duration time which includes job submission and log collection. If a job does not return by the default 10 sec 'wait_time_s' value, it can be increased up to 86400 seconds.
      - behavior changed when a volume is defined in the module options such that it will catalog the data set if it is not cataloged and submit the job. In the past, the function did not catalog the data set and instead performed I/O operations and then submitted the job. This behavior aligns to other module behaviors and reduces the possibility to encounter a permissions issue.
- ``zos_lineinfile`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_mount`` - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
- ``zos_mvs_raw``

      - Ensures that temporary datasets created by DD Statements use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
      - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults.
      - updated module documentation on how to use a multi-line string when using the content field option as well as an example.
- ``zos_operator``

      - added in the response the cmd result.
      - added in the response the elapsed time.
      - added in the response the wait_time_s set.
      - deprecated the wait option, not needed with wait_time_s minor_changes.
      - was updated to remove the usage of REXX and replaced with ZOAU python APIs. This reduces code replication and it removes the need for REXX interpretation which increases performance.


Bugfixes
--------

- ``zos_copy``

      - fixes a bug such that the module fails when copying files from a directory needing also to be encoded. The failure would also delete the `src` which was not desirable behavior. Fixes deletion of src on encoding error.
      - module was updated to correct a bug in the case when the destination (dest) is a PDSE and the source (src) is a Unix Systems File (USS). The module would fail in determining if the PDSE actually existed and try to create it when it already existed resulting in an error that would prevent the module from correctly executing.
      - fixes a bug where the computed record length for a new destination dataset would include newline characters.
      - fixes a bug where if a destination has accented characters in its content, the module would fail when trying to determine if it is empty.
      - fixes a bug where copying a member from a loadlib to another loadlib fails.
      - fixed wrongful creation of destination backups when module option `force` is true, creating emergency backups meant to restore the system to its initial state in case of a module failure only when force is false.
      - copy failed from a loadlib member to another loadlib member. Fix now looks for an error in stdout while copying to perform a fallback copy for executables.
      - fixes a bug where the module would change the mode for a directory when copying into it the contents of another.
      - fixes a bug where source files not encoded in IBM-1047 would trigger an encoding error while computing the record length for a new destination dataset.
      - fixes a bug where the code for fixing an issue with newlines in files would use the wrong encoding for normalization.
- ``zos_data_set``

      - Fixes a bug such that the module will delete a catalogued data set over an uncatalogued data set even though the volume is provided for the uncataloged data set. This is unexpected behavior and does not align to documentation; correct behavior is that when a volume is provided that is the first place the module should look for the data set, whether or not it is cataloged.
      - fixes a bug where the default record format FB was actually never enforced and when enforced it would cause VSAM creation to fail with a Dynalloc failure. This also cleans up some of the options that are set by default when they have no bearing for batch.
- ``zos_fetch`` - Updates the modules behavior when fetching VSAM data sets such that the maximum record length is now determined when creating a temporary data set to copy the VSAM data into and a variable-length (VB) data set is used.
- ``zos_job_output`` - fixes a bug that returned all ddname's when a specific ddnamae was provided. Now a specific ddname can be returned and all others ignored.
- ``zos_job_query`` - was updated to correct a boolean condition that always evaluated to "CANCELLED".
- ``zos_job_submit``

      - fixes the issue when `wait_time_s` was set to 0 that would result in a `type` error and the response would be a stack trace.
      - fixes the issue when a job encounters a security exception, no job log would would result in the response.
      - fixes the issue when a job is configured for a syntax check using TYPRUN=SCAN that it would wait the full duration set by `wait_time_s` to return a response.
      - fixes the issue when a job is configured for a syntax check using TYPRUN=SCAN that no job log would result in the response.
      - fixes the issue when a job is purged by the system that the response would result in a stack trace.
      - fixes the issue when invalid JCL syntax is submitted such that the response would result in a stack trace.
      - fixes the issue when resources (data sets) identified in JCL did not exist such that a response would result in a stack trace.
      - fixes the issue where the response did not include the job log when a non-zero return code would occur.
- ``zos_mount`` - fixed option `tag_ccsid` to correctly allow for type int.
- ``zos_mvs_raw`` - module was updated to correct a bug when no DD statements were provided. The module when no option was provided for `dds` would error, a default was provided to correct this behavior.
- ``zos_operator``

      - fixed case sensitive error checks, invalid, error & unidentifiable.
      - fixed such that specifying wait_time_s would throw an error.
      - fixed the wait_time_s to default to 1 second.
      - was updated to correct missing verbosity content when the option verbose was set to True. zos_operator - was updated to correct the trailing lines that would appear in the result content.
      - fixed incorrect example descriptions and updated the doc to highlight the deprecated option `wait`.

Deprecated Features
-------------------

- ``zos_encode`` - deprecates the module options `from_encoding` and `to_encoding` to use suboptions `from` and `to` in order to remain consistent with all other modules.
- ``zos_job_submit`` - Response 'message' property has been deprecated, all responses are now in response property 'msg'.
- ``zos_job_submit`` - The 'wait' option has been deprecated because using option 'wait_time_s' implies the job is going to wait.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

.. .............................................................................
.. Global Links
.. .............................................................................
.. _GitHub:
   https://github.com/ansible-collections/ibm_zos_core
.. _Galaxy:
   https://galaxy.ansible.com/ibm/ibm_zos_core
.. _Ansible Automation Platform:
   https://www.ansible.com/products/automation-hub
.. _IBM Open Enterprise SDK for Python:
   https://www.ibm.com/products/open-enterprise-python-zos
.. _3.8:
   https://www.ibm.com/docs/en/python-zos/3.8
.. _3.9:
   https://www.ibm.com/docs/en/python-zos/3.9
.. _3.10:
   https://www.ibm.com/docs/en/python-zos/3.10
.. _3.11:
   https://www.ibm.com/docs/en/python-zos/3.11
.. _3.12:
   https://www.ibm.com/docs/en/python-zos/3.12
.. _Z Open Automation Utilities:
   https://www.ibm.com/docs/en/zoau/latest
.. _Z Open Automation Utilities 1.1.0:
   https://www.ibm.com/docs/en/zoau/1.1.x
.. _Z Open Automation Utilities 1.1.1:
   https://www.ibm.com/docs/en/zoau/1.1.1
.. _Z Open Automation Utilities 1.2.2:
   https://www.ibm.com/docs/en/zoau/1.2.x
.. _Z Open Automation Utilities 1.2.3:
   https://www.ibm.com/docs/en/zoau/1.2.x
.. _Z Open Automation Utilities 1.2.4:
   https://www.ibm.com/docs/en/zoau/1.2.x
.. _Z Open Automation Utilities 1.2.5:
   https://www.ibm.com/docs/en/zoau/1.2.x
.. _Z Open Automation Utilities 1.3.0:
   https://www.ibm.com/docs/en/zoau/1.3.x
.. _z/OS® shell:
   https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm
.. _z/OS®:
   https://www.ibm.com/docs/en/zos
.. _z/OS V2R3:
   https://www.ibm.com/support/knowledgecenter/SSLTBW_2.3.0/com.ibm.zos.v2r3/en/homepage.html
.. _z/OS V2R4:
   https://www.ibm.com/docs/en/zos/2.4.0
.. _z/OS Version:
   https://www.ibm.com/docs/en/zos
.. _FAQs:
   https://ibm.github.io/z_ansible_collections_doc/faqs/faqs.html

.. .............................................................................
.. Playbook Links
.. .............................................................................
.. _playbook repository:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/README.md
.. _synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/program_authorization/git_apf
.. _copy, sort and fetch data sets on z/OS playbook:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/data_transfer/copy_sort_fetch
.. _manage z/OS Users Using Ansible:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/user_management/add_remove_user
.. _zos_operator_basics.yaml:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/zos_concepts/zos_operator/zos_operator_basics/zos_operator_basics.yaml
.. _SMP/E Playbooks:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/software_management

.. .............................................................................
.. Configuration Links
.. .............................................................................
.. _playbook configuration:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/configuration_guide.md
.. _configure Python and ZOAU Installation:
   https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_administration/host_setup
.. _inventory:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/configuration_guide.md#inventory
.. _variables:
   https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/configuration_guide.md#variables
.. _support tickets:
   https://github.com/IBM/z_ansible_collections_samples/issues
.. _configured IBM Open Enterprise Python on z/OS:
   https://www.ibm.com/support/knowledgecenter/SSCH7P_3.8.0/install.html

.. .............................................................................
.. Blog Links
.. .............................................................................
.. _Running Batch Jobs on z/OS using Ansible:
   https://community.ibm.com/community/user/ibmz-and-linuxone/blogs/asif-mahmud1/2020/08/04/how-to-run-batch-jobs-on-zos-without-jcl-using-ans
.. _z/OS User Management With Ansible:
   https://community.ibm.com/community/user/ibmz-and-linuxone/blogs/blake-becker1/2020/09/03/zos-user-management-with-ansible
