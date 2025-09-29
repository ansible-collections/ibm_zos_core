.. ...........................................................................
.. © Copyright IBM Corporation 2020, 2025                                    .
.. ...........................................................................

========
Releases
========

Version 1.15.0
==============

Minor Changes
-------------

- ``zos_archive``

   - Adds support for encoding before archiving files.
   - Adds support for skipping encoding in archive module. This allows users to skip encoding for certain files before archiving them.
   - Adds support for reverting the encoding of a source's files after archiving them.

- ``zos_copy``

   - Adds new option `identical_gdg_copy` in the module. This allows copying GDG generations from a source base to a destination base while preserving generation data set absolute names when the destination base does not exist prior to the copy.
   - Adds support of using alias names in src and dest parameters for PS, PDS and PDSE data sets.
   - Added support for british pound character usage in file content and data set names for both source and destination when copying.

- ``zos_fetch`` - Updated the documentation to correctly state what the default behavior of the module is.
- ``zos_find``

   - Adds functionality to find migrated data sets.
   - Adds functionality to find different types of data sets at the same time.

- ``zos_job_output`` - Adds new fields cpu_time, origin_node and execution_node to response.
- ``zos_job_query`` - Adds new fields cpu_time, origin_node and execution_node to response.
- ``zos_job_submit`` - Adds new fields cpu_time, origin_node and execution_node to response.

- ``zos_mvs_raw``

   - Before this addition, you could not put anything in columns 1 or 2, were reserved for JCL processing. Change now allows add reserved_cols option and validate that the module get access to modify dd_content option base on the value, if not retain the previous behavior or work.
   - Adds support for volume data definition.

- ``zos_stat``

   - Added support to recall migrated data sets and return its attributes.
   - Adds new fields that describe the type of the resource that was queried. These new fields are ``isfile``, ``isdataset``, ``isaggregate`` and ``isgdg``.
   - Adds support to query data sets using their aliases.
   - Module now returns whether the resource queried exists on the managed node with the `exists` field inside `stat`.

- ``zos_unarchive`` - Added encoding support in the zos_unarchive module. This allows users to encode the files after unarchiving them.

Bugfixes
--------
- ``zos_backup_restore`` - Return value ``backup_name`` was empty upon successful result. Fix now returns ``backup_name`` populated.
- ``zos_data_set`` - Attempting to create a data set with the same name on a different volume did not work, nor did it report a failure. The fix now informs the user that if the data set is cataloged on a different volume, it needs to be uncataloged before using the data set module to create a new data set on a different volume.
- ``zos_fetch`` - Previously, the use of `become` would result in a permissions error  while trying to fetch a data set or a member. Fix now allows a user to escalate privileges when fetching resources.
- ``zos_lineinfile``

   - Return values ``return_content`` and ``backup_name`` were not always being returned. Fix now ensure that these values are always present in the module's response.
   - The module would report a false negative when certain special characters where present in the `line` option. Fix now reports the successful operation.

- ``zos_mount`` - FSUMF168 return in stderror means that the mount dataset wouldn't resolve. While this shows a catalog or volume issue, it should not impact our search for an existing mount. Added handling to the df call, so that FSUMF168 are ignored.


New Modules
-----------

- ibm.ibm_zos_core.zos_replace - Replace all instances of a pattern within a file or data set.

Availability
------------
* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_copy`` - Copying from a sequential data set that is in use will result in a false positive and destination data set will be empty. The same is true when ``type=gdg`` and source GDS is a sequential data set in use.


Version 1.14.1
==============

Bugfixes
--------

- zos_copy - Previously, if the Ansible user was not a superuser copying a file into the managed node resulted in a permission denied error. Fix now sets the correct permissions for the Ansible user for copying to the remote.
- zos_job_submit - Previously, if the Ansible user was not a superuser copying a file into the managed node resulted in a permission denied error. Fix now sets the correct permissions for the Ansible user for copying to the remote.
- zos_script - Previously, if the Ansible user was not a superuser copying a file into the managed node resulted in a permission denied error. Fix now sets the correct permissions for the Ansible user for copying to the remote.
- zos_unarchive - Previously, if the Ansible user was not a superuser copying a file into the managed node resulted in a permission denied error. Fix now sets the correct permissions for the Ansible user for copying to the remote.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_copy`` - Copying from a sequential data set that is in use will result in a false positive and destination data set will be empty. The same is true when ``type=gdg`` and source GDS is a sequential data set in use.


Version 1.14.0
==============

Minor Changes
-------------

