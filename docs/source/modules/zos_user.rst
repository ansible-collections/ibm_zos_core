
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_user.py

.. _zos_user_module:


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
  Whether the RACF profile specified in :emphasis:`name` is a user or group profile.

  | **required**: True
  | **type**: str
  | **choices**: user, group


state
  Specifies the state to perform on the RACF profile.

  The available choices depend on the value of :emphasis:`profile\_type`.

  :literal:`create` \- Creates a new profile. Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  :literal:`update` \- Modifies an existing profile. Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  :literal:`delete` \- Removes the profile from RACF database, but may leave references to the profile in other RACF profiles or database records. Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  :literal:`purge` \- Completely removes the profile and all associated references from the RACF database. Unloads the RACF database using \ `IRRDBU00 <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-unload-utility-irrdbu00>`__\ , identifies all references via \ `IRRRID00 <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-remove-id-irrrid00-utility>`__\ , and executes the necessary commands to remove them.

  :literal:`connect` \- Links a user to a group. Only supported when :emphasis:`profile\_type=user`.

  :literal:`remove` \- Removes a user from a group. Only supported when :emphasis:`profile\_type=user`.

  | **required**: True
  | **type**: str
  | **choices**: create, update, delete, purge, connect, remove


database
  Name of the RACF database to use for the purge state.

  This option is only applicable when :emphasis:`state=purge`.

  | **required**: False
  | **type**: str


keep_dump
  Whether to keep the database dump data sets after the purge completes.

  This option is only applicable when :emphasis:`state=purge`.

  When set to :literal:`true`\ , the IRRDBU00 dump data set and IRRRID00 CLIST is retained for debugging or auditing purposes.

  When set to :literal:`false`\ , these temporary data sets are deleted after the purge.

  | **required**: False
  | **type**: bool
  | **default**: False


optimize_dump
  Whether to skip locking the RACF database during the dump state to optimize performance.

  This option is only applicable when :emphasis:`state=purge`.

  When set to :literal:`true`\ , the IRRDBU00 utility runs with the :literal:`NOLOCKINPUT` option. This improves system availability by allowing concurrent updates to the database. However, it may result in inconsistent data if changes occur during the process.

  The user ID requires :literal:`READ` authority to the RACF database when using :literal:`NOLOCKINPUT`.

  When set to :literal:`false`\ , the IRRDBU00 utility runs with the :literal:`LOCKINPUT` option. This ensures data consistency by locking the database, but it prevents other processes from updating RACF profiles until the dump completes.

  The user ID requires :literal:`UPDATE` authority to the RACF database when using :literal:`LOCKINPUT`.

  See \ `IRRDBU00 allowable parameters <https://www.ibm.com/docs/en/zos/latest?topic=irrdbu00-allowable-parameters>`__ for more information about :literal:`LOCKINPUT` and :literal:`NOLOCKINPUT`.

  | **required**: False
  | **type**: bool
  | **default**: True


execute_clist
  Whether to execute the generated CLIST.

  This option is only applicable when :emphasis:`state=purge`.

  When set to :literal:`true`\ , the module generates the CLIST, removes the safety :literal:`EXIT` statement, and executes the DELUSER/DELGROUP commands.

  When set to :literal:`false`\ , the module generates the CLIST but does not execute it.

  This option is useful for reviewing the purge commands before execution.

  | **required**: False
  | **type**: bool
  | **default**: True


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary data sets.

  This option is only applicable when :emphasis:`state=purge`.

  Temporary data sets are created during the purge for database dumps, CLIST generation, and intermediate processing.

  If not specified, the system default HLQ is used.

  | **required**: False
  | **type**: str


base_segment
  Configures the RACF BASE segment attributes.

  The BASE segment contains core profile information applicable to both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  Supported attributes include :emphasis:`display\_name`\ , :emphasis:`model`\ , :emphasis:`owner`\ , :emphasis:`installation\_data`\ , and :emphasis:`custom\_fields`.

  Note that :emphasis:`display\_name` is only valid when :emphasis:`profile\_type=user`.

  | **required**: False
  | **type**: dict


  display_name
    Display name for the user profile (the descriptive name shown in listings, not the 8\-character userid used for login).

    This corresponds to the RACF NAME parameter.

    For example, userid "JSMITH01" might have display\_name "John Smith".

    Maximum length of 20 characters.

    This option is only valid for user profiles (\ :emphasis:`profile\_type=user`\ ).

    This option is only applicable when :emphasis:`state=create` or :emphasis:`state=update`.

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

      Custom fields are specified as a dictionary of :literal:`key=value` pairs.

      This option is valid when :emphasis:`state=create` or :emphasis:`state=update`.

      This option is mutually exclusive with :emphasis:`delete` and :emphasis:`delete\_block`.

      Note \- Values containing colons should be enclosed in quotes to ensure correct YAML parsing in playbooks.

      | **required**: False
      | **type**: dict


    delete
      List of custom fields to delete.

      This option is only valid when :emphasis:`state=update`\ ; it is ignored for all other values of state.

      This option is mutually exclusive with :emphasis:`add` and :emphasis:`delete\_block`.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete_block
      Delete all custom fields from the profile.

      This removes the entire custom fields section, not just individual fields.

      Use :emphasis:`delete` to remove specific custom fields, or :emphasis:`delete\_block=true` to remove all custom fields at once.

      This option is only valid when :emphasis:`state=update`\ ; it is ignored for all other values of state, including :emphasis:`state=create`.

      This option is mutually exclusive with :emphasis:`add` and :emphasis:`delete`.

      | **required**: False
      | **type**: bool




