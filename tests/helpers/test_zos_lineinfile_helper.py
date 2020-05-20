# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
import os
from pprint import pprint

__metaclass__ = type


def set_uss_test_env(test_name, hosts, test_env):
    test_env["TEST_FILE"] = test_env["TEST_DIR"] + test_env["USS_FILE"].split('/')[-1] + "." + test_name
    try:
        if not os.path.exists(test_env["TEST_DIR"]):
            os.mkdir(test_env["TEST_DIR"])
        hosts.all.shell(cmd="cp -p {0} {1}".format(test_env["USS_FILE"], test_env["TEST_FILE"]))
    except:
        assert "Failed to set the test env"

def clean_uss_test_env(test_dir):
    try:
        os.rmdir(test_dir)
    except:
        assert "Failed to clean the test env"

def test_uss_general(test_name, ansible_zos_module, test_env, test_info):
    hosts = ansible_zos_module
    set_uss_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["TEST_FILE"]
    results = hosts.all.zos_lineinfile(**test_info)
    #clean_uss_test_env(test_env["TEST_DIR"])
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") == 1