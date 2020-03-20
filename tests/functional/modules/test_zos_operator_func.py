# -*- coding: utf-8 -*-

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


def test_zos_operator_goldenpath(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd='d u,all', verbose=False, debug=False)
    for result in results.contacted.values():
        assert result['rc'] == 0
        assert result['changed'] == True
        assert result['content'] != None
        
def test_zos_operator_goldenpath_with_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd='d u,all', verbose=True, debug=False)
    for result in results.contacted.values():
        assert result['rc'] == 0
        assert result['changed'] == True
        assert result['content'] != None

def test_zos_operator_goldenpath_with_debug(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd='d u,all', verbose=False, debug=True)
    for result in results.contacted.values():
        assert result['rc'] == 0
        assert result['changed'] == True
        assert result['content'] != None

def test_zos_operator_goldenpath_with_debug_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd='d u,all', verbose=True, debug=True)
    for result in results.contacted.values():
        assert result['rc'] == 0
        assert result['changed'] == True
        assert result['content'] != None
