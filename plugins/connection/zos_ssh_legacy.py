# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright 2015 Abhijit Menon-Sen <ams@2ndQuadrant.com>
# Copyright 2017 Toshio Kuratomi <tkuratomi@ansible.com>
# Copyright (c) 2017 Ansible Project
# Copyright (c) IBM Corporation 2019, 2020, 2021
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

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
                            display.vvv(u"SSH transfer method updated from {0} to {1}.".format(user_ssh_transfer_method,scp_transfer_method), host=self.host)
                            # 'user_ssh_transfer_method' should never return as 'None' because the default is 'smart'
                            return user_ssh_transfer_method
                        else:
                            return None
            except (IOError, OSError):
                pass
            return None
        return _flag_in_file()
