
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_user.py

.. _zos_user_module:


zos_user -- Manage user and group profiles in RACF
==================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The \ `zos\_user <./zos_user.html>`__ module executes RACF TSO commands that can manage user and group RACF profiles.
- The module can create, update and delete RACF profiles about them.





Parameters
----------


name
  Name of the RACF profile the module will operate on.

  | **required**: True
  | **type**: str


operation
  Specifies the operation to perform on the RACF profile.

  The available choices depend on the value of :emphasis:`scope`.

  :literal:`create` \- Creates a new profile. Supported for both :emphasis:`scope=user` and :emphasis:`scope=group`.

  :literal:`update` \- Modifies an existing profile. Supported for both :emphasis:`scope=user` and :emphasis:`scope=group`.

  :literal:`delete` \- Removes the profile from RACF but may leave residual references in the database. Supported for both :emphasis:`scope=user` and :emphasis:`scope=group`.

  :literal:`purge` \- Completely removes the profile and all associated references from the RACF database. Unloads the database using :literal:`IRRDBU00`\ , identifies all references via :literal:`IRRRID00`\ , and executes the necessary commands to remove them.

  :literal:`connect` \- Links a user to a group. Only supported when :emphasis:`scope=user`.

  :literal:`remove` \- Removes a user from a group. Only supported when :emphasis:`scope=user`.

  | **required**: True
  | **type**: str
  | **choices**: create, update, delete, purge, connect, remove


scope
  Whether the RACF profile specified in :emphasis:`name` is a user or group profile.

  | **required**: True
  | **type**: str
  | **choices**: user, group


database
  Name of the RACF database to use for the purge operation.

  This option is only applicable when :emphasis:`operation=purge`.

  | **required**: False
  | **type**: str


keep_dump
  Whether to keep the database dump datasets after the purge operation completes.

  This option is only applicable when :emphasis:`operation=purge`.

  When set to :literal:`true`\ , the IRRDBU00 dump dataset and IRRRID00 CLIST will be retained for debugging or auditing purposes.

  When set to :literal:`false`\ , these temporary datasets will be deleted after the purge operation.

  | **required**: False
  | **type**: bool
  | **default**: False


optimize_dump
  Whether to optimize the database dump operation without locking the input RACF database.

  This option is only applicable when :emphasis:`operation=purge`.

  When set to :literal:`true`\ , the IRRDBU00 utility runs with the :literal:`NOLOCKINPUT` option. This improves system availability by allowing concurrent updates to the database. However, it may result in inconsistent data if changes occur during the process.

  The user ID requires :literal:`READ` authority to the RACF database when using :literal:`NOLOCKINPUT`.

  When set to :literal:`false`\ , the IRRDBU00 utility runs with the :literal:`LOCKINPUT` option. This ensures data consistency by locking the database, but it prevents other processes from updating RACF profiles until the dump completes.

  The user ID requires :literal:`UPDATE` authority to the RACF database to permit the utility to :literal:`LOCKINPUT`.

  | **required**: False
  | **type**: bool
  | **default**: True


no_exec
  Whether to skip execution of generated clist.

  This option is only applicable when :emphasis:`operation=purge`.

  When set to :literal:`true`\ , the module will generate the CLIST with DELUSER/DELGROUP commands but will not execute it.

  When set to :literal:`false`\ , the CLIST will be generated and executed to purge the profiles.

  This option is useful for reviewing the purge commands before execution.

  | **required**: False
  | **type**: bool
  | **default**: False


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary data sets.

  This option is only applicable when :emphasis:`operation=purge`.

  Temporary data sets are created during the purge operation for database dumps, CLIST generation, and intermediate processing.

  If not specified, the system default HLQ will be used.

  | **required**: False
  | **type**: str


general
  Options that change common attributes in a RACF profile.

  | **required**: False
  | **type**: dict


  user_name
    Display name for the user profile(not the userid).

    This corresponds to the RACF NAME parameter.

    Maximum length of 20 characters.

    This option is only valid for user profiles (\ :emphasis:`scope=user`\ ).

    This option is only applicable when :emphasis:`operation=create` or :emphasis:`operation=update`.

    If omitted, RACF will display UNKNOWN when listing the user.

    To remove/reset the user name to default (UNKNOWN), set this to an empty string :literal:`""`.

    | **required**: False
    | **type**: str


  model
    RACF profile that will be used as a model for the profile being changed.

    An empty string will delete this field from the profile.

    | **required**: False
    | **type**: str


  owner
    Owner of the profile that is being changed.

    It can be a user or a group profile.

    | **required**: False
    | **type**: str


  installation_data
    Installation\-defined data that will be stored in the profile.

    Maximum length of 255 characters.

    The module will automatically enclose the contents in single quotation marks.

    An empty string will delete this field from the profile.

    | **required**: False
    | **type**: str


  custom_fields
    Custom fields that will be stored with the profile.

    | **required**: False
    | **type**: dict


    add
      Adds custom fields to this profile.

      Each custom field should be a :literal:`key: value` pair.

      | **required**: False
      | **type**: dict


    delete
      Deletes each custom field listed.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete_block
      Delete the whole custom fields block from the profile.

      This option is only valid when updating profiles, it will be ignored when creating one.

      This option is mutually exclusive with :literal:`add` and :literal:`delete`.

      | **required**: False
      | **type**: bool




