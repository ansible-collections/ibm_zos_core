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
The helpers/users.py file contains various utility functions that
will support test case user needs. Such cases could be randomly
generated users with specific limitations or users with UID 0.
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

def get_random_passwd():
    letters = string.ascii_uppercase
    start = ''.join(random.choice(letters) for i in range(3))
    middle = ''.join(str(random.randint(1,9)))
    finish = ''.join(random.choice(letters) for i in range(4))
    return f"{start}{middle}{finish}"

def get_random_user():
    letters = string.ascii_uppercase
    suffix = ''.join(random.choice(letters) for i in range(4))
    return "ANSI" + suffix


class ManagedUsers (Enum):
    """
    Represents the z/OS users available for functional testing.

    Attributes:
    ZOAU_LIMITED_ACCESS_OPERCMD: ManagedUsers
        A z/OS managed user with restricted access to ZOAU
        SAF Profile 'MVS.MCSOPER.ZOAU' and SAF Class OPERCMDS
        with universal access authority set to UACC(NONE). With
        UACC as NONE, this user will be refused access to the
        ZOAU opercmd utility.
    ZOS_LIMITED_HLQ: ManagedUsers
        A z/OS managed user with restricted access to High Level
        Qualifiers (HLQ): (RESTRICT, NOPERMIT, ....).
    ZOS_LIMITED_TMP_HLQ: ManagedUsers
        A z/OS managed user with restricted access to temporary
        High Level Qualifiers (HLQ): (TSTRICT, TNOPERM, ....).

    Methods:
        user_access() - Returns the user access requested.
        user_name() - Returns the user name to be used in the functional test.
        is_equal(user_name) - Checks if this user name is equal to user name.
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
    ZOS_LIMITED_HLQ=("zos_limited_hlq","ANSUSR02")
    """
    A z/OS managed user with restricted access to High Level
    Qualifiers (HLQ): (RESTRICT, NOPERMIT, ....).
    """

    ZOS_LIMITED_TMP_HLQ=("zos_limited_tmp_hlq", "ANSUSR03")
    """
    A z/OS managed user with restricted access to temporary
    High Level Qualifiers (HLQ): (TSTRICT, TNOPERM, ....).
    """

    def __str__(self) -> str:
        """
        Convert the name of the project to uppercase when converting it to a string.

        Return:
            str: The lowercase name of the project.
        """
        return self.name.upper()

    def string(self) -> str:
        """
        Returns the string value contained in the tuple.
        'online' for ONLINE and 'offline' for OFFLINE.

        Return:
            str: The string value contained in the tuple.
                'online' for ONLINE and 'offline' for OFFLINE.
        """
        return self.value.upper()


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
    """Copy SSH key to a remote host using subprocess, note that some systems will not have sshpass installed."""

    command = ["sshpass", "-p", f"{passwd}", "ssh-copy-id", "-o", "StrictHostKeyChecking=no", "-i", f"{key_path}", f"{user}@{host}"] #, "&>/dev/null"]
    result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

    if result.returncode != 0:
        raise Exception("Unable to copy public keys to remote host, check that sshpass is installed.") 

def get_managed_user_name(ansible_zos_module, managed_user: ManagedUsers = None) -> str:

    # TODO: Check if user exists and retry? Given this a randomly generated user, we can assume
    # this won't be an issue and save the compute.
    user = get_random_user()

    # Generate the password to establish an password-less connection and use with RACF.
    passwd = get_random_passwd()

    # An existing user (model) will be used to access system specific values used to create a new user
    model_user = ansible_zos_module["options"]["user"]

    results_tso_noracf = ansible_zos_module.all.shell(
            cmd=f"tsocmd LISTUSER {model_user} TSO NORACF"
    )

    # Extract the model user TSO entries for reuse in a new user
    model_listuser_tso_attributes = list(results_tso_noracf.contacted.values())[0].get("stdout_lines")

    # Match the tso list results and place in variables (not all are used)
    model_tso_acctnum = [v for v in model_listuser_tso_attributes if "ACCTNUM" in v][0].split('=')[1].strip() or ""
    model_tso_proc = [v for v in model_listuser_tso_attributes if "PROC" in v][0].split('=')[1].strip() or ""
    model_tso_size = [v for v in model_listuser_tso_attributes if "SIZE" in v][0].split('=')[1].strip() or ""
    model_tso_maxsize = [v for v in model_listuser_tso_attributes if "MAXSIZE" in v][0].split('=')[1].strip() or ""
    model_tso_unit = [v for v in model_listuser_tso_attributes if "UNIT" in v][0].split('=')[1].strip() or ""
    model_tso_userdata = [v for v in model_listuser_tso_attributes if "USERDATA" in v][0].split('=')[1].strip() or ""
    model_tso_command = [v for v in model_listuser_tso_attributes if "COMMAND" in v][0].split('=')[1].strip() or ""

    # Print the matches for validation
    print(f"model_tso_acctnum: [{model_tso_acctnum}]")
    print(f"model_tso_proc: [{model_tso_proc}]")
    print(f"model_tso_size: [{model_tso_size}]")
    print(f"model_tso_maxsize: [{model_tso_maxsize}]")
    print(f"model_tso_unit: [{model_tso_unit}]")
    print(f"model_tso_userdata: [{model_tso_userdata}]")
    print(f"model_tso_command: [{model_tso_command}]")

    results_listuser = ansible_zos_module.all.shell(
            cmd=f"tsocmd LISTUSER {model_user}"
    )

    # Extract the model user TSO entries for reuse in a new user
    model_listuser_attributes = list(results_listuser.contacted.values())[0].get("stdout_lines")

    # Match the list user results and place in variables (not all are used)
    model_owner = [v for v in model_listuser_attributes if "OWNER" in v][0].split('OWNER=')[1].split()[0].strip() or ""

    # The shell command consisting of shell and tso operations to create a user.
    add_user_cmd = StringIO()

    # (1) Create group ANSIGRP for general identification of users and auto assign the UID
    #     Success of the command yields 'Group ANSIGRP was assigned an OMVS GID value of 4'
    #     Failure of the command yields 'INVALID GROUP, ANSIGRP' with usually a RC 8 if the group exists.
    user_group = "ANSIGRP"
    add_user_cmd.write(f"tsocmd 'ADDGROUP {user_group} OMVS(AUTOGID)';")
    add_user_cmd.write(f"echo Create {user_group} RC=$?;")
    public_keys = read_files_in_directory("~/.ssh/", "*.pub")
    print(str(public_keys))

    # (2) Add the user to be owned by the model_owner. Expect a similar error when a new TSO userid is defined,
    #     because that id can't receive deferred messages until the id is defined in SYS1.BRODCAST,  thus the SEND
    #     message fails to that user id.
    #       BROADCAST DATA SET NOT USABLE+
    #       I/O SYNAD ERROR
    add_user_cmd.write(f"tsocmd ADDUSER {user} DFLTGRP\\({user_group}\\) OWNER\\({model_owner}\\) NOPASSWORD TSO\\(ACCTNUM\\({model_tso_acctnum}\\) PROC\\({model_tso_proc}\\)\\) OMVS\\(HOME\\('/u/{user}'\\) PROGRAM\\('/bin/sh'\\) AUTOUID;")
    add_user_cmd.write(f"echo ADDUSER {user} RC=$?;")
    add_user_cmd.write(f"mkdir -p /u/{user}/.ssh;")
    add_user_cmd.write(f"echo mkdir {user} RC=$?;")
    add_user_cmd.write(f"umask 0022;")
    add_user_cmd.write(f"touch /u/{user}/.ssh/authorized_keys;")
    add_user_cmd.write(f"chown -R {user} /u/{user};")
    add_user_cmd.write(f"echo chown {user} RC=$?;")
    for pub_key in public_keys:
        add_user_cmd.write(f"echo {pub_key} >> /u/{user}/.ssh/authorized_keys;")
    add_user_cmd.write(f"tsocmd ALTUSER {user} PASSWORD\\({passwd}\\) NOEXPIRED")
    print(f"add_user_cmd [{add_user_cmd.getvalue()}]")

    results_add_user_cmd = ansible_zos_module.all.shell(
            cmd=f"{add_user_cmd.getvalue()}"
    )

    # Extract the new user stdout lines for evaluation
    add_user_attributes = list(results_add_user_cmd.contacted.values())[0].get("stdout_lines")
    print("results_add_user_cmd.contacted.values() " + str(results_add_user_cmd.contacted.values()))
    print("add_user_attributes: " + str(add_user_attributes))
    # Match the new user return codes
    assigned_omvs_uid = True if [v for v in add_user_attributes if f"User {user} was assigned an OMVS UID value" in v] else False
    create_group_rc = [v for v in add_user_attributes if f"Create {user_group} RC=" in v][0].split('=')[1].strip() or None
    add_user_rc = [v for v in add_user_attributes if f"ADDUSER {user} RC=" in v][0].split('=')[1].strip() or None
    mkdir_rc = [v for v in add_user_attributes if f"mkdir {user} RC=" in v][0].split('=')[1].strip() or None
    chown_rc = [v for v in add_user_attributes if f"chown {user} RC=" in v][0].split('=')[1].strip() or None

    # Print the RCs for validation
    print(f"assigned_omvs_uid: [{assigned_omvs_uid}]")
    print(f"create_group_rc: [{create_group_rc}]")
    print(f"add_user_rc: [{add_user_rc}]")
    print(f"mkdir_rc: [{mkdir_rc}]")
    print(f"chown_rc: [{chown_rc}]")

    # remote_host = ansible_zos_module["options"]["inventory"].replace(",", "")
    return None #operations[managed_user.name](ansible_zos_module)

    # These will serve the general purpose of our test cases
def create_user_zoau_limited_access_opercmd(ansible_zos_module) -> str:


    # tsocmd f"ADDUSER ANSUSR01 DFLTGRP(ANSIGROUP) OWNER(RACF000) PASSWORD(PASSWD) TSO(ACCTNUM(ACCT#) PROC(ISPFPROC)) OMVS(HOME('/u/fflores') PROGRAM(' bin/sh') AUTOUID "
    # _USER="usrt001"
    # SAF_PROFILE="MVS.MCSOPER.ZOAU"
    # SAF_CLASS="OPERCMDS"
    # tsocmd "RDEFINE ${SAF_CLASS} ${SAF_PROFILE} UACC(NONE) AUDIT(ALL)"
    # tsocmd "PERMIT ${SAF_PROFILE} CLASS(${SAF_CLASS}) ID(${_USER}) ACCESS(NONE)"
    # tsocmd "SETROPTS RACLIST(${SAF_CLASS}) REFRESH"
    # return None

    # Build a command from this and the below and above for a new user with limited powers.
    # To start, we can create a new group for our use.
    # ```bash
    # tsocmd "ADDGROUP ANSUSER1 OMVS(AUTOGID) "
    # ```

    # We can create a user using the following:
    # ```bash
    # tsocmd "ADDUSER fflores DFLTGRP(ANSUSER1) OWNER(SYS1) PASSWORD(RESET1A) TSO(ACCTNUM(ACCT#) PROC(ISPFPROC)) OMVS(HOME('/u/fflores') PROGRAM('/bin/sh') AUTOUID "
    # mkdir /u/fflores
    # chown fflores /u/fflores
    # chgrp ANSUSER1 /u/fflores
    # ```


    # LISTUSER USRt001 RESULTS:
    # USER=USRT001  NAME=UNKNOWN  OWNER=RACF000   CREATED=81.208
    # DEFAULT-GROUP=SYS1     PASSDATE=24.273 PASS-INTERVAL= 90 PHRASEDATE=N/A
    # ATTRIBUTES=NONE
    # REVOKE DATE=NONE   RESUME DATE=NONE
    # LAST-ACCESS=24.275/15:51:54
    # CLASS AUTHORIZATIONS=NONE
    # NO-INSTALLATION-DATA
    # NO-MODEL-NAME
    # LOGON ALLOWED   (DAYS)          (TIME)
    # ---------------------------------------------
    # ANYDAY                          ANYTIME
    # GROUP=SYS1      AUTH=USE      CONNECT-OWNER=RACF000   CONNECT-DATE=81.208
    #     CONNECTS=   900  UACC=NONE     LAST-CONNECT=24.275/15:51:54
    #     CONNECT ATTRIBUTES=NONE
    #     REVOKE DATE=NONE   RESUME DATE=NONE
    # GROUP=RAD       AUTH=USE      CONNECT-OWNER=RACF000   CONNECT-DATE=87.056
    #     CONNECTS=    00  UACC=NONE     LAST-CONNECT=UNKNOWN
    #     CONNECT ATTRIBUTES=NONE
    #     REVOKE DATE=NONE   RESUME DATE=NONE
    # GROUP=DB2       AUTH=USE      CONNECT-OWNER=USER000   CONNECT-DATE=94.287
    #     CONNECTS=    00  UACC=NONE     LAST-CONNECT=UNKNOWN
    #     CONNECT ATTRIBUTES=NONE
    #     REVOKE DATE=NONE   RESUME DATE=NONE
    # SECURITY-LEVEL=NONE SPECIFIED
    # CATEGORY-AUTHORIZATION
    # NONE SPECIFIED
    # SECURITY-LABEL=NONE SPECIFIED

    # tsocmd LISTUSER OMVSADM TSO NORACF
    # LISTUSER OMVSADM TSO NORACF
    # USER=OMVSADM

    # TSO INFORMATION
    # ---------------
    # ACCTNUM= D1001
    # PROC= TPROC02
    # SIZE= 00512000
    # MAXSIZE= 00000000
    # UNIT= SYSDA
    # USERDATA= 0000

    return "result create_user_zoau_limited_access_opercmd"

def create_user_zos_limited_hlq(ansible_zos_module) -> str:
    return "result create_user_zos_limited_hlq"

def create_user_zos_limited_tmp_hlq(ansible_zos_module) -> str:
    return "result create_user_zos_limited_tmp_hlq"

operations = {
    ManagedUsers.ZOAU_LIMITED_ACCESS_OPERCMD.name: create_user_zoau_limited_access_opercmd,
    ManagedUsers.ZOS_LIMITED_HLQ.name: create_user_zos_limited_hlq,
    ManagedUsers.ZOS_LIMITED_TMP_HLQ.name: create_user_zos_limited_tmp_hlq
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


    # tsocmd "ADDUSER fflores DFLTGRP(ANSUSER1) OWNER(SYS1) PASSWORD(RESET1A) TSO(ACCTNUM(ACCT#) PROC(ISPFPROC)) OMVS(HOME('/u/fflores') PROGRAM(' bin/sh') AUTOUID "
    # mkdir /u/fflores
    # chown fflores /u/fflores
    # chgrp ANSUSER1 /u/fflores

    # tsocmd "ADDGROUP (MISC) OWNER(OMVSADM) SUPGROUP(SYS1) DATA('HLQ STUB')"
    # tsocmd "CONNECT FFLORES GROUP(MISC)"
    # tsocmd "ADDSD 'MISC.FFLORES.*'    UACC(NONE)   DATA ('only allow to create under misc.fflores')"
    # tsocmd "PERMIT 'MISC.FFLORES.*'  CLASS(DATASET) ACCESS(ALTER) ID(FFLORES)"
    # tsocmd "SETROPTS GENERIC(DATASET) REFRESH"
    # tsocmd "LISTDSD ALL PREFIX(MISC.FFLORES)"

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
