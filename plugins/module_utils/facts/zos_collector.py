# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.facts.collector import BaseFactCollector

import sys

class ZosFactCollector(BaseFactCollector):
    # name and members of _fact_ids are valid entries for the gather_subset param
    name = 'zos_a'
    _fact_ids = set(['zos_b',
                    'system',
                    'zos_c'])

    def collect(self, module, collected_facts):
        zos_test_facts = {}
        zos_test_facts['test'] = 'testing'

        # TODO - remove fully qualified path to opercmd (use path from env vars instead)
        cmd = '/ZOAU/bin/opercmd D SYMBOLS'
        rc, fcinfo_out, err = module.run_command(cmd)
        # rc, fcinfo_out, err = module.run_command(cmd, use_unsafe_shell=True)

        zos_test_facts['z_symbols'] = {
            'rc': rc,
            'fcinfo_out': fcinfo_out,
            'err': err
        }

        return zos_test_facts