group
  Options that change group\-specific attributes in a RACF profile.

  Only valid when changing a group profile, ignored for user profiles.

  | **required**: False
  | **type**: dict


  superior_group
    Superior group that will be assigned to the profile.

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
  Options that set DFP attributes from the Storage Management Subsystem.

  | **required**: False
  | **type**: dict


  data_app_id
    Name of a DFP data application.

    | **required**: False
    | **type**: str


  data_class
    Default data class for data set allocation.

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
    Delete the whole DFP block from the profile.

    This option is only valid when updating profiles, it will be ignored when creating one.

    This option is mutually exclusive with every other option in this section.

    | **required**: False
    | **type**: bool



language
  Options that set the preferred national languages for a user profile.

  These options will override the system\-wide defaults.

  | **required**: False
  | **type**: dict


  primary
    User's primary language.

    Value should be either a 3 character\-long language code or an installation\-defined name of up to 24 characters.

    An empty string will delete this field from the profile.

    | **required**: False
    | **type**: str


  secondary
    User's secondary language.

    Value should be either a 3 character\-long language code or an installation\-defined name of up to 24 characters.

    An empty string will delete this field from the profile.

    | **required**: False
    | **type**: str


  delete
    Delete the whole LANGUAGE block from the profile.

    This option is only valid when updating user profiles, it will be ignored when creating one.

    This option is mutually exclusive with every other option in this section.

    | **required**: False
    | **type**: bool



omvs
  Attributes for how Unix System Services should work under a profile.

  | **required**: False
  | **type**: dict


  uid
    How RACF should assign a user its UID.

    :literal:`none` will be ignored when creating a profile.

    :literal:`custom` and :literal:`shared` require :literal:`custom\_uid` too.

    | **required**: False
    | **type**: str
    | **choices**: auto, custom, shared, none


  custom_uid
    Specifies the profile's UID.

    A number between 0 and 2,147,483,647.

    | **required**: False
    | **type**: int


  home
    Path name for the z/OS Unix System Services home directory.

    Maximum length of 1023 characters.

    An empty string will delete this field from the profile.

    | **required**: False
    | **type**: str


  program
    Path of the shell program to use when the user logs in.

    Maximum length of 1023 characters.

    An empty string will delete this field from the profile.

    | **required**: False
    | **type**: str


  nonshared_size
    Maximum number of bytes of nonshared memory that can be allocated by the user.

    Must be a number between 0 and 16,777,215 suffixed by a unit.

    Valid units are m (megabytes), g (gigabytes), t (terabytes) or p (petabytes).

    An empty string will delete the current limit set.

    | **required**: False
    | **type**: str


  shared_size
    Maximum number of bytes of shared memory that can be allocated by the user.

    Must be a number between 1 and 16,777,215 suffixed by a unit.

    Valid units are m (megabytes), g (gigabytes), t (terabytes) or p (petabytes).

    An empty string will delete the current limit set.

    | **required**: False
    | **type**: str


  addr_space_size
    Address space region size in bytes.

    Value between 10,485,760 and 2,147,483,647.

    A value of 0 will delete this field from the profile.

    | **required**: False
    | **type**: int


  map_size
    Maximum amount of data space storage that can be allocated by the user.

    This option represents the number of memory pages, not bytes, available.

    Value between 1 and 16,777,216.

    A value of 0 will delete this field from the profile.

    | **required**: False
    | **type**: int


  max_procs
    Maximum number of processes the user is allowed to have active at the same time.

    Value between 3 and 32,767.

    A value of 0 will delete this field from the profile.

    | **required**: False
    | **type**: int


  max_threads
    Maximum number of threads the user can have concurrently active.

    Value between 0 and 100,000.

    A value of \-1 will delete this field from the profile.

    | **required**: False
    | **type**: int


  max_cpu_time
    Specifies the RLIMIT\_CPU hard limit. Indicates the cpu\-time that a user process is allowed to use.

    Value between 7 and 2,147,483,647 seconds.

    A value of 0 will delete this field from the profile.

    | **required**: False
    | **type**: int


  max_files
    Maximum number of files the user is allowed to have concurrently active or open.

    Value between 3 and 524,287.

    A value of 0 will delete this field from the profile.

    | **required**: False
    | **type**: int


  delete
    Delete the whole OMVS block from the profile.

    This option is only valid when updating profiles, it will be ignored when creating one.

    This option is mutually exclusive with every other option in this section.

    | **required**: False
    | **type**: bool



