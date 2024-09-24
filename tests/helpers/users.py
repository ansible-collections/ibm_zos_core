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
from enum import Enum
import json
from __future__ import annotations
from typing import Annotated

class ManagedUsers (Enum):
    zoau_limited_access_opercmd=("zoau_limited_access_opercmd")
    """
    A z/OS managed user with restricted access to ZOAU
    SAF Profile 'MVS..MCSOPER.ZOAU' and SAF Class OPERCMDS
    with universal access authority set to UACC(NONE). With
    UACC as NONE, this user will be refused access to the
    ZOAU opercmd utility.
    """
    zos_limited_hlq=("zos_limited_hlq")
    """
    A z/OS managed user with restricted access to High Level
    Qualifiers (HLQ): (RESTRICT, NOPERMIT, ....).
    """

    zos_limited_tmp_hlq=("zos_limited_tmp_hlq")
    """
    A z/OS managed user with restricted access to temporary
    High Level Qualifiers (HLQ): (TSTRICT, TNOPERM, ....).
    """

class Racf:
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

    # get_user(ENUM)
    # Check if the user exist 
    # # lookup enum call right method 
    # return get_zoau_limited_access_opercmd


    # These will serve the general purpose of our test cases
    def get_zoau_limited_access_opercmd() -> str:
    # _USER="usrt001"
    # SAF_PROFILE="MVS.MCSOPER.ZOAU"
    # SAF_CLASS="OPERCMDS"
    # tsocmd "RDEFINE ${SAF_CLASS} ${SAF_PROFILE} UACC(NONE) AUDIT(ALL)"
    # tsocmd "PERMIT ${SAF_PROFILE} CLASS(${SAF_CLASS}) ID(${_USER}) ACCESS(NONE)"
    # tsocmd "SETROPTS RACLIST(${SAF_CLASS}) REFRESH"
    # return None


if __name__ == '__main__':
    racf = Racf()
    adduser = Racf.Adduser()
