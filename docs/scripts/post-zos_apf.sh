#!/bin/sh

################################################################################
# © Copyright IBM Corporation 2023
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

################################################################################
# This scripts actions called after generating RST and before generating Html.
# This script corrects the RST so that correct HTMl can be generated removing the
# warning:
# ibm_zos_core/docs/source/modules.rst:23: WARNING: toctree glob pattern 'modules/*' didn't match any documents
# This script will replace:
# "    | **default**: /* {mark} ANSIBLE MANAGED BLOCK <timestamp> */"
# To this:
# "    | **default**: /* {mark} ANSIBLE MANAGED BLOCK <timestamp> \*/"
################################################################################
set -x
SCRIPT_DIR=`dirname "$0"`
CURR_PATH=`pwd`
# Delete any temporary index RST
if [[ -f $CURR_PATH/source/modules/zos_apf.rst ]]; then
    sed -i '' -e "s/\> \\*\//\> \\\*\//g" $CURR_PATH/source/modules/zos_apf.rst
fi