group
  Options that change group\-specific attributes in a RACF profile.

  Only valid when :emphasis:`profile\_type=group`\ , ignored for user profiles.

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

    Valid only for :emphasis:`profile\_type=group`.

    This option is valid for :emphasis:`state=create` only.

    | **required**: False
    | **type**: bool



dfp
  Options that set DFP attributes from the Storage Management Subsystem (SMS).

  Supported for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group`.

  This option is applicable for :emphasis:`state=create` and :emphasis:`state=update`.

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

    This option is only valid when :emphasis:`state=update`\ , it is ignored for all other values of state including :emphasis:`state=create`.

    This option is mutually exclusive with :emphasis:`data\_app\_id`\ , :emphasis:`data\_class`\ , :emphasis:`management\_class` and :emphasis:`storage\_class`.

    | **required**: False
    | **type**: bool



language
  Options that set the preferred national languages for a :emphasis:`profile\_type=user`.

  Valid when :emphasis:`state=create` and :emphasis:`state=update`.

  These options override the system\-wide defaults.

  | **required**: False
  | **type**: dict


  primary
    Specifies the user's primary language.

    Value should be either a 3 character\-long language code or an installation\-defined name of up to 24 characters.

    To delete this field from the profile, set :emphasis:`primary=""`.

    This option is mutually exclusive with :emphasis:`delete`.

    | **required**: False
    | **type**: str


  secondary
    Specifies the user's secondary language.

    Value should be either a 3 character\-long language code or an installation\-defined name of up to 24 characters.

    To delete this field from the profile, set :emphasis:`secondary=""`.

    This option is mutually exclusive with :emphasis:`delete`.

    | **required**: False
    | **type**: str


  delete
    Setting to :literal:`true` deletes the whole LANGUAGE block from the profile.

    This option is only valid when :emphasis:`state=update`\ , it is ignored for all other values of state, including :emphasis:`state=create`.

    This option is mutually exclusive with :emphasis:`primary` and :emphasis:`secondary`.

    | **required**: False
    | **type**: bool



omvs
  Attributes for the RACF OMVS segment.

  Configures z/OS Unix System Services access and resource limits for the profile.

  Valid for both :emphasis:`profile\_type=user` and :emphasis:`profile\_type=group` are :emphasis:`uid`\ , :emphasis:`custom\_uid`\ , :emphasis:`delete`.

  Valid only for :emphasis:`profile\_type=user` are :emphasis:`home`\ , :emphasis:`program`\ , :emphasis:`nonshared\_size`\ , :emphasis:`shared\_size`\ , :emphasis:`addr\_space\_size`\ , :emphasis:`map\_size`\ , :emphasis:`max\_procs`\ , :emphasis:`max\_threads`\ , :emphasis:`max\_cpu\_time`\ , :emphasis:`max\_files`\ , and their related unit options.

  User\-only options control process and memory resource limits which do not apply to group profiles.

  | **required**: False
  | **type**: dict


  uid
    Specifies how RACF should assign UIDs to users or GIDs to groups.

    This option is valid when :emphasis:`state=create` and :emphasis:`state=update`

    :literal:`none` deletes the user or group identifier from the OMVS segment of the profile. This is only valid when :emphasis:`state=update`\ , it is ignored for all other values of state including :emphasis:`state=create`.

    :literal:`custom` and :literal:`shared` require :emphasis:`omvs.custom\_uid` to be defined.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: str
    | **choices**: auto, custom, shared, none


  custom_uid
    Specifies the OMVS identifier for the profile.

    For :emphasis:`profile\_type=user`\ , this is the UID; for :emphasis:`profile\_type=group`\ , this is the GID.

    A number between 0 and 2,147,483,647.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  home
    Specifies the path name for the z/OS Unix System Services home directory.

    Maximum length of 1023 characters.

    To remove the home from the profile, set :emphasis:`home=""`.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: str


  program
    Specifies the path to the shell program when the user logs in.

    Maximum length of 1023 characters.

    To remove the program from the profile, set :emphasis:`program=""`.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: str


  nonshared_size
    Specifies the maximum number of bytes of nonshared memory that can be allocated by the user.

    Value between 0 and 16,777,215.

    Set to :literal:`\-1` to remove the limit :literal:`NOMEMLIMIT`. When set to :literal:`\-1`\ , :emphasis:`nonshared\_size\_unit` is ignored.

    Unit is specified separately via :emphasis:`nonshared\_size\_unit`\ , defaults to 'm' (megabytes) if not specified.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  nonshared_size_unit
    Specifies the unit for the nonshared memory size.

    Only used when :emphasis:`nonshared\_size` is specified and not set to \-1.

    Ignored when :emphasis:`nonshared\_size` is \-1.

    Defaults to :literal:`m` (megabytes) if not specified.

    | **required**: False
    | **type**: str
    | **choices**: m, g, t, p


  shared_size
    Specifies the maximum number of bytes of shared memory that can be allocated by the user.

    Value between 1 and 16,777,215.

    Set to :literal:`\-1` to remove the limit :literal:`NOSHMEMMAX`. When set to :literal:`\-1`\ , :emphasis:`shared\_size\_unit` is ignored.

    Unit is specified separately via :emphasis:`shared\_size\_unit`\ , defaults to 'm' (megabytes) if not specified.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  shared_size_unit
    Specifies the unit for the shared memory size.

    Only used when :emphasis:`shared\_size` is specified and not set to \-1.

    Ignored when :emphasis:`shared\_size=\-1`.

    Defaults to :literal:`m` (megabytes) if not specified.

    | **required**: False
    | **type**: str
    | **choices**: m, g, t, p


  addr_space_size
    Specifies the maximum size of the address space region in bytes for the profile.

    Value between 10,485,760 and 2,147,483,647.

    Set to :literal:`0` to remove the user\-specific limit :literal:`NOASSIZEMAX`. This allows the system default from :literal:`BPXPRMxx` to apply.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  map_size
    Specifies the maximum amount of data space storage that can be allocated by the user.

    This option represents the number of memory pages, not bytes, available.

    Value between 1 and 16,777,216.

    Set this to :literal:`0` to remove the user\-specific limit (\ :literal:`NOMMAPAREAMAX`\ ). This allows the system default from :literal:`BPXPRMxx` to apply.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  max_procs
    Specifies the maximum number of processes the user is allowed to have active at the same time.

    Value between 3 and 32,767.

    Set this to :literal:`0` to remove the user\-specific limit (NOPROCUSERMAX). This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  max_threads
    Specifies the maximum number of threads the user can have concurrently active.

    Value between 0 and 100,000.

    Set this to :literal:`\-1` to remove the user\-specific limit (NOTHREADSMAX). This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  max_cpu_time
    Specifies the RLIMIT\_CPU hard limit. Indicates the cpu\-time that a user process is allowed to use.

    Value between 7 and 2,147,483,647 seconds.

    Set this to :literal:`0` to remove the user\-specific limit (NOCPUTIMEMAX). This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  max_files
    Specifies the maximum number of files the user is allowed to have concurrently active or open.

    Value between 3 and 524,287.

    Set this to :literal:`0` to remove the user\-specific limit :literal:`NOFILEPROCMAX`. This allows the system default from BPXPRMxx to apply.

    This option is mutually exclusive with :emphasis:`omvs.delete`.

    | **required**: False
    | **type**: int


  delete
    Setting to :literal:`true` deletes the whole OMVS block from the profile.

    This option is only valid when :emphasis:`state=update`\ ; it is ignored for all other state values, including :emphasis:`state=create`.

    This option is mutually exclusive with :emphasis:`uid`\ , :emphasis:`custom\_uid`\ , :emphasis:`home`\ , :emphasis:`program`\ , :emphasis:`nonshared\_size`\ , :emphasis:`nonshared\_size\_unit`\ , :emphasis:`shared\_size`\ , :emphasis:`shared\_size\_unit`\ , :emphasis:`addr\_space\_size`\ , :emphasis:`map\_size`\ , :emphasis:`max\_procs`\ , :emphasis:`max\_threads`\ , :emphasis:`max\_cpu\_time`\ , and :emphasis:`max\_files`.

    | **required**: False
    | **type**: bool



tso
  Attributes for the RACF TSO segment.

  Configures TSO settings for the user profile.

  Only valid for :emphasis:`profile\_type=user`\ , :emphasis:`state=create` and :emphasis:`state=update`.

  | **required**: False
  | **type**: dict


  account_num
    Specifies the user's default TSO account number at logon.

    Maximum length of 39 characters.

    To delete this field from the profile, set :emphasis:`account\_num=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  logon_cmd
    Specifies the command to run during TSO/E logon.

    Maximum length of 80 characters.

    This option is case\-sensitive.

    To delete this field from the profile, set :emphasis:`logon\_cmd=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  logon_proc
    Specifies the user's default logon procedure.

    The value for this field is 1 to 8 alphanumeric characters.

    To delete this field from the profile, set :emphasis:`logon\_proc=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  dest_id
    Specifies the default destination for dynamically allocated SYSOUT data sets.

    The value for this field is 1 to 7 alphanumeric characters.

    To delete this field from the profile, set :emphasis:`dest\_id=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  hold_class
    Specifies the user's default hold class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :emphasis:`hold\_class=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  job_class
    Specifies the user's default job class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :emphasis:`job\_class=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  msg_class
    Specifies the user's default message class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :emphasis:`msg\_class=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  sysout_class
    Specifies the user's default SYSOUT class.

    This option consists of 1 alphanumeric character.

    To delete this field from the profile, set :emphasis:`sysout\_class=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  region_size
    Specifies the minimum region size if none is requested at logon.

    A value between 0 and 2,096,128.

    When :emphasis:`region\_size=\-1` is set, this field is set to :literal:`00000000`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: int


  max_region_size
    Specifies the maximum region size that can be requested at logon.

    A value between 0 and 2,096,128.

    When :emphasis:`max\_region\_size=\-1` is set, this field is set to :literal:`00000000`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: int


  security_label
    Specifies the user's security label on the TSO logon panel.

    To delete this field from the profile, set :emphasis:`security\_label=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  unit_name
    Specifies the default device or device group name used for allocations.

    The value for this field is 1 to 8 alphanumeric characters.

    To delete this field from the profile, set :emphasis:`unit\_name=""`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  user_data
    Specifies optional installation data for the user profile.

    Must be exactly 4 characters (0–9, A–F only).

    When :emphasis:`user\_data=""`\ , this field is set to :literal:`0000`.

    This option is mutually exclusive with :emphasis:`tso.delete`.

    | **required**: False
    | **type**: str


  delete
    Setting to :literal:`true` deletes the whole TSO block from the profile.

    This option is only valid when :emphasis:`state=update`\ ; it is ignored for all other values, including :emphasis:`state=create`.

    This option is mutually exclusive with :emphasis:`account\_num`\ , :emphasis:`logon\_cmd`\ , :emphasis:`logon\_proc`\ , :emphasis:`dest\_id`\ , :emphasis:`hold\_class`\ , :emphasis:`job\_class`\ , :emphasis:`msg\_class`\ , :emphasis:`sysout\_class`\ , :emphasis:`region\_size`\ , :emphasis:`max\_region\_size`\ , :emphasis:`security\_label`\ , :emphasis:`unit\_name`\ , and :emphasis:`user\_data`.

    | **required**: False
    | **type**: bool



