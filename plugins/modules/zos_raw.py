#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
module: zos_raw
author:
    - "Xiao Yuan Ma (@bjmaxy)"
    - "Blake Becker (@blakeinate)"
short_description: Run a z/OS program.
version_added: "2.9"
options:
  program_name:
    description: The name of the z/OS program to run (e.g. IDCAMS, IEFBR14, IEBGENER, etc.).
    required: true
    type: str
  parms:
    description:
      - The program arguments (e.g. -a='MARGINS(1,72)').
    required: false
    type: str
  auth:
    description:
      - Determines whether this program should run with authorized privileges.
      - If I(auth=true), the program runs as APF authorized.
      - If I(auth=false), the program runs as unauthorized.
    required: false
    type: bool
    default: false
  dds:
    description:
      - The input data source.
      - I(dds) supports 6 types of sources:
          - I(dd_data_set) for data set files.
          - I(dd_uss) for UNIX files.
          - I(dd_input) for in-stram data set.
          - I(dd_sysout) for the output (i.e. stdout).
          - I(dd_dummy) for no content input.
          - I(dd_concat) for a data set concatenation.
      - I(dds) supports any combination of source types.
    required: false
    type: list
    elements: dict
    suboptions:
      dd_data_set:
        description:
          - Specify a data set.
          - I(dd_data_set) can reference an existing data set or be
            used to define a new data set to be created during execution.
        required: false
        type: dict
        suboptions:
          dd_name:
            description: The dd name.
            required: true
            type: str
          data_set_name:
            description: The data set name.
            type: str
            required: false
          data_set_type:
            description:
              - The data set type. Only required when I(disposition=new).
              - Maps to DSNTYPE on z/OS.
            type: str
            choices:
              - library
              - hfs
              - pds
              - large
              - basic
              - rrds
              - esds
              - lds
              - ksds
          disposition:
            description:
              - I(disposition) indicates the status of a data set.
            type: str
            default: shr
            required: false
            choices:
              - new
              - shr
              - mod
              - old
          disposition_normal:
            description:
              - I(disposition_normal) tells the system what to do with the data set after normal termination of the program.
            type: str
            required: false
            default: catalog
            choices:
              - del
              - keep
              - catalog
              - uncatalog
          disposition_abnormal:
            description:
              - I(disposition_abnormal) tells the system what to do with the data set after abnormal termination of the
                program.
            type: str
            required: false
            default: catalog
            choices:
              - del
              - keep
              - catalog
              - uncatalog
          reuse:
            description:
              - Determines if data set should be reused if I(disposition=NEW) and a data set with matching name already exists.
              - If I(reuse=true), I(disposition) will be automatically switched to C(SHR).
              - If I(reuse=false), and a data set with a matching name already exists, allocation will fail.
              - Mutually exclusive with I(replace).
              - I(reuse) is only considered when I(disposition=NEW)
            type: bool
            default: false
          replace:
            description:
              - Determines if data set should be replaced if I(disposition=NEW) and a data set with matching name already exists.
              - If I(replace=true), the original data set will be deleted, and a new data set created.
              - If I(replace=false), and a data set with a matching name already exists, allocation will fail.
              - Mutually exclusive with I(reuse).
              - I(replace) is only considered when I(disposition=NEW)
              - I(replace) will result in loss of all data in the original data set unless I(backup) is specified.
            type: bool
            default: false
          backup:
            description:
              - Determines if a backup should be made of existing data set when I(disposition=NEW), I(replace=true),
                and a data set with the desired name is found.
              - I(backup) is only used when I(replace=true).
            type: bool
            default: false
          space_type:
            description:
              - The unit of measurement to use when allocating space for a new data set
                using I(space_primary) and I(space_secondary).
            type: str
            choices:
              - trk
              - cyl
              - b
              - k
              - m
              - g
              - blklgth
              - reclgth
            default: m
          space_primary:
            description:
              - The primary amount of space to allocate for a new data set.
              - The value provided to I(space_type) is used as the unit of space for the allocation.
              - Not applicable when I(space_type=blklgth) or I(space_type=reclgth).
            type: int
            default: 5
          space_secondary:
            description:
              - When primary allocation of space is filled,
                secondary space will be allocated with the provided size as needed.
              - The value provided to I(space_type) is used as the unit of space for the allocation.
              - Not applicable when I(space_type=blklgth) or I(space_type=reclgth).
            type: int
            default: 5
          volumes:
            description:
              - The volume or volumes on which a data set resides or will reside.
              - Do not specify the same volume multiple times.
            type: list
            elements: str
            required: false
          sms_management_class:
            description:
              - The desired management class for a new SMS-managed data set.
              - I(sms_management_class) is ignored if specified for an existing data set.
              - All values must be between 1-8 alpha-numeric chars
            type: str
            required: false
          sms_storage_class:
            description:
              - The desired storage class for a new SMS-managed data set.
              - I(sms_storage_class) is ignored if specified for an existing data set.
              - All values must be between 1-8 alpha-numeric chars
            type: str
            required: false
          sms_data_class:
            description:
              - The desired data class for a new SMS-managed data set.
              - I(sms_data_class) is ignored if specified for an existing data set.
              - All values must be between 1-8 alpha-numeric chars
            type: str
            required: false
          block_size:
            description:
              - The maximum length of a block.
              - I(block_size_type) is used to provide unit of size.
              - Default is dependent on I(record_format)
            type: int
            required: false
          # TODO: add support for multiple types of block size
          # ? can we even have gb block sizes??
          block_size_type:
            description:
              - The unit of measurement for I(block_size).
            type: str
            choices:
              - b
              - k
              - m
              - g
            default: b
          data_set_key_label:
            description:
              - The label for the encryption key used by the system to encrypt the data set.
              - I(data_set_key_label) is the public name of a protected encryption key in the ICSF key repository.
              - I(data_set_key_label) should only be provided when creating an extended format data set.
              - Maps to DSKEYLBL on z/OS.
            type: str
            required: false
          encryption_key_1:
            description:
              - The encrypting key used by the Encryption Key Manager.
              - Specification of the key labels does not by itself enable encryption.
                Encryption must be enabled by a data class that specifies an encryption format.
            type: dict
            required: false
            suboptions:
              label:
                description:
                  - The label for the key encrypting key used by the Encryption Key
                    Manager.
                  - Key label must have a private key associated with it.
                  - I(label) can be a maximum of 64 characters.
                  - Maps to KEYLAB1 on z/OS.
                type: str
                required: true
              encoding:
                description:
                  - How the label for the key encrypting key specified by
                    I(label) is encoded by the Encryption Key Manager.
                  - I(encoding) can either be set to C(L) for label encoding,
                    or C(H) for hash encoding.
                  - Maps to KEYCD1 on z/OS.
                type: str
                required: true
                choices:
                  - l
                  - h
          encryption_key_2:
            description:
              - The encrypting key used by the Encryption Key Manager.
              - Specification of the key labels does not by itself enable encryption.
                Encryption must be enabled by a data class that specifies an encryption format.
            type: dict
            required: false
            suboptions:
              label:
                description:
                  - The label for the key encrypting key used by the Encryption Key
                    Manager.
                  - Key label must have a private key associated with it.
                  - I(label) can be a maximum of 64 characters.
                  - Maps to KEYLAB2 on z/OS.
                type: str
                required: true
              encoding:
                description:
                  - How the label for the key encrypting key specified by
                    I(label) is encoded by the Encryption Key Manager.
                  - I(encoding) can either be set to C(L) for label encoding,
                    or C(H) for hash encoding.
                  - - Maps to KEYCD2 on z/OS.
                type: str
                required: true
                choices:
                  - l
                  - h
          key_length:
            description:
              - The length of the keys used in a new data set.
              - If using SMS, setting I(key_length) overrides the key length defined in the SMS data class of the data set.
              - Valid values are (0-255 non-vsam), (1-255 vsam).
            type: int
            required: false
          key_offset:
            description:
              - The position of the first byte of the record key in each logical record of a new VSAM data set.
              - The first byte of a logical record is position 0.
              - Provide I(key_offset) only for VSAM key-sequenced data sets.
            type: int
            required: false
          record_length:
            description:
              - The logical record length. (e.g C(80)).
              - For variable data sets, the length must include the 4-byte prefix area.
              - Defaults vary depending on format. If FB/FBA 80, if VB/VBA 137, if U 0.
              - Valid values are (1-32760 for non-vsam,  1-32761 for vsam).
              - Maps to LRECL on z/OS.
            type: int
            required: false
          record_format:
            description:
              - The format and characteristics of the records for new data set.
            type: str
            choices:
              - u
              - v
              - vb
              - vba
              - f
              - fb
              - fba
            default: fb
          return_content:
            description:
            type: str
            choices:
              - none
              - text
              - base64
            default: none
      dd_sysout:
        description:
          - Specify location to place system output.
        required: false
        type: dict
        suboptions:
          dd_name:
            description: The dd name.
            required: true
            type: str
          return_content:
            description:
              - Whether to return the I(dd_sysout) content.
              - C(none) means do not return content.
              - C(text) means return value in ASCII, converted from EBCDIC.
              - C(base64) means in binary mode.
            required: false
            type: str
            choices:
              - none
              - text
              - base64
          sysout_class:
            description: The sysout class.
            type: str
      dd_uss:
        description:
          - The path to a file in Unix System Services (USS).
        required: false
        type: dict
        suboptions:
          dd_name:
            description: The dd name.
            required: true
            type: str
          path:
            description:
              - The path to an existing UNIX file.
              - Or provide the path to an new created UNIX file when I(path_status_group=OCREAT).
              - The provided path must be absolute.
            required: true
            type: str
          path_disposition_normal:
            description:
              - Tells the system what to do with the UNIX file after normal termination of
                the program.
            type: str
            default: keep
            choices:
              - keep
              - delete
          path_disposition_abnormal:
            description:
              - Tells the system what to do with the UNIX file after abnormal termination of
                the program.
            type: str
            default: keep
            choices:
              - keep
              - delete
          # ? what default path modes do we want?
          path_mode:
            description:
              - The file access attributes when the UNIX file is created specified in I(path).
              - For those used to /usr/bin/chmod remember that modes are actually octal numbers.
                You must either add a leading zero so that Ansible's YAML parser knows it is an octal number
                (like 0644 or 01777) or quote it (like '644' or '1777') so Ansible receives a string and can
                do its own conversion from string into number.
              - The mode may be specified as a symbolic mode (for example, C(u+rwx) or C(u=rw,g=r,o=r)).
              - Maps to PATHMODE on z/OS.
            type: str
          # TODO: determine if path_access_group equivalent is available or not
          path_access_group:
            description:
              - The access attributes for the UNIX file specified in I(path).
              # - Maps to PATHOPTS access group file options on z/OS.
            type: str
            default: read_only
            choices:
              - read_only
              - write_only
              - read_write
          path_status_group:
            description:
              - The status for the UNIX file specified in I(path).
              - If you do not code a value on the I(path_status_group) parameter the module assumes that the
                pathname exists, searches for it, and fails the module if the pathname does not exist.
              - Maps to PATHOPTS status group file options on z/OS.
              - You can choose up to 6 of the following:
                  - oappend
                  - ocreat
                  - oexcl
                  - onoctty
                  - ononblock
                  - osync
                  - otrunc
            type: list
            elements: str
            required: false
          file_data_type: # ? should this be renamed to data_type or file_data_type?
            description:
              - The type of data that is (or will be) stored in the file specified in I(path).
              - Maps to FILEDATA on z/OS.
            type: str
            default: binary
            choices:
              - binary
              - text
              - record
          return_content:
            description:
              - Whether to return the I(dd_uss) content.
              - C(none) means do not return content.
              - C(text) means return content in ASCII, converted from EBCDIC.
              - C(base64) means return content in binary mode.
            type: str
            choices:
              - none
              - text
              - base64
            default: none
      dd_input:
        description:
          - I(dd_input) is used to specify an in-stream data set.
        required: false
        type: dict
        suboptions:
          dd_name:
            description: The dd name.
            required: true
            type: str
          dd_content:
            description:
              - The input contents for the DD.
              - I(dd_input) supports single or multiple lines of input.
              - Multi-line input can be provided as a multi-line string
                or a list of strings with 1 line per list item.
              - If a list of strings is provided, newlines will be
                added to each of the lines when used as input.
            required: false
            type: raw
          return_content:
            description:
              - Whether to return the I(dd_input) content.
              - C(none) means do not return content.
              - C(text) means return value in ASCII, converted from EBCDIC.
              - C(base64) means in binary mode.
            type: str
            choices:
              - none
              - text
              - base64
            default: none
      dd_dummy:
        description:
          - Use I(dd_dummy) to specify:
              - No device or external storage space is to be allocated to the data set.
              - No disposition processing is to be performed on the data set.
          - I(dd_dummy) accepts no content input.
        required: false
        type: dict
        suboptions:
          dd_name:
            description: The dd name.
            required: true
            type: str
      dd_concat:
        description:
          - "I(dd_concat) is a list containing any of the following types:
            I(dd_data_set), I(dd_uss), and I(dd_input)."
        required: false
        type: list
        elements: dict
