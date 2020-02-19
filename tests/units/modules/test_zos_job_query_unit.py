# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

import sys
from mock import MagicMock
import pytest
from pytest_mock import mocker

IMPORT_NAME = 'ibm_zos_core.plugins.modules.zos_job_query'

dummy_dict1 = {
    'job_name': 'iyk*'
}

dummy_dict2 = {
    'job_name': 'iyk'
}

dummy_dict3 = {
    'job_name': 'IYK3ZNA*',
    'owner': 'BROWNAD'
}

dummy_dict4 = {
    'job_name': 'IYK3ZNA*',
    'job_id': 'JOB01427'
}

dummy_dict5 = {
    'job_name': 'IYK3ZNA*',
    'job_id': 'JOB01427',
    'owner': 'BROWNAD'
}

dummy_dict1_invalid = {
    'job_name': 'MORETHAN8CHARS'
}

dummy_dict2_invalid = {
    'job_name': 'IYK3ZNA*',
    'job_id': 'JOB014278'
}


dummy_return_dict = [
    {
        'owner': 'BROWNAD', 
        'name': 'IYK3Z0R9', 
        'id': 'JOB01427', 
        'status': 'AC',
        'return': '?'
    }, 
    {
        'owner': 'XIAOPIN', 
        'name': 'IYK3Z0RP', 
        'id': 'STC75334', 
        'status': 'CANCELED', 
        'return': '?'
    },
    {
        'owner': 'XIAOPIN', 
        'name': 'IYK3Z0RP', 
        'id': 'JOB01427', 
        'status': 'ABEND', 
        'return': 'S222'
    }
]

test_data = [
    (dummy_dict1, dummy_return_dict, True),
    (dummy_dict1, [],False),
    (dummy_dict2, dummy_return_dict,True),
    (dummy_dict3, dummy_return_dict,True),
    (dummy_dict4, dummy_return_dict,True),
    (dummy_dict5, dummy_return_dict,True),
]

@pytest.mark.parametrize("test_input_args,zoau_return_value,expected", test_data)
def test_list_jobs_with_wildcard(zos_import_mocker, test_input_args, zoau_return_value, expected):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.Jobs.list', create=True, return_value=zoau_return_value)
    try:
        jobs.query_jobs(test_input_args)
    except RuntimeError:
        passed = False
    assert passed == expected

def test_invalid_job_name(zos_import_mocker):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = False
    try:
        jobs.validate_arguments(dummy_dict1_invalid)
    except RuntimeError:
        passed = True
    assert passed == True

def test_invalid_job_id(zos_import_mocker):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = False
    try:
        jobs.validate_arguments(dummy_dict2_invalid)
    except RuntimeError:
        passed = True
    assert passed == True

def test_parsing_jobs(zos_import_mocker):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = False
    try:
        jobs_out = jobs.parsing_jobs(dummy_return_dict)
    except RuntimeError:
        passed = False
    assert len(jobs_out) == 3