tso
  Attributes for how TSO should handle a user profile.

  | **required**: False
  | **type**: dict


  account_num
    User's default TSO account number when logging in.

    Maximum length of 40 characters.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  logon_cmd
    Command that needs to be run during TSO/E logon.

    Maximum length of 80 characters.

    This option keeps case.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  logon_proc
    User's default logon procedure.

    The value for this field is 1 to 8 alphanumeric characters.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  dest_id
    Default destination to which the user can route dynamically allocated SYSOUT data sets.

    The value for this field is 1 to 7 alphanumeric characters.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  hold_class
    User's default hold class.

    This option consists of 1 alphanumeric character.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  job_class
    User's default job class.

    This option consists of 1 alphanumeric character.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  msg_class
    User's default message class.

    This option consists of 1 alphanumeric character.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  sysout_class
    User's default SYSOUT class.

    This option consists of 1 alphanumeric character.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  region_size
    Minimum region size if the user does not request a region size at logon.

    A value between 0 and 2,096,128.

    A value of \-1 deletes this field.

    | **required**: False
    | **type**: int


  max_region_size
    Maximum region size that the user can request at logon.

    A value between 0 and 2,096,128.

    A value of \-1 deletes this field.

    | **required**: False
    | **type**: int


  security_label
    User's security label if the user specifies one on the TSO logon panel.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  unit_name
    Default name of a device or group of devices that a procedure uses for allocations.

    The value for this field is 1 to 8 alphanumeric characters.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  user_data
    Optional installation data defined for the user profile.

    Must be 4 EBCDIC characters.

    An empty value deletes this field.

    | **required**: False
    | **type**: str


  delete
    Delete the whole TSO block from the profile.

    This option is only valid when updating profiles, it will be ignored when creating one.

    This option is mutually exclusive with every other option in this section.

    | **required**: False
    | **type**: bool



connect
  Options that configure what a user can do inside a group that is connected to.

  These options are only used when :literal:`operation=connect` and they are ignored otherwise.

  | **required**: False
  | **type**: dict


  authority
    Level of group authority given to a user profile.

    | **required**: False
    | **type**: str
    | **choices**: use, create, connect, join


  universal_access
    Level of universal access authority given to a user profile.

    | **required**: False
    | **type**: str
    | **choices**: alter, control, update, read, none


  group_name
    Group to which the user will be connected to.

    The rest of the options in this block will affect this group.

    If not supplied, RACF will use a default group. It is recommended to specify this option when trying to connect a user to a group.

    | **required**: False
    | **type**: str


  group_account
    Whether the user's protected data sets are accessible to other users in the group.

    | **required**: False
    | **type**: bool
    | **default**: False


  group_operations
    Whether a user should have the group\-OPERATIONS attribute when connected to a group.

    | **required**: False
    | **type**: bool
    | **default**: False


  auditor
    Whether a user should have auditor privileges for the group it is connected to.

    | **required**: False
    | **type**: bool
    | **default**: False


  adsp_attribute
    Whether to give a user the ADSP attribute, which tells RACF to automatically protect data sets it creates with discrete profiles.

    | **required**: False
    | **type**: bool
    | **default**: False


  special
    Whether to give a user profile the SPECIAL attribute.

    This attribute lets a user change attributes of other profiles. Use with caution.

    | **required**: False
    | **type**: bool
    | **default**: False



