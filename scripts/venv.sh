
#!/bin/sh
# ==============================================================================
# Copyright (c) IBM Corporation 2022, 2024
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

# TODO: Need to add more global vars as some are scoped to fucntions and hidden
# from view.
# ------------------------------------------------------------------------------
# Source
# ------------------------------------------------------------------------------
cd $(dirname $0)
VERSION_PYTHON_MIN=3.9
VERSION_PYTHON="0"
VERSION_PYTHON_PATH=""
DIVIDER="===================================================================="
VENV_HOME_MANAGED=${PWD%/*}/venv
# Array where each entry is: "<index>:<version>:<mount>:<data_set>"
HOSTS_ALL=""

OPER_EQ="=="
OPER_NE="!="
OPER_LT="<"
OPER_LE="<="
OPER_GT=">"
OPER_GE=">="

# hosts_env="hosts.env"

# if [ -f "$hosts_env" ]; then
#     . ./$hosts_env
# else
#     echo "Unable to source file: $hosts_env, exiting."
#     exit 1
# fi

mount_sh="mounts.sh"

if [ -f "$mount_sh" ]; then
    . ./$mount_sh
else
    echo "Unable to source file: $mount_sh, exiting."
    exit 1
fi

################################################################################
# Converts the requirements array into a exported single line delimited with
# '\\\n' so that it can be echo'd into a requirements.txt. For example in the make
# file `echo "${REQ}">$(VENV)/requirements.txt` returns a string:
# "ansible-core==2.11.12;\\\nastroid==2.12.11;\nattrs==22.1.0;.."
# If you want echo this to a file you will need to do something like:
# X=$(./make.env --req)
# echo -e $X>requirements.txt
# Or a one-iner: echo -e $(./make.env --req)>requirements.txt
################################################################################
export_requirements(){
    unset REQ
    export REQ
    for pkg in "${requirements[@]}" ; do
        key=${pkg%%:*}
        value=${pkg#*:}
        REQ=${REQ}"$key==$value;\n"
    done
}

################################################################################
# Converts the requirements array into a single line delimited with '\\\n'
# so that it can be echo'd into a file. For example in the make
# file `echo "${REQ}">$(VENV)/requirements.txt`.
################################################################################
echo_requirements(){

    unset requirements_common
    unset requirements
    requirements_common="configurations/requirements-common.env"
    unset REQ_COMMON

    if [ -f "$requirements_common" ]; then
        . ./$requirements_common
    else
        echo "Unable to source file: $requirements_common, exiting."
        exit 1
    fi

    for pkg in "${requirements[@]}" ; do
        key=${pkg%%:*}
        value=${pkg#*:}
        if [ "$key" = "$value" ]; then
            REQ_COMMON=${REQ_COMMON}"$key;\\n"
        elif [ -z "$value" ]; then
            REQ_COMMON=${REQ_COMMON}"$key;\\n"
        else
            REQ_COMMON=${REQ_COMMON}"$key==$value;\\n"
        fi
    done

    for file in `ls configurations/*requirements-[0-9].[0-9]*.env* configurations/*requirements-latest* 2>/dev/null`; do
        # Unset the vars from any prior sourced files
        unset REQ
        unset requirements
        unset venv
        # Soure the file
        if [ -f "$file" ]; then
            . ./$file
        else
            echo "Unable to source file: $file."
        fi

        if [[ "$file" =~ "latest" ]]; then
            # eg extract 'latest' from configurations/requirements-latest file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1`
            venv_name="venv"-$ansible_version
        else
            # eg extract 2.14 from configurations/requirements-2.14.sh file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1,2`
            venv_name="venv"-$ansible_version
            #echo $venv_name
        fi

        for pkg in "${requirements[@]}" ; do
            key=${pkg%%:*}
            value=${pkg#*:}
            if [ "$key" = "$value" ]; then
                REQ=${REQ}"$key;\\n"
            elif [ -z "$value" ]; then
                REQ=${REQ}"$key;\\n"
            elif [ "$key" = "ansible-core" ] && [ "$value" = "latest" ]; then
                REQ=${REQ}"https://github.com/ansible/ansible/archive/devel.tar.gz\\n"
            else
                REQ=${REQ}"$key==$value;\\n"
            fi
        done
        echo "${REQ}""${REQ_COMMON}"

        py_req="0"
        for ver in "${python[@]}" ; do
            py_op=`echo "${ver}" | cut -d ":" -f 1`
            py_name=`echo "${ver}" | cut -d ":" -f 2`
            py_req=`echo "${ver}" | cut -d ":" -f 3`
        done
         echo "${py_req}"
    done
}


# Lest normalize the version from 3.10.2 to 3010002000
# Do we we need that 4th octet? 
normalize_version() {
    echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }';
}

make_venv_dirs(){
    # VENV's control are under this script which is to create them the GitHub
    # project root (../venv/), this is because we want this to be managed such
    # that direcotry `../venv` is defined in .gitignore and galaxy.yml
    # (build_ignore) to avoid having them pulled in by any build process.

    # We should think about the idea of allowing:
    # --force, --synch, --update thus not sure we need this method and better to
    # manage this logic inline to write_req
    for file in `ls configurations/*requirements-[0-9].[0-9]*.env* configurations/*requirements-latest* 2>/dev/null`; do
        if [[ "$file" =~ "latest" ]]; then
            # eg extract 'latest' from configurations/requirements-latest file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1`
            venv_name="venv"-$ansible_version
        else
            # eg extract 2.14 from configurations/requirements-2.14.sh file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1,2`
            venv_name="venv"-$ansible_version
            #echo $venv_name
        fi
        mkdir -p "${VENV_HOME_MANAGED}"/"${venv_name}"
    done
}

write_requirements(){
    option_pass=$1
    unset requirements_common
    unset requirements
    unset REQ
    unset REQ_COMMON
    requirements_common_file="configurations/requirements-common.env"

    # Source the requirements file for now, easy way to do this. Exit may not
    # not be needed but leave it for now.
    if [ -f "$requirements_common_file" ]; then
        . ./$requirements_common_file
    else
        echo "Unable to source file: $requirements_common_file, exiting."
        exit 1
    fi

    for pkg in "${requirements[@]}" ; do
        key=${pkg%%:*}
        value=${pkg#*:}
        if [ "$key" = "$value" ]; then
            REQ_COMMON=${REQ_COMMON}"$key;\\n"
        elif [ -z "$value" ]; then
            REQ_COMMON=${REQ_COMMON}"$key;\\n"
        else
            REQ_COMMON=${REQ_COMMON}"$key==$value;\\n"
        fi
    done

    for file in `ls configurations/*requirements-[0-9].[0-9]*.env* configurations/*requirements-latest* 2>/dev/null`; do
        # Unset the vars from any prior sourced files
        unset REQ
        unset requirements
        unset venv
        # Soure the file
        if [ -f "$file" ]; then
            . ./$file
        else
            echo "Unable to source file: $file."
        fi

        if [[ "$file" =~ "latest" ]]; then
            # eg extract 'latest' from configurations/requirements-latest file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1`
            venv_name="venv"-$ansible_version
            echo $venv_name
        else
            # eg extract 2.14 from configurations/requirements-2.14.sh file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1,2`
            venv_name="venv"-$ansible_version
            echo $venv_name
        fi

        for pkg in "${requirements[@]}" ; do
            key=${pkg%%:*}
            value=${pkg#*:}
            #REQ=${REQ}"$key==$value;\\n"
            if [ "$key" = "$value" ]; then
                REQ=${REQ}"$key;\\n"
            elif [ -z "$value" ]; then
                REQ=${REQ}"$key;\\n"
            elif [ "$key" = "ansible-core" ] && [ "$value" = "latest" ]; then
                REQ=${REQ}"https://github.com/ansible/ansible/archive/devel.tar.gz\\n"
            else
                REQ=${REQ}"$key==$value;\\n"
            fi
        done

        py_req="0"
        for ver in "${python[@]}" ; do
            py_op=`echo "${ver}" | cut -d ":" -f 1`
            py_name=`echo "${ver}" | cut -d ":" -f 2`
            py_req=`echo "${ver}" | cut -d ":" -f 3`
        done

        if [ "$OPER_EQ" == "$py_op" ];then
			py_op="-eq"
		elif [ "$OPER_NE" == "$py_op" ];then
			py_op="-ne"
		elif [ "$OPER_LT" == "$py_op" ];then
			py_op="-lt"
		elif [ "$OPER_LE" == "$py_op" ];then
			py_op="-le"
		elif [ "$OPER_GT" == "$py_op" ];then
			py_op="-gt"
		elif [ "$OPER_GE" == "$py_op" ];then
			py_op="-ge"
		fi

        discover_python $py_op $py_req

        # Is the discoverd python >= what the requirements.txt requires?
        if [ $(normalize_version $VERSION_PYTHON) "$py_op" $(normalize_version $py_req) ]; then
            echo "${REQ}${REQ_COMMON}">"${VENV_HOME_MANAGED}"/"${venv_name}"/requirements.txt
            cp mounts.env "${VENV_HOME_MANAGED}"/"${venv_name}"/
            #cp info.env "${VENV_HOME_MANAGED}"/"${venv_name}"/
            #cp info.env.axx "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp mounts.sh "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp hosts.env "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp venv.sh "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp profile.sh "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp ../tests/dependencyfinder.py "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp ce.py "${VENV_HOME_MANAGED}"/"${venv_name}"/
            cp -R modules "${VENV_HOME_MANAGED}"/"${venv_name}"/

            # Decrypt file
            if [ "$option_pass" ]; then
                touch "${VENV_HOME_MANAGED}"/"${venv_name}"/info.env
                # Probably can be a 600 - needs testing
                chmod 700 "${VENV_HOME_MANAGED}"/"${venv_name}"/info.env
                #echo "${option_pass}" | openssl bf -d -a -in info.env.axx -out "${VENV_HOME_MANAGED}"/"${venv_name}"/info.env -pass stdin
                echo "${option_pass}" | openssl enc -d -aes-256-cbc -a -in info.env.axx -out "${VENV_HOME_MANAGED}"/"${venv_name}"/info.env -pass stdin
            else
                # echo a stub so the user can later choose to rename and configure
                touch "${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "# This configuration file is used by the tool to avoid exporting enviroment variables">>"${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "# To use this, update all the variables with a value and rename the file to 'info.env'.">>"${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "USER=\"\"">>"${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "PASS=\"\"">>"${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "HOST_SUFFIX=\"\"">>"${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "SSH_KEY_PIPELINE=\"\"">>"${VENV_HOME_MANAGED}"/"${venv_name}"/info.env.changeme
                echo "No password was provided, a temporary 'info.env.changeme' file has been created for your convenience."
            fi
        else
            echo "Not able to create managed venv path: ${VENV_HOME_MANAGED}/${venv_name} , min python required is ${py_req}, found version $VERSION_PYTHON"
            echo "Consider installing another Python for your system, if on Mac 'brew install python@3.10', otherwise review your package manager"
            rm -rf "${VENV_HOME_MANAGED}"/"${venv_name}"/
        fi
    done
}


create_venv_and_pip_install_req(){

    for file in `ls configurations/*requirements-[0-9].[0-9]*.env* configurations/*requirements-latest* 2>/dev/null`; do
        unset venv

        if [[ "$file" =~ "latest" ]]; then
            # eg extract 'latest' from configurations/requirements-latest file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1`
            venv_name="venv"-$ansible_version
        else
            # eg extract 2.14 from configurations/requirements-2.14.sh file name
            ansible_version=`echo $file | cut -d"-" -f2|cut -d"." -f1,2`
            venv_name="venv"-$ansible_version
            #echo $venv_name
        fi


        if [ -f $VENV_HOME_MANAGED/$venv_name/requirements.txt ]; then
            echo ${DIVIDER}
		    echo "Creating python virtual environment: ${VENV_HOME_MANAGED}/${venv_name}."
		    echo ${DIVIDER}
		    ${VERSION_PYTHON_PATH} -m venv "${VENV_HOME_MANAGED}"/"${venv_name}"/
            ${VENV_HOME_MANAGED}/${venv_name}/bin/pip3 install --upgrade pip
            ${VENV_HOME_MANAGED}/${venv_name}/bin/pip install --upgrade pip
            "${VENV_HOME_MANAGED}"/"${venv_name}"/bin/pip3 install -r "${VENV_HOME_MANAGED}"/"${venv_name}"/requirements.txt
        else
            echo "Virtual environment "${VENV_HOME_MANAGED}"/"${venv_name}" already exists, no changes made."; \
        fi
    done
}


find_in_path() {
    result=""
    OTHER_PYTHON_PATHS="/Library/Frameworks/Python.framework/Versions/Current/bin:/opt/homebrew/bin:"
    PATH="${OTHER_PYTHON_PATHS}${PATH}"
    OLDIFS=$IFS
    IFS=:
    for x in $PATH; do
        if [ -x "$x/$1" ]; then
            result=${result}" $x/$1"
        fi
    done
    IFS=$OLDIFS
    echo $result
}


# Find the most recent python in a users path
discover_python(){
    operator=$1
    required_python=$2
    if [ ! "$operator" ]; then
        operator="-ge"
    fi

    if [ "$required_python" ]; then
        VERSION_PYTHON=$required_python
    fi

    # Note:
    #   Don't use which, it only will find first in path within the script
    #   for python_found in `which python3 | cut -d" " -f3`; do
    #
    #   The 'pys' array will search for pythons in reverse order, once it finds one that matches
    #   the configurations/requirements-x.xx.env it does not continue searching. Reverse order is important to
    #   maintain.
    rc=-1
    pys="python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8"
    for py in $(echo $pys| tr ' ' '\n');do
        for python_found in `find_in_path $py`; do
            ver=`${python_found} --version | cut -d" " -f2`
            rc=$?
            ver=`echo $ver  |cut -d"." -f1,2`
            ver_path="$python_found"
            echo "Found $ver_path"
        done

        if [ $rc -eq 0  ];then
            if [ $(normalize_version $ver) "$operator" $(normalize_version $VERSION_PYTHON) ]; then
                VERSION_PYTHON="$ver"
                VERSION_PYTHON_PATH="$ver_path"
                break
            fi
        fi
    done

    # pys=("python3.14" "python3.13" "python3.12" "python3.11" "python3.10" "python3.9" "python3.8")
    # rc=1
    # for py in "${pys[@]}"; do
    #     for python_found in `find_in_path $py`; do
    #         ver=`${python_found} --version | cut -d" " -f2`
    #         rc=$?
    #         ver=`echo $ver  |cut -d"." -f1,2`
    #         ver_path="$python_found"
    #         echo "Found $ver_path"
    #     done

    #     if [ $rc -eq 0  ];then
    #         if [ $(normalize_version $ver) "$operator" $(normalize_version $VERSION_PYTHON) ]; then
    #             VERSION_PYTHON="$ver"
    #             VERSION_PYTHON_PATH="$ver_path"
    #             break
    #         fi
    #     fi
    # done

    echo ${DIVIDER}
	echo "Discovered Python version: ${VERSION_PYTHON}."
    echo "Discovered Python path: ${VERSION_PYTHON_PATH}."
	echo ${DIVIDER}
}
################################################################################
# Return Python HOME path when given a key that is contained in the zoau array.
################################################################################

get_pyz(){
    set_python_mount_paths
    arg=$1
    unset PYZ
    echo ${PYTHON_MOUNT_PATHS[@]}
    for py in "${PYTHON_MOUNT_PATHS[@]}" ; do
        key=${py%%:*}
        value=${py#*:}
        if [ "$key" = "$arg" ]; then
            PYZ="$value"
        fi
    done
}

################################################################################
# Echo Python HOME path when given a key that is contained in the zoau array.
################################################################################
echo_pyz(){
    get_pyz $1
    echo "${PYZ}"
}

################################################################################
# Return ZOAU HOME path when given a key that is contained in the zoau array.
################################################################################
get_zoau(){
    arg=$1
    unset ZOAU
    for zo in "${zoau[@]}" ; do
        key=${zo%%:*}
        value=${zo#*:}
        if [ "$key" = "$arg" ]; then
            ZOAU="$value"
        fi
    done
}

################################################################################
# Echo ZOAU HOME path when given a key that is contained in the zoau array.
################################################################################
echo_zoau(){
    get_zoau $1
    echo "${ZOAU}"
}

latest_venv(){
    dir_version_latest="0"
    test_for_managed_venv=`ls -d "$VENV_HOME_MANAGED"/venv-[0-9].[0-9]* 2>/dev/null`

    if [ ! -z "$test_for_managed_venv" ]; then
        for dir_version in `ls -d "$VENV_HOME_MANAGED"/venv-[0-9].[0-9]* | cut -d"-" -f2`; do
            if [ $(normalize_version $dir_version) -ge $(normalize_version $dir_version_latest) ]; then
                dir_version_latest=$dir_version
            fi
        done
        echo "${VENV_HOME_MANAGED}"/"venv-"$dir_version_latest
    fi
}



# ==============================================================================
# Public function that initializes a global array `ZOAU_MOUNTS` where each index
# contains clolon `:` delimited values about ZOAU mounts. For example
# ZOAU_MOUNTS[0] has in it <index>:<version>:<mount>:<data_set> where that may
# look like "1:v1.2.0:/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS", see sourced script
# `mounts.env` for more information.
# GLOBAL:       ZOAU_MOUNTS
# ARGUMENTS:    None
# OUTPUTS:      None
# RETURN:       None
# USAGE:        set_zoau_mounts
# ==============================================================================
set_hosts_to_array(){

    # Source the envrionment file here rather than at the top of this script.
    # If you source it to early it will trigger the condtion below that was
    # removed from info.env.
    if [ -f "info.env" ]; then
        . ./info.env
    else # check if the env varas instead have been exported
        if [ -z "$USER" ] || [ -z "$PASS" ]  || [ -z "$HOST_SUFFIX" ]; then
            echo "This configuration requires either 'info.env' exist or environment vars for the z/OS host exist and be exported."
            echo "Export and set vars: 'USER', 'PASS','HOST_SUFFIX' and optionally 'SSH_KEY_PIPELINE', or place them in a file named info.env."
            exit 1
        fi
    fi

    hosts_env="hosts.env"

    if [ -f "$hosts_env" ]; then
        . ./$hosts_env
    else
        echo "Unable to source file: $hosts_env, exiting."
        exit 1
    fi

    _set_shell_array HOSTS_ALL "$(echo $host_list_str)"
}


################################################################################
# Host list details used by the function `get_config` to generate
# a collections configuration. Keys can be an ECs hostname or a users laptop
# user name which is the same as what `whoami` returns.
# Using word spliting to split the values into an array, for example
# temp_array=(${tgt//:/ }) translates to ${string//substring/replacement}, thus
# all ':' are matched and replaced with a ' ' and then you have
# (element1 element2 ... elementN) to initialize the array.
################################################################################

get_host_ids(){
    set_hosts_to_array
    unset host_index
    unset host_prefix
    for tgt in "${HOSTS_ALL[@]}" ; do
        host_index=`echo "${tgt}" | cut -d ":" -f 1`
        host_prefix=`echo "${tgt}" | cut -d ":" -f 2`

        echo "ID: $host_index Host: $host_prefix"
    done
}

get_host_ids_production(){
    set_hosts_to_array
    unset host_index
    unset host_prefix
    unset host_production
    first_entry=true
    for tgt in "${HOSTS_ALL[@]}" ; do
        host_index=`echo "${tgt}" | cut -d ":" -f 1`
        host_prefix=`echo "${tgt}" | cut -d ":" -f 2`
        host_production=`echo "${tgt}" | cut -d ":" -f 5`
        if [ "$host_production" == "production" ];then
            if [ "$first_entry" == "true" ];then
                first_entry=false
                echo "$host_prefix"
            else
                echo " $host_prefix"
            fi
        fi
    done
}

    first_entry=true
    skip_tests=""
    for i in $(echo $skip | sed "s/,/ /g")
    do
        if [ "$first_entry" == "true" ];then
            first_entry=false
            skip_tests="$CURR_DIR/tests/functional/modules/$i"
        else
            skip_tests="$skip_tests $CURR_DIR/tests/functional/modules/$i"
        fi
    done

# Should renane this with a prefix of set_ to make it more readable
ssh_host_credentials(){
	arg=$1
	unset host
	unset user
	unset pass

	# Call helper script to have ZOAU_MOUNTS generated
	set_hosts_to_array
    for tgt in "${HOSTS_ALL[@]}" ; do
		key=`echo "${tgt}" | cut -d ":" -f 1`
		if [ "$key" = "$arg" ]; then
			host=`echo "${tgt}" | cut -d ":" -f 2`
			user=`echo "${tgt}" | cut -d ":" -f 3`
			pass=`echo "${tgt}" | cut -d ":" -f 4`
		fi
	done
}

################################################################################
# Copy a users key to a remote target to be a known host, if the host has a cert
# field in the host_list not equal to none, it will also be copied for jenkins
################################################################################
ssh_copy_key(){
    # sshpass -p "${pass}" ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa.pub "${user}"@"${host}" &> /dev/null
    # Copying all public keys because some of the sytems don't agree on RSA as a mutual signature algorithm
    for pub in `ls ~/.ssh/*.pub`; do
        echo "Copying public key ${pub} to host ${host}"
        sshpass -p "${pass}" ssh-copy-id -o StrictHostKeyChecking=no -i "${pub}" "${user}"@"${host}" &> /dev/null;
    done

    if [ ! -z "$SSH_KEY_PIPELINE" ]; then
        echo "${SSH_KEY_PIPELINE}" | ssh "${user}"@"${host}"  "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
    else
        echo "This is optional, if you define and export 'SSH_KEY_PIPELINE', the z/OS host can be authenticated with additonal keys such as a pipeline."
    fi
}

################################################################################
# Scp some scripts to the remote host and execute them.
################################################################################
ssh_copy_files_and_mount(){
    scp -O "$1" "$2" "$3" "${user}"@"${host}":/u/"${user}"
    ssh "${user}"@"${host}" "cd /u/"${user}"; chmod 755 *.sh; ./mounts.sh --mount; exit;"
}

################################################################################
# Echo the configuration used by the ansible core python test framework
################################################################################
echo_config(){
unset CONFIG

CONFIG=${CONFIG}"host: ${host}\\\n"
CONFIG=${CONFIG}"user: ${user}\\\n"
CONFIG=${CONFIG}"python_path: ${PYZ_HOME}/bin/python3\\\n"
CONFIG=${CONFIG}"\\\n"
CONFIG=${CONFIG}"environment:\\\n"
CONFIG=${CONFIG}"  _BPXK_AUTOCVT: \"ON\"\\\n"
CONFIG=${CONFIG}"  _CEE_RUNOPTS: \"'FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)'\"\\\n"
CONFIG=${CONFIG}"  _TAG_REDIR_ERR: txt\\\n"
CONFIG=${CONFIG}"  _TAG_REDIR_IN: txt\\\n"
CONFIG=${CONFIG}"  _TAG_REDIR_OUT: txt\\\n"
CONFIG=${CONFIG}"  LANG: C\\\n"
CONFIG=${CONFIG}"  ZOAU_HOME: ${ZOAU_HOME}\\\n"
CONFIG=${CONFIG}"  LIBPATH: ${ZOAU_HOME}/lib:${PYZ_HOME}/lib:/lib:/usr/lib:.\\\n"
CONFIG=${CONFIG}"  PYTHONPATH: ${ZOAU_HOME}/lib\\\n"
CONFIG=${CONFIG}"  PATH: ${ZOAU_HOME}/bin:${PYZ_HOME}/bin:/bin:/usr/sbin:/var/bin\\\n"
CONFIG=${CONFIG}"  PYTHONSTDINENCODING: \"cp1047\"\\n"

echo  ${CONFIG}
}

write_test_config(){
unset CONFIG
host_zvm=$1
pyz_version=$2
zoau_version=$3
managed_venv_path=$4

ssh_host_credentials "$host_zvm"
get_python_mount "$pyz_version"
get_zoau_mount "$zoau_version"

CONFIG=${CONFIG}"host: ${host}\\n"
CONFIG=${CONFIG}"user: ${user}\\n"
CONFIG=${CONFIG}"python_path: ${PYZ_HOME}/bin/python3\\n"
CONFIG=${CONFIG}"\\n"
CONFIG=${CONFIG}"environment:\\n"
CONFIG=${CONFIG}"  _BPXK_AUTOCVT: \"ON\"\\n"
CONFIG=${CONFIG}"  _CEE_RUNOPTS: \"'FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)'\"\\n"
CONFIG=${CONFIG}"  _TAG_REDIR_IN: txt\\n"
CONFIG=${CONFIG}"  _TAG_REDIR_OUT: txt\\n"
CONFIG=${CONFIG}"  LANG: C\\n"
CONFIG=${CONFIG}"  ZOAU_HOME: ${ZOAU_HOME}\\n"
CONFIG=${CONFIG}"  LIBPATH: ${ZOAU_HOME}/lib:${PYZ_HOME}/lib:/lib:/usr/lib:.\\n"
CONFIG=${CONFIG}"  PYTHONPATH: ${ZOAU_HOME}/lib\\n"
CONFIG=${CONFIG}"  PATH: ${ZOAU_HOME}/bin:${PYZ_HOME}/bin:/bin:/usr/sbin:/var/bin\\n"
CONFIG=${CONFIG}"  PYTHONSTDINENCODING: \"cp1047\"\\n"

echo $CONFIG>$managed_venv_path/config.yml
}

################################################################################
# Main arg parser
################################################################################

case "$1" in
--cert)
    ssh_host_credentials $2
    ssh_copy_key
    ;;
--host-credentials)
    ssh_host_credentials $2
    echo "$host"
    ;;
--user-credentials)
    ssh_host_credentials $2
    echo "$user"
    ;;
--pass-credentials)
    ssh_host_credentials $2
    echo "$pass"
    ;;
--host-setup-files)  #ec33017a "mounts.env" "mounts.sh" "shell-helper.sh" "profile.sh"
    ssh_host_credentials $2
    ssh_copy_files_and_mount $3 $4 $5
    ;;
--targets)
    get_host_ids
    ;;
--targets-production)
    get_host_ids_production
    ;;
--config)
    write_test_config $2 $3 $4 $5
    ;;
--disc)
    discover_python
    ;;
--vsetup)
    #discover_python
    make_venv_dirs
    #echo_requirements
    write_requirements $3
    create_venv_and_pip_install_req
    ;;
--latest_venv)
    latest_venv
    ;;
--perform-unit-test)
    discover_python
    #make_venv_dirs
    echo_requirements
    #write_requirements $3
    ;;
*)
    echo "ERROR: unknown parameter $1"
    ;;
esac
