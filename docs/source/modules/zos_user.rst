
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_user.py

.. _zos_user_module:


zos_user -- Manage Z/OS user and group profiles in RACF
=======================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manage z/OS user and group profiles in RACF database.
- Create, update, delete, and purge RACF user and group profiles, and connect users to groups.
- Operations are performed using RACF TSO commands.
- For more details, see the \ `zos\_user <./zos_user.html>`__ documentation.





Parameters
----------


name
  The name of the RACF profile to manage.

  | **required**: True
  | **type**: str


profile_type
  Whether the RACF profile specified in :emphasis:`name` is a user or group profile.

  | **required**: True
  | **type**: str
  | **choices**: user, group


operation
  Specifies the operation to perform on the RACF profile.

  The available choices depend on the value of :emphasis:`profile\_type`.

  :literal:`create` \- Creates a new profile. Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  :literal:`update` \- Modifies an existing profile. Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  :literal:`delete` \- Removes the profile from RACF database, but may leave references to the profile in other RACF profiles or database records. Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  :literal:`purge` \- Completely removes the profile and all associated references from the RACF database. Unloads the RACF database using :literal:`IRRDBU00`\ , identifies all references via :literal:`IRRRID00`\ , and executes the necessary commands to remove them. See \ `https://www.ibm.com/docs/en/zos/3.2.0?topic=database\-using\-racf\-unload\-utility\-irrdbu00 <https://www.ibm.com/docs/en/zos/3.2.0?topic=database-using-racf-unload-utility-irrdbu00>`__ and \ `https://www.ibm.com/docs/en/zos/3.2.0?topic=database\-using\-racf\-remove\-id\-irrrid00\-utility <https://www.ibm.com/docs/en/zos/3.2.0?topic=database-using-racf-remove-id-irrrid00-utility>`__

  :literal:`connect` \- Links a user to a group. Only supported when :emphasis:`profile\_type=user`.

  :literal:`remove` \- Removes a user from a group. Only supported when :emphasis:`profile\_type=user`.

  | **required**: True
  | **type**: str
  | **choices**: create, update, delete, purge, connect, remove


database
  Name of the RACF database to use for the purge operation.

  This option is only applicable when :emphasis:`operation=purge`.

  | **required**: False
  | **type**: str


keep_dump
  Whether to keep the database dump data sets after the purge operation completes.

  This option is only applicable when :emphasis:`operation=purge`.

  When set to :literal:`true`\ , the IRRDBU00 dump data set and IRRRID00 CLIST is retained for debugging or auditing purposes.

  When set to :literal:`false`\ , these temporary data sets are deleted after the purge operation.

  | **required**: False
  | **type**: bool
  | **default**: False


optimize_dump
  Whether to skip locking the RACF database during the dump operation to optimize performance.

  This option is only applicable when :emphasis:`operation=purge`.

  When set to :literal:`true`\ , the IRRDBU00 utility runs with the :literal:`NOLOCKINPUT` option. This improves system availability by allowing concurrent updates to the database. However, it may result in inconsistent data if changes occur during the process.

  The user ID requires :literal:`READ` authority to the RACF database when using :literal:`NOLOCKINPUT`.

  When set to :literal:`false`\ , the IRRDBU00 utility runs with the :literal:`LOCKINPUT` option. This ensures data consistency by locking the database, but it prevents other processes from updating RACF profiles until the dump completes.

  The user ID requires :literal:`UPDATE` authority to the RACF database when using :literal:`LOCKINPUT`.

  See \ `https://www.ibm.com/docs/en/zos/3.2.0?topic=irrdbu00\-allowable\-parameters <https://www.ibm.com/docs/en/zos/3.2.0?topic=irrdbu00-allowable-parameters>`__ for more information about :literal:`LOCKINPUT` and :literal:`NOLOCKINPUT`.

  | **required**: False
  | **type**: bool
  | **default**: True


execute_clist
  Whether to execute the generated CLIST.

  This option is only applicable when :emphasis:`operation=purge`.

  When set to :literal:`true`\ , the module generates the CLIST, removes the safety :literal:`EXIT` statement, and executes the DELUSER/DELGROUP commands.

  When set to :literal:`false`\ , the module generates the CLIST but does not execute it.

  This option is useful for reviewing the purge commands before execution.

  | **required**: False
  | **type**: bool
  | **default**: True


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary data sets.

  This option is only applicable when :emphasis:`operation=purge`.

  Temporary data sets are created during the purge operation for database dumps, CLIST generation, and intermediate processing.

  If not specified, the system default HLQ is used.

  | **required**: False
  | **type**: str


