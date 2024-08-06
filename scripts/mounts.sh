#!/bin/sh
# ==============================================================================
# Copyright (c) IBM Corporation 2022, 2023
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
# Description:
# TODO...
# Maintain:
#   zoau_mount_list_str     - zoau mount points
#   python_mount_list_str   - python mount points
#   python_path_list_str    - python executable paths
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------
#cd $(dirname $0)

script_directory=$(cd -- "$(dirname -- "$0")" 2>/dev/null && pwd)

# Depending on from where the file is sourced it can result in null so default it to .
if [ ! -n "$script_directory" ]; then
	script_directory="."
fi

cd ${script_directory}

# Current shell, bash returns 'bash'
CURR_SHELL=`echo $$ $SHELL | cut -d " " -f 2 | sed 's|.*/||'`

# System script is running on at the momement
SYSTEM=`uname`

# Array where each entry is: "<index>:<version>:<mount>:<data_set>"
ZOAU_MOUNTS=""

# Array where each entry is: "<mount>:<data_set>"
PYTHON_MOUNTS=""

# Array where each entry is: "<index>:<version>:<path>"
PYTHON_MOUNT_PATHS=""

# ZOAU matching an ZOAU ID (first column in mount table)
ZOAU_HOME=""

# PYZ matching an PYZ ID (first column in mount table)
PYZ_HOME=""

# Cosmetic divider
DIV="-----------------------------------------------------------------------"

# Supporting bash will take added testing, the port on z/OS has enough
# differences to warrnat temporarily disabliing the function on z/OS. More
# specifically, when using `vi` in Bash, editing becomes a problem.
if [ "$CURR_SHELL" = "bash" ]; then
	if [ "$SYSTEM" = "OS/390" ]; then
		echo "Script $0 can not run in 'bash', please execute in another shell."
		exit 1
	fi
fi

# ==============================================================================
#       ********************* Helper functions ********************* 
# ==============================================================================
message(){
  echo $DIV;
	echo "$1";
  echo $DIV;
}

# ------------------------------------------------------------------------------
# Private function that initializes an array ($1) from a properly delimited
# string. Array types supported are either Korn Shell (ksh) (more precisely,
# ksh88 and ksh93 variants) or Bash style.
# More on ksh arrays: https://docstore.mik.ua/orelly/unix3/korn/ch06_04.htm
# Other shells may need to be supported in the future.
# GLOBAL:   See arguments $1
# ARGUMENTS:
# 	- $1 (variable) a global var that will be unset and initialized as an array
#   - $2 (string) a string delimited by spaces (' ') and entries delimited by a
#        colon (':'). This string is used to create set an array.
# OUTPUTS:  None
# RETURN:   None
# USAGE:    _set_shell_array <var> <string>
# ------------------------------------------------------------------------------
_set_shell_array(){
	# Notes:
    # ksh is hard to detect on z/OS, for now comparing to `sh` works else we can
    # add in the results for `echo $PS1;  echo $PS2;  echo $PS3;  echo $PS4`
    # which returns in this order ('#', '>', '#?', '+') to detect `sh`
    unset $1
    if [ "$CURR_SHELL" = "sh" ]; then
        # set -A $1 "${@:2}" # parens `{` don't work in z/OS ksh, work on mac
        set -A $1 $2
    else
        #eval $1='("${@:2}")'
       eval $1='(${@:2})'
    fi
}

# ------------------------------------------------------------------------------
# Source scripts needed by this script.
# ------------------------------------------------------------------------------

if [ -f "mounts.env" ]; then
	. ./mounts.env
else
    echo "Unable to source file: 'mounts.env', exiting."
	exit 1
fi

# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------
# _set_shell_array(){
#     # ksh is hard to detect, for now comparing to `sh` works else we can
#     # add in the results for `echo $PS1;  echo $PS2;  echo $PS3;  echo $PS4`
#     # which returns in this order ('#', '>', '#?', '+') to detect `sh`
#     if [ "$CURR_SHELL" = "sh" ]; then
#         # set -A $1 "${@:2}" # parens `{` don't work in z/OS ksh, work on mac
#         set -A $1 $2
#     else
#         eval $1='(${@:2})'
#     fi
# }

