#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'comminuty'}

DOCUMENTATION = r'''
---
module: zos_blockinfile
author:
  - "Behnam (@balkajbaf)"
short_description: Manage block of multi-line textual data on z/OS
description:
  - Manage block of multi-lines in z/OS UNIX System Services (USS) files,
    PS(sequential data set), PDS, PDSE, or member of a PDS or PDSE.
  - This module ensures a particular block of multi-line text surrounded
    by customizable marker lines is present in a USS file or data set, or
    replaces an existing block identified by the markers.
  - This is primarily useful when you want to change a block of multi-line
    text in a USS file or data set.
options:
  src:
    description:
      - The location can be a UNIX System Services (USS) file,
        PS(sequential data set), member of a PDS or PDSE, PDS, PDSE.
      - The USS file must be an absolute pathname.
    type: str
    aliases: [ path, destfile, name ]
    required: true
  state:
    description:
      - Whether the block should be inserted/replaced (present) or removed (absent).
    type: str
    choices:
      - absent
      - present
    default: present
  marker:
    description:
    - The marker line template.
    - C({mark}) will be replaced with the values C(in marker_begin)
      (default="BEGIN") and C(marker_end) (default="END").
    - Using a custom marker without the C({mark}) variable may result
      in the block being repeatedly inserted on subsequent playbook runs.
    required: false
    type: str
    default: '# {mark} ANSIBLE MANAGED BLOCK'
  block:
    description:
    - The text to insert inside the marker lines.
    - If it is missing or an empty string, the block will be removed as if
      C(state) were specified to C(absent).
    - Multi-line can be separated by '\n'.
    required: false
    type: str
    default: ''
    aliases: [ content ]
  insertafter:
    description:
    - If specified, the block will be inserted after the last match of the specified
      regular expression.
    - A special value C(EOF) for inserting a block at the end of the file is
      available.
    - If a specified regular expression has no matches, C(EOF) will be used instead.
    - Choices are EOF or '*regex*'.
    - Default is EOF.
    required: false
    type: str
  insertbefore:
    description:
    - If specified, the block will be inserted before the last match of specified
      regular expression.
    - A special value C(BOF) for inserting the block at the beginning of the file
      is available.
    - If a specified regular expression has no matches, the block will be inserted
      at the end of the file.
    - Choices are BOF or '*regex*'.
    required: false
    type: str
  marker_begin:
    description:
    - This will be inserted at C({mark}) in the opening ansible block marker.
    required: false
    type: str
    default: BEGIN
  marker_end:
    required: false
    description:
    - This will be inserted at C({mark}) in the closing ansible block marker.
    type: str
    default: END
  backup:
    description:
      - Creates a backup file or backup data set for I(src), including the
        timestamp information to ensure that you retrieve the original file.
      - I(back_name) can be used to specify a backup file name
        if I(backup=true).
      - The backup file name will be returned on both success and failure
        of module execution such that data can be retrieved.
    required: false
    type: bool
    default: false
  back_name:
    description:
      - Specify the USS file name or data set name for the destination backup.
      - If the source I(src) is a USS file or path, the back_name name must be a file
        or path name, and the USS file or path must be an absolute path name.
      - If the source is an MVS data set, the back_name name must be an MVS
        data set name.
      - If the back_name is not provided, the default back_name name will
        be used. If the source is a USS file or path, the name of the backup
        file will be the source file or path name appended with a
        timestamp, e.g. C(/path/file_name.2020-04-23-08-32-29-bak.tar).
      - If the source is an MVS data set, it will be a data set with a random
        name generated by calling the ZOAU API. The MVS backup data set
        recovery can be done by renaming it.
    required: false
    type: str
  encoding:
    description:
      - The character set of the source I(src). M(zos_lineinfile)
        requires to be provided with correct encoding to read the content
        of USS file or data set. If this parameter is not provided, this
        module assumes that USS file or data set is encoded in IBM-1047.
      - Supported character sets rely on the charset conversion utility (iconv)
        version; the most common character sets are supported.
    required: false
    type: str
    default: IBM-1047
notes:
  - It is the playbook author or user's responsibility to avoid files
    that should not be encoded, such as binary files. A user is described
    as the remote user, configured either for the playbook or playbook
    tasks, who can also obtain escalated privileges to execute as root
    or another user.
  - All data sets are always assumed to be cataloged. If an uncataloged data set
    needs to be encoded, it should be cataloged first.
  - For supported character sets used to encode data, refer to
    U(https://ansible-collections.github.io/ibm_zos_core/supplementary.html#encode)
  - When using 'with_*' loops be aware that if you do not set a unique mark
    the block will be overwritten on each iteration.
  - When more then one block should be handled in a file you must change
    the I(marker) per task.
'''

