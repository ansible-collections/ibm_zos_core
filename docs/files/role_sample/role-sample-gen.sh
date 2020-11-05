################################################################################
# © Copyright IBM Corporation 2020
################################################################################

################################################################################
# Script Vars
################################################################################

_SCRIPTS="/scripts"
_DOC_SCRIPTS="/docs/scripts"
_ROLE_NAME="role_sample"

# SCRIPT_PATH /Users/xxx/git/github/ibm_zos_core/docs/scripts
SCRIPT_PATH="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

# PROJECT_ROOT_PATH /Users/xxx/git/github/ibm_zos_core
PROJECT_ROOT_PATH="${SCRIPT_PATH/${_DOC_SCRIPTS}/}"

# ROLE_SAMPLE_FILES_PATH /Users/xxx/git/github/ibm_zos_core/docs/files/samples/roles
ROLE_SAMPLE_FILES_PATH="${SCRIPT_PATH/${_SCRIPTS}/}"/files/samples/roles

# ROLE_ROOT /Users/xxx/git/github/ibm_zos_core/roles
ROLE_ROOT="${PROJECT_ROOT_PATH}"/roles

# ROLE_PATH /Users/xxx/git/github/ibm_zos_core/roles/role_sample
ROLE_PATH=${ROLE_ROOT}/${_ROLE_NAME}

echo SCRIPT_PATH $SCRIPT_PATH
echo PROJECT_ROOT_PATH $PROJECT_ROOT_PATH
echo ROLE_SAMPLE_FILES_PATH $ROLE_SAMPLE_FILES_PATH
echo ROLE_ROOT $ROLE_ROOT
echo ROLE_PATH $ROLE_PATH

# Does ROLE_ROOT_PATH (/Users/ddimatos/git/github/ibm_zos_core/roles) exist mkidr -p $ROLE_ROOT_PATH

# cd to ROLE_ROOT and ansible-galaxy init role_sample

# mkdir ROLE_PATH/docs

# cp ROLE_SAMPLE_FILES_PATH/defaults-main.yml to ROLE_PATH/defaults
# cp ROLE_SAMPLE_FILES_PATH/meta-main.yml to ROLE_PATH/meta
# cp ROLE_SAMPLE_FILES_PATH/tasks-main.yml to ROLE_PATH/tasks
# cp ROLE_SAMPLE_FILES_PATH/vars-main.yml to ROLE_PATH/vars
# cp ROLE_SAMPLE_FILES_PATH/docs-doc_role_sample to ROLE_PATH/docs
# cp ROLE_SAMPLE_FILES_PATH/roletest.yml to ROLE_PATH


# run sample
# gen doc