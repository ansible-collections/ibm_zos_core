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

class ManagedUsers (Enum):
    """
    Represents the z/OS users available for functional testing.

    Attributes:
    ZOAU_LIMITED_ACCESS_OPERCMD: ManagedUsers
    ZOS_LIMITED_HLQ: ManagedUsers
    ZOS_LIMITED_TMP_HLQ: ManagedUsers
    """

    ZOAU_LIMITED_ACCESS_OPERCMD=("zoau_limited_access_opercmd")
    """
    user_access:user_name
    A z/OS managed user with restricted access to ZOAU
    SAF Profile 'MVS.MCSOPER.ZOAU' and SAF Class OPERCMDS
    with universal access authority set to UACC(NONE). With
    UACC as NONE, this user will be refused access to the
    ZOAU opercmd utility.
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

    ZOS_BEGIN_WITH_AT_SIGN=("zos_begin_with_at_sign")
    """
    A z/OS managed user....
    """

    ZOS_BEGIN_WITH_POUND=("zos_begin_with_pound")
    """
    A z/OS managed user....
    """

    ZOS_RANDOM_SYMBOLS=("zos_random_symbols")
    """
    A z/OS managed user....user ID cannot exceed seven characters and must begin with an alphabetic, # (X'7B'), $ (X'5B'), or @ (X'7C') character.
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

def get_random_passwd() -> str:
    letters = string.ascii_uppercase
    start = ''.join(random.choice(letters) for i in range(3))
    middle = ''.join(str(random.randint(1,9)))
    finish = ''.join(random.choice(letters) for i in range(4))
    return f"{start}{middle}{finish}"

def get_random_user(managed_user: ManagedUsers = None) -> str:
    """A-Z, 0-9, #, $, or @."""
    letters = string.ascii_uppercase
    if managed_user is not None:
        if managed_user.name == ManagedUsers.ZOS_BEGIN_WITH_AT_SIGN.name:
            return "@" + ''.join(random.choice(letters) for i in range(7))
        elif managed_user.name == ManagedUsers.ZOS_BEGIN_WITH_POUND.name:
            return "#" + ''.join(random.choice(letters) for i in range(7))
        elif managed_user.name == ManagedUsers.ZOS_RANDOM_SYMBOLS.name:
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

def read_files_in_directory(directory: str = "~/.ssh", pattern: str = "*.pub") -> list:
    """Reads files in a directory that match the pattern and return file contents as a list entry."""

    file_contents_as_list = []

    # Expand the tilde to the home directory
    expanded_directory = os.path.expanduser(directory)

    for filename in glob.glob(os.path.join(expanded_directory, pattern)):
        with open(filename, 'r') as f:
            file_contents_as_list.append(f.read().rstrip('\n'))
    return file_contents_as_list

def copy_ssh_key(user, passwd, host, key_path):
    """
    Copy SSH key to a remote host using subprocess.
    Note:
        This requires the host have sshpass installed.
    See:
        Method read_files_in_directory instead to copy the public keys.
    """

    command = ["sshpass", "-p", f"{passwd}", "ssh-copy-id", "-o", "StrictHostKeyChecking=no", "-i", f"{key_path}", f"{user}@{host}"] #, "&>/dev/null"]
    result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

    if result.returncode != 0:
        raise Exception("Unable to copy public keys to remote host, check that sshpass is installed.")

