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

# ####################################################################
# The users.py file contains various utility functions that
# will support functional test cases. For example, request a randomly
# generated user with specific limitations.
# ####################################################################

from collections import OrderedDict
from io import StringIO
from enum import Enum
import random
import string
import subprocess
import os
import glob
import re
import subprocess
from typing import List, Tuple

class ManagedUserType (Enum):
    """
    Represents the z/OS users available for functional testing.

    Managed user types
    ------------------
    - ZOAU_LIMITED_ACCESS_OPERCMD
    - ZOS_BEGIN_WITH_AT_SIGN
    - ZOS_BEGIN_WITH_POUND
    - ZOS_RANDOM_SYMBOLS
    - ZOS_LIMITED_HLQ
    - ZOS_LIMITED_TMP_HLQ
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
        Return the ManagedUserType name as upper case.
        """
        return self.name.upper()

    def string(self) -> str:
        """
        Returns the ManagedUserType value as uppercase.
        """
        return self.value.upper()

class ManagedUser:
    """
    This class provides methods in which can provide a user and password for a requested
    ManagedUserType.

    Usage
    -----
    The pytest fixture (ansible_zos_module) is a generator object done so by 'yield'ing;
    where a yield essentially pauses (streaming) a function and the state and control is
    goes to the function that called it. Thus the fixture can't be passed to this API to
    be updated with the new user or use the fixture to perform managed node inquiries,
    thus SSH is used for those managed node commands.

    Another important not is when using this API, you can't parametrize test cases, because
    once the pytest fixture (ansible_zos_module) is updated with a new user and performs a
    remote operation on a managed node, the fixture's user can not be changed because control
    is passed back and all attempts to change the user for reuse will fail, unless your goal
    is to use the same managedUserType in the parametrization this is not recommended.

    Example
    -------
    from ibm_zos_core.tests.helpers.users import ManagedUserType

    def test_demo_how_to_use_managed_user(ansible_zos_module):
        # Request a user who has no authority to execute zoau opercmd
        hosts = ansible_zos_module
        managed_user, user, passwd = None, None, None

        # Managed user type requested, requesting a z/OS user with no opercmd access
        managed_user_type = ManagedUserType.ZOAU_LIMITED_ACCESS_OPERCMD

        try:

            # Instance of the ManagedUser initialized with a user who has authority to create users and the remote host.
            remote_host = hosts["options"]["inventory"].replace(",", "")
            remote_user = hosts["options"]["user"]

            # Initialize the Managed user API
            managed_user = ManagedUser(remote_user, remote_host)
            # Pass the managed user type needed, there are several types.
            user, passwd = managed_user.create_managed_user(managed_user_type)
            # Print the results.
            print(f"\nNew managed user created = {user}")
            print(f"New managed password created = {passwd}")

            # Update the pytest fixture (hosts) with the newly created managed user, important step.
            hosts["options"]["user"] = user

            # Perform operations as usual.
            who = hosts.all.shell(cmd="whoami")
            for person in who.contacted.values():
                print(f"Who am I = {person.get("stdout")}")
        finally:
            # Delete the managed user on the remote host to avoid proliferation of users.
            managed_user.delete_managed_user()

    Example Output
    --------------
        New managed user created = MVKPJKNV
        New managed password created = JQT9GAZL
        Who am I = MVKPJKNV
    """
    _model_user = None
    _managed_racf_user = None
    _managed_user_group = None
    _remote_host = None

    def __init__(self, model_user: str, remote_host: str) -> None:
        """
        Initialize class with necessary parameters.

        Parameters
        ----------
        model_user (str):
            The user that will connect to the managed node and execute RACF commands
            and serve as a model for other users attributes.
            This user should have enough authority to perform RACF operations.
        remote_host (str):
            The z/OS managed node (host) to connect to to create the managed user.
        """
        self._model_user = model_user
        self._remote_host = remote_host

    def _connect(self, remote_host:str , model_user: str, command: str) -> List[str]:
        """
        Connect to the remote managed node and execute requested command.

        Parameters
        ----------
        remote_host (str)
            The z/OS managed node (host) to connect to to create the managed user.
        model_user (str)
            The user that will connect to the managed node and execute RACF commands
            and serve as a model for other users attributes.
            This user should have enough authority to perform RACF operations.
        command (str)
            Command to run on the managed node.

        Returns
        -------
        List[str]
            Command result as a list of strings.
        """
        ssh_command = ["ssh", f"{model_user}@{remote_host}", command]
        result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # RC 20 command failure - let this fall through for now, will be caught by command processors
        # RC 255 failed connection
        if result.returncode == 255:
            raise Exception(f"Unable to connect remote user [{model_user}] to remote host [{remote_host}], RC [{result.returncode}], stdout [{result.stdout}], stderr [{result.stderr}].")

        return [line.strip() for line in result.stdout.split('\n')]


    def delete_managed_user(self) -> None:
        """
        Delete managed user from z/OS managed node. Performs clean up of the remote
        system removing the RACF user, RACF Group, TSO ID and home directory and its
        contents.

        Raises
        ------
        Exception
            If any of the remote commands return codes are out of range an exception
            and the stdout and stderr is returned.
        """
        escaped_user = re.escape(self._managed_racf_user)
        command = StringIO()
        command.write(f"echo Deleting USER '{self._managed_racf_user}';")
        command.write(f"tsocmd DELUSER {escaped_user};")
        command.write(f"echo DELUSER '{escaped_user}' RC=$?;")
        command.write(f"tsocmd DELGROUP {self._managed_user_group};")
        command.write(f"echo DELGROUP '{self._managed_user_group}' RC=$?;")

        # Access additional module user attributes for use in a new user.
        cmd=f"{command.getvalue()}"
        results_stdout_lines = self._connect(self._remote_host, self._model_user,cmd)

        deluser_rc = [v for v in results_stdout_lines if f"DELUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not deluser_rc or int(deluser_rc[0]) > 0:
            raise Exception(f"Unable to delete user {escaped_user}, please review the command output {results_stdout_lines}.")

        delgroup_rc = [v for v in results_stdout_lines if f"DELGROUP {self._managed_user_group} RC=" in v][0].split('=')[1].strip() or None
        if not delgroup_rc or int(delgroup_rc[0]) > 0:
            raise Exception(f"Unable to delete user {escaped_user}, please review the command output {results_stdout_lines}.")


    def _get_random_passwd(self) -> str:
        """
        Generate a random password of length 8 adhering a supported common password
        pattern.

        Returns
        -------
        str
            Password string with pattern [CCCNCCCC].
            - (C) Random characters A - Z
            - (N) Random integers 1 - 9
        """
        letters = string.ascii_uppercase
        start = ''.join(random.choice(letters) for i in range(3))
        middle = ''.join(str(random.randint(1,9)))
        end = ''.join(random.choice(letters) for i in range(4))
        return f"{start}{middle}{end}"

    def _get_random_user(self, managed_user: ManagedUserType = None) -> str:
        """
        Generate a random user of length 8 adhering the ManagedUserType
        requested.

        Parameters
        ----------
        managed_user (ManagedUserType)
            The requested managed user type that correlates to how the user name will be created.
            Default is a user id consistent with random A - Z.

        See Also
        --------
            :py:class:`ManagedUserType`

        Returns
        -------
        str
            A user id suitable for RACF and based on the ManagedUserType.
            A user id can contain any of the supported symbols A-Z, 0-9, #, $, or @.
        """
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

    def _read_files_in_directory(self, directory: str = "~/.ssh", pattern: str = "*.pub") -> List[str]:
        """
        Reads files in a directory that match the pattern and return file names
        as a list of strings, each list index is a file name.

        Parameters
        ----------
        directory (str):
            The directory to search for files matching a pattern. Default, '~/.ssh'.
        pattern (str):
            The pattern to match file names. Default, '*.pub'.

        Returns
        -------
        List[str]
            A list of file names, each list index is a file name matching the pattern.
        """
        file_contents_as_list = []

        # Expand the tilde to the home directory
        expanded_directory = os.path.expanduser(directory)

        for filename in glob.glob(os.path.join(expanded_directory, pattern)):
            with open(filename, 'r') as f:
                file_contents_as_list.append(f.read().rstrip('\n'))
        return file_contents_as_list


    def _copy_ssh_key(model_user: str, passwd: str, remote_host: str, key_path: str):
        """
        Copy SSH key to a remote host using subprocess.

        Note
        ----
        This requires that the host have 'sshpass' installed.

        Parameters
        ----------
        remote_host (str)
            The z/OS managed node (host) to connect to to create the managed user.
        model_user (str)
            The user that will connect to the managed node and execute RACF commands
            and serve as a model for other users attributes. This user should have
            enough authority to perform RACF operations.
        command (str)
            Command to run on the managed node.

        Returns
        -------
        List[str]
            A list of file names, each list index is a file name matching the pattern.

        See Also
        --------
        :py:func:`_read_files_in_directory` to copy the public keys.
        """
        command = ["sshpass", "-p", f"{passwd}", "ssh-copy-id", "-o", "StrictHostKeyChecking=no", "-i", f"{key_path}", f"{model_user}@{remote_host}"] #, "&>/dev/null"]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

        if result.returncode != 0:
            raise Exception("Unable to copy public keys to remote host, check that sshpass is installed.")


    def create_managed_user(self, managed_user: ManagedUserType) -> Tuple[str, str]:
        """
        Generate a managed user for the remote node according to the ManagedUseeType selected.

        Parameters
        ----------
        managed_user (ManagedUserType)
            The requested managed user type that correlates to how the user name will be created.
            Default is a user id consistent with random A - Z.

        See Also
        --------
            :py:class:`ManagedUserType`

        Returns
        -------
        Tuple[str, str]
            A managed users ID and password as a tuple. eg (user, passwd)

        Raises
        ------
        Exception
            If any of the remote commands return codes are out of range an exception
            and the stdout and stderr is returned.
        """
        # Create random user based on ManagedUserType requirements
        self._managed_racf_user = self._get_random_user(managed_user)

        # Generate the password to establish a password-less connection and use with RACF.
        passwd = self._get_random_passwd()

        try:
            # Access module user's TSO attributes for reuse
            cmd=f"tsocmd LISTUSER {self._model_user} TSO NORACF"
            model_listuser_tso_attributes = self._connect(self._remote_host, self._model_user,cmd)

            # Match the tso list results and place in variables (not all are used)
            model_tso_acctnum = [v for v in model_listuser_tso_attributes if "ACCTNUM" in v][0].split('=')[1].strip() or None
            if not model_tso_acctnum:
                err_details = "TSO account number"
                err_msg = f"Unable access the model user [{self._managed_racf_user}] {err_details}, this is required to create user [{self._managed_racf_user}]."
                raise Exception(err_msg)

            model_tso_proc = [v for v in model_listuser_tso_attributes if "PROC" in v][0].split('=')[1].strip() or None
            if not model_tso_proc:
                err_details = "TSO Proc"
                err_msg = f"Unable access the model user [{self._managed_racf_user}] {err_details}, this is required to create user [{self._managed_racf_user}]."
                raise Exception(err_msg)
        except IndexError as err:
            err_msg = f"Unable access the model user [{self._managed_racf_user}] results, this is required to create user [{self._managed_racf_user}]."
            raise Exception(f"{err_msg}, exception [{err}].")
        except Exception as err:
            raise Exception(f"Unable to LISTUSER TSO NORACF for [{self._model_user}], exception [{err}]")

        # TODO: These are currently not used when creating the user, consider minimally adding SIZE and MAXXSIZE to dynamic users
        # model_tso_size = [v for v in model_listuser_tso_attributes if "SIZE" in v][0].split('=')[1].strip() or None
        # model_tso_maxsize = [v for v in model_listuser_tso_attributes if "MAXSIZE" in v][0].split('=')[1].strip() or None
        # model_tso_unit = [v for v in model_listuser_tso_attributes if "UNIT" in v][0].split('=')[1].strip() or ""
        # model_tso_userdata = [v for v in model_listuser_tso_attributes if "USERDATA" in v][0].split('=')[1].strip() or ""
        # model_tso_command = [v for v in model_listuser_tso_attributes if "COMMAND" in v][0].split('=')[1].strip() or ""

        try:
            # Access additional module user attributes for use in a new user.
            cmd=f"tsocmd LISTUSER {self._model_user}"
            model_listuser_attributes = self._connect(self._remote_host, self._model_user,cmd)

            # Match the list user results and place in variables (not all are used)
            model_owner = [v for v in model_listuser_attributes if "OWNER" in v][0].split('OWNER=')[1].split()[0].strip() or None

            if not model_owner:
                err_details = "OWNER"
                err_msg = f"Unable access the model user [{self._managed_racf_user}] {err_details}, this is required to create user [{self._managed_racf_user}]."
                raise Exception(err_msg)
        except IndexError as err:
            err_msg = f"Unable access the results, this is required to create user [{self._managed_racf_user}]."
            raise Exception(f"{err_msg}, exception [{err}].")
        except Exception as err:
            raise Exception(f"Unable to LISTUSER for {self._model_user}, exception [{err}]")

        # Collect the various public keys for use with the z/OS managed node, some accept only RSA and others ED25519
        public_keys = self._read_files_in_directory("~/.ssh/", "*.pub")

        # The command consisting of shell and tso operations to create a user.
        add_user_cmd = StringIO()

        # (1) Create group ANSIGRP for general identification of users and auto assign the UID
        #     Success of the command yields 'Group ANSIGRP was assigned an OMVS GID value of...'
        #     Failure of the command yields 'INVALID GROUP, ANSIGRP' with usually a RC 8 if the group exists.
        self._managed_user_group = self._get_random_user()

        add_user_cmd.write(f"tsocmd 'ADDGROUP {self._managed_user_group} OMVS(AUTOGID)';")
        add_user_cmd.write(f"echo Create {self._managed_user_group} RC=$?;")

        # (2) Add a user owned by the model_owner. Expect an error when a new TSO userid is defined since the ID can't
        #     receive deferred messages until the id is defined in SYS1.BRODCAST, thus the SEND message fails.
        #       BROADCAST DATA SET NOT USABLE+
        #       I/O SYNAD ERROR
        escaped_user = re.escape(self._managed_racf_user)
        add_user_cmd.write(f"Creating USER '{escaped_user}' with PASSWORD {passwd} for remote host {self._remote_host};")
        add_user_cmd.write(f"tsocmd ADDUSER {escaped_user} DFLTGRP\\({self._managed_user_group}\\) OWNER\\({model_owner}\\) NOPASSWORD TSO\\(ACCTNUM\\({model_tso_acctnum}\\) PROC\\({model_tso_proc}\\)\\) OMVS\\(HOME\\(/u/{escaped_user}\\) PROGRAM\\('/bin/sh'\\) AUTOUID;")
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

        try:
            cmd=f"{add_user_cmd.getvalue()}"
            add_user_attributes = self._connect(self._remote_host, self._model_user,cmd)

            print(f"DEBUG OUT {add_user_attributes}")
            # Because this is a tsocmd run through shell, any user with a $ will be expanded and thus truncated, you can't change
            # that behavior since its happening on the managed node, solution is to match a shorter pattern without the user.
            is_assigned_omvs_uid = True if [v for v in add_user_attributes if f"was assigned an OMVS UID value" in v] else False
            if not is_assigned_omvs_uid:
                err_details = "create OMVS UID"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)

            create_group_rc = [v for v in add_user_attributes if f"Create {self._managed_user_group} RC=" in v][0].split('=')[1].strip() or None
            if not create_group_rc or int(create_group_rc[0]) > 8:
                err_details = "create user group"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)

            add_user_rc = [v for v in add_user_attributes if f"ADDUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
            if not add_user_rc or int(add_user_rc[0]) > 0:
                err_details = "ADDUSER"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)

            mkdir_rc = [v for v in add_user_attributes if f"mkdir {escaped_user} RC=" in v][0].split('=')[1].strip() or None
            if not mkdir_rc or int(mkdir_rc[0]) > 0:
                err_details = "create home directory for {escaped_user}"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)

            authorized_keys_rc = [v for v in add_user_attributes if f"touch authorized_keys RC=" in v][0].split('=')[1].strip() or None
            if not authorized_keys_rc or int(authorized_keys_rc[0]) > 0:
                err_details = "create authorized_keys file for {escaped_user}"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)

            chown_rc = [v for v in add_user_attributes if f"chown {escaped_user} RC=" in v][0].split('=')[1].strip() or None
            if not chown_rc or int(chown_rc[0]) > 0:
                err_details = "change ownership of home directory for {escaped_user}"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)

            altuser_rc = [v for v in add_user_attributes if f"ALTUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
            if not altuser_rc or int(altuser_rc[0]) > 0:
                err_details = "update password for {escaped_user}"
                err_msg = f"Unable to {err_details}, this is required to create user [{self._managed_racf_user}, review output {add_user_attributes}."
                raise Exception(err_msg)
        except IndexError as err:
            err_msg = f"Unable access the results, this is required to create user [{self._managed_racf_user}]."
            raise Exception(f"{err_msg}, exception [{err}].")
        except Exception as err:
            raise Exception(f"The model user {self._model_user} is unable to create managed RACF user {escaped_user}, exception [{err}]")

        # Update the user according to the ManagedUserType type by invoking the mapped function
        self.operations[managed_user.name](self)

        return (self._managed_racf_user, passwd)


    def _create_user_zoau_limited_access_opercmd(self) -> None:
        """
        Update a managed user id for the remote node with restricted access to ZOAU
        SAF Profile 'MVS.MCSOPER.ZOAU' and SAF Class OPERCMDS with universal access
        authority set to UACC(NONE). With UACC as NONE, this user will be refused
        access to the ZOAU opercmd utility.

        Parameters
        ----------
        managed_racf_user (str)
            The managed user created that will we updated according tho the ManagedUseeType selected.

        See Also
        --------
            :py:class:`ManagedUserType`
            :py:func:`create_managed_user`

        Raises
        ------
        Exception
            If any of the remote commands return codes are out of range an exception
            and the stdout and stderr is returned.
        """
        saf_profile="MVS.MCSOPER.ZOAU"
        saf_class="OPERCMDS"
        command = StringIO()

        command.write(f"Redefining USER '{self._managed_racf_user}';")
        command.write(f"tsocmd RDEFINE {saf_class} {saf_profile} UACC\\(NONE\\) AUDIT\\(ALL\\);")
        command.write(f"echo RDEFINE RC=$?;")
        command.write(f"tsocmd PERMIT {saf_profile} CLASS\\({saf_class}\\) ID\\({self._managed_racf_user}\\) ACCESS\\(NONE\\);")
        command.write(f"echo PERMIT RC=$?;")
        command.write(f"tsocmd SETROPTS RACLIST\\({saf_class}\\) REFRESH;")
        command.write(f"echo SETROPTS RC=$?;")

        cmd=f"{command.getvalue()}"
        results_stdout_lines = self._connect(self._remote_host, self._model_user,cmd)

        try:
            # Evaluate the results
            rdefine_rc = [v for v in results_stdout_lines if f"RDEFINE RC=" in v][0].split('=')[1].strip() or None
            if not rdefine_rc or int(rdefine_rc[0]) > 4:
                err_details = f"rdefine {saf_class} {saf_profile}"
                err_msg = f"Unable to {err_details} for managed user [{self._managed_racf_user}, review output {results_stdout_lines}."
                raise Exception(err_msg)

            permit_rc = [v for v in results_stdout_lines if f"PERMIT RC=" in v][0].split('=')[1].strip() or None
            if not permit_rc or int(permit_rc[0]) > 4:
                err_details = f"permit {saf_profile} class {saf_class}"
                err_msg = f"Unable to {err_details} for managed user [{self._managed_racf_user}, review output {results_stdout_lines}."
                raise Exception(err_msg)

            setropts_rc = [v for v in results_stdout_lines if f"SETROPTS RC=" in v][0].split('=')[1].strip() or None
            if not setropts_rc or int(setropts_rc[0]) > 4:
                err_details = f"setropts raclist {saf_class} refresh"
                err_msg = f"Unable to {err_details} for managed user [{self._managed_racf_user}, review output {results_stdout_lines}."
                raise Exception(err_msg)
        except IndexError as err:
            err_msg = f"Unable access the results, this is required to reduce permissions for user [{self._managed_racf_user}]."
            raise Exception(f"{err_msg}, exception [{err}].")
        except Exception as err:
            raise Exception(f"The model user {self._model_user} is unable to reduce permissions RACF user {self._managed_racf_user}, exception [{err}]")

    # TODO: Implement this method in the future
    def _create_user_zos_limited_hlq(self) -> None:
        """
        Update a managed user id for the remote node with restricted access to
        High LevelQualifiers:
        - RESTRICT
        - NOPERMIT
        Any attempt for this user to access the HLQ will be rejected.

        Parameters
        ----------
        managed_racf_user (str)
            The managed user created that will we updated according tho the ManagedUseeType selected.

        See Also
        --------
            :py:class:`ManagedUserType`
            :py:func:`create_managed_user`

        Raises
        ------
        Exception
            If any of the remote commands return codes are out of range an exception
            and the stdout and stderr is returned.
        """
        print("Needs to be implemented")


    # TODO: Implement this method in the future
    def _create_user_zos_limited_tmp_hlq(self) -> None:
        """
        Update a managed user id for the remote node with restricted access to
        temporary data set High LevelQualifiers:
        - TSTRICT
        - TNOPERM
        Any attempt for this user to access the HLQ will be rejected.

        Parameters
        ----------
        managed_racf_user (str)
            The managed user created that will we updated according tho the ManagedUseeType selected.

        See Also
        --------
            :py:class:`ManagedUserType`
            :py:func:`create_managed_user`

        Raises
        ------
        Exception
            If any of the remote commands return codes are out of range an exception
            and the stdout and stderr is returned.
        """
        print("Needs to be implemented")

    def _noop(self) -> None:
        """
        Method intentionally takes any number of args and does nothing.
        It is meant to be a NOOP function to be used as a stub with several
        of the ManagedUserTypes.
        """
        pass


    """
    Function pointer mapping of ManagedUserType to functions that complete the requested
    access for for the user. Simple lookup table to reduce the if/else proliferation.
    """
    operations = {
        ManagedUserType.ZOAU_LIMITED_ACCESS_OPERCMD.name: _create_user_zoau_limited_access_opercmd,
        ManagedUserType.ZOS_LIMITED_HLQ.name: _create_user_zos_limited_hlq,
        ManagedUserType.ZOS_LIMITED_TMP_HLQ.name: _create_user_zos_limited_tmp_hlq,
        ManagedUserType.ZOS_BEGIN_WITH_AT_SIGN.name: _noop,
        ManagedUserType.ZOS_BEGIN_WITH_POUND.name: _noop,
        ManagedUserType.ZOS_RANDOM_SYMBOLS.name: _noop
    }
