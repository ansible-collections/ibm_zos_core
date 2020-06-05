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
module: blockinfile
short_description: Insert/update/remove a text block surrounded by marker lines
version_added: '2.0'
description:
- This module will insert/update/remove a block of multi-line text surrounded by customizable marker lines.
author:
- Yaegashi Takeshi (@yaegashi)
options:
  path:
    description:
    - The file to modify.
    - Before Ansible 2.3 this option was only usable as I(dest), I(destfile) and I(name).
    type: path
    required: yes
    aliases: [ dest, destfile, name ]
  state:
    description:
    - Whether the block should be there or not.
    type: str
    choices: [ absent, present ]
    default: present
  marker:
    description:
    - The marker line template.
    - C({mark}) will be replaced with the values C(in marker_begin) (default="BEGIN") and C(marker_end) (default="END").
    - Using a custom marker without the C({mark}) variable may result in the block being repeatedly inserted on subsequent playbook runs.
    type: str
    default: '# {mark} ANSIBLE MANAGED BLOCK'
  block:
    description:
    - The text to insert inside the marker lines.
    - If it is missing or an empty string, the block will be removed as if C(state) were specified to C(absent).
    type: str
    default: ''
    aliases: [ content ]
  insertafter:
    description:
    - If specified, the block will be inserted after the last match of specified regular expression.
    - A special value is available; C(EOF) for inserting the block at the end of the file.
    - If specified regular expression has no matches, C(EOF) will be used instead.
    type: str
    choices: [ EOF, '*regex*' ]
    default: EOF
  insertbefore:
    description:
    - If specified, the block will be inserted before the last match of specified regular expression.
    - A special value is available; C(BOF) for inserting the block at the beginning of the file.
    - If specified regular expression has no matches, the block will be inserted at the end of the file.
    type: str
    choices: [ BOF, '*regex*' ]
  marker_begin:
    description:
    - This will be inserted at C({mark}) in the opening ansible block marker.
    type: str
    default: BEGIN
    version_added: '2.5'
  marker_end:
    required: false
    description:
    - This will be inserted at C({mark}) in the closing ansible block marker.
    type: str
    default: END
    version_added: '2.5'
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
      - If I(backup_file) is not provided, the default backup name will be used.
        The default backup name for a USS file or path will be the destination
        file or path name appended with a timestamp,
        e.g. /path/file_name.2020-04-23-08-32-29-bak.tar. If dest is an
        MVS data set, the default backup name will be a random name generated
        by IBM Z Open Automation Utilities.
    required: false
    type: str
  encoding:
    description:
      - Specifies the encoding of USS file or data set. zos_lineinfile
        requires to be provided with correct encoding to read the content
        of USS file or data set. If this parameter is not provided, this
        module assumes that USS file or data set is encoded in IBM-1047.
    required: false
    type: str
    default: IBM-1047
notes:
  - This module supports check mode.
  - When using 'with_*' loops be aware that if you do not set a unique mark the block will be overwritten on each iteration.
  - As of Ansible 2.3, the I(dest) option has been changed to I(path) as default, but I(dest) still works as well.
  - Option I(follow) has been removed in Ansible 2.5, because this module modifies the contents of the file so I(follow=no) doesn't make sense.
  - When more then one block should be handled in one file you must change the I(marker) per task.
extends_documentation_fragment:
- files
- validate
'''

EXAMPLES = r'''
# Before Ansible 2.3, option 'dest' or 'name' was used instead of 'path'
- name: Insert/Update "Match User" configuration block in /etc/ssh/sshd_config
  blockinfile:
    path: /etc/ssh/sshd_config
    block: |
      Match User ansible-agent
      PasswordAuthentication no

- name: Insert/Update eth0 configuration stanza in /etc/network/interfaces
        (it might be better to copy files into /etc/network/interfaces.d/)
  blockinfile:
    path: /etc/network/interfaces
    block: |
      iface eth0 inet static
          address 192.0.2.23
          netmask 255.255.255.0

- name: Insert/Update configuration using a local file and validate it
  blockinfile:
    block: "{{ lookup('file', './local/sshd_config') }}"
    dest: /etc/ssh/sshd_config
    backup: yes
    validate: /usr/sbin/sshd -T -f %s

- name: Insert/Update HTML surrounded by custom markers after <body> line
  blockinfile:
    path: /var/www/html/index.html
    marker: "<!-- {mark} ANSIBLE MANAGED BLOCK -->"
    insertafter: "<body>"
    block: |
      <h1>Welcome to {{ ansible_hostname }}</h1>
      <p>Last updated on {{ ansible_date_time.iso8601 }}</p>

- name: Remove HTML as well as surrounding markers
  blockinfile:
    path: /var/www/html/index.html
    marker: "<!-- {mark} ANSIBLE MANAGED BLOCK -->"
    block: ""

