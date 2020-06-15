#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r"""
---
module: zos_lineinfile
author:
  - "Behnam (@balkajbaf)"
short_description: Manage textual data on z/OS
description:
  - Manage lines in z/OS Unix System Services (USS) files,
    PS(sequential data set), member of a PDS or PDSE data set.
  - This module ensures a particular line is in a USS file or data set, or
    replace an existing line using a back-referenced regular expression.
  - This is primarily useful when you want to change a single line in a USS
    file or data set only.
options:
  dest:
    description:
      - The location of the input characters.
      - The location can be a UNIX System Services (USS) file,
        PS(sequential data set), member of a PDS or PDSE data set.
      - The USS file must be an absolute pathname.
      - It is the playbook author or user's responsibility to avoid files
        that should not be encoded, such as binary files. A user is described
        as the remote user, configured either for the playbook or playbook
        tasks, who can also obtain escalated privileges to execute as root
        or another user.
    type: str
    aliases: [ path, destfile, destds, name ]
    required: true
  regexp:
    description:
      - The regular expression to look for in every line of the USS file
        or data set.
      - For C(state=present), the pattern to replace if found. Only the
        last line found will be replaced.
      - For C(state=absent), the pattern of the line(s) to remove.
      - If the regular expression is not matched, the line will be
        added to the USS file or data set in keeping with C(insertbefore) or
        C(insertafter) settings.
      - When modifying a line the regexp should typically match both
        the initial state of the line as well as its state after replacement by
        C(line) to ensure idempotence.
    type: str
    required: false
  state:
    description:
      - Whether the line should be inserted/replaced(present) or removed(absent).
    type: str
    choices:
      - absent
      - present
    default: present
  line:
    description:
      - The line to insert/replace into the USS file or data set.
      - Required for C(state=present).
      - If C(backrefs) is set, may contain backreferences that will get
        expanded with the C(regexp) capture groups if the regexp matches.
    required: false
    type: str
  backrefs:
    description:
      - Used with C(state=present).
      - If set, C(line) can contain backreferences (both positional and named)
        that will get populated if the C(regexp) matches.
      - This parameter changes the operation of the module slightly;
        C(insertbefore) and C(insertafter) will be ignored, and if the
        C(regexp) does not match anywhere in the USS file or data set, the USS file
        or data set will be left unchanged.
      - If the C(regexp) does match, the last matching line will be replaced by
        the expanded line parameter.
    required: false
    type: bool
    default: no
  insertafter:
    description:
      - Used with C(state=present).
      - If specified, the line will be inserted after the last match of
        specified regular expression.
      - If the first match is required, use(firstmatch=yes).
      - A special value is available; C(EOF) for inserting the line at the end
        of the USS file or data set.
      - If specified regular expression has no matches, EOF will be used
        instead.
      - If C(insertbefore) is set, default value C(EOF) will be ignored.
      - If regular expressions are passed to both C(regexp) and C(insertafter),
        C(insertafter) is only honored if no match for C(regexp) is found.
      - May not be used with C(backrefs) or C(insertbefore).
      - choices: EOF, '*regex*'
    required: false
    type: str
    default: EOF
  insertbefore:
    description:
      - Used with C(state=present).
      - If specified, the line will be inserted before the last match of
        specified regular expression.
      - If the first match is required, use C(firstmatch=yes).
      - A value is available; C(BOF) for inserting the line at the beginning of
        the USS file or data set.
      - If specified regular expression has no matches, the line will be
        inserted at the end of the USS file or data set.
      - If regular expressions are passed to both C(regexp) and
        C(insertbefore), C(insertbefore) is only honored if no match for
        C(regexp) is found.
      - May not be used with C(backrefs) or C(insertafter).
      - choices: BOF, '*regex*'
    required: false
    type: str
  backup:
    description:
      - Creates a backup file or backup data set for I(dest), including the
        timestamp information to ensure that you retrieve the original file.
      - I(backup_file) can be used to specify a backup file name
        if I(backup=true).
      - The backup file name will be return on either success or failure
        of module execution such that data can be retrieved.
    required: false
    type: bool
    default: false
  backup_file:
    description:
      - Specify the USS file name or data set name for the destination backup.
      - If the destination (dest) is a USS file or path, the backup_file name must be a file
        or path name, and the USS path or file must be an absolute path name.
      - If the destination is an MVS data set, the backup_file name must be an MVS
        data set name.
      - If the backup_file is not provided, the default backup_file name will
        be used. If the destination is a USS file or USS path, the name of the backup
        file will be the destination file or path name appended with a
        timestamp, e.g. C(/path/file_name.2020-04-23-08-32-29-bak.tar).
      - If the destination is an MVS data set, it will be a data set with a random
        name generated by calling the ZOAU API. The MVS backup data set
        recovery can be done by renaming it.
    required: false
    type: str
  firstmatch:
    description:
      - Used with C(insertafter) or C(insertbefore).
      - If set, C(insertafter) and C(insertbefore) will work with the first
        line that matches the given regular expression.
    required: false
    type: bool
    default: no
  encoding:
    description:
      - The character set of the destination I(dest). M(zos_lineinfile)
        requires to be provided with correct encoding to read the content
        of USS file or data set. If this parameter is not provided, this
        module assumes that USS file or data set is encoded in IBM-1047.
      - Supported character sets rely on the target version; the most
        common character sets are supported.
    required: false
    type: str
    default: IBM-1047
