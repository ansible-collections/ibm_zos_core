# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
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
import time
import yaml
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
class Volume:
    """ Volume class represents a volume on the z system, it tracks if the volume name
    and status of the volume with respect to the current test session."""
    def __init__(self, *args):
        self.name = args[0]
        self.unit = args[1] if len(args) > 1 else None
        self.in_use = False

    def __str__(self):
        return f'The volume {self.name} is in {self.in_use} in use'

    def use(self):
        self.in_use = True

    def free(self):
        self.in_use = False

class Volume_Handler:
    """ Class to manage use of the volumes generated by a session."""
    def __init__(self, list_volumes):
        self.volumes = list_volumes
        def init_volumes(list_volumes):
            list_volumes = []
            for volume in self.volumes:
                if type(volume) is list:
                    vol = volume[0]
                    unit = volume[1]
                    list_volumes.append(Volume(vol, unit))
                else:
                    list_volumes.append(Volume(volume))
            return list_volumes
        self.volumes = init_volumes(list_volumes)

    def get_available_vol(self):
        """ Check in the list of volumes one on use or not, also send a default
        volume 0 as is the one with more tracks available."""
        for volume in self.volumes:
            if not (volume.in_use):
                volume.use()
                return volume.name
        print("Not more volumes in disposal return volume 000000")
        return "000000"

    def get_available_vol_addr(self):
        """ Check in the list of volumes one on use or not, also send a default
        volume USER02 as is the one with less data sets included."""
        for volume in self.volumes:
            if not (volume.in_use):
                volume.use()
                return volume.name, volume.unit
        print("Not more volumes in disposal return volume USER02")
        return "USER02","01A2"

    def free_vol(self, vol):
        """ Check from the array the volume is already free for other test to use."""
        for volume in self.volumes:
            if volume.name == vol:
                volume.free()


def get_volumes(ansible_zos_module, path):
    """Get an array of available volumes"""
    # Using the command d u,dasd,online to fill an array of available volumes with the priority
    # of of actives (A) and storage (STRG) first then online (O) and storage and if is needed, the
    # private ones but actives then to get a flag if is available or not every volumes
    # is a instance of a class to manage the use.
    hosts = ansible_zos_module
    list_volumes = []
    all_volumes_list = []
    storage_online = []
    flag = False
    iteration = 5
    prefer_vols = read_test_config(path)
    # The first run of the command d u,dasd,online,,n in the system can conclude with empty data
    # to ensure get volumes is why require not more 5 runs and lastly one second of wait.
    while not flag and iteration > 0:
        all_volumes = hosts.all.zos_operator(cmd="d u,dasd,online,,65536")
        time.sleep(1)
        if all_volumes is not None:
            for volume in all_volumes.contacted.values():
                temp = volume.get('content')
                if temp is not None:
                    all_volumes_list += temp
            flag = True if len(all_volumes_list) > 5 else False
        iteration -= 1
    # Check if the volume is of storage and is active on prefer but also online as a correct option
    for info in all_volumes_list:
        if "ACTIVATED" in info or "-D U," in info or "UNIT" in info:
            continue
        vol_w_info = info.split()
        if len(vol_w_info)>3:
            if vol_w_info[2] == 'O' and vol_w_info[4] == "STRG/RSDNT":
                storage_online.append(vol_w_info[3])
    # Insert a volumes for the class ls_Volumes to give flag of in_use and correct manage
    for vol in storage_online:
        list_volumes.append(vol)
    if prefer_vols is not None:
        list(map(str, prefer_vols))
        prefer_vols.extend(list_volumes)
        prefer_vols = list(filter(lambda item: item is not None, prefer_vols))
        return prefer_vols
    else:
        return list_volumes


def read_test_config(path):
    p = path
    with open(p, 'r') as file:
        config = yaml.safe_load(file)
    if "VOLUMES" in config.keys():
        if len(config["VOLUMES"]) > 0:
            return config["VOLUMES"]
    else:
        return None

