# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

import pytest
from unittest.mock import MagicMock, Mock

IMPORT_NAME = 'ibm_zos_core.plugins.modules.zos_job_output'

dummy_return_dict = (
    0, '{"jobs":[{"changed":"false","class":"","content-type":"STC","ddnames":[],"failed":"false","job_id":"STC02502","job_name":"TCPIP","owner":"TCPIP","ret_code":{"msg":"CC 0000"},"subsystem":"S0W1"}]}', '')
no_job_return_dict = (0, '{"jobs":[]}', '')

test_data = [
    ("NO_JOB_ID", "*", "*", "?", no_job_return_dict, True),
    ("*", "NO_JOB_NAME", "*", "?", no_job_return_dict, True),
    ("*", "*", "NO_OWNER", "?", no_job_return_dict, True),
    ("*", "*", "*", "?", dummy_return_dict, True)
]
@pytest.mark.parametrize("job_id, job_name, owner, ddname, zoau_return_value, expected", test_data)
def test_job_out(zos_import_mocker, job_id, job_name, owner, ddname, zoau_return_value, expected):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = True
    module = MagicMock()
    module.run_command = Mock(return_value=zoau_return_value)
    try:
        jobs.get_job_json(job_id, job_name, owner, ddname, module)
    except RuntimeError:
        passed = False
    assert passed == expected