def get_managed_user_name(ansible_zos_module, managed_user: ManagedUsers = None) -> str:

    # TODO: Check if user exists and retry?
    # Given this a randomly generated user, we can assume this won't be an issue and save the compute.
    user = get_random_user(managed_user)

    print("USER " + user)
    # Generate the password to establish a password-less connection and use with RACF.
    passwd = get_random_passwd()

    print("PASSWD " + passwd)
    # An existing user (model) will be used to access system specific values used to create a new user
    model_user = ansible_zos_module["options"]["user"]

    # Access module user's TSO attributes for reuse
    results_tso_noracf = ansible_zos_module.all.shell(
            cmd=f"tsocmd LISTUSER {model_user} TSO NORACF"
    )

    # Extract the model user TSO entries for reuse in a new user
    model_listuser_tso_attributes = list(results_tso_noracf.contacted.values())[0].get("stdout_lines")

    # Match the tso list results and place in variables (not all are used)
    model_tso_acctnum = [v for v in model_listuser_tso_attributes if "ACCTNUM" in v][0].split('=')[1].strip() or None
    if not model_tso_acctnum:
        raise Exception(f"Unable to determine the TSO Account number required for adding TSO {user}.")

    model_tso_proc = [v for v in model_listuser_tso_attributes if "PROC" in v][0].split('=')[1].strip() or None
    if not model_tso_proc:
        raise Exception(f"Unable to determine the TSO Proc required for adding TSO {user}.")

    # TODO: These are currently not used when creating the user, consider minimally adding SIZE and MAXXSIZE to dynamic users
    # model_tso_size = [v for v in model_listuser_tso_attributes if "SIZE" in v][0].split('=')[1].strip() or None
    # model_tso_maxsize = [v for v in model_listuser_tso_attributes if "MAXSIZE" in v][0].split('=')[1].strip() or None
    # model_tso_unit = [v for v in model_listuser_tso_attributes if "UNIT" in v][0].split('=')[1].strip() or ""
    # model_tso_userdata = [v for v in model_listuser_tso_attributes if "USERDATA" in v][0].split('=')[1].strip() or ""
    # model_tso_command = [v for v in model_listuser_tso_attributes if "COMMAND" in v][0].split('=')[1].strip() or ""


    # Access additional module user attributes for use in a new user.
    results_listuser = ansible_zos_module.all.shell(
            cmd=f"tsocmd LISTUSER {model_user}"
    )

    # Extract the model user TSO entries for reuse in a new user
    model_listuser_attributes = list(results_listuser.contacted.values())[0].get("stdout_lines")

    # Match the list user results and place in variables (not all are used)
    model_owner = [v for v in model_listuser_attributes if "OWNER" in v][0].split('OWNER=')[1].split()[0].strip() or ""

    # Collect the various public keys for use with the z/OS managed node, some accept only RSA and others ED25519
    public_keys = read_files_in_directory("~/.ssh/", "*.pub")

    # The command consisting of shell and tso operations to create a user.
    add_user_cmd = StringIO()

    # For verbosity, extract the host for debugging if needed. 
    remote_host = ansible_zos_module["options"]["inventory"].replace(",", "")

    # (1) Create group ANSIGRP for general identification of users and auto assign the UID
    #     Success of the command yields 'Group ANSIGRP was assigned an OMVS GID value of...'
    #     Failure of the command yields 'INVALID GROUP, ANSIGRP' with usually a RC 8 if the group exists.
    user_group = "ANSIGRP"
    add_user_cmd.write(f"tsocmd 'ADDGROUP {user_group} OMVS(AUTOGID)';")
    add_user_cmd.write(f"echo Create {user_group} RC=$?;")

    # (2) Add a user owned by the model_owner. Expect an error when a new TSO userid is defined since the ID can't
    #     receive deferred messages until the id is defined in SYS1.BRODCAST, thus the SEND message fails.
    #       BROADCAST DATA SET NOT USABLE+
    #       I/O SYNAD ERROR
    user = re.escape(user)
    add_user_cmd.write(f"Creating USER '{user}' with PASSWORD {passwd} for remote host {remote_host};")
    add_user_cmd.write(f"tsocmd ADDUSER {user} DFLTGRP\\({user_group}\\) OWNER\\({model_owner}\\) NOPASSWORD TSO\\(ACCTNUM\\({model_tso_acctnum}\\) PROC\\({model_tso_proc}\\)\\) OMVS\\(HOME\\(/u/{user}\\) PROGRAM\\('/bin/sh'\\) AUTOUID;")
    add_user_cmd.write(f"echo ADDUSER '{user}' RC=$?;")
    add_user_cmd.write(f"mkdir -p /u/{user}/.ssh;")
    add_user_cmd.write(f"echo mkdir '{user}' RC=$?;")
    add_user_cmd.write(f"umask 0022;")
    add_user_cmd.write(f"touch /u/{user}/.ssh/authorized_keys;")
    add_user_cmd.write(f"echo touch authorized_keys RC=$?;")
    add_user_cmd.write(f"chown -R {user} /u/{user};")
    add_user_cmd.write(f"echo chown '{user}' RC=$?;")
    for pub_key in public_keys:
        add_user_cmd.write(f"echo {pub_key} >> /u/{user}/.ssh/authorized_keys;")
        add_user_cmd.write(f"echo PUB_KEY RC=$?;")
    add_user_cmd.write(f"tsocmd ALTUSER {user} PASSWORD\\({passwd}\\) NOEXPIRED;")
    add_user_cmd.write(f"echo ALTUSER '{user}' RC=$?;")

    # Now that the user is created, update the user according to the managedUsers type
    add_user_cmd = operations[managed_user.name](user, add_user_cmd)
    # Extract command from from StringsIO and run it on the z/OS managed node.
    results_add_user_cmd = ansible_zos_module.all.shell(
            cmd=f"{add_user_cmd.getvalue()}"
    )

    # Extract the new user stdout lines for evaluation
    add_user_attributes = list(results_add_user_cmd.contacted.values())[0].get("stdout_lines")

    # Because this is a tsocmd run through shell, any user with a $ will be expanded and thus truncated, you can't change
    # that behavior since its happening on the managed node, solution is to match a shorter pattern without the user.
    is_assigned_omvs_uid = True if [v for v in add_user_attributes if f"was assigned an OMVS UID value" in v] else False
    if not is_assigned_omvs_uid:
        raise Exception(f"Unable to create OMVS UID, please review the command output {add_user_attributes}.")

    create_group_rc = [v for v in add_user_attributes if f"Create {user_group} RC=" in v][0].split('=')[1].strip() or None
    if not create_group_rc or int(create_group_rc[0]) > 8:
        raise Exception(f"Unable to create user group {user_group}, please review the command output {add_user_attributes}.")

    add_user_rc = [v for v in add_user_attributes if f"ADDUSER {user} RC=" in v][0].split('=')[1].strip() or None
    if not add_user_rc or int(add_user_rc[0]) > 0:
        raise Exception(f"Unable to ADDUSER {user}, please review the command output {add_user_attributes}.")

    mkdir_rc = [v for v in add_user_attributes if f"mkdir {user} RC=" in v][0].split('=')[1].strip() or None
    if not mkdir_rc or int(mkdir_rc[0]) > 0:
        raise Exception(f"Unable to make home directories for {user}, please review the command output {add_user_attributes}.")

    authorized_keys_rc = [v for v in add_user_attributes if f"touch authorized_keys RC=" in v][0].split('=')[1].strip() or None
    if not authorized_keys_rc or int(authorized_keys_rc[0]) > 0:
        raise Exception(f"Unable to make authorized_keys file for {user}, please review the command output {add_user_attributes}.")

    chown_rc = [v for v in add_user_attributes if f"chown {user} RC=" in v][0].split('=')[1].strip() or None
    if not chown_rc or int(chown_rc[0]) > 0:
        raise Exception(f"Unable to change ownership of home directory for {user}, please review the command output {add_user_attributes}.")

    altuser_rc = [v for v in add_user_attributes if f"ALTUSER {user} RC=" in v][0].split('=')[1].strip() or None
    if not altuser_rc or int(altuser_rc[0]) > 0:
        raise Exception(f"Unable to update password for {user}, please review the command output {add_user_attributes}.")

    rdefine_rc = [v for v in add_user_attributes if f"RDEFINE RC=" in v][0].split('=')[1].strip() or None
    if not rdefine_rc or int(rdefine_rc[0]) > 4:
        raise Exception(f"Unable to rdefine {saf_class} {saf_profile}, please review the command output {add_user_attributes}.")
    permit_rc = [v for v in add_user_attributes if f"PERMIT RC=" in v][0].split('=')[1].strip() or None
    if not permit_rc or int(permit_rc[0]) > 4:
        raise Exception(f"Unable to permit {saf_profile} class {saf_class} for ID {user}, please review the command output {add_user_attributes}.")
    setropts_rc = [v for v in add_user_attributes if f"SETROPTS RC=" in v][0].split('=')[1].strip() or None
    if not setropts_rc or int(setropts_rc[0]) > 4:
        raise Exception(f"Unable to setropts raclist {saf_class} refresh, please review the command output {add_user_attributes}.")

    # TODO: Return a tuple of the ansible connection and user, maybe password

