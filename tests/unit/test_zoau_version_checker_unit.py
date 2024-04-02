# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023
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

from ibm_zos_core.plugins.module_utils.zoau_version_checker import (
    get_zoau_version_str,
    is_valid_version_string,
    is_zoau_version_higher_than
)

import pytest, mock
import types

# used in patch decorators below
IMPORT_NAME = "ibm_zos_core.plugins.module_utils.zoau_version_checker"

# Tests for zoau_version_checker

zoaversion_output = [

    (['1','0','2'], "2020/03/03 19:24:41 CUT V1.0.2"),
    (['1','0','3'], "2020/05/06 18:17:13 CUT V1.0.3"),
    (['1','0','3'], "2020/07/07 14:54:31 CUT V1.0.3"),
    (['1','1','0'], "2020/08/05 13:08:52 CUT V1.1.0"),
    (['1','1','0'], "2020/08/20 12:50:07 CUT V1.1.0"),
    (['1','1','0'], "2020/09/16 13:41:25 CUT V1.1.0"),
    (['1','1','0'], "2020/09/25 14:07:34 CUT V1.1.0"),
    (['1','1','1'], "2021/03/26 15:44:32 CUT V1.1.1"),
    (['1','2','0'], "2021/07/07 22:36:30 CUT V1.2.0"),
    (['1','2','0'], "2021/08/05 22:12:58 CUT V1.2.0"),
    (['1','2','1'], "2022/07/12 18:35:28 CUT V1.2.1"),
    (['1','2','1'], "2022/08/17 21:25:13 CUT V1.2.1"),
    (['1','2','1'], "2022/08/25 21:44:21 CUT V1.2.1 31163ab 1856"),
    (['1','2','1'], "2022/09/07 15:26:50 CUT V1.2.1 d2f6557 1880"),
    (['1','2','1','1'], ""),
    (['1','2','3'], "2022/12/03 13:33:22 CUT V1.2.3 6113dc9 2512"),
    (['1','2','2'], "2022/12/06 20:44:00 CUT V1.2.2 ee30137 2525"),
    (['1','2','3'], "2023/03/16 18:17:00 CUT V1.2.3 1aa591fb 2148 PH50145"),
    (['1','2','3','1'], ""),
    (['1','2','3','2'], ""),
    (['1','2','4','0'], "2023/06/02 13:28:30 CUT V1.2.4.0 3b866824 2873 PH52034 826 267d9646"),
    (['1','2','4','1'], ""),
    (['1','2','4','2'], ""),
    (['1','2','4','3'], ""),
    (['1','2','4','4'], ""),
    (['1','2','4','5'], ""),
    (['1','2','5','0'], ""),
    (['1','2','5','1'], ""),
    (['1','2','5','2'], ""),
    (['1','2','5','3'], ""),
    (['1','2','5','4'], ""),
    (['1','2','5','6'], ""),

]


@pytest.mark.parametrize("version_string, zoaversion", zoaversion_output)
@mock.patch('subprocess.run')
def test_get_zoau_version_str(mocker, version_string, zoaversion):
    # 'get_zoau_version_str' makes a call to 'zoaversion' on the target host by
    # calling 'subprocess.run', which returns an object with an attr 'stdout'
    # that contains the byte string of the console output. The following mocks
    # this behavior so the code can be tested without making a call to a host.
    # Instead, zoaversion output for various versions of ZOAU are stored in the
    # list of tuples 'zoaversion_output' above and returned by the mocked call
    # to 'subprocess.run' after being converted to bytes. SimpleNamespace is an
    # object subclass which allows for attributes to be set/removed. In our
    # case, 'get_zoau_version_str' expects a 'stdout' attribute in the return
    # struct of 'subprocess.run', which we mock via SimpleNamespace.

    mocker.return_value = types.SimpleNamespace(
            stdout = bytes(zoaversion, 'utf-8'),
        )

    assert version_string == get_zoau_version_str()


@pytest.mark.parametrize("version_string, zoaversion", zoaversion_output)
def test_is_valid_version_string(version_string,zoaversion):
    # The first parameter in our zoaversion_output list of tuples above is the
    # return value of the function 'get_zoau_version_str' in the form of
    # ['#','#','#'] or ['#','#','#','#']. A 'join' str operation with a dot(.)
    # yields "#.#.#" or "#.#.#.#". And since these values are taken from this
    # list, they can all be expected to be valid ZOAU verison strings.

    assert True == is_valid_version_string('.'.join(version_string))


test_data = [
#   result, "sytem-level" ZOAU  >=  min-ZOAU
    (True,     ['1', '2', '1'],         "1.2.1"),
    (True,     ['1', '2', '3'],         "1.2.1"),
    (True,     ['1', '2', '4', '0'],    "1.2.2"),

    (False,     ['1', '1', '1'],        "1.2.3"),
    (False,     ['1', '1', '1'],        "1.2.4.0"),
    (False,     ['1', '2', '0', '1'],    "1.2.1"),
]


@pytest.mark.parametrize("expected, sys_zoau, min_version_str", test_data)
@mock.patch(IMPORT_NAME+'.get_zoau_version_str')
def test_is_zoau_version_higher_than(mocker, expected, sys_zoau, min_version_str):
    # The 'is_zoau_version_higher_than' function calls 'get_zoau_version_str' to
    # get the ZOAU version string from the system. We mock that call and provide
    # our own "system" level ZOAU version str to compare against our provided
    # minimum ZOAU version string.

    mocker.return_value = sys_zoau
    assert expected == is_zoau_version_higher_than(min_version_str)
