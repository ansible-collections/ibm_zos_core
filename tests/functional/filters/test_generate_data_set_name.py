# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

# trust_as_template was introduced in Ansible Core 2.19 to satisfy its new
# template-trust security model. On 2.18 and earlier the function does not
# exist and is not needed — a plain string is templated unconditionally.
try:
    from ansible.template import trust_as_template
except ImportError:
    def trust_as_template(value):  # type: ignore[misc]
        return value

def test_generate_data_set_name_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    hosts.all.set_fact(input_string=input_string)
    results = hosts.all.debug(msg=trust_as_template("{{ input_string | generate_data_set_name }}"))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert input_string in result.get('msg')

def test_generate_data_set_name_mlq_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    mlq = "mlqadm"
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"middle_level_qualifier='{mlq}'"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert input_string in result.get('msg')
        assert mlq.upper() in result.get('msg')

def test_generate_data_set_name_mlq_multiple_generations_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    mlq = "mlqadm"
    num_names = 5
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"middle_level_qualifier='{mlq}', "
        f"num_names={num_names}"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert len(result.get('msg')) == num_names
        assert input_string in result.get('msg')[0]
        assert mlq.upper() in result.get('msg')[0]

def test_generate_data_set_name_llq_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    llq = "llqadm"
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"low_level_qualifier='{llq}'"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert input_string in result.get('msg')
        assert llq.upper() in result.get('msg')

def test_generate_data_set_name_llq_multiple_generations_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    llq = "llqadm"
    num_names = 5
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"low_level_qualifier='{llq}', "
        f"num_names={num_names}"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert len(result.get('msg')) == num_names
        assert input_string in result.get('msg')[0]
        assert llq.upper() in result.get('msg')[0]

def test_generate_data_set_name_mlq_llq_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    mlq = "mlqadm"
    llq = "llqadm"
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"middle_level_qualifier='{mlq}', "
        f"low_level_qualifier='{llq}') }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert input_string in result.get('msg')
        assert mlq.upper() in result.get('msg')
        assert llq.upper() in result.get('msg')

def test_generate_data_set_name_mlq_llq_multiple_generations_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    mlq = "mlqadm"
    llq = "llqadm"
    num_names = 3
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"middle_level_qualifier='{mlq}', "
        f"low_level_qualifier='{llq}', "
        f"num_names={num_names}"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert len(result.get('msg')) == num_names
        assert input_string in result.get('msg')[0]
        assert mlq.upper() in result.get('msg')[0]
        assert llq.upper() in result.get('msg')[0]

def test_generate_data_set_name_filter_multiple_generations(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    num_names = 10
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"num_names={num_names}"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('msg') is not None
        assert input_string in result.get('msg')[0]
        assert len(result.get('msg')) == 10

def test_generate_data_set_name_filter_bad_hlq(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADMONE"
    hosts.all.set_fact(input_string=input_string)
    results = hosts.all.debug(msg=trust_as_template("{{ input_string | generate_data_set_name }}"))

    for result in results.contacted.values():
        assert result.get('failed') is True
        assert f"The qualifier {input_string} is too long for the data set name." in result.get('msg')

def test_generate_data_set_name_filter_bad_mlq(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    mlq = "1mlq"
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"middle_level_qualifier='{mlq}'"
        f") }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('failed') is True
        assert f"The qualifier {mlq.upper()} is not following the rules for naming conventions." in result.get('msg')

def test_generate_data_set_name_mlq_bad_llq(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    mlq = "mlqadm"
    llq = "llqadmhere"
    hosts.all.set_fact(input_string=input_string)
    jinja_expr = (
        f"{{{{ input_string | generate_data_set_name("
        f"middle_level_qualifier='{mlq}', "
        f"low_level_qualifier='{llq}') }}}}"
    )
    results = hosts.all.debug(msg=trust_as_template(jinja_expr))

    for result in results.contacted.values():
        assert result.get('failed') is True
        assert f"The qualifier {llq.upper()} is too long for the data set name." in result.get('msg')

def test_generate_data_set_name_filter_no_hlq(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADMONE"
    results = hosts.all.debug(msg=trust_as_template("{{ generate_data_set_name }}"))

    for result in results.contacted.values():
        assert result.get('failed') is True

def test_generate_data_set_name_filter_bad_hlq(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = ""
    hosts.all.set_fact(input_string=input_string)
    results = hosts.all.debug(msg=trust_as_template("{{ input_string | generate_data_set_name }}"))

    for result in results.contacted.values():
        assert result.get('failed') is True
        assert "A High-Level Qualifier is required." in result.get('msg')