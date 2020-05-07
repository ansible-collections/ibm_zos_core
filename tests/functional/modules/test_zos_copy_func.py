# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os
import sys
import warnings
import shutil
import tempfile

import ansible.constants
import ansible.errors
import ansible.utils
import pytest

from ansible.utils.hashing import checksum

__metaclass__ = type


DUMMY_DATA = '''DUMMY DATA ---- LINE 001 ------
DUMMY DATA ---- LINE 002 ------
DUMMY DATA ---- LINE 003 ------
DUMMY DATA ---- LINE 004 ------
DUMMY DATA ---- LINE 005 ------
DUMMY DATA ---- LINE 006 ------
DUMMY DATA ---- LINE 007 ------
'''


def test_copy_local_file_to_non_existing_uss_file(ansible_zos_module):
    pass


def test_copy_local_file_to_existing_uss_file(ansible_zos_module):
    pass


def test_copy_local_file_to_uss_dir(ansible_zos_module):
    pass


def test_copy_local_file_to_non_existing_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    fd, source_path = tempfile.mkstemp(text=True)
    with os.fdopen(fd, 'w') as infile:
        infile.write(DUMMY_DATA)
    
    dest = 'USER.TEST.SEQ'
    params = dict(src=source_path, dest=dest)
    copy_result = hosts.all.zos_copy(**params)
    verify_copy = hosts.all.shell(
        cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
        executable="/usr/lpp/rsusr/ported/bin/bash"
    )
    try:
        for cp_res in copy_result.contacted.values(ansible_zos_module):
            assert cp_res.get('module_stderr') is None
        for v_cp in verify_copy.contacted.values(ansible_zos_module):
            assert v_cp.get('rc') == 0
    finally:
        os.remove(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_existing_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    fd, source_path = tempfile.mkstemp(text=True)
    with open(fd, 'w') as infile:
        infile.write(DUMMY_DATA)
    
    dest = 'USER.TEST.SEQ'
    hosts.all.zos_data_set(name=dest, type='seq', state='present')
    params = dict(src=source_path, dest=dest)
    copy_result = hosts.all.zos_copy(**params)
    verify_copy = hosts.all.shell(
        cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
        executable="/usr/lpp/rsusr/ported/bin/bash"
    )
    dest_path = '/tmp/TERRY.IMSV14.ADFSBASE'
    try:
        for cp_res in copy_result.contacted.values(ansible_zos_module):
            assert cp_res.get('module_stderr') == False
            assert cp_res.get('changed') == True
        for v_cp in verify_copy.constants.values(ansible_zos_module):
            assert v_cp.get('rc') == 0
            assert v_cp.get('stdout') != ""
        
    finally:
        os.remove(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    fd, source_path = tempfile.mkstemp(text=True)
    with open(fd, 'w') as infile:
        infile.write(DUMMY_DATA)
    
    dest = 'USER.TEST.PDS(data)'
    params = dict(src=source_path, dest=dest)
    hosts.all.zos_data_set(
        name=dest[:dest.find('(')], 
        type='pds', size='5M', format='fba', record_length=25
    )
    hosts.all.zos_data_set(name=dest, type='MEMBER', replace='yes')
    copy_result = hosts.all.zos_copy(**params)
    verify_copy = hosts.all.shell(
        cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
        executable="/usr/lpp/rsusr/ported/bin/bash"
    )
    try:
        for cp_res in copy_result.contacted.values(ansible_zos_module):
            assert cp_res.get('module_stderr') == False
        for v_cp in verify_copy.contacted.values(ansible_zos_module):
            assert v_cp.get('rc') == 0
            assert v_cp.get('stdout') != ""
    finally:
        os.remove(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_non_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_local_file_to_non_existing_pdse(ansible_zos_module):
    pass


def test_copy_local_dir_to_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    source_path = tempfile.mkdtemp()
    dest = 'USER.TEST.PDS'
    params = dict(src=source_path, dest=dest)
    hosts.all.zos_data_set(name=dest, type='pds', size='5M', format='fba', record_length=25)
    hosts.all.zos_data_set(name=dest + '(data)', type='MEMBER', replace='yes')
    copy_result = hosts.all.zos_copy(**params)
    verify_copy = hosts.all.shell(
        cmd="tsocmd \"LISTDS '{}'\" > /dev/null 2>/dev/null".format(dest), 
        executable="/usr/lpp/rsusr/ported/bin/bash"
    )
    try:
        for cp_res in copy_result.contacted.values(ansible_zos_module):
            assert cp_res.get('module_stderr') == False
        for v_cp in verify_copy.contacted.values(ansible_zos_module):
            assert v_cp.get('rc') == 0
    finally:
        shutil.rmtree(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_dir_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    source_path = tempfile.mkdtemp()
    num_files = 5
    for i in range(num_files):
        fd,_ = tempfile.mkstemp(dir=source_path, text=True)
        with open(fd, 'w') as infile:
            infile.write(DUMMY_DATA)
    
    dest = 'USER.TEST.PDS'
    params = dict(src=source_path, dest=dest)
    copy_result = hosts.all.zos_copy(**params)
    verify_copy = hosts.all.shell(
        cmd="tsocmd \"LISTDS '{}'\" > /dev/null 2>/dev/null".format(dest), 
        executable="/usr/lpp/rsusr/ported/bin/bash"
    )
    try:
        for cp_res in copy_result.contacted.values(ansible_zos_module):
            assert cp_res.get('module_stderr') == False
        for v_cp in verify_copy.contacted.values(ansible_zos_module):
            assert v_cp.get('rc') == 0
    finally:
        shutil.rmtree(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_file_to_uss_file(ansible_zos_module):
    pass


def test_copy_uss_file_to_uss_dir(ansible_zos_module):
    pass


def test_copy_uss_file_to_non_existing_sequential_data_set(ansible_zos_module):
    pass


def test_copy_uss_file_to_existing_sequential_data_set(ansible_zos_module):
    pass


def test_copy_uss_file_to_non_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_uss_file_to_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_uss_dir_to_existing_pdse(ansible_zos_module):
    pass


def test_copy_uss_dir_to_non_existing_pdse(ansible_zos_module):
    pass


def test_copy_ps_to_existing_uss_file(ansible_zos_module):
    pass


def test_copy_ps_to_non_existing_uss_file(ansible_zos_module):
    pass


def test_copy_ps_to_existing_uss_dir(ansible_zos_module):
    pass


def test_copy_ps_to_non_existing_uss_dir(ansible_zos_module):
    pass


def test_copy_ps_to_ps(ansible_zos_module):
    pass


def test_copy_ps_to_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_ps_to_non_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_pds_to_non_existing_uss_dir(ansible_zos_module):
    pass


def test_copy_pds_to_existing_uss_dir(ansible_zos_module):
    pass


def test_copy_pds_to_existing_pds(ansible_zos_module):
    pass


def test_copy_pds_to_non_existing_pds(ansible_zos_module):
    pass


def test_copy_pds_to_existing_pdse(ansible_zos_module):
    pass


def test_copy_pds_to_non_existing_pdse(ansible_zos_module):
    pass


def test_copy_pdse_to_non_existing_uss_dir(ansible_zos_module):
    pass


def test_copy_pdse_to_existing_uss_dir(ansible_zos_module):
    pass


def test_copy_pdse_to_existing_pdse(ansible_zos_module):
    pass


def test_copy_pdse_to_non_existing_pdse(ansible_zos_module):
    pass


def test_copy_pdse_to_non_existing_pds(ansible_zos_module):
    pass


def test_copy_pds_member_to_existing_uss_file(ansible_zos_module):
    pass


def test_copy_pds_member_to_non_existing_uss_file(ansible_zos_module):
    pass


def test_copy_pds_member_to_existing_ps(ansible_zos_module):
    pass


def test_copy_pds_member_to_non_existing_ps(ansible_zos_module):
    pass


def test_copy_pds_member_to_existing_pds_member(ansible_zos_module):
    pass


def test_copy_pds_member_to_non_existing_pds_member(ansible_zos_module):
    pass


def test_copy_pds_member_to_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_pds_member_to_non_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_pdse_member_to_existing_uss_file(ansible_zos_module):
    pass


def test_copy_pdse_member_to_non_existing_uss_file(ansible_zos_module):
    pass


def test_copy_pdse_member_to_existing_ps(ansible_zos_module):
    pass


def test_copy_pdse_member_to_non_existing_ps(ansible_zos_module):
    pass


def test_copy_pdse_member_to_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_pdse_member_to_non_existing_pdse_member(ansible_zos_module):
    pass


def test_copy_pdse_member_to_existing_pds_member(ansible_zos_module):
    pass


def test_copy_pdse_member_to_non_existing_pds_member(ansible_zos_module):
    pass


def test_copy_pds_member_to_uss_dir(ansible_zos_module):
    pass


def test_copy_pdse_member_to_uss_dir(ansible_zos_module):
    pass


def test_copy_vsam_ksds_to_existing_vsam_ksds(ansible_zos_module):
    pass


def test_copy_vsam_ksds_to_non_existing_vsam_ksds(ansible_zos_module):
    pass


def test_copy_vsam_lds_to_existing_vsam_lds(ansible_zos_module):
    pass


def test_copy_vsam_lds_to_non_existing_vsam_lds(ansible_zos_module):
    pass


def test_copy_inline_content_to_uss_file(ansible_zos_module):
    pass


def test_copy_inline_content_to_ps(ansible_zos_module):
    pass


def test_copy_inline_content_to_pds_member(ansible_zos_module):
    pass


def test_copy_inline_content_to_pdse_member(ansible_zos_module):
    pass


def test_backup_uss_file(ansible_zos_module):
    pass


def test_backup_ps(ansible_zos_module):
    pass


def test_backup_pds(ansible_zos_module):
    pass


def test_backup_pds_member(ansible_zos_module):
    pass


def test_backup_pdse(ansible_zos_module):
    pass


def test_backup_vsam(ansible_zos_module):
    pass


def test_copy_to_existing_dest_not_forced(ansible_zos_module):
    pass


def test_copy_local_symlink_to_uss_file(ansible_zos_module):
    pass


def test_copy_local_file_to_uss_file_convert_encoding(ansible_zos_module):
    pass


def test_copy_uss_file_to_uss_file_convert_encoding(ansible_zos_module):
    pass


def test_copy_uss_file_to_pds_member_convert_encoding(ansible_zos_module):
    pass