- name: Add mappings to /etc/hosts
  blockinfile:
    path: /etc/hosts
    block: |
      {{ item.ip }} {{ item.name }}
    marker: "# {mark} ANSIBLE MANAGED BLOCK {{ item.name }}"
  loop:
    - { name: host1, ip: 10.10.1.10 }
    - { name: host2, ip: 10.10.1.11 }
    - { name: host3, ip: 10.10.1.12 }
'''

import re
import os
import tempfile
import subprocess
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
    from zoautil_py import Datasets
except Exception:
    Datasets = MissingZOAUImport()

if PY3:
    from shlex import quote
else:
    from pipes import quote

def write_changes(module, contents, path):

    tmpfd, tmpfile = tempfile.mkstemp(dir=module.tmpdir)
    f = os.fdopen(tmpfd, 'wb')
    f.write(contents)
    f.close()

    validate = module.params.get('validate', None)
    valid = not validate
    if validate:
        if "%s" not in validate:
            module.fail_json(msg="validate must contain %%s: %s" % (validate))
        (rc, out, err) = module.run_command(validate % tmpfile)
        valid = rc == 0
        if rc != 0:
            module.fail_json(msg='failed to validate: '
                                 'rc:%s error:%s' % (rc, err))
    if valid:
        module.atomic_move(tmpfile, path, unsafe_writes=module.params['unsafe_writes'])


def check_file_attrs(module, changed, message, diff):

    file_args = module.load_file_common_arguments(module.params)
    if module.set_file_attributes_if_different(file_args, False, diff=diff):

        if changed:
            message += " and "
        changed = True
        message += "ownership, perms or SE linux context changed"

    return message, changed

def iconv(content, from_encoding, to_encoding):
    iconv_cmd = "iconv -f {0} -t {1}".format(quote(from_encoding), quote(to_encoding))
    p = subprocess.Popen(iconv_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    p.stdin.write(content)
    p.stdin.close()
    return p.stdout.read()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['dest', 'destfile', 'name']),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            marker=dict(type='str', default='# {mark} ANSIBLE MANAGED BLOCK'),
            block=dict(type='str', default='', aliases=['content']),
            insertafter=dict(type='str'),
            insertbefore=dict(type='str'),
            create=dict(type='bool', default=False),
            validate=dict(type='str'),
            marker_begin=dict(type='str', default='BEGIN'),
            marker_end=dict(type='str', default='END'),
            backup=dict(type='bool', default=False),
            backup_file=dict(type='str', required=False, default=None),
            encoding=dict(type=str, default="IBM-1047"),
        ),
        mutually_exclusive=[['insertbefore', 'insertafter']],
        add_file_common_args=True,
        supports_check_mode=True
    )

    params = module.params
    path = params['path']

    arg_defs = dict(
        path=dict(arg_type="data_set_or_path", aliases=['zosdest', 'dest', 'destfile', 'name'], required=True),
        state=dict(arg_type='str', default='present',choices=['absent', 'present']),
        marker=dict(arg_type='str', default='# {mark} ANSIBLE MANAGED BLOCK'),
        block=dict(arg_type='str', default='', aliases=['content']),
        insertafter=dict(arg_type="str", required=False),
        insertbefore=dict(arg_type="str", required=False),
        create=dict(arg_type='bool', required=False, default=False),
        validate=dict(arg_type='str', required=False),
        marker_begin=dict(arg_type='str', default='BEGIN'),
        marker_end=dict(arg_type='str', default='END'),
        encoding=dict(arg_type="str", default="IBM-1047", required=False),
        backup=dict(arg_type="bool", default=False, required=False),
        backup_file=dict(arg_type="data_set_or_path", required=False, default=None),
        mutually_exclusive=[["insertbefore","insertafter"]],
    )

    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    backup = parsed_args.get('backup')
    backup_file = None
    if parsed_args.get('backup_file') and backup:
        backup = parsed_args.get('backup_file')
    path = parsed_args.get('path')
    insertafter = parsed_args.get('insertafter')
    insertbefore = parsed_args.get('insertbefore')
    encoding = parsed_args.get('encoding')
    #block = to_bytes(parsed_args.get('block'))
    block = to_bytes(params['block'])
    marker = to_bytes(parsed_args.get('marker'))
    present = parsed_args.get('state') == 'present'

    # analysis the file type
    ds_utils = data_set.DataSetUtils(path)
    file_type = ds_utils.ds_type()
    if file_type == 'USS':
        file_type = 1
    else:
        file_type = 0
    if not encoding:
        encoding = "IBM-1047"

    if file_type:
        if os.path.isdir(path):
            module.fail_json(rc=256,
                         msg='Path %s is a directory !' % path)

        path_exists = os.path.exists(path)
        if not path_exists:
            if not module.boolean(params['create']):
                module.fail_json(rc=257,
                             msg='Path %s does not exist !' % path)
            destpath = os.path.dirname(path)
            if not os.path.exists(destpath) and not module.check_mode:
                try:
                    os.makedirs(destpath)
                except Exception as e:
                    module.fail_json(msg='Error creating %s Error code: %s Error description: %s' % (destpath, e[0], e[1]))
            original = None
            lines = []
        else:
            f = open(path, 'rb')
            original = f.read()
            f.close()
            if encoding != "ISO8859-1":
                original = iconv(original, encoding, "ISO8859-1")
            lines = original.splitlines()
    else:
        #original = to_bytes(Datasets.read_from(path, start=1))
        path = "//'" + path + "'"
        f = open(path, 'rb')
        original = f.read()
        f.close()
        if encoding != "ISO8859-1":
            original = iconv(original, encoding, "ISO8859-1")
        lines = []
        recLen = 80
        start = 0
        end = recLen
        while(end <= len(original)):
            lines.append(original[start:end])
            start = end
            end += recLen

    diff = {'before': '',
            'after': '',
            'before_header': '%s (content)' % path,
            'after_header': '%s (content)' % path}

    if module._diff and original:
        diff['before'] = original

    if not present and not path_exists:
        module.exit_json(changed=False, msg="File %s not present" % path)

    if insertbefore is None and insertafter is None:
        insertafter = 'EOF'

    if insertafter not in (None, 'EOF'):
        insertre = re.compile(to_bytes(insertafter, errors='surrogate_or_strict'))
    elif insertbefore not in (None, 'BOF'):
        insertre = re.compile(to_bytes(insertbefore, errors='surrogate_or_strict'))
    else:
        insertre = None

    marker0 = re.sub(b(r'{mark}'), b(params['marker_begin']), marker)
    marker1 = re.sub(b(r'{mark}'), b(params['marker_end']), marker)
    if present and block:
        # Escape sequences like '\n' need to be handled in Ansible 1.x
        if module.ansible_version.startswith('1.'):
            block = re.sub('', block, '')
        blocklines = [marker0] + block.splitlines() + [marker1]
    else:
        blocklines = []
    if not file_type:
        for i in range(len(blocklines)):
            blocklines[i] += b((' ')*(recLen - len(blocklines[i])))

    n0 = n1 = None
    for i, line in enumerate(lines):
        if line == marker0:
            n0 = i
        if line == marker1:
            n1 = i

    if None in (n0, n1):
        n0 = None
        if insertre is not None:
            for i, line in enumerate(lines):
                if insertre.search(line):
                    n0 = i
            if n0 is None:
                n0 = len(lines)
            elif insertafter is not None:
                n0 += 1
        elif insertbefore is not None:
            n0 = 0  # insertbefore=BOF
        else:
            n0 = len(lines)  # insertafter=EOF
    elif n0 < n1:
        lines[n0:n1 + 1] = []
    else:
        lines[n1:n0 + 1] = []
        n0 = n1

    lines[n0:n0] = blocklines

    if file_type:
        if lines:
            result = b('\n').join(lines)
            if original is None or original.endswith(b('\n')):
                result += b('\n')
        else:
            result = b''
    else:
        result = b('').join(lines)

    if module._diff:
        diff['after'] = result

    if original == result:
        msg = ''
        changed = False
    elif original is None:
        msg = 'File created'
        changed = True
    elif not blocklines:
        msg = 'Block removed'
        changed = True
    else:
        msg = 'Block inserted'
        changed = True

    if changed and not module.check_mode:
        if backup:
            if type(backup) == bool:
                backup = None
            try:
                if file_type:
                    backup_file = Backup.uss_file_backup(path, backup_name=backup, compress=False)
                else:
                    backup_file = Backup.mvs_file_backup(dsn=path, bk_dsn=backup)
            except Exception:
                module.fail_json(msg="creating backup has failed")
        if file_type:
            if encoding != "ISO8859-1":
                result = iconv(result, "ISO8859-1", encoding)
            # We should always follow symlinks so that we change the real file
            real_path = os.path.realpath(params['path'])
            write_changes(module, result, real_path)
        else:
            if encoding != "ISO8859-1":
                result = iconv(result, "ISO8859-1", encoding)
            f = open(path, 'wb')
            f.write(result)
            f.close()

    if module.check_mode and not path_exists:
        module.exit_json(changed=changed, msg=msg, diff=diff, backup_file=backup_file)

    attr_diff = {}
    if file_type:
        msg, changed = check_file_attrs(module, changed, msg, attr_diff)

    attr_diff['before_header'] = '%s (file attributes)' % path
    attr_diff['after_header'] = '%s (file attributes)' % path

    difflist = [diff, attr_diff]
    module.exit_json(changed=changed, msg=msg, diff=difflist, backup_file=backup_file)


if __name__ == '__main__':
    main()