EXAMPLES = r'''
- name: Insert/Update new mount point
  zos_blockinfile:
    src: SYS1.PARMLIB(BPXPRM00)
    marker: "/* {mark} ANSIBLE MANAGED BLOCK */"
    block: |
      " MOUNT FILESYSTEM('SOME.DATA.SET') TYPE(ZFS) MODE(READ)"
      "    MOUNTPOINT('/tmp/src/somedirectory')"

- name: Remove a library as well as surrounding markers
  zos_blockinfile:
    src: SYS1.PARMLIB(PROG00)
    marker: "/* {mark} ANSIBLE MANAGED BLOCK FOR SOME.DATA.SET */"
    block: ""

- name: Insert/Update eth0 configuration in /etc/network/interfaces
  zos_blockinfile:
    src: /etc/network/interfaces
    insertafter: "auto eth0"
    block: |
      iface eth0 inet static
          address 192.0.2.23
          netmask 255.255.255.0

- name: Insert/Update HTML surrounded by custom markers after <body> line
  zos_blockinfile:
    path: /var/www/html/index.html
    marker: "<!-- {mark} ANSIBLE MANAGED BLOCK -->"
    insertafter: "<body>"
    block: |
      <h1>Welcome to {{ ansible_hostname }}</h1>
      <p>Last updated on {{ ansible_date_time.iso8601 }}</p>

- name: Remove HTML as well as surrounding markers
  zos_blockinfile:
    path: /var/www/html/index.html
    state: absent
    marker: "<!-- {mark} ANSIBLE MANAGED BLOCK -->"
    block: ""

- name: Add mappings to /etc/hosts
  zos_blockinfile:
    path: /etc/hosts
    block: |
      {{ item.ip }} {{ item.name }}
    marker: "# {mark} ANSIBLE MANAGED BLOCK {{ item.name }}"
  loop:
    - { name: host1, ip: 10.10.1.10 }
    - { name: host2, ip: 10.10.1.11 }
    - { name: host3, ip: 10.10.1.12 }
'''

RETURN = r"""
changed:
  description: Indicates if the source was modified
  returned: success
  type: bool
  sample: 1
found:
  description: Number of the matching patterns
  returned: success
  type: int
  sample: 5
cmd:
  description: constructed dmod shell cmd based on the parameters
  returned: success
  type: str
  sample: dmodhelper -d -b -c IBM-1047 -m "BEGIN\nEND\n# {mark} ANSIBLE MANAGED BLOCK" -s -e "/^PATH=/a\\PATH=/dir/bin:$PATH/$" -e "$ a\\PATH=/dir/bin:$PATH" /etc/profile
msg:
  description: The module messages
  returned: failure
  type: str
  sample: Parameter verification failed
stdout:
  description: The stdout from ZOAU dmod when json.loads() fails
  returned: failure
  type: str
stderr:
  description: The error messages from ZOAU dmod
  returned: failure
  type: str
  sample: BGYSC1311E Iconv error, cannot open converter from ISO-88955-1 to IBM-1047
rc:
  description: The return code from ZOAU dmod when json.loads() fails
  returned: failure
  type: bool
back_name:
    description: Name of the backup file or data set that was created.
    returned: if backup=true
    type: str
    sample: /path/to/file.txt.2015-02-03@04:15~
"""

