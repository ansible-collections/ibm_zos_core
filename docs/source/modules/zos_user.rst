
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_user.py

.. _ibm.ibm_zos_core.zos_user_module:


zos_user -- Manage z/OS user and group profiles in RACF
=======================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manage z/OS user and group profiles in RACF database.
- Create, update, delete, and purge RACF user and group profiles, and connect users to groups.
- Operations are performed using RACF TSO commands.





Parameters
----------


name
  The name of the RACF profile to manage.

  | **required**: True
  | **type**: str


profile_type
  Whether the RACF profile specified in *name* is a user or group profile.

  | **required**: True
  | **type**: str
  | **choices**: user, group


state
  Specifies the state to perform on the RACF profile.

  The available choices depend on the value of *profile_type*.

  ``create`` - Creates a new profile. Supported for both *profile_type=user* and *profile_type=group*.

  ``update`` - Modifies an existing profile. Supported for both *profile_type=user* and *profile_type=group*.

  ``delete`` - Removes the profile from RACF database, but may leave references to the profile in other RACF profiles or database records. Supported for both *profile_type=user* and *profile_type=group*.

  ``purge`` - Completely removes the profile and all associated references from the RACF database. Unloads the RACF database using `IRRDBU00 <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-unload-utility-irrdbu00>`_, identifies all references via `IRRRID00 <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-remove-id-irrrid00-utility>`_, and executes the necessary commands to remove them.

  ``connect`` - Links a user to a group. Only supported when *profile_type=user*.

  ``remove`` - Removes a user from a group. Only supported when *profile_type=user*.

  | **required**: True
  | **type**: str
  | **choices**: create, update, delete, purge, connect, remove


database
  Name of the RACF database to use for the purge state.

  This option is only applicable when *state=purge*.

  | **required**: False
  | **type**: str


keep_dump
  Whether to keep the database dump data sets after the purge completes.

  This option is only applicable when *state=purge*.

  When set to ``true``, the IRRDBU00 dump data set and IRRRID00 CLIST is retained for debugging or auditing purposes.

  When set to ``false``, these temporary data sets are deleted after the purge.

  | **required**: False
  | **type**: bool
  | **default**: False


optimize_dump
  Whether to skip locking the RACF database during the dump state to optimize performance.

  This option is only applicable when *state=purge*.

  When set to ``true``, the IRRDBU00 utility runs with the ``NOLOCKINPUT`` option. This improves system availability by allowing concurrent updates to the database. However, it may result in inconsistent data if changes occur during the process.

  The user ID requires ``READ`` authority to the RACF database when using ``NOLOCKINPUT``.

  When set to ``false``, the IRRDBU00 utility runs with the ``LOCKINPUT`` option. This ensures data consistency by locking the database, but it prevents other processes from updating RACF profiles until the dump completes.

  The user ID requires ``UPDATE`` authority to the RACF database when using ``LOCKINPUT``.

  See `IRRDBU00 allowable parameters <https://www.ibm.com/docs/en/zos/latest?topic=irrdbu00-allowable-parameters>`_ for more information about ``LOCKINPUT`` and ``NOLOCKINPUT``.

  | **required**: False
  | **type**: bool
  | **default**: False


execute_clist
  Whether to execute the generated CLIST.

  This option is only applicable when *state=purge*.

  When set to ``true``, the module generates the CLIST, removes the safety ``EXIT`` statement, and executes the DELUSER/DELGROUP commands.

  When set to ``false``, the module generates the CLIST but does not execute it.

  This option is useful for reviewing the purge commands before execution.

  | **required**: False
  | **type**: bool
  | **default**: True


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary data sets.

  This option is only applicable when *state=purge*.

  Temporary data sets are created during the purge for database dumps, CLIST generation, and intermediate processing.

  If not specified, the system default HLQ is used.

  | **required**: False
  | **type**: str


base_segment
  Configures the RACF BASE segment attributes.

  The BASE segment contains core profile information applicable to both *profile_type=user* and *profile_type=group*.

  Supported attributes include *display_name*, *model*, *owner*, *installation_data*, and *custom_fields*.

  Note that *display_name* is only valid when *profile_type=user*.

  | **required**: False
  | **type**: dict


  display_name
    Display name for the user profile (the descriptive name shown in listings, not the 8-character userid used for login).

    This corresponds to the RACF NAME parameter.

    For example, userid "JSMITH01" might have display_name "John Smith".

    Maximum length of 20 characters.

    This option is only valid for user profiles (*profile_type=user*).

    This option is only applicable when *state=create* or *state=update*.

    If omitted, RACF will display UNKNOWN when listing the user.

    To remove/reset the display name to default (UNKNOWN), set this to an empty string ``""``.

    | **required**: False
    | **type**: str


  model
    Name of an existing RACF profile to use as a model.

    Attributes not explicitly specified will be copied from the model profile.

    To remove the model field from the profile, set ``model=""``.

    | **required**: False
    | **type**: str


  owner
    Specifies the user or group profile name to set as the owner.

    | **required**: False
    | **type**: str


  installation_data
    Installation-defined data to store in the profile.

    Maximum length of 255 characters.

    The module automatically encloses the contents in single quotation marks.

    To remove the installation data from the profile, set ``installation_data=""``.

    | **required**: False
    | **type**: str


  custom_fields
    Custom fields to store with the profile.

    | **required**: False
    | **type**: dict


    add
      Custom fields to add to the profile.

      Custom fields are specified as a dictionary of ``key=value`` pairs.

      This option is valid when *state=create* or *state=update*.

      This option is mutually exclusive with *delete* and *delete_block*.

      Note - Values containing colons should be enclosed in quotes to ensure correct YAML parsing in playbooks.

      | **required**: False
      | **type**: dict


    delete
      List of custom fields to delete.

      This option is only valid when *state=update*; it is ignored for all other values of state.

      This option is mutually exclusive with *add* and *delete_block*.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete_block
      Delete all custom fields from the profile.

      This removes the entire custom fields section, not just individual fields.

      Use *delete* to remove specific custom fields, or *delete_block=true* to remove all custom fields at once.

      This option is only valid when *state=update*; it is ignored for all other values of state, including *state=create*.

      This option is mutually exclusive with *add* and *delete*.

      | **required**: False
      | **type**: bool




