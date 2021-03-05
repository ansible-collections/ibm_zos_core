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

# from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.facts.zos_collector import ZosFactCollector

# from ansible.module_utils.facts import default_collectors
from ansible.module_utils.facts.system.python import PythonFactCollector
from ansible.module_utils.facts.system.platform import PlatformFactCollector
from ansible.module_utils.facts.system.distribution import DistributionFactCollector

from ansible.module_utils.facts.system.distribution import DistributionFactCollector
from ansible.module_utils.facts.system.date_time import DateTimeFactCollector
from ansible.module_utils.facts.system.env import EnvFactCollector
from ansible.module_utils.facts.system.platform import PlatformFactCollector
from ansible.module_utils.facts.system.python import PythonFactCollector
from ansible.module_utils.facts.system.service_mgr import ServiceMgrFactCollector
from ansible.module_utils.facts.system.ssh_pub_keys import SshPubKeyFactCollector
from ansible.module_utils.facts.system.user import UserFactCollector


# these should always be first due to most other facts depending on them
_base = [
    PlatformFactCollector,
    DistributionFactCollector,
]

# general info, not required but probably useful for other facts
_general = [
    PythonFactCollector,
    ServiceMgrFactCollector,
    DateTimeFactCollector,
    EnvFactCollector,
    SshPubKeyFactCollector,
    UserFactCollector
]

# _zos = [
#     ZosFactCollector
# ]

# other fact sources
_extra_facts = [
    # LocalFactCollector
]

collectors = _base + _general + _extra_facts #+ _zos