import json
from ansible.module_utils.six import b
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes
from ansible.module_utils.six import PY3
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser, data_set, backup as Backup)
from os import path
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)

try:
    from zoautil_py import datasets
except Exception:
    Datasets = MissingZOAUImport()

if PY3:
    from shlex import quote
else:
    from pipes import quote

# supported data set types
DS_TYPE = ['PS', 'PO']


def present(src, block, marker, ins_aft, ins_bef, encoding):
    """Replace a block with the matching regex pattern
    Insert a block before/after the matching pattern
    Insert a block at BOF/EOF

    Arguments:
        src: {str} -- The z/OS USS file or data set to modify.
        block: {str} -- The block to insert/replace into the src.
        marker: {str} -- The block will be inserted/updated with the markers.
        ins_aft: {str} -- Insert the block after matching '*regex*' pattern or EOF.
            choices:
                - EOF
                - '*regex*'
        ins_bef: {str} -- Insert the block before matching '*regex*' pattern or BOF.
            choices:
                - BOF
                - '*regex*'
        encoding: {str} -- Encoding of the src.

    Returns:
        str -- Information in JSON format. keys:
            cmd: {str} -- dmod shell command
            found: {int} -- Number of matching regex pattern
            changed: {bool} -- Indicates if the destination was modified.
    """
    return datasets.blockinfile(src, block=block, marker=marker, ins_aft=ins_aft, ins_bef=ins_bef, encoding=encoding, state=True, debug=True)


def absent(src, marker, encoding):
    """Delete blocks with matching regex pattern

    Arguments:
        src: {str} -- The z/OS USS file or data set to modify.
        marker: {str} -- Identifies the block to be removed.
        encoding: {str} -- Encoding of the src.

    Returns:
        str -- Information in JSON format. keys:
            cmd: {str} -- dmod shell command
            found: {int} -- Number of matching regex pattern
            changed: {bool} -- Indicates if the destination was modified.
    """
    return datasets.blockinfile(src, marker=marker, encoding=encoding, state=False, debug=True)