"""

# TODO: write return info

# RETURN = """
# ret_code: 
#     description: The return code. 
#     returned : always
#     type: dict
#     contains:
#         msg:
#             description: Holds the return code 
#             type: str
#         msg_code: 
#             description: Holds the return code string 
#             type: str
#         msg_txt: 
#             description: Holds additional information related to the program that may be useful to the user.
#             type: str
#         code: 
#             description: return code converted to integer value (when possible)
#             type: int 
#     sample: Value 0 indicates success, non-zero indicates failure.
#        - code: 0
#        - msg: "0"
#        - msg_code: "0"
#        - msg_txt: "THE z/OS PROGRAM EXECUTION SUCCEED." 
# ddnames:
#     description: All the related dds with the program. 
#     returned: always
#     type: list<dict> 
#     contains:
#         ddname:
#           description: data definition name
#           type: str
#         dataset:
#           description: the dataset name  
#           type: str
#         content:
#           description: ddname content
#           type: list[str] 
#         record_count:
#           description: the lines of the content 
#           type: int
#         byte_count:
#           description: bytes count
#           type: int
#     samples:         
#         - ddname: "SYSIN", "SYSPRINT",etc.
#         - dataset: "TEST.TESTER.DATA", "stdout", "dummy", etc
#         - content: " "
#         - record_count: 4
#         - byte_count:  415
# changed: 
#     description: Indicates if any changes were made during module operation.
#     type: bool
# """