group
  Options that change group-specific attributes in a RACF profile.

  Only valid when *profile_type=group*, ignored for user profiles.

  | **required**: False
  | **type**: dict


  superior_group
    Specifies the name of a group profile to set as the superior group.

    | **required**: False
    | **type**: str


  terminal_access
    Whether to allow the use of the universal access authority for a terminal during authorization checking.

    | **required**: False
    | **type**: bool


  universal_group
    Whether the group should be allowed to have an unlimited number of users.

    Valid only for *profile_type=group*.

    This option is valid for *state=create* only.

    | **required**: False
    | **type**: bool



dfp
  Options that set DFP attributes from the Storage Management Subsystem (SMS).

  Supported for both *profile_type=user* and *profile_type=group*.

  This option is applicable for *state=create* and *state=update*.

  | **required**: False
  | **type**: dict


  data_app_id
    Specifies the name of a DFP data application.

    | **required**: False
    | **type**: str


  data_class
    Specifies the default data class for data set allocation.

    | **required**: False
    | **type**: str


  management_class
    Default management class for data set migration and backup.

    | **required**: False
    | **type**: str


  storage_class
    Default storage class for data set space, device and volume.

    | **required**: False
    | **type**: str


  delete
    Setting to ``true`` deletes the whole DFP block from the profile.

    This option is only valid when *state=update*, it is ignored for all other values of state including *state=create*.

    This option is mutually exclusive with *data_app_id*, *data_class*, *management_class* and *storage_class*.

    | **required**: False
    | **type**: bool



language
  Options that set the preferred national languages for a *profile_type=user*.

  Valid when *state=create* and *state=update*.

  These options override the system-wide defaults.

  | **required**: False
  | **type**: dict


  primary
    Specifies the user's primary language.

    Value should be either a 3 character-long language code or an installation-defined name of up to 24 characters.

    To delete this field from the profile, set *primary=""*.

    This option is mutually exclusive with *delete*.

    | **required**: False
    | **type**: str


  secondary
    Specifies the user's secondary language.

    Value should be either a 3 character-long language code or an installation-defined name of up to 24 characters.

    To delete this field from the profile, set *secondary=""*.

    This option is mutually exclusive with *delete*.

    | **required**: False
    | **type**: str


  delete
    Setting to ``true`` deletes the whole LANGUAGE block from the profile.

    This option is only valid when *state=update*, it is ignored for all other values of state, including *state=create*.

    This option is mutually exclusive with *primary* and *secondary*.

    | **required**: False
    | **type**: bool