def quotedString(string):
    # add escape if string was quoted
    if not isinstance(string, str):
        return string
    return string.replace('"', '\\\"')


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(
                type='str',
                required=True,
                aliases=['path', 'destfile', 'name']
            ),
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present']
            ),
            marker=dict(
                type='str',
                default='# {mark} ANSIBLE MANAGED BLOCK'
            ),
            block=dict(
                type='str',
                default='',
                aliases=['content']
            ),
            insertafter=dict(
                type='str'
            ),
            insertbefore=dict(
                type='str'
            ),
            marker_begin=dict(
                type='str',
                default='BEGIN'
            ),
            marker_end=dict(
                type='str',
                default='END'
            ),
            backup=dict(
                type='bool',
                default=False
            ),
            back_name=dict(
                type='str',
                required=False,
                default=None
            ),
            encoding=dict(
                type='str',
                default='IBM-1047'
            ),
        ),
        mutually_exclusive=[['insertbefore', 'insertafter']],
    )

    params = module.params

    arg_defs = dict(
        src=dict(arg_type='data_set_or_path', aliases=['path', 'destfile', 'name'], required=True),
        state=dict(arg_type='str', default='present', choices=['absent', 'present']),
        marker=dict(arg_type='str', default='# {mark} ANSIBLE MANAGED BLOCK', required=False),
        block=dict(arg_type='str', default='', aliases=['content'], required=False),
        insertafter=dict(arg_type='str', required=False),
        insertbefore=dict(arg_type='str', required=False),
        marker_begin=dict(arg_type='str', default='BEGIN', required=False),
        marker_end=dict(arg_type='str', default='END', required=False),
        encoding=dict(arg_type='str', default='IBM-1047', required=False),
        backup=dict(arg_type='bool', default=False, required=False),
        back_name=dict(arg_type='data_set_or_pat', required=False, default=None),
        mutually_exclusive=[['insertbefore', 'insertafter']],
    )
    result = dict(changed=False, cmd='', found=0)
    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    backup = parsed_args.get('backup')
    if parsed_args.get('back_name') and backup:
        backup = parsed_args.get('back_name')
    src = parsed_args.get('src')
    ins_aft = parsed_args.get('insertafter')
    ins_bef = parsed_args.get('insertbefore')
    encoding = parsed_args.get('encoding')
    block = parsed_args.get('block')
    marker = parsed_args.get('marker')
    marker_begin = parsed_args.get('marker_begin')
    marker_end = parsed_args.get('marker_end')

    if not block and parsed_args.get('state') == 'present':
        module.fail_json(msg='block is required with state=present')
    if not marker:
        marker = '# {mark} ANSIBLE MANAGED BLOCK'
    if "{mark}" not in marker:
        module.fail_json(msg='marker should have {mark}')
    # make sure the default encoding is set if empty string was passed
    if not encoding:
        encoding = "IBM-1047"
    if not ins_aft and not ins_bef and parsed_args.get('state') == 'present':
        ins_aft = "EOF"
    if not marker_begin:
        marker_begin = 'BEGIN'
    if not marker_end:
        marker_end = 'END'

    marker = "{0}\\n{1}\\n{2}".format(marker_begin, marker_end, marker)
    blocklines = block.splitlines()
    block = '\\n'.join(blocklines)

    # analysis the file type
    ds_utils = data_set.DataSetUtils(src)
    file_type = ds_utils.ds_type()
    if file_type == 'USS':
        file_type = 1
    else:
        if file_type not in DS_TYPE:
            message = "{0} data set type is NOT supported".format(str(file_type))
            module.fail_json(msg=message)
        file_type = 0

    if backup:
        # backup can be True(bool) or none-zero length string. string indicates that back_name was provided.
        # setting backup to None if back_name wasn't provided. if backup=None, Backup module will use
        # pre-defined naming scheme and return the created destination name.
        if isinstance(backup, bool):
            backup = None
        try:
            if file_type:
                result['back_name'] = Backup.uss_file_backup(src, backup_name=backup, compress=False)
            else:
                result['back_name'] = Backup.mvs_file_backup(dsn=src, bk_dsn=backup)
        except Exception:
            module.fail_json(msg="creating backup has failed")
    # state=present, insert/replace a block with matching regex pattern
    # state=absent, delete blocks with matching regex pattern
    if parsed_args.get('state') == 'present':
        return_content = present(src, quotedString(block), quotedString(marker), quotedString(ins_aft), quotedString(ins_bef), encoding)
    else:
        return_content = absent(src, quotedString(marker), encoding)
    stdout = return_content.stdout_response
    stderr = return_content.stderr_response
    rc = return_content.rc
    try:
        # change the return string to be loadable by json.loads()
        stdout = stdout.replace('/c\\', '/c\\\\')
        stdout = stdout.replace('/a\\', '/a\\\\')
        stdout = stdout.replace('/i\\', '/i\\\\')
        stdout = stdout.replace('$ a\\', '$ a\\\\')
        stdout = stdout.replace('1 i\\', '1 i\\\\')
        if block:
            stdout = stdout.replace(block, quotedString(block))
        if ins_aft:
            stdout = stdout.replace(ins_aft, quotedString(ins_aft))
        if ins_bef:
            stdout = stdout.replace(ins_bef, quotedString(ins_bef))
        # Try to extract information from stdout
        ret = json.loads(stdout)
        result['cmd'] = ret['cmd']
        result['changed'] = ret['changed']
        result['found'] = ret['found']
    except Exception:
        messageDict = dict(msg="dmod return content is NOT in json format", stdout=str(stdout), stderr=str(stderr), rc=rc)
        if result.get('back_name'):
            messageDict['back_name'] = result['back_name']
        module.fail_json(**messageDict)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
