
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_tso_command.py

.. _zos_ickdsf_command_module:


zos_ickdsf_command -- Execute TSO commands
=======================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Execute ickdsf init command on device and receive response in html form.





Parameters
----------


commands
  ICKDSF command being selected. Currently only accepts init

  | **required**: true
  | **type**: dict

    volume_address
      3 or 4 hexadecimal digits that contain the address of the volume to initialize.

      | **required**: true
      | **type**: str

    verify_existing_volid
      Used to indicate one of the following
      Verification that an existing volume serial number does not exist for the volume by not including it.
      Verification that the volume contains an existing specific volume serial number. This would be indicated by 1 to 6 alphanumeric characters that would contain the serial number that you wish to verify currently exists on the volume.

      | **required**: false
      | **type**: str

    verify_offline
      Used to indicate if verification should be done to verify that the volume is offline to all host systems.

      defaults to true

      | **required**: false
      | **type**: bool

    volid
      This is used to indicate the 1 to 6 alphanumeric character volume serial number that you want to initialize the volume with. 

      | **required**: false
      | **type**: str

    vtoc_tracks
      This is used to indicate the number of tracks to initialize the VTOC with. The VTOC will be placed at cylinder 0 head 1 for the number of tracks specified. 

      | **required**: false
      | **type**: int

    index
      This is used to indicate if a VTOC index should be created when initializing the volume. The index size will be created based on the size of the volume and the size of the VTOC that was created. The Index will be placed on the volume after the VTOC.

      defaults to true

      | **required**: false
      | **type**: bool

    sms_managed
      Used to indicate whether the device should be managed by a Storage Manager System or SMS.

      defaults to true
      
      | **required**: false
      | **type**: bool

    verify_no_data_sets_exist
      This is used to verify if data sets other than the VTOC index data set and/or VVDS exist on the volume to be initialized.

      defaults to true
      
      | **required**: false
      | **type**: bool

    addr_range
      If initializing a range of volumes, how many additional addresses to initialize

      | **required**: false
      | **type**: int

      volid_prefix
        If initializing a range of volumes, the prefix of volume IDs to initialize. This with have the address appended to it.

        | **required**: true
        | **type**: str

output_html
  Options for creating HTML output of ICKDSF command

  | **required**: false
  | **type**: dict

  full_file path:
    File path to place output HTML file

    | **required**: true
    | **type**: str

  append:
    Optionally append to file, instead of overwriting

    defaults to true
    
    | **required**: false
    | **type**: bool


Examples
--------

.. code-block:: yaml+jinja

   
   - name: Initialize dasd volume for use on a z/OS system
        zos_ickdsf_command:
          init:
            volume_address: 9124
            verify_offline: no
            volid: IN9124
            vtoc_tracks: 30
            index: yes   
            sms_managed: yes
            verify_no_data_sets_exist: no
          output_html:
            full_file_path: ./test.html
            append: yes











Return Values
-------------


output
  List of each ICKDSF command output.

  | **returned**: always
  | **type**: list
  | **elements**: dict

  dd_names
    All the related dds with the content of the program output.

    | **returned**: on success
    | **type**: list
    | **elements**: dict

    byte_count
      The number of bytes in the response content.

      | **type**: int
    
    content
      The content contained in the data definition.

      | **type**: list
      | **elements**: str
      
    dd_name
      The data definition name.

      | **type**: str
    
    name
      The data set or path name associated with the data definition.

      | **type**: str

    record_count
      The lines of the content.

      | **type**: int

  ret_code
    The return code from the executed ICKDSF command.

    | **returned**: always
    | **type**: list
    | **elements**: dict

    code
      Return code

      | **type**: int

  invocation
    The parameters inputted for zos_mvs_raw

    | **returned**: always
    | **type**: list
    | **elements**: dict
    
    module_args
    The arguments for zos_mvs_raw 

    | **type**: list
    | **elements**: dict

    auth
      whether the request was authorized

      | **type**: bool
    
    dds
      All the related dds with the input of the program and encoding of the output

      | **type**: list
      | **elements**: dict

      dd_input
        device data input parameters

        | **type**: list
        | **elements**: dict

        content
          the command submitted by the program

          | **type**: list
          | **elements***: str
    