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
# If the current shell is bash, exit it because the ported rocket shell misbaves
# when VI'ing scripts and this script is specifically written to Korn Shell (ksh)
# ------------------------------------------------------------------------------
CURR_SHELL=`echo $0`

if [ "$CURR_SHELL" = "bash" ]; then
    # Have not found a good way to exit the bash shell without ending the profile
	echo "This script can not run in a bash emulator, exiting bash and and thus"\
	"you must exit this profile again."
	exit 1
fi

# ------------------------------------------------------------------------------
# Source the known mount points
# ------------------------------------------------------------------------------
. ./mounts.sh

################################################################################
# Global vars - since ksh is the default shell and local ksh vars are defined
# with `typeset`, e.g. `typeset var foo`, I don't want to script this solely for
# ksh given there are other ported shells for z/OS.
################################################################################
ZOAU_INDEX=""
ZOAU_VERSION=""
ZOAU_MOUNT=""
ZOAU_DATA_SET=""

PYTHON_INDEX=""
PYTHON_VERSION=""
PYTHON_PATH=""

# ------------------------------------------------------------------------------
# Mount all data sets from the mount table, check if there is something mounted
# already, compare that to the data set being mounted, if they don't match,
# umount and mount the correct one else skip over it.
# ------------------------------------------------------------------------------
mount(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
    for tgt in "${zoau_mount_list[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		# zoau_mounted_data_set can be empty so perform added validation
		zoau_mounted_data_set=`df ${zoau_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`

		# If zoau_mounted_data_set is empty or not, we will perform a mount
		if [ "$zoau_mounted_data_set" != "$zoau_data_set" ]; then
			echo "Mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."

			# If zoau_mounted_data_set not empty, compare the mount points and if they match, then unmount.
			# Note, the mount point could be root (/) waitng for children so lets compare before unmounting.
			if [ ! -z "${zoau_mounted_data_set}" ]; then
				temp_mount=`df ${zoau_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 1`
				if [ "${zoau_mount}" = "${temp_mount}" ]; then
					/usr/sbin/unmount ${zoau_mount}
				fi
			fi
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount -r -t zfs -f ${zoau_data_set} ${zoau_mount}
		else
			echo "ZOAU ${zoau_version} is already mounted on data set ${zoau_data_set} to path ${zoau_mount}."
		fi
    done

	unset python_mount
	unset python_data_set
    for tgt in "${python_mount_list[@]}" ; do
	    python_mount=`echo "${tgt}" | cut -d ":" -f 1`
        python_data_set=`echo "${tgt}" | cut -d ":" -f 2`

		# python_mounted_data_set can be empty so perform added validation
		python_mounted_data_set=`df ${python_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`

		# If python_mounted_data_set is empty or not, we will perform a mount
		if [ "$python_mounted_data_set" != "$python_data_set" ]; then
			echo "Mouting Python ${python_mount} on data set ${python_data_set}."

			# If python_mounted_data_set not empty, compare the mount points and if they match, then unmount.
			# Note, the mount point could be root (/) waitng for children so lets compare before unmounting.
			if [ ! -z "${python_mounted_data_set}" ]; then
				temp_mount=`df ${python_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 1`
				if [ "${python_mount}" = "${temp_mount}" ]; then
					/usr/sbin/unmount ${python_mount}
				fi
			fi

			mkdir -p ${python_mount}
        	/usr/sbin/mount -r -t zfs -f ${python_data_set} ${python_mount}
		else
			echo "Python ${python_mount} is already mounted on data set ${python_data_set}."
		fi
    done
}

# ------------------------------------------------------------------------------
# Unmount all data sets from the mount table
# ------------------------------------------------------------------------------
unmount(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
    for tgt in "${zoau_mount_list[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		zoau_mounted_data_set=`df ${zoau_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		if [ "$zoau_mounted_data_set" = "$zoau_data_set" ]; then
			echo "Unmouting ZOAU ${zoau_version} on data set ${zoau_data_set} from path ${zoau_mount}."
			/usr/sbin/unmount ${zoau_mount}
		else
			echo "ZOAU ${zoau_version} is not currently mounted on data set ${zoau_data_set} to path ${zoau_mount}."
		fi
    done

	unset python_mount
	unset python_data_set
    for tgt in "${python_mount_list[@]}" ; do
	    python_mount=`echo "${tgt}" | cut -d ":" -f 1`
        python_data_set=`echo "${tgt}" | cut -d ":" -f 2`

		python_mounted_data_set=`df ${python_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		if [ "$python_mounted_data_set" = "$python_data_set" ]; then
			echo "Unmouting Python ${python_mount} on data set ${python_data_set}."
			/usr/sbin/unmount ${python_mount}
		else
			echo "Python ${python_mount} is not currently mounted on data set ${python_data_set}."
		fi
    done
}

# ------------------------------------------------------------------------------
# Remount all data sets from the mount table, check if there is something mounted
# already, compare that to the data set being mounted, if they don't match,
# umount and mount the correct one else skip over it.
# ------------------------------------------------------------------------------
remount(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
    for tgt in "${zoau_mount_list[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

		zoau_mounted_data_set=`df ${zoau_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		if [ "$zoau_mounted_data_set" = "$zoau_data_set" ]; then
			echo "Mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."
			/usr/sbin/unmount ${zoau_mount}
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount -r -t zfs -f ${zoau_data_set} ${zoau_mount}
		else
			echo "Mouting ZOAU ${zoau_version} on data set ${zoau_data_set} to path ${zoau_mount}."
			if [ ! -z "${zoau_mounted_data_set}" ]; then
				/usr/sbin/unmount ${zoau_mount}
			fi
			mkdir -p ${zoau_mount}
        	/usr/sbin/mount -r -t zfs -f ${zoau_data_set} ${zoau_mount}
		fi
    done

	unset python_mount
	unset python_data_set
    for tgt in "${python_mount_list[@]}" ; do
	    python_mount=`echo "${tgt}" | cut -d ":" -f 1`
        python_data_set=`echo "${tgt}" | cut -d ":" -f 2`

		python_mounted_data_set=`df ${python_mount} | tr -s [:blank:] | tail -n +2 |cut -d' ' -f 2 | sed 's/(//' | sed 's/.$//'`
		if [ "$python_mounted_data_set" = "$python_data_set" ]; then
			echo "Mouting Python ${python_mount} on data set ${python_data_set}."
			/usr/sbin/unmount ${python_mount}
			mkdir -p ${python_mount}
        	/usr/sbin/mount -r -t zfs -f ${python_data_set} ${python_mount}
		else
			echo "Mouting Python ${python_mount} on data set ${python_data_set}."
			if [ ! -z "${python_mounted_data_set}" ]; then
				/usr/sbin/unmount ${python_mount}
			fi
			mkdir -p ${python_mount}
        	/usr/sbin/mount -r -t zfs -f ${python_data_set} ${python_mount}
		fi
    done
}
################################################################################
# Main arg parser
################################################################################
case "$1" in
--mount)
    mount
    ;;
--unmount)
    unmount
    ;;
--remount)
	remount
    ;;
*)
    echo "ERROR: unknown parameter $1"
    ;;
esac
