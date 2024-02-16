#!/bin/sh

################################################################################
# © Copyright IBM Corporation 2020
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
# This scripts actions called before after generating RST such that the
# original template.py is put back in its original state.
################################################################################

# Obtain the galaxy collection installion up to the template.py located on the host
template_doc_source=`ansible-config dump|grep DEFAULT_MODULE_PATH| cut -d'=' -f2|sed 's/[][]//g' | tr -d \'\" |sed 's/modules/doc_fragments\/template.py/g'`
mv $template_doc_source.tmp $template_doc_source