# TODO: verify examples match expected format

# EXAMPLES = r"""
# - name: Run IEFBR14 program. This is a simple program, no output.  
#     zos_mvs_raw:
#         program_name: IEFBR14

# - name: run IDCAMS program to list the catagory of dataset 'TESTER.DATASET'  
#     zos_mvs_raw:
#         program_name: IDCAMS
#         parms:
#         auth: true
#         dds:
#           - dd_input:
#               - dd_name: sysin
#               - dd_content: LISTCAT ENT('TESTER.DATASET')
#               - return_content: text
#           - dd_dataset:
#               - dd_name: sysprint
#               - data_set_name: TESTER.MVSUTIL.PYTHON.OUT
#               - disposition: old
#               - disposition_normal: keep
#               - disposition_abnormal: keep
#               - return_content: text

#   - name: TSO isrsupc program, multiple lines sysin inputs
#     zos_mvs_raw:
#       program_name: isrsupc
#       parms: DELTAL,SRCHCMP,ANYC
#       dds:
#         - dd_dataset:
#             - dd_name: newdd
#             - data_set_name: BJMAXY.IMSTESTL.IMS1.TEST05:BJMAXY.IMSTESTL.IMS1.TEST06
#             - disposition: old
#             - disposition_normal: keep
#             - disposition_abnormal: keep
#             - return_content: text
#         - dd_input:
#             - dd_name: sysin
#             - dd_content:
#               - "  CMPCOLM 7:71"
#               - "  DPLINE  '*',7"
#               - "  SRCHFOR 'NEEDLE',W,10:20"
#             - return_content: text
#         - dd_dataset:
#             - dd_name: olddd
#             - data_set_name: BJMAXY.IMSTESTL.IMS1.TEST07
#             - disposition: old
#             - disposition_normal: keep
#             - disposition_abnormal: keep
#             - return_content: text
#         - dd_sysout:
#             - dd_name: outdd
#             - sysout_class: A
#             - return_content: text
              