omvs
  Attributes for the RACF OMVS segment.

  Configures z/OS Unix System Services access and resource limits for the profile.

  Valid for both *profile_type=user* and *profile_type=group* are *uid*, *custom_uid*, *delete*.

  Valid only for *profile_type=user* are *home*, *program*, *nonshared_size*, *shared_size*, *addr_space_size*, *map_size*, *max_procs*, *max_threads*, *max_cpu_time*, *max_files*, and their related unit options.

  User-only options control process and memory resource limits which do not apply to group profiles.

  | **required**: False
  | **type**: dict


  uid
    Specifies how RACF should assign UIDs to users or GIDs to groups.

    This option is valid when *state=create* and *state=update*

    ``none`` deletes the user or group identifier from the OMVS segment of the profile. This is only valid when *state=update*, it is ignored for all other values of state including *state=create*.

    ``custom`` and ``shared`` require *omvs.custom_uid* to be defined.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: str
    | **choices**: auto, custom, shared, none


  custom_uid
    Specifies the OMVS identifier for the profile.

    For *profile_type=user*, this is the UID; for *profile_type=group*, this is the GID.

    A number between 0 and 2,147,483,647.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  home
    Specifies the path name for the z/OS Unix System Services home directory.

    Maximum length of 1023 characters.

    To remove the home from the profile, set *home=""*.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: str


  program
    Specifies the path to the shell program when the user logs in.

    Maximum length of 1023 characters.

    To remove the program from the profile, set *program=""*.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: str


  nonshared_size
    Specifies the maximum number of bytes of nonshared memory that can be allocated by the user.

    Value between 0 and 16,777,215.

    Set to ``-1`` to remove the limit ``NOMEMLIMIT``. When set to ``-1``, *nonshared_size_unit* is ignored.

    Unit is specified separately via *nonshared_size_unit*, defaults to 'm' (megabytes) if not specified.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  nonshared_size_unit
    Specifies the unit for the nonshared memory size.

    Only used when *nonshared_size* is specified and not set to -1.

    Ignored when *nonshared_size* is -1.

    Defaults to ``m`` (megabytes) if not specified.

    | **required**: False
    | **type**: str
    | **choices**: m, g, t, p


  shared_size
    Specifies the maximum number of bytes of shared memory that can be allocated by the user.

    Value between 1 and 16,777,215.

    Set to ``-1`` to remove the limit ``NOSHMEMMAX``. When set to ``-1``, *shared_size_unit* is ignored.

    Unit is specified separately via *shared_size_unit*, defaults to 'm' (megabytes) if not specified.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  shared_size_unit
    Specifies the unit for the shared memory size.

    Only used when *shared_size* is specified and not set to -1.

    Ignored when *shared_size=-1*.

    Defaults to ``m`` (megabytes) if not specified.

    | **required**: False
    | **type**: str
    | **choices**: m, g, t, p


  addr_space_size
    Specifies the maximum size of the address space region in bytes for the profile.

    Value between 10,485,760 and 2,147,483,647.

    Set to ``0`` to remove the user-specific limit ``NOASSIZEMAX``. This allows the system default from ``BPXPRMxx`` to apply.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  map_size
    Specifies the maximum amount of data space storage that can be allocated by the user.

    This option represents the number of memory pages, not bytes, available.

    Value between 1 and 16,777,216.

    Set this to ``0`` to remove the user-specific limit (``NOMMAPAREAMAX``). This allows the system default from ``BPXPRMxx`` to apply.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  max_procs
    Specifies the maximum number of processes the user is allowed to have active at the same time.

    Value between 3 and 32,767.

    Set this to ``0`` to remove the user-specific limit (NOPROCUSERMAX). This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  max_threads
    Specifies the maximum number of threads the user can have concurrently active.

    Value between 0 and 100,000.

    Set this to ``-1`` to remove the user-specific limit (NOTHREADSMAX). This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  max_cpu_time
    Specifies the RLIMIT_CPU hard limit. Indicates the cpu-time that a user process is allowed to use.

    Value between 7 and 2,147,483,647 seconds.

    Set this to ``0`` to remove the user-specific limit (NOCPUTIMEMAX). This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  max_files
    Specifies the maximum number of files the user is allowed to have concurrently active or open.

    Value between 3 and 524,287.

    Set this to ``0`` to remove the user-specific limit ``NOFILEPROCMAX``. This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with *omvs.delete*.

    | **required**: False
    | **type**: int


  delete
    Setting to ``true`` deletes the whole OMVS block from the profile.

    This option is only valid when *state=update*; it is ignored for all other state values, including *state=create*.

    This option is mutually exclusive with *uid*, *custom_uid*, *home*, *program*, *nonshared_size*, *nonshared_size_unit*, *shared_size*, *shared_size_unit*, *addr_space_size*, *map_size*, *max_procs*, *max_threads*, *max_cpu_time*, and *max_files*.

    | **required**: False
    | **type**: bool



tso
  Attributes for the RACF TSO segment.

  Configures TSO settings for the user profile.

  Only valid for *profile_type=user*, *state=create* and *state=update*.

  | **required**: False
  | **type**: dict


  account_num
    Specifies the user's default TSO account number at logon.

    Maximum length of 39 characters.

    To delete this field from the profile, set *account_num=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  logon_cmd
    Specifies the command to run during TSO/E logon.

    Maximum length of 80 characters.

    This option is case-sensitive.

    To delete this field from the profile, set *logon_cmd=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  logon_proc
    Specifies the user's default logon procedure.

    The value for this field is 1 to 8 alphanumeric characters.

    To delete this field from the profile, set *logon_proc=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  dest_id
    Specifies the default destination for dynamically allocated SYSOUT data sets.

    The value for this field is 1 to 7 alphanumeric characters.

    To delete this field from the profile, set *dest_id=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  hold_class
    Specifies the user's default hold class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set *hold_class=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  job_class
    Specifies the user's default job class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set *job_class=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  msg_class
    Specifies the user's default message class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set *msg_class=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  sysout_class
    Specifies the user's default SYSOUT class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set *sysout_class=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  region_size
    Specifies the minimum region size if none is requested at logon.

    A value between 0 and 2,096,128.

    When *region_size=-1* is set, this field is set to ``00000000``.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: int


  max_region_size
    Specifies the maximum region size that can be requested at logon.

    A value between 0 and 2,096,128.

    When *max_region_size=-1* is set, this field is set to ``00000000``.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: int


  security_label
    Specifies the user's security label on the TSO logon panel.

    To delete this field from the profile, set *security_label=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  unit_name
    Specifies the default device or device group name used for allocations.

    The value for this field is 1 to 8 alphanumeric characters.

    To delete this field from the profile, set *unit_name=""*.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  user_data
    Specifies optional installation data for the user profile.

    Must be exactly 4 characters (0–9, A–F only).

    When *user_data=""*, this field is set to ``0000``.

    This option is mutually exclusive with *tso.delete*.

    | **required**: False
    | **type**: str


  delete
    Setting to ``true`` deletes the whole TSO block from the profile.

    This option is only valid when *state=update*; it is ignored for all other values, including *state=create*.

    This option is mutually exclusive with *account_num*, *logon_cmd*, *logon_proc*, *dest_id*, *hold_class*, *job_class*, *msg_class*, *sysout_class*, *region_size*, *max_region_size*, *security_label*, *unit_name*, and *user_data*.

    | **required**: False
    | **type**: bool



