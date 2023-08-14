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
# Class volume to save the information with volume name and a flag of use
# to mange in all test suits
    def __init__(self, name):
        self.name = name
        self.in_use = False

    def use(self):
        self.in_use = True

    def free(self):
        self.in_use = False

class ls_Volume:
# Class to call fixture get_volumes and filled the array and manage volumes
# instances of are in use or not
    def __init__(self, *get_volumes):
        self.volume = get_volumes


def get_disposal_vol(ls_vols):
    # Check in the list of volumes one on disposal if not, send a error
    for volume in ls_vols.volume:
        if not (volume.in_use):
            volume.use()
            return volume.name
    print("Not more volumes in disposal return volume 000000")
    return "000000"

def free_vol(vol, ls_vols):
    # Check from the array the volume is already free for other test to use
    for volume in ls_vols.volume:
        if volume.name == vol:
            volume.free()

def validate_volume(volume, hosts):
    failed = False
    results = hosts.all.shell(cmd="vtocls {0}".format(volume))
    for result in results.contacted.values():
        if result.get("failed", False) is True:
            failed = True
        if result.get("rc", 0) > 0:
            failed = True
    return not failed