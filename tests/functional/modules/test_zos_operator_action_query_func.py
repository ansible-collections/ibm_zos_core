#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

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
            if result['changed'] not False:
                    assert True
            if result.get('actions') not None:
                    assert True
