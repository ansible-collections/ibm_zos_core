# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The users.py file contains various utility functions that
will support functional test cases. For example, request a randomly
generated user with specific limitations.

Usage:
def test_copy_dest_lock_test_apf_authorization_3(ansible_zos_module):
    # Request a user who has no authority to execute zoau opercmd
    hosts = ansible_zos_module
    managed_user, user, passwd = None, None, None
    managed_user_type = ManagedUserType.ZOAU_LIMITED_ACCESS_OPERCMD

    # Instance of the ManagedUser initialized with a user who has authority to create users and the remote host.
    remote_host = hosts["options"]["inventory"].replace(",", "")
    remote_user = hosts["options"]["user"]
    try:
        # Check for a managed user type request
        if managed_user_type:
            managed_user = ManagedUser(remote_user, remote_host)
            user, passwd = managed_user.create_managed_user(managed_user_type)
            print(f"New managed user created = {user}")
            print(f"New managed password created = {passwd}")

        # Update fixture with the new user
        hosts["options"]["user"] = user

        who = hosts.all.shell(cmd="whoami")
        for person in who.contacted.values():
            print("Who am I = " + str(person))

    finally:
        # Delete the managed user on the remote host to avoid proliferation of users.
        managed_user.delete_managed_user()
"""
from collections import OrderedDict
from io import StringIO
from enum import Enum
import random
import string
import subprocess
import sys
import os
import glob
import re
import subprocess

class ManagedUserType (Enum):
    """
    Represents the z/OS users available for functional testing.

    Managed user types:
        ZOAU_LIMITED_ACCESS_OPERCMD
        ZOS_BEGIN_WITH_AT_SIGN
        ZOS_BEGIN_WITH_POUND
        ZOS_RANDOM_SYMBOLS
        ZOS_LIMITED_HLQ
        ZOS_LIMITED_TMP_HLQ
    """

    ZOAU_LIMITED_ACCESS_OPERCMD=("zoau_limited_access_opercmd")
    """
    A z/OS managed user with restricted access to ZOAU
    SAF Profile 'MVS.MCSOPER.ZOAU' and SAF Class OPERCMDS
    with universal access authority set to UACC(NONE). With
    UACC as NONE, this user will be refused access to the
    ZOAU opercmd utility.
    """

    ZOS_BEGIN_WITH_AT_SIGN=("zos_begin_with_at_sign")
    """
    A z/OS managed user ID that begins with the '@' symbol.
    User retains the universal access of the original user (model user).
    """

    ZOS_BEGIN_WITH_POUND=("zos_begin_with_pound")
    """
    A z/OS managed user ID that begins with the '#' symbol.
    User retains the universal access of the original user (model user).
    """

    ZOS_RANDOM_SYMBOLS=("zos_random_symbols")
    """
    A z/OS managed user ID that is randomly assigned symbols, '#', '$', '@'.
    User retains the universal access of the original user (model user).
    """
    # TODO: Implement this, use the recommended HLQ
    ZOS_LIMITED_HLQ=("zos_limited_hlq")
    """
    A z/OS managed user with restricted access to High Level
    Qualifiers (HLQ): (RESTRICT, NOPERMIT, ....).
    """

    # TODO: Implement this, use the recommended tmp HLQ
    ZOS_LIMITED_TMP_HLQ=("zos_limited_tmp_hlq")
    """
    A z/OS managed user with restricted access to temporary
    High Level Qualifiers (HLQ): (TSTRICT, TNOPERM, ....).
    """

    def __str__(self) -> str:
        """
        Return the enum name as upper case.
        """
        return self.name.upper()

    def string(self) -> str:
        """
        Returns the enum value as uppercase.
        """
        return self.value.upper()

class ManagedUser:
    """
    This class provides methods to augment the pytest-ansible fixture with the
    requested managed user and on completion restore the fixture.
    """
    _model_user = None
    _user = None
    _user_group = None
    _ansible_zos_module = None
    _host = None

    def __init__(self, model_user, host):
        self._model_user = model_user
        self._host = host

    def connect(self, host, user, command):
        ssh_command = ["ssh", f"{user}@{host}", command]
        result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Don't do anything with stderr, there is code that will check RCs to determine if there is an error
        # std_err = result.stderr

        return [line.strip() for line in result.stdout.split('\n')]

    def delete_managed_user(self):
        escaped_user = re.escape(self._user)
        command = StringIO()
        command.write(f"echo Deleting USER '{self._user}';")
        command.write(f"tsocmd DELUSER {escaped_user};")
        command.write(f"echo DELUSER '{escaped_user}' RC=$?;")
        command.write(f"tsocmd DELGROUP {self._user_group};")
        command.write(f"echo DELGROUP '{self._user_group}' RC=$?;")

        # Access additional module user attributes for use in a new user.
        cmd=f"{command.getvalue()}"
        results_stdout_lines = self.connect(self._host, self._model_user,cmd)

        deluser_rc = [v for v in results_stdout_lines if f"DELUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not deluser_rc or int(deluser_rc[0]) > 0:
            raise Exception(f"Unable to delete user {escaped_user}, please review the command output {results_stdout_lines}.")

        delgroup_rc = [v for v in results_stdout_lines if f"DELGROUP {self._user_group} RC=" in v][0].split('=')[1].strip() or None
        if not delgroup_rc or int(delgroup_rc[0]) > 0:
            raise Exception(f"Unable to delete user {escaped_user}, please review the command output {results_stdout_lines}.")


    def __get_random_passwd(self) -> str:
        letters = string.ascii_uppercase
        start = ''.join(random.choice(letters) for i in range(3))
        middle = ''.join(str(random.randint(1,9)))
        finish = ''.join(random.choice(letters) for i in range(4))
        return f"{start}{middle}{finish}"

    def __get_random_user(self, managed_user: ManagedUserType = None) -> str:
        """A-Z, 0-9, #, $, or @."""
        letters = string.ascii_uppercase
        if managed_user is not None:
            if managed_user.name == ManagedUserType.ZOS_BEGIN_WITH_AT_SIGN.name:
                return "@" + ''.join(random.choice(letters) for i in range(7))
            elif managed_user.name == ManagedUserType.ZOS_BEGIN_WITH_POUND.name:
                return "#" + ''.join(random.choice(letters) for i in range(7))
            elif managed_user.name == ManagedUserType.ZOS_RANDOM_SYMBOLS.name:
                letters = string.ascii_uppercase
                numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                symbols = ['#', '$', '@',]

                prefix = random.sample(letters,1)
                alphas = random.sample(letters,2)
                num = random.sample(numbers,2)
                sym = random.sample(symbols,3)
                alphas.extend(num)
                alphas.extend(sym)
                random.shuffle(alphas)
                return str(prefix[0]) + ''.join([str(entry) for entry in alphas])

        # All other cases can use any formatted user name, so random 8 letters is fine.
        return ''.join(random.choice(letters) for i in range(8))

    def __read_files_in_directory(self, directory: str = "~/.ssh", pattern: str = "*.pub") -> list:
        """Reads files in a directory that match the pattern and return file contents as a list entry."""

        file_contents_as_list = []

        # Expand the tilde to the home directory
        expanded_directory = os.path.expanduser(directory)

        for filename in glob.glob(os.path.join(expanded_directory, pattern)):
            with open(filename, 'r') as f:
                file_contents_as_list.append(f.read().rstrip('\n'))
        return file_contents_as_list

    def __copy_ssh_key(user, passwd, host, key_path):
        """
        Copy SSH key to a remote host using subprocess.
        Note:
            This requires the host have sshpass installed.
        See:
            Method __read_files_in_directory instead to copy the public keys.
        """

        command = ["sshpass", "-p", f"{passwd}", "ssh-copy-id", "-o", "StrictHostKeyChecking=no", "-i", f"{key_path}", f"{user}@{host}"] #, "&>/dev/null"]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

        if result.returncode != 0:
            raise Exception("Unable to copy public keys to remote host, check that sshpass is installed.")

    def create_managed_user(self, managed_user: ManagedUserType) -> str:
        # Create random user based on ManagedUserType requirements
        self._user = self.__get_random_user(managed_user)

        # Generate the password to establish a password-less connection and use with RACF.
        passwd = self.__get_random_passwd()

        # Access module user's TSO attributes for reuse
        cmd=f"tsocmd LISTUSER {self._model_user} TSO NORACF"
        model_listuser_tso_attributes = self.connect(self._host, self._model_user,cmd)

        # Match the tso list results and place in variables (not all are used)
        model_tso_acctnum = [v for v in model_listuser_tso_attributes if "ACCTNUM" in v][0].split('=')[1].strip() or None
        if not model_tso_acctnum:
            raise Exception(f"Unable to determine the TSO Account number required for adding TSO {self._user}.")

        model_tso_proc = [v for v in model_listuser_tso_attributes if "PROC" in v][0].split('=')[1].strip() or None
        if not model_tso_proc:
            raise Exception(f"Unable to determine the TSO Proc required for adding TSO {self._user}.")

        # TODO: These are currently not used when creating the user, consider minimally adding SIZE and MAXXSIZE to dynamic users
        # model_tso_size = [v for v in model_listuser_tso_attributes if "SIZE" in v][0].split('=')[1].strip() or None
        # model_tso_maxsize = [v for v in model_listuser_tso_attributes if "MAXSIZE" in v][0].split('=')[1].strip() or None
        # model_tso_unit = [v for v in model_listuser_tso_attributes if "UNIT" in v][0].split('=')[1].strip() or ""
        # model_tso_userdata = [v for v in model_listuser_tso_attributes if "USERDATA" in v][0].split('=')[1].strip() or ""
        # model_tso_command = [v for v in model_listuser_tso_attributes if "COMMAND" in v][0].split('=')[1].strip() or ""

        # Access additional module user attributes for use in a new user.
        cmd=f"tsocmd LISTUSER {self._model_user}"
        model_listuser_attributes = self.connect(self._host, self._model_user,cmd)

        # Match the list user results and place in variables (not all are used)
        model_owner = [v for v in model_listuser_attributes if "OWNER" in v][0].split('OWNER=')[1].split()[0].strip() or ""

        # Collect the various public keys for use with the z/OS managed node, some accept only RSA and others ED25519
        public_keys = self.__read_files_in_directory("~/.ssh/", "*.pub")

        # The command consisting of shell and tso operations to create a user.
        add_user_cmd = StringIO()

        # (1) Create group ANSIGRP for general identification of users and auto assign the UID
        #     Success of the command yields 'Group ANSIGRP was assigned an OMVS GID value of...'
        #     Failure of the command yields 'INVALID GROUP, ANSIGRP' with usually a RC 8 if the group exists.
        self._user_group = self.__get_random_user()

        add_user_cmd.write(f"tsocmd 'ADDGROUP {self._user_group} OMVS(AUTOGID)';")
        add_user_cmd.write(f"echo Create {self._user_group} RC=$?;")

        # (2) Add a user owned by the model_owner. Expect an error when a new TSO userid is defined since the ID can't
        #     receive deferred messages until the id is defined in SYS1.BRODCAST, thus the SEND message fails.
        #       BROADCAST DATA SET NOT USABLE+
        #       I/O SYNAD ERROR
        escaped_user = re.escape(self._user)
        add_user_cmd.write(f"Creating USER '{escaped_user}' with PASSWORD {passwd} for remote host {self._host};")
        add_user_cmd.write(f"tsocmd ADDUSER {escaped_user} DFLTGRP\\({self._user_group}\\) OWNER\\({model_owner}\\) NOPASSWORD TSO\\(ACCTNUM\\({model_tso_acctnum}\\) PROC\\({model_tso_proc}\\)\\) OMVS\\(HOME\\(/u/{escaped_user}\\) PROGRAM\\('/bin/sh'\\) AUTOUID;")
        add_user_cmd.write(f"echo ADDUSER '{escaped_user}' RC=$?;")
        add_user_cmd.write(f"mkdir -p /u/{escaped_user}/.ssh;")
        add_user_cmd.write(f"echo mkdir '{escaped_user}' RC=$?;")
        add_user_cmd.write(f"umask 0022;")
        add_user_cmd.write(f"touch /u/{escaped_user}/.ssh/authorized_keys;")
        add_user_cmd.write(f"echo touch authorized_keys RC=$?;")
        add_user_cmd.write(f"chown -R {escaped_user} /u/{escaped_user};")
        add_user_cmd.write(f"echo chown '{escaped_user}' RC=$?;")
        for pub_key in public_keys:
            add_user_cmd.write(f"echo {pub_key} >> /u/{escaped_user}/.ssh/authorized_keys;")
            add_user_cmd.write(f"echo PUB_KEY RC=$?;")
        add_user_cmd.write(f"tsocmd ALTUSER {escaped_user} PASSWORD\\({passwd}\\) NOEXPIRED;")
        add_user_cmd.write(f"echo ALTUSER '{escaped_user}' RC=$?;")

        cmd=f"{add_user_cmd.getvalue()}"
        add_user_attributes = self.connect(self._host, self._model_user,cmd)

        # Because this is a tsocmd run through shell, any user with a $ will be expanded and thus truncated, you can't change
        # that behavior since its happening on the managed node, solution is to match a shorter pattern without the user.
        is_assigned_omvs_uid = True if [v for v in add_user_attributes if f"was assigned an OMVS UID value" in v] else False
        if not is_assigned_omvs_uid:
            raise Exception(f"Unable to create OMVS UID, please review the command output {add_user_attributes}.")

        create_group_rc = [v for v in add_user_attributes if f"Create {self._user_group} RC=" in v][0].split('=')[1].strip() or None
        if not create_group_rc or int(create_group_rc[0]) > 8:
            raise Exception(f"Unable to create user group {self._user_group}, please review the command output {add_user_attributes}.")

        add_user_rc = [v for v in add_user_attributes if f"ADDUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not add_user_rc or int(add_user_rc[0]) > 0:
            raise Exception(f"Unable to ADDUSER {escaped_user}, please review the command output {add_user_attributes}.")

        mkdir_rc = [v for v in add_user_attributes if f"mkdir {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not mkdir_rc or int(mkdir_rc[0]) > 0:
            raise Exception(f"Unable to make home directories for {escaped_user}, please review the command output {add_user_attributes}.")

        authorized_keys_rc = [v for v in add_user_attributes if f"touch authorized_keys RC=" in v][0].split('=')[1].strip() or None
        if not authorized_keys_rc or int(authorized_keys_rc[0]) > 0:
            raise Exception(f"Unable to make authorized_keys file for {escaped_user}, please review the command output {add_user_attributes}.")

        chown_rc = [v for v in add_user_attributes if f"chown {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not chown_rc or int(chown_rc[0]) > 0:
            raise Exception(f"Unable to change ownership of home directory for {escaped_user}, please review the command output {add_user_attributes}.")

        altuser_rc = [v for v in add_user_attributes if f"ALTUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not altuser_rc or int(altuser_rc[0]) > 0:
            raise Exception(f"Unable to update password for {escaped_user}, please review the command output {add_user_attributes}.")

        # Update the user according to the ManagedUserType type by invoking the mapped function
        self.operations[managed_user.name](self, self._user)

        return (self._user, passwd)


    def create_user_zoau_limited_access_opercmd(self, user: str) -> None:
        saf_profile="MVS.MCSOPER.ZOAU"
        saf_class="OPERCMDS"
        command = StringIO()

        command.write(f"Redefining USER '{user}';")
        command.write(f"tsocmd RDEFINE {saf_class} {saf_profile} UACC\\(NONE\\) AUDIT\\(ALL\\);")
        command.write(f"echo RDEFINE RC=$?;")
        command.write(f"tsocmd PERMIT {saf_profile} CLASS\\({saf_class}\\) ID\\({user}\\) ACCESS\\(NONE\\);")
        command.write(f"echo PERMIT RC=$?;")
        command.write(f"tsocmd SETROPTS RACLIST\\({saf_class}\\) REFRESH;")
        command.write(f"echo SETROPTS RC=$?;")

        cmd=f"{command.getvalue()}"
        results_stdout_lines = self.connect(self._host, self._model_user,cmd)

        # Evaluate the results
        rdefine_rc = [v for v in results_stdout_lines if f"RDEFINE RC=" in v][0].split('=')[1].strip() or None
        if not rdefine_rc or int(rdefine_rc[0]) > 4:
            raise Exception(f"Unable to rdefine {saf_class} {saf_profile}, please review the command output {results_stdout_lines}.")
        permit_rc = [v for v in results_stdout_lines if f"PERMIT RC=" in v][0].split('=')[1].strip() or None
        if not permit_rc or int(permit_rc[0]) > 4:
            raise Exception(f"Unable to permit {saf_profile} class {saf_class} for ID {user}, please review the command output {results_stdout_lines}.")
        setropts_rc = [v for v in results_stdout_lines if f"SETROPTS RC=" in v][0].split('=')[1].strip() or None
        if not setropts_rc or int(setropts_rc[0]) > 4:
            raise Exception(f"Unable to setropts raclist {saf_class} refresh, please review the command output {results_stdout_lines}.")

    def create_user_zos_limited_hlq(self, user) -> None:
        print("Needs to be implemented")

    def create_user_zos_limited_tmp_hlq(self, user) -> None:
        print("Needs to be implemented")

    def noop(self, *arg) -> None:
        """
        Method intentionally takes any number of args and does nothing.
        It is meant to be a NOOP function to be used as a stub.
        """
        pass

    operations = {
        ManagedUserType.ZOAU_LIMITED_ACCESS_OPERCMD.name: create_user_zoau_limited_access_opercmd,
        ManagedUserType.ZOS_LIMITED_HLQ.name: create_user_zos_limited_hlq,
        ManagedUserType.ZOS_LIMITED_TMP_HLQ.name: create_user_zos_limited_tmp_hlq,
        ManagedUserType.ZOS_BEGIN_WITH_AT_SIGN.name: noop,
        ManagedUserType.ZOS_BEGIN_WITH_POUND.name: noop,
        ManagedUserType.ZOS_RANDOM_SYMBOLS.name: noop
    }
