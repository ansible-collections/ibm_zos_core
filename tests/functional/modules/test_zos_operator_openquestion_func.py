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

# TODO: make commented-out tests generic for use with different z/OS environments (including CI/CD pipeline)
# ? add set-up steps to handle environment configuration so expected values are present?

def test_zos_operator_openquestion_goldenpath(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_openquestion()
    for result in results.contacted.values():
        assert result['changed'] == False
        assert result.get('requests') != None

def test_zos_operator_openquestion_missing_all_parms(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_openquestion()
    for result in results.contacted.values():
        assert result['changed'] == False
        assert result.get('requests') != None

# def test_zos_operator_openquestion_with_request_number_filter(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_openquestion(request_number_list='010')
#     for result in results.contacted.values():
#         assert result['changed'] == False
#         assert result['list_requests'] != 0
#         assert result.get('list_requests') != None


# def test_zos_operator_openquestion_with_system_filter(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_openquestion(system='mv2c')
#     for result in results.contacted.values():
#         assert result['changed'] == False
#         assert result['list_requests'] != 0
#         assert result.get('list_requests') != None

# def test_zos_operator_openquestion_with_jobname_filter(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_openquestion(jobname='IM*')
#     for result in results.contacted.values():
#         assert result['changed'] == False
#         assert result.get('requests') != None

# def test_zos_operator_openquestion_with_message_id_filter(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_openquestion(message_id='DFH*')
#     for result in results.contacted.values():
#         assert result['changed'] == False
#         assert result['list_requests'] != 0
#         assert result.get('list_requests') != None

# def test_zos_operator_openquestion_with_combined_filter(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_openquestion(message_id='DFH*',system='mv28')
#     for result in results.contacted.values():
#         assert result['changed'] == False
#         assert result['list_requests'] != 0
#         assert result.get('list_requests') != None