connect
  Options that configure a user's connection to a group.

  Only valid when :emphasis:`state=connect`\ ; ignored for all other state values.

  | **required**: False
  | **type**: dict


  authority
    Specifies the level of group authority assigned to the user for the connection.

    This determines what actions the user can perform within the group.

    If not specified when creating a connection, the default authority is :literal:`use`.

    :literal:`use` \- Allows access to resources authorized to the group.

    :literal:`create` \- Allows creation of RACF data set profiles for the group.

    :literal:`connect` \- Allows connecting other users to the group.

    :literal:`join` \- Allows adding users or subgroups to the group and assigning group authorities.

    See \ `Group Authorities <https://www.ibm.com/docs/en/zos/latest?topic=summary-group-authorities>`__.

    | **required**: False
    | **type**: str
    | **choices**: use, create, connect, join


  universal_access
    Specifies the level of universal access authority assigned for the connection.

    Specifies the level of universal access authority :literal:`(UACC`\ ) for resources associated with the connection.

    This value applies to new resource profiles created while the user is connected to the group.

    If not specified when creating a connection, the default value is :literal:`none`.

    :literal:`alter` \- Allows full access, including read, update, and delete.

    :literal:`control` \- Allows read and update access, and modification of the resource profile.

    :literal:`update` \- Allows read and update access.

    :literal:`read` \- Allows read\-only access.

    :literal:`none` \- Allows no access.

    | **required**: False
    | **type**: str
    | **choices**: alter, control, update, read, none


  group_name
    Specifies the group to connect the user to.

    If omitted, the user is connected to the current connect group.

    | **required**: False
    | **type**: str


  group_account
    Whether data sets defined by the user are accessible to other users in the group.

    When enabled, the group is given UPDATE access to data sets created by the user with the group as the high\-level qualifier.

    | **required**: False
    | **type**: bool
    | **default**: False


  group_operations
    Whether the user should has the group\-OPERATIONS attribute for the connection.

    Allows the user to perform maintenance operations on RACF\-protected data sets and resources within the scope of the group

    | **required**: False
    | **type**: bool
    | **default**: False


  auditor
    Whether the user has group\-AUDITOR attribute for the connection.

    Allows the user to list profiles connected to the group and review audit information for the group.

    This is independent of the system\-wide AUDITOR attribute (\ :emphasis:`access.auditor`\ ).

    A user can have group\-AUDITOR in one group but not in another.

    | **required**: False
    | **type**: bool
    | **default**: False


  auto_protect_datasets
    Whether the user has the group\-ADSP attribute for the specific group connection.

    Causes RACF to automatically create discrete profiles for permanent data sets created while the user is connected to the group.

    This is independent of the system\-wide ADSP attribute (\ :emphasis:`access.auto\_protect\_datasets`\ ).

    A user can have ADSP in one group but not in another.

    | **required**: False
    | **type**: bool
    | **default**: False


  special
    Whether the user has group\-SPECIAL attribute for the connection.

    Allows the user to manage profiles owned by the group and user connections to the group.

    This is independent of the system\-wide SPECIAL attribute (\ :emphasis:`access.special`\ ).

    A user can have group\-SPECIAL in one group but not in another.

    | **required**: False
    | **type**: bool
    | **default**: False



