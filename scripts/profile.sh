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

# Supporting bash will take added testing, the port on z/OS has enough
# differences to warrnat temporarily disabliing the function on z/OS. More
# specifically, when using `vi` in Bash, editing becomes a problem.
if [ "$CURR_SHELL" = "bash" ]; then
	if [ "$SYSTEM" = "OS/390" ]; then
		echo "Script $0 can not run in 'bash', please execute in another shell."
		exit 1
	fi
fi

# ------------------------------------------------------------------------------
# Source the known mount points
# ------------------------------------------------------------------------------
mounts_env="mounts.env"

if [ -f "$mounts_env" ]; then
    . ./$mounts_env
else
    echo "Unable to source file: $mounts_env, exiting."
    exit 1
fi

mount_sh="mounts.sh"

if [ -f "$mount_sh" ]; then
    . ./$mount_sh
else
    echo "Unable to source file: $mount_sh, exiting."
    exit 1
fi

################################################################################
# Global vars - since ksh is the default shell and local ksh vars are defined
# with `typeset`, e.g. `typeset var foo`, I don't want to script this solely for
# ksh given there are othe ported shells for z/OS.
################################################################################
ZOAU_INDEX=""
ZOAU_VERSION=""
ZOAU_MOUNT=""
ZOAU_DATA_SET=""

PYTHON_INDEX=""
PYTHON_VERSION=""
PYTHON_PATH=""

BASH_SELECTED=false

# Array where each entry is: "<index>:<version>:<mount>:<data_set>"
ZOAU_MOUNTS=""

# Array where each entry is: "<mount>:<data_set>"
PYTHON_MOUNTS=""

# Array where each entry is: "<index>:<version>:<path>"
PYTHON_MOUNT_PATHS=""
# ******************************************************************************
# Search the array `zoau_mount_list` for a matching arg, if it matches set the
# global zoau_version var to the zoau version.
# ******************************************************************************

get_option_zoau(){

    arg=$1
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
	set_zoau_mounts
    for tgt in "${ZOAU_MOUNTS[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`

        if [ "$zoau_index" = "$arg" ]; then
			ZOAU_INDEX="$zoau_index"
            ZOAU_VERSION="$zoau_version"
			ZOAU_MOUNT="$zoau_mount"
			ZOAU_DATA_SET="$zoau_data_set"
        fi
    done
}

get_option_python(){

    arg=$1
	unset python_index
	unset python_version
	unset python_path
	set_python_mount_paths
    for tgt in "${PYTHON_MOUNT_PATHS[@]}" ; do
	    python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
        python_path=`echo "${tgt}" | cut -d ":" -f 3`

        if [ "$python_index" = "$arg" ]; then
			PYTHON_INDEX="$python_index"
            PYTHON_VERSION="$python_version"
			PYTHON_PATH="$python_path"
        fi
    done
}

get_option_shell(){

    arg=$1
	case "$1" in
    	[yY][eE][sS]|[yY]* ) BASH_SELECTED=true;;
     esac
}

################################################################################
# User input for Python
################################################################################
help_option_zoau(){
	unset zoau_index
	unset zoau_version
	unset zoau_mount
	unset zoau_data_set
	echo ""
	echo "ZOAU Options:"
	set_zoau_mounts
    for tgt in "${ZOAU_MOUNTS[@]}" ; do
	    zoau_index=`echo "${tgt}" | cut -d ":" -f 1`
        zoau_version=`echo "${tgt}" | cut -d ":" -f 2`
        zoau_mount=`echo "${tgt}" | cut -d ":" -f 3`
		zoau_data_set=`echo "${tgt}" | cut -d ":" -f 4`
        echo "\t[${zoau_index}] - ZOAU ${zoau_version}"
    done
}

help_option_python(){
	unset python_index
	unset python_version
	unset python_path
	set_python_mount_paths
	echo "Python Options:"
    for tgt in "${PYTHON_MOUNT_PATHS[@]}" ; do
	    python_index=`echo "${tgt}" | cut -d ":" -f 1`
        python_version=`echo "${tgt}" | cut -d ":" -f 2`
        python_path=`echo "${tgt}" | cut -d ":" -f 3`
        echo "\t[${python_index}] - Python ${python_version}"
    done
}

