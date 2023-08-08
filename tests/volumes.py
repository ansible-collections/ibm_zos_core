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

class Volume:

    def __init__(self, name):
        self.name = name
        self.in_use = False

    def use(self):
        self.in_use = True

    def free(self):
        self.in_use = False

class ls_Volume:

    def __init__(self, *get_volumes):
        self.volume = get_volumes


def get_disposal_vol(ls_vols):
    for volume in ls_vols.volume:
        if not (volume.in_use):
            return volume.name
    print("Not more volumes in disposal")
    return "@@@@@"

def free_vol(vol, ls_vols):
    for volume in ls_vols.volume:
        if volume.name == vol:
            volume.in_use = False