def create_user_zoau_limited_access_opercmd(user: str, command: StringIO) -> StringIO:
    saf_profile="MVS.MCSOPER.ZOAU"
    saf_class="OPERCMDS"

    command.write(f"Redefining USER '{user}';")
    command.write(f"tsocmd RDEFINE {saf_class} {saf_profile} UACC\\(NONE\\) AUDIT\\(ALL\\);")
    command.write(f"echo RDEFINE RC=$?;")
    command.write(f"tsocmd PERMIT {saf_profile} CLASS\\({saf_class}\\) ID\\({user}\\) ACCESS\\(NONE\\);")
    command.write(f"echo PERMIT RC=$?;")
    command.write(f"tsocmd SETROPTS RACLIST\\({saf_class}\\) REFRESH;")
    command.write(f"echo SETROPTS RC=$?;")

    return command

def create_user_zos_limited_hlq(ansible_zos_module) -> str:
    return "result create_user_zos_limited_hlq"

def create_user_zos_limited_tmp_hlq(ansible_zos_module) -> str:
    return "result create_user_zos_limited_tmp_hlq"

def noop(*arg) -> None:
    """
    Method intentionally takes any number of args and does nothing.
    It is meant to be a NOOP function to be used as a stub.
    """
    pass

operations = {
    ManagedUsers.ZOAU_LIMITED_ACCESS_OPERCMD.name: create_user_zoau_limited_access_opercmd,
    ManagedUsers.ZOS_LIMITED_HLQ.name: create_user_zos_limited_hlq,
    ManagedUsers.ZOS_LIMITED_TMP_HLQ.name: create_user_zos_limited_tmp_hlq,
    ManagedUsers.ZOS_BEGIN_WITH_AT_SIGN.name: noop,
    ManagedUsers.ZOS_BEGIN_WITH_POUND.name: noop,
    ManagedUsers.ZOS_RANDOM_SYMBOLS.name: noop
}


