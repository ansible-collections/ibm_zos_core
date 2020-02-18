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


def test_zos_job_query_func(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_query(job_name='*',owner='*')
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('changed') == False
        assert result.get('jobs') != None
