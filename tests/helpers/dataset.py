# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023
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
import string
import random
import re

def get_tmp_ds_name(hosts, hlq_size=8):
    """ Function or test to ensure random names of datasets
    Is need the hosts to call the shell in every test and for some cases of
    long datasets names that will generate problems with jcl the hlq size can
    change."""
    # Generate the first random hlq of size pass as parameter
    letters =  string.ascii_uppercase
    hlq =  ''.join(random.choice(letters)for iteration in range(hlq_size))
    count = 0
    # Generate a random HLQ and verify if is valid, if not, repeat the process
    while  count < 5 and not re.fullmatch(
    r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})",
            hlq,
            re.IGNORECASE,
        ):
        hlq =  ''.join(random.choice(letters)for iteration in range(hlq_size))
        count += 1
    # Get the second part of the name with the command mvstmp by time is give
    response = hosts.all.command(cmd="mvstmp {0}".format(hlq))
    for data_set in response.contacted.values():
        ds = data_set.get("stdout")
    return ds
