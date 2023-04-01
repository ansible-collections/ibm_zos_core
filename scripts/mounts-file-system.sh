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

# ------------------------------------------------------------------------------
# zoau_mount_list[0]="<index>:<version>:<mount>:<data_set><space>"
#   e.g: zoau_mount_list[0]="1:v1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS "
# Format:
#   index   - used by the generated profile so a user can select an option
#   version    - describes the option a user can select
#   mount - the mount point path the data set will be mounted to
#   data_set - the z/OS data set containing the binaries to mount
#   space - must be a space before the closing quote
# ------------------------------------------------------------------------------
zoau_mount_list_str="1:1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS "\
"2:1.0.0-ga:/zoau/v1.0.0-ga:IMSTESTU.ZOAU.V100.GA.ZFS "\
"3:1.0.1-ga:/zoau/v1.0.1-ga:IMSTESTU.ZOAU.V101.GA.ZFS "\
"6:1.0.2-ga:/zoau/v1.0.2-ga:IMSTESTU.ZOAU.V102.GA.ZFS "\
"7:1.0.3-ga5:/zoau/v1.0.3-ga5:IMSTESTU.ZOAU.V103.GA5.ZFS "\
"8:1.0.3-ptf2:/zoau/v1.0.3-ptf2:IMSTESTU.ZOAU.V103.PTF2.ZFS "\
"12:1.1.0-ga:/zoau/v1.1.0-ga:IMSTESTU.ZOAU.V110.GA.ZFS "\
"13:1.1.1-ptf1:/zoau/v1.1.1-ptf1:IMSTESTU.ZOAU.V111.PTF1.ZFS "\
"15:1.2.1:/zoau/v1.2.1:IMSTESTU.ZOAU.V121.ZFS "\
"19:1.2.2:/zoau/v1.2.2:IMSTESTU.ZOAU.V122.ZFS "\
"20:latest:/zoau/latest:IMSTESTU.ZOAU.LATEST.ZFS "

# ------------------------------------------------------------------------------
# python_mount_list[0]="<mount>:<data_set><space>"
# python_mount_list[0]="/python2:IMSTESTU.PYZ.ROCKET.V362B.ZFS "
# Format:
#   mount - the mount point path the data set will be mounted to
#   data_set - the z/OS data set containing the binaries to mount
#   space - must be a space before the closing quote
# Mismarked: "/allpython/3.8.5:IMSTESTU.PYZ.V380.GA.ZFS "\
# ------------------------------------------------------------------------------
python_mount_list_str="/allpython/3.8.2:IMSTESTU.PYZ.ROCKET.V362B.ZFS "\
"/allpython/3.8.3:IMSTESTU.PYZ.V383PLUS.ZFS "\
"/allpython/3.9:IMSTESTU.PYZ.V380.GA.ZFS "\
"/allpython/3.10:IMSTESTU.PYZ.V3A0.ZFS "\
"/allpython/3.11:IMSTESTU.PYZ.V3B0.ZFS "\
"/allpython/3.11-ga:IMSTESTU.PYZ.V311GA.ZFS "

# ------------------------------------------------------------------------------
# python_path_list[0]="<index>:<version>:<path><space>"
# python_path_list[0]="1:3.8:/python3/usr/lpp/IBM/cyp/v3r8/pyz "
# Format:
#   index   - used by the generated profile so a user can select an option
#   version    - describes the option a user can select
#   path - the path where a particular python can be found
#   space - must be a space before the closing quote
# ------------------------------------------------------------------------------
python_path_list_str="1:3.8.2:/allpython/3.8.2/usr/lpp/IBM/cyp/v3r8/pyz "\
"2:3.8.3:/allpython/3.8.3/usr/lpp/IBM/cyp/v3r8/pyz "\
"3:3.9:/allpython/3.9/usr/lpp/IBM/cyp/v3r9/pyz "\
"4:3.10:/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz "\
"5:3.11:/allpython/3.11/usr/lpp/IBM/cyp/v3r11/pyz "\
"6:3.11:/allpython/3.11-ga/usr/lpp/IBM/cyp/v3r11/pyz "

# ==============================================================================
# ****************** There is no need to edit below this point *****************
# ==============================================================================

