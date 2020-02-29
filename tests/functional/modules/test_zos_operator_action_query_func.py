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

def test_zos_operator_action_query_goldenpath(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query()
    for result in results.contacted.values():
        assert result['changed'] == False
        assert result.get('result') != None
