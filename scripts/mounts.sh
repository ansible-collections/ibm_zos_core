    # ==============================================================================
    # Copyright (c) IBM Corporation 2023
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #     http://www.apache.org/licenses/LICENSE-2.0
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    # ==============================================================================

    # ==============================================================================
    # KSH (Korn Shell) Array of mounts index delimited by " ", etries delimited by ":"
    # More on ksh arrays: https://docstore.mik.ua/orelly/unix3/korn/ch06_04.htm
    # This `mounts.sh` is sourced by serveral other files, only these lists needs to
    # be maintained.
    # ==============================================================================

    # ------------------------------------------------------------------------------
    # zoau_mount_list[0]="<index>:<version>:<mount>:<data_set>"
    #   e.g: zoau_mount_list[0]="1:v1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS"
    # Format:
    #   index   - used by the generated profile so a user can select an option
    #   version    - describes the option a user can select
    #   mount - the mount point path the data set will be mounted to
    #   data_set - the z/OS data set containing the binaries to mount
    # ------------------------------------------------------------------------------
    set -A zoau_mount_list "1:1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS" \
    "2:1.0.0-ga:/zoau/v1.0.0-ga:IMSTESTU.ZOAU.V100.GA.ZFS" \
    "3:1.0.1-ga:/zoau/v1.0.1-ga:IMSTESTU.ZOAU.V101.GA.ZFS" \
    "4:1.0.1-ptf1:/zoau/v1.0.1-ptf1:IMSTESTU.ZOAU.V101.PTF1.ZFS" \
    "5:1.0.1-ptf2:/zoau/v1.0.1-ptf2:IMSTESTU.ZOAU.V101.PTF2.ZFS" \
    "6:1.0.2-ga:/zoau/v1.0.2-ga:IMSTESTU.ZOAU.V102.GA.ZFS" \
    "7:1.0.3-ga5:/zoau/v1.0.3-ga5:IMSTESTU.ZOAU.V103.GA5.ZFS" \
    "8:1.0.3-ptf2:/zoau/v1.0.3-ptf2:IMSTESTU.ZOAU.V103.PTF2.ZFS" \
    "9:1.1.0-spr:/zoau/v1.1.0-spr:IMSTESTU.ZOAU.V110.SPRINT.ZFS" \
    "10:1.1.0-spr5:/zoau/v1.1.0-spr5:IMSTESTU.ZOAU.V1105.SPRINT.ZFS" \
    "11:1.1.0-spr7:/zoau/v1.1.0-spr7:IMSTESTU.ZOAU.V1107.SPRINT.ZFS" \
    "12:1.1.0-ga:/zoau/v1.1.0-ga:IMSTESTU.ZOAU.V110.GA.ZFS" \
    "13:1.1.1-ptf1:/zoau/v1.1.1-ptf1:IMSTESTU.ZOAU.V111.PTF1.ZFS" \
    "14:1.2.0f:/zoau/v1.2.0f:IMSTESTU.ZOAU.V120F.ZFS" \
    "15:1.2.1:/zoau/v1.2.1:IMSTESTU.ZOAU.V121.ZFS" \
    "16:1.2.1-rc1:/zoau/v1.2.1-rc1:IMSTESTU.ZOAU.V121.RC1.ZFS" \
    "17:1.2.1g:/zoau/v1.2.1g:IMSTESTU.ZOAU.V121G.ZFS" \
    "18:1.2.1h:/zoau/v1.2.1h:IMSTESTU.ZOAU.V121H.ZFS" \
    "19:1.2.2:/zoau/v1.2.2:IMSTESTU.ZOAU.V122.ZFS" \
    "20:latest:/zoau/latest:IMSTESTU.ZOAU.LATEST.ZFS"

    # ------------------------------------------------------------------------------
    # python_mount_list[0]="<mount>:<data_set>"
    # python_mount_list[0]="/python2:IMSTESTU.PYZ.ROCKET.V362B.ZFS"
    # ------------------------------------------------------------------------------
    set -A python_mount_list "/python:IMSTESTU.PYZ.ROCKET.V362B.ZFS" \
    "/python2:IMSTESTU.PYZ.V380.GA.ZFS" \
    "/python3:IMSTESTU.PYZ.V383PLUS.ZFS" \
    "/allpython/3.10:IMSTESTU.PYZ.V3A0.ZFS" \
    "/allpython/3.11:IMSTESTU.PYZ.V3B0.ZFS" \
    "/allpython/3.11-ga:IMSTESTU.PYZ.V311GA.ZFS"

    # ------------------------------------------------------------------------------
    # python_path_list[0]="<index>:<version>:<path>"
    # python_path_list[0]="1:3.8:/python3/usr/lpp/IBM/cyp/v3r8/pyz"
    # ------------------------------------------------------------------------------
    set -A python_path_list "1:3.8:/python3/usr/lpp/IBM/cyp/v3r8/pyz" \
    "2:3.9:/python2/usr/lpp/IBM/cyp/v3r9/pyz" \
    "3:3.10:/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz" \
    "4:3.11:/allpython/3.11-ga/usr/lpp/IBM/cyp/v3r11/pyz"

