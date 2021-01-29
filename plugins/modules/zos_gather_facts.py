#!/usr/bin/python
# -*- coding: utf-8 -*-

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


DOCUMENTATION = r"""
---
module: zos_gather_facts
version_added: "999.999" #TODO
short_description: Gathers facts about remote z/OS hosts.
description:
  - Gathers facts from remote z/OS hosts. Gather scripts are a combination of ported Ansible engine scripts, unique z/OS scripts which interface with USS, and any scripts provided by other zos collections.
  - This module emulates ansible's gather_facts module but specificallly for hosts running z/OS.
  # - TODO - actually the setup module is the default one, gather_facts needs to be specified
author: "Ketan Kelkar (@ketankelkar)"
options:
  fact_path:
    description: # TODO - determine if z/OS will support this feature
    required: false
    default:

  filter:
    description:
      - if supplied, only return facts that match this shell-style (fnmatch) wildcard.
    required: false
    default: "*"
    type: str

  gather_subset:
    description:
      - If supplied, restrict the additional facts collected to the given subset.
      - Possbile values: C(all), C(min), C(harware), C(network), C(virtual), C(ohai), C(facter).
      - TODO - determine whether z/OS have compatibility with ohai and/or facter?
      - Can specify a list of values to specify a larger subset.
      - Values can also be used with an initial C(!) to specify that specific subset should not be collected.
      - EG: C(!hardware, !network, !virtual, !ohai, !facter).
      - If C(!all) is specified then only the min susbet is collected. To avoid collecting even the min subset specify C(!all, !min).
      - To collect only specific facts, use C(!all, !min) and specify the particular fact subsets.
      - Use the filter parameter if you do not want to display some collected facts.
    required: false
    default: "all"
    type: str

  gather_timeout:
    description:
      - Set the default timeout in seconds for indivual fact gathering.
    required: false
    default: 10
    type: str

notes: This module is modeled off of Ansible's default setup module for gathering facts.
https://docs.ansible.com/ansible/latest/collections/ansible/builtin/setup_module.html#setup-module

"""


EXAMPLES = r"""
- name: Gather all (default) available facts from a z/OS host.
  zos_gather_facts:

- name: Gather only the min subset of facts from a z/OS host.
  zos_gather_facts:
    gather_subset: min

- name: Gather all facts except those in the virtual subset from a z/OS host.
  zos_gather_facts:
    gather_subset:
      - '!virtual'

- name: Gather facts ONLY from the network subset from a z/OS host.
  zos_gather_facts:
    gather_subset:
      - '!all'
      - '!min'
      - network

- name: Spend a maximum of 2 seconds gathering facts only in the network subset from a z/OS host..
  zos_gather_facts:
    gather_subset: network
    gather_timeout: 2

- name: Gather all facts from the min subset that match the wildcard from a z/OS host.
  zos_gather_facts:
    filter: 'zos*' # TODO - pick an actualy viable wildcad string for this filter
    gather_subset: min

"""


# will be built out as gather scripts are integrated into the module.
# following the example of nxos_facts module: https://github.com/ansible/ansible/blob/98f804ecb44278628070829bd1841ca51476f7b9/lib/ansible/modules/network/nxos/nxos_facts.py

RETURN = r"""
file:


"""

from ansible.module_utils.basic import AnsibleModule


# TODO remove following imports if unused
from ansible.module_utils.facts.namespace import PrefixFactNamespace
from ansible.module_utils.facts import ansible_collector

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.facts import zos_default_collectors


def main():
    module = AnsibleModule(
        argument_spec=dict(
            gather_subset=dict(default=["all"], required=False, type='list', elements='str'),
            gather_timeout=dict(default=10, required=False, type='int'),
            filter=dict(default=[], required=False, type='list', elements='str'),
            fact_path=dict(default='/etc/ansible/facts.d', required=False, type='path'),
        ),
        supports_check_mode=True,
    )


    gather_subset = module.params['gather_subset']
    gather_timeout = module.params['gather_timeout']
    filter_spec = module.params['filter']


    all_collector_classes = zos_default_collectors.collectors

    # TODO - change from ansible to IBMZ for z scripts?
    namespace = PrefixFactNamespace(namespace_name='zos_ansible', prefix='zos_ansible_')

    fact_collector = \
        ansible_collector.get_ansible_collector(
            all_collector_classes=all_collector_classes,
            namespace=namespace,
            filter_spec=filter_spec,
            gather_subset=gather_subset,
            gather_timeout=gather_timeout,
            minimal_gather_subset=None)

    facts_dict = fact_collector.collect(module=module)

    module.exit_json(zos_ansible_facts=facts_dict)

if __name__ == '__main__':
    main()