base_segment
  Configures the RACF BASE segment attributes.

  The BASE segment contains core profile information applicable to both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  Supported attributes include :literal:`display\_name`\ , :literal:`model`\ , :literal:`owner`\ , :literal:`installation\_data`\ , and :literal:`custom\_fields`.

  Note that :literal:`display\_name` is only valid when :emphasis:`profile\_type=user`.

  | **required**: False
  | **type**: dict


  display_name
    Display name for the user profile (not the userid).

    This corresponds to the RACF NAME parameter.

    Maximum length of 20 characters.

    This option is only valid for user profiles (\ :emphasis:`profile\_type=user`\ ).

    This option is only applicable when :emphasis:`operation=create` or :emphasis:`operation=update`.

    If omitted, RACF will display UNKNOWN when listing the user.

    To remove/reset the display name to default (UNKNOWN), set this to an empty string :literal:`""`.

    | **required**: False
    | **type**: str


  model
    Name of an existing RACF profile to use as a model.

    Attributes not explicitly specified will be copied from the model profile.

    To remove the model field from the profile, set :literal:`model=""`.

    | **required**: False
    | **type**: str


  owner
    Specifies the user or group profile name to set as the owner.

    | **required**: False
    | **type**: str


  installation_data
    Installation\-defined data to store in the profile.

    Maximum length of 255 characters.

    The module automatically encloses the contents in single quotation marks.

    To remove the installation data from the profile, set :literal:`installation\_data=""`.

    | **required**: False
    | **type**: str


  custom_fields
    Custom fields to store with the profile.

    | **required**: False
    | **type**: dict


    add
      Custom fields to add to the profile.

      Each custom field should be a :literal:`key: value` pair.

      This option is valid when :literal:`operation=create` or :literal:`operation=update`.

      This option is mutually exclusive with :literal:`delete` and :literal:`delete\_block`

      | **required**: False
      | **type**: dict


    delete
      List of custom fields to delete.

      This option is only valid when :literal:`operation=update`\ ; it is ignored for all other values of operation.

      This option is mutually exclusive with :literal:`add` and :literal:`delete\_block`.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete_block
      Delete the whole custom fields block from the profile.

      This option is only valid when :literal:`operation=update`\ ; it is ignored for all other values of operation, including :literal:`operation=create`.

      This option is mutually exclusive with :literal:`add` and :literal:`delete`.

      | **required**: False
      | **type**: bool




group
  Options that change group\-specific attributes in a RACF profile.

  Only valid when :literal:`profile\_type=group`\ , ignored for user profiles.

  | **required**: False
  | **type**: dict


  superior_group
    specifies the name of a group profile to set as the superior group.

    | **required**: False
    | **type**: str


  terminal_access
    Whether to allow the use of the universal access authority for a terminal during authorization checking.

    | **required**: False
    | **type**: bool


  universal_group
    Whether the group should be allowed to have an unlimited number of users.

    | **required**: False
    | **type**: bool



dfp
  Options that set DFP attributes from the Storage Management Subsystem (SMS).

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
    Setting to :literal:`true` deletes the whole DFP block from the profile.

    This option is only valid when :literal:`operation=update`\ , it is ignored for all other values of operation including :literal:`operation=create`.

    This option is mutually exclusive with every other option in this section.

    | **required**: False
    | **type**: bool



language
  Options that set the preferred national languages for a user profile.

  These options override the system\-wide defaults.

  | **required**: False
  | **type**: dict


  primary
    Specifies the user's primary language.

    Value should be either a 3 character\-long language code or an installation\-defined name of up to 24 characters.

    To delete this field from the profile, set :literal:`primary=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  secondary
    Specifies the user's secondary language.

    Value should be either a 3 character\-long language code or an installation\-defined name of up to 24 characters.

    To delete this field from the profile, set :literal:`secondary=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  delete
    Setting to :literal:`true` deletes the whole LANGUAGE block from the profile.

    This option is only valid when :literal:`operation=update`\ , it is ignored for all other values of operation, including :literal:`operation=create`.

    This option is mutually exclusive with :literal:`primary` and :literal:`secondary`.

    | **required**: False
    | **type**: bool



