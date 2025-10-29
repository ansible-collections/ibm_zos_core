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

def test_generate_data_set_name_filter(ansible_zos_module):
    hosts = ansible_zos_module
    input_string = "OMVSADM"
    hosts.all.set_fact(input_string=input_string)
    results = hosts.all.debug(msg="{{ input_string | generate_data_set_name }}")

    for result in results.contacted.values():
        print(result)
        assert result.get('msg') is not None
        assert input_string in result.get('msg')