access
  Options that configure security attributes for a user profile.

  Only valid for :emphasis:`profile\_type=user`

  This option is valid for :emphasis:`state=create` and :emphasis:`state=update`.

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
    Specifies whether to assign the :literal:`ROAUDIT` attribute to the user.

    When enabled, the user has responsibility for auditing system resources with read\-only access to audit records and settings.

    In RACF output, this appears under the user's ATTRIBUTES list.

    Requires the :literal:`SPECIAL` attribute to modify.

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
    Whether the user profile should have the RESTRICTED attribute.

    When enabled, the user is denied access to resources via UACC or ID(\*). Access is only granted if the user or their group is explicitly added to the resource's access list.

    Also bypasses global access checking and z/OS UNIX other permission bits.

    | **required**: False
    | **type**: bool
    | **default**: False


  security_label
    Specifies the security label applied to the profile.

    To delete this field from the profile, set :emphasis:`security\_label=""`.

    | **required**: False
    | **type**: str


  security_level
    Specifies the security level applied to the profile.

    To delete this field from the profile, set :literal:`security\_level=""`.

    | **required**: False
    | **type**: str


  auto_protect_datasets
    Whether the user has the system\-wide ADSP (Automatic Data Set Protection) attribute.

    When enabled, RACF automatically defines a discrete profile for any new data set created by the user.

    This is a user profile attribute that applies globally across all groups.

    Different from :emphasis:`connect.auto\_protect\_datasets` which applies only to a specific group connection.

    | **required**: False
    | **type**: bool
    | **default**: False


  auditor
    Whether the user has the system\-wide AUDITOR attribute.

    Provides responsibility for auditing the use of system resources.

    Allows the user to review audit records and control logging of accesses to RACF\-protected resource

    This is a user profile attribute that applies globally across all groups.

    Different from :emphasis:`connect.auditor` which provides group\-AUDITOR authority for a specific group only.

    | **required**: False
    | **type**: bool
    | **default**: False


  authority
    Specifies the user's default group authority level.

    This is used as the default when connecting the user to groups if :emphasis:`connect.authority` is not specified.

    Also applies to the user's default group (DFLTGRP) connection.

    :literal:`use` \- Allows the user to access resources to which the group is authorized.

    :literal:`create` \- Allows the user to create RACF data set profiles for the group.

    :literal:`connect` \- Allows the user to connect other users to the group.

    :literal:`join` \- Allows the user to add users or subgroups to the group and assign group authorities..

    Can be overridden per\-group using :emphasis:`connect.authority`.

    See \ `Group Authorities <https://www.ibm.com/docs/en/zos/latest?topic=summary-group-authorities>`__.

    | **required**: False
    | **type**: str
    | **choices**: use, create, connect, join


  special
    Whether the user has the system\-wide SPECIAL attribute.

    Allows the user to issue most RACF commands and manage RACF profiles and user IDs system\-wide.

    This is a user profile attribute that applies globally across all groups.

    Different from :emphasis:`connect.special` which provides group\-SPECIAL authority for a specific group only.

    | **required**: False
    | **type**: bool
    | **default**: False


  universal_access
    Specifies the user's default universal access authority (UACC).

    This value applies to new resource profiles created while the user is connected to a group.

    It is used when :emphasis:`connect.universal\_access` is not specified during group connection.

    Also applies to the user's default group (DFLTGRP) connection

    The user can have different UACC values for each group connection.

    :literal:`alter` \- Allows full access, including read, update, delete, rename, and control of the resource profile.

    :literal:`control` \- Allows read and update access, and the ability to modify the resource profile.

    :literal:`update` \- Allows read and update access to the resource.

    :literal:`read` \- Allows read\-only access to the resource.

    :literal:`none` \- Allows no access to the resource.

    Can be overridden per group using :emphasis:`connect.universal\_access`.

    | **required**: False
    | **type**: str
    | **choices**: alter, control, update, read, none



