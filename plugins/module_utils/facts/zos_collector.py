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
        zos_test_facts['test'] = 'testing'

        # zos_test_facts['zos_aa_test1'] = 'testing-a1'
        # zos_test_facts['zos_aa_test2'] = 'testing-a2'
        # zos_test_facts['zos_aa_test3'] = 'testing-a3'
        # zos_test_facts['zos_bb_test1'] = 'testing-b1'
        # zos_test_facts['zos_bb_test2'] = 'testing-b2'
        # zos_test_facts['zos_bb_test3'] = 'testing-b3'
        # zos_test_facts['zos_bb_test4'] = 'testing-b4'
        # zos_test_facts['zos_cc_test1'] = 'testing-c1'
        # zos_test_facts['zos_cc_test2'] = 'testing-c2'

        # cmd = 'sleep 5'
        # rc, fcinfo_out, err = module.run_command(cmd)
        # # rc, fcinfo_out, err = module.run_command(cmd, use_unsafe_shell=True)

        # zos_test_facts['sleep50'] = "slept for 50"

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


