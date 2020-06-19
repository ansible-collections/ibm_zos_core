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
  - Return a list of data sets based on specific criteria. 
  - Multiple criteria are AND’d together.
  - Use the M(find) module to find USS files.
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
    description:
      - A regular expression or pattern which should be matched against the data
        set content.
    type: str
    required: false
  excludes:
    description:
      - One or more (shell or regex) patterns, which type is controlled by use_regex option.
      - Data sets whose names match an excludes pattern are culled from patterns matches. 
        Multiple patterns can be specified using a list.
    type: list
    required: false
    aliases: ['exclude']
  patterns:
    description:
      - One or more (shell or regex) patterns, which type is controlled by use_regex option.
      - The patterns restrict the list of files to be returned to those whose 
        basenames match at least one of the patterns specified. Multiple patterns 
        can be specified using a list.
      - The pattern is matched against the file base name, excluding the directory.
      - When using regexen, the pattern MUST match the ENTIRE file name, not just 
        parts of it. So if you are looking to match all files ending in .default, 
        you'd need to use '.*\.default' as a regexp and not just '\.default'.
      - This parameter expects a list, which can be either comma separated or YAML. 
        If any of the patterns contain a comma, make sure to put them in a list 
        to avoid splitting the patterns in undesirable ways.
    type: list
    required: false
  size:
    description:
      - Select files whose size is equal to or greater than the specified size.
      - Use a negative size to find files equal to or less than the specified size.
      - Unqualified values are in bytes but b, k, m, g, and t can be appended to 
        specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.
    type: str
    required: false
  use_regex:
    - If C(true), they are python regexes
    - If C(false), they are 
  paths:
    description:
      - List of data sets to search.
      - All paths must be full data set names.
    type: list
    required: false
  file_type;
    description:
      - List of PDS/PDSE to search. Wild-card possible. 
      - Required only when searching for members, otherwise ignored.
notes:
  - Only cataloged data sets will searched. If an uncataloged data set needs to
    be searched, it should be cataloged first.
seealso:
- module: find


"""


EXAMPLES = r"""

"""


RETURN = r"""


"""