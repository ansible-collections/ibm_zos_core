# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright 2015 Abhijit Menon-Sen <ams@2ndQuadrant.com>
# Copyright 2017 Toshio Kuratomi <tkuratomi@ansible.com>
# Copyright (c) 2017 Ansible Project
# Copyright (c) IBM Corporation 2021
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible import cli

version_inf = cli.CLI.version_info(False)
version_major = version_inf['major']
version_minor = version_inf['minor']


DOCUMENTATION = '''
    name: zos_ssh
    short_description: connect via ssh client binary
    description:
        - This connection plugin allows ansible to communicate to the target machines via normal ssh command line.
        - Ansible does not expose a channel to allow communication between the user and the ssh process to accept
          a password manually to decrypt an ssh key when using this connection plugin (which is the default). The
          use of ``ssh-agent`` is highly recommended.
    author:
        - ansible (@core)
        - Demetrios Dimatos (@ddimatos)
    version_added: historical
    notes:
        - Many options default to 'None' here but that only means we don't override the ssh tool's defaults and/or configuration.
          For example, if you specify the port in this plugin it will override any C(Port) entry in your C(.ssh/config).
'''

if version_major == 2 and version_minor >= 11:
    DOCUMENTATION = '''
        name: zos_ssh
        short_description: connect via ssh client binary
        description:
            - This connection plugin allows ansible to communicate to the target machines via normal ssh command line.
            - Ansible does not expose a channel to allow communication between the user and the ssh process to accept
              a password manually to decrypt an ssh key when using this connection plugin (which is the default). The
              use of ``ssh-agent`` is highly recommended.
        author:
            - ansible (@core)
            - Demetrios Dimatos (@ddimatos)
        extends_documentation_fragment:
            - connection_pipelining
        version_added: historical
        notes:
            - Many options default to 'None' here but that only means we don't override the ssh tool's defaults and/or configuration.
              For example, if you specify the port in this plugin it will override any C(Port) entry in your C(.ssh/config).
        options:
          host:
              description: Hostname/ip to connect to.
              vars:
                  - name: inventory_hostname
                  - name: ansible_host
                  - name: ansible_ssh_host
                  - name: delegated_vars['ansible_host']
                  - name: delegated_vars['ansible_ssh_host']
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
              description: Authentication password for the C(remote_user). Can be supplied as CLI option.
              vars:
                  - name: ansible_password
                  - name: ansible_ssh_pass
                  - name: ansible_ssh_password
          sshpass_prompt:
              description: Password prompt that sshpass should search for. Supported by sshpass 1.06 and up.
              default: ''
              ini:
                  - section: 'ssh_connection'
                    key: 'sshpass_prompt'
              env:
                  - name: ANSIBLE_SSHPASS_PROMPT
              vars:
                  - name: ansible_sshpass_prompt
              version_added: '2.10'
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
              cli:
                  - name: ssh_args
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
              cli:
                  - name: ssh_common_args
          ssh_executable:
              default: ssh
              description:
                - This defines the location of the ssh binary. It defaults to ``ssh`` which will use the first ssh binary available in $PATH.
                - This option is usually not required, it might be useful when access to system ssh is restricted,
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
              cli:
                - name: scp_extra_args
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
              cli:
                - name: sftp_extra_args
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
              cli:
                - name: ssh_extra_args
          retries:
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
                  - User name with which to login to the remote server, normally set by the remote_user keyword.
                  - If no user is supplied, Ansible will let the ssh client binary choose the user as it normally
              ini:
                - section: defaults
                  key: remote_user
              env:
                - name: ANSIBLE_REMOTE_USER
              vars:
                - name: ansible_user
                - name: ansible_ssh_user
              cli:
                - name: user
          pipelining:
              env:
                - name: ANSIBLE_PIPELINING
                - name: ANSIBLE_SSH_PIPELINING
              ini:
                - section: connection
                  key: pipelining
                - section: ssh_connection
                  key: pipelining
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
              cli:
                - name: private_key_file

          control_path:
            description:
              - This is the location to save ssh's ControlPath sockets, it uses ssh's variable substitution.
              - Since 2.3, if null (default), ansible will generate a unique hash. Use `%(directory)s` to indicate where to use the control dir path setting.
              - Before 2.3 it defaulted to `control_path=%(directory)s/ansible-ssh-%%h-%%p-%%r`.
              - Be aware that this setting is ignored if `-o ControlPath` is set in ssh args.
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
              - This sets the directory to use for ssh control path if the control path setting is null.
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
          scp_if_ssh:
            default: smart
            description:
              - "Preferred method to use when transfering files over ssh"
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
          timeout:
            default: 10
            description:
                - This is the default ammount of time we will wait while establishing an ssh connection
                - It also controls how long we can wait to access reading the connection once established (select on the socket)
            env:
                - name: ANSIBLE_TIMEOUT
                - name: ANSIBLE_SSH_TIMEOUT
                  version_added: '2.11'
            ini:
                - key: timeout
                  section: defaults
                - key: timeout
                  section: ssh_connection
                  version_added: '2.11'
            vars:
              - name: ansible_ssh_timeout
                version_added: '2.11'
            cli:
              - name: timeout
            type: integer
    '''
    try:
        # Load z/OS connection plugin for versions of Ansible greater or equal to 2.11
        from ansible_collections.ibm.ibm_zos_core.plugins.connection.zos_ssh_2_11 import Connection
    except ImportError:
        pass
else:
    DOCUMENTATION = '''
        connection: ssh
        short_description: connect via ssh client binary
        description:
            - This connection plugin allows ansible to communicate to the target machines via normal ssh command line.
            - Ansible does not expose a channel to allow communication between the user and the ssh process to accept
              a password manually to decrypt an ssh key when using this connection plugin (which is the default). The
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
              description: Authentication password for the C(remote_user). Can be supplied as CLI option.
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
                - This defines the location of the ssh binary. It defaults to ``ssh`` which will use the first ssh binary available in $PATH.
                - This option is usually not required, it might be useful when access to system ssh is restricted,
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
                  - User name with which to login to the remote server, normally set by the remote_user keyword.
                  - If no user is supplied, Ansible will let the ssh client binary choose the user as it normally
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
                - Pipelining reduces the number of SSH operations required to execute a module on the remote server,
                  by executing many Ansible modules without actual file transfer.
                - This can result in a very significant performance improvement when enabled.
                - However this conflicts with privilege escalation (become).
                  For example, when using sudo operations you must first disable 'requiretty' in the sudoers file for the target hosts,
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
              - This is the location to save ssh's ControlPath sockets, it uses ssh's variable substitution.
              - Since 2.3, if null, ansible will generate a unique hash. Use `%(directory)s` to indicate where to use the control dir path setting.
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
              - This sets the directory to use for ssh control path if the control path setting is null.
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
    try:
        # Load legacy z/OS connection plugin for versions of Ansible lesser than 2.11
        from ansible_collections.ibm.ibm_zos_core.plugins.connection.zos_ssh_legacy import Connection
    except ImportError:
        pass