omvs
  Attributes for the RACF OMVS segment.

  Configures z/OS Unix System Services access and resource limits for the profile.

  Valid for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  | **required**: False
  | **type**: dict


  uid
    Specifies how RACF should assign UIDs to users or GIDs to groups.

    This option is valid when :literal:`operation=create` and :literal:`operation=update`

    :literal:`none` deletes the user or group identifier from the OMVS segment of the profile. This is only valid when :literal:`operation=update`\ , it is ignored for all other values of operation including :literal:`operation=create`.

    :literal:`custom` and :literal:`shared` require :literal:`custom\_uid` to be defined.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: auto, custom, shared, none


  custom_uid
    Specifies the OMVS identifier for the profile.

    For :emphasis:`profile\_type=user`\ , this is the UID; for :emphasis:`profile\_type=group`\ , this is the GID.

    A number between 0 and 2,147,483,647.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  home
    Path name for the z/OS Unix System Services home directory.

    Maximum length of 1023 characters.

    To remove the home from the profile, set :literal:`home=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  program
    Specifies the path to the shell program when the user logs in.

    Maximum length of 1023 characters.

    To remove the program from the profile, set :literal:`program=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  nonshared_size
    Maximum number of bytes of nonshared memory that can be allocated by the user.

    Value between 0 and 16,777,215.

    Set to \-1 to remove the limit (NOMEMLIMIT). When set to :literal:`\-1`\ , :literal:`nonshared\_size\_unit` is ignored.

    Unit is specified separately via :literal:`nonshared\_size\_unit`\ , defaults to 'm' (megabytes) if not specified.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  nonshared_size_unit
    The unit for the nonshared memory size.

    Only used when :literal:`nonshared\_size` is specified and not set to \-1.

    Ignored when :literal:`nonshared\_size` is \-1.

    Defaults to 'm' (megabytes) if not specified.

    | **required**: False
    | **type**: str
    | **choices**: m, g, t, p


  shared_size
    Maximum number of bytes of shared memory that can be allocated by the user.

    Value between 1 and 16,777,215.

    Set to \-1 to remove the limit (NOSHMEMMAX). When set to \-1, :literal:`shared\_size\_unit` is ignored.

    Unit is specified separately via :literal:`shared\_size\_unit`\ , defaults to 'm' (megabytes) if not specified.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  shared_size_unit
    The unit for the shared memory size.

    Only used when :literal:`shared\_size` is specified and not set to \-1.

    Ignored when :literal:`shared\_size` is \-1.

    Defaults to 'm' (megabytes) if not specified.

    | **required**: False
    | **type**: str
    | **choices**: m, g, t, p


  addr_space_size
    Address space region size in bytes.

    Maximum address space size for the profile.

    Value between 10,485,760 and 2,147,483,647.

    A value of 0 sets this field to None.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  map_size
    Maximum amount of data space storage that can be allocated by the user.

    This option represents the number of memory pages, not bytes, available.

    Value between 1 and 16,777,216.

    A value of 0 sets this field to NONE.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  max_procs
    Maximum number of processes the user is allowed to have active at the same time.

    Value between 3 and 32,767.

    A value of 0 sets this field to NONE.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  max_threads
    Maximum number of threads the user can have concurrently active.

    Value between 0 and 100,000.

    A value of \-1 sets this field to NONE.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  max_cpu_time
    Specifies the RLIMIT\_CPU hard limit. Indicates the cpu\-time that a user process is allowed to use.

    Value between 7 and 2,147,483,647 seconds.

    A value of 0 sets this field to NONE.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  max_files
    Maximum number of files the user is allowed to have concurrently active or open.

    Value between 3 and 524,287.

    A value of 0 sets this field to NONE.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  delete
    Setting to :literal:`true` deletes the whole OMVS block from the profile.

    This option is only valid when :literal:`operation=update`\ ; it is ignored for all other operation values, including :literal:`operation=create`.

    This option is mutually exclusive with :literal:`uid`\ , :literal:`custom\_uid`\ , :literal:`home`\ , :literal:`program`\ , :literal:`nonshared\_size`\ , :literal:`nonshared\_size\_unit`\ , :literal:`shared\_size`\ , :literal:`shared\_size\_unit`\ , :literal:`addr\_space\_size`\ , :literal:`map\_size`\ , :literal:`max\_procs`\ , :literal:`max\_threads`\ , :literal:`max\_cpu\_time`\ , and :literal:`max\_files`.

    | **required**: False
    | **type**: bool