#   - name: TSO iebgener program,This program copy the content from sysut1 to sysut2.
#     zos_mvs_raw:
#       program_name: iebgener
#       dds:
#         - dd_dummy:
#             - dd_name: sysin
#         - dd_dataset:
#             - dd_name: sysut1
#             - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.A
#         - dd_dataset:
#             - dd_name: sysut2
#             - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.B
#         - dd_sysout:
#             - dd_name: sysprint
#             - sysout_class: A
#             - return_content: text
#       debug: True
    
#   - name: TSO IEBUPDTE program, add/replace a new dataset member ERASE in sysut1 and store it in sysut2. ERASE content is Hello world!
#     zos_mvs_raw:
#       program_name: IEBUPDTE
#       parms: NEW
#       dds:
#         - dd_dataset:
#             - dd_name: sysut1
#             - data_set_name: BJMAXY.CICS.SETUP
#             - disposition: old
#             - disposition_normal: keep
#             - disposition_abnormal: keep
#             - return_content: text
#         - dd_dataset:
#             - dd_name: sysut2
#             - data_set_name: BJMAXY.CICS.SETUP
#             - disposition: old
#             - disposition_normal: keep
#             - disposition_abnormal: keep
#             - return_content: text
#         - dd_input:
#             - dd_name: sysin
#             - dd_content:
#                 - "./        ADD   LIST=ALL,NAME=ERASE,LEVEL=01,SOURCE=0"
#                 - "./     NUMBER   NEW1=10,INCR=10"
#                 - "Hello world! "
#                 - "./      ENDUP   "
#             - return_content: text
#         - dd_dataset:
#             - dd_name: sysprint
#             - data_set_name: BJMAXY.NOEXIST.DS
#       debug: True    
     
