# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
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
      # zos_facts['test_hard_coded_fact'] = 'i_am_a_hard_coded_fact'
      # zos_other_facts = json.loads('{"test9" : "77" , "test8" : "44" }')
      # zstr = '{"test9" : "77" , "test8" : "44" }'

      # TODO - add logic here to figure out which call to zinfo to make
      # zinfo -t aaa -t bbb -t ccc ... vs zinfo -a
      # Maybe just a combination of '-t's for now (and not ever call -a)


      cmd = "/u/oeusr01/zinfohelper -t ipl -t exp"
      rc, fcinfo_out, err = module.run_command(cmd, encoding=None)
      decode_str = fcinfo_out.decode('utf-8')

      # zos_facts['run_command'] = {
      #    'rc': rc,
      #    'fcinfo_out': fcinfo_out,
      #    'err': err
      # }

   # TODO - implement actual error handling

      try:

         zos_facts['zinfo'] = json.loads(decode_str)

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