tso
  Attributes for the RACF TSO segment.

  Configures TSO settings for the user profile.

  only valid for :emphasis:`profile\_type=user`\ , :emphasis:`operation=create` and :emphasis:`operation=update`.

  | **required**: False
  | **type**: dict


  account_num
    Specifies the user's default TSO account number at logon.

    Maximum length of 39 characters.

    To delete this field from the profile, set :literal:`account\_num=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  logon_cmd
    Specifies the command to run during TSO/E logon.

    Maximum length of 80 characters.

    This option keeps case.

    To delete this field from the profile, set :literal:`logon\_cmd=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  logon_proc
    Specifies the user's default logon procedure.

    The value for this field is 1 to 8 alphanumeric characters.

    To delete this field from the profile, set :literal:`logon\_proc=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  dest_id
    Specifies the default destination for dynamically allocated SYSOUT data sets.

    The value for this field is 1 to 7 alphanumeric characters.

    To delete this field from the profile, set :literal:`dest\_id=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  hold_class
    Specifies the user's default hold class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :literal:`hold\_class=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  job_class
    Specifies the user's default job class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :literal:`job\_class=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  msg_class
    Specifies the user's default message class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :literal:`msg\_class=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  sysout_class
    Specifies the user's default SYSOUT class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :literal:`sysout\_class=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  region_size
    Specifies the minimum region size if none is requested at logon.

    A value between 0 and 2,096,128.

    When :literal:`region\_size=\-1` is set, this field is set to :literal:`00000000`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  max_region_size
    Specifies the maximum region size that can be requested at logon.

    A value between 0 and 2,096,128.

    When :literal:`max\_region\_size=\-1` is set, this field is set to :literal:`00000000`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  security_label
    Specifies the user's security label on the TSO logon panel.

    To delete this field from the profile, set :literal:`security\_label=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  unit_name
    Specifies the default device or device group name used for allocations.

    The value for this field is 1 to 8 alphanumeric characters.

    To delete this field from the profile, set :literal:`unit\_name=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  user_data
    Specifies optional installation data for the user profile.

    Must be 4 EBCDIC characters.

    When :literal:`user\_data=""` is set, this field is set to :literal:`0000`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  delete
    Setting to :literal:`true` deletes the whole TSO block from the profile.

    This option is only valid when :literal:`operation=update`\ ; it is ignored for all other values, including :literal:`operation=create`.

    This option is mutually exclusive with :literal:`account\_num`\ , :literal:`logon\_cmd`\ , :literal:`logon\_proc`\ , :literal:`dest\_id`\ , :literal:`hold\_class`\ , :literal:`job\_class`\ , :literal:`msg\_class`\ , :literal:`sysout\_class`\ , :literal:`region\_size`\ , :literal:`max\_region\_size`\ , :literal:`security\_label`\ , :literal:`unit\_name`\ , and :literal:`user\_data`.

    | **required**: False
    | **type**: bool



connect
  Options that configure a user's connection to a group.

  Only valid when :literal:`operation=connect`\ ; ignored for all other operation values.

  | **required**: False
  | **type**: dict


  authority
    Specifies the level of group authority assigned to the user.

    | **required**: False
    | **type**: str
    | **choices**: use, create, connect, join


  universal_access
    Specifies the level of universal access authority assigned for the connection.

    | **required**: False
    | **type**: str
    | **choices**: alter, control, update, read, none


  group_name
    Specifies the group to which the user will be connected.

    The other options in this block apply to this group.

    If omitted, RACF uses a default group. It is recommended to specify this option when connecting a user to a group.

    | **required**: False
    | **type**: str


  group_account
    Whether the user's protected data sets are accessible to other users in the group.

    | **required**: False
    | **type**: bool
    | **default**: False


  group_operations
    Whether the user should have the group\-OPERATIONS attribute for the connection.

    | **required**: False
    | **type**: bool
    | **default**: False


  auditor
    Whether the user should have auditor privileges for the connected group.

    | **required**: False
    | **type**: bool
    | **default**: False


  adsp_attribute
    Whether to assign the ADSP attribute for the connection.

    This attribute tells RACF to automatically protect data sets the user creates with discrete profiles.

    | **required**: False
    | **type**: bool
    | **default**: False


  special
    Whether to assign the SPECIAL attribute for the connection.

    This attribute allows the user to change attributes of other profiles.

    | **required**: False
    | **type**: bool
    | **default**: False



access
  Options that configure security attributes for a user profile.

  Only valid for :emphasis:`profile\_type=user`

  | **required**: False
  | **type**: dict


  default_group
    Specifies the RACF default group for the user profile.

    | **required**: False
    | **type**: str


  clauth
    Classes in which the user is allowed to define profiles to RACF for protection.

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
    Whether the user should have full responsibility for auditing the use of system resources.

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
    Whether the user is authorized to perform maintenance operations on all RACF\-protected DASD data sets, tape volumes, and DASD volumes.

    | **required**: False
    | **type**: bool
    | **default**: False


  restricted
    Whether the profile should have the RESTRICTED attribute.

    | **required**: False
    | **type**: bool
    | **default**: False


  security_label
    Specifies the security label applied to the profile.

    To delete this field from the profile, set :literal:`security\_label=""`.

    | **required**: False
    | **type**: str


  security_level
    Specifies the security level applied to the profile.

    To delete this field from the profile, set :literal:`security\_level=""`.

    | **required**: False
    | **type**: str



operator
  Configures the RACF OPERPARM segment attributes.

  The OPERPARM segment contains extended MCS console session attributes for the user.

  Only valid when :emphasis:`profile\_type=user`.

  Supported for :emphasis:`operation=create` and :emphasis:`operation=update`.

  | **required**: False
  | **type**: dict


  alt_group
    The console group used in recovery operations.

    Must be between 1 and 8 characters in length.

    To delete this field from the profile, set :literal:`alt\_group=""`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  authority
    The console's authority to issue operator commands.

    :literal:`master` \- Full authority to issue all commands.

    :literal:`all` \- Authority to issue all commands except those requiring master authority.

    :literal:`info` \- Authority to issue information\-only commands.

    :literal:`cons` \- Authority to issue console\-related commands.

    :literal:`io` \- Authority to issue I/O\-related commands.

    :literal:`sys` \- Authority to issue system\-related commands.

    :literal:`delete` \- Removes this field from the profile.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: master, all, info, cons, io, sys, delete


  cmd_system
    The system to which commands from this console are sent.

    Specify 1 to 8 characters.

    To remove this field from the profile, set to an empty string (\ :literal:`""`\ ).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  search_key
    The name used to display information for all consoles with the specified key.

    Use the MVS command :literal:`DISPLAY CONSOLES,KEY` to view consoles by this key.

    Length must be between 1 and 8 characters.

    To remove this field from the profile, set to an empty string (\ :literal:`""`\ ).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str


  migration_id
    Whether a 1\-byte migration ID should be assigned to this console.

    :literal:`yes` \- Assigns a migration ID to the console (MIGID).

    :literal:`no` \- Explicitly sets the console to not have a migration ID.

    :literal:`delete` \- Removes the migration ID parameter from the profile (NOMIGID).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  display
    The information displayed when monitoring jobs, TSO sessions, or data set status.

    :literal:`jobnames` \- Display job names.

    :literal:`jobnamest` \- Display job names with timestamps.

    :literal:`sess` \- Display TSO session information.

    :literal:`sesst` \- Display TSO session information with timestamps.

    :literal:`status` \- Display status information.

    :literal:`delete` \- Removes this field from the profile.

    Multiple values can be specified.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **choices**: jobnames, jobnamest, sess, sesst, status, delete


  msg_level
    The messages that this console receives.

    :literal:`nb` \- Non\-broadcast messages only.

    :literal:`all` \- All messages.

    :literal:`r` \- Routing messages.

    :literal:`i` \- Information messages.

    :literal:`ce` \- Critical and eventual action messages.

    :literal:`e` \- Eventual action messages.

    :literal:`in` \- Immediate and eventual action messages.

    :literal:`delete` \- Removes this field from the profile.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: nb, all, r, i, ce, e, in, delete


  msg_format
    The format in which messages are displayed at the console.

    :literal:`j` \- Job\-related format.

    :literal:`m` \- Mixed format.

    :literal:`s` \- Short format.

    :literal:`t` \- Time\-stamped format.

    :literal:`x` \- Extended format.

    :literal:`delete` \- Removes this field from the profile.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: j, m, s, t, x, delete


  msg_storage
    The amount of storage in the TSO/E user's address space for message queuing to the console.

    Specify a value between :literal:`1` and :literal:`2000`.

    Set to :literal:`0` to reset this field to :literal:`00000`.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: int


  msg_scope
    The systems from which this console can receive messages not directed to a specific console.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: dict


    add
      Adds new systems to the message scope list.

      When :emphasis:`operation=create`\ , this sets the initial message scope (MSCOPE).

      When :emphasis:`operation=update`\ , this adds systems to the existing list (ADDMSCOPE).

      This option is mutually exclusive with :emphasis:`remove` and :emphasis:`delete`.

      | **required**: False
      | **type**: list
      | **elements**: str


    remove
      Removes all message scope systems from the profile.

      This sets the profile to have no message scope (NOMSCOPE).

      This option is mutually exclusive with :emphasis:`add` and :emphasis:`delete`.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete
      Deletes specific systems from the message scope list.

      This removes only the specified systems from the existing list (DELMSCOPE).

      This option is mutually exclusive with :emphasis:`add` and :emphasis:`remove`.

      | **required**: False
      | **type**: list
      | **elements**: str



  automated_msgs
    Whether the extended console can receive messages automated by the Message Flood Automation (MFA).

    :literal:`yes` \- Enables the console to receive automated messages (AUTO).

    :literal:`no` \- Explicitly disables automated messages for the console.

    :literal:`delete` \- Removes the automated messages parameter from the profile (NOAUTO).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  del_msgs
    The delete operator message (DOM) requests the console can receive.

    :literal:`normal` \- Normal delete requests.

    :literal:`all` \- All delete requests.

    :literal:`none` \- No delete requests.

    :literal:`delete` \- Removes this field from the profile.

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: normal, all, none, delete


  hardcopy_msgs
    Whether the console receives all messages directed to hardcopy.

    :literal:`yes` \- Enables the console to receive hardcopy messages (HC).

    :literal:`no` \- Explicitly disables hardcopy messages for the console.

    :literal:`delete` \- Removes the hardcopy messages parameter from the profile (NOHC).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  internal_msgs
    Whether the console receives messages directed to console ID zero.

    :literal:`yes` \- Enables the console to receive internal messages (INTIDS).

    :literal:`no` \- Explicitly disables internal messages for the console.

    :literal:`delete` \- Removes the internal messages parameter from the profile (NOINTIDS).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  routing_msgs
    The routing codes of messages this operator receives.

    Specify :literal:`ALL` to receive all routing codes.

    Specify :literal:`NONE` to receive no routing codes.

    Specify :literal:`delete` as a single\-element list to remove all routing codes from the profile (NOROUTCODE).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: list
    | **elements**: str


  undelivered_msgs
    Whether the console receives undelivered messages.

    :literal:`yes` \- Enables the console to receive undelivered messages (UD).

    :literal:`no` \- Explicitly disables undelivered messages for the console.

    :literal:`delete` \- Removes the undelivered messages parameter from the profile (NOUD).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  unknown_msgs
    Whether the console receives messages directed to unknown console IDs.

    :literal:`yes` \- Enables the console to receive unknown messages (UNKNIDS).

    :literal:`no` \- Explicitly disables unknown messages for the console.

    :literal:`delete` \- Removes the unknown messages parameter from the profile (NOUNKNIDS).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  responses
    Whether command responses should be logged.

    :literal:`yes` \- Enables logging of command responses (LOGCMDRESP(SYSTEM)).

    :literal:`no` \- Explicitly disables logging of command responses (LOGCMDRESP(NO)).

    :literal:`delete` \- Removes the command response logging parameter from the profile (NOLOGCMDRESP).

    This option is mutually exclusive with :literal:`delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  delete
    When set to :literal:`true`\ , deletes the entire OPERPARM segment from the profile.

    This option is only valid when :emphasis:`operation=update`\ ; it is ignored for all other operation values.

    This option is mutually exclusive with :literal:`alt\_group`\ , :literal:`authority`\ , :literal:`cmd\_system`\ , :literal:`search\_key`\ , :literal:`migration\_id`\ , :literal:`display`\ , :literal:`msg\_level`\ , :literal:`msg\_format`\ , :literal:`msg\_storage`\ , :literal:`msg\_scope`\ , :literal:`automated\_msgs`\ , :literal:`del\_msgs`\ , :literal:`hardcopy\_msgs`\ , :literal:`internal\_msgs`\ , :literal:`routing\_msgs`\ , :literal:`undelivered\_msgs`\ , :literal:`unknown\_msgs`\ , and :literal:`responses`.

    | **required**: False
    | **type**: bool



restrictions
  Attributes that determine the days and times a user is allowed to login.

  | **required**: False
  | **type**: dict


  days
    Days of the week that a user is allowed to login.

    Multiple choices are allowed.

    Valid values are :literal:`anyday`\ , :literal:`weekdays`\ , :literal:`monday`\ , :literal:`tuesday`\ , :literal:`wednesday`\ , :literal:`thursday`\ , :literal:`friday`\ , :literal:`saturday` and :literal:`sunday`.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **default**: ['anyday']
    | **choices**: anyday, weekdays, monday, tuesday, wednesday, thursday, friday, saturday, sunday


  time
    Daily time period when the user is allowed to login.

    The value for this option must be in the format HHMM:HHMM.

    This field uses a 24\-hour format.

    This field also accepts the value :literal:`anytime` to indicate a user is free to login at any time of the day.

    | **required**: False
    | **type**: str
    | **default**: anytime


  resume
    Date when the user is allowed access to a system again.

    The value for this option must be in the format MM/DD/YY, where :literal:`YY` are the last two digits of the year.

    | **required**: False
    | **type**: str


  delete_resume
    Delete the resume field from the profile.

    This option is only valid when connecting a user to a group.

    This option is mutually exclusive with :emphasis:`resume`.

    | **required**: False
    | **type**: bool


  revoke
    Date when the user is forbidden access to a system.

    The value for this option must be in the format MM/DD/YY, where :literal:`YY` are the last two digits of the year.

    | **required**: False
    | **type**: str


  delete_revoke
    Delete the revoke field from the profile.

    This option is only valid when connecting a user to a group.

    This option is mutually exclusive with :emphasis:`revoke`.

    | **required**: False
    | **type**: bool



password_mgmt
  Options that manage password and passphrase settings for a user profile.

  These options are only valid for user profiles (\ :emphasis:`profile\_type=user`\ ).

  These options are only applicable when :emphasis:`operation=create` or :emphasis:`operation=update`.

  | **required**: False
  | **type**: dict


  password
    Password for the user.

    Maximum length of 8 characters.

    When creating a user, if neither :emphasis:`password` nor :emphasis:`passphrase` is specified, RACF will not assign a password and the user will need to be assigned one before they can log in.

    When a password is set for the first time during user creation, RACF marks it as EXPIRED by default. To change this, update the user with :emphasis:`expired=false` after creation.

    An empty string will remove the password and set it to NOPASSWORD.

    It is recommended to use Ansible Vault to encrypt this value.

    This option is mutually exclusive with :emphasis:`passphrase`.

    | **required**: False
    | **type**: str


  passphrase
    Passphrase for the user.

    Minimum length of 9 characters, maximum length of 100 characters.

    When creating a user, if neither :emphasis:`password` nor :emphasis:`passphrase` is specified, RACF will not assign a password and the user will need to be assigned one before they can log in.

    When a passphrase is set for the first time during user creation, RACF marks it as EXPIRED by default. To change this, update the user with :emphasis:`expired=false` after creation.

    An empty string will remove the passphrase and set it to NOPHRASE.

    It is recommended to use Ansible Vault to encrypt this value.

    This option is mutually exclusive with :emphasis:`password`.

    | **required**: False
    | **type**: str


  expired
    Whether the password or passphrase should be marked as expired.

    When :literal:`true`\ , the user will be required to change their password/passphrase on next login.

    When :literal:`false`\ , the password/passphrase will be marked as NOEXPIRED.

    This option is only applicable when :emphasis:`operation=update`.

    This option :strong:`must` be used together with :emphasis:`password` or :emphasis:`passphrase` in the same task. RACF requires a password/passphrase to be specified when using EXPIRED/NOEXPIRED.

    When a password/passphrase is set for the first time during user creation, RACF automatically marks it as EXPIRED. To change it to NOEXPIRED, you must update the user and specify the same password/passphrase again with :literal:`expired=false`.

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
       operation: create
       profile_type: group

   - name: Create a user with full name and owner.
     zos_user:
       name: newuser
       operation: create
       profile_type: user
       base_segment:
         display_name: John Doe
         owner: admin

   - name: Update a user's full name.
     zos_user:
       name: existusr
       operation: update
       profile_type: user
       base_segment:
         display_name: Jane Smith

   - name: Remove a user's full name (sets to UNKNOWN).
     zos_user:
       name: existusr
       operation: update
       profile_type: user
       base_segment:
         display_name: ""

   - name: Create a new group profile using another group as a model and setting its owner.
     zos_user:
       name: newgrp
       operation: create
       profile_type: group
       base_segment:
         model: oldgrp
         owner: admin

   - name: Create a new group profile and set group attributes.
     zos_user:
       name: newgrp
       operation: create
       profile_type: group
       group:
         superior_group: sys1
         terminal_access: true
         universal_group: false

   - name: Update a group profile to change its installation data and remove custom fields.
     zos_user:
       name: usergrp
       operation: update
       profile_type: group
       base_segment:
         installation_data: New installation data
         custom_fields:
           delete_block: true

   - name: Create a user using RACF defaults.
     zos_user:
       name: newuser
       operation: create
       profile_type: user

   - name: Create a user using another profile as a model.
     zos_user:
       name: newuser
       operation: create
       profile_type: user
       base_segment:
         model: olduser

   - name: Create a user and set how Unix System Services should behave when it logs in.
     zos_user:
       name: newuser
       operation: create
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
       operation: create
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
       operation: update
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
       operation: connect
       profile_type: user
       connect:
         group_name: usergrp

   - name: Connect a user to a group and give it special permissions.
     zos_user:
       name: user
       operation: connect
       profile_type: user
       connect:
         group_name: usergrp
         authority: connect
         universal_access: alter
         group_account: true
         group_operations: true
         auditor: true
         adsp_attribute: true
         special: true

   - name: Remove a user from a group.
     zos_user:
       name: user
       operation: remove
       profile_type: user
       connect:
         group_name: usergrp

   - name: Delete a user from the RACF database.
     zos_user:
       name: user
       operation: delete
       profile_type: user

   - name: Delete group from the RACF database.
     zos_user:
       name: usergrp
       operation: delete
       profile_type: group

   - name: Purge user from RACF database
     zos_user:
       name: user
       operation: purge
       profile_type: user
       database: racf_db

   - name: Purge group from RACF database
     zos_user:
       name: newgrp
       operation: purge
       profile_type: group
       database: racf_db

   - name: Create a user with password (will be marked as EXPIRED by default)
     zos_user:
       name: newuser
       operation: create
       profile_type: user
       password_mgmt:
         password: "{{ user_password }}"

   - name: Create a user with passphrase (will be marked as EXPIRED by default)
     zos_user:
       name: newuser
       operation: create
       profile_type: user
       password_mgmt:
         passphrase: "{{ user_passphrase }}"

   - name: Update user password to NOEXPIRED
     zos_user:
       name: newuser
       operation: update
       profile_type: user
       password_mgmt:
         password: "{{ user_password }}"
         expired: false
       omvs:
         uid: auto





Notes
-----

.. note::
   This module requires appropriate RACF authority to execute commands.

   For standard operations (create, update, delete, connect, remove), the user executing the module must have sufficient RACF authority to perform the requested operation (typically SPECIAL or group\-SPECIAL attribute).

   For purge operations using IRRDBU00 utility \- When :emphasis:`optimize\_dump=true` (default), IRRDBU00 runs with PARM=NOLOCKINPUT requiring READ authority to the input RACF database data sets. When :emphasis:`optimize\_dump=false`\ , IRRDBU00 runs with PARM=LOCKINPUT requiring UPDATE authority to lock the database during the unload.

   The IRRRID00 utility is used during purge operations to identify residual references and generate a CLIST of removal commands. The user must have READ authority to the input data set (the unloaded RACF database produced by IRRDBU00).

   To execute the generated CLIST from IRRRID00, the user must have sufficient RACF authority \- DELUSER/DELGROUP requires the SPECIAL attribute, group\-SPECIAL (within scope), or ownership of the target profile/superior group.



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
  Message returned by the module. Contains error messages on failure,
informational messages when no changes are needed (e.g., entity already exists),
or validation error messages.

  | **returned**: always
  | **type**: str
  | **sample**: An error occurred while executing the RACF command.

rc
  Return code from the RACF command execution.

  | **returned**: always
  | **type**: int

stdout
  Standard output from the RACF command execution.
In check mode, may contain informational messages about the entity state.
For :emphasis:`operation=purge`\ , this includes technical details such as dump data set names and CLIST processing messages.

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
  Standard error from the RACF command execution.
TSO command output is automatically filtered out.

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
  Returns the number of profiles and references modified by the operation.
Set to :literal:`0` if no changes were made (e.g., the entity is already in the desired state).
Set to :literal:`1` for successful single\-entity operations (create, update, or delete).
For :emphasis:`operations=purge`\ , this reflects the total number of user and group entities deleted.

  | **returned**: always
  | **type**: int
  | **sample**: 1

entities_modified
  A list of profiles and references modified by the operation.
For :emphasis:`profile\_type=user`\ , operations (\ :literal:`create`\ , :literal:`update`\ , :literal:`delete`\ , :literal:`connect`\ , :literal:`remove`\ ): Contains the user profile name upon success.
For :emphasis:`profile\_type=group`\ , operations :literal:`create`\ , :literal:`update`\ , :literal:`delete`\ ): Contains the group profile name upon success.
For :emphasis:`operations=purge`\ , contains all users/groups IDs deleted by the CLIST.
Returns an empty list if no changes were necessary (e.g., entity is already in the desired state).

  | **returned**: always
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "DUSR1001"
        ]

database_dumped
  Whether the module used IRRDBU00 utility to dump the RACF database.
Set to :literal:`true` only when the purge operation successfully executes the :literal:`IRRDBU00` utility.
Only relevant when :emphasis:`operation=purge`.

  | **returned**: always
  | **type**: bool

dump_kept
  Indicates whether the RACF database dump was retained on the managed node.
This behavior is controlled by the :emphasis:`keep\_dump` input parameter.
Only relevant when :emphasis:`database\_dumped=true`.

  | **returned**: always
  | **type**: bool

dump_name
  The name of the data set containing the output from the :literal:`IRRDBU00` utility.
This field is only populated when both :emphasis:`database\_dumped` and :emphasis:`keep\_dump` are :literal:`true`.
Otherwise, this value returns :literal:`null`.

  | **returned**: always
  | **type**: str
  | **sample**: USER.BACKUP.RACF.DATABASE