# ------------------------------------------------------------------------------
# Normalize the array for the shell use, creates an array capatible for `ksh`
# or `bash` from the mount tables; this allows a single source of data to be
# used in various shells.
# Creats a normalized array `PYTHON_MOUNTS`, `ZOAU_MOUNTS`
# ------------------------------------------------------------------------------
# set_python_to_array(){
#     unset PYTHON_MOUNTS
#     _set_shell_array PYTHON_MOUNTS "$(echo $python_mount_list_str)"
# }

# set_zoau_to_array(){
#     unset ZOAU_MOUNTS
#     _set_shell_array ZOAU_MOUNTS "$(echo $zoau_mount_list_str)"
# }

# ------------------------------------------------------------------------------
# Normalize an array for the shell use, create an array capatible for `ksh`
# or `bash` from the mount tables; this allows a single source of data to be
# used in various shells. Initializes a global array `ZOAU_MOUNTS` where each
# index contains a clolon `:` delimited values about ZOAU mounts. For example
# ZOAU_MOUNTS[0] has in it <index>:<version>:<mount>:<data_set> where that may
# look like "1:v1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS", see sourced script
# `mounts.env` for more information.
# GLOBAL:       ZOAU_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_zoau_mounts
# ------------------------------------------------------------------------------
set_zoau_mounts(){
    unset ZOAU_MOUNTS
    _set_shell_array ZOAU_MOUNTS "$(echo $zoau_mount_list_str)"
}

# ------------------------------------------------------------------------------
# Normalize an array for the shell use, create an array capatible for `ksh`
# or `bash` from the mount tables; this allows a single source of data to be
# used in various shells. Initializes a global array `PYTHON_MOUNTS` where each
# index contains clolon `:` delimited values about PYTHON mounts. For example
# PYTHON_MOUNTS[0] has in it <index>:<version>:<mount>:<data_set> where that may
# look like "4:3.10:/allpython/3.10/usr/lpp/IBM/cyp/v3r10:IMSTESTU.PYZ.V3A0.ZFS ",
# see sourced script `mounts.env` for more information.
# GLOBAL:       PYTHON_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_python_mounts
# ------------------------------------------------------------------------------
set_python_mounts(){
    unset PYTHON_MOUNTS
    _set_shell_array PYTHON_MOUNTS "$(echo $python_mount_list_str)"
}

# ------------------------------------------------------------------------------
# Normalize an array for the shell use, create an array capatible for `ksh`
# or `bash` from the mount tables; this allows a single source of data to be
# used in various shells. Initializes a global array `PYTHON_MOUNT_PATHS` where each
# index contains clolon `:` delimited values about PYTHON paths. For example
# PYTHON_MOUNT_PATHS[0] has in it <index>:<version>:<path><space> where that may
# look like "1:3.8:/python3/usr/lpp/IBM/cyp/v3r8/pyz ",
# see sourced script `mounts.env` for more information.
# GLOBAL:
#   ZOAU_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_python_mount_paths
# ------------------------------------------------------------------------------
set_python_mount_paths(){
    unset PYTHON_MOUNT_PATHS
    _set_shell_array PYTHON_MOUNT_PATHS "$(echo $python_path_list_str)"
}

# ==============================================================================
#       ********************* Mount functions *********************
# ==============================================================================