connect
  Options that configure a user's connection to a group.

  Only valid when *state=connect*; ignored for all other state values.

  | **required**: False
  | **type**: dict


  authority
    Specifies the level of group authority assigned to the user for the connection.

    This determines what actions the user can perform within the group.

    If not specified when creating a connection, the default authority is ``use``.

    ``use`` - Allows access to resources authorized to the group.

    ``create`` - Allows creation of RACF data set profiles for the group.

    ``connect`` - Allows connecting other users to the group.

    ``join`` - Allows adding users or subgroups to the group and assigning group authorities.

    See `Group Authorities <https://www.ibm.com/docs/en/zos/latest?topic=summary-group-authorities>`_.

    | **required**: False
    | **type**: str
    | **choices**: use, create, connect, join


  universal_access
    Specifies the level of universal access authority assigned for the connection.

    Specifies the level of universal access authority ``(UACC``) for resources associated with the connection.

    This value applies to new resource profiles created while the user is connected to the group.

    If not specified when creating a connection, the default value is ``none``.

    ``alter`` - Allows full access, including read, update, and delete.

    ``control`` - Allows read and update access, and modification of the resource profile.

    ``update`` - Allows read and update access.

    ``read`` - Allows read-only access.

    ``none`` - Allows no access.

    | **required**: False
    | **type**: str
    | **choices**: alter, control, update, read, none


  group_name
    Specifies the group to connect the user to.

    If omitted, the user is connected to the current connect group.

    | **required**: False
    | **type**: str


  group_access
    Whether data sets defined by the user are accessible to other users in the group.

    When enabled, the group is given UPDATE access to data sets created by the user with the group as the high-level qualifier.

    | **required**: False
    | **type**: bool
    | **default**: False


  group_operations
    Whether the user should has the group-OPERATIONS attribute for the connection.

    Allows the user to perform maintenance operations on RACF-protected data sets and resources within the scope of the group

    | **required**: False
    | **type**: bool
    | **default**: False


  auditor
    Whether the user has group-AUDITOR attribute for the connection.

    Allows the user to list profiles connected to the group and review audit information for the group.

    This is independent of the system-wide AUDITOR attribute (*access.auditor*).

    A user can have group-AUDITOR in one group but not in another.

    | **required**: False
    | **type**: bool
    | **default**: False


  auto_protect_datasets
    Whether the user has the group-ADSP attribute for the specific group connection.

    Causes RACF to automatically create discrete profiles for permanent data sets created while the user is connected to the group.

    This is independent of the system-wide ADSP attribute (*access.auto_protect_datasets*).

    A user can have ADSP in one group but not in another.

    | **required**: False
    | **type**: bool
    | **default**: False


  special
    Whether the user has group-SPECIAL attribute for the connection.

    Allows the user to manage profiles owned by the group and user connections to the group.

    This is independent of the system-wide SPECIAL attribute (*access.special*).

    A user can have group-SPECIAL in one group but not in another.

    | **required**: False
    | **type**: bool
    | **default**: False



access
  Options that configure security attributes for a user profile.

  Only valid for *profile_type=user*

  This option is valid for *state=create* and *state=update*.

  | **required**: False
  | **type**: dict


  default_group
    Specifies the RACF default group for the user profile.

    | **required**: False
    | **type**: str


  clauth
    Specifies the RACF resource classes the user is permitted to define profiles in.

    | **required**: False
    | **type**: dict


    add
      List of classes to add to the profile.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete
      List of classes to remove from the profile.

      | **required**: False
      | **type**: list
      | **elements**: str



  roaudit
    Specifies whether to assign the ``ROAUDIT`` attribute to the user.

    When enabled, the user has responsibility for auditing system resources with read-only access to audit records and settings.

    In RACF output, this appears under the user's ATTRIBUTES list.

    Requires the ``SPECIAL`` attribute to modify.

    | **required**: False
    | **type**: bool
    | **default**: False


  category
    Security categories assigned to the profile.

    | **required**: False
    | **type**: dict


    add
      List of security categories to add to the profile.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete
      List of security categories to remove from the profile.

      | **required**: False
      | **type**: list
      | **elements**: str



  operator_card
    Whether the user must supply an operator identification card at logon.

    | **required**: False
    | **type**: bool
    | **default**: False


  maintenance_access
    Whether the user is authorized to perform maintenance operations on all RACF-protected DASD data sets, tape volumes, and DASD volumes.

    | **required**: False
    | **type**: bool
    | **default**: False


  restricted
    Whether the user profile should have the RESTRICTED attribute.

    When enabled, the user is denied access to resources via UACC or ID(*). Access is only granted if the user or their group is explicitly added to the resource's access list.

    Also bypasses global access checking and z/OS UNIX other permission bits.

    | **required**: False
    | **type**: bool
    | **default**: False


  security_label
    Specifies the security label applied to the profile.

    To delete this field from the profile, set *security_label=""*.

    | **required**: False
    | **type**: str


  security_level
    Specifies the security level applied to the profile.

    To delete this field from the profile, set ``security_level=""``.

    | **required**: False
    | **type**: str


  auto_protect_datasets
    Whether the user has the system-wide ADSP (Automatic Data Set Protection) attribute.

    When enabled, RACF automatically defines a discrete profile for any new data set created by the user.

    This is a user profile attribute that applies globally across all groups.

    Different from *connect.auto_protect_datasets* which applies only to a specific group connection.

    | **required**: False
    | **type**: bool
    | **default**: False


  auditor
    Whether the user has the system-wide AUDITOR attribute.

    Provides responsibility for auditing the use of system resources.

    Allows the user to review audit records and control logging of accesses to RACF-protected resource

    This is a user profile attribute that applies globally across all groups.

    Different from *connect.auditor* which provides group-AUDITOR authority for a specific group only.

    | **required**: False
    | **type**: bool
    | **default**: False


  authority
    Specifies the user's default group authority level.

    This is used as the default when connecting the user to groups if *connect.authority* is not specified.

    Also applies to the user's default group (DFLTGRP) connection.

    ``use`` - Allows the user to access resources to which the group is authorized.

    ``create`` - Allows the user to create RACF data set profiles for the group.

    ``connect`` - Allows the user to connect other users to the group.

    ``join`` - Allows the user to add users or subgroups to the group and assign group authorities..

    Can be overridden per-group using *connect.authority*.

    See `Group Authorities <https://www.ibm.com/docs/en/zos/latest?topic=summary-group-authorities>`_.

    | **required**: False
    | **type**: str
    | **choices**: use, create, connect, join


  special
    Whether the user has the system-wide SPECIAL attribute.

    Allows the user to issue most RACF commands and manage RACF profiles and user IDs system-wide.

    This is a user profile attribute that applies globally across all groups.

    Different from *connect.special* which provides group-SPECIAL authority for a specific group only.

    | **required**: False
    | **type**: bool
    | **default**: False


  universal_access
    Specifies the user's default universal access authority (UACC).

    This value applies to new resource profiles created while the user is connected to a group.

    It is used when *connect.universal_access* is not specified during group connection.

    Also applies to the user's default group (DFLTGRP) connection

    The user can have different UACC values for each group connection.

    ``alter`` - Allows full access, including read, update, delete, rename, and control of the resource profile.

    ``control`` - Allows read and update access, and the ability to modify the resource profile.

    ``update`` - Allows read and update access to the resource.

    ``read`` - Allows read-only access to the resource.

    ``none`` - Allows no access to the resource.

    Can be overridden per group using *connect.universal_access*.

    | **required**: False
    | **type**: str
    | **choices**: alter, control, update, read, none