operator
  Configures the RACF OPERPARM segment attributes.

  The OPERPARM segment defined extended MCS console session attributes for the user.

  Only valid when :emphasis:`profile\_type=user`.

  Supported for :emphasis:`state=create` and :emphasis:`state=update`.

  | **required**: False
  | **type**: dict


  alt_group
    The console group used in recovery operations.

    Must be between 1 and 8 characters in length.

    To delete this field from the profile, set :emphasis:`alt\_group=""`.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str


  authority
    The console authority level for issuing operator commands.

    :literal:`master` \- Full authority to issue all commands.

    :literal:`all` \- Authority to issue all commands except those requiring master authority.

    :literal:`info` \- Authority to issue information\-only commands.

    :literal:`cons` \- Authority to issue console\-related commands.

    :literal:`io` \- Authority to issue I/O\-related commands.

    :literal:`sys` \- Authority to issue system\-related commands.

    :literal:`delete` \- Removes this field from the profile.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: master, all, info, cons, io, sys, delete


  cmd_system
    The system to which commands from this console are sent.

    Specify 1 to 8 characters.

    To remove this field from the profile, set :emphasis:`cmd\_system=""`.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str


  search_key
    The name used to display information for all consoles with the specified key.

    Use the MVS command :literal:`DISPLAY CONSOLES,KEY` to view consoles by this key.

    Length must be between 1 and 8 characters.

    To remove this field from the profile, set :emphasis:`search\_key=""`.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str


  migration_id
    Whether a 1\-byte migration ID should be assigned to this console.

    :literal:`yes` \- Assigns a migration ID to the console (MIGID).

    :literal:`no` \- Explicitly sets the console to not have a migration ID.

    :literal:`delete` \- Removes the migration ID parameter from the profile (NOMIGID).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  display
    List of information to display when monitoring jobs, TSO sessions, or data set status.

    :literal:`jobnames` \- Display job names.

    :literal:`jobnamest` \- Display job names with timestamps.

    :literal:`sess` \- Display TSO session information.

    :literal:`sesst` \- Display TSO session information with timestamps.

    :literal:`status` \- Display status information.

    :literal:`delete` \- Removes this field from the profile.

    Multiple values can be specified.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **choices**: jobnames, jobnamest, sess, sesst, status, delete


  msg_level
    Specifies the message levels that the Extended MCS (EMCS) console associated with this user profile receives.

    This attribute acts as a filter for the messages routed to the user's console session.

    :literal:`r` \- The console receives messages requiring an operator reply.

    :literal:`i` \- The console receives immediate action messages.

    :literal:`ce` \- The console receives critical eventual action messages.

    :literal:`e` \- The console receives eventual action messages.

    :literal:`in` \- The console receives informational messages.

    :literal:`nb` \- The console receives no broadcast messages.

    :literal:`all` \- The console receives all message levels :literal:`(R, I, CE, E, and IN`\ ).

    :literal:`delete` \- Removes the message level field from the user's profile.

    This option is mutually exclusive with :emphasis:`operator.delete`.

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

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: j, m, s, t, x, delete


  msg_storage
    The amount of storage in the TSO/E user's address space for message queuing to the console.

    Specify a value between :literal:`1` and :literal:`2000`.

    Set to :literal:`0` to reset this field to :literal:`00000`.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: int


  msg_scope
    Specifies the systems from which the Extended MCS (EMCS) console associated with this user profile receives unsolicited messages (messages not directed to a specific console).

    This field updates the OPERPARM segment of the RACF user profile.

    :literal:`\*` \- The console receives messages only from the system on which the console session is currently active.

    :literal:`\*all` \- The console receives messages from all systems in the sysplex.

    :literal:`system\_names` \- A list of one or more specific system names (e.g., SYS1, SYS2) to define the scope.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: dict


    add
      List of new systems to add to the message scope list.

      When :emphasis:`state=create`\ , this sets the initial message scope :literal:`(MSCOPE`\ ).

      When :emphasis:`state=update`\ , this adds systems to the existing list :literal:`(ADDMSCOPE`\ ).

      This option is mutually exclusive with :emphasis:`msg\_scope.remove` and :emphasis:`msg\_scope.delete`.

      | **required**: False
      | **type**: list
      | **elements**: str


    remove
      Set to :literal:`true` to remove all message scope systems from the profile :literal:`(NOMSCOPE`\ ).

      This option is mutually exclusive with :emphasis:`msg\_scope.add` and :emphasis:`msg\_scope.delete`.

      | **required**: False
      | **type**: bool


    delete
      List of specific systems to delete from the message scope list :literal:`(DELMSCOPE`\ ).

      This does not clear the entire list unless all listed systems are specified.

      This option is mutually exclusive with :emphasis:`msg\_scope.add` and :emphasis:`msg\_scope.remove`.

      | **required**: False
      | **type**: list
      | **elements**: str



  automated_msgs
    Whether the extended console can receive messages automated by the Message Flood Automation (MFA).

    :literal:`yes` \- Enables the console to receive automated messages :literal:`(AUTO`\ ).

    :literal:`no` \- Explicitly disables automated messages for the console.

    :literal:`delete` \- Removes the automated messages parameter from the profile :literal:`(NOAUTO`\ ).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  delete_operator_msgs
    Specifies which Delete Operator Message (DOM) requests the Extended MCS (EMCS) console associated with this user profile can receive.

    :literal:`normal` \- The system queues all appropriate local DOM requests to the console.

    :literal:`all` \- All systems in the sysplex queue DOM requests to the console.

    :literal:`none` \- No DOM requests are queued to the console.

    :literal:`delete` \- Removes the DOM field from the user profile. This corresponds to the RACF :literal:`NODOM` operand.

    Note that when this field is deleted or omitted :literal:`NODOM`\ , the DOM information will not appear in profile listings (e.g., :literal:`LU` command), and the EMCS console will default to :literal:`normal` behavior when a session is established.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: normal, all, none, delete


  hardcopy_msgs
    Whether the console receives all messages directed to hardcopy.

    :literal:`yes` \- Enables the console to receive hardcopy messages :literal:`(HC`\ ).

    :literal:`no` \- Explicitly disables hardcopy messages for the console.

    :literal:`delete` \- Removes the hardcopy messages parameter from the profile :literal:`(NOHC`\ ).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  internal_msgs
    Whether the console receives messages directed to console ID zero.

    :literal:`yes` \- Enables the console to receive internal messages :literal:`(INTIDS`\ ).

    :literal:`no` \- Explicitly disables internal messages for the console.

    :literal:`delete` \- Removes the internal messages parameter from the profile :literal:`(NOINTIDS`\ ).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  routing_msgs
    The routing codes of messages this operator receives.

    Accepts one of the following (mutually exclusive).

    :literal:`["ALL"]` \- Receive all routing codes.

    :literal:`["NONE"]` \- Receive no routing codes.

    :literal:`["delete"]` \- Removes routing code information from the profile (NOROUTCODE).

    List of routing codes \- One or more routing codes (integers 1\-128) or sequences (ranges).

    Examples \- :literal:`["1"]`\ , :literal:`["1", "2", "11"]`\ , :literal:`["1\-5"]`\ , :literal:`["1\-5", "10", "20\-25"]`.

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: list
    | **elements**: str


  undelivered_msgs
    Whether the console receives undelivered messages.

    :literal:`yes` \- Enables the console to receive undelivered messages :literal:`(UD`\ ).

    :literal:`no` \- Explicitly disables undelivered messages for the console.

    :literal:`delete` \- Removes the undelivered messages parameter from the profile :literal:`(NOUD`\ ).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  unknown_msgs
    Whether the console receives messages directed to unknown console IDs.

    :literal:`yes` \- Enables the console to receive unknown messages :literal:`(UNKNIDS`\ ).

    :literal:`no` \- Explicitly disables unknown messages for the console.

    :literal:`delete` \- Removes the unknown messages parameter from the profile :literal:`(NOUNKNIDS`\ ).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  log_responses
    Whether command responses should be logged.

    :literal:`yes` \- Enables logging of command responses :literal:`(LOGCMDRESP(SYSTEM`\ )).

    :literal:`no` \- Explicitly disables logging of command responses :literal:`(LOGCMDRESP(NO`\ )).

    :literal:`delete` \- Removes the command response logging parameter from the profile :literal:`(NOLOGCMDRESP`\ ).

    This option is mutually exclusive with :emphasis:`operator.delete`.

    | **required**: False
    | **type**: str
    | **choices**: yes, no, delete


  delete
    When set to :literal:`true`\ , deletes the entire OPERPARM segment from the profile.

    This option is only valid when :emphasis:`state=update`\ ; it is ignored for all other state values.

    This option is mutually exclusive with :emphasis:`alt\_group`\ , :emphasis:`authority`\ , :emphasis:`cmd\_system`\ , :emphasis:`search\_key`\ , :emphasis:`migration\_id`\ , :emphasis:`display`\ , :emphasis:`msg\_level`\ , :emphasis:`msg\_format`\ , :emphasis:`msg\_storage`\ , :emphasis:`msg\_scope`\ , :emphasis:`automated\_msgs`\ , :emphasis:`delete\_operator\_msgs`\ , :emphasis:`hardcopy\_msgs`\ , :emphasis:`internal\_msgs`\ , :emphasis:`routing\_msgs`\ , :emphasis:`undelivered\_msgs`\ , :emphasis:`unknown\_msgs`\ , and :emphasis:`log\_responses`.

    | **required**: False
    | **type**: bool