access
  Options that set different security attributes in a user profile.

  | **required**: False
  | **type**: dict


  default_group
    RACF's default group for the user profile.

    | **required**: False
    | **type**: str


  clauth
    Classes in which a user is allowed to define profiles to RACF for protection.

    | **required**: False
    | **type**: dict


    add
      Adds classes to the profile.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete
      Removes classes from the profile.

      | **required**: False
      | **type**: list
      | **elements**: str



  roaudit
    Whether a user should have full responsibility for auditing the use of system resources.

    | **required**: False
    | **type**: bool
    | **default**: False


  category
    Security categories that the profile should have.

    | **required**: False
    | **type**: dict


    add
      Adds security categories to the profile.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete
      Removes security categories from the profile.

      | **required**: False
      | **type**: list
      | **elements**: str



  operator_card
    Whether a user must supply an operator identification card when logging in.

    | **required**: False
    | **type**: bool
    | **default**: False


  maintenance_access
    Whether the user has authorization to do maintenance operations on all RACF\-protected DASD data sets, tape volumes, and DASD volumes.

    | **required**: False
    | **type**: bool
    | **default**: False


  restricted
    Whether to give the profile the RESTRICTED attribute.

    | **required**: False
    | **type**: bool
    | **default**: False


  security_label
    Security label applied to the profile.

    Empty value deletes this field.

    | **required**: False
    | **type**: str


  security_level
    Security level applied to the profile.

    Empty value deletes this field.

    | **required**: False
    | **type**: str