# ------------------------------------------------------------------------------
# Mount all data sets in the sourced mount table, check if the entries are
# already mounted, compare that to the data set being mounted, if they don't
# match, umount and mount the correct one else skip over it.
#
# GLOBAL:   See arguments $1
# ARGUMENTS:
# 	- $1 (variable) a global var that will be unset and initialized as an array
#   - $2 (string) a string delimited by spaces used to create a global array
# OUTPUTS:  None
# RETURN:   None
# USAGE:    _set_shell_array <var> <string>
# ------------------------------------------------------------------------------
mount(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set

	# Call helper script to have ZOAU_MOUNTS generated
	set_zoau_mounts
    for tgt in "${ZOAU_MOUNTS[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		# zoau_mounted_data_set can be empty so perform added validation
		zoau_mounted_data_set=`df ${zoau_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`

		# If zoau_mounted_data_set is empty or does not match expected, it means we should perform the mount
		if [ "$zoau_mounted_data_set" != "$zoau_data_set" ]; then
			# If zoau_mounted_data_set not empty, compare the mount points and if they match, then continue below
			if [ ! -z "${zoau_mounted_data_set}" ]; then
				temp_mount=`df ${zoau_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 1`

				# If zoau_mount is mounted to a different data set it means there has been a mount table update
				# and it should be remounted with the new data set.
				if [ "${zoau_mounted_data_set}" != "${zoau_data_set}" ]; then
					# If the data set is mounted elsewhere, it needs to be unmounted so the mount command can succeed,
					# thus zoau_to_unmount will eval to where the zoau_data_set might be mounted.
					zoau_to_unmount=`df |grep ${zoau_data_set} | cut -d' ' -f 1`
					if [ ! -z "${zoau_to_unmount}" ]; then
						echo "Unmouting path ${zoau_to_unmount} from data set ${zoau_data_set} so that the data set can be mounted to ${zoau_mount}."
						/usr/sbin/unmount ${zoau_to_unmount} 2>/dev/null
					fi
				fi

				# If the mount points match then unmount so that a mount can be performed because it could mean the
				# data set has been refreshed.
				if [ "${zoau_mount}" = "${temp_mount}" ]; then
					# If you try to unmount / because that is where zoau_mount evals to currently, consume the error
					echo "Unmouting path ${zoau_mount} from data set ${zoau_data_set} so that the mount point can be refreshed with the data set."
					/usr/sbin/unmount ${zoau_mount} 2>/dev/null
				fi
			fi
			echo "Mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount ${1} ${zoau_data_set} ${zoau_mount}
		else
			echo "ZOAU ${zoau_version} is already mounted on data set ${zoau_data_set} to path ${zoau_mount}."
		fi
    done

	unset python_mount
	unset python_data_set
	# Call helper script to have PYTHON_MOUNTS generated
	set_python_mounts
    for tgt in "${PYTHON_MOUNTS[@]}" ; do
		python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
		python_home=`echo "${tgt}" | cut -d ":" -f 3`
        python_mount=`echo "${tgt}" | cut -d ":" -f 4`
		python_data_set=`echo "${tgt}" | cut -d ":" -f 5`

		# python_mounted_data_set can be empty so perform added validation
		python_mounted_data_set=`df ${python_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`

		# If python_mounted_data_set is empty or not, we will perform a mount
		if [ "$python_mounted_data_set" != "$python_data_set" ]; then
			echo "Mouting Python ${python_mount} on data set ${python_data_set}."

			# If python_mounted_data_set not empty, compare the mount points and if they match, then unmount.
			# Note, the mount point could be root (/) waitng for children so lets compare before unmounting.
			if [ ! -z "${python_mounted_data_set}" ]; then
				temp_mount=`df ${python_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 1`
				if [ "${python_mount}" = "${temp_mount}" ]; then
					/usr/sbin/unmount ${python_mount}
				fi
			fi

			mkdir -p ${python_mount}
        	/usr/sbin/mount ${1} ${python_data_set} ${python_mount}
		else
			echo "Python ${python_mount} is already mounted on data set ${python_data_set}."
		fi
    done
}

