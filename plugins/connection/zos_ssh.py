# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright 2015 Abhijit Menon-Sen <ams@2ndQuadrant.com>
# Copyright 2017 Toshio Kuratomi <tkuratomi@ansible.com>
# Copyright (c) 2017 Ansible Project
# Copyright (c) IBM Corporation 2021
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
    name: zos_ssh
    short_description: connect via ssh client binary
    description:
        - This connection plugin will conditionally import the correct
          implementation of the z/OS ssh plugin dependent on the version of
          Ansible running on the controller.
        - The z/OS ssh plugin is used to connect to a z/OS managed node and
          properly transport EBCDIC encoded files so to execute in their native
          encoding.
        - To transfer a file from ASCII to EBCDIC such is the case for a REXX
          written module, the first line of the content be
          "/* rexx  __ANSIBLE_ENCODE_EBCDIC__  */".
    notes:
        - Many options have been removed from the original connection plugin
          M(ssh) to serve as a minimal portable implementaton. While it may be
          minimal, when the M(zos_ssh) plugin loads the appropriate connection
          plugin, all options from M(ssh) will be available.
    author:
        - ansible (@core)
        - Demetrios Dimatos (@ddimatos)
    version_added: historical
    options:
      ssh_executable:
          default: ssh
          description:
            - This defines the location of the ssh binary. It defaults to ``ssh`` which will use the first ssh binary available in $PATH.
            - This option is usually not required, it might be useful when access to system ssh is restricted,
              or when using ssh wrappers to connect to remote hosts.
            - For more on this connection plugin, refer to
              U(https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/plugins.html#z-os-connection-plugin)
          env: [{name: ANSIBLE_SSH_EXECUTABLE}]
          ini:
          - {key: ssh_executable, section: ssh_connection}
          #const: ANSIBLE_SSH_EXECUTABLE
          version_added: "2.2"
          vars:
              - name: ansible_ssh_executable
                version_added: '2.7'
      sftp_executable:
          default: sftp
          description:
            - This defines the location of the sftp binary. It defaults to ``sftp`` which will use the first binary available in $PATH.
          env: [{name: ANSIBLE_SFTP_EXECUTABLE}]
          ini:
          - {key: sftp_executable, section: ssh_connection}
          version_added: "2.6"
          vars:
              - name: ansible_sftp_executable
                version_added: '2.7'
      scp_executable:
          default: scp
          description:
            - This defines the location of the scp binary. It defaults to `scp` which will use the first binary available in $PATH.
          env: [{name: ANSIBLE_SCP_EXECUTABLE}]
          ini:
          - {key: scp_executable, section: ssh_connection}
          version_added: "2.6"
          vars:
              - name: ansible_scp_executable
                version_added: '2.7'
      ssh_transfer_method:
        default: smart
        description:
            - "Preferred method to use when transferring files over ssh"
            - Setting to 'smart' (default) will try them in order, until one succeeds or they all fail
            - Using 'piped' creates an ssh pipe with ``dd`` on either side to copy the data
        choices: ['sftp', 'scp', 'piped', 'smart']
        env: [{name: ANSIBLE_SSH_TRANSFER_METHOD}]
        ini:
            - {key: transfer_method, section: ssh_connection}
      use_tty:
        version_added: '2.5'
        default: 'yes'
        description: add -tt to ssh commands to force tty allocation
        env: [{name: ANSIBLE_SSH_USETTY}]
        ini:
        - {key: usetty, section: ssh_connection}
        type: bool
        vars:
          - name: ansible_ssh_use_tty
            version_added: '2.7'
'''

from ansible import cli

version_inf = cli.CLI.version_info(False)
version_major = version_inf['major']
version_minor = version_inf['minor']


if version_major == 2 and version_minor >= 11:
    try:
        # Load z/OS connection plugin for versions of Ansible greater or equal to 2.11
        from ansible_collections.ibm.ibm_zos_core.plugins.connection.zos_ssh_2_11 import Connection
    except ImportError:
        pass
else:
    try:
        # Load legacy z/OS connection plugin for versions of Ansible lesser than 2.11
        from ansible_collections.ibm.ibm_zos_core.plugins.connection.zos_ssh_legacy import Connection
    except ImportError:
        pass