operator
  Configures the RACF OPERPARM segment attributes.

  The OPERPARM segment defined extended MCS console session attributes for the user.

  Only valid when *profile_type=user*.

  Supported for *state=create* and *state=update*.

  | **required**: False
  | **type**: dict


  alt_group
    The console group used in recovery operations.

    Must be between 1 and 8 characters in length.

    To delete this field from the profile, set *alt_group=""*.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str


  authority
    The console authority level for issuing operator commands.

    ``master`` - Full authority to issue all commands.

    ``all`` - Authority to issue all commands except those requiring master authority.

    ``info`` - Authority to issue information-only commands.

    ``cons`` - Authority to issue console-related commands.

    ``io`` - Authority to issue I/O-related commands.

    ``sys`` - Authority to issue system-related commands.

    ``delete`` - Removes this field from the profile.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: master, all, info, cons, io, sys, delete


  cmd_system
    The system to which commands from this console are sent.

    Specify 1 to 8 characters.

    To remove this field from the profile, set *cmd_system=""*.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str


  search_key
    The name used to display information for all consoles with the specified key.

    Use the MVS command ``DISPLAY CONSOLES,KEY`` to view consoles by this key.

    Length must be between 1 and 8 characters.

    To remove this field from the profile, set *search_key=""*.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str


  migration_id
    Whether a 1-byte migration ID should be assigned to this console.

    ``yes`` - Assigns a migration ID to the console (MIGID).

    ``no`` - Explicitly sets the console to not have a migration ID.

    ``delete`` - Removes the migration ID parameter from the profile (NOMIGID).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  display
    List of information to display when monitoring jobs, TSO sessions, or data set status.

    ``jobnames`` - Display job names.

    ``jobnamest`` - Display job names with timestamps.

    ``sess`` - Display TSO session information.

    ``sesst`` - Display TSO session information with timestamps.

    ``status`` - Display status information.

    ``delete`` - Removes this field from the profile.

    Multiple values can be specified.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **choices**: jobnames, jobnamest, sess, sesst, status, delete


  msg_level
    Specifies the message levels that the Extended MCS (EMCS) console associated with this user profile receives.

    This attribute acts as a filter for the messages routed to the user's console session.

    ``r`` - The console receives messages requiring an operator reply.

    ``i`` - The console receives immediate action messages.

    ``ce`` - The console receives critical eventual action messages.

    ``e`` - The console receives eventual action messages.

    ``in`` - The console receives informational messages.

    ``nb`` - The console receives no broadcast messages.

    ``all`` - The console receives all message levels ``(R, I, CE, E, and IN``).

    ``delete`` - Removes the message level field from the user's profile.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: nb, all, r, i, ce, e, in, delete


  msg_format
    The format in which messages are displayed at the console.

    ``j`` - Job-related format.

    ``m`` - Mixed format.

    ``s`` - Short format.

    ``t`` - Time-stamped format.

    ``x`` - Extended format.

    ``delete`` - Removes this field from the profile.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: j, m, s, t, x, delete


  msg_storage
    The amount of storage in the TSO/E user's address space for message queuing to the console.

    Specify a value between ``1`` and ``2000``.

    Set to ``0`` to reset this field to ``00000``.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: int


  msg_scope
    Specifies the systems from which the Extended MCS (EMCS) console associated with this user profile receives unsolicited messages (messages not directed to a specific console).

    This field updates the OPERPARM segment of the RACF user profile.

    ``*`` - The console receives messages only from the system on which the console session is currently active.

    ``*all`` - The console receives messages from all systems in the sysplex.

    ``system_names`` - A list of one or more specific system names (e.g., SYS1, SYS2) to define the scope.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: dict


    add
      List of new systems to add to the message scope list.

      When *state=create*, this sets the initial message scope ``(MSCOPE``).

      When *state=update*, this adds systems to the existing list ``(ADDMSCOPE``).

      This option is mutually exclusive with *msg_scope.remove_all* and *msg_scope.delete*.

      | **required**: False
      | **type**: list
      | **elements**: str


    remove_all
      Set to ``true`` to remove all message scope systems from the profile ``(NOMSCOPE``).

      This option is mutually exclusive with *msg_scope.add* and *msg_scope.delete*.

      | **required**: False
      | **type**: bool


    delete
      List of specific systems to delete from the message scope list ``(DELMSCOPE``).

      This does not clear the entire list unless all listed systems are specified.

      This option is mutually exclusive with *msg_scope.add* and *msg_scope.remove_all*.

      | **required**: False
      | **type**: list
      | **elements**: str



  automated_msgs
    Whether the extended console can receive messages automated by the Message Flood Automation (MFA).

    ``yes`` - Enables the console to receive automated messages ``(AUTO``).

    ``no`` - Explicitly disables automated messages for the console.

    ``delete`` - Removes the automated messages parameter from the profile ``(NOAUTO``).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  delete_operator_msgs
    Specifies which Delete Operator Message (DOM) requests the Extended MCS (EMCS) console associated with this user profile can receive.

    ``normal`` - The system queues all appropriate local DOM requests to the console.

    ``all`` - All systems in the sysplex queue DOM requests to the console.

    ``none`` - No DOM requests are queued to the console.

    ``delete`` - Removes the DOM field from the user profile. This corresponds to the RACF ``NODOM`` operand.

    Note that when this field is deleted or omitted ``NODOM``, the DOM information will not appear in profile listings (e.g., ``LU`` command), and the EMCS console will default to ``normal`` behavior when a session is established.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: normal, all, none, delete


  hardcopy_msgs
    Whether the console receives all messages directed to hardcopy.

    ``yes`` - Enables the console to receive hardcopy messages ``(HC``).

    ``no`` - Explicitly disables hardcopy messages for the console.

    ``delete`` - Removes the hardcopy messages parameter from the profile ``(NOHC``).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  internal_msgs
    Whether the console receives messages directed to console ID zero.

    ``yes`` - Enables the console to receive internal messages ``(INTIDS``).

    ``no`` - Explicitly disables internal messages for the console.

    ``delete`` - Removes the internal messages parameter from the profile ``(NOINTIDS``).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  routing_msgs
    The routing codes of messages this operator receives.

    Accepts one of the following (mutually exclusive).

    ``["ALL"]`` - Receive all routing codes.

    ``["NONE"]`` - Receive no routing codes.

    ``["delete"]`` - Removes routing code information from the profile (NOROUTCODE).

    List of routing codes - One or more routing codes (integers 1-128) or sequences (ranges).

    Examples - ``["1"]``, ``["1", "2", "11"]``, ``["1-5"]``, ``["1-5", "10", "20-25"]``.

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: list
    | **elements**: str


  undelivered_msgs
    Whether the console receives undelivered messages.

    ``yes`` - Enables the console to receive undelivered messages ``(UD``).

    ``no`` - Explicitly disables undelivered messages for the console.

    ``delete`` - Removes the undelivered messages parameter from the profile ``(NOUD``).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  unknown_msgs
    Whether the console receives messages directed to unknown console IDs.

    ``yes`` - Enables the console to receive unknown messages ``(UNKNIDS``).

    ``no`` - Explicitly disables unknown messages for the console.

    ``delete`` - Removes the unknown messages parameter from the profile ``(NOUNKNIDS``).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  log_responses
    Whether command responses should be logged.

    ``yes`` - Enables logging of command responses ``(LOGCMDRESP(SYSTEM``)).

    ``no`` - Explicitly disables logging of command responses ``(LOGCMDRESP(NO``)).

    ``delete`` - Removes the command response logging parameter from the profile ``(NOLOGCMDRESP``).

    This option is mutually exclusive with *operator.delete*.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  delete
    When set to ``true``, deletes the entire OPERPARM segment from the profile.

    This option is only valid when *state=update*; it is ignored for all other state values.

    This option is mutually exclusive with *alt_group*, *authority*, *cmd_system*, *search_key*, *migration_id*, *display*, *msg_level*, *msg_format*, *msg_storage*, *msg_scope*, *automated_msgs*, *delete_operator_msgs*, *hardcopy_msgs*, *internal_msgs*, *routing_msgs*, *undelivered_msgs*, *unknown_msgs*, and *log_responses*.

    | **required**: False
    | **type**: bool



