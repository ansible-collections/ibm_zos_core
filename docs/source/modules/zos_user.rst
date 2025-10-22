.. _zos_user_module:


zos_user -- Manage user and group profiles in RACF
==================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

The \ `zos\_user <./zos_user.html>`__ module executes RACF TSO commands that can manage user and group RACF profiles.

The module can create, update and delete RACF profiles, as well as list information about them.






Parameters
----------

  name (True, str, None)
    Name of the RACF profile the module will operate on.


  operation (True, str, None)
    RACF command that will be executed.

    Group profiles can be created, updated, listed, deleted and purged.

    User profiles can use any of the choices.

    :literal:`delete` will run a RACF :literal:`DELGROUP` or a :literal:`DELUSER` TSO command. This will remove the profile but not every reference in the RACF database.

    :literal:`purge` will execute the RACF utility IRRDBU00, thereby removing all references of a profile from the RACF database.

    :literal:`connect` will add a given user profile to a group. :literal:`remove` will remove the user from a group.


  scope (True, str, None)
    Whether commands should affect a user or a group profile.


  general (False, dict, None)
    Options that change common attributes in a RACF profile.


    model (False, str, None)
      RACF profile that will be used as a model for the profile being changed.

      An empty string will delete this field from the profile.


    owner (False, str, None)
      Owner of the profile that is being changed.

      It can be a user or a group profile.


    installation_data (False, str, None)
      Installation-defined data that will be stored in the profile.

      Maximum length of 255 characters.

      The module will automatically enclose the contents in single quotation marks.

      An empty string will delete this field from the profile.


    custom_fields (False, dict, None)
      Custom fields that will be stored with the profile.


      add (False, dict, None)
        Adds custom fields to this profile.

        Each custom field should be a :strong:`ERROR while parsing`\ : While parsing "C(key" at index 31 of paragraph 1: Cannot find closing ")" after last parameter


      delete (False, list, None)
        Deletes each custom field listed.


      delete_block (required, bool, None)
        Delete the whole custom fields block from the profile.

        This option is only valid when updating profiles, it will be ignored when creating one.

        This option is mutually exclusive with :literal:`add` and :literal:`delete`.




  group (False, dict, None)
    Options that change group-specific attributes in a RACF profile.

    Only valid when changing a group profile, ignored for user profiles.


    superior_group (False, str, None)
      Superior group that will be assigned to the profile.


    terminal_access (False, bool, None)
      Whether to allow the use of the universal access authority for a terminal during authorization checking.


    universal_group (False, bool, None)
      Whether the group should be allowed to have an unlimited number of users.



  dfp (False, dict, None)
    Options that set DFP attributes from the Storage Management Subsytem.


    data_app_id (False, str, None)
      Name of a DFP data application.


    data_class (False, str, None)
      Default data class for data set allocation.


    management_class (False, str, None)
      Default management class for data set migration and backup.


    storage_class (False, str, None)
      Default storage class for data set space, device and volume.


    delete (False, bool, None)
      Delete the whole DFP block from the profile.

      This option is only valid when updating profiles, it will be ignored when creating one.

      This option is mutually exclusive with every other option in this section.



  language (False, dict, None)
    Options that set the preferred national languages for a user profile.

    These options will override the system-wide defaults.


    primary (False, str, None)
      User's primary language.

      Value should be either a 3 character-long language code or an installation-defined name of up to 24 characters.

      An empty string will delete this field from the profile.


    secondary (False, str, None)
      User's secondary language.

      Value should be either a 3 character-long language code or an installation-defined name of up to 24 characters.

      An empty string will delete this field from the profile.


    delete (False, bool, None)
      Delete the whole LANGUAGE block from the profile.

      This option is only valid when updating user profiles, it will be ignored when creating one.

      This option is mutually exclusive with every other option in this section.



  omvs (False, dict, None)
    Attributes for how Unix System Services should work under a profile.


    uid (False, str, None)
      How RACF should assign a user its UID.

      :literal:`none` will be ignored when creating a profile.

      :literal:`custom` and :literal:`shared` require :literal:`custom\_uid` too.


    custom_uid (False, int, None)
      Specifies the profile's UID.

      A number between 0 and 2,147,483,647.


    home (False, str, None)
      Path name for the z/OS Unix System Services home directory.

      Maximum length of 1023 characters.

      An empty string will delete this field from the profile.


    program (False, str, None)
      Path of the shell program to use when the user logs in.

      Maximum length of 1023 characters.

      An empty string will delete this field from the profile.


    nonshared_size (False, str, None)
      Maximum number of bytes of nonshared memory that can be allocated by the user.

      Must be a number between 0 and 16,777,215 subfixed by a unit.

      Valid units are m (megabytes), g (gigabytes), t (terabytes) or p (petabytes).

      An empty string will delete the current limit set.


    shared_size (False, str, None)
      Maximum number of bytes of shared memory that can be allocated by the user.

      Must be a number between 1 and 16,777,215 subfixed by a unit.

      Valid units are m (megabytes), g (gigabytes), t (terabytes) or p (petabytes).

      An empty string will delete the current limit set.


    addr_space_size (False, int, None)
      Address space region size in bytes.

      Value between 10,485,760 and 2,147,483,647.

      A value of 0 will delete this field from the profile.


    map_size (False, int, None)
      Maximum amount of data space storage that can be allocated by the user.

      This option represents the number of memory pages, not bytes, available.

      Value between 1 and 16,777,216.

      A value of 0 will delete this field from the profile.


    max_procs (False, int, None)
      Maximum number of processes the user is allowed to have active at the same time.

      Value between 3 and 32,767.

      A value of 0 will delete this field from the profile.


    max_threads (False, int, None)
      Maximum number of threads the user can have concurrently active.

      Value between 0 and 100,000.

      A value of -1 will delete this field from the profile.


    max_cpu_time (False, int, None)
      Specifies the RLIMIT\_CPU hard limit. Indicates the cpu-time that a user process is allowed to use.

      Value between 7 and 2,147,483,647 seconds.

      A value of 0 will delete this field from the profile.


    max_files (False, int, None)
      Maximum number of files the user is allowed to have concurrently active or open.

      Value between 3 and 524,287.

      A value of 0 will delete this field from the profile.


    delete (False, bool, None)
      Delete the whole OMVS block from the profile.

      This option is only valid when updating profiles, it will be ignored when creating one.

      This option is mutually exclusive with every other option in this section.



  tso (False, dict, None)
    Attributes for how TSO should handle a user profile.


    account_num (False, int, None)
      User's default TSO account number when logging in.

      Value between 3 and 524,287.

      A value of 0 will delete this field from the profile.


    logon_cmd (False, str, None)
      Command that needs to be run during TSO/E logon.

      Maximum length of 80 characters.

      This option keeps case.

      An empty value deletes this field.


    logon_proc (False, str, None)
      User's default logon procedure.

      The value for this field is 1 to 8 alphanumeric characters.

      An empty value deletes this field.


    dest_id (False, str, None)
      Default destination to which the user can route dynamically allocated SYSOUT data sets.

      The value for this field is 1 to 7 alphanumeric characters.

      An empty value deletes this field.


    hold_class (False, str, None)
      User's default hold class.

      This option consists of 1 alphanumeric character.

      An empty value deletes this field.


    job_class (False, str, None)
      User's default job class.

      This option consists of 1 alphanumeric character.

      An empty value deletes this field.


    msg_class (False, str, None)
      User's default message class.

      This option consists of 1 alphanumeric character.

      An empty value deletes this field.


    sysout_class (False, str, None)
      User's default SYSOUT class.

      This option consists of 1 alphanumeric character.

      An empty value deletes this field.


    region_size (False, int, None)
      Minimum region size if the user does not request a region size at logon.

      A value between 0 and 2,096,128.

      A value of -1 deletes this field.


    max_region_size (False, int, None)
      Maximum region size that the user can request at logon.

      A value between 0 and 2,096,128.

      A value of -1 deletes this field.


    security_label (False, str, None)
      User's security label if the user specifies one on the TSO logon panel.

      An empty value deletes this field.


    unit_name (False, str, None)
      Default name of a device or group of devices that a procedure uses for allocations.

      The value for this field is 1 to 8 alphanumeric characters.

      An empty value deletes this field.


    user_data (False, str, None)
      Optional installation data defined for the user profile.

      Must be 4 EBCDIC characters.

      An empty value deletes this field.


    delete (False, bool, None)
      Delete the whole TSO block from the profile.

      This option is only valid when updating profiles, it will be ignored when creating one.

      This option is mutually exclusive with every other option in this section.



  connect (False, dict, None)
    Options that configure what a user can do inside a group that is connected to.

    These options are only used when :literal:`operation=connect` and they are ignored otherwise.


    authority (False, str, None)
      Level of group authority given to a user profile.


    universal_access (False, str, None)
      Level of universal access authority given to a user profile.


    group_name (False, str, None)
      Group to which the user will be connected to.

      The rest of the options in this block will affect this group.

      If not supplied, RACF will use a default group. It is recommended to specify this option when trying to connect a user to a group.


    group_account (False, bool, None)
      Whether the user's protected data sets are accessible to other users in the group.


    group_operations (False, bool, None)
      Whether a user should have the group-OPERATIONS attribute when connected to a group.


    auditor (False, bool, None)
      Whether a user should have auditor privileges for the group it is connected to.


    adsp_attribute (False, bool, None)
      Whether to give a user the ADSP attribute, which tells RACF to automatically protect data sets it creates with discrete profiles.


    special (False, bool, None)
      Whether to give a user profile the SPECIAL attribute.

      This attribute lets a user change attributes of other profiles. Use with caution.



  access (False, dict, None)
    Options that set different security attributes in a user profile.


    default_group (False, str, None)
      RACF's default group for the user profile.


    clauth (False, dict, None)
      Classes in which a user is allowed to define profiles to RACF for protection.


      add (False, list, None)
        Adds classes to the profile.


      delete (False, list, None)
        Removes classes from the profile.



    roaudit (False, bool, None)
      Whether a user should have full responsibility for auditing the use of system resources.


    category (False, dict, None)
      Security categories that the profile should have.


      add (False, list, None)
        Adds security categories to the profile.


      delete (False, list, None)
        Removes security categories from the profile.



    operator_card (False, bool, None)
      Whether a user must supply an operator identification card when logging in.


    maintenance_access (False, bool, None)
      Whether the user has authorization to do maintenance operations on all RACF-protected DASD data sets, tape volumes, and DASD volumes.


    restricted (False, bool, None)
      Whether to give the profile the RESTRICTED attribute.


    security_label (False, str, None)
      Security label applied to the profile.

      Empty value deletes this field.


    security_level (False, str, None)
      Security level applied to the profile.

      Empty value deletes this field.



  operator (False, dict, None)
    Attributes used when a user establishes an extended MCS console session.


    alt_group (False, str, None)
      Console group used in recovery.

      Must be between 1 and 8 characters in length.

      Empty value deletes this field.


    authority (False, str, None)
      Console's authority to issue operator commands.

      :literal:`delete` will remove the field from the profile.


    cmd_system (False, str, None)
      System to which commands from this console are to be sent.

      Must be between 1 and 8 characters in length.

      Empty value deletes this field.


    search_key (False, str, None)
      Name used to display information for all consoles with the specified key by using the MVS command :literal:`DISPLAY CONSOLES,KEY`.

      Must be between 1 and 8 characters in length.

      Empty value deletes this field.


    migration_id (False, bool, None)
      Whether a 1-byte migration ID should be assigned to this console.


    display (False, str, ['jobnames', 'sess'])
      Which information should be displayed when monitoring jobs, TSO sessions, or data set status.

      Possible values are :literal:`jobnames`\ , :literal:`jobnamest`\ , :literal:`sess`\ , :literal:`sesst`\ , :literal:`status` and :literal:`delete`.

      Multiple choices are allowed.

      :literal:`delete` will remove this field from the profile.


    msg_level (False, str, None)
      Specifies the messages that this console is to receive.

      :literal:`delete` will remove this field from the profile.


    msg_format (False, str, None)
      Format in which messages are displayed at the console.

      :literal:`delete` will remove this field from the profile.


    msg_storage (False, int, None)
      Specifies the amount of storage in the TSO/E user's address space that can be used for message queuing to the console.

      Its value can be a number between 1 and 2,000.

      A value of 0 deletes this field.


    msg_scope (False, dict, None)
      Systems from which this console can receive messages that are not directed to a specific console.


      add (False, list, None)
        Add new systems to this field.


      remove (False, list, None)
        Removes systems from this field.


      delete (False, bool, None)
        Deletes this field from the profile.

        Mutually exclusive with the rest of the options in this section.



    automated_msgs (False, bool, None)
      Whether the extended console can receive messages that have been automated by the MFP.


    del_msgs (False, str, None)
      Which delete operator message (DOM) requests the console can receive.

      :literal:`delete` will remove the field from the profile.


    hardcopy_msgs (False, bool, None)
      Whether the console should receive all messages that are directed to hardcopy.


    internal_msgs (False, bool, None)
      Whether the console should receive messages that are directed to console ID zero.


    routing_msgs (False, list, None)
      Specifies the routing codes of messages this operator is to receive.

      :literal:`ALL` can be specified to receive all codes. Conversely, :literal:`NONE` can be used to receive none.


    undelivered_msgs (False, bool, None)
      Whether the console should receive undelivered messages.


    unknown_msgs (False, bool, None)
      Whether the console should receive messages that are directed to unknown console IDs.


    responses (False, bool, None)
      Whether command responses should be logged.


    delete (False, bool, None)
      Delete the whole OPERPARM block from the profile.

      This option is only valid when updating profiles, it will be ignored when creating one.

      This option is mutually exclusive with every other option in this section.



  restrictions (False, dict, None)
    Attributes that determine the days and times a user is allowed to login.


    days (False, list, None)
      Days of the week that a user is allowed to login.

      Multiple choices are allowed.

      Valid values are :literal:`anyday`\ , :literal:`weekdays`\ , :literal:`monday`\ , :literal:`tuesday`\ , :literal:`wednesday`\ , :literal:`thursday`\ , :literal:`friday`\ , :literal:`saturday` and :literal:`sunday`.


    time (False, str, None)
      Daily time period when the user is allowed to login.

      The value for this option must be in the format HHMM:HHMM.

      This field uses a 24-hour format.

      This field also accepts the value :literal:`anytime` to indicate a user is free to login at any time of the day.


    resume (False, str, None)
      Date when the user is allowed access to a system again.

      The value for this option must be in the format MM/DD/YY, where :literal:`YY` are the last two digits of the year.


    delete_resume (False, bool, None)
      Delete the resume field from the profile.

      This option is only valid when connecting a user to a group.

      This option is mutually exclusive with :emphasis:`resume`.


    revoke (False, str, None)
      Date when the user is forbidden access to a system.

      The value for this option must be in the format MM/DD/YY, where :literal:`YY` are the last two digits of the year.


    delete_revoke (False, bool, None)
      Delete the revoke field from the profile.

      This option is only valid when connecting a user to a group.

      This option is mutually exclusive with :emphasis:`revoke`.








See Also
--------

.. seealso::

   :ref:`zos_tso_command_module`
      The official documentation on the **zos_tso_command** module.


Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create a new group profile using RACF defaults.
      zos_user:
        name: newgrp
        operation: create
        scope: group

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
        operation: create
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



Return Values
-------------

operation (always, str, create)
  Operation that was performed by the module.


racf_command (success, str, DELUSER (user))
  Full command string that was executed with tsocmd.


num_entities_modified (always, int, 1)
  Number of profiles and references modified by the operation.


entities_modified (success, list, ['user'])
  List of all profiles and references modified by the operation.


database_dumped (always, bool, False)
  Whether the module used IRRRID00 to dump the RACF database.


dump_kept (always, bool, False)
  Whether the RACF database dump was kept on the managed node.


dump_name (success, str, USER.BACKUP.RACF.DATABASE)
  Name of the database containing the output from the IRRRID00 utility.





Status
------





Authors
~~~~~~~

- Alex Moreno (@rexemin)

