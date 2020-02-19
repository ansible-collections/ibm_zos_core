# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

import sys
import unittest
from unittest.mock import MagicMock, Mock
import pytest

IMPORT_NAME = 'ibm_zos_core.plugins.modules.zos_job_submit'



class DummyModule(object):
    """Used in place of Ansible's module 
    so we can easily mock the desired behavior."""
    
    def __init__(self, rc, stdout, stderr):
        self.rc = 0
        self.stdout = stdout
        self.stderr = stderr

    def run_command(self, *args, **kwargs):
        return (self.rc, self.stdout, self.stderr)

# class TestSubmit(unittest.TestCase):
'''src, return_value, expected'''
test_data_PDS = [
    ('BJMAXY.HILL3(SAMPLE)', 'JOB12345', True),
    ('BJMAXY.HILL3(LONGRUN)', 'JOB12345', True),
    ('', None, False)
]


@pytest.mark.parametrize("src, return_value, expected", test_data_PDS)
def test_submit_pds_jcl(zos_import_mocker, src, return_value, expected):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.Jobs.submit', create=True, return_value=return_value)
    try:
        jobs.submit_pds_jcl(src)
    except jobs.SubmitJCLError:
        passed = False
    assert passed == expected


'''stdin, stdout, stderr, pid, returncode'''

comm_return_tuple1 = (0,'JOB12345', '')
comm_return_tuple2 = (0,'', 'Not accepted by JES')

test_data_USS = [
    ('/u/test/sample.jcl', comm_return_tuple1, True),
    ('/u/test/test2.jcl', comm_return_tuple2, False)
]
@pytest.mark.parametrize("src, return_value, expected", test_data_USS)
def test_submit_uss_jcl(zos_import_mocker, src, return_value, expected):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = True
    module = DummyModule(*return_value)    
    try:
        jobs.submit_uss_jcl(src,module)
    except jobs.SubmitJCLError:
        passed = False
    assert passed == expected



return_tuple1 = (0, 'JOB12345', '')
return_tuple2 = (0, '', 'Not accepted by JES')

test_data_PDS_in_volume = [
    ('BJMAXY.UNCATLOG.JCL(SAMPLE)',  '', return_tuple1, True),
    ('BJMAXY.UNCATLOG.JCL(SAMPLE)',  'P2SS01', return_tuple2, False),
]
@pytest.mark.parametrize("src, volume, return_value, expected", test_data_PDS_in_volume)
def test_submit_jcl_in_volume(zos_import_mocker, src, volume, return_value, expected):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = True
    module = DummyModule(*return_value)
    mocker.patch('{0}.copy_rexx_and_run'.format(
        IMPORT_NAME), create=True, return_value=return_value)    
    try:
        jobs.submit_jcl_in_volume(src, volume, module)
    except jobs.SubmitJCLError:
        passed = False
    assert passed == expected


list_return_dict = [
    {'owner': 'TESTER', 'name': 'TEST', 'id': 'JOB12345', 'status': 'AC', 'return': '0'}
]
listDD_return_dict = [
    {'stepname': 'JES2', 'dataset': 'JESMSGLG', 'format': 'VB' },
]
output_dict = [
    {'stepname': 'JES2',
     'dataset': 'JESMSGLG',
     'DDoutput': 'ICH70001I BJMAXY   LAST ACCESS AT 08:35:35 ON FRIDAY, DECEMBER 6, 2019 IEFA111I TEST IS USING THE FOLLOWING JOB RELATED SETTINGS:',}
]
test_data_get_info = [
    ('JOB12345', list_return_dict, listDD_return_dict ,output_dict, True),
    (None, None, [], [], False)
]
@pytest.mark.parametrize("jobid,  zoau_list_return_value, zoau_listDD_returned_value, zoau_output_dict, expected", test_data_get_info)
def test_get_job_info(zos_import_mocker,jobid,  zoau_list_return_value, zoau_listDD_returned_value, zoau_output_dict, expected):
    mocker, importer = zos_import_mocker
    jobs = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.Jobs.list_dds', create=True, return_value=zoau_listDD_returned_value)
    mocker.patch('zoautil_py.Jobs.list', create=True, return_value=zoau_list_return_value)
    mocker.patch('zoautil_py.Jobs.read_output',create=True, return_value= zoau_output_dict)
    try:
        jobs.get_job_info(jobid, True)
    except jobs.SubmitJCLError:
        passed = False
    assert passed == expected