restrictions
  Attributes that determine the days and times a user is allowed to login.

  This option is valid for *profile_type=user*.

  | **required**: False
  | **type**: dict


  days
    Days of the week that a user is allowed to login.

    Multiple choices are allowed.

    Valid values are ``anyday``, ``weekdays``, ``monday``, ``tuesday``, ``wednesday``, ``thursday``, ``friday``, ``saturday`` and ``sunday``.

    This option is valid for *state=create* and *state=update*.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **default**: ['anyday']
    | **choices**: anyday, weekdays, monday, tuesday, wednesday, thursday, friday, saturday, sunday


  time
    Daily time period when the user is allowed to login.

    The value for this option must be in the format ``HHMM:HHMM``.

    Enclose the time value in quotes (for example, 0900:1700) to avoid YAML parsing issues.

    This field uses a 24-hour format.

    This field also accepts the value ``anytime`` to indicate a user is free to login at any time of the day.

    This option is valid for *state=create* and *state=update*.

    | **required**: False
    | **type**: str
    | **default**: anytime


  resume
    Date when the user is allowed access to a system again.

    The value for this option must be in the format ``MM/DD/YY``, where ``YY`` are the last two digits of the year.

    This option is valid for *state=connect* and *state=update*.

    | **required**: False
    | **type**: str


  delete_resume
    Delete the resume field from the profile.

    This option is valid for *state=connect* and *state=update*.

    This option is mutually exclusive with *restrictions.resume*.

    | **required**: False
    | **type**: bool


  revoke
    Date when the user is forbidden access to a system.

    The value for this option must be in the format ``MM/DD/YY``, where ``YY`` are the last two digits of the year.

    This option is valid for *state=connect* and *state=update*.

    | **required**: False
    | **type**: str


  delete_revoke
    Delete the revoke field from the profile.

    This option is valid for *state=connect* and *state=update*.

    This option is mutually exclusive with *restrictions.revoke*.

    | **required**: False
    | **type**: bool



