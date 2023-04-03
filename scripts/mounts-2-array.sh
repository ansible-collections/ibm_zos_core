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
# Source the known mount points
# ------------------------------------------------------------------------------
. ./mounts.sh

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
# Private function that initializes a variable as an global array for either
# Korn Shell (ksh) or other shells where other at this point is following
# bash style arrays. Other shells may need to be supported in the future.
#
# GLOBAL:   See arguments $1
# ARGUMENTS:
# 	- $1 (variable) a global var that will be unset and initialized as an array
#   - $2 (string) a string delimited by spaces used to create a global array
# OUTPUTS:  None
# RETURN:   None
# USAGE:    _set_shell_array <var> <string>
# ==============================================================================
_set_shell_array(){
    # ksh is hard to detect, for now comparing to `sh` works else we can
    # add in the results for `echo $PS1;  echo $PS2;  echo $PS3;  echo $PS4`
    # which returns in this order ('#', '>', '#?', '+') to detect `sh`
    if [ "$CURR_SHELL" = "sh" ]; then
        # set -A $1 "${@:2}" # parens `{` don't work in z/OS ksh, work on mac
        set -A $1 $2
    else
        eval $1='(${@:2})'
    fi
}

# ==============================================================================
# Public function that initializes a global array `ZOAU_MOUNTS` where each index
# contains clolon `:` delimited values about ZOAU mounts. For example
# ZOAU_MOUNTS[0] has in it <index>:<version>:<mount>:<data_set> where that may
# look like "1:v1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS", see sourced script
# `mounts.sh` for more information.
# GLOBAL:       ZOAU_MOUNTS
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
# Public function that initializes a global array `PYTHON_MOUNTS` where each
# index contains clolon `:` delimited values about PYTHON mounts. For example
# PYTHON_MOUNTS[0] has in it <index>:<version>:<mount>:<data_set> where that may
# look like "4:3.10:/allpython/3.10/usr/lpp/IBM/cyp/v3r10:IMSTESTU.PYZ.V3A0.ZFS ",
# see sourced script `mounts.sh` for more information.
# GLOBAL:       PYTHON_MOUNTS
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
# I think we can sunset this code now that the mounts have changed
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
# Simple method to test arrays, test automation should be designed but this
# serves as a lightweight verification test
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
   # If $1 exists and the script matches to $0 because when sourced this would
   # thrown error and the added check is to prevent the errors when sourced.
   if [ -n "$1" ]; then
      if [ "$0" = "mounts-to-array.sh" ]; then
         echo "ERROR: unknown parameter $1 for script $0"
      fi
   fi
esac
