# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.facts.collector import BaseFactCollector

import sys

class ZosFactCollector(BaseFactCollector):
    # name and members of _fact_ids are valid entries for the gather_subset param
    # _platform = 'OS/380' -- double check
    name = 'zos_a'
    _fact_ids = set(['zos_b',
                    'system',
                    'zos_c',
                    'zos'])

    def collect(self, module, collected_facts):
        zos_test_facts = {}
        zos_test_facts['test_base_collector_fact'] = 'testing-base'


        return zos_test_facts