password_mgmt
  Options that manage password and passphrase settings for a user profile.

  These options are only valid for user profiles (*profile_type=user*).

  These options are only applicable when *state=create* or *state=update*.

  | **required**: False
  | **type**: dict


  password
    Password for the user.

    Maximum length of 8 characters.

    When creating a user, if neither *password* nor *passphrase* is specified, no password is assigned. The user must be assigned one before logging in.

    When a password is set for the first time during user creation, RACF marks it as EXPIRED by default. To allow the user to use the password without an immediate change, update the user with *expired=false* after creation.

    *password=""* removes the password and sets the NOPASSWORD attribute on the user profile.

    It is highly recommended to use **Ansible Vault** to encrypt this value.

    This option is mutually exclusive with *passphrase*.

    | **required**: False
    | **type**: str


  passphrase
    Passphrase for the user.

    Minimum length of 9 characters, maximum length of 100 characters.

    When creating a user, if neither *password* nor *passphrase* is specified, no password or passphrase is assigned. The user must be assigned one before logging in.

    When a passphrase is set for the first time during user creation, RACF marks it as EXPIRED by default. To change this, update the user with *expired=false* after creation.

    Setting *passphrase=""* removes the passphrase and sets the NOPHRASE attribute on the user profile.

    It is recommended to use Ansible Vault to encrypt this value.

    This option is mutually exclusive with *password*.

    | **required**: False
    | **type**: str


  expired
    Whether the password or passphrase should be marked as expired.

    When ``true``, the user will be required to change their password/passphrase on next login.

    When ``false``, the password/passphrase will be marked as NOEXPIRED.

    This option is only applicable when *state=update*.

    This option **must** be used together with *password* or *passphrase* in the same task. RACF requires a password/passphrase to be specified when using ``EXPIRED/NOEXPIRED``.

    When a password/passphrase is set for the first time during user creation, RACF automatically marks it as ``EXPIRED``. To change it to ``NOEXPIRED``, you must update the user and specify the same password/passphrase again with *expired=false*.

    | **required**: False
    | **type**: bool





Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: full
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Create a new group profile using RACF defaults.
     zos_user:
       name: newgrp
       state: create
       profile_type: group

   - name: Create a user with full name and owner.
     zos_user:
       name: newuser
       state: create
       profile_type: user
       base_segment:
         display_name: John Doe
         owner: admin

   - name: Update a user's full name.
     zos_user:
       name: existusr
       state: update
       profile_type: user
       base_segment:
         display_name: Jane Smith

   - name: Remove a user's full name (sets to UNKNOWN).
     zos_user:
       name: existusr
       state: update
       profile_type: user
       base_segment:
         display_name: ""

   - name: Create a new group profile using another group as a model and setting its owner.
     zos_user:
       name: newgrp
       state: create
       profile_type: group
       base_segment:
         model: oldgrp
         owner: admin

   - name: Create a new group profile and set group attributes.
     zos_user:
       name: newgrp
       state: create
       profile_type: group
       group:
         superior_group: sys1
         terminal_access: true
         universal_group: false

   - name: Update a group profile to change its installation data and remove custom fields.
     zos_user:
       name: usergrp
       state: update
       profile_type: group
       base_segment:
         installation_data: New installation data
         custom_fields:
           delete_block: true

   - name: Create a user using RACF defaults.
     zos_user:
       name: newuser
       state: create
       profile_type: user

   - name: Create a user using another profile as a model.
     zos_user:
       name: newuser
       state: create
       profile_type: user
       base_segment:
         model: olduser

   - name: Create a user and set how Unix System Services should behave when it logs in.
     zos_user:
       name: newuser
       state: create
       profile_type: user
       omvs:
         uid: auto
         home: /u/newuser
         program: /bin/sh
         nonshared_size: 10
         nonshared_size_unit: g
         shared_size: 10
         shared_size_unit: g
         addr_space_size: 10485760
         map_size: 2056
         max_procs: 16
         max_threads: 150
         max_cpu_time: 4096
         max_files: 4096

   - name: Create a user and set access permissions to it.
     zos_user:
       name: newuser
       state: create
       profile_type: user
       access:
         default_group: usergrp
         roaudit: true
         operator_card: false
         maintenance_access: true
         restricted: false
       restrictions:
         days:
           - monday
           - tuesday
           - wednesday
         time: anytime

   - name: Update a user profile to change its TSO attributes and owner.
     zos_user:
       name: user
       state: update
       profile_type: user
       base_segment:
         owner: admin
       tso:
         hold_class: K
         job_class: K
         msg_class: K
         sysout_class: K
         region_size: 2048
         max_region_size: 4096

   - name: Connect a user to a group using RACF defaults.
     zos_user:
       name: user
       state: connect
       profile_type: user
       connect:
         group_name: usergrp

   - name: Connect a user to a group and give it special permissions.
     zos_user:
       name: user
       state: connect
       profile_type: user
       connect:
         group_name: usergrp
         authority: connect
         universal_access: alter
         group_access: true
         group_operations: true
         auditor: true
         auto_protect_datasets: true
         special: true

   - name: Remove a user from a group.
     zos_user:
       name: user
       state: remove
       profile_type: user
       connect:
         group_name: usergrp

   - name: Delete a user from the RACF database.
     zos_user:
       name: user
       state: delete
       profile_type: user

   - name: Delete group from the RACF database.
     zos_user:
       name: usergrp
       state: delete
       profile_type: group

   - name: Purge user from RACF database.
     zos_user:
       name: user
       state: purge
       profile_type: user
       database: racf_db
       execute_clist: true

   - name: Dry run of purge group from RACF database (group not purged).
     zos_user:
       name: newgrp
       state: purge
       profile_type: group
       database: racf_db
       execute_clist: false

   - name: Create a user with auto-assigned UID and initial password.
     zos_user:
       name: newuser
       state: create
       profile_type: user
       password_mgmt:
         password: "{{ user_password }}"
       omvs:
         uid: auto

   - name: Create user with passphrase and assign a custom uid.
     zos_user:
       name: newuser
       state: create
       profile_type: user
       password_mgmt:
         passphrase: "{{ user_passphrase }}"
       omvs:
         uid: custom
         custom_uid: 5189

   - name: Update user password and make it active.
     zos_user:
       name: newuser
       state: update
       profile_type: user
       password_mgmt:
         password: "{{ user_password }}"
         expired: false




