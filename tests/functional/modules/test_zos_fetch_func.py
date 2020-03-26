# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

import os
import sys
import warnings
import shutil
import stat

import ansible.constants
import ansible.errors
import ansible.utils
import pytest

from ansible.utils.hashing import checksum

__metaclass__ = type


DUMMY_DATA = '''DUMMY DATA == LINE 01 ==
DUMMY DATA == LINE 02 ==
DUMMY DATA == LINE 03 ==
'''


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
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'USS'
            assert result.get('module_stderr') is None
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
            assert result.get('changed') is True
            assert result.get('checlsum') != local_checksum
            assert result.get('module_stderr') is None
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
            assert result.get('changed') is False
            assert result.get('checksum') == local_checksum
            assert result.get('module_stderr') is None
    finally:
        os.remove(dest_path)


def test_fetch_sequential_data_set_fixed_block(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.IMS01.DDCHKPT',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMS01.DDCHKPT'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') is None
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
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMS01.SPOOL1'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') is None
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
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.COMN91'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') is None
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
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.LDS01.WADS2'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'VSAM'
            assert result.get('module_stderr') is None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_member_in_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.COMNUC(ATRQUERY)',
        dest='/tmp/',
        flat=True,
        is_binary=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/ATRQUERY'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') is None
            assert result.get('dest') == dest_path
            assert result.get('is_binary') is True
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
        is_binary=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMS01.DDCHKPT'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') is None
            assert result.get('is_binary') is True
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
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') is None
            assert result.get('is_binary') is True
            assert os.path.exists(dest_path)
            assert os.path.isdir(dest_path)
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)


def test_fetch_sequential_data_set_empty(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.IMSCOM.HOLDER',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/IMSTESTL.IMSCOM.HOLDER'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Sequential'
            assert result.get('module_stderr') is None
            assert result.get('dest') == dest_path
            assert os.path.exists(dest_path)
            assert os.stat(dest_path).st_size == 0
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_empty_fails(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = "ZOS.FETCH.TEST.PDS"
    hosts.all.zos_data_set(
        name=pds_name,
        type='pds',
        size='5M',
        format='fba',
        record_length=25
    )
    params = dict(
        src=pds_name,
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('msg')
            assert result.get('stderr') != ""
    finally:
        hosts.all.zos_data_set(name=pds_name, state='absent')


def test_fetch_partitioned_data_set_member_empty(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = "ZOS.FETCH.TEST.PDS"
    hosts.all.zos_data_set(
        name=pds_name,
        type='pds',
        size='5M',
        format='fba',
        record_length=25
    )
    hosts.all.zos_data_set(
        name=pds_name + "(MYDATA)",
        type='MEMBER',
        replace='yes'
    )
    params = dict(
        src='ZOS.FETCH.TEST.PDS(MYDATA)',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    dest_path = '/tmp/MYDATA'
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('data_set_type') == 'Partitioned'
            assert result.get('module_stderr') is None
            assert os.path.exists(dest_path)
            assert os.stat(dest_path).st_size == 0
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        hosts.all.zos_data_set(name=pds_name, state='absent')


def test_fetch_missing_uss_file_does_not_fail(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='/tmp/dummy_file_on_remote_host',
        dest='/tmp/',
        flat=True,
        fail_on_missing=False
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('changed') is False
            assert result.get('note') != ""
            assert result.get('module_stderr') is None
    except Exception:
        raise


def test_fetch_missing_uss_file_fails(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='/tmp/dummy_file_on_remote_host',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    fail_msg = ("The data set /tmp/dummy_file_on_remote_host does not exist"
                " or is uncataloged")
    try:
        for result in results.contacted.values():
            assert result.get('msg') == fail_msg
    except Exception:
        raise


def test_fetch_missing_mvs_data_set_does_not_fail(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='FETCH.TEST.DATA.SET',
        dest='/tmp/',
        flat=True,
        fail_on_missing=False
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('changed') is False
            assert result.get('note') != ""
            assert result.get('module_stderr') is None
            assert not os.path.exists('/tmp/FETCH.TEST.DATA.SET')
    except Exception:
        raise


def test_fetch_partitioned_data_set_member_missing_fails(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='IMSTESTL.COMNUC(DUMMY)',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('msg')
            assert result.get('stderr') != ""
    except Exception:
        raise


def test_fetch_mvs_data_set_missing_fails(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src='ZOS.FETCH.TEST.PDS',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('msg')
            assert result.get('stderr') != ""
            assert not os.path.exists('/tmp/ZOS.FETCH.TEST.PDS')
    except Exception:
        raise


def test_fetch_sequential_data_set_replace_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = 'IMSTESTL.IMS01.DDCHKPT'
    dest_path = "/tmp/" + ds_name
    with open(dest_path, 'w') as infile:
        infile.write(DUMMY_DATA)

    local_checksum = checksum(dest_path)
    params = dict(
        src=ds_name,
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('module_stderr') is None
            assert checksum(dest_path) != local_checksum
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_replace_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = "ZOS.FETCH.TEST.PDS"
    dest_path = "/tmp/" + pds_name
    full_path = dest_path + "/MYDATA"
    hosts.all.zos_data_set(
        name=pds_name,
        type='pds',
        size='5M',
        format='fba',
        record_length=25
    )
    hosts.all.zos_data_set(
        name=pds_name + "(MYDATA)",
        type='MEMBER',
        replace='yes'
    )
    os.mkdir(dest_path)
    with open(full_path, 'w') as infile:
        infile.write(DUMMY_DATA)
    with open(dest_path + "/NEWMEM", 'w') as infile:
        infile.write(DUMMY_DATA)

    prev_timestamp = os.path.getmtime(dest_path)
    params = dict(
        src=pds_name,
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get('module_stderr') is None
            assert os.path.getmtime(dest_path) != prev_timestamp
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        hosts.all.zos_data_set(name=pds_name, state='absent')


def test_fetch_uss_file_insufficient_write_permission_fails(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/profile"
    with open(dest_path, 'w'):
        pass
    os.chmod(dest_path, stat.S_IREAD)
    params = dict(
        src='/etc/profile',
        dest='/tmp/profile',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('msg')
    finally:
        os.remove(dest_path)


def test_fetch_pds_dir_insufficient_write_permission_fails(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/IMSTESTL.COMNUC"
    os.mkdir(dest_path)
    os.chmod(dest_path, stat.S_IREAD)
    params = dict(
        src='IMSTESTL.COMNUC',
        dest='/tmp/',
        flat=True
    )
    results = hosts.all.zos_fetch(**params)
    try:
        for result in results.contacted.values():
            assert result.get('msg')
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