class Racf:
    from collections import OrderedDict
    import json
    # Try to provide ordered execution to avoid command failure
    racf = OrderedDict()  # Better to remove the ordered dictionary and allow the class to accept an ordering yet follow a default.
    racf['adduser'] = []
    racf['xxx'] = []
    racf['xxx'] = []
    racf['xxx'] = []
    racf['xxx'] = []
    racf['xxx'] = []
    racf['xxx'] = []
    racf['rdefine'] = []
    racf['permit'] = []
    racf['setropts'] = []

    class Adduser:
        user = OrderedDict()
        user['user'] = []
        user['dfltgrp'] = []
        user['password'] = []
        user['tso'] = []
        user['proc'] = []
        user['omvs'] = []
        user['program'] = []

        def __str__(self) -> str:
            return str(json.dumps(self.user, indent=4))

        class User_parameter (Enum):
            user=("USER")
            dfltgrp=("DFLTGRP")

        def __str__(self) -> str:
            """
            Convert the name of the project to lowercase when converting it to a string.

            Return:
                str: The lowercase name of the project.
            """
            return self.name.lower()

        def set_parameter(self, parm: User_parameter):
           # self.racf['user'] = "foobar"
           return None

        def __exit__(self):
            #on exit build a command and set RACF with a function pointer

            #self.racf['user'] = self (as a function pointer) or maybe a command built out is sufficient so string
            # The only reason I see why function pointers would be good is in case there other things to do , eg
            # before you can use TSO commands for RACF, you might need to do some shell commands to set up the users home
            # in USS, this is two different types commands, one being TSO other being shell. 
            return None

    class Redefine:
        redefine = OrderedDict()
        redefine['class'] = []
        redefine['profile'] = []
        redefine['uacc'] = []
        redefine['audit'] = []

    class Permit:
        redefine = OrderedDict()
        redefine['class'] = []
        redefine['profile'] = []
        redefine['user'] = []
        redefine['access'] = []

    class Setropts:
        setropts = OrderedDict()
        setropts['raclist'] = []


def main():
    x=get_managed_user_name("nothing", ManagedUsers.zoau_limited_access_opercmd)
    print(x)

if __name__ == '__main__':
    # racf = Racf()
    # adduser = Racf.Adduser()
    main()
