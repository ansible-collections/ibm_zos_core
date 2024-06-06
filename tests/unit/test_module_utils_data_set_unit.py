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

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import MVSCmdExecError

IMPORT_NAME = "ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set"


class DummyModule(object):
    """Used in place of Ansible's module
    so we can easily mock the desired behavior."""

    def __init__(self, rc=0, stdout="", stderr=""):
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr

    def run_command(self, *args, **kwargs):
        return (self.rc, self.stdout, self.stderr)


# Unit tests are intended to exercise code paths (not test for functionality).

# These unit tests are NOT run on any z/OS system, so hard-coded data set names will not matter.
data_set_name = "USER.PRIVATE.TESTDS"

stdout_ds_in_catatlog = """0
  LISTCAT ENTRIES('{0}')
0NONVSAM ------- {0}
      IN-CAT --- CATALOG.SVPLEX9.MASTER
1IDCAMS  SYSTEM SERVICES  """.format(data_set_name)

stdout_ds_not_in_catalog="""0
  LISTCAT ENTRIES('{0}')
0IDC3012I ENTRY {0} NOT FOUND
 IDC3009I ** VSAM CATALOG RETURN CODE IS 8 - REASON CODE IS IGG0CLEG-42
 IDC1566I ** {0} NOT LISTED""".format(data_set_name)

# passing in a lowercase data set causes idcams to fail.
# this behavior isn't possible via ansible because we upper-case the input.
stdout_mvscmd_failed="""0
  LISTCAT ENTRIES('...................')
0IDC3203I ITEM '...................' DOES NOT ADHERE TO RESTRICTIONS
0IDC3202I ABOVE TEXT BYPASSED UNTIL NEXT COMMAND. CONDITION CODE IS 12
0        
0IDC0002I IDCAMS PROCESSING COMPLETE. MAXIMUM CONDITION CODE WAS 12"""


@pytest.mark.parametrize(
    ("rc, stdout, expected_return, expected_exception_type"),
    [
        (0, stdout_ds_in_catatlog, True, None),
        (4, stdout_ds_not_in_catalog, False, None),
        (12, stdout_mvscmd_failed, None, MVSCmdExecError)
    ],
)
def test_dataset_cataloged_unit(zos_import_mocker, rc, stdout, expected_return, expected_exception_type):
    mocker, importer = zos_import_mocker
    zos_module_util_data_set = importer(IMPORT_NAME)
    mocker.patch(
        "{0}.AnsibleModuleHelper".format(IMPORT_NAME),
        create=True,
        return_value=DummyModule(rc=rc, stdout=stdout),
    )


    results = None
    error_raised = False
    try:
        results = zos_module_util_data_set.DataSet.data_set_cataloged(data_set_name)
    except Exception as e:
        error_raised = True
        assert type(e) == expected_exception_type
    finally:
        if not expected_exception_type:
            assert not error_raised
        assert results == expected_return