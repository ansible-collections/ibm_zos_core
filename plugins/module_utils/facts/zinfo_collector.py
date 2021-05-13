# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
from json.decoder import JSONDecodeError
__metaclass__ = type


import json

from ansible.module_utils.facts.collector import BaseFactCollector
# from plugins.module_utils.facts.zos_collector import ZosFactCollector


class ZinfoCollector(BaseFactCollector):
   # name and members of _fact_ids are valid entries for the gather_subset param
   name = 'zos_c_test'
   _fact_ids = set()

   def collect(self, module, collected_facts):

      zos_c_pgm_facts = {}
      zos_c_pgm_facts['test_c_pgm'] = 'testing_zos_c'

      cmd = "/u/oeusr01/zinfohelper"
      rc, fcinfo_out, err = module.run_command(cmd)
      # rc, fcinfo_out, err = module.run_command(cmd, use_unsafe_shell=True)
      zos_c_pgm_facts['z_c_run'] = {
         'rc': rc,
         'fcinfo_out': fcinfo_out,
         'err': err
      }

      print('hi')
      print('type - ' + str(type(fcinfo_out)))
      print(fcinfo_out)
      print('bytes')
      print(bytes(fcinfo_out, 'utf-8'))
      print('bye')

      zos_other_facts = json.loads('{"test9" : "77" , "test8" : "44" }')

      zos_c_pgm_facts.update(zos_other_facts)

      try:
         print('try ------------------------- block')
         # print(json.loads(fcinfo_out))
         print(bytes(fcinfo_out, 'utf-8').hex())
         # zos_zinfo = json.loads(fcinfo_out)
      except JSONDecodeError as e:

         print('json decode error')
         print(e)
         print('///')

         pass
      except:
         print("Errored out...")
         pass

      return zos_c_pgm_facts



# 27 7b20 2274657374 22203a20372c20 227465737432 22203a2034207d 27

# 7b20 5c 2274657374 5c 22203a20372c20 5c 227465737432 5c 22203a2034207d