#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
  args:
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
          - I(dd_unix) for UNIX files.
          - I(dd_input) for in-stream data set.
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
          type:
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
              - delete
              - keep
              - catlg
              - catalog
              - uncatlg
              - uncatalog
          disposition_abnormal:
            description:
              - I(disposition_abnormal) tells the system what to do with the data set after abnormal termination of the
                program.
            type: str
            required: false
            default: catalog
            choices:
              - delete
              - keep
              - catlg
              - catalog
              - uncatlg
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
          key_label:
            description:
              - The label for the encryption key used by the system to encrypt the data set.
              - I(key_label) is the public name of a protected encryption key in the ICSF key repository.
              - I(key_label) should only be provided when creating an extended format data set.
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
              - Determines how content should be returned to the user.
              - If not provided, no content from the DD is returned.
            type: dict
            required: false
            suboptions:
              type:
                description:
                  - The type of the content to be returned.
                  - C(text) means return content in ASCII, converted from EBCDIC.
                  - C(base64) means return content in binary mode.
                type: str
                choices:
                  - text
                  - base64
                required: true
              src_encoding:
                description:
                  - The encoding of the data set on the z/OS system.
                type: str
                default: ibm-1047
              response_encoding:
                description:
                  - The encoding to use when returning the contents of the data set.
                type: str
                default: iso8859-1
      dd_unix:
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
              - Determines how content should be returned to the user.
              - If not provided, no content from the DD is returned.
            type: dict
            required: false
            suboptions:
              type:
                description:
                  - The type of the content to be returned.
                  - C(text) means return content in ASCII, converted from EBCDIC.
                  - C(base64) means return content in binary mode.
                type: str
                choices:
                  - text
                  - base64
                required: true
              src_encoding:
                description:
                  - The encoding of the file on the z/OS system.
                type: str
                default: ibm-1047
              response_encoding:
                description:
                  - The encoding to use when returning the contents of the file.
                type: str
                default: iso8859-1
      dd_input:
        description:
          - I(dd_input) is used to specify an in-stream data set.
          - Input will be saved to a temporary data set with a record length of 80.
        required: false
        type: dict
        suboptions:
          dd_name:
            description: The dd name.
            required: true
            type: str
          content:
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
              - Determines how content should be returned to the user.
              - If not provided, no content from the DD is returned.
            type: dict
            required: false
            suboptions:
              type:
                description:
                  - The type of the content to be returned.
                  - C(text) means return content in ASCII, converted from EBCDIC.
                  - C(base64) means return content in binary mode.
                type: str
                choices:
                  - text
                  - base64
                required: true
              src_encoding:
                description:
                  - The encoding of the data set on the z/OS system.
                type: str
                default: ibm-1047
              response_encoding:
                description:
                  - The encoding to use when returning the contents of the data set.
                type: str
                default: iso8859-1
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
            I(dd_data_set), I(dd_unix), and I(dd_input)."
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
              data_set_name:
                description: The data set name.
                type: str
                required: false
              type:
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
                  - delete
                  - keep
                  - catlg
                  - catalog
                  - uncatlg
                  - uncatalog
              disposition_abnormal:
                description:
                  - I(disposition_abnormal) tells the system what to do with the data set after abnormal termination of the
                    program.
                type: str
                required: false
                default: catalog
                choices:
                  - delete
                  - keep
                  - catlg
                  - catalog
                  - uncatlg
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
              key_label:
                description:
                  - The label for the encryption key used by the system to encrypt the data set.
                  - I(key_label) is the public name of a protected encryption key in the ICSF key repository.
                  - I(key_label) should only be provided when creating an extended format data set.
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
                  - Determines how content should be returned to the user.
                  - If not provided, no content from the DD is returned.
                type: dict
                required: false
                suboptions:
                  type:
                    description:
                      - The type of the content to be returned.
                      - C(text) means return content in ASCII, converted from EBCDIC.
                      - C(base64) means return content in binary mode.
                    type: str
                    choices:
                      - text
                      - base64
                    required: true
                  src_encoding:
                    description:
                      - The encoding of the data set on the z/OS system.
                    type: str
                    default: ibm-1047
                  response_encoding:
                    description:
                      - The encoding to use when returning the contents of the data set.
                    type: str
                    default: iso8859-1
          dd_unix:
            description:
              - The path to a file in Unix System Services (USS).
            required: false
            type: dict
            suboptions:
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
                  - Determines how content should be returned to the user.
                  - If not provided, no content from the DD is returned.
                type: dict
                required: false
                suboptions:
                  type:
                    description:
                      - The type of the content to be returned.
                      - C(text) means return content in ASCII, converted from EBCDIC.
                      - C(base64) means return content in binary mode.
                    type: str
                    choices:
                      - text
                      - base64
                    required: true
                  src_encoding:
                    description:
                      - The encoding of the file on the z/OS system.
                    type: str
                    default: ibm-1047
                  response_encoding:
                    description:
                      - The encoding to use when returning the contents of the file.
                    type: str
                    default: iso8859-1
          dd_input:
            description:
              - I(dd_input) is used to specify an in-stream data set.
              - Input will be saved to a temporary data set with a record length of 80.
            required: false
            type: dict
            suboptions:
              content:
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
                  - Determines how content should be returned to the user.
                  - If not provided, no content from the DD is returned.
                type: dict
                required: false
                suboptions:
                  type:
                    description:
                      - The type of the content to be returned.
                      - C(text) means return content in ASCII, converted from EBCDIC.
                      - C(base64) means return content in binary mode.
                    type: str
                    choices:
                      - text
                      - base64
                    required: true
                  src_encoding:
                    description:
                      - The encoding of the data set on the z/OS system.
                    type: str
                    default: ibm-1047
                  response_encoding:
                    description:
                      - The encoding to use when returning the contents of the data set.
                    type: str
                    default: iso8859-1
