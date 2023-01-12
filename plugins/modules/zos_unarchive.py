#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2022
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zos_unarchive
version_added: "1.7.0"
author:
  - Oscar Fernando Flores Garcia (@fernandofloresg)
short_description: Unarchive a dataset on z/OS.
description:
  - The C(zos_unarchive) module unpacks an archive. It will not unpack a compressed file that does not contain an archive.
  - By default, it will copy the source file from the local system to the target before unpacking.
  - Set C(remote_src=yes) to unpack an archive which already exists on the target.
  - If checksum validation is desired, use M(ansible.builtin.get_url) or M(ansible.builtin.uri) instead to fetch the file and set C(remote_src=yes).
options:
    src:
      description:
        - If C(remote_src=no) (default), local path to archive file to copy to the target server; can be absolute or relative. If C(remote_src=yes), path on the
          target server to existing archive file to unpack.
        - If C(remote_src=yes) and C(src) contains C(://), the remote machine will download the file from the URL first. (version_added 2.0). This is only for
          simple cases, for full download support use the M(ansible.builtin.get_url) module.
      type: path
      required: true
  dest:
    description:
      - Remote absolute path where the archive should be unpacked.
      - The given path must exist. Base directory is not created by this module.
    type: path
    required: true
  copy:
    description:
      - If true, the file is copied from local controller to the managed (remote) node, otherwise, the plugin will look for src archive on the managed machine.
      - This option has been deprecated in favor of C(remote_src).
      - This option is mutually exclusive with C(remote_src).
    type: bool
    default: yes
  creates:
    description:
      - If the specified absolute path (file or directory) already exists, this step will B(not) be run.
      - The specified absolute path (file or directory) must be below the base path given with C(dest:).
    type: path
    version_added: "1.6"
  io_buffer_size:
    description:
      - Size of the volatile memory buffer that is used for extracting files from the archive in bytes.
    type: int
    default: 65536
    version_added: "2.12"
  list_files:
    description:
      - If set to True, return the list of files that are contained in the tarball.
    type: bool
    default: no
    version_added: "2.0"
  exclude:
    description:
      - List the directory and file entries that you would like to exclude from the unarchive action.
      - Mutually exclusive with C(include).
    type: list
    default: []
    elements: str
    version_added: "2.1"
  include:
    description:
      - List of directory and file entries that you would like to extract from the archive. If C(include)
        is not empty, only files listed here will be extracted.
      - Mutually exclusive with C(exclude).
    type: list
    default: []
    elements: str
    version_added: "2.11"
  keep_newer:
    description:
      - Do not replace existing files that are newer than files from the archive.
    type: bool
    default: no
    version_added: "2.1"
  extra_opts:
    description:
      - Specify additional options by passing in an array.
      - Each space-separated command-line option should be a new element of the array. See examples.
      - Command-line options with multiple elements must use multiple lines in the array, one for each element.
    type: list
    elements: str
    default: []
    version_added: "2.1"
  remote_src:
    description:
      - Set to C(true) to indicate the archived file is already on the remote system and not local to the Ansible controller.
      - This option is mutually exclusive with C(copy).
    type: bool
    default: no
    version_added: "2.2"
  validate_certs:
    description:
      - This only applies if using a https URL as the source of the file.
      - This should only set to C(false) used on personally controlled sites using self-signed certificate.
      - Prior to 2.2 the code worked as if this was set to C(true).
    type: bool
    default: yes
    version_added: "2.2"
extends_documentation_fragment:
- action_common_attributes
- action_common_attributes.flow
- action_common_attributes.files
- decrypt
- files
attributes:
    action:
      support: full
    async:
      support: none
    bypass_host_loop:
      support: none
    check_mode:
      support: partial
      details: Not supported for gzipped tar files.
    diff_mode:
      support: partial
      details: Uses gtar's C(--diff) arg to calculate if changed or not. If this C(arg) is not supported, it will always unpack the archive.
    platform:
      platforms: posix
    safe_file_operations:
      support: none
    vault:
      support: full
todo:
    - Re-implement tar support using native tarfile module.
    - Re-implement zip support using native zipfile module.
notes:
    - Requires C(zipinfo) and C(gtar)/C(unzip) command on target host.
    - Requires C(zstd) command on target host to expand I(.tar.zst) files.
    - Can handle I(.zip) files using C(unzip) as well as I(.tar), I(.tar.gz), I(.tar.bz2), I(.tar.xz), and I(.tar.zst) files using C(gtar).
    - Does not handle I(.gz) files, I(.bz2) files, I(.xz), or I(.zst) files that do not contain a I(.tar) archive.
    - Existing files/directories in the destination which are not in the archive
      are not touched. This is the same behavior as a normal archive extraction.
    - Existing files/directories in the destination which are not in the archive
      are ignored for purposes of deciding if the archive should be unpacked or not.
seealso:
- module: community.general.archive
- module: community.general.iso_extract
- module: community.windows.win_unzip
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world
# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true
# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
state:
    description:
        The state of the input C(path).
    type: str
    returned: always
dest_state:
    description:
      - The state of the I(dest) file.
      - C(absent) when the file does not exist.
      - C(archive) when the file is an archive.
      - C(compress) when the file is compressed, but not an archive.
      - C(incomplete) when the file is an archive, but some files under I(path) were not found.
    type: str
    returned: success
    version_added: 3.4.0
missing:
    description: Any files that were missing from the source.
    type: list
    returned: success
archived:
    description: Any files that were compressed or added to the archive.
    type: list
    returned: success
arcroot:
    description: The archive root.
    type: str
    returned: always
expanded_paths:
    description: The list of matching paths from paths argument.
    type: list
    returned: always
expanded_exclude_paths:
    description: The list of matching exclude paths from the exclude_path argument.
    type: list
    returned: always
'''

def run_module():
    None


def main():
    run_module()


if __name__ == '__main__':
    main()