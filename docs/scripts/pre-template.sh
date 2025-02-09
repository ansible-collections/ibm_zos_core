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
# This scripts actions called before generating RST, this scripts leaves the
# "\n", "\r", "\r\n" in the template.py doc_fragment so that ansible linting
# test will pass such that the doc and module are match. Later this script will
# update the above strings to liters with an esacpe, for example "\n" --> '\\n'.
# This allows for RST to be generated that is usable by the ansible-doc-extractor
# and Jinja2 template, and later sphinx html.
# This requries that the ansible collection be prebuilt so that it can find
# the template.py within the collection (not within the git project). Thus run
# './ac --ac-build' before the make file that builds doc.
################################################################################

template_doc_source=`ansible-config dump|grep DEFAULT_MODULE_PATH| cut -d'=' -f2|sed 's/[][]//g' | tr -d \'\" |sed 's/modules/doc_fragments\/template.py/g'`
cp $template_doc_source $template_doc_source.tmp
sed -i '' -e "s/\"\\\\n\"/'\\\\\\\\n'/g" $template_doc_source
sed -i '' -e "s/\"\\\\r\"/'\\\\\\\\r'/g" $template_doc_source
sed -i '' -e "s/\"\\\\r\\\\n\"/'\\\\\\\\r\\\\\\\\n'/g" $template_doc_source