- ``zos_copy``

   - Adds ``large`` as a choice for ``type`` in ``dest_data_set``.
   - Adds logging of Jinja rendered template content when `use_template` is true and verbosity level `-vvv` is used.
   - Adds support for copying in asynchronous mode inside playbooks.
   - Removes the need to allow READ access to MVS.MCSOPER.ZOAU to execute the module by changing how the module checks if a data set is locked.
   - Previously, when trying to copy into remote and ansible's default temporary directory was not created before execution the copy task would fail. Fix now creates the temporary directory if possible.

- ``zos_job_output`` - Add execution_time return value in the modules response.
- ``zos_job_query``

   - Add execution_time return value in the modules response.
   - Loads correct bytes size value for dds when using zoau 1.3.4 or later
   - System and Subsystem are now retrieved from JES.

- ``zos_job_submit``

   - Adds logging of Jinja rendered template content when `use_template` is true and verbosity level `-vvv` is used.
   - Add execution_time return value in the modules response.
   - Loads correct bytes size value for dds when using zoau 1.3.4 or later.
   - Previously, the use of `become` would result in a permissions error while trying to execute a job from a local file. Fix now allows a user to escalate privileges when executing a job transferred from the controller node.

- ``zos_script``

   - Adds error message for when remote source does not exist.
   - Adds logging of Jinja rendered template content when `use_template` is true and verbosity level `-vvv` is used.
   - Adds support for running local and remote scripts in asynchronous mode inside playbooks.
   - Support automatic removal of carriage return line breaks [CR, CRLF] when copying local files to USS.

- ``zos_stat`` - Adds support to query data sets using their aliases.
- ``zos_unarchive`` - Adds support for unarchiving files in asynchronous mode inside playbooks.
- ``zos_zfs_resize`` - Adds validations for trace destination dataset used for trace verbose.

Bugfixes
--------

- ``zos_apf`` - When trying to add a library into the APF list that was already added, the module would fail. Fix now will not fail the module, and will inform the user that the library is already on the APF list.
- ``zos_copy``

   - Previously, if the dataset name included special characters such as $, validation would fail when force_lock was false. This has been changed to allow the use of special characters when force_lock option is false.    - When ``asa_text`` was set to true at the same time as ``force_lock``, a copy would fail saying the destination was already in use. Fix now opens destination data sets up with disposition SHR when ``force_lock`` and ``asa_text`` are set to true.
   - the carriage return characters were being removed from only first 1024 bytes of a file. Now fixed that issue to support removal of the carriage return characters from the complete file content if the file size is more than 1024 bytes.

- ``zos_data_set``

   - Module would fail when trying to delete a non-existent Generation Data Group. Fix now provides a successful response with `changed=false`.
   - Module would fail with TypeError when trying to replace an existing GDG. Fix now allows to replacing a GDG.

- ``zos_job_output`` - When searching for a job name, module performed a '*' (find all), then filtered the results. Fix now asks for specific job name, making the return faster and more precise.
- ``zos_job_query`` - When searching for a job name, module performed a '*' (find all), then filtered the results. Fix now asks for specific job name, making the return faster and more precise.
- ``zos_job_submit`` - When searching for a job name, module performed a '*' (find all), then filtered the results. Fix now asks for specific job name, making the return faster and more precise.
- ``zos_mount`` - Module failed when using persistent option with a data set that contains non UTF-8 characters. Fix now can use a data set with non UTF-8 characters as data_store.

New Modules
-----------

- ibm.ibm_zos_core.zos_stat - Retrieve facts from MVS data sets, USS files, aggregates and generation data groups.

Availability
------------

* `Ansible Automation Platform`_
* `Galaxy`_
* `GitHub`_

Known Issues
------------
- ``zos_copy`` - Copying from a sequential data set that is in use will result in a false positive and destination data set will be empty. The same is true when ``type=gdg`` and source GDS is a sequential data set in use.
- ``zos_copy`` - When elevating privileges using the `become` keyword, the module would attempt to connect using the elevated user id, if the user cannot connect to the managed node through ssh the module would fail.
- ``zos_job_submit`` - When elevating privileges using the `become` keyword, the module would attempt to connect using the elevated user id, if the user cannot connect to the managed node through ssh the module would fail.
- ``zos_script`` - When elevating privileges using the `become` keyword, the module would attempt to connect using the elevated user id, if the user cannot connect to the managed node through ssh the module would fail.
- ``zos_unarchive`` - When elevating privileges using the `become` keyword, the module would attempt to connect using the elevated user id, if the user cannot connect to the managed node through ssh the module would fail.
- ``zos_fetch`` - When elevating privileges using the `become` keyword, the module would attempt to connect using the elevated user id, if the user cannot connect to the managed node through ssh the module would fail.



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
