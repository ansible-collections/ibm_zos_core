# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
from json.decoder import JSONDecodeError
__metaclass__ = type


import json

from ansible.module_utils.facts.collector import BaseFactCollector
# from plugins.module_utils.facts.zos_collector import ZosFactCollector


class ZinfoCollector(BaseFactCollector):
   # name and members of _fact_ids are valid entries for the gather_subset param
   name = 'zos_test'
   _fact_ids = set()

   def collect(self, module, collected_facts):

      zos_facts = {}
      zos_facts['test_hard_coded_fact'] = 'i_am_a_hard_coded_fact'
      # zos_other_facts = json.loads('{"test9" : "77" , "test8" : "44" }')

      cmd = "/u/oeusr01/zinfohelper"
      rc, fcinfo_out, err = module.run_command(cmd)
      # rc, fcinfo_out, err = module.run_command(cmd, use_unsafe_shell=True)
      zos_facts['run_command'] = {
         'rc': rc,
         'fcinfo_out': fcinfo_out,
         'err': err
      }

   # TODO - implement actual error handling

      try:
         iplinfo = json.loads(fcinfo_out.strip())
         zos_facts['iplinfo'] = iplinfo

      except Exception as e:
         print(e)
         pass
         # try:
         #    print(' ---- begin try block ---- ')
         #    # print(json.loads(fcinfo_out))
         #    # print(bytes(fcinfo_out, 'utf-8').hex())
         #    zos_zinfo = json.loads(fcinfo_out.strip())
         # except JSONDecodeError as e:

         #    print(' *** json decode error ***')
         #    print(e)
         #    print('///')

         #    pass
         # except:
         #    print("Errored out...")
         #    pass

      return zos_facts