notes:
  - All data sets are always assumed to be cataloged. If an uncataloged data set
    needs to be encoded, it should be cataloged first.
  - For supported character sets used to encode data, refer to
    U(https://ansible-collections.github.io/ibm_zos_core/supplementary.html#encode)
"""

EXAMPLES = r"""
- name: Ensure value of a variable in the sequential data set
  zos_lineinfile:
    dest: SOME.DATA.SET
    regexp: '^VAR='
    line: VAR="some value"

- name: Remove all comments in the USS file
  zos_lineinfile:
    dest: /tmp/src/somefile
    state: absent
    regexp: '^#'

- name: Ensure the https port is 8080
  zos_lineinfile:
    dest: /tmp/src/somefile
    regexp: '^Listen '
    insertafter: '^#Listen '
    line: Listen 8080

- name: Ensure we have our own comment added to the partitioned data set member
  zos_lineinfile:
    dest: SOME.PARTITIONED.DATA.SET(DATA)
    regexp: '#^VAR='
    insertbefore: '^VAR='
    line: '# VAR default value'

- name: Ensure the user working directory for liberty is set as needed
  zos_lineinfile:
    dest: /tmp/src/somefile
    regexp: '^(.*)User(\d+)m(.*)$'
    line: '\1APPUser\3'
    backrefs: yes
"""

RETURN = r"""
changed:
  description: Indicates if the destination was modified
  returned: success
  type: bool
  sample: 1
found:
  description: Number of the matching patterns
  returned: success
  type: int
  sample: 5
cmd:
  description: constructed dsed shell cmd based on the parameters
  returned: success
  type: str
  sample: dsedhelper -d -en IBM-1047 /^PATH=/a\\PATH=/dir/bin:$PATH/$ /etc/profile
msg:
  description: The module messages
  returned: failure
  type: str
  sample: Parameter verification failed
return_content:
  description: The error messages from ZOAU dsed
  returned: failure
  type: str
  sample: BGYSC1311E Iconv error, cannot open converter from ISO-88955-1 to IBM-1047
backup_file:
    description: Name of the backup file or data set that was created.
    returned: if backup=true
    type: str
    sample: /path/to/file.txt.2015-02-03@04:15~
"""
import re
import json
from ansible.module_utils.basic import AnsibleModule
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
    from zoautil_py import Datasets
except Exception:
    Datasets = MissingZOAUImport()


# supported data set types
DS_TYPE = ['PS', 'PO']


def present(dest, line, regexp, ins_aft, ins_bef, encoding, first_match, backrefs):
    """Replace a line with the matching regex pattern
    Insert a line before/after the matching pattern
    Insert a line at BOF/EOF

    Arguments:
        dest: {str} -- The z/OS USS file or data set to modify.
        line: {str} -- The line to insert/replace into the dest.
        regexp: {str} -- The regular expression to look for in every line of the dest.
            If regexp matches, ins_aft/ins_bef will be ignored.
        ins_aft: {str} -- Insert the line after matching '*regex*' pattern or EOF.
            choices:
                - EOF
                - '*regex*'
        ins_bef: {str} -- Insert the line before matching '*regex*' pattern or BOF.
            choices:
                - BOF
                - '*regex*'
        encoding: {str} -- Encoding of the dest.
        first_match: {bool} -- Take the first matching regex pattern.
        backrefs: {bool} -- Back reference

    Returns:
        str -- Information in JSON format. keys:
            cmd: {str} -- dsed shell command
            found: {int} -- Number of matching regex pattern
            changed: {bool} -- Indicates if the destination was modified.
    """
    return Datasets.lineinfile(dest, line, regexp, ins_aft, ins_bef, encoding, first_match, backrefs, state=True)


def absent(dest, line, regexp, encoding):
    """Delete lines with matching regex pattern

    Arguments:
        dest: {str} -- The z/OS USS file or data set to modify.
        line: {str} -- The line to insert/replace into the the dest. If line matches,
            regexp will be ignored.
        regexp: {str} -- The regular expression to look for in every line of the dest.
        encoding: {str} -- Encoding of the dest.

    Returns:
        str -- Information in JSON format. keys:
            cmd: {str} -- dsed shell command
            found: {int} -- Number of matching regex pattern
            changed: {bool} -- Indicates if the destination was modified.
    """
    return Datasets.lineinfile(dest, line, regexp, encoding=encoding, state=False)


def main():
    module_args = dict(
        dest=dict(
            type='str',
            aliases=['path', 'destfile', 'destds', 'name'],
            required=True
        ),
        state=dict(
            type='str',
            default='present',
            choices=['absent', 'present']
        ),
        regexp=dict(type='str'),
        line=dict(type='str'),
        insertafter=dict(
            type='str',
            default='EOF'
        ),
        insertbefore=dict(
            type='str',
            default=None
        ),
        backrefs=dict(type='bool', default=False),
        backup=dict(type='bool', default=False),
        backup_file=dict(type='str', required=False, default=None),
        firstmatch=dict(type='bool', default=False),
        encoding=dict(type='str', default="IBM-1047"),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(changed=False, cmd='', found=0)

    arg_defs = dict(
        dest=dict(arg_type="data_set_or_path", aliases=['path', 'destfile', 'destds', 'name'], required=True),
        state=dict(arg_type="str", default='present', choices=['absent', 'present']),
        regexp=dict(arg_type="str", required=False),
        line=dict(arg_type="str", required=False),
        insertafter=dict(arg_type="str", default="EOF", required=False),
        insertbefore=dict(arg_type="str", required=False),
        encoding=dict(arg_type="str", default="IBM-1047", required=False),
        backup=dict(arg_type="bool", default=False, required=False),
        backup_file=dict(arg_type="data_set_or_path", required=False, default=None),
        firstmatch=dict(arg_type="bool", required=False, default=False),
        backrefs=dict(arg_type="bool", dependencies=['regexp'], required=False, default=False),
        mutually_exclusive=[["insertbefore", "insertafter"]],)

    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    backup = parsed_args.get('backup')
    # if backup_file is provided, update backup variable
    if parsed_args.get('backup_file') and backup:
        backup = parsed_args.get('backup_file')
    backrefs = parsed_args.get('backrefs')
    dest = parsed_args.get('dest')
    firstmatch = parsed_args.get('firstmatch')
    regexp = parsed_args.get('regexp')
    line = parsed_args.get('line')
    ins_aft = parsed_args.get('insertafter')
    ins_bef = parsed_args.get('insertbefore')
    encoding = parsed_args.get('encoding')

    # analysis the file type
    ds_utils = data_set.DataSetUtils(dest)
    file_type = ds_utils.ds_type()
    if file_type == 'USS':
        file_type = 1
    else:
        if file_type not in DS_TYPE:
            message = "{0} data set type is NOT supported".format(str(file_type))
            module.fail_json(msg=message)
        file_type = 0
    # make sure the default encoding is set if null was passed
    if not encoding:
        encoding = "IBM-1047"
    if backup:
        # backup can be True(bool) or none-zero length string. string indicates that backup_file was provided.
        # setting backup to None if backup_file wasn't provided. if backup=None, Backup module will use
        # pre-defined naming scheme and return the created destination name.
        if isinstance(backup, bool):
            backup = None
        try:
            if file_type:
                result['backup_file'] = Backup.uss_file_backup(dest, backup_name=backup, compress=False)
            else:
                result['backup_file'] = Backup.mvs_file_backup(dsn=dest, bk_dsn=backup)
        except Exception:
            module.fail_json(msg="creating backup has failed")
    # state=present, insert/replace a line with matching regex pattern
    # state=absent, delete lines with matching regex pattern
    if parsed_args.get('state') == 'present':
        if backrefs and regexp is None:
            module.fail_json(msg='regexp is required with backrefs=true')
        if line is None:
            module.fail_json(msg='line is required with state=present')
        if regexp is None and ins_aft is None and ins_bef is None:
            module.fail_json(msg='at least one of regexp/insertafter/insertbefore is required with state=present')
        return_content = present(dest, line, regexp, ins_aft, ins_bef, encoding, firstmatch, backrefs)
    else:
        if regexp is None and line is None:
            module.fail_json(msg='one of line or regexp is required with state=absent')
        return_content = absent(dest, line, regexp, encoding)
    try:
        # change the return string to be loadable by json.loads()
        return_content = return_content.replace('/c\\', '/c\\\\')
        return_content = return_content.replace('/a\\', '/a\\\\')
        return_content = return_content.replace('/i\\', '/i\\\\')
        return_content = return_content.replace('$ a\\', '$ a\\\\')
        return_content = return_content.replace('1 i\\', '1 i\\\\')
        # Try to extract information from return_content
        # If json.loads() fails, ZOAU dsed execution was failed.
        ret = json.loads(return_content)
        result['cmd'] = ret['cmd']
        result['changed'] = ret['changed']
        result['found'] = ret['found']
    except Exception:
        messageDict = dict(msg="dsed return content is NOT in json format", return_content=str(return_content))
        if result.get('backup_file'):
            messageDict['backup_file'] = result['backup_file']
        module.fail_json(**messageDict)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
