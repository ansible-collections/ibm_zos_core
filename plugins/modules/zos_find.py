#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: zos_find
version_added: '2.9'
short_description: Find matching data sets
description:
  - Return a list of files or data sets based on specific criteria. 
  - Multiple criteria are AND’d together.
author: "Asif Mahmud (@asifmahmud)"
options:
  age:
    description:
      - Select files or data sets whose age is equal to or greater than the specified time.
      - Use a negative age to find data sets equal to or less than the specified time.
      - You can choose seconds, minutes, hours, days, or weeks by specifying the 
        first letter of any of those words (e.g., "1w").
    type: str
    required: false
  age_stamp:
    description:
      - Choose the date property against which we compare age.
      - C(c_date) refers to creation date and C(r_date) refers to referenced date.
      - Only valid if C(age) is provided.
    type: str
    choices:
      - c_date
      - r_date
    default: c_date
    required: false
  contains:
    -
  exclude:
    - 
  get_checksum:
    - 
  patterns:
    - 
  size:
    - 
  use_regex:
    - 
  paths:
    - 
  file_type;
    - 
  


"""


EXAMPLES = r"""

"""


RETURN = r"""


"""