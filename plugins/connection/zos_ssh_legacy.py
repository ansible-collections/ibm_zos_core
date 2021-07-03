# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright 2015 Abhijit Menon-Sen <ams@2ndQuadrant.com>
# Copyright 2017 Toshio Kuratomi <tkuratomi@ansible.com>
# Copyright (c) 2017 Ansible Project
# Copyright (c) IBM Corporation 2019, 2020, 2021
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    connection: ssh
    short_description: connect via ssh client binary
    description:
        - This connection plugin allows ansible to communicate to the target machines via
        - Ansible does not expose a channel to allow communication between the user and t
          a password manually to decrypt an ssh key when using this connection plugin (wh
          use of ``ssh-agent`` is highly recommended.
    author: ansible (@core)
    version_added: historical
    options:
      host:
          description: Hostname/ip to connect to.
          default: inventory_hostname
          vars:
              - name: ansible_host
              - name: ansible_ssh_host
      host_key_checking:
          description: Determines if ssh should check host keys
          type: boolean
          ini:
              - section: defaults
                key: 'host_key_checking'
              - section: ssh_connection
                key: 'host_key_checking'
                version_added: '2.5'
          env:
              - name: ANSIBLE_HOST_KEY_CHECKING
              - name: ANSIBLE_SSH_HOST_KEY_CHECKING
                version_added: '2.5'
          vars:
              - name: ansible_host_key_checking
                version_added: '2.5'
              - name: ansible_ssh_host_key_checking
                version_added: '2.5'
      password:
          description: Authentication password for the C(remote_user). Can be supplied as
          vars:
              - name: ansible_password
              - name: ansible_ssh_pass
              - name: ansible_ssh_password
      ssh_args:
          description: Arguments to pass to all ssh cli tools
          default: '-C -o ControlMaster=auto -o ControlPersist=60s'
          ini:
              - section: 'ssh_connection'
                key: 'ssh_args'
          env:
              - name: ANSIBLE_SSH_ARGS
          vars:
              - name: ansible_ssh_args
                version_added: '2.7'
      ssh_common_args:
          description: Common extra args for all ssh CLI tools
          ini:
              - section: 'ssh_connection'
                key: 'ssh_common_args'
                version_added: '2.7'
          env:
              - name: ANSIBLE_SSH_COMMON_ARGS
                version_added: '2.7'
          vars:
              - name: ansible_ssh_common_args
      ssh_executable:
          default: ssh
          description:
            - This defines the location of the ssh binary. It defaults to ``ssh`` which w
            - This option is usually not required, it might be useful when access to syst
              or when using ssh wrappers to connect to remote hosts.
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
            - This defines the location of the sftp binary. It defaults to ``sftp`` which
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
            - This defines the location of the scp binary. It defaults to `scp` which wil
          env: [{name: ANSIBLE_SCP_EXECUTABLE}]
          ini:
          - {key: scp_executable, section: ssh_connection}
          version_added: "2.6"
          vars:
              - name: ansible_scp_executable
                version_added: '2.7'
      scp_extra_args:
          description: Extra exclusive to the ``scp`` CLI
          vars:
              - name: ansible_scp_extra_args
          env:
            - name: ANSIBLE_SCP_EXTRA_ARGS
              version_added: '2.7'
          ini:
            - key: scp_extra_args
              section: ssh_connection
              version_added: '2.7'
      sftp_extra_args:
          description: Extra exclusive to the ``sftp`` CLI
          vars:
              - name: ansible_sftp_extra_args
          env:
            - name: ANSIBLE_SFTP_EXTRA_ARGS
              version_added: '2.7'
          ini:
            - key: sftp_extra_args
              section: ssh_connection
              version_added: '2.7'
      ssh_extra_args:
          description: Extra exclusive to the 'ssh' CLI
          vars:
              - name: ansible_ssh_extra_args
          env:
            - name: ANSIBLE_SSH_EXTRA_ARGS
              version_added: '2.7'
          ini:
            - key: ssh_extra_args
              section: ssh_connection
              version_added: '2.7'
      retries:
          # constant: ANSIBLE_SSH_RETRIES
          description: Number of attempts to connect.
          default: 3
          type: integer
          env:
            - name: ANSIBLE_SSH_RETRIES
          ini:
            - section: connection
              key: retries
            - section: ssh_connection
              key: retries
          vars:
            - name: ansible_ssh_retries
              version_added: '2.7'
      port:
          description: Remote port to connect to.
          type: int
          default: 22
          ini:
            - section: defaults
              key: remote_port
          env:
            - name: ANSIBLE_REMOTE_PORT
          vars:
            - name: ansible_port
            - name: ansible_ssh_port
      remote_user:
          description:
              - User name with which to login to the remote server, normally set by the r
              - If no user is supplied, Ansible will let the ssh client binary choose the
          ini:
            - section: defaults
              key: remote_user
          env:
            - name: ANSIBLE_REMOTE_USER
          vars:
            - name: ansible_user
            - name: ansible_ssh_user
      pipelining:
          default: ANSIBLE_PIPELINING
          description:
            - Pipelining reduces the number of SSH operations required to execute a modul
              by executing many Ansible modules without actual file transfer.
            - This can result in a very significant performance improvement when enabled.
            - However this conflicts with privilege escalation (become).
              For example, when using sudo operations you must first disable 'requiretty'
              which is why this feature is disabled by default.
          env:
            - name: ANSIBLE_PIPELINING
            #- name: ANSIBLE_SSH_PIPELINING
          ini:
            - section: defaults
              key: pipelining
            #- section: ssh_connection
            #  key: pipelining
          type: boolean
          vars:
            - name: ansible_pipelining
            - name: ansible_ssh_pipelining
      private_key_file:
          description:
              - Path to private key file to use for authentication
          ini:
            - section: defaults
              key: private_key_file
          env:
            - name: ANSIBLE_PRIVATE_KEY_FILE
          vars:
            - name: ansible_private_key_file
            - name: ansible_ssh_private_key_file
      control_path:
        description:
          - This is the location to save ssh's ControlPath sockets, it uses ssh's variabl
          - Since 2.3, if null, ansible will generate a unique hash. Use `%(directory)s`
        env:
          - name: ANSIBLE_SSH_CONTROL_PATH
        ini:
          - key: control_path
            section: ssh_connection
        vars:
          - name: ansible_control_path
            version_added: '2.7'
      control_path_dir:
        default: ~/.ansible/cp
        description:
          - This sets the directory to use for ssh control path if the control path setti
          - Also, provides the `%(directory)s` variable for the control path setting.
        env:
          - name: ANSIBLE_SSH_CONTROL_PATH_DIR
        ini:
          - section: ssh_connection
            key: control_path_dir
        vars:
          - name: ansible_control_path_dir
            version_added: '2.7'
      sftp_batch_mode:
        default: 'yes'
        description: 'TODO: write it'
        env: [{name: ANSIBLE_SFTP_BATCH_MODE}]
        ini:
        - {key: sftp_batch_mode, section: ssh_connection}
        type: bool
        vars:
          - name: ansible_sftp_batch_mode
            version_added: '2.7'
      scp_if_ssh:
        default: smart
        description:
          - "Prefered method to use when transfering files over ssh"
          - When set to smart, Ansible will try them until one succeeds or they all fail
          - If set to True, it will force 'scp', if False it will use 'sftp'
        env: [{name: ANSIBLE_SCP_IF_SSH}]
        ini:
        - {key: scp_if_ssh, section: ssh_connection}
        vars:
          - name: ansible_scp_if_ssh
            version_added: '2.7'
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

import os

from ansible.errors import (
    AnsibleAuthenticationFailure,
    AnsibleConnectionFailure,
    AnsibleError,
    AnsibleFileNotFound,
)

from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.plugins.connection.ssh import Connection as connection
from ansible.utils.display import Display

display = Display()


class Connection(connection):
    ''' Supports Ansible 2.10 or earlier '''

    module_implementation_preferences = ('.rexx', '.py', '')
    display.vvv(u"Loaded connection plugin {0} ".format(os.path.basename(__file__)))

    def put_file(self, in_path, out_path):
        ''' transfer a file from local to remote '''

        super(Connection, self).put_file(in_path, out_path)

        display.vvv(u"PUT {0} TO {1}".format(in_path, out_path), host=self.host)
        if not os.path.exists(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound("file or module does not exist: {0}".format(to_native(in_path)))

        zos_transfer_method = self._zos_transport(in_path)
        file_transport_response = self._file_transport_command(in_path, out_path, 'put')

        # User's ssh_transfer_method was changed so we should restore it
        if zos_transfer_method is not None:
            self._play_context.ssh_transfer_method = zos_transfer_method
            display.vvv(u"SSH transfer method restored to {0}".format(zos_transfer_method), host=self.host)
        return file_transport_response

    def _zos_transport(self, path):
        """
        sets 'ssh_transfer_method' to 'scp' when file encoding tag
        __ANSIBLE_ENCODE_EBCDIC__ is read. SCP is used to ensure text is
        transferred in native EBCDIC encoding. If 'ssh_transfer_method' is
        changed, the original value is returned so that it can be reset with
        self.set_option() else None.
        """

        scp_transfer_method = "scp"
        user_ssh_transfer_method = self._play_context.ssh_transfer_method

        def _flag_in_file():
            try:
                with open(path) as f:
                    if "__ANSIBLE_ENCODE_EBCDIC__" in f.readline():
                        if user_ssh_transfer_method != scp_transfer_method:
                            self._play_context.ssh_transfer_method = scp_transfer_method
                            display.vvv(u"SSH transfer method updated from {0} to {1}.".format(user_ssh_transfer_method, scp_transfer_method), host=self.host)
                            # 'user_ssh_transfer_method' should never return as 'None' because the default is 'smart'
                            return user_ssh_transfer_method
                        else:
                            return None
            except (IOError, OSError):
                pass
            return None
        return _flag_in_file()
