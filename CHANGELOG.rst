==============================
ibm.ibm_zos_core Release Notes
==============================

.. contents:: Topics


v1.7.0-beta.2
=============

Release Summary
---------------

Release Date: '2023-08-21'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__

Minor Changes
-------------

- zos_archive - If destination data set space is not provided then the module computes it based on the src list and/or expanded src list based on pattern provided. (https://github.com/ansible-collections/ibm_zos_core/pull/930).
- zos_archive - When xmit faces a space error in xmit operation because of dest or log data set are filled raises an appropriate error hint. (https://github.com/ansible-collections/ibm_zos_core/pull/930).
- zos_unarchive - When copying to remote fails now a proper error message is displayed. (https://github.com/ansible-collections/ibm_zos_core/pull/930).
- zos_unarchive - When copying to remote if space_primary is not defined, then is defaulted to 5M. (https://github.com/ansible-collections/ibm_zos_core/pull/930).

Bugfixes
--------

- zos_archive - Module did not return the proper src state after archiving. Fix now displays the status of the src after the operation. (https://github.com/ansible-collections/ibm_zos_core/pull/930).

v1.7.0-beta.1
=============

Release Summary
---------------

Release Date: '2023-07-26'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__

Major Changes
-------------

- zos_copy - Previously, backups were taken when force was set to false; whether or not a user specified this operation which caused allocation issues with space and permissions. This removes the automatic backup performed and reverts to the original logic in that backups must be initiated by the user. (https://github.com/ansible-collections/ibm_zos_core/pull/896)

Minor Changes
-------------

- Add support for Jinja2 templates in zos_copy and zos_job_submit when using local source files. (https://github.com/ansible-collections/ibm_zos_core/pull/667)
- zos_copy - Adds block_size, record_format, record_length, space_primary, space_secondary, space_type and type in the return output when the destination data set does not exist and has to be created by the module. (https://github.com/ansible-collections/ibm_zos_core/pull/773)
- zos_data_set - record format = 'F' has been added to support 'fixed' block records. This allows records that can use the entire block. (https://github.com/ansible-collections/ibm_zos_core/pull/821)
- zos_job_output - zoau added 'program_name' to their field output starting with v1.2.4.  This enhancement checks for that version and passes the extra column through. (https://github.com/ansible-collections/ibm_zos_core/pull/841)
- zos_job_query - Adds new fields job_class, svc_class, priority, asid, creation_datetime, and queue_position to the return output when querying or submitting a job. Available when using ZOAU v1.2.3 or greater. (https://github.com/ansible-collections/ibm_zos_core/pull/778)
- zos_job_query - unnecessary calls were made to find a jobs DDs that incurred unnecessary overhead. This change removes those resulting in a performance increase in job related queries. (https://github.com/ansible-collections/ibm_zos_core/pull/911)
- zos_job_query - zoau added 'program_name' to their field output starting with v1.2.4.  This enhancement checks for that version and passes the extra column through. (https://github.com/ansible-collections/ibm_zos_core/pull/841)
- zos_job_submit - zoau added 'program_name' to their field output starting with v1.2.4.  This enhancement checks for that version and passes the extra column through. (https://github.com/ansible-collections/ibm_zos_core/pull/841)

Bugfixes
--------

- module_utils - data_set.py - Reported a failure caused when cataloging a VSAM data set. Fix now corrects how VSAM data sets are cataloged. (https://github.com/ansible-collections/ibm_zos_core/pull/791).
- zos_blockinfile - Test case generate a data set that was not correctly removed. Changes delete the correct data set not only member. (https://github.com/ansible-collections/ibm_zos_core/pull/840)
- zos_copy - Module returned the dynamic values created with the same dataset type and record format. Fix validate the correct dataset type and record format of target created. (https://github.com/ansible-collections/ibm_zos_core/pull/824)
- zos_copy - Reported a false positive such that the response would have `changed=true` when copying from a source (src) or destination (dest) data set that was in use (DISP=SHR). This change now displays an appropriate error message and returns `changed=false`. (https://github.com/ansible-collections/ibm_zos_core/pull/794).
- zos_copy - Reported a warning about the use of _play_context.verbosity.This change corrects the module action to prevent the warning message. (https://github.com/ansible-collections/ibm_zos_core/pull/806).
- zos_copy - Test case for recursive encoding directories reported a UTF-8 failure. This change ensures proper test coverage for nested directories and file permissions. (https://github.com/ansible-collections/ibm_zos_core/pull/806).
- zos_copy - Zos_copy did not encode inner content inside subdirectories once the source was copied to the destination. Fix now encodes all content in a source directory, including subdirectories. (https://github.com/ansible-collections/ibm_zos_core/pull/772).
- zos_copy - kept permissions on target directory when copy overwrote files. The fix now set permissions when mode is given. (https://github.com/ansible-collections/ibm_zos_core/pull/795)
- zos_data_set - Reported a failure caused when `present=absent` for a VSAM data set leaving behind cluster components. Fix introduces a new logical flow that will evaluate the volumes, compare it to the provided value and if necessary catalog and delete. (https://github.com/ansible-collections/ibm_zos_core/pull/791).
- zos_fetch - Reported a warning about the use of _play_context.verbosity.This change corrects the module action to prevent the warning message. (https://github.com/ansible-collections/ibm_zos_core/pull/806).
- zos_job_output - Error message did not specify the job not found. Fix now specifies the job_id or job_name being searched to ensure more information is given back to the user. (https://github.com/ansible-collections/ibm_zos_core/pull/747)
- zos_operator - Reported a failure caused by unrelated error response. Fix now gives a transparent response of the operator to avoid false negatives. (https://github.com/ansible-collections/ibm_zos_core/pull/762).

New Modules
-----------

- ibm.ibm_zos_core.zos_archive - Archive files and data sets on z/OS.
- ibm.ibm_zos_core.zos_unarchive - Unarchive files and data sets in z/OS.

v1.6.0
======

Release Summary
---------------

Release Date: '2023-06-23'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__

Major Changes
-------------

- zos_volume_init - Introduces new module to handle volume (or minidisk) initialization. (https://github.com/ansible-collections/ibm_zos_core/pull/654)

Minor Changes
-------------

- Updated the text converter import from "from ansible.module_utils._text" to "from ansible.module_utils.common.text.converters" to remove warning".. warn Use ansible.module_utils.common.text.converters instead.". (https://github.com/ansible-collections/ibm_zos_core/pull/602)
- module_utils - job.py utility did not support positional wiled card placement, this enhancement uses `fnmatch` logic to support wild cards.
- zos_copy - Fixed a bug where the module would change the mode for a directory when copying into it the contents of another. (https://github.com/ansible-collections/ibm_zos_core/pull/723)
- zos_copy - was enhanced to keep track of modified members in a destination dataset, restoring them to their previous state in case of a failure. (https://github.com/ansible-collections/ibm_zos_core/pull/551)
- zos_data_set - add force parameter to enable member delete while pdse is in use (https://github.com/ansible-collections/ibm_zos_core/pull/718).
- zos_job_query - ansible module does not support positional wild card placement for `job_name1 or `job_id`. This enhancement allows embedded wildcards throughout the `job_name` and `job_id`. (https://github.com/ansible-collections/ibm_zos_core/pull/721)
- zos_lineinfile - would access data sets with exclusive access so no other task can read the data, this enhancement allows for a data set to be opened with a disposition set to share so that other tasks can access the data when option `force` is set to `true`. (https://github.com/ansible-collections/ibm_zos_core/pull/731)
- zos_tso_command - was enhanced to accept `max_rc` as an option. This option allows a non-zero return code to succeed as a valid return code. (https://github.com/ansible-collections/ibm_zos_core/pull/666)

Bugfixes
--------

- Fixed wrong error message when a USS source is not found, aligning with a similar error message from zos_blockinfile "{src} does not exist".
- module_utils - data_set.py - Reported a failure caused when cataloging a VSAM data set. Fix now corrects how VSAM data sets are cataloged. (https://github.com/ansible-collections/ibm_zos_core/pull/816).
- zos_blockinfile - was unable to use double quotes which prevented some use cases and did not display an approriate message. The fix now allows for double quotes to be used with the module. (https://github.com/ansible-collections/ibm_zos_core/pull/680)
- zos_copy - Encoding normalization used to handle newlines in text files was applied to binary files too. Fix makes sure that binary files bypass this normalization. (https://github.com/ansible-collections/ibm_zos_core/pull/810)
- zos_copy - Fixes a bug where files not encoded in IBM-1047 would trigger an error while computing the record length for a new destination dataset. Issue 664. (https://github.com/ansible-collections/ibm_zos_core/pull/743)
- zos_copy - Fixes a bug where the code for fixing an issue with newlines in files (issue 599) would use the wrong encoding for normalization. Issue 678. (https://github.com/ansible-collections/ibm_zos_core/pull/743)
- zos_copy - Reported a warning about the use of _play_context.verbosity.This change corrects the module action to prevent the warning message. (https://github.com/ansible-collections/ibm_zos_core/pull/814).
- zos_copy - kept permissions on target directory when copy overwrote files. The fix now set permissions when mode is given. (https://github.com/ansible-collections/ibm_zos_core/pull/790)
- zos_data_set - Reported a failure caused when `present=absent` for a VSAM data set leaving behind cluster components. Fix introduces a new logical flow that will evaluate the volumes, compare it to the provided value and if necessary catalog and delete. (https://github.com/ansible-collections/ibm_zos_core/pull/816).
- zos_encode - fixes a bug where converted files were not tagged afterwards with the new code set. (https://github.com/ansible-collections/ibm_zos_core/pull/534)
- zos_fetch - Reported a warning about the use of _play_context.verbosity.This change corrects the module action to prevent the warning message. (https://github.com/ansible-collections/ibm_zos_core/pull/814).
- zos_find - fixes a bug where find result values stopped being returned after first value in a list was 'not found'. (https://github.com/ansible-collections/ibm_zos_core/pull/668)
- zos_gather_facts - Fixes an issue in the zoau version checker which prevented the zos_gather_facts module from running with newer versions of ZOAU. (https://github.com/ansible-collections/ibm_zos_core/pull/797)
- zos_lineinfile - Fixed a bug where a Python f-string was used and thus removed to ensure support for Python 2.7 on the controller. (https://github.com/ansible-collections/ibm_zos_core/pull/659)

New Modules
-----------

- ibm.ibm_zos_core.zos_volume_init - Initialize volumes or minidisks.

v1.5.0
======

Release Summary
---------------

Release Date: '2023-04-21'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__

Major Changes
-------------

- ibm_zos_core - Updates the entire collection in that the collection no longer depends on the managed node having installed System Display and Search Facility (SDSF). Remove SDSF dependency from ibm_zos_core collection. (https://github.com/ansible-collections/ibm_zos_core/pull/303).

Minor Changes
-------------

- module utility jobs - was updated to remove the usage of REXX and replaced with ZOAU python APIs. This reduces code replication and it removes the need for REXX interpretation which increases performance. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
- module utils backup - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- module utils dd_statement- updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- module utils encode - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_apf - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_blockinfile - fixes a bug when using double quotes in the block text of the module. When double quotes appeared in block text, the module would error differently depending on the usage of option insertafter. Examples of this error have return code 1 or 16 along with message "ZOAU dmod return content is NOT in json format" and a varying stderr. (https://github.com/ansible-collections/ibm_zos_core/pull/303).
- zos_blockinfile - updates the module with a new option named force. This allows for a user to specify that the data set can be shared with others during an update which results in the data set you are updating to be simultaneously updated by others. (https://github.com/ansible-collections/ibm_zos_core/pull/316).
- zos_blockinfile - updates the module with a new option named indentation. This allows for a user to specify a number of spaces to prepend to the content before being inserted into the destination. (https://github.com/ansible-collections/ibm_zos_core/pull/317).
- zos_blockinfile - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_copy - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_data_set - Ensures that temporary datasets created by zos_data_set use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/491).
- zos_encode - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_fetch - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_gather_facts - is a new module that can discover facts about the managed z/OS target. This module leverages the zinfo utility offered by ZOAU. (https://github.com/ansible-collections/ibm_zos_core/pull/322).
- zos_job_output - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
- zos_job_query - was updated to leverage the latest changes that removes the REXX code by calling the module utility jobs. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
- zos_job_query - was updated to use the jobs module utility. (https://github.com/ansible-collections/ibm_zos_core/pull/312).
- zos_job_submit - The architecture changed such that the entire modules execution time now captured in the duration time which includes job submission and log collection. If a job does not return by the default 10 sec 'wait_time_s' value, it can be increased up to 86400 seconds. (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_job_submit - behavior changed when a volume is defined in the module options such that it will catalog the data set if it is not cataloged and submit the job. In the past, the function did not catalog the data set and instead performed I/O operations and then submitted the job. This behavior aligns to other module behaviors and reduces the possibility to encounter a permissions issue. (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_job_submit - was updated to include an additional error code condition JCLERR. (https://github.com/ansible-collections/ibm_zos_core/pull/312)
- zos_lineinfile - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_mount - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_mvs_raw - Ensures that temporary datasets created by DD Statements use the tmp_hlq specified. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/414).
- zos_mvs_raw - updates the module with a new option named tmp_hlq. This allows for a user to specify the data set high level qualifier (HLQ) used in any temporary data set created by the module. Often, the defaults are not permitted on systems, this provides a way to override the defaults. (https://github.com/ansible-collections/ibm_zos_core/pull/341).
- zos_operator - added in the response the cmd result (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - added in the response the elapsed time (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - added in the response the wait_time_s set (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - deprecated the wait option, not needed with wait_time_s minor_changes (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - was updated to remove the usage of REXX and replaced with ZOAU python APIs. This reduces code replication and it removes the need for REXX interpretation which increases performance. (https://github.com/ansible-collections/ibm_zos_core/pull/312).

Deprecated Features
-------------------

- zos_encode - deprecates the module options `from_encoding` and `to_encoding` to use suboptions `from` and `to` in order to remain consistent with all other modules. (https://github.com/ansible-collections/ibm_zos_core/pull/345).
- zos_job_submit - Response 'message' property has been deprecated, all responses are now in response property 'msg'. (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_job_submit - The 'wait' option has been deprecated because using option 'wait_time_s' implies the job is going to wait. (https://github.com/ansible-collections/ibm_zos_core/issues/389).

Bugfixes
--------

- zos_copy - Copy failed from a loadlib member to another loadlib member. Fix now looks for error in stdout in the if statement to use -X option. (https://github.com/ansible-collections/ibm_zos_core/pull/641)
- zos_copy - Fixed a bug where the module would change the mode for a directory when copying into it the contents of another. (https://github.com/ansible-collections/ibm_zos_core/pull/746)
- zos_copy - Fixes a bug such that the module fails when copying files from a directory needing also to be encoded. The failure would also delete the `src` which was not desirable behavior. Fixes deletion of src on encoding error. (https://github.com/ansible-collections/ibm_zos_core/pull/321).
- zos_copy - Fixes a bug where copying a member from a loadlib to another loadlib fails. (https://github.com/ansible-collections/ibm_zos_core/pull/640)
- zos_copy - Fixes a bug where files not encoded in IBM-1047 would trigger an error while computing the record length for a new destination dataset. Issue 664. (https://github.com/ansible-collections/ibm_zos_core/pull/725)
- zos_copy - Fixes a bug where if a destination has accented characters in its content, the module would fail when trying to determine if it is empty. (https://github.com/ansible-collections/ibm_zos_core/pull/634)
- zos_copy - Fixes a bug where the code for fixing an issue with newlines in files (issue 599) would use the wrong encoding for normalization. Issue 678. (https://github.com/ansible-collections/ibm_zos_core/pull/725)
- zos_copy - Fixes a bug where the computed record length for a new destination dataset would include newline characters. (https://github.com/ansible-collections/ibm_zos_core/pull/620)
- zos_copy - Fixes wrongful creation of destination backups when module option `force` is true, creating emergency backups meant to restore the system to its initial state in case of a module failure only when force is false. (https://github.com/ansible-collections/ibm_zos_core/pull/590)
- zos_copy - module was updated to correct a bug in the case when the destination (dest) is a PDSE and the source (src) is a Unix Systems File (USS). The module would fail in determining if the PDSE actually existed and try to create it when it already existed resulting in an error that would prevent the module from correctly executing. (https://github.com/ansible-collections/ibm_zos_core/pull/327)
- zos_data_set - Fixes a bug such that the module will delete a catalogued data set over an uncatalogued data set even though the volume is provided for the uncataloged data set. This is unexpected behavior and does not align to documentation; correct behavior is that when a volume is provided that is the first place the module should look for the data set, whether or not it is cataloged. (https://github.com/ansible-collections/ibm_zos_core/pull/325).
- zos_data_set - Fixes a bug where the default record format FB was actually never enforced and when enforced it would cause VSAM creation to fail with a Dynalloc failure. Also cleans up some of the options that are set by default when they have no bearing for batch. (https://github.com/ansible-collections/ibm_zos_core/pull/647)
- zos_fetch - Updates the modules behavior when fetching VSAM data sets such that the maximum record length is now determined when creating a temporary data set to copy the VSAM data into and a variable-length (VB) data set is used. (https://github.com/ansible-collections/ibm_zos_core/pull/350)
- zos_job_output - Fixes a bug that returned all ddname's when a specific ddnamae was provided. Now a specific ddname can be returned and all others ignored. (https://github.com/ansible-collections/ibm_zos_core/pull/334)
- zos_job_query - was updated to correct a boolean condition that always evaluated to "CANCELLED". (https://github.com/ansible-collections/ibm_zos_core/pull/312).
- zos_job_submit - Fixes the issue when `wait_time_s` was set to 0 that would result in a `type` error that a stack trace would result in the response, issue 670. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue when a job encounters a security exception no job log would would result in the response, issue 684. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue when a job is configured for a syntax check using TYPRUN=SCAN that it would wait the full duration set by `wait_time_s` to return a response, issue 685. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue when a job is configured for a syntax check using TYPRUN=SCAN that no job log would result in the response, issue 685. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue when a job is purged by the system that a stack trace would result in the response, issue 681. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue when invalid JCL syntax is submitted that a stack trace would result in the response, issue 623. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue when resources (data sets) identified in JCL did not exist such that a stack trace would result in the response, issue 624. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_job_submit - Fixes the issue where the response did not include the job log when a non-zero return code would occur, issue 655. (https://github.com/ansible-collections/ibm_zos_core/pull/683)
- zos_mount - Fixes option `tag_ccsid` to correctly allow for type int. (https://github.com/ansible-collections/ibm_zos_core/pull/511)
- zos_mvs_raw - module was updated to correct a bug when no DD statements were provided. The module when no option was provided for `dds` would error, a default was provided to correct this behavior. (https://github.com/ansible-collections/ibm_zos_core/pull/336)
- zos_operator - Fixes case sensitive error checks, invalid, error & unidentifiable (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - Fixes such that specifying wait_time_s would throw an error (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - Fixes the wait_time_s to default to 1 second (https://github.com/ansible-collections/ibm_zos_core/issues/389).
- zos_operator - fixed incorrect example descriptions and updated the doc to highlight the deprecated option `wait`. (https://github.com/ansible-collections/ibm_zos_core/pull/648)
- zos_operator - was updated to correct missing verbosity content when the option verbose was set to True. zos_operator - was updated to correct the trailing lines that would appear in the result content. (https://github.com/ansible-collections/ibm_zos_core/pull/400).

New Modules
-----------

- ibm.ibm_zos_core.zos_gather_facts - Gather z/OS system facts.

v1.4.1
======

Release Summary
---------------

Release Date: '2023-04-18'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__


Bugfixes
--------

- zos_copy - Copy failed from a loadlib member to another loadlib member. Fix now looks for error in stdout in the if statement to use -X option. (https://github.com/ansible-collections/ibm_zos_core/pull/640)
- zos_copy - Fixed a bug where the module would change the mode for a directory when copying into it the contents of another. (https://github.com/ansible-collections/ibm_zos_core/pull/742)
- zos_copy - Fixes a bug where files not encoded in IBM-1047 would trigger an error while computing the record length for a new destination dataset. Issue 664. (https://github.com/ansible-collections/ibm_zos_core/pull/732)
- zos_copy - Fixes a bug where the code for fixing an issue with newlines in files (issue 599) would use the wrong encoding for normalization. Issue 678. (https://github.com/ansible-collections/ibm_zos_core/pull/732)
- zos_copy - fixed wrongful creation of destination backups when module option `force` is true, creating emergency backups meant to restore the system to its initial state in case of a module failure only when force is false. (https://github.com/ansible-collections/ibm_zos_core/pull/590)
- zos_copy - fixes a bug where the computed record length for a new destination dataset would include newline characters. (https://github.com/ansible-collections/ibm_zos_core/pull/620)
- zos_job_query - fixes a bug where a boolean was not being properly compared. (https://github.com/ansible-collections/ibm_zos_core/pull/379)

v1.4.0
======

Release Summary
---------------

Release Date: '2022-12-07'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__


Major Changes
-------------

- zos_copy was updated to support the ansible.builtin.ssh connection options; for further reference refer to the SSH plugin documentation.
- zos_copy was updated to take into account the record length when the source is a USS file and the destination is a data set with a record length. This is done by inspecting the destination data set attributes and using these attributes to create a new data set.
- zos_copy was updated with the capabilities to define destination data sets from within the zos_copy module. In the case where you are copying to a data set destination that does not exist, you can now do so using the new zos_copy module option destination.
- zos_fetch was updated to support the ansible.builtin.ssh connection options; for further reference refer to the SSH plugin documentation.
- zos_job_output was updated to to include the completion code (CC) for each individual job step as part of the ret_code response.
- zos_job_query was updated to handle when an invalid job ID or job name is used with the module and returns a proper response.
- zos_job_query was updated to support a 7 digit job number ID for when there are greater than 99,999 jobs in the history.
- zos_job_submit was enhanced to check for 'JCL ERROR' when jobs are submitted and result in a proper module response.
- zos_job_submit was updated to fail fast when a submitted job fails instead of waiting a predetermined time.
- zos_operator_action_query response messages were improved with more diagnostic information in the event an error is encountered.
- zos_ping was updated to remove the need for the zos_ssh connection plugin dependency.

Minor Changes
-------------

- zos_copy - enhanced the force option when `force=true` and the remote file or data set `dest` is NOT empty, the `dest` will be deleted and recreated with the `src` data set attributes, otherwise it will be recreated with the `dest` data set attributes. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_copy - enhanced to optimize how it captures the permission bits state for the `dest`. This change now reviews the source files instead of traversing the entire `dest` path. (https://github.com/ansible-collections/ibm_zos_core/pull/561)
- zos_copy - enhanced to support creating a parent directory when it does not exist in the `dest` path. Prior to this change, if a parent directory anywhere in the path did not exist the task would fail as it was stated in documentation. (https://github.com/ansible-collections/ibm_zos_core/pull/561)
- zos_copy - enhanced to support system symbols in PARMLIB. System symbols are elements that allow different z/OS® systems to share PARMLIB definitions while retaining unique values in those definitions. This was fixed in a future release through the use of one of the ZOAU dependency but this version of `ibm_zos_core` does not support that dependency version so this support was added. (https://github.com/ansible-collections/ibm_zos_core/pull/566)
- zos_copy - fixes a bug that when a directory is copied from the controller to the managed node and a mode is set, the mode is applied to the directory on the managed node. If the directory being copied contains files and mode is set, mode will only be applied to the files being copied not the pre-existing files. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_copy - fixes a bug where options were not defined in the module argument spec that will result in error when running `ansible-core` v2.11 and using options `force` or `mode`. (https://github.com/ansible-collections/ibm_zos_core/pull/496)
- zos_copy - introduced an updated creation policy referred to as precedence rules such that if `dest_data_set` is set, this will take precedence. If `dest` is an empty data set, the empty data set will be written with the expectation its attributes satisfy the copy. If no precedent rule has been exercised, `dest` will be created with the same attributes of `src`. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_copy - introduced new computation capabilities such that if `dest` is a nonexistent data set, the attributes assigned will depend on the type of `src`. If `src` is a USS file, `dest` will have a Fixed Block (FB) record format and the remaining attributes will be computed. If `src` is binary, `dest` will have a Fixed Block (FB) record format with a record length of 80, block size of 32760, and the remaining attributes will be computed. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_copy - option `dest_dataset` has been deprecated and removed in favor of the new option `dest_data_set`. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_copy - was enhanced for when `src` is a directory and ends with "/", the contents of it will be copied into the root of `dest`. It it doesn't end with "/", the directory itself will be copied. (https://github.com/ansible-collections/ibm_zos_core/pull/496)

Deprecated Features
-------------------

- zos_copy and zos_fetch option sftp_port has been deprecated. To set the SFTP port, use the supported options in the ansible.builtin.ssh plugin. Refer to the `SSH port <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ssh_connection.html#parameter-port>`__ option to configure the port used during the modules SFTP transport.
- zos_copy module option model_ds has been removed. The model_ds logic is now automatically managed and data sets are either created based on the src data set or overridden by the new option destination_dataset.
- zos_ssh connection plugin has been removed, it is no longer required. You must remove all playbook references to connection ibm.ibm_zos_core.zos_ssh.

Bugfixes
--------

- zos_copy - fixes a bug that did not create a data set on the specified volume. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_copy - fixes a bug where a number of attributes were not an option when using `dest_data_set`. (https://github.com/ansible-collections/ibm_zos_core/pull/306)
- zos_job_output - fixes a bug that returned all ddname's when a specific ddname was provided. Now a specific ddname can be returned and all others ignored. (https://github.com/ansible-collections/ibm_zos_core/pull/507)
- zos_job_output was updated to correct possible truncated responses for the ddname content. This would occur for jobs with very large amounts of content from a ddname.
- zos_mount - fixed option `tag_ccsid` to correctly allow for type int. (https://github.com/ansible-collections/ibm_zos_core/pull/502)
- zos_operator - enhanced to allow for MVS operator `SET` command, `SET` is equivalent to the abbreviated `T` command. (https://github.com/ansible-collections/ibm_zos_core/pull/501)
- zos_ssh - connection plugin was updated to correct a bug in Ansible that
    would result in playbook task retries overriding the SSH connection
    retries. This is resolved by renaming the zos_ssh option
    retries to reconnection_retries. The update addresses users of
    ansible-core v2.9 which continues to use retries and users of
    ansible-core v2.11 or later which uses reconnection_retries.
    This also resolves a bug in the connection that referenced a deprecated
    constant. (https://github.com/ansible-collections/ibm_zos_core/pull/328)

New Modules
-----------

- ibm.ibm_zos_core.zos_mount - Mount a z/OS file system.

v1.3.6
======

Release Summary
---------------

Release Date: '2022-10-07'
This changelog describes all changes made to the modules and plugins included
in this collection. The release date is the date the changelog is created.
For additional details such as required dependencies and availability review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Minor Changes
-------------

- zos_copy - was enhanced for when `src` is a directory and ends with "/", the contents of it will be copied into the root of `dest`. If it doesn't end with "/", the directory itself will be copied. (https://github.com/ansible-collections/ibm_zos_core/pull/515)

Bugfixes
--------

- jobs.py - fixes a utility used by module `zos_job_output` that would truncate the DD content. (https://github.com/ansible-collections/ibm_zos_core/pull/462)
- zos_copy - fixes a bug that when a directory is copied from the controller to the managed node and a mode is set, the mode is now applied to the directory on the controller. If the directory being copied contains files and mode is set, mode will only be applied to the files being copied not the pre-existing files.(https://github.com/ansible-collections/ibm_zos_core/pull/462)
- zos_copy - fixes a bug where options were not defined in the module argument spec that will result in error when running `ansible-core` 2.11 and using options `force` or `mode`. (https://github.com/ansible-collections/ibm_zos_core/pull/462)
- zos_fetch - fixes a bug where an option was not defined in the module argument spec that will result in error when running `ansible-core` 2.11 and using option `encoding`. (https://github.com/ansible-collections/ibm_zos_core/pull/462)
- zos_job_submit - fixes a bug where an option was not defined in the module argument spec that will result in error when running `ansible-core` 2.11 and using option `encoding`. (https://github.com/ansible-collections/ibm_zos_core/pull/462)
- zos_ssh - fixes connection plugin which will error when using `ansible-core` 2.11 with an `AttributeError module 'ansible.constants' has no attribute 'ANSIBLE_SSH_CONTROL_PATH_DIR'`. (https://github.com/ansible-collections/ibm_zos_core/pull/462)
- zos_ssh - fixes connection plugin which will error when using `ansible-core` 2.11 with an `AttributeError module 'ansible.constants' has no attribute 'ANSIBLE_SSH_CONTROL_PATH_DIR'`. (https://github.com/ansible-collections/ibm_zos_core/pull/513)

v1.3.5
======

Release Summary
---------------

Release Date: '2022-03-06'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Bugfixes
--------

- zos_ssh - connection plugin was updated to correct a bug in Ansible that
    would result in playbook task retries overriding the SSH connection
    retries. This is resolved by renaming the zos_ssh option
    retries to reconnection_retries. The update addresses users of
    ansible-core v2.9 which continues to use retries and users of
    ansible-core v2.11 or later which uses reconnection_retries.
    This also resolves a bug in the connection that referenced a deprecated
    constant. (https://github.com/ansible-collections/ibm_zos_core/pull/328)

v1.3.3
======

Release Summary
---------------

Release Date: '2022-26-04'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Bugfixes
--------

- zos_copy was updated to correct deletion of all temporary files and unwarranted deletes. - When the module would complete, a cleanup routine did not take into account that other processes had open temporary files and thus would error when trying to remove them. - When the module would copy a directory (source) from USS to another USS directory (destination), any files currently in the destination would be deleted. The modules behavior has changed such that files are no longer deleted unless the force option is set to true. When **force=true**, copying files or a directory to a USS destination will continue if it encounters existing files or directories and overwrite any corresponding files.
- zos_job_query was updated to correct a boolean condition that always evaluated to "CANCELLED". - When querying jobs that are either **CANCELLED** or have **FAILED**, they were always treated as **CANCELLED**.

v1.3.1
======

Release Summary
---------------

Release Date: '2022-27-04'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 


Bugfixes
--------

- zos_ping was updated to support Automation Hub documentation generation.
- zos_ssh connection plugin was updated to prioritize the execution of modules written in REXX over other implementations such is the case for zos_ping.

Known Issues
------------

- When executing programs using zos_mvs_raw, you may encounter errors that originate in the implementation of the programs. Two such known issues are noted below of which one has been addressed with an APAR. - zos_mvs_raw module execution fails when invoking Database Image Copy 2 Utility or Database Recovery Utility in conjunction with FlashCopy or Fast Replication. - zos_mvs_raw module execution fails when invoking DFSRRC00 with parm "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is addressed by APAR PH28089.

v1.3.0
======

Release Summary
---------------

Release Date: '2021-19-04'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 

`New Playbooks <https://github.com/IBM/z_ansible_collections_samples>`__
  - Authorize and synchronize APF authorized libraries on z/OS from a configuration file cloned from GitHub
  - Automate program execution with copy, sort and fetch data sets on z/OS playbook.
  - Automate user management with add, remove, grant permission, generate
    passwords, create zFS, mount zFS and send email notifications when deployed
    to Ansible Tower or AWX with the manage z/OS Users Using Ansible playbook.
  - Use the configure Python and ZOAU Installation playbook to scan the
    **z/OS** target to find the latest supported configuration and generate
    inventory and a variables configuration.
  - Automate software management with SMP/E Playbooks


Minor Changes
-------------

- All modules support relative paths and remove choice case sensitivity.
- zos_data_set added support to allocate and format zFS data sets.
- zos_operator supports new options **wait** and **wait_time_s** such that you can specify that zos_operator wait the full **wait_time_s** or return as soon as the first operator command executes.

Bugfixes
--------

- Action plugin zos_copy was updated to support Python 2.7.
- Job utility is an internal library used by several modules. It has been updated to use a custom written parsing routine capable of handling special characters to prevent job related reading operations from failing when a special character is encountered.
- Module zos_copy was updated to fail gracefully when a it encounters a non-zero return code.
- Module zos_copy was updated to support copying data set members that are program objects to a PDSE. Prior to this update, copying data set members would yield an error; - FSUM8976 Error writing <src_data_set_member> to PDSE member <dest_data_set_member>
- Module zos_job_submit referenced a non-existent option and was corrected to **wait_time_s**.
- Module zos_job_submit was updated to remove all trailing **\r** from jobs that are submitted from the controller.
- Module zos_tso_command support was added for when the command output contained special characters.
- Playbook zos_operator_basics.yaml has been updated to use end in the WTO reply over the previous use of cancel. Using cancel is not a valid reply and results in an execution error.

Known Issues
------------

- When executing programs using zos_mvs_raw, you may encounter errors that originate in the implementation of the programs. Two such known issues are noted below of which one has been addressed with an APAR. - zos_mvs_raw module execution fails when invoking Database Image Copy 2 Utility or Database Recovery Utility in conjunction with FlashCopy or Fast Replication. - zos_mvs_raw module execution fails when invoking DFSRRC00 with parm "UPB,PRECOMP", "UPB, POSTCOMP" or "UPB,PRECOMP,POSTCOMP". This issue is addressed by APAR PH28089.

New Modules
-----------

- ibm.ibm_zos_core.zos_apf - Add or remove libraries to Authorized Program Facility (APF)
- ibm.ibm_zos_core.zos_backup_restore - Backup and restore data sets and volumes
- ibm.ibm_zos_core.zos_blockinfile - Manage block of multi-line textual data on z/OS
- ibm.ibm_zos_core.zos_data_set - Manage data sets
- ibm.ibm_zos_core.zos_find - Find matching data sets

v1.2.1
======

Release Summary
---------------

Release Date: '2020-10-09'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__.

Beginning this release, all playbooks previously included with the collection
will be made available on the `playbook repository <https://github.com/IBM/z_ansible_collections_samples>`__.

Minor Changes
-------------

- Documentation related to configuration has been migrated to the `playbook repository <https://github.com/IBM/z_ansible_collections_samples>`__
- Python 2.x support

Bugfixes
--------

- zos_copy - fixed regex support, dictionary merge operation fix
- zos_encode - removed TemporaryDirectory usage.
- zos_fetch - fix quote import

New Modules
-----------

- ibm.ibm_zos_core.zos_lineinfile - Manage textual data on z/OS

v1.1.0
======

Release Summary
---------------

Release Date: '2020-26-01'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__


Minor Changes
-------------

- Documentation updates
- Improved error handling and messages
- New Filter that will filter a list of WTOR messages based on message text.

New Modules
-----------

- ibm.ibm_zos_core.zos_encode - Perform encoding operations.
- ibm.ibm_zos_core.zos_fetch - Fetch data from z/OS
- ibm.ibm_zos_core.zos_mvs_raw - Run a z/OS program.
- ibm.ibm_zos_core.zos_operator - Execute operator command
- ibm.ibm_zos_core.zos_operator_action_query - Display messages requiring action
- ibm.ibm_zos_core.zos_ping - Ping z/OS and check dependencies.
- ibm.ibm_zos_core.zos_tso_command - Execute TSO commands

v1.0.0
======

Release Summary
---------------

Release Date: '2020-18-03'
This changlelog describes all changes made to the modules and plugins included
in this collection.
For additional details such as required dependencies and availablity review
the collections `release notes <https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html>`__ 

Minor Changes
-------------

- Documentation updates
- Module zos_data_set catalog support added

Security Fixes
--------------

- Improved test, security and injection coverage
- Security vulnerabilities fixed

New Modules
-----------

- ibm.ibm_zos_core.zos_copy - Copy data to z/OS
- ibm.ibm_zos_core.zos_job_output - Display job output
- ibm.ibm_zos_core.zos_job_query - Query job status
- ibm.ibm_zos_core.zos_job_submit - Submit JCL