#   - name: TSO isrsupc program, Compare 2 PDS members olddd and newdd and write the output to outdd.
#     zos_mvs_raw:
#         program_name: ISRSUPC
#         parms: DELTAL,LINECMP
#         dds:
#           - dd_dataset:
#               - dd_name: newdd
#               - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.A
#               - disposition: old
#               - disposition_normal: keep
#               - disposition_abnormal: keep
#               - return_content: text
#           - dd_dataset:
#               - dd_name: olddd
#               - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.B
#               - disposition: old
#               - disposition_normal: keep
#               - disposition_abnormal: keep
#               - return_content: text
#           - dd_dataset:
#               - dd_name: sysin
#               - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.OPT
#               - disposition: old
#               - disposition_normal: keep
#               - disposition_abnormal: keep
#               - return_content: text
#           - dd_dataset:
#               - dd_name: outdd
#               - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.RESULT
#               - disposition: old
#               - disposition_normal: keep
#               - disposition_abnormal: keep
#               - return_content: text
#           - dd_dataset:
#               - dd_name: sysprint
#               - data_set_name: BJMAXY.MVSUTIL.PYTHON.MVSCMD.RESULT2
#               - disposition: old
#               - disposition_normal: keep
#               - disposition_abnormal: keep
#               - return_content: text

     
# EXAMPLE RESULTS:
# "msg": "    
#     "changed": true,
#     "ddnames": [
#         {
#             "byte_count": "748",
#             "content": "TEST                                                                            ",
#             "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.A",
#             "ddname": "newdd",
#             "record_count": 1
#         },
#         {
#             "byte_count": "748",
#             "content": "TEST                                                                            ",
#             "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.B",
#             "ddname": "olddd",
#             "record_count": 1
#         },
#         {
#             "byte_count": "748",
#             "content": "   CMPCOLM 1:72                                                                 ",
#             "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.OPT",
#             "ddname": "sysin",
#             "record_count": 1
#         },
#         {
#             "byte_count": "3400",
#             "content": "
#                        ISRSUPC   -   MVS/PDF FILE/LINE/WORD/BYTE/SFOR COMPARE UTILITY- ISPF FOR z/OS         2020/02/25   3.36    PAGE     1
#                         NEW: TESTER.MVSUTIL.PYTHON.MVSCMD.A                          OLD: TESTER.MVSUTIL.PYTHON.MVSCMD.B                       
                                                                                                                       
#                                             LINE COMPARE SUMMARY AND STATISTICS                                                             
                                                                                                                       
                                                                                                                       
                                                                                                                       
#                             1 NUMBER OF LINE MATCHES               0  TOTAL CHANGES (PAIRED+NONPAIRED CHNG)                                 
#                             0 REFORMATTED LINES                    0  PAIRED CHANGES (REFM+PAIRED INS/DEL)                                  
#                             0 NEW FILE LINE INSERTIONS             0  NON-PAIRED INSERTS                                                    
#                             0 OLD FILE LINE DELETIONS              0  NON-PAIRED DELETES                                                    
#                             1 NEW FILE LINES PROCESSED                                                                                      
#                             1 OLD FILE LINES PROCESSED                                                                                      
                                                                                                                       