"""

RETURN = r"""
ret_code:
    description: The return code.
    returned : always
    type: dict
    contains:
      code:
        description: The return code number returned from the program.
        type:
dd_names:
    description: All the related dds with the program.
    returned: always
    type: list
    elements: dict
    contains:
      dd_name:
        description: The data definition name.
        type: str
      name:
        description: The data set or path name associated with the data definition.
        type: str
      content:
        description: The content contained in the data definition.
        type: list
        elements: str
      record_count:
        description: The lines of the content.
        type: int
      byte_count:
        description: The number of bytes in the response content.
        type: int
"""

# TODO: verify examples match expected format


from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dd_statement import (
    DDStatement,
    FileDefinition,
    DatasetDefinition,
    StdinDefinition,
    DummyDefinition,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zos_raw import MVSCmd

from ansible.module_utils.basic import AnsibleModule
import re
from ansible.module_utils.six import PY3

if PY3:
    from shlex import quote
else:
    from pipes import quote


def run_module():
    """Executes all module-related functions.

    Raises:
        ZOSRawError: When an issue occurs attempting to run the desired program.
    """
    dd_name_base = dict(dd_name=dict(type="str", required=True))

    dd_data_set_base = dict(
        data_set_name=dict(type="str"),
        disposition=dict(type="str", choices=["new", "shr", "mod", "old"]),
        disposition_normal=dict(
            type="str", choices=["delete", "keep", "catalog", "uncatalog"]
        ),
        disposition_abnormal=dict(
            type="str", choices=["delete", "keep", "catalog", "uncatalog"]
        ),
        space_type=dict(type="str", choices=["trk", "cyl", "b", "k", "m", "g"]),
        space_primary=dict(type="int"),
        space_secondary=dict(type="int"),
        volumes=dict(type="raw"),
        sms_management_class=dict(type="str"),
        sms_storage_class=dict(type="str"),
        sms_data_class=dict(type="str"),
        block_size=dict(type="int"),
        block_size_type=dict(type="str", choices=["b", "k", "m", "g"]),
        key_label=dict(type="str"),
        type=dict(
            type="str",
            choices=[
                "library",
                "pds",
                "pdse",
                "seq",
                "basic",
                "large",
                "ksds",
                "rrds",
                "lds",
                "esds",
            ],
        ),
        encryption_key_1=dict(
            type="dict",
            options=dict(
                label=dict(type="str", required=True),
                encoding=dict(type="str", required=True, choices=["l", "h"]),
            ),
        ),
        encryption_key_2=dict(
            type="dict",
            options=dict(
                label=dict(type="str", required=True),
                encoding=dict(type="str", required=True, choices=["l", "h"]),
            ),
        ),
        key_length=dict(type="int"),
        key_offset=dict(type="int"),
        record_length=dict(type="int"),
        record_format=dict(
            type="str", choices=["u", "v", "vb", "vba", "f", "fb", "fba"]
        ),
        return_content=dict(
            type="dict",
            options=dict(
                type=dict(type="str", choices=["text", "base64"], required=True),
                src_encoding=dict(type="str", default="ibm-1047"),
                response_encoding=dict(type="str", default="iso8859-1"),
            ),
        ),
    )

    dd_input_base = dict(
        content=dict(type="raw", required=True),
        return_content=dict(
            type="dict",
            options=dict(
                type=dict(type="str", choices=["text", "base64"], required=True),
                src_encoding=dict(type="str", default="ibm-1047"),
                response_encoding=dict(type="str", default="iso8859-1"),
            ),
        ),
    )

    dd_unix_base = dict(
        path=dict(type="str", required=True),
        disposition_normal=dict(type="str", choices=["keep", "delete"]),
        disposition_abnormal=dict(type="str", choices=["keep", "delete"]),
        mode=dict(type="int"),
        status_group=dict(
            type="list",
            elements="str",
            choices=[
                "ocreat",
                "oexcl",
                "oappend",
                "ordwr",
                "ordonly",
                "owronly",
                "onoctty",
                "ononblock",
                "osync",
                "otrunc",
            ],
        ),
        file_data_type=dict(
            type="str", choices=["binary", "text", "record"], default="binary"
        ),
        return_content=dict(
            type="dict",
            options=dict(
                type=dict(type="str", choices=["text", "base64"], required=True),
                src_encoding=dict(type="str", default="ibm-1047"),
                response_encoding=dict(type="str", default="iso8859-1"),
            ),
        ),
    )

    dd_dummy_base = dict()

    dd_concat_base = dict(
        dds=dict(
            type="list",
            elements="dict",
            options=dict(
                dd_data_set=dict(type="dict", options=dd_data_set_base),
                dd_input=dict(type="dict", options=dd_input_base),
                dd_unix=dict(type="dict", options=dd_unix_base),
            ),
        )
    )

    dd_data_set = dict(type="dict", options=dict(**dd_name_base, **dd_data_set_base))
    dd_unix = dict(type="dict", options=dict(**dd_name_base, **dd_unix_base))
    dd_input = dict(type="dict", options=dict(**dd_name_base, **dd_input_base))
    dd_dummy = dict(type="dict", options=dict(**dd_name_base, **dd_dummy_base))
    dd_concat = dict(type="dict", options=dict(**dd_name_base, **dd_concat_base))

    module_args = dict(
        program_name=dict(type="str"),
        auth=dict(type="bool", default=False),
        args=dict(type="str", required=False),
        dds=dict(
            type="list",
            elements="dict",
            options=dict(
                dd_data_set=dd_data_set,
                dd_unix=dd_unix,
                dd_input=dd_input,
                dd_concat=dd_concat,
                dd_dummy=dd_dummy,
            ),
        ),
        verbose=dict(type="bool", required=False),
        debug=dict(type="bool", required=False),
    )
    result = dict(changed=False, dd_names=[], ret_code=dict(code=0))
    response = {}
    try:

        module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
        parms = parse_and_validate_args(module.params)
        dd_statements = build_dd_statements(parms)
        program = parms.get("program_name")
        args = parms.get("args")
        authorized = parms.get("auth")
        program_response = run_zos_program(
            program=program,
            args=args,
            dd_statements=dd_statements,
            authorized=authorized,
        )
        if program_response.rc != 0 and program_response.stderr:
            raise ZOSRawError(program, program_response.stderr)

        response = build_response(program_response.rc, dd_statements)

    except Exception as e:
        module.fail_json(msg=repr(e), **result)

    result["changed"] = True
    to_return = {**result, **response}
    module.exit_json(**to_return)


def parse_and_validate_args(params):
    """Perform additional argument validation to validate and update input content,

    Args:
        params (dict): The raw module parameters as provided by AnsibleModule.

    Returns:
        dict: The module parameters after validation and content updates.
    """
    dd_name_base = dict(dd_name=dict(type="dd", required=True))

    dd_data_set_base = dict(
        data_set_name=dict(type="data_set", required=True),
        disposition=dict(type="str", choices=["new", "shr", "mod", "old"]),
        disposition_normal=dict(
            type="str", choices=["delete", "keep", "catalog", "uncatalog"]
        ),
        disposition_abnormal=dict(
            type="str", choices=["delete", "keep", "catalog", "uncatalog"]
        ),
        space_type=dict(type="str", choices=["trk", "cyl", "b", "k", "m", "g"]),
        space_primary=dict(type="int"),
        space_secondary=dict(type="int"),
        volumes=dict(type=volumes),
        sms_management_class=dict(type="str"),
        sms_storage_class=dict(type="str"),
        sms_data_class=dict(type="str"),
        block_size=dict(type="int"),
        block_size_type=dict(type="str", choices=["b", "k", "m", "g"]),
        key_label=dict(type="str"),
        type=dict(
            type="str",
            choices=[
                "library",
                "pds",
                "pdse",
                "seq",
                "basic",
                "large",
                "ksds",
                "rrds",
                "lds",
                "esds",
            ],
        ),
        encryption_key_1=dict(
            type="dict",
            options=dict(
                label=dict(type="str", required=True),
                encoding=dict(type="str", required=True, choices=["l", "h"]),
            ),
        ),
        encryption_key_2=dict(
            type="dict",
            options=dict(
                label=dict(type="str", required=True),
                encoding=dict(type="str", required=True, choices=["l", "h"]),
            ),
        ),
        key_length=dict(type="int"),
        key_offset=dict(type="int"),
        record_length=dict(type="int"),
        record_format=dict(
            type="str", choices=["u", "v", "vb", "vba", "f", "fb", "fba"]
        ),
        return_content=dict(
            type="dict",
            options=dict(
                type=dict(type="str", choices=["text", "base64"], required=True),
                src_encoding=dict(type="encoding", default="ibm-1047"),
                response_encoding=dict(type="encoding", default="iso8859-1"),
            ),
        ),
    )

    dd_input_base = dict(
        content=dict(type=dd_content, required=True),
        return_content=dict(
            type="dict",
            options=dict(
                type=dict(type="str", choices=["text", "base64"], required=True),
                src_encoding=dict(type="encoding", default="ibm-1047"),
                response_encoding=dict(type="encoding", default="iso8859-1"),
            ),
        ),
    )

    dd_unix_base = dict(
        path=dict(type="path", required=True),
        disposition_normal=dict(type="str", choices=["keep", "delete"]),
        disposition_abnormal=dict(type="str", choices=["keep", "delete"]),
        mode=dict(type="int"),
        status_group=dict(
            type="list",
            elements="str",
            choices=[
                "ocreat",
                "oexcl",
                "oappend",
                "ordwr",
                "ordonly",
                "owronly",
                "onoctty",
                "ononblock",
                "osync",
                "otrunc",
            ],
        ),
        file_data_type=dict(
            type="str", choices=["binary", "text", "record"], default="binary"
        ),
        return_content=dict(
            type="dict",
            options=dict(
                type=dict(type="str", choices=["text", "base64"], required=True),
                src_encoding=dict(type="encoding", default="ibm-1047"),
                response_encoding=dict(type="encoding", default="iso8859-1"),
            ),
        ),
    )

    dd_dummy_base = dict()

    dd_concat_base = dict(
        dds=dict(
            type="list",
            elements="dict",
            options=dict(
                dd_data_set=dict(type="dict", options=dd_data_set_base),
                dd_input=dict(type="dict", options=dd_input_base),
                dd_unix=dict(type="dict", options=dd_unix_base),
            ),
        )
    )

    dd_data_set = dict(type="dict", options=dict(**dd_name_base, **dd_data_set_base))
    dd_unix = dict(type="dict", options=dict(**dd_name_base, **dd_unix_base))
    dd_input = dict(type="dict", options=dict(**dd_name_base, **dd_input_base))
    dd_dummy = dict(type="dict", options=dict(**dd_name_base, **dd_dummy_base))
    dd_concat = dict(type="dict", options=dict(**dd_name_base, **dd_concat_base))

    module_args = dict(
        program_name=dict(type="str"),
        auth=dict(type="bool", default=False),
        args=dict(type="str", required=False),
        dds=dict(
            type="list",
            elements="dict",
            options=dict(
                dd_data_set=dd_data_set,
                dd_unix=dd_unix,
                dd_input=dd_input,
                dd_concat=dd_concat,
                dd_dummy=dd_dummy,
            ),
        ),
        verbose=dict(type="bool", required=False),
        debug=dict(type="bool", required=False),
    )
    parser = BetterArgParser(module_args)
    parsed_args = parser.parse_args(params)
    return parsed_args


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
    """Validate volume arguments.

    Args:
        contents (Union[str, list[str]]): The contents provided for the volume argument.
        dependencies (dict): Any arguments this argument is dependent on.

    Raises:
        ValueError: When invalid argument provided.

    Returns:
        list[str]: The contents returned as a list of volumes
    """
    if not contents:
        return None
    if not isinstance(contents, list):
        contents = [contents]
    for vol in contents:
        if not re.fullmatch(r"^[A-Z0-9]{1,6}$", str(vol), re.IGNORECASE,):
            raise ValueError('Invalid argument "{0}" for type "volumes".'.format(vol))
        vol = vol.upper()
    return contents


def build_dd_statements(parms):
    """Build a list of DDStatement objects from provided module parms.

    Args:
        parms (dict): Module parms after formatting and validation.

    Raises:
        ValueError: If no data definition can be found matching provided DD type.

    Returns:
        list[DDStatement]: List of DDStatement objects representing DD statements specified in module parms.
    """
    dd_statements = []
    for dd in parms.get("dds"):
        dd_name = get_dd_name(dd)
        data_definition = build_data_definition(dd)
        if data_definition is None:
            raise ValueError("No valid data definition found.")
        dd_statement = DDStatement(dd_name, data_definition)
        dd_statements.append(dd_statement)
    return dd_statements


def get_dd_name(dd):
    """Get the DD name from a dd parm as specified in module parms.

    Args:
        dd (dict): A single DD parm as specified in module parms.

    Returns:
        str: The DD name.
    """
    dd_name = ""
    if dd.get("dd_data_set"):
        dd_name = dd.get("dd_data_set").get("dd_name")
    elif dd.get("dd_unix"):
        dd_name = dd.get("dd_unix").get("dd_name")
    elif dd.get("dd_input"):
        dd_name = dd.get("dd_input").get("dd_name")
    elif dd.get("dd_dummy"):
        dd_name = dd.get("dd_dummy").get("dd_name")
    elif dd.get("dd_concat"):
        dd_name = dd.get("dd_concat").get("dd_name")
    return dd_name


def build_data_definition(dd):
    """Build a DataDefinition object for a particular DD parameter.

    Args:
        dd (dict): A single DD parm as specified in module parms.

    Returns:
        Union[list[RawDatasetDefinition, RawFileDefinition,
              RawStdinDefinition],
              RawDatasetDefinition, RawFileDefinition,
              RawStdinDefinition, DummyDefinition]: The DataDefinition object or a list of DataDefinition objects.
    """
    data_definition = None
    if dd.get("dd_data_set"):
        data_definition = RawDatasetDefinition(dd.get("dd_data_set"))
    elif dd.get("dd_unix"):
        data_definition = RawFileDefinition(dd.get("dd_unix"))
    elif dd.get("dd_input"):
        data_definition = RawStdinDefinition(dd.get("dd_input"))
    elif dd.get("dd_dummy"):
        data_definition = DummyDefinition()
    elif dd.get("dd_concat"):
        data_definition = []
        for single_dd in dd.get("dd_concat").get("dds", []):
            data_definition.append(build_data_definition(single_dd))
    return data_definition


# TODO: clean up data definition wrapper classes
class RawDatasetDefinition(DatasetDefinition):
    """Wrapper around DatasetDefinition to contain information about
    desired return contents.

    Args:
        DatasetDefinition (DatasetDefinition): Dataset DD data type to be used in a DDStatement.
    """

    def __init__(self, dd_data_set_parms):
        """Initialize RawDatasetDefinition

        Args:
            dd_data_set_parms (dict): dd_data_set parm as specified in module.
        """
        self.return_content = ReturnContent(
            **(dd_data_set_parms.pop("return_content", None) or {})
        )
        parms = self.restructure_parms(dd_data_set_parms)
        super().__init__(**parms)

    def restructure_parms(self, dd_data_set_parms):
        """Restructure parms to match expected input keys and values for DatasetDefinition.

        Args:
            dd_data_set_parms (dict): The parms with same keys as provided to the module.

        Returns:
            dict: Restructured parms in format expected by DatasetDefinition
        """
        DATA_SET_NAME_MAP = {
            "data_set_name": "dataset_name",
            "type": "type",
            "key_label": "dataset_key_label",
            "space_primary": "primary",
            "space_secondary": "secondary",
            "disposition_normal": "normal_disposition",
            "disposition_abnormal": "conditional_disposition",
            "sms_storage_class": "storage_class",
            "sms_data_class": "data_class",
            "sms_management_class": "management_class",
        }
        parms = remove_unused_args(dd_data_set_parms)
        parms.pop("dd_name", None)
        if parms.get("block_size_type") and parms.get("block_size"):
            parms["block_size"] = to_bytes(
                parms.get("block_size"), parms.get("block_size_type")
            )
        if parms.get("space_type"):
            if parms.get("space_primary"):
                parms["primary_unit"] = parms.get("space_type")
            if parms.get("space_secondary"):
                parms["secondary_unit"] = parms.get("space_type")
            parms.pop("space_type", None)
        if parms.get("encryption_key_1"):
            if parms.get("encryption_key_1").get("label"):
                parms["key_label1"] = parms.get("encryption_key_1").get("label")
            if parms.get("encryption_key_1").get("encoding"):
                parms["key_encoding1"] = parms.get("encryption_key_1").get("encoding")
            parms.pop("encryption_key_1", None)
        if parms.get("encryption_key_2"):
            if parms.get("encryption_key_2").get("label"):
                parms["key_label2"] = parms.get("encryption_key_2").get("label")
            if parms.get("encryption_key_2").get("encoding"):
                parms["key_encoding2"] = parms.get("encryption_key_2").get("encoding")
            parms.pop("encryption_key_2", None)
        parms = rename_parms(parms, DATA_SET_NAME_MAP)
        return parms


class RawFileDefinition(FileDefinition):
    """Wrapper around FileDefinition to contain information about
    desired return contents.

    Args:
        FileDefinition (FileDefinition): File DD data type to be used in a DDStatement.
    """

    def __init__(self, dd_unix_parms):
        """Initialize RawFileDefinition

        Args:
            dd_unix_parms (dict): dd_unix parms as specified in module.
        """
        self.return_content = ReturnContent(
            **(dd_unix_parms.pop("return_content", None) or {})
        )
        parms = self.restructure_parms(dd_unix_parms)
        super().__init__(**parms)

    def restructure_parms(self, dd_unix_parms):
        """Restructure parms to match expected input keys and values for FileDefinition.

        Args:
            dd_unix_parms (dict): The parms with same keys as provided to the module.

        Returns:
            dict: Restructured parms in format expected by FileDefinition
        """
        UNIX_NAME_MAP = {
            "path": "path_name",
            "disposition_normal": "normal_disposition",
            "disposition_abnormal": "conditional_disposition",
            "mode": "path_mode",
            "file_data_type": "file_data",
        }
        parms = remove_unused_args(dd_unix_parms)
        parms.pop("dd_name", None)
        parms = rename_parms(parms, UNIX_NAME_MAP)
        return parms


class RawStdinDefinition(StdinDefinition):
    """Wrapper around StdinDefinition to contain information about
    desired return contents.

    Args:
        StdinDefinition (StdinDefinition): Stdin DD data type to be used in a DDStatement.
    """

    def __init__(self, dd_input_parms):
        """Initialize RawStdinDefinition

        Args:
            dd_input_parms (dict): dd_input parms as specified in module.
        """
        parms = dd_input_parms
        parms.pop("dd_name", None)
        self.return_content = ReturnContent(**(parms.pop("return_content", None) or {}))
        super().__init__(**parms)


class ReturnContent(object):
    """Holds information about what type of content
    should be returned for a particular DD, if any.

    Args:
        object (object): The most base type.
    """

    def __init__(self, type=None, src_encoding=None, response_encoding=None):
        """Initialize ReturnContent

        Args:
            type (str, optional): The type of content to return.
                    Defaults to None.
            src_encoding (str, optional): The encoding of the data set or file on the z/OS system.
                    Defaults to None.
            response_encoding (str, optional): The encoding to use when returning the contents of the data set or file.
                    Defaults to None.
        """
        self.type = type
        self.src_encoding = src_encoding
        self.response_encoding = response_encoding


def to_bytes(size, unit):
    """Convert sizes of various units to bytes.

    Args:
        size (int): The size to convert.
        unit (str): The unit of size.

    Returns:
        int: The size converted to bytes.
    """
    num_bytes = 0
    if unit == "b":
        num_bytes = size
    elif unit == "k":
        num_bytes = size * 1024
    elif unit == "m":
        num_bytes = size * 1048576
    elif unit == "g":
        num_bytes = size * 1073741824
    return num_bytes


def rename_parms(parms, name_map):
    """Rename parms based on a provided dictionary.

    Args:
        parms (dict): The parms before name remapping.
        name_map (dict): The dictionary to use for name mapping.

    Returns:
        dict: The parms after name mapping.
    """
    renamed_parms = {}
    for key, value in parms.items():
        if name_map.get(key):
            renamed_parms[name_map.get(key)] = value
        else:
            renamed_parms[key] = value
    return renamed_parms


def remove_unused_args(parms):
    """Remove unused arguments from a dictionary.
    Does not function recursively.

    Args:
        parms (dict): The dictionary to remove unused arguments from.

    Returns:
        dict: The dictionary without any unused arguments.
    """
    return {key: value for key, value in parms.items() if value is not None}


def run_zos_program(program, args="", dd_statements=[], authorized=False):
    """Run a program on z/OS.

    Args:
        program (str): The name of the program to run.
        args (str, optional): Additional argument string if required. Defaults to "".
        dd_statements (list[DDStatement], optional): DD statements to allocate for the program. Defaults to [].
        authorized (bool, optional): Determines if program will execute as an authorized user. Defaults to False.

    Returns:
        MVSCmdResponse: Holds the response information for program execution.
    """
    response = None
    if authorized:
        response = MVSCmd.execute_authorized(pgm=program, args=args, dds=dd_statements)
    else:
        response = MVSCmd.execute(pgm=program, args=args, dds=dd_statements)
    return response


def build_response(rc, dd_statements):
    """Build response dictionary to return at module completion.

    Args:
        rc (int): The return code of the program.
        dd_statements (list[DDStatement]): The DD statements for the program.

    Returns:
        dict: Response dictionary in format expected for response on module completion.
    """
    response = {"ret_code": {"code": rc}}
    response["dd_names"] = gather_output(dd_statements)
    return response


def gather_output(dd_statements):
    """Gather DD contents for all DD statements for which
    content was requested.

    Args:
        dd_statements (list[DDStatement]): The DD statements for the program.

    Returns:
        list[dict]: The list of DD outputs, in format expected for response on module completion.
    """
    output = []
    for dd_statement in dd_statements:
        output += get_dd_output(dd_statement)
    return output


def get_dd_output(dd_statement):
    """Get the output for a single DD statement.

    Args:
        dd_statement (DDStatement): A single DD statement.

    Returns:
        list[dict]: The output of a single DD, in format expected for response on module completion.
    """
    dd_output = []
    if (
        isinstance(dd_statement.definition, RawDatasetDefinition)
        and dd_statement.definition.return_content.type
    ):
        dd_output = [get_data_set_output(dd_statement)]
    elif (
        isinstance(dd_statement.definition, RawFileDefinition)
        and dd_statement.definition.return_content.type
    ):
        dd_output = [get_unix_file_output(dd_statement)]
    elif (
        isinstance(dd_statement.definition, RawStdinDefinition)
        and dd_statement.definition.return_content.type
    ):
        dd_output = [get_data_set_output(dd_statement)]
    elif isinstance(dd_statement.definition, list):
        dd_output = get_concatenation_output(dd_statement)
    return dd_output


def get_data_set_output(dd_statement):
    """Get the output of a single data set DD statement.

    Args:
        dd_statement (DDStatement): A single DD statement.

    Returns:
        dict: The output of a single DD, in format expected for response on module completion.
    """
    contents = ""
    if dd_statement.definition.return_content.type == "text":
        contents = get_data_set_content(
            name=dd_statement.definition.name,
            binary=False,
            from_encoding=dd_statement.definition.return_content.src_encoding,
            to_encoding=dd_statement.definition.return_content.response_encoding,
        )
    elif dd_statement.definition.return_content.type == "base64":
        contents = get_data_set_content(name=dd_statement.definition.name, binary=True)
    return build_dd_response(dd_statement.name, dd_statement.definition.name, contents)


def get_unix_file_output(dd_statement):
    """Get the output of a single unix file DD statement.

    Args:
        dd_statement (DDStatement): A single DD statement.

    Returns:
        dict: The output of a single DD, in format expected for response on module completion.
    """
    contents = ""
    if dd_statement.definition.return_content.type == "text":
        contents = get_unix_content(
            name=dd_statement.definition.name,
            binary=False,
            from_encoding=dd_statement.definition.return_content.src_encoding,
            to_encoding=dd_statement.definition.return_content.response_encoding,
        )
    elif dd_statement.definition.return_content.type == "base64":
        contents = get_unix_content(name=dd_statement.definition.name, binary=True)
    return build_dd_response(dd_statement.name, dd_statement.definition.name, contents)


def get_concatenation_output(dd_statement):
    """Get the output of a single concatenation DD statement.

    Args:
        dd_statement (DDStatement): A single DD statement.

    Returns:
        list[dict]: The output of a single DD, in format expected for response on module completion.
                Response can contain multiple outputs.
    """
    dd_response = gather_output(dd_statement.definition)
    return dd_response


def build_dd_response(dd_name, name, contents):
    """Gather additional response metrics and format
    as expected for response on module completion.

    Args:
        dd_name (str): The DD name associated with this response.
        name (str): The data set or unix file name associated with the response.
        contents (str): The raw contents taken from the data set or unix file.

    Returns:
        dict: Response content info of a single DD, in format expected for response on module completion.
    """
    dd_response = {}
    dd_response["dd_name"] = dd_name
    dd_response["name"] = name
    dd_response["content"] = contents.split("\n")
    dd_response["record_count"] = len(dd_response.get("content", []))
    dd_response["byte_count"] = len(contents.encode("utf-8"))
    return dd_response


def get_data_set_content(name, binary=False, from_encoding=None, to_encoding=None):
    """Retrieve the raw contents of a data set.

    Args:
        name (str): The name of the data set.
        binary (bool, optional): Determines if contents are retrieved without encoding conversion. Defaults to False.
        from_encoding (str, optional): The encoding of the data set on the z/OS system. Defaults to None.
        to_encoding (str, optional): The encoding to receive the data back in. Defaults to None.

    Returns:
        str: The raw content of the data set.
    """
    quoted_name = quote(name)
    if "'" not in quoted_name:
        quoted_name = "'{0}'".format(quoted_name)
    return get_content(
        '"//{0}"'.format(quoted_name), binary, from_encoding, to_encoding
    )


def get_unix_content(name, binary=False, from_encoding=None, to_encoding=None):
    """Retrieve the raw contents of a unix file.

    Args:
        name (str): The name of the unix file.
        binary (bool, optional): Determines if contents are retrieved without encoding conversion. Defaults to False.
        from_encoding (str, optional): The encoding of the unix file on the z/OS system. Defaults to None.
        to_encoding (str, optional): The encoding to receive the data back in. Defaults to None.

    Returns:
        str: The raw content of the unix file.
    """
    return get_content("{0}".format(quote(name)), binary, from_encoding, to_encoding)


def get_content(formatted_name, binary=False, from_encoding=None, to_encoding=None):
    """Retrieve raw contents of a data set or unix file.

    Args:
        name (str): The name of the data set or unix file, formatted and quoted for proper usage in command.
        binary (bool, optional): Determines if contents are retrieved without encoding conversion. Defaults to False.
        from_encoding (str, optional): The encoding of the data set or unix file on the z/OS system. Defaults to None.
        to_encoding (str, optional): The encoding to receive the data back in. Defaults to None.

    Returns:
        str: The raw content of the data set or unix file. If unsuccessful in retrieving data, returns empty string.
    """
    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
    conversion_command = ""
    if not binary:
        conversion_command = " | iconv -f {0} -t {1}".format(
            quote(from_encoding), quote(to_encoding)
        )
    # * name argument should already be quoted by the time it reaches here
    rc, stdout, stderr = module.run_command(
        "cat {0}{1}".format(formatted_name, conversion_command), use_unsafe_shell=True
    )
    if rc:
        return ""
    else:
        return stdout


class ZOSRawError(Exception):
    def __init__(self, program="", error=""):
        self.msg = "An error occurred during execution of z/OS program {0}. {1}".format(
            program, error
        )
        super().__init__(self.msg)


def main():
    run_module()


if __name__ == "__main__":
    main()