# ------------------------------------------------------------------------------
# Unmount all data sets in the sourced mount table.
# ------------------------------------------------------------------------------
unmount(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
	# Call helper script to have ZOAU_MOUNTS generated
	set_zoau_mounts
    for tgt in "${ZOAU_MOUNTS[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		zoau_mounted_data_set=`df ${zoau_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		if [ "$zoau_mounted_data_set" = "$zoau_data_set" ]; then
			echo "Unmouting ZOAU ${zoau_version} on data set ${zoau_data_set} from path ${zoau_mount}."
			/usr/sbin/unmount ${zoau_mount}
		else
			echo "ZOAU ${zoau_version} is not currently mounted on data set ${zoau_data_set} to path ${zoau_mount}."
		fi
    done

	unset python_mount
	unset python_data_set
	# Call helper script to have PYTHON_MOUNTS generated
	set_python_to_array
    for tgt in "${PYTHON_MOUNTS[@]}" ; do
		python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
		python_home=`echo "${tgt}" | cut -d ":" -f 3`
        python_mount=`echo "${tgt}" | cut -d ":" -f 4`
		python_data_set=`echo "${tgt}" | cut -d ":" -f 5`

		python_mounted_data_set=`df ${python_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		if [ "$python_mounted_data_set" = "$python_data_set" ]; then
			echo "Unmouting Python ${python_mount} on data set ${python_data_set}."
			/usr/sbin/unmount ${python_mount}
		else
			echo "Python ${python_mount} is not currently mounted on data set ${python_data_set}."
		fi
    done
}

# ------------------------------------------------------------------------------
# Remount all data sets sourced in the mount table, check if there is something
# already mounted, compare that to the data set being mounted, if they don't
# match, umount and mount the correct one else skip over it.
# ------------------------------------------------------------------------------
remount(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
	# Call helper script to have ZOAU_MOUNTS generated
	set_zoau_mounts
    for tgt in "${ZOAU_MOUNTS[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		zoau_mounted_data_set=`df ${zoau_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		# ZOAU is not mounted, perform mount
		if [ ! -n "$zoau_mounted_data_set" ]; then
			echo "Nothing to unmount, mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount -r -t zfs -f ${zoau_data_set} ${zoau_mount}
		# ZOAU is currently mounted and matches what we expect
		elif [ "$zoau_mounted_data_set" = "$zoau_data_set" ]; then
			echo "Unmounting ZOAU ${zoau_version} from path ${zoau_mount} on data set ${zoau_data_set}."
			/usr/sbin/unmount ${zoau_mount}
			echo "Mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount -r -t zfs -f ${zoau_data_set} ${zoau_mount}
		# What is mounted does not match our expected value, perform unmount and mount
		elif [ "$zoau_mounted_data_set" != "$zoau_data_set" ]; then
		    echo "WARNING: Overriding existing mount ${python_mount}."
			echo "Unmounting data set ${zoau_mounted_data_set} from path ${zoau_mount}."
			/usr/sbin/unmount ${zoau_mount}
			echo "Mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount -r -t zfs -f ${zoau_data_set} ${zoau_mount}
		else
			echo "Unable to determine the existing mounts to remount."
		fi
    done

	unset python_mount
	unset python_data_set
	# Call helper script to have PYTHON_MOUNTS generated
	set_python_to_array
    for tgt in "${PYTHON_MOUNTS[@]}" ; do
		python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
		python_home=`echo "${tgt}" | cut -d ":" -f 3`
        python_mount=`echo "${tgt}" | cut -d ":" -f 4`
		python_data_set=`echo "${tgt}" | cut -d ":" -f 5`

		python_mounted_data_set=`df ${python_mount} 2>/dev/null | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		# Pythion is not mounted, perform mount
		if [ ! -n "$python_mounted_data_set" ]; then
			echo "Nothing to unmount, mouting Python ${python_version} on data set ${python_data_set} to path ${python_mount}."
			mkdir -p ${python_mount}
        	/usr/sbin/mount -r -t zfs -f ${python_data_set} ${python_mount}
		#Python is currently mounted and matches what we expect
		elif [ "$python_mounted_data_set" = "$python_data_set" ]; then
			echo "Unmounting Python ${python_version} from path ${python_mount} on data set ${python_data_set}."
			/usr/sbin/unmount ${python_mount}
			echo "Mouting Python ${python_version} on data set ${python_data_set} to path ${python_mount}."
			mkdir -p ${python_mount}
        	/usr/sbin/mount -r -t zfs -f ${python_data_set} ${python_mount}
		# What is mounted does not match our expected value, perform unmount and mount
		elif [ "$python_mounted_data_set" != "$python_data_set" ]; then
		    echo "WARNING: Overriding existing mount ${python_mount}."
			echo "Unmounting data set ${python_mounted_data_set} from path ${python_mount}."
			/usr/sbin/unmount ${python_mount}
			echo "Mouting Python ${python_version} on data set ${python_data_set} to path ${python_mount}."
			mkdir -p ${python_mount}
        	/usr/sbin/mount -r -t zfs -f ${python_data_set} ${python_mount}
		else
			echo "Unable to determine the existing mounts to remount."
		fi
    done
}


# ==============================================================================
#       ********************* Getter functions *********************
# ==============================================================================

get_python_mount(){

	arg=$1
	unset PYZ_HOME
	unset python_version
	unset python_home

	# Set PYZ mount table to shell array types
	set_python_mounts

    for tgt in "${PYTHON_MOUNTS[@]}" ; do
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
        python_home=`echo "${tgt}" | cut -d ":" -f 3`

		if [ "$arg" = "$python_version" ]; then
			PYZ_HOME=$python_home
		fi

    done

	if [ ! "$PYZ_HOME" ]; then
		echo "PYZ vesion [$arg] was not found in the mount table."
		exit 1
	fi

	echo "${PYZ_HOME}"
}


# Get the zoau home/path given $1/arg else error
get_zoau_mount(){
	arg=$1
	unset ZOAU_HOME
	unset zoau_version
	unset zoau_mount

	# Set ZOAU mount table to shell array types
	set_zoau_mounts

    for tgt in "${ZOAU_MOUNTS[@]}" ; do
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`

		if [ "$arg" = "$zoau_version" ]; then
			ZOAU_HOME=$zoau_mount
		fi

    done

	if [ ! "$ZOAU_HOME" ]; then
		echo "ZOAU vesion [$arg] was not found in the mount table."
		exit 1
	fi

	echo "${ZOAU_HOME}"
}

# ==============================================================================
#       ********************* Print functions *********************
# ==============================================================================

# ------------------------------------------------------------------------------
# Print python and zoau mount tables
# ------------------------------------------------------------------------------
print_mount_tables(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set

	set_zoau_mounts

	message "Displaying z/OS Python ZOAU table."
    for tgt in "${ZOAU_MOUNTS[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		echo "ID:" $zoau_index
		echo "  Version:" $zoau_version
		echo "  Home:" $zoau_mount
		echo "  Mount:" $zoau_data_set

    done

	unset python_index
	unset python_version
	unset python_home
	unset python_mount
	unset python_data_set

	set_python_mounts

	message "Displaying z/OS Python mount table."
    for tgt in "${PYTHON_MOUNTS[@]}" ; do
		python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
		python_home=`echo "${tgt}" | cut -d ":" -f 3`
        python_mount=`echo "${tgt}" | cut -d ":" -f 4`
		python_data_set=`echo "${tgt}" | cut -d ":" -f 5`

		echo "ID:" $python_index
		echo "  Version:" $python_version
		echo "  Home:" $python_home
		echo "  Mount:" $python_mount
		echo "  Data Set:" $python_data_set
    done

	unset python_index
	unset python_version
	unset python_path
	set_python_mount_paths
	message "Displaying z/OS Python path for 'pyz'"
    for tgt in "${PYTHON_MOUNTS[@]}" ; do
		python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
		python_path=`echo "${tgt}" | cut -d ":" -f 3`

		echo "ID:" $python_index
		echo "  Version:" $python_version
		echo "  Path:" $python_path
    done

}


# ==============================================================================
#       ********************* Test functions *********************
# ==============================================================================

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

################################################################################
# Main arg parser
################################################################################
case "$1" in
  --get-python-mount)
    get_python_mount $2
    ;;
  --get-zoau-mount)
    get_zoau_mount $2
    ;;
  --mount)
    mount "-r -t zfs -f"
    ;;
  --mount-rw)
  	unmount
    mount "-t zfs -f"
    ;;
  --unmount)
    unmount
    ;;
  --remount)
	remount
    ;;
  --print-mount-tables)
    print_mount_tables
	;;
   --perform-unit-test)
    _test_arrays
    ;;
   --val)
    	get_zoau_mount "1.2.1"
		get_python_mount "3.10"
		echo $ZOAU_HOME
		echo $PYZ_HOME
    ;;
  *)
   # If $1 exists and the script matches to $0 because when sourced this would
   # thrown error and the added check is to prevent the errors when sourced.
   if [ -n "$1" ]; then
      if [ "$0" = "mounts-datasets.sh" ]; then
         echo "ERROR: unknown parameter $1 for script $0"
      fi
   fi
esac

