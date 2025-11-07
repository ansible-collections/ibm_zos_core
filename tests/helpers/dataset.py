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
import string
import random
import time
import re


def get_tmp_ds_name(mlq_size=7, llq_size=7, symbols=False):
    """ Function or test to ensure random names of datasets
    the values of middle and last qualifier can change size by parameter,
    but by default includes one letter.
    Also includes indication if symbols should be in the string, default=false."""
    ds = "ANSIBLE" + "."
    if symbols:
        ds += "P" + get_random_qs(mlq_size).upper() + "."
    else:
        ds += "P" + get_random_q(mlq_size).upper() + "."
    ds += "T" + str(int(time.time()*1000))[-7:] + "."
    if symbols:
        ds += "C" + get_random_qs(llq_size).upper()
    else:
        ds += "C" + get_random_q(llq_size).upper()

    return(ds)


def get_random_q(size=7):
    """ Function or test to ensure random hlq of datasets"""
    # Generate the first random hlq of size pass as parameter
    letters =  string.ascii_uppercase + string.digits
    random_q =  ''.join(random.choice(letters)for iteration in range(size))
    count = 0
    # Generate a random HLQ and verify if is valid, if not, repeat the process
    while  count < 5 and not re.fullmatch(
    r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})",
            random_q,
            re.IGNORECASE,
        ):
        random_q =  ''.join(random.choice(letters)for iteration in range(size))
        count += 1
    return random_q

def get_random_qs(size=7):
    """ Function or test to ensure random hlq of datasets, including symbol characters"""
    # Generate the first random hlq of size pass as parameter
    letters =  string.ascii_uppercase + string.digits
    special_chars = "$@#-"
    random_q =  ''.join(random.choice(letters)for iteration in range(size))
    random_char = random_q[random.choice(range(0, size))]
    random_q = random_q.replace(random_char, random.choice(special_chars))
    count = 0
    # Generate a random HLQ and verify if is valid, if not, repeat the process
    while  count < 5 and not re.fullmatch(
    r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})",
            random_q,
            re.IGNORECASE,
        ):
        random_q =  ''.join(random.choice(letters)for iteration in range(size))
        random_char = random_q[random.choice(range(0, size))]
        random_q = random_q.replace(random_char, random.choice(special_chars))
        count += 1
    return random_q

def get_tmp_member():
    # Generate a random length between 3 and 7
    length = random.randint(2, 6)
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    return random_str.upper()