# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division

import os
import sys
import warnings

import ansible.constants
import ansible.errors
import ansible.utils
import pytest
from pprint import pprint
__metaclass__ = type

# TODO: determine if data set names need to be more generic for testcases
# TODO: add additional tests to check additional data set creation parameter combinations


data_set_types = [
    ('pds'),
    ('seq'),
    ('pdse'),
    ('esds'),
    ('rrds'),
    ('lds'),
    (None),
]

@pytest.mark.parametrize("dstype", data_set_types)
def data_set_typesset_creation_when_present_no_replace(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='imstestl.ims1.test05', state='present', type=dstype, replace=True)
    results = hosts.all.zos_data_set(name='imstestl.ims1.test05', state='present', type=dstype)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == False
        assert result.get('module_stderr') == None
        
@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_replace(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='imstestl.ims1.test05', state='present', type=dstype, replace=True)
    results = hosts.all.zos_data_set(name='imstestl.ims1.test05', state='present', type=dstype, replace=True)
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None

@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='imstestl.ims1.test05', state='absent')
    results = hosts.all.zos_data_set(name='imstestl.ims1.test05', state='present', type=dstype)
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None

@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_deletion_when_present(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='imstestl.ims1.test05', state='present', type=dstype)
    results = hosts.all.zos_data_set(name='imstestl.ims1.test05', state='absent')
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'absent'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None
        
def test_data_set_deletion_when_absent(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name='imstestl.ims1.test05', state='absent')
    results = hosts.all.zos_data_set(name='imstestl.ims1.test05', state='absent')
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'absent'
        assert result.get('changed') == False
        assert result.get('module_stderr') == None
    
def test_batch_data_set_creation_and_deletion(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(batch=[
        {
            'name': 'imstestl.ims1.test05',
            'state': 'absent'
        },
        {
            'name': 'imstestl.ims1.test05',
            'type': 'pds',
            'state': 'present'
        },
        {
            'name': 'imstestl.ims1.test05',
            'state': 'absent'
        },
    ])
    for result in results.contacted.values():
        assert result.get('changed') == True
        assert result.get('module_stderr') == None
        
def test_batch_data_set_and_member_creation(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(batch=[
        {
            'name': 'imstestl.ims1.test05',
            'type': 'pds',
        },
        {
            'name': 'imstestl.ims1.test05(newmem1)',
            'type': 'member',
        },
        {
            'name': 'imstestl.ims1.test05(newmem2)',
            'type': 'member',
            'state': 'present'
        },
        {
            'name': 'imstestl.ims1.test05',
            'state': 'absent'
        },
    ])
    for result in results.contacted.values():
        assert result.get('changed') == True
        assert result.get('module_stderr') == None
        
def test_repeated_operations(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(
        name='USER.PRIVATE.TEST4',
        type='PDS',
        size='5CYL',
        record_length=15,
        replace=True
    )
    
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None
        
    results = hosts.all.zos_data_set(
        name='USER.PRIVATE.TEST4',
        type='PDS',
        # size='15TRK',
        # record_length=30,
        replace=True
    )

    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None

    results = hosts.all.zos_data_set(
        name='USER.PRIVATE.TEST4(testme)',
        type='MEMBER',
        replace=True
    )

    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None

    results = hosts.all.zos_data_set(
        name='USER.PRIVATE.TEST4(testme)',
        type='MEMBER' 
    )

    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'present'
        assert result.get('changed') == False
        assert result.get('module_stderr') == None

    results = hosts.all.zos_data_set(
        name='USER.PRIVATE.TEST4(testme)',
        type='MEMBER',
        state='absent'
    )

    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'absent'
        assert result.get('changed') == True
        assert result.get('module_stderr') == None

    results = hosts.all.zos_data_set(
        name='USER.PRIVATE.TEST4(testme)',
        type='MEMBER',
        state='absent'
    )
    
    for result in results.contacted.values():
        assert result.get('original_message').get('state') == 'absent'
        assert result.get('changed') == False
        assert result.get('module_stderr') == None