restrictions
  Attributes that determine the days and times a user is allowed to login.

  This option is valid for :emphasis:`profile\_type=user`.

  | **required**: False
  | **type**: dict


  days
    Days of the week that a user is allowed to login.

    Multiple choices are allowed.

    Valid values are :literal:`anyday`\ , :literal:`weekdays`\ , :literal:`monday`\ , :literal:`tuesday`\ , :literal:`wednesday`\ , :literal:`thursday`\ , :literal:`friday`\ , :literal:`saturday` and :literal:`sunday`.

    This option is valid for :emphasis:`state=create` and :emphasis:`state=update`.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **default**: ['anyday']
    | **choices**: anyday, weekdays, monday, tuesday, wednesday, thursday, friday, saturday, sunday


  time
    Daily time period when the user is allowed to login.

    The value for this option must be in the format :literal:`"HHMM:HHMM"`.

    Enclose the time value in quotes (for example, "0900:1700") to avoid YAML parsing issues.

    This field uses a 24\-hour format.

    This field also accepts the value :literal:`anytime` to indicate a user is free to login at any time of the day.

    This option is valid for :emphasis:`state=create` and :emphasis:`state=update`.

    | **required**: False
    | **type**: str
    | **default**: anytime


  resume
    Date when the user is allowed access to a system again.

    The value for this option must be in the format :literal:`MM/DD/YY`\ , where :literal:`YY` are the last two digits of the year.

    This option is valid for :emphasis:`state=connect` and :emphasis:`state=update`.

    | **required**: False
    | **type**: str


  delete_resume
    Delete the resume field from the profile.

    This option is valid for :emphasis:`state=connect` and :emphasis:`state=update`.

    This option is mutually exclusive with :emphasis:`restrictions.resume`.

    | **required**: False
    | **type**: bool


  revoke
    Date when the user is forbidden access to a system.

    The value for this option must be in the format :literal:`MM/DD/YY`\ , where :literal:`YY` are the last two digits of the year.

    This option is valid for :emphasis:`state=connect` and :emphasis:`state=update`.

    | **required**: False
    | **type**: str


  delete_revoke
    Delete the revoke field from the profile.

    This option is valid for :emphasis:`state=connect` and :emphasis:`state=update`.

    This option is mutually exclusive with :emphasis:`restrictions.revoke`.

    | **required**: False
    | **type**: bool



