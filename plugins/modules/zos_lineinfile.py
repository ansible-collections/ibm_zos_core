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
  - Manage lines in z/OS Unix System Services (USS) files, partitioned data set
    members or sequential data sets.
  - This module ensures a particular line is in a USS file or data set, or
    replace an existing line using a back-referenced regular expression.
  - This is primarily useful when you want to change a single line in a USS
    file or dataset only.
options:
  zosdest:
    description:
      - The zos uss file or dataset to modify.
    type: str
    required: true
    aliases:
      - path
      - dest
      - destfile
      - name
      - zosdest
  regexp:
    description:
      - The regular expression to look for in every line of the uss file
        or dataset.
      - For C(state=present), the pattern to replace if found. Only the
        last line found will be replaced.
      - For C(state=absent), the pattern of the line(s) to remove.
      - If the regular expression is not matched, the line will be
        added to the file in keeping with C(insertbefore) or C(insertafter)
        settings.
      - When modifying a line the regexp should typically match both
        the initial state of the line as well as its state after replacement by
        C(line) to ensure idempotence.
      - Uses Python regular expressions.
        See U(http://docs.python.org/2/library/re.html).
    type: str
  state:
    description:
      - Whether the line should be there or not.
    type: str
    choices:
      - absent
      - present
    default: present
  line:
    description:
      - The line to insert/replace into the uss file or dataset.
      - Required for C(state=present).
      - If C(backrefs) is set, may contain backreferences that will get
        expanded with the C(regexp) capture groups if the regexp matches.
    type: str
    aliases:
      - value
  backrefs:
    description:
      - Used with C(state=present).
      - If set, C(line) can contain backreferences (both positional and named)
        that will get populated if the C(regexp) matches.
      - This parameter changes the operation of the module slightly;
        C(insertbefore) and C(insertafter) will be ignored, and if the
        C(regexp) does not match anywhere in the file, the file will be left
        unchanged.
      - If the C(regexp) does match, the last matching line will be replaced by
        the expanded line parameter.
    type: bool
    default: no
  insertafter:
    description:
      - Used with C(state=present).
      - If specified, the line will be inserted after the last match of
        specified regular expression.
      - If the first match is required, use(firstmatch=yes).
      - A special value is available; C(EOF) for inserting the line at the end
        of the file.
      - If specified regular expression has no matches, EOF will be used
        instead.
      - If C(insertbefore) is set, default value C(EOF) will be ignored.
      - If regular expressions are passed to both C(regexp) and C(insertafter),
        C(insertafter) is only honored if no match for C(regexp) is found.
      - May not be used with C(backrefs) or C(insertbefore).
    type: str
    choices:
      - EOF
      - '*regex*'
    default: EOF
  insertbefore:
    description:
      - Used with C(state=present).
      - If specified, the line will be inserted before the last match of
        specified regular expression.
      - If the first match is required, use C(firstmatch=yes).
      - A value is available; C(BOF) for inserting the line at the beginning of
        the uss file or dataset.
      - If specified regular expression has no matches, the line will be
        inserted at the end of the file.
      - If regular expressions are passed to both C(regexp) and
        C(insertbefore), C(insertbefore) is only honored if no match for
        C(regexp) is found.
      - May not be used with C(backrefs) or C(insertafter).
    type: str
    choices:
      - BOF
      - '*regex*'
  backup:
    description:
      - Creates a backup file or backup data set for I(dest), including the
        timestamp information to ensure that you retrieve the original file.
      - I(backup_file) can be used to specify a backup file name
        if I(backup=true).
    required: false
    type: bool
    default: false
  backup_file:
    description:
      - Specify the USS file name or data set name for the dest backup.
      - If dest is a USS file or path, I(backup_file) must be a file or
        path name, and the USS path or file must be an absolute pathname.
      - If dest is an MVS data set, the I(backup_file) must be an MVS data
        set name.
      - If I(backup_file) is not provided, the default backup name will be
        used.
      - The default backup name for a USS file or path will be the destination
        file or path name appended with a timestamp,
        e.g. /path/file_name.2020-04-23-08-32-29-bak.tar.
      - If dest is an MVS data set, the default backup name will be a random
        name generated by IBM Z Open Automation Utilities.
    required: false
    type: str
  firstmatch:
    description:
      - Used with C(insertafter) or C(insertbefore).
      - If set, C(insertafter) and C(insertbefore) will work with the first
        line that matches the given regular expression.
    type: bool
    default: no
  encoding:
    description:
      - Specifies the encoding of USS file or data set. M(zos_lineinfile)
        requires to be provided with correct encoding to read the content
        of USS file or data set. If this parameter is not provided, this
        module assumes that USS file or data set is encoded in IBM-1047.
    required: false
    type: str
    default: IBM-1047
"""

EXAMPLES = r"""
- name: Ensure dataset for cics SIT input has the SEC setting as YES
  lineinfile:
    path: XIAOPIN.TEST.TXT(SIT)
    regexp: '^SEC='
    line: SEC=YES

- name: Remove the encoding configuration in liberty profiles
  lineinfile:
    path: /samples/cicswlp_oci/LIBERTY.jvmprofile
    state: absent
    regexp: '^%encoding'

- name: Ensure the liberty https port is 8080
  lineinfile:
    path: /samples/cicswlp_oci/LIBERTY.jvmprofile
    regexp: '^Listen '
    insertafter: '^#Listen '
    line: Listen 8080

- name: Ensure we have our own comment added to CICS SIT member
  lineinfile:
    path: XIAOPIN.TEST.TXT(SIT)
    regexp: '#^SEC='
    insertbefore: '^SEC='
    line: '# security configuration by default'

- name: Ensure the user working directory for liberty is set as needed
  lineinfile:
    path: /samples/cicswlp_oci/LIBERTY.jvmprofile
    regexp: '^(.*)User(\d+)m(.*)$'
    line: '\1APPUser\3'
    backrefs: yes
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


def present(zosdest, line, regexp, ins_aft, ins_bef, encoding, first_match, backrefs, file_type):
    return Datasets.lineinfile(zosdest, line, regexp, ins_aft, ins_bef, encoding, first_match, backrefs, state=True)


def absent(zosdest, line, regexp, encoding, file_type):
    return Datasets.lineinfile(zosdest, line, regexp, encoding=encoding, state=False)


def main():
    module_args = dict(
        path=dict(
            type='str',
            required=True,
            aliases=['zosdest', 'dest', 'destfile', 'name']
        ),
        state=dict(
            type='str',
            default='present',
            choices=['absent', 'present']
        ),
        regexp=dict(type='str', aliases=['regex']),
        line=dict(type='str', aliases=['value']),
        insertafter=dict(
            type='str',
            default='EOF',
            choices=['EOF', '*regex*'],
        ),
        insertbefore=dict(
            type='str',
            default=None,
            choices=['BOF', '*regex*'],
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
    result = dict(changed=False, message='', found=0, backup='')

    arg_defs = dict(
        path=dict(arg_type="data_set_or_path", aliases=['zosdest', 'dest', 'destfile', 'name'], required=True),
        state=dict(arg_type="str", default='present', choices=['absent', 'present']),
        regexp=dict(arg_type="str", aliases=['regex'], required=False),
        line=dict(arg_type="str", aliases=['value'], required=False),
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
    if parsed_args.get('backup_file') and backup:
        backup = parsed_args.get('backup_file')
    backrefs = parsed_args.get('backrefs')
    path = parsed_args.get('path')
    firstmatch = parsed_args.get('firstmatch')
    regexp = parsed_args.get('regexp')
    line = parsed_args.get('line')
    ins_aft = parsed_args.get('insertafter')
    ins_bef = parsed_args.get('insertbefore')
    encoding = parsed_args.get('encoding')

    # analysis the file type
    ds_utils = data_set.DataSetUtils(path)
    file_type = ds_utils.ds_type()
    if file_type == 'USS':
        file_type = 1
    else:
        file_type = 0
    if not encoding:
        encoding = "IBM-1047"
    if backup:
        if type(backup) == bool:
            backup = None
        try:
            if file_type:
                result['backup'] = Backup.uss_file_backup(path, backup_name=backup, compress=False)
            else:
                result['backup'] = Backup.mvs_file_backup(dsn=path, bk_dsn=backup)
        except Exception:
            module.fail_json(msg="creating backup has failed")
    if parsed_args.get('state') == 'present':
        if backrefs and regexp is None:
            module.fail_json(msg='regexp is required with backrefs=true')
        if line is None:
            module.fail_json(msg='line is required with state=present')
        if regexp is None and ins_aft is None and ins_bef is None:
            module.fail_json(msg='at least one of regexp/insertafter/insertbefore is required with state=present')
        return_content = present(path, line, regexp, ins_aft, ins_bef, encoding, firstmatch, backrefs, file_type)
    else:
        if regexp is None and line is None:
            module.fail_json(msg='one of line or regexp is required with state=absent')
        return_content = absent(path, line, regexp, encoding, file_type)
    try:
        # change the return string to be loadable by json.loads()
        return_content = return_content.replace('/c\\', '/c\\\\')
        return_content = return_content.replace('/a\\', '/a\\\\')
        return_content = return_content.replace('/i\\', '/i\\\\')
        return_content = return_content.replace('$ a\\', '$ a\\\\')
        return_content = return_content.replace('1 i\\', '1 i\\\\')
        ret = json.loads(return_content)
        result['cmd'] = ret['cmd']
        result['changed'] = ret['changed']
        result['found'] = ret['found']
    except:
        result['message'] = "warning: dsed return content isn't in json format"
        result['return_content'] = return_content
    module.exit_json(**result)


if __name__ == '__main__':
    main()
