# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os
import sys
import warnings
import shutil

import ansible.constants
import ansible.errors
import ansible.utils
import pytest

from ansible.utils.hashing import checksum

__metaclass__ = type


def test_fetch_uss_file_not_present_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='/etc/profile', 
        dest='/tmp/', 
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/profile'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Unix'
            assert result.get('module_stderr') == None
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_uss_file_replace_on_local_machine(ansible_zos_module):
    open('/tmp/profile', 'w').close()
    hosts = ansible_zos_module
    params = dict(
        src='/etc/profile', 
        dest='/tmp/', 
        flat=True
    )
    dest_path = '/tmp/profile'
    local_checksum = checksum(dest_path)
    results = hosts.all.zos_fetch(**params)

    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('checlsum') != local_checksum
            assert result.get('module_stderr') == None
            assert os.path.exists(dest_path)
    finally:
        os.remove(dest_path)

def test_fetch_uss_file_present_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='/etc/profile', 
        dest='/tmp/', 
        flat=True
    )
    dest_path = '/tmp/profile'
    hosts.all.zos_fetch(**params)
    local_checksum = checksum(dest_path)
    results = hosts.all.zos_fetch(**params)

    try:
        for result in results.contacted.values():
            assert result.get('changed') == False
            assert result.get('checksum') == local_checksum
            assert result.get('module_stderr') == None
    finally:
        os.remove(dest_path)

def test_fetch_ascii_encoded_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='/etc/profile', 
        dest='/tmp/', 
        flat=True,
        encoding='ASCII'
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/profile'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Unix'
            assert result.get('module_stderr') == None
            assert result.get('encoding') == 'ASCII'
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_sequential_data_set_fixed_block(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.IMS01.DDCHKPT', 
        dest='/tmp/', 
        flat=True,
        use_qualifier=False
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMS01.DDCHKPT'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') == None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_sequential_data_set_variable_block(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.IMS01.SPOOL1', 
        dest='/tmp/', 
        flat=True,
        use_qualifier=False
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMS01.SPOOL1'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') == None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_partitioned_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.COMN91', 
        dest='/tmp/', 
        flat=True,
        use_qualifier=False
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.COMN91'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') == None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
            assert os.path.isdir(dest_path)
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

def test_fetch_vsam_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.LDS01.WADS2', 
        dest='/tmp/', 
        flat=True,
        use_qualifier=False
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.LDS01.WADS2'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'VSAM'
            assert result.get('module_stderr') == None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_partitioned_data_set_member(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.COMNUC(ATRQUERY)', 
        dest='/tmp/', 
        flat=True,
        use_qualifier=False,
        is_binary=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/ATRQUERY'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') == None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
            assert os.path.isfile(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_sequential_data_set_in_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.IMS01.DDCHKPT', 
        dest='/tmp/', 
        flat=True,
        is_binary=True,
        use_qualifier=False
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMS01.DDCHKPT'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') == None
            assert result.get('transfer_mode') == 'binary'
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)

def test_fetch_partitioned_data_set_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.COMN91', 
        dest='/tmp/', 
        flat=True,
        is_binary=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.COMN91'
    try:
        for result in results.contacted.values():
            assert result.get('changed') == True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') == None
            assert result.get('is_binary') == True
            assert os.path.exists(dest_path)
            assert os.path.isdir(dest_path)
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