operator
  Attributes used when a user establishes an extended MCS console session.

  | **required**: False
  | **type**: dict


  alt_group
    Console group used in recovery.

    Must be between 1 and 8 characters in length.

    Empty value deletes this field.

    | **required**: False
    | **type**: str


  authority
    Console's authority to issue operator commands.

    :literal:`delete` will remove the field from the profile.

    | **required**: False
    | **type**: str
    | **choices**: master, all, info, cons, io, sys, delete


  cmd_system
    System to which commands from this console are to be sent.

    Must be between 1 and 8 characters in length.

    Empty value deletes this field.

    | **required**: False
    | **type**: str


  search_key
    Name used to display information for all consoles with the specified key by using the MVS command :literal:`DISPLAY CONSOLES,KEY`.

    Must be between 1 and 8 characters in length.

    Empty value deletes this field.

    | **required**: False
    | **type**: str


  migration_id
    Whether a 1\-byte migration ID should be assigned to this console.

    | **required**: False
    | **type**: bool
    | **default**: False


  display
    Which information should be displayed when monitoring jobs, TSO sessions, or data set status.

    Possible values are :literal:`jobnames`\ , :literal:`jobnamest`\ , :literal:`sess`\ , :literal:`sesst`\ , :literal:`status` and :literal:`delete`.

    Multiple choices are allowed.

    :literal:`delete` will remove this field from the profile.

    | **required**: False
    | **type**: list
    | **elements**: str
    | **choices**: jobnames, jobnamest, sess, sesst, status, delete


  msg_level
    Specifies the messages that this console is to receive.

    :literal:`delete` will remove this field from the profile.

    | **required**: False
    | **type**: str
    | **choices**: nb, all, r, i, ce, e, in, delete


  msg_format
    Format in which messages are displayed at the console.

    :literal:`delete` will remove this field from the profile.

    | **required**: False
    | **type**: str
    | **choices**: j, m, s, t, x, delete


  msg_storage
    Specifies the amount of storage in the TSO/E user's address space that can be used for message queuing to the console.

    Its value can be a number between 1 and 2,000.

    A value of 0 deletes this field.

    | **required**: False
    | **type**: int


  msg_scope
    Systems from which this console can receive messages that are not directed to a specific console.

    | **required**: False
    | **type**: dict


    add
      Add new systems to this field.

      | **required**: False
      | **type**: list
      | **elements**: str


    remove
      Removes systems from this field.

      | **required**: False
      | **type**: list
      | **elements**: str


    delete
      Deletes the systems from this field.

      | **required**: False
      | **type**: list
      | **elements**: str



  automated_msgs
    Whether the extended console can receive messages that have been automated by the MFP.

    | **required**: False
    | **type**: bool
    | **default**: False


  del_msgs
    Which delete operator message (DOM) requests the console can receive.

    :literal:`delete` will remove the field from the profile.

    | **required**: False
    | **type**: str
    | **choices**: normal, all, none, delete


  hardcopy_msgs
    Whether the console should receive all messages that are directed to hardcopy.

    | **required**: False
    | **type**: bool
    | **default**: False


  internal_msgs
    Whether the console should receive messages that are directed to console ID zero.

    | **required**: False
    | **type**: bool
    | **default**: False


  routing_msgs
    Specifies the routing codes of messages this operator is to receive.

    :literal:`ALL` can be specified to receive all codes. Conversely, :literal:`NONE` can be used to receive none.

    | **required**: False
    | **type**: list
    | **elements**: str


  undelivered_msgs
    Whether the console should receive undelivered messages.

    | **required**: False
    | **type**: bool
    | **default**: False


  unknown_msgs
    Whether the console should receive messages that are directed to unknown console IDs.

    | **required**: False
    | **type**: bool
    | **default**: False


  responses
    Whether command responses should be logged.

    | **required**: False
    | **type**: bool
    | **default**: True


  delete
    Delete the whole OPERPARM block from the profile.

    This option is only valid when updating profiles, it will be ignored when creating one.

    This option is mutually exclusive with every other option in this section.

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

  These options are only valid for user profiles (\ :emphasis:`scope=user`\ ).

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
       scope: group

   - name: Create a user with full name and owner.
     zos_user:
       name: newuser
       operation: create
       scope: user
       general:
         user_name: John Doe
         owner: admin

   - name: Update a user's full name.
     zos_user:
       name: existusr
       operation: update
       scope: user
       general:
         user_name: Jane Smith

   - name: Remove a user's full name (sets to UNKNOWN).
     zos_user:
       name: existusr
       operation: update
       scope: user
       general:
         user_name: ""

   - name: Create a new group profile using another group as a model and setting its owner.
     zos_user:
       name: newgrp
       operation: create
       scope: group
       general:
         model: oldgrp
         owner: admin

   - name: Create a new group profile and set group attributes.
     zos_user:
       name: newgrp
       operation: create
       scope: group
       group:
         superior_group: sys1
         terminal_access: true
         universal_group: false

   - name: Update a group profile to change its installation data and remove custom fields.
     zos_user:
       name: usergrp
       operation: update
       scope: group
       general:
         installation_data: New installation data
         custom_fields:
           delete_block: true

   - name: Create a user using RACF defaults.
     zos_user:
       name: newuser
       operation: create
       scope: user

   - name: Create a user using another profile as a model.
     zos_user:
       name: newuser
       operation: create
       scope: user
       general:
         model: olduser

   - name: Create a user and set how Unix System Services should behave when it logs in.
     zos_user:
       name: newuser
       operation: create
       scope: user
       omvs:
         uid: auto
         home: /u/newuser
         program: /bin/sh
         nonshared_size: '10g'
         shared_size: '10g'
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
       scope: user
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
       scope: user
       general:
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
       scope: user
       connect:
         group_name: usergrp

   - name: Connect a user to a group and give it special permissions.
     zos_user:
       name: user
       operation: connect
       scope: user
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
       scope: user
       connect:
         group_name: usergrp

   - name: Delete a user from the RACF database.
     zos_user:
       name: user
       operation: delete
       scope: user

   - name: Delete group from the RACF database.
     zos_user:
       name: usergrp
       operation: delete
       scope: group

   - name: Purge user from RACF database
     zos_user:
       name: user
       operation: purge
       scope: user
       database: racf_db

   - name: Purge group from RACF database
     zos_user:
       name: newgrp
       operation: purge
       scope: group
       database: racf_db

   - name: Create a user with password (will be marked as EXPIRED by default)
     zos_user:
       name: newuser
       operation: create
       scope: user
       password_mgmt:
         password: "{{ user_password }}"

   - name: Create a user with passphrase (will be marked as EXPIRED by default)
     zos_user:
       name: newuser
       operation: create
       scope: user
       password_mgmt:
         passphrase: "{{ user_passphrase }}"

   - name: Update user password to NOEXPIRED
     zos_user:
       name: newuser
       operation: update
       scope: user
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

   The IRRRID00 utility is used during purge operations to identify residual references and generate a CLIST of removal commands. The user must have READ authority to the input dataset (the unloaded RACF database produced by IRRDBU00).

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
For :emphasis:`operation=purge`\ , this includes technical details such as dump dataset names and CLIST processing messages.

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
  Number of profiles and references modified by the operation.
Set to 0 when entity already exists or is already in desired state.
Set to 1 for successful single entity operations.
For purge operations, reflects the count of entities deleted.

  | **returned**: always
  | **type**: int
  | **sample**: 1

entities_modified
  List of all profiles and references modified by the operation.
For user scope operations (create, update, delete, connect, remove), contains the user profile name when successful.
For group scope operations (create, update, delete), contains the group profile name when successful.
For purge operations, contains all users/groups deleted by the CLIST.
Empty list when no changes are made (entity already exists or in desired state).

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
  The name of the dataset containing the output from the :literal:`IRRDBU00` utility.
This field is only populated when both :emphasis:`database\_dumped` and :emphasis:`keep\_dump` are :literal:`true`.
Otherwise, this value returns :literal:`null`.

  | **returned**: always
  | **type**: str
  | **sample**: USER.BACKUP.RACF.DATABASE