#                     LISTING-TYPE = DELTA      COMPARE-COLUMNS =    1:72        LONGEST-LINE = 80                                           
#                     PROCESS OPTIONS USED: NONE                                                                                             
                                                                                                                       
#                     THE FOLLOWING PROCESS STATEMENTS (USING COLUMNS 1:72) WERE PROCESSED:                                                  
#                             CMPCOLM 1:72                                                                                                     
#                      " 
#             "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT",
#             "ddname": "outdd",
#             "record_count": 20
#         },
#         {
#             "byte_count": "0",
#             "content": "",
#             "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.RESULT2",
#             "ddname": "sysprint",
#             "record_count": 1
#         }
#     ],
#     "ret_code": {
#         "code": 0,
#         "msg": 0,
#         "msg_code": 0,
#         "msg_txt": "THE z/OS PROGRAM EXECUTION SUCCEED.",
#     }
# "

# "msg" : "
#     "changed": true,
#     "ddnames": [
#         {
#             "byte_count": "748",
#             "content": "  LISTCAT ENT('TESTER.HILL3')                                                   ",
#             "dataset": "TESTER.P3621680.T0979893.C0000000",
#             "ddname": "sysin",
#             "record_count": 1
#         },
#         {
#             "byte_count": "2006",
#             "content": "
#                         1IDCAMS  SYSTEM SERVICES                                           TIME: 04:04:12        02/25/20     PAGE      1 
#                         0                                                                                                                 
#                         LISTCAT ENT('TESTER.HILL3')                                                                                    
#                         0NONVSAM ------- TESTER.HILL3                                                                                     
#                               IN-CAT --- ICFCAT.SYSPLEX2.CATALOGB                                                                         
#                         1IDCAMS  SYSTEM SERVICES                                           TIME: 04:04:12        02/25/20     PAGE      2 
#                         0         THE NUMBER OF ENTRIES PROCESSED WAS:                                                                    
#                                             AIX -------------------0                                                                      
#                                             ALIAS -----------------0                                                                      
#                                             CLUSTER ---------------0                                                                      
#                                             DATA ------------------0                                                                      
#                                             GDG -------------------0                                                                      
#                                             INDEX -----------------0                                                                      
#                                             NONVSAM ---------------1                                                                      
#                                             PAGESPACE -------------0                                                                      
#                                             PATH ------------------0                                                                      
#                                             SPACE -----------------0                                                                      
#                                             USERCATALOG -----------0                                                                      
#                                             TAPELIBRARY -----------0                                                                      
#                                             TAPEVOLUME ------------0                                                                      
#                                             TOTAL -----------------1                                                                      
#                         0         THE NUMBER OF PROTECTED ENTRIES SUPPRESSED WAS 0                                                        
#                         0IDC0001I FUNCTION COMPLETED, HIGHEST CONDITION CODE WAS 0                                                        
#                         0                                                                                                                 
#                         0IDC0002I IDCAMS PROCESSING COMPLETE. MAXIMUM CONDITION CODE WAS 0                                                
#             " 
#             "dataset": "TESTER.MVSUTIL.PYTHON.MVSCMD.AUTH.OUT",
#             "ddname": "sysprint",
#             "record_count": 25
#         }
#     ], 
#     "ret_code": {
#         "code": 0,
#         "msg": 0,
#         "msg_code": 0,
#         "msg_txt": "THE z/OS PROGRAM EXECUTION SUCCEED."
#     }
# "
# """

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible.module_utils.basic import AnsibleModule
import re

def dd_content(contents, dependencies):
    """Reformats dd content arguments

    Args:
        contents (Union[str, list[str]]): argument contents
        dependencies (dict): Any dependent arguments

    Returns:
        str: content string to save to data set
    """
    if not contents:
        return None
    if isinstance(contents, list):
        return "\n".join(contents)
    return contents