Notes
-----

.. note::
   This module requires appropriate RACF authority to execute commands.

   For standard states (create, update, delete, connect, remove), the user executing the module must have sufficient RACF authority to perform the requested state (typically ``SPECIAL`` or ``group-SPECIAL`` attribute).

   For purge state using the `IRRDBU00 utility <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-unload-utility-irrdbu00>`_, When *optimize_dump=true*, IRRDBU00 runs with ``PARM=NOLOCKINPUT`` requiring ``READ`` authority to the input RACF database data sets. When *optimize_dump=false* (default), IRRDBU00 runs with ``PARM=LOCKINPUT`` requiring ``UPDATE`` authority to lock the database during the unload.

   The `IRRRID00 <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-remove-id-irrrid00-utility>`_ utility is used during purge operations to identify residual references and generate a ``CLIST`` of removal commands. The user must have ``READ`` authority to the input data set (the unloaded RACF database produced by IRRDBU00).

   To execute the generated ``CLIST`` from IRRRID00, the user must have sufficient RACF authority - ``DELUSER/DELGROUP`` requires the ``SPECIAL`` attribute, ``group-SPECIAL`` (within scope), or ownership of the target profile/superior group.



See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zos_core.zos_tso_command_module`




Return Values
-------------


changed
  Indicates whether any changes were made to the system.

  | **returned**: always
  | **type**: bool
  | **sample**:

    .. code-block:: json

        true

cmd
  The RACF command that was executed with tsocmd.

  | **returned**: always
  | **type**: str
  | **sample**: ADDUSER (DUSR1001)

msg
  Message returned by the module. Contains error messages on failure, informational messages when no changes are needed (e.g., entity already exists), or validation error messages.


  | **returned**: always
  | **type**: str
  | **sample**: An error occurred while executing the RACF command.

rc
  Return code from the RACF command execution.

  | **returned**: always
  | **type**: int

stdout
  Standard output from the RACF command execution. In check mode, may contain informational messages about the entity state. For *state=purge*, this includes technical details such as dump data set names and CLIST processing messages.


  | **returned**: always
  | **type**: str
  | **sample**: User DUSR1001 is defined as PROTECTED.


stdout_lines
  List of strings containing individual lines from stdout.

  | **returned**: always
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "User DUSR1001 is defined as PROTECTED.",
            ""
        ]

stderr
  Standard error from the RACF command execution. TSO command output is automatically filtered out.


  | **returned**: always
  | **type**: str

stderr_lines
  List of strings containing individual lines from stderr.

  | **returned**: always
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            ""
        ]

num_entities_modified
  Returns the number of profiles and references modified by the state. Set to ``0`` if no changes were made (e.g., ``the entity is already in the desired state``). Set to ``1`` for successful single-entity states ``create, update, or delete``. For *state=purge*, this reflects the total number of user and group entities deleted.


  | **returned**: always
  | **type**: int
  | **sample**: 1

entities_modified
  A list of profiles and references modified by the state. For *profile_type=user*, state (``create``, ``update``, ``delete``, ``connect``, ``remove``): Contains the user profile name upon success. For *profile_type=group*, state ``create``, ``update``, ``delete``): Contains the group profile name upon success. For *state=purge*, contains all users/groups IDs deleted by the CLIST. Returns an empty list if no changes were necessary (e.g., entity is already in the desired state).


  | **returned**: always
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "DUSR1001"
        ]

database_dumped
  Whether the module used IRRDBU00 utility to dump the RACF database. Set to ``true`` only when the purge state successfully executes the ``IRRDBU00`` utility. Only relevant when *state=purge*.


  | **returned**: always
  | **type**: bool

dump_kept
  Indicates whether the RACF database dump was retained on the managed node. This behavior is controlled by the *keep_dump* input parameter. Only relevant when *database_dumped=true*.


  | **returned**: always
  | **type**: bool

dump_name
  The name of the data set containing the output from the ``IRRDBU00`` utility. This field is only populated when both *database_dumped* and *keep_dump* are ``true``. Otherwise, this value returns ``null``.


  | **returned**: always
  | **type**: str
  | **sample**: USER.BACKUP.RACF.DATABASE

