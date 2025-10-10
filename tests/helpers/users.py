# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024, 2025
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

import inspect
from io import StringIO
from enum import Enum
import json
import random
import shutil
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

    Another important note is when using this API, you can't parametrize test cases, because
    once the pytest fixture (ansible_zos_module) is updated with a new user and performs a
    remote operation on a managed node, the fixture's user can not be changed because control
    is passed back and all attempts to change the user for reuse will fail, unless your goal
    is to use the same managedUserType in the parametrization this is not recommended.


    Example
    -------
    from ibm_zos_core.tests.helpers.users import ManagedUserType

    def test_demo_how_to_use_managed_user(ansible_zos_module):
        # This demonstrates a user who has specific requirements
        hosts = ansible_zos_module
        managed_user = None

        who = hosts.all.shell(cmd = "whoami")
        for person in who.contacted.values():
            print(f"Who am I BEFORE asking for a managed user = {person.get("stdout")}")

        try:
            # Initialize the Managed user API from the pytest fixture.
            managed_user = ManagedUser.from_fixture(ansible_zos_module)

            # Important: Execute the test case with the managed users execution utility.
            managed_user.execute_managed_user_test(
                managed_user_test_case = "managed_user_test_demo_how_to_use_managed_user",
                debug = True, verbose = False, managed_user_type=ManagedUserType.ZOAU_LIMITED_ACCESS_OPERCMD)

        finally:
            # Delete the managed user on the remote host to avoid proliferation of users.
            managed_user.delete_managed_user()

    def managed_user_test_demo_how_to_use_managed_user(ansible_zos_module):
        hosts = ansible_zos_module
        who = hosts.all.shell(cmd = "whoami")
        for person in who.contacted.values():
            print(f"Who am I AFTER asking for a managed user = {person.get("stdout")}")


    Example Output
    --------------
        Who am I BEFORE asking for a managed user = BPXROOT
        Who am I AFTER asking for a managed user = LJBXMONV
    """

    def __init__(self, model_user: str = None, remote_host: str = None, zoau_path: str = None, pyz_path: str = None, pythonpath: str = None, volumes: str = None, hostpattern: str = None) -> None:
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
        self._zoau_path = zoau_path
        self._pyz_path = pyz_path
        self._pythonpath = pythonpath
        self._volumes = volumes
        self._hostpattern = "all" # can also get it from options host_pattern
        self._managed_racf_user = None
        self._managed_user_group = None
        self._managed_group = None
        self._ssh_config_file_size = 0
        self._ssh_directory_present = True
        self._create_ssh_config_and_directory()

    @classmethod
    def from_fixture(cls, pytest_module_fixture, pytest_interpreter_fixture):
        remote_host = pytest_module_fixture["options"]["inventory"].replace(",", "")
        model_user = pytest_module_fixture["options"]["user"]
        inventory_hosts = pytest_module_fixture["options"]["inventory_manager"]._inventory.hosts
        inventory_list = list(inventory_hosts.values())[0].vars.get('ansible_python_interpreter').split(";")
        environment_vars = pytest_interpreter_fixture[0]

        zoau_path = environment_vars.get("ZOAU_HOME")
        pythonpath = environment_vars.get("PYTHONPATH")
        pyz_path = [v for v in inventory_list if f"bin/python" in v][0].split('/bin')[0].strip() or None

        # TODO: To make this dynamic, we need to update AC and then also test with the new fixture because
        # the legacy fixture is using a VOLUMES keyword while raw fixture uses extra_args. Best to move
        # volumes to extra_args. 
        volumes = "000000,222222"
        hostpattern = pytest_module_fixture["options"]["host_pattern"]
        return cls(model_user, remote_host, zoau_path, pyz_path, pythonpath, volumes, hostpattern)


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

        # If the RC=20 (command failure) - let this fall through for now, will be caught by command processors.
        # If the RC=255, raise exection for the connection
        if result.returncode == 255:
            raise Exception(f"Unable to connect remote user [{model_user}] to remote host [{remote_host}], RC [{result.returncode}], stdout [{result.stdout}], stderr [{result.stderr}].")

        return [line.strip() for line in result.stdout.split('\n')]

    def _create_ssh_keys(self, directory:str) -> None:
        """
        Create SSH keys for the new managed user to be used for password-less authentication.
        Creates both RSA and ED25519 because some of the systems only take one or the other
        so both are generated and shared now.

        Parameters
        ----------
        directory (str)
            The directory where to create the ssh keys.

        Raise
        -----
        Exception - if unable to create or run ssh-keygen.
        """
        escaped_user = re.escape(self._managed_racf_user)
        key_command = ["mkdir", "-p", f"{directory}/{escaped_user}"]
        result = subprocess.run(key_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Unable to create keys {result.stdout}, {result.stdout}")

        key_command = ["ssh-keygen", "-q","-t", "rsa", "-N", "", "-f",  f"{directory}/{escaped_user}/id_rsa"]
        result = subprocess.run(key_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Unable to create keys {result.stdout}, {result.stdout}")

        key_command = ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", f"{directory}/{escaped_user}/id_ed25519"]
        result = subprocess.run(key_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Unable to create keys {result.stdout}, {result.stdout}")


    def _ssh_config_append(self):
        """
        Appends necessary configurations needed to use the managed user in a containerized environment but also
        works for non-containerized. This will append the custom ssh key paths to '~/.ssh/config', typically /tmp/{user}/*.

        Notes
        -----
        Although this logic of creating temporary keys is not needed when managed VENVs are used via `.ac/` , because
        those IDs have access to the controller's keys are are passed to the managed node as the new users id. For now,
        this logic is applied to both venv's and containers. I don't forsee any concurrent issues with updating
        the config at this time.

        See Also
        --------
        :py:member:`delete_managed_user()` for cleaning up and restoring the '~/.ssh/config' which calls
        `_ssh_config_remove_host()`.
        :py:member:`_create_ssh_keys` for creating the ssh keys for the new managed user.
        """
        escaped_user = re.escape(self._managed_racf_user)
        config_file = os.path.expanduser("~/.ssh/config")

        with open(config_file, "a") as f:
            f.write(f"\nHost {self._remote_host}\n")
            f.write(f"    Hostname {self._remote_host}\n")
            f.write(f"    IdentityFile ~/.ssh/id_rsa\n")
            f.write(f"    IdentityFile ~/.ssh/id_ed25519\n")
            f.write(f"    IdentityFile /tmp/{escaped_user}/id_ed25519\n")
            f.write(f"    IdentityFile /tmp/{escaped_user}/id_rsa\n")

        # If you need to debug, uncomment this to see what is put in to the ssh/config.
        # with open(config_file, 'r') as f:
        #    print(f"Config file {config_file} contents, f.read()")

    def _create_ssh_config_and_directory(self) -> None:
        """
        This method will create as well as track the prior state of the ssh config and .ssh directory.
        During class initialization this is called to determine the ssh config state, eg does the
        'ssh/' dir exit, does the 'ssh/config' exist, is the 'ssh/config', empty, etc. This is done
        so that on deletion of the user, the config file or directory can be properly restored.

        Notes:
        Class variable '_ssh_config_file_size' can have values:
        - `-1`  - if the file does not exist
        - `0` - if the file exists and has no content
        - `> 0` - if the file existed prior to updates.
        Default '_ssh_config_file_size = True'

        Class variable '_ssh_directory_present' can have values:
        - `True` if the '~/.ssh' directory was present at the time this class was instantiated
        - `False` if the '~/.ssh' directory was not present at the time this class was instantiated
        Default '_ssh_directory_present = 0'
        """
        ssh_config_dir = os.path.expanduser("~/.ssh")
        ssh_config_file = os.path.expanduser("~/.ssh/config")

        if not os.path.exists(ssh_config_dir):
            # Set class variable indicators
            self._ssh_directory_present = False
            self._ssh_config_file_size = -1

            # Create the empty directory
            os.makedirs(ssh_config_dir)

            # Create the empty file
            open(ssh_config_dir, 'a').close()
        else:
            try:
                self._ssh_config_file_size = os.stat(ssh_config_file).st_size
            except FileNotFoundError:
                # If the config does not exist, set it to -1 so we know to completely remove the config.
                self._ssh_config_file_size = -1
                # Create the empty file
                open(ssh_config_file, 'a').close()


    def _ssh_config_remove_host(self) -> None:
        """
        This method reads the '~/.ssh/config' and will remove any added entries that match to the newly
        created managed user, ensuring that the original filed be restored to its previous state.

        This method uses class variable '_ssh_directory_present' which can have values:
        - `True` if the '~/.ssh' directory was present at the time this class was instantiated
        - `False` if the '~/.ssh' directory was not present at the time this class was instantiated
        -  Default '_ssh_directory_present = 0'
        """

        # Delete entry from shell (useful for AC): sed 's/^Host/\n&/' ~/.ssh/config | sed '/^Host '"$host"'$/,/^$/d;/^$/d'
        # Optionally Python: cmd = f"sed 's/^Host/\\n&/' {file} | sed '/^Host '\"{host}\"'$/,/^$/d;/^$/d'"
        #                    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        ssh_config_dir = os.path.expanduser("~/.ssh")
        ssh_config_file = os.path.expanduser("~/.ssh/config")

        # No .ssh/ dir existed to begin with, delete it all.
        if not self._ssh_directory_present:
            shutil.rmtree(ssh_config_dir)
        # .ssh/ dir exists but no config existed, remove config
        elif self._ssh_config_file_size == -1:
            os.remove(ssh_config_file)
        # File previously existed so remove only the updated portions, restoring the original.
        elif self._ssh_config_file_size >= 0:
            is_host = False
            with open(ssh_config_file, "r") as fr:
                lines = fr.readlines()

            with open(ssh_config_file, "w") as fw:
                for line in lines:
                    if len(line.split()) > 0 and line.split()[0] == "Host":
                        if self._remote_host in line:
                            is_host = True
                        else:
                            is_host = False
                    if not is_host:
                        fw.write(line)


    def execute_managed_user_test(self, managed_user_test_case: str, debug: bool = False, verbose: bool = False, managed_user_type: ManagedUserType = None) -> None:
        """
        Executes the test case using articulated pytest options when the test case needs a managed user. This is required
        to execute any test that needs a manage user, a wrapper test case should call this method, the 'managed_user_test_case'
        must begin with 'managed_user_' as opposed to 'test_', this because the pytest command built will override the ini
        with this value.

        Parameters
        ----------
        managed_user_test_case (str)
            The managed user test case that begins with 'managed_user_'
        debug (str)
            Enable verbose output for pytest, the equivalent command line option of '-s'.
        verbose (str)
            Enables pytest verbosity level 4 (-vvvv)

        Raises
        ------
        Exception - if the test case fails (non-zero RC from pytest/subprocess), the stdout and stderr are returned for evaluation.
        ValueError - if the managed user is not created, you must call `self._managed_racf_user()`.

        See Also
        --------
        :py:member:`_create_managed_user` required before this function can be used as a managed user needs to exist.
        """

        if managed_user_test_case is None or not managed_user_test_case.startswith("managed_user_"):
            raise ValueError("Test cases using a managed user must begin with 'managed_user_' to be collected for execution.")

        # if not self._managed_racf_user:
        #     raise ValueError("No managed user has been created, please ensure that the method `self._managed_racf_user()` has been called prior.")

        self._create_managed_user(managed_user_type)

        # Get the file path of the caller function
        calling_test_path = inspect.getfile(inspect.currentframe().f_back)

        # Get the test case name that this code is being run from, this is not an function arg.
        # managed_user_test_case = inspect.stack()[1][3]

        testcase = f"{calling_test_path}::{managed_user_test_case}"
        # hostpattern = "all" # can also get it from options host_pattern
        capture = " -s"
        verbosity = " -vvvv"

        inventory: dict [str, str] = {}
        inventory.update({'host': self._remote_host})
        inventory.update({'user': self._managed_racf_user})
        inventory.update({'zoau': self._zoau_path})  # get this from fixture
        inventory.update({'pyz': self._pyz_path})    # get this from fixture
        inventory.update({'pythonpath': self._pythonpath}) # get this from fixture
        extra_args = {}
        extra_args.update({'extra_args':{'volumes':self._volumes.split(",")}}) # get this from fixture
        inventory.update(extra_args)

        node_inventory = json.dumps(inventory)

        # Carefully crafted 'pytest' command to be allow for it to be called from anther test driven by pytest and uses the zinventory-raw fixture.
        pytest_cmd = f"""pytest {testcase} --override-ini "python_functions=managed_user_" --host-pattern={self._hostpattern}{capture if debug else ""}{verbosity if verbose else ""} --zinventory-raw='{node_inventory}'"""
        result = subprocess.run(pytest_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode != 0:
             raise Exception(result.stdout + result.stderr)
        else:
            print(result.stdout)


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
        # Clean up the ~/.ssh/config file
        self._ssh_config_remove_host()

        # Remove the OMVS segment from the remote hoste
        escaped_user = re.escape(self._managed_racf_user)
        command = StringIO()
        command.write(f"echo Deleting USER '{self._managed_racf_user}';")
        command.write(f"tsocmd DELUSER {escaped_user};")
        command.write(f"echo DELUSER '{escaped_user}' RC=$?;")
        command.write(f"tsocmd DELGROUP {self._managed_user_group};")
        command.write(f"echo DELGROUP '{self._managed_user_group}' RC=$?;")
        if self._managed_group is not None:
            command.write(f"export TSOPROFILE=\"noprefix\";tsocmd DELDSD {self._managed_group}.*;")
            command.write(f"tsocmd DELGROUP {self._managed_group};")
            command.write(f"echo DELMANAGEDGROUP '{self._managed_group}' RC=$?;")
        # Access additional module user attributes for use in a new user.
        cmd=f"{command.getvalue()}"
        results_stdout_lines = self._connect(self._remote_host, self._model_user,cmd)

        deluser_rc = [v for v in results_stdout_lines if f"DELUSER {escaped_user} RC=" in v][0].split('=')[1].strip() or None
        if not deluser_rc or int(deluser_rc[0]) > 0:
            raise Exception(f"Unable to delete user {escaped_user}, please review the command output {results_stdout_lines}.")

        delgroup_rc = [v for v in results_stdout_lines if f"DELGROUP {self._managed_user_group} RC=" in v][0].split('=')[1].strip() or None
        if not delgroup_rc or int(delgroup_rc[0]) > 0:
            raise Exception(f"Unable to delete user {escaped_user}, please review the command output {results_stdout_lines}.")

        if self._managed_group is not None:
            delmanagedgroup_rc = [v for v in results_stdout_lines if f"DELMANAGEDGROUP {self._managed_group} RC=" in v][0].split('=')[1].strip() or None
            if not delmanagedgroup_rc or int(delmanagedgroup_rc[0]) > 0:
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


    def _create_managed_user(self, managed_user: ManagedUserType) -> Tuple[str, str]:
        """
        Generate a managed user for the remote node according to the ManagedUserType selected.

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
        # Since this code could run in a container and not connected to the host via a venv, we must create new keys
        # for the managed user and share their location with ssh.

        # Create ssh keys for the new managed user, `/tmp/{user}/*.pub`
        self._create_ssh_keys("/tmp")
        esc_user = re.escape(self._managed_racf_user)
        public_keys = self._read_files_in_directory(f"/tmp/{esc_user}", "*.pub")

        # Append the new users key paths to the ssh/config so that ansible can find the private key for password-less connections
        self._ssh_config_append()

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
            # need to connect with ssh  -i /tmp/UPGLSFLH/id_rsa UPGLSFLH@xyz.com
            add_user_attributes = self._connect(self._remote_host, self._model_user,cmd)

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

        # Update the user according to the ManagedUserType type by invoking the mapped function pointer
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
            :py:func:`_create_managed_user`

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

    def _create_user_zos_limited_hlq(self) -> None:
        """
        Update a managed user id for the remote node with restricted access to
        High LevelQualifiers:
        - NOPERMIT
        Any attempt for this user to access the HLQ will be rejected.

        Parameters
        ----------
        managed_racf_user (str)
            The managed user created that will we updated according tho the ManagedUseeType selected.

        See Also
        --------
            :py:class:`ManagedUserType`
            :py:func:`_create_managed_user`

        Raises
        ------
        Exception
            If any of the remote commands return codes are out of range an exception
            and the stdout and stderr is returned.
        """
        group="NOPERMIT"
        restricted_hlq="NOPERMIT.*"
        saf_class = "DATASET"
        command = StringIO()
        command.write(f"echo create GROUP '{group}';")
        command.write(f"tsocmd ADDGROUP \\({group}\\) OMVS\\(AUTOGID\\);")
        command.write(f"echo ADDGROUP RC=$?;")
        command.write(f"export TSOPROFILE=\"noprefix\";")
        command.write(f"tsocmd ADDSD \"NOPERMIT.*\" UACC\\(NONE\\);")
        command.write(f"tsocmd PERMIT \'{restricted_hlq}\' CLASS\\({saf_class}\\) ID\\({self._managed_racf_user}\\) ACCESS\\(NONE\\);")
        command.write(f"echo PERMIT RC=$?;")
        command.write(f"tsocmd SETROPTS GENERIC\\(DATASET\\) REFRESH;")
        command.write(f"echo SETROPTS RC=$?;")

        cmd=f"{command.getvalue()}"
        results_stdout_lines = self._connect(self._remote_host, self._model_user,cmd)
        print(cmd)
        print(results_stdout_lines)
        try:
            # Evaluate the results
            addgroup_rc = [v for v in results_stdout_lines if f"ADDGROUP RC=" in v][0].split('=')[1].strip() or None
            if not addgroup_rc or int(addgroup_rc[0]) > 4:
                err_details = f"addgroup {group}"
                err_msg = f"Unable to {err_details} for managed user [{self._managed_racf_user}, review output {results_stdout_lines}."
                raise Exception(err_msg)

            permit_rc = [v for v in results_stdout_lines if f"PERMIT RC=" in v][0].split('=')[1].strip() or None
            if not permit_rc or int(permit_rc[0]) > 4:
                err_details = f"permit {restricted_hlq} class {saf_class}"
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
        self._managed_group = group

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
        ManagedUserType.ZOS_BEGIN_WITH_AT_SIGN.name: _noop,
        ManagedUserType.ZOS_BEGIN_WITH_POUND.name: _noop,
        ManagedUserType.ZOS_RANDOM_SYMBOLS.name: _noop
    }
