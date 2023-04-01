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
# This script supports both KSH (Korn Shell) and bash, more precisely ksh88
# ksh93 variants.
# Array delimited by " ", etries delimited by ":"
# More on ksh arrays: https://docstore.mik.ua/orelly/unix3/korn/ch06_04.htm
# Script `mounts.sh` is sourced by serveral other files.
# ==============================================================================

# ------------------------------------------------------------------------------
# Source the known mount points
# ------------------------------------------------------------------------------
. ./mounts.sh

# ==============================================================================
# Globals
# ==============================================================================

# Current shell, bash returns 'bash'
CURR_SHELL=`echo $$ $SHELL | cut -d " " -f 2 | sed 's|.*/||'`

# Array where each entry is: "<index>:<version>:<mount>:<data_set>"
export ZOAU_MOUNTS=""

# Array where each entry is: "<mount>:<data_set>"
export PYTHON_MOUNTS=""

# Array where each entry is: "<index>:<version>:<path>"
export PYTHON_MOUNT_PATHS=""

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
# GLOBAL:       ZOAU_MOUNTS
# ARGUMENTS:    (str) zoau_mount_list_str
# OUTPUTS:      None
# RETURN:       None
# USAGE:        _set_shell_array ZOAU_MOUNTS "$(echo $zoau_mount_list_str)"
# ==============================================================================
set_zoau_mounts(){
    unset ZOAU_MOUNTS
    _set_shell_array ZOAU_MOUNTS "$(echo $zoau_mount_list_str)"

}

# ==============================================================================
# Initialize global variable PYTHON_MOUNTS as an array for the specific shell
# the script is executed in (ksh, bash, etc)
# GLOBAL:       PYTHON_MOUNTS
# ARGUMENTS:    (str) python_mount_list_str
# OUTPUTS:      None
# RETURN:       None
# USAGE:        _set_shell_array PYTHON_MOUNTS "$(echo $python_mount_list_str)"
# ==============================================================================
set_python_mounts(){
    unset PYTHON_MOUNTS
    _set_shell_array PYTHON_MOUNTS "$(echo $python_mount_list_str)"
}

# ==============================================================================
# Initialize global variable PYTHON_MOUNT_PATHS as an array for the specific shell
# the script is executed in (ksh, bash, etc)
# GLOBAL:       PYTHON_MOUNT_PATHS
# ARGUMENTS:    (str) python_path_list_str
# OUTPUTS:      None
# RETURN:       None
# USAGE:        _set_shell_array PYTHON_MOUNT_PATHS "$(echo $python_path_list_str)"
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
echo "Python path 3 is:"
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