def get_volumes_with_vvds( ansible_zos_module, volumes_on_system):
    """
    Get a list of volumes that contain a VVDS, if no volume has a VVDS then
    creates one on any volume.
    """
    volumes_with_vvds = find_volumes_with_vvds(ansible_zos_module, volumes_on_system)
    if len(volumes_with_vvds) == 0 and len(volumes_on_system) > 0:
        volumes_with_vvds = list()
        for volume in volumes_on_system:
            if create_vvds_on_volume(ansible_zos_module, volume):
                volumes_with_vvds.append(volume)
    return volumes_with_vvds

def find_volumes_with_vvds( ansible_zos_module, volumes_on_system):
    """
    Fetches all VVDS in the system and returns a list of volumes for
    which there are VVDS.
    """
    hosts = ansible_zos_module
    vls_result = hosts.all.shell(cmd="vls SYS1.VVDS.*")
    for vls_res in vls_result.contacted.values():
        vvds_list = vls_res.get("stdout")
    return [volume for volume in volumes_on_system if volume in vvds_list]

def create_vvds_on_volume( ansible_zos_module, volume):
    """
    Creates a vvds on a volume by allocating a small VSAM and then deleting it.
    """
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name(mlq_size=7, llq_size=7)
    hosts.all.shell(cmd=f"dtouch -tesds -s10K -V{volume} {data_set_name}")
    # Remove that dataset
    hosts.all.shell(cmd=f"drm {data_set_name}")
    # Verify that the VVDS is in place
    vls_result = hosts.all.shell(cmd=f"vls SYS1.VVDS.V{volume} ")
    for vls_res in vls_result.contacted.values():
        if vls_res.get("rc") == 0:
            return True
    return False


def get_volume_and_unit(ansible_zos_module, path):
    """Get an array of available volumes, and it's unit"""
    # Using the command d u,dasd,online to fill an array of available volumes with the priority
    # of of actives (A) and storage (STRG) first then online (O) and storage and if is needed, the
    # private ones but actives then to get a flag if is available or not every volumes
    # is a instance of a class to manage the use.
    hosts = ansible_zos_module
    list_volumes = []
    all_volumes_list = []
    priv_online = []
    flag = False
    iteration = 5
    volumes_datasets = []
    # The first run of the command d u,dasd,online,,n in the system can conclude with empty data
    # to ensure get volumes is why require not more 5 runs and lastly one second of wait.
    while not flag and iteration > 0:
        all_volumes = hosts.all.zos_operator(cmd="d u,dasd,online,,65536")
        time.sleep(1)
        if all_volumes is not None:
            for volume in all_volumes.contacted.values():
                temp = volume.get('content')
                if temp is not None:
                    all_volumes_list += temp
            flag = True if len(all_volumes_list) > 5 else False
        iteration -= 1
    # Check if the volume is of storage and is active on prefer but also online as a correct option
    for info in all_volumes_list:
        if "ACTIVATED" in info or "-D U," in info or "UNIT" in info:
            continue
        vol_w_info = info.split()

        if len(vol_w_info)>3:
            if vol_w_info[2] == 'O' and "USER" in vol_w_info[3] and vol_w_info[4] == "PRIV/RSDNT":

                # The next creation of dataset is to validate if the volume will work properly for the test suite
                dataset = get_tmp_ds_name()
                valid_creation = hosts.all.zos_data_set(name=dataset, type='pds', volumes=f'{vol_w_info[3]}')

                for valid in valid_creation.contacted.values():
                    if valid.get("changed") == "false":
                        valid = False
                    else:
                        valid = True
                        hosts.all.zos_data_set(name=dataset, state="absent")

                # When is a valid volume is required to get the datasets present on the volume
                if valid:
                    ds_on_vol = hosts.all.shell(cmd=f"vtocls {vol_w_info[3]}")
                    for ds in ds_on_vol.contacted.values():
                        datasets = str(ds.get("stdout")).split("\n")
                        volumes_datasets.append([len(datasets), vol_w_info[3], vol_w_info[0]])

    # To ensure we use the best volume available the order of the volumes will help
    sorted_volumes = sorted(volumes_datasets, key=lambda x: x[0], reverse=False)
    list_volumes = [[x[1], x[2]] for x in sorted_volumes]

    return list_volumes