# ==============================================================================
# This script supports both KSH (Korn Shell) and bash, more precisely ksh88
# ksh93 variants.
#  Array delimited by " ", etries delimited by ":"
# More on ksh arrays: https://docstore.mik.ua/orelly/unix3/korn/ch06_04.htm
# Script `mounts.sh` is sourced by serveral other files.
# Maintain:
#   zoau_mount_list_str     - zoau mount points
#   python_mount_list_str   - python mount points
#   python_path_list_str    - python executable paths
# ==============================================================================

# ==============================================================================
# Globals
# ==============================================================================

# Current shell, bash returns 'bash'
CURR_SHELL=`echo $$ $SHELL | cut -d " " -f 2 | sed 's|.*/||'`

# Array where each entry is: "<index>:<version>:<mount>:<data_set>"
ZOAU_MOUNTS=""

# Array where each entry is: "<mount>:<data_set>"
PYTHON_MOUNTS=""

# Array where each entry is: "<index>:<version>:<path>"
PYTHON_MOUNT_PATHS=""

# ==============================================================================
# Initializes a variable as an array for either Korn Shell (ksh) or other where
# other at this point is following bash style arrays.
# Other shells may need to be supported in the future.
# Private function
# GLOBAL:
#   See arguments
# ARGUMENTS:
# 	A global var that can can be unset and initialized with a string delimited
#   with spaces to create an array
# OUTPUTS:  None
# RETURN:   None
# USAGE:
#   _set_shell_array <var> <string>
# ==============================================================================
_set_shell_array(){
    # ksh is hard to detect, for now comparing to `sh` works else we can
    # add in the results for `echo $PS1;  echo $PS2;  echo $PS3;  echo $PS4`
    # which returns in this order '#', '>', '#?', '+'.
    if [ "$CURR_SHELL" = "sh" ]; then
        # set -A $1 "${@:2}" # `{` don't work in z/OS ksh use a string
        #set -A $1 $2
        #set -A $1 "${@:2}" # woks on mac ksh
        set -A $1 $2
    else
        eval $1='(${@:2})'
    fi
}

# ==============================================================================
# Initialize global variable ZOAU_MOUNTS as an array for the specific shell
# the script is executed in (ksh, bash, etc)
# GLOBAL:
#   ZOAU_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_zoau_mounts
# ==============================================================================
set_zoau_mounts(){
    unset ZOAU_MOUNTS
    _set_shell_array ZOAU_MOUNTS "$(echo $zoau_mount_list_str)"

}

# ==============================================================================
# Initialize global variable PYTHON_MOUNTS as an array for the specific shell
# the script is executed in (ksh, bash, etc)
# GLOBAL:
#   ZOAU_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_python_mounts
# ==============================================================================
set_python_mounts(){
    unset PYTHON_MOUNTS
    _set_shell_array PYTHON_MOUNTS "$(echo $python_mount_list_str)"
}

# ==============================================================================
# Initialize global variable PYTHON_MOUNT_PATHS as an array for the specific shell
# the script is executed in (ksh, bash, etc)
# GLOBAL:
#   ZOAU_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_python_mount_paths
# ==============================================================================
set_python_mount_paths(){
    unset PYTHON_MOUNT_PATHS
    _set_shell_array PYTHON_MOUNT_PATHS "$(echo $python_path_list_str)"
}

# ==============================================================================
# Simple main to test arrays
# GLOBAL:       None
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        _test_arrays
# ==============================================================================
_test_arrays(){
echo "Current shell is: $CURR_SHELL"

set_zoau_mounts
echo ""
echo "All ZOAU mounts are:"
echo ${ZOAU_MOUNTS[@]}
echo "ZOAU mount 3 is:"
echo ${ZOAU_MOUNTS[3]}

set_python_mounts
echo ""
echo "All Python mounts are:"
echo ${PYTHON_MOUNTS[@]}
echo "Python mount 3 is:"
echo ${PYTHON_MOUNTS[3]}

set_python_mount_paths
echo ""
echo "All Python paths are:"
echo ${PYTHON_MOUNT_PATHS[@]}
echo "Python path 3:"
echo ${PYTHON_MOUNT_PATHS[3]}
}

# ==============================================================================
# Main
# ==============================================================================
#_test_arrays
case "$1" in
--set_zoau)
    set_zoau_mounts
    ;;
--set_python)
    set_python_mounts
    set_python_mount_paths
    ;;
--set_all)
	set_zoau_mounts
    set_python_mounts
    set_python_mount_paths
    ;;
--perform_unit_test)
    _test_arrays
    ;;
*)
    echo "ERROR: unknown parameter $1"
    ;;
esac