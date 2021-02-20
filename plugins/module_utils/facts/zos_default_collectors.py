# Copyright (c) IBM Corporation 2019, 2020
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

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.facts.zos_collector import ZosFactCollector


# from ansible.module_utils.facts import default_collectors
from ansible.module_utils.facts.system.python import PythonFactCollector
from ansible.module_utils.facts.system.platform import PlatformFactCollector
from ansible.module_utils.facts.system.distribution import DistributionFactCollector


from ansible.module_utils.facts.virtual.base import VirtualCollector
from ansible.module_utils.facts.virtual.dragonfly import DragonFlyVirtualCollector
from ansible.module_utils.facts.virtual.freebsd import FreeBSDVirtualCollector
from ansible.module_utils.facts.virtual.hpux import HPUXVirtualCollector
from ansible.module_utils.facts.virtual.linux import LinuxVirtualCollector
from ansible.module_utils.facts.virtual.netbsd import NetBSDVirtualCollector
from ansible.module_utils.facts.virtual.openbsd import OpenBSDVirtualCollector
from ansible.module_utils.facts.virtual.sunos import SunOSVirtualCollector

my_list = [PythonFactCollector, PlatformFactCollector, DistributionFactCollector]


# virtual, this might also limit hardware/networking
_virtual = [
    VirtualCollector,
    DragonFlyVirtualCollector,
    FreeBSDVirtualCollector,
    LinuxVirtualCollector,
    OpenBSDVirtualCollector,
    NetBSDVirtualCollector,
    SunOSVirtualCollector,
    HPUXVirtualCollector
]

collectors = [ZosFactCollector] + [PythonFactCollector] + [PlatformFactCollector]
# collectors = [PlatformFactCollector]
# collectors = [PythonFactCollector]