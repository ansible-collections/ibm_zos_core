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
import pytest


class Volumes:
    # Can be declare a variable in all test case, just would required to call
    # the EC in use for the valid volumes
    EC_33012=dict(VOLUME_1="000000", VOLUME_2="222222", VOLUME_3="333333")
    EC_11047=dict(VOLUME_1="000000", VOLUME_2="222222", VOLUME_3="333333")

    # Needs to add other systems