help_option_shell(){
	echo "Bash shell:"
	echo "\t[Y/N] - Default no."
}

usage () {
	echo ""
    echo "Usage: $0 [1-n] [1-n] Y/N"
	echo "Example: $0 12 1 Y"
	echo "Default: $0 19 2 N"
    help_option_zoau
	help_option_python
	help_option_shell
}

################################################################################
# Message to user
################################################################################
selected_option () {
	echo "Using ZOAU version $ZOAU_VERSION"
	echo "Using python version $PYTHON_VERSION"
	if [ "${BASH_SELECTED}" = true ]; then
		echo "Bash is enabled."
	fi
}

################################################################################
# Configure all exports
################################################################################
set_exports (){

	export PATH=/bin:.

	################################################################################
	# Set the ported tools directory on the EC, see the tools you can use, eg:
	# vim, bash, etc
	################################################################################
	export TOOLS_DIR=/usr/lpp/rsusr/ported
	export PATH=$PATH:$TOOLS_DIR/bin

	################################################################################
	# Set the editor to VI
	################################################################################
	export TERM=xterm

	################################################################################
	# Standard exports used in EBCDIC/ASCII conversion needed by tools like pyz/zoau
	################################################################################
	export _BPXK_AUTOCVT='ON'
	export _CEE_RUNOPTS='FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)'
	export _TAG_REDIR_ERR=txt
	export _TAG_REDIR_IN=txt
	export _TAG_REDIR_OUT=txt
	export LANG=C

	################################################################################
	# Set Java
	################################################################################
	export JAVA_HOME=/usr/lpp/java170/J7.0

	################################################################################
	# Configure Python
	################################################################################
	export PYTHON_HOME=$PYTHON_PATH
	export PYTHON=$PYTHON_HOME/bin
	export LIBPATH=$PYTHON_HOME/lib:$LIBPATH

	################################################################################
	# ZOAU 1.0.2 or or earlier ueses ZOAU_ROOT and not ZOAU_HOME
	################################################################################
	export ZOAU_HOME=${ZOAU_MOUNT}
	export PATH=$ZOAU_HOME/bin:$PATH:$PYTHON:$JAVA_HOME/bin:$TOOLS_DIR/bin
	export MANPATH=$MANPATH:$TOOLS_DIR/man
	export ZOAU_ROOT=${ZOAU_HOME}
	export PYTHONPATH=${ZOAU_HOME}/lib/:${PYTHONPATH}
	export LIBPATH=${ZOAU_HOME}/lib:${LIBPATH}

	################################################################################
	# Custom terminal configurations
	################################################################################
	# Append home directory to the current path
	export PATH=$PATH:$HOME:

	# Set the prompt to display your login name & current directory
	export PS1='[ $LOGNAME':'$PWD':' ]'

	alias python="python3"
	alias pip="pip3"
}

set_bash (){
	################################################################################
	# Run bash shell:
	# I have have seen many issues using this version of bash to edit files on the
	# EC, for example of you edit your .profile with VI under BASH, it will render
	# unreable, for times I have to edit, I type exit it defaults be back into
	# the zos_ssh shell which does not have any issues with VI or editing files.
	# I generally use bash only for history and running commands.
	################################################################################
	if [ "${BASH_SELECTED}" = true ]; then
	   	bash;
	fi
}
################################################################################
# Main
################################################################################
# User enters choices for zoau, python and bash
if [ $# -eq 3 ];then
	get_option_zoau $1
	get_option_python $2
	get_option_shell $3
	set_exports
	selected_option
	set_bash
# User enters choices for zoau and python, bash defaults to false
elif [ $# -eq 2 ];then
	get_option_zoau $1
	get_option_python $2
	get_option_shell false
	set_exports
	selected_option
	set_bash
# Default  zoau 1.2.2 and python 3.9
elif [ $# -eq 0 ]; then
	get_option_zoau 12
	get_option_python 2
	get_option_shell false
	set_exports
	selected_option
	set_bash
elif [ "$1" = help]; then
	usage
else
	usage
fi
