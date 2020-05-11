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

SHELL_EXECUTABLE = "/usr/lpp/rsusr/ported/bin/bash"


def populate_dir(dir_path):
    for i in range(5):
        with open(dir_path + '/' + "file" + str(i+1), 'w') as infile:
            infile.write(DUMMY_DATA)


def test_copy_local_file_to_non_existing_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = '/tmp/profile'
    try:
        hosts.all.file(path=dest_path, state='absent')
        copy_res = hosts.all.zos_copy(
            src='/etc/profile',
            dest=dest_path
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_local_file_to_existing_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = '/tmp/profile'
    try:
        hosts.all.file(path=dest_path, state='touch')
        stat_res = list(hosts.all.stat(path=dest_path).contacted.values())
        timestamp = stat_res[0].get('stat').get('atime')
        assert timestamp is not None
        copy_res = hosts.all.zos_copy(
            src='/etc/profile',
            dest=dest_path
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
            assert result.get('stat').get('atime') != timestamp
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_local_file_to_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = '/tmp/testdir'
    try:
        hosts.all.file(path=dest_path, state='directory')
        copy_res = hosts.all.zos_copy(
            src='/etc/profile',
            dest=dest_path
        )
        stat_res = hosts.all.stat(path=dest_path + '/' + 'profile')
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_local_file_to_non_existing_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.SEQ.FUNCTEST'
    src_file = '/etc/profile'
    try:
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_existing_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.SEQ.FUNCTEST'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(name=dest, type='seq', state='present')
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
            assert v_cp.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDS.FUNCTEST'
    dest_path = 'USER.TEST.PDS.FUNCTEST(DATA)'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pds', size='5M', format='fba', record_length=25
        )
        hosts.all.zos_data_set(name=dest_path, type='MEMBER', replace='yes')
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest_path)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_non_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDS.FUNCTEST'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pds', size='5M', format='fba', record_length=25
        )
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest + '(PROFILE)'), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDS.FUNCTEST'
    dest_path = 'USER.TEST.PDS.FUNCTEST(PROFILE)'
    src_file = '/etc/profile'
    try:
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest_path)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_dir_to_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    source_path = tempfile.mkdtemp()
    dest = 'USER.TEST.PDS.FUNCTEST'
    try:
        populate_dir(source_path)
        hosts.all.zos_data_set(name=dest, type='pds', size='5M', format='fba', record_length=25)
        hosts.all.zos_data_set(name=dest + '(FILE1)', type='MEMBER', replace='yes')
        copy_result = hosts.all.zos_copy(src=source_path, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest+"(FILE2)"), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        shutil.rmtree(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_dir_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    source_path = tempfile.mkdtemp()
    dest = 'USER.TEST.PDS.FUNCTEST'
    try:
        populate_dir(source_path)
        copy_result = hosts.all.zos_copy(src=source_path, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{}'\" > /dev/null 2>/dev/null".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        shutil.rmtree(source_path)
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_uss_binary(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = '/tmp/profile'
    try:
        hosts.all.file(path=dest_path, state='absent')
        copy_res = hosts.all.zos_copy(
            src='/etc/profile',
            dest=dest_path,
            is_binary=True
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_local_file_to_sequential_data_set_binary(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.SEQ.FUNCTEST'
    src_file = '/etc/profile'
    try:
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest,
            is_binary=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_pds_member_binary(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDS.FUNCTEST'
    dest_path = 'USER.TEST.PDS.FUNCTEST(DATA)'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pds', size='5M', format='fba', record_length=25
        )
        hosts.all.zos_data_set(name=dest_path, type='MEMBER', replace='yes')
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest_path,
            is_binary=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_local_file_to_pdse_member_binary(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDS.FUNCTEST'
    dest_path = 'USER.TEST.PDS.FUNCTEST(DATA)'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pdse', size='5M', format='fba', record_length=25
        )
        hosts.all.zos_data_set(name=dest_path, type='MEMBER', replace='yes')
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest_path,
            is_binary=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_file_to_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    remote_src = '/etc/profile'
    dest = '/tmp/test_profile'
    try:
        hosts.all.file(path=dest, state='absent')
        copy_result = hosts.all.zos_copy(
            src=remote_src, 
            dest=dest, 
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest)
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for st in stat_res.contacted.values():
            assert st.get('stat').get('exists') is True
    finally:
        hosts.all.file(path=dest, state='absent')


def test_copy_uss_file_to_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    remote_src = '/etc/profile'
    dest = '/tmp'
    dest_path = '/tmp/profile'
    try:
        hosts.all.file(path=dest_path, state='absent')
        copy_result = hosts.all.zos_copy(
            src=remote_src, 
            dest=dest, 
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest_path)
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for st in stat_res.contacted.values():
            assert st.get('stat').get('exists') is True
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_uss_file_to_non_existing_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.SEQ.FUNCTEST'
    src_file = '/etc/profile'
    try:
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_file_to_existing_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.SEQ.FUNCTEST'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(name=dest, type='seq', state='present')
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_file_to_non_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDSE.FUNCTEST'
    dest_path = 'USER.TEST.PDSE.FUNCTEST(DATA)'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pdse', size='5M', format='fba', record_length=25
        )
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest_path,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_file_to_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    dest = 'USER.TEST.PDSE.FUNCTEST'
    dest_path = 'USER.TEST.PDSE.FUNCTEST(DATA)'
    src_file = '/etc/profile'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pdse', size='5M', format='fba', record_length=25
        )
        hosts.all.zos_data_set(
            name=dest_path, type='MEMBER', replace='yes'
        )
        copy_result = hosts.all.zos_copy(
            src=src_file, 
            dest=dest_path,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for cp_res in copy_result.contacted.values():
            assert cp_res.get('msg') is None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get('rc') == 0
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_dir_to_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_dir = '/tmp/testdir'
    dest = 'USER.TEST.PDSE.FUNCTEST'
    try:
        hosts.all.zos_data_set(
            name=dest, type='pdse', size='5M', format='fba', record_length=25
        )
        hosts.all.file(path=src_dir, state='directory')
        for i in range(5):
            hosts.all.file(path=src_dir + '/' + 'file' + str(i), state='touch')

        copy_res = hosts.all.zos_copy(
            src=src_dir,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest + "(FILE2)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
    finally:
        hosts.all.file(path=src_dir, state='absent')
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_uss_dir_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_dir = '/tmp/testdir'
    dest = 'USER.TEST.PDSE.FUNCTEST'
    try:
        hosts.all.file(path=src_dir, state='directory')
        for i in range(5):
            hosts.all.file(path=src_dir + '/' + 'file' + str(i), state='touch')

        copy_res = hosts.all.zos_copy(
            src=src_dir,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\" > /dev/null 2>/dev/null".format(dest + "(FILE2)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
    finally:
        hosts.all.file(path=src_dir, state='absent')
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_ps_to_existing_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest = '/tmp/ddchkpt'
    try:
        hosts.all.file(path=dest, state='touch')
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.file(path=dest, state='absent')


def test_copy_ps_to_non_existing_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest = '/tmp/ddchkpt'
    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.file(path=dest, state='absent')


def test_copy_ps_to_existing_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest = '/tmp/ddchkpt'
    dest_path = dest + '/' + 'IMSTESTL.IMS01.DDCHKPT'
    try:
        hosts.all.file(path=dest, state='directory')
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest_path)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest_path), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.file(path=dest, state='absent')


def test_copy_ps_to_non_existing_ps(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest = 'USER.TEST.SEQ.FUNCTEST'
    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_ps_to_existing_ps(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest = 'USER.TEST.SEQ.FUNCTEST'
    try:
        hosts.all.zos_data_set(name=dest, type='seq', state='present')
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_ps_to_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest_ds = 'USER.TEST.PDSE.FUNCTEST'
    dest = dest_ds + "(DATA)"
    try:
        hosts.all.zos_data_set(name=dest_ds, type='pdse', state='present')
        hosts.all.zos_data_set(name=dest, type='MEMBER', replace='yes')
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest_ds, state='absent')


def test_copy_ps_to_non_existing_pdse_member(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.IMS01.DDCHKPT'
    dest_ds = 'USER.TEST.PDSE.FUNCTEST'
    dest = dest_ds + "(DATA)"
    try:
        hosts.all.zos_data_set(name=dest_ds, type='pdse', state='present')
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest_ds, state='absent')


def test_copy_pds_to_non_existing_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.COMNUC'
    dest = '/tmp/'
    dest_path = '/tmp/IMSTESTL.COMNUC'
    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
            assert result.get('stat').get('isdir') is True
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_pds_to_existing_pds(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.COMNUC'
    dest = "USER.TEST.PDS.FUNCTEST"
    try:
        hosts.all.zos_data_set(
            name=dest, type='pds', size='5M', format='fba', record_length=25
        )
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest+"(ATRQUERY)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_pds_to_non_existing_pds(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.COMNUC'
    dest = "USER.TEST.PDS.FUNCTEST"
    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest+"(ATRQUERY)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_pds_to_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'IMSTESTL.COMNUC'
    dest = "USER.TEST.PDSE.FUNCTEST"
    try:
        hosts.all.zos_data_set(
            name=dest, type='pdse', size='5M', format='fba', record_length=25
        )
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{}'\"".format(dest+"(ATRQUERY)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_pdse_to_non_existing_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'SYS1.NFSLIBE'
    dest = "/tmp/"
    dest_path = '/tmp/SYS1.NFSLIBE'
    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get('stat').get('exists') is True
            assert result.get('stat').get('isdir') is True
    finally:
        hosts.all.file(path=dest_path, state='absent')


def test_copy_pdse_to_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'SYS1.NFSLIBE'
    dest = "USER.TEST.PDSE.FUNCTEST"
    try:
        hosts.all.zos_data_set(
            name=dest, type='pdse', size='5M', format='fba', record_length=25
        )
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="head \"//'{}'\"".format(dest+"(GFSAMAIN)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


def test_copy_pdse_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = 'SYS1.NFSLIBE'
    dest = "USER.TEST.PDSE.FUNCTEST"
    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest,
            remote_src=True
        )
        verify_copy = hosts.all.shell(
            cmd="head \"//'{}'\"".format(dest+"(GFSAMAIN)"), 
            executable=SHELL_EXECUTABLE
        )
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in verify_copy.contacted.values():
            assert result.get('rc') == 0
            assert result.get('stdout') != ""
    finally:
        hosts.all.zos_data_set(name=dest, state='absent')


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


def test_ensure_tmp_cleanup(ansible_zos_module):
    pass


def test_backup_uss_file_default_backup_path(ansible_zos_module):
    pass


def test_backup_sequential_data_set_default_backup_path(ansible_zos_module):
    pass


def test_backup_pds_default_backup_path(ansible_zos_module):
    pass


def test_backup_pdse_default_backup_path(ansible_zos_module):
    pass


def test_backup_vsam_default_backup_path(ansible_zos_module):
    pass


def test_backup_uss_file_user_backup_path(ansible_zos_module):
    pass


def test_backup_sequential_data_set_user_backup_path(ansible_zos_module):
    pass


def test_backup_pds_user_backup_path(ansible_zos_module):
    pass


def test_backup_pdse_user_backup_path(ansible_zos_module):
    pass


def test_backup_vsam_user_backup_path(ansible_zos_module):
    pass


def test_copy_inline_content_to_uss_file(ansible_zos_module):
    pass


def test_copy_inline_content_to_sequential_data_set(ansible_zos_module):
    pass


def test_copy_inline_content_to_pds_member(ansible_zos_module):
    pass


def test_copy_inline_content_to_pdse_member(ansible_zos_module):
    pass