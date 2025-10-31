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

import random
import string
import re
from ansible.errors import AnsibleFilterError


def generate_data_set_name(value, generations=1):
    """Filter to generate valid data set names

    Args:
        value {str} -- value of high level qualifier to use on data set names
        generations {int, optional} -- number of dataset names to generate. Defaults to 1.

    Returns:
        list -- the total dataset names valid
    """
    if len(value) > 8:
        raise AnsibleFilterError("The high level qualifier is too long for the data set name")

    if generations > 1:
        dataset_names = []
        for generation in range(generations):
            name = value + get_tmp_ds_name()
            dataset_names.append(name)
    else:
        dataset_names = value + get_tmp_ds_name()

    return dataset_names


def get_tmp_ds_name():
    """Unify the random qualifiers generate in one name.

    Returns:
        str: valid data set name
    """
    ds = "."
    ds += "P" + get_random_q() + "."
    ds += "T" + get_random_q() + "."
    ds += "C" + get_random_q()
    return ds


def get_random_q():
    """ Function or test to ensure random hlq of datasets"""
    # Generate the first random hlq of size pass as parameter
    letters = string.ascii_uppercase + string.digits
    random_q = ''.join(random.choice(letters)for iteration in range(7))
    count = 0
    # Generate a random HLQ and verify if is valid, if not, repeat the process
    while count < 5 and not re.fullmatch(
        r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})",
        random_q,
        re.IGNORECASE,
    ):
        random_q = ''.join(random.choice(letters)for iteration in range(7))
        count += 1
    return random_q


class FilterModule(object):
    """ Jinja2 filter for the returned list or string by the collection module. """
    def filters(self):
        return {
            'generate_data_set_name': generate_data_set_name
        }