password_mgmt
  Options that manage password and passphrase settings for a user profile.

  These options are only valid for user profiles (\ :emphasis:`profile\_type=user`\ ).

  These options are only applicable when :emphasis:`state=create` or :emphasis:`state=update`.

  | **required**: False
  | **type**: dict


  password
    Password for the user.

    Maximum length of 8 characters.

    When creating a user, if neither :emphasis:`password` nor :emphasis:`passphrase` is specified, no password is assigned. The user must be assigned one before logging in.

    When a password is set for the first time during user creation, RACF marks it as EXPIRED by default. To allow the user to use the password without an immediate change, update the user with :emphasis:`expired=false` after creation.

    :emphasis:`password=""` removes the password and sets the NOPASSWORD attribute on the user profile.

    It is highly recommended to use :strong:`Ansible Vault` to encrypt this value.

    This option is mutually exclusive with :emphasis:`passphrase`.

    | **required**: False
    | **type**: str


  passphrase
    Passphrase for the user.

    Minimum length of 9 characters, maximum length of 100 characters.

    When creating a user, if neither :emphasis:`password` nor :emphasis:`passphrase` is specified, no password or passphrase is assigned. The user must be assigned one before logging in.

    When a passphrase is set for the first time during user creation, RACF marks it as EXPIRED by default. To change this, update the user with :emphasis:`expired=false` after creation.

    Setting :emphasis:`passphrase=""` removes the passphrase and sets the NOPHRASE attribute on the user profile.

    It is recommended to use Ansible Vault to encrypt this value.

    This option is mutually exclusive with :emphasis:`password`.

    | **required**: False
    | **type**: str


  expired
    Whether the password or passphrase should be marked as expired.

    When :literal:`true`\ , the user will be required to change their password/passphrase on next login.

    When :literal:`false`\ , the password/passphrase will be marked as NOEXPIRED.

    This option is only applicable when :emphasis:`state=update`.

    This option :strong:`must` be used together with :emphasis:`password` or :emphasis:`passphrase` in the same task. RACF requires a password/passphrase to be specified when using :literal:`EXPIRED/NOEXPIRED`.

    When a password/passphrase is set for the first time during user creation, RACF automatically marks it as :literal:`EXPIRED`. To change it to :literal:`NOEXPIRED`\ , you must update the user and specify the same password/passphrase again with :emphasis:`expired=false`.

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
         group_account: true
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

   For standard states (create, update, delete, connect, remove), the user executing the module must have sufficient RACF authority to perform the requested state (typically :literal:`SPECIAL` or :literal:`group\-SPECIAL` attribute).

   For purge state using the \ `IRRDBU00 utility <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-unload-utility-irrdbu00>`__\ , When :emphasis:`optimize\_dump=true` (default), IRRDBU00 runs with :literal:`PARM=NOLOCKINPUT` requiring :literal:`READ` authority to the input RACF database data sets. When :emphasis:`optimize\_dump=false`\ , IRRDBU00 runs with :literal:`PARM=LOCKINPUT` requiring :literal:`UPDATE` authority to lock the database during the unload.

   The \ `IRRRID00 <https://www.ibm.com/docs/en/zos/latest?topic=database-using-racf-remove-id-irrrid00-utility>`__ utility is used during purge operations to identify residual references and generate a :literal:`CLIST` of removal commands. The user must have :literal:`READ` authority to the input data set (the unloaded RACF database produced by IRRDBU00).

   To execute the generated :literal:`CLIST` from IRRRID00, the user must have sufficient RACF authority \- :literal:`DELUSER/DELGROUP` requires the :literal:`SPECIAL` attribute, :literal:`group\-SPECIAL` (within scope), or ownership of the target profile/superior group.



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
For :emphasis:`state=purge`\ , this includes technical details such as dump data set names and CLIST processing messages.

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
  Returns the number of profiles and references modified by the state.
Set to :literal:`0` if no changes were made (e.g., :literal:`the entity is already in the desired state`\ ).
Set to :literal:`1` for successful single\-entity states :literal:`create, update, or delete`.
For :emphasis:`state=purge`\ , this reflects the total number of user and group entities deleted.

  | **returned**: always
  | **type**: int
  | **sample**: 1

entities_modified
  A list of profiles and references modified by the state.
For :emphasis:`profile\_type=user`\ , state (\ :literal:`create`\ , :literal:`update`\ , :literal:`delete`\ , :literal:`connect`\ , :literal:`remove`\ ): Contains the user profile name upon success.
For :emphasis:`profile\_type=group`\ , state :literal:`create`\ , :literal:`update`\ , :literal:`delete`\ ): Contains the group profile name upon success.
For :emphasis:`state=purge`\ , contains all users/groups IDs deleted by the CLIST.
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
Set to :literal:`true` only when the purge state successfully executes the :literal:`IRRDBU00` utility.
Only relevant when :emphasis:`state=purge`.

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