def volumes(contents, dependencies):
    """Validates volume is valid.
    Returns uppercase volume."""
    if not contents:
        return None
    if not isinstance(contents, list):
        contents = [contents]
    for vol in contents:
        if not re.fullmatch(r"^[A-Z0-9]{1,6}$", str(vol), re.IGNORECASE,):
            raise ValueError(
                'Invalid argument "{0}" for type "volumes".'.format(vol)
            )
        vol = vol.upper()
    return contents


def parse_and_validate_args(params):
    dd_name_base = dict(
        dd_name=dict(type="dd")
    )

    dd_data_set_base = dict(
        data_set_name=dict(type="data_set", required=True),
        disposition=dict(type="str", choices=["new", "shr", "mod", "old"]),
        disposition_normal=dict(type="str", choices=["delete", "keep", "catalog", "uncatalog"]),
        disposition_abnormal=dict(type="str", choices=["delete", "keep", "catalog", "uncatalog"]),
        space_type=dict(type="str", choices=["trk", "cyl", "b", "k", "m", "g", "blklgth", "reclgth"]),
        space_primary=dict(type="int"),
        space_secondary=dict(type="int"),
        volumes=dict(type=volumes),
        sms_management_class=dict(type="str"),
        sms_storage_class=dict(type="str"),
        sms_data_class=dict(type="str"),
        block_size=dict(type="int"),
        block_size_type=dict(type="str", choices=["b", "k", "m", "g"]),
        data_set_key_label=dict(type="str"),
        data_set_type=dict(type="str", choices=["library", "pds", "pdse", "seq", "basic", "large", "ksds", "rrds", "lds", "esds"]),
        encryption_key_1=dict(type="dict", options=dict(
            label=dict(type="str", required=True),
            encoding=dict(type="str", required=True, choices=["l", "h"])
        )),
        encryption_key_2=dict(type="dict", options=dict(
            label=dict(type="str", required=True),
            encoding=dict(type="str", required=True, choices=["l", "h"])
        )),
        key_length=dict(type="int"),
        key_offset=dict(type="int"),
        record_length=dict(type="int"),
        record_format=dict(type="str", choices=["u", "v", "vb", "vba", "f", "fb", "fba"]),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_input_base = dict(
        dd_content=dict(type=dd_content, required=True),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_unix_base = dict(
        path=dict(type="path", required=True),
        path_disposition_normal=dict(type="str", choices=["keep", "delete"]),
        path_disposition_abnormal=dict(type="str", choices=["keep", "delete"]),
        path_mode=dict(type="int"),
        path_status_group=dict(type="list", elements="str", choices=["ocreat", "oexcl", "oappend", "ordwr", "ordonly", "owronly", "onoctty", "ononblock", "osync", "otrunc"]),
        file_data_type=dict(type="str", choices=["binary", "text", "record"], default="binary"),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_sysout = dict(
        dd_name=dict(type="dd"),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_dummy = dict(dd_name=dict(type="dd"))

    dd_concat_base = dict(
        dd_data_set=dict(type="dict", options=dd_data_set_base),
        dd_input=dict(type="dict", options=dd_input_base),
        dd_unix=dict(type="dict", options=dd_unix_base)
    )

    dd_data_set = dict(type="dict", options={**dd_name_base, **dd_data_set_base})
    dd_unix = dict(type="dict", options={**dd_name_base, **dd_unix_base})
    dd_input = dict(type="dict", options={**dd_name_base, **dd_input_base})
    dd_concat = dict(type="dict", options={**dd_name_base, **dd_concat_base})
    dd_sysout = dict(type="dict", options=dd_sysout)
    dd_dummy = dict(type="dict", options=dd_dummy)

    module_args = dict(
        program_name=dict(type="str"),
        auth=dict(type="bool", default=False),
        parms=dict(type="str", required=False),
        dds=dict(type="list", elements="dict", options=dict(
            dd_data_set=dd_data_set,
            dd_unix=dd_unix,
            dd_input=dd_input,
            dd_concat=dd_concat,
            dd_sysout=dd_sysout,
            dd_dummy=dd_dummy
        )),
        verbose=dict(type="bool", required=False),
        debug=dict(type="bool", required=False),
    )
    parser = BetterArgParser(module_args)
    parsed_args = parser.parse_args(params)
    return parsed_args


def initialize_module():
    dd_name_base = dict(
        dd_name=dict(type="str")
    )

    dd_data_set_base = dict(
        data_set_name=dict(type="str"),
        disposition=dict(type="str", choices=["new", "shr", "mod", "old"]),
        disposition_normal=dict(type="str", choices=["delete", "keep", "catalog", "uncatalog"]),
        disposition_abnormal=dict(type="str", choices=["delete", "keep", "catalog", "uncatalog"]),
        space_type=dict(type="str", choices=["trk", "cyl", "b", "k", "m", "g", "blklgth", "reclgth"]),
        space_primary=dict(type="int"),
        space_secondary=dict(type="int"),
        volumes=dict(type="raw"),
        sms_management_class=dict(type="str"),
        sms_storage_class=dict(type="str"),
        sms_data_class=dict(type="str"),
        block_size=dict(type="int"),
        block_size_type=dict(type="str", choices=["b", "k", "m", "g"]),
        data_set_key_label=dict(type="str"),
        data_set_type=dict(type="str", choices=["library", "pds", "pdse", "seq", "basic", "large", "ksds", "rrds", "lds", "esds"]),
        encryption_key_1=dict(type="dict", options=dict(
            label=dict(type="str", required=True),
            encoding=dict(type="str", required=True, choices=["l", "h"])
        )),
        encryption_key_2=dict(type="dict", options=dict(
            label=dict(type="str", required=True),
            encoding=dict(type="str", required=True, choices=["l", "h"])
        )),
        key_length=dict(type="int"),
        key_offset=dict(type="int"),
        record_length=dict(type="int"),
        record_format=dict(type="str", choices=["u", "v", "vb", "vba", "f", "fb", "fba"]),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_input_base = dict(
        dd_content=dict(type="raw", required=True),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_unix_base = dict(
        path=dict(type="str", required=True),
        path_disposition_normal=dict(type="str", choices=["keep", "delete"]),
        path_disposition_abnormal=dict(type="str", choices=["keep", "delete"]),
        path_mode=dict(type="int"),
        path_status_group=dict(type="list", elements="str", choices=["ocreat", "oexcl", "oappend", "ordwr", "ordonly", "owronly", "onoctty", "ononblock", "osync", "otrunc"]),
        file_data_type=dict(type="str", choices=["binary", "text", "record"], default="binary"),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
    )

    dd_sysout = dict(
        dd_name=dict(type="str"),
        return_content=dict(type="str", default="none", choices=["none", "text", "base64"]),
        # sysout_class=dict(type="str", required=False, default="*"),
    )

    dd_dummy = dict(dd_name=dict(type="str"))

    dd_concat_base = dict(type="list", elements="dict", options=dict(
        dd_data_set=dd_data_set_base,
        dd_input=dd_input_base,
        dd_unix=dd_unix_base
    ))

    dd_data_set = dict(type="dict", options={**dd_name_base, **dd_data_set_base})
    dd_unix = dict(type="dict", options={**dd_name_base, **dd_unix_base})
    dd_input = dict(type="dict", options={**dd_name_base, **dd_input_base})
    dd_concat = dict(type="dict", options={**dd_name_base, **dd_concat_base})
    dd_sysout = dict(type="dict", options=dd_sysout)
    dd_dummy = dict(type="dict", options=dd_dummy)

    module_args = dict(
        program_name=dict(type="str"),
        auth=dict(type="bool", default=False),
        parms=dict(type="str", required=False),
        dds=dict(type="list", elements="dict", options=dict(
            dd_data_set=dd_data_set,
            dd_unix=dd_unix,
            dd_input=dd_input,
            dd_concat=dd_concat,
            dd_sysout=dd_sysout,
            dd_dummy=dd_dummy
        )),
        verbose=dict(type="bool", required=False),
        debug=dict(type="bool", required=False),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    return module

def run_module():
    result = dict(changed=False, ddnames="", ret_code="",)
    try:
        module = initialize_module()
        params = parse_and_validate_args(module.params)
        result["params"] = params
        result["original_message"] = module.params

    except Exception as e:
        module.fail_json(msg=repr(e), **result)

    result["changed"] = True
    module.exit_json(**result)


class Error(Exception):
    pass


class ZOSRawError(Error):
    def __init__(self, program):
        self.msg = "An error occurred during execution of z/OS program {}.".format(
            program
        )


def main():
    run_module()


if __name__ == "__main__":
    main()
