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
      - Select data sets whose age is equal to or greater than the specified time.
      - Use a negative age to find data sets equal to or less than the specified time.
      - You can choose seconds, minutes, hours, days, or weeks by specifying the
        first letter of any of those words (e.g., "1w").
    type: str
    required: false
  age_stamp:
    description:
      - Choose the date property against which to compare age.
      - C(c_date) refers to creation date and C(r_date) refers to referenced date.
      - Only valid if C(age) is provided.
    type: str
    choices:
      - c_date
      - r_date
    default: r_date
    required: false
  contains:
    description:
      - A regular expression or pattern which should be matched against the data
        set content.
    type: str
    required: false
  excludes:
    description:
      - One or more (shell or regex) patterns, which type is controlled by C(use_regex) option.
      - Data sets whose names match an excludes pattern are culled from patterns matches. 
        Multiple patterns can be specified using a list.
    type: list
    required: false
    aliases: ['exclude']
  patterns:
    description:
      - One or more (shell or regex) patterns, which type is controlled by C(use_regex) option.
      - The patterns restrict the list of data sets to be returned to those whose 
        names match at least one of the patterns specified. Multiple patterns 
        can be specified using a list.
      - When using regexes, the pattern MUST match the ENTIRE data set name, not just 
        parts of it.
      - This parameter expects a list, which can be either comma separated or YAML. 
        If any of the patterns contain a comma, make sure to put them in a list 
        to avoid splitting the patterns in undesirable ways.
    type: list
    required: true
  size:
    description:
      - Select data sets whose size is equal to or greater than the specified size.
      - Use a negative size to find files equal to or less than the specified size.
      - Unqualified values are in bytes but b, k, m, g, and t can be appended to 
        specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.
    type: str
    required: false
  use_regex:
    description:
      - If C(true), patterns will be interpreted as python regex. Default is C(false).
    type: bool
    required: false
    default: false
  paths:
    description:
      - List of PDS/PDSE to search. Wild-card possible.
      - Required only when searching for members, otherwise ignored.
    type: list
    required: false
  file_type;
    description:
      - The type of resource to search. The two choices are 'NONVSAM' and 'VSAM'.
      - 'NONVSAM' refers to one of SEQ, LIBRARY (PDSE), PDS, LARGE, BASIC, EXTREQ, EXTPREF.
    choices:
      - NONVSAM
      - VSAM
    type: str
    required: false
    default: NONVSAM
  volume:
    description:
      - If provided, only the data sets allocated in the specified list of volumes will be
        searched.
    type: list
    required: false
    aliases: ['volumes']
notes:
  - Only cataloged data sets will be searched. If an uncataloged data set needs to
    be searched, it should be cataloged first.
  - The M(zos_find) module currently does not support wildcards for high level qualifiers.
    For example, C(SOME.*.DATA.SET) is a valid pattern, but C(*.DATA.SET) is not. 
seealso:
- module: find
"""


EXAMPLES = r"""
- name: Find all data sets with HLQ 'IMS' or 'IMSTEST' that contain the word 'hello'
  zos_find:
    patterns:
      - IMS.*
      - IMSTEST.*
    contains: hello
    age: 2d

- name: Exclude data sets that have a low level qualifier 'TEST'
  zos_find:
    patterns: '^IMS[1-9].*'
    contains: '^hello[a-z0-9]$'
    excludes: '*.TEST'
    use_regex: true

- name: Find all members starting with characters 'TE' in a list of PDS
  zos_find:
    patterns: '^TE*'
    paths:
      - IMSTEST.TEST.*
      - IMSTEST.USER.*
      - USER.*.LIB
    use_regex: true

- name: Find all data sets greater than 2MB and allocated in one of the specified volumes
  zos_find:
    patterns: '*'
    size: 2m
    volumes:
      - SCR03
      - IMSSUN

- name: Find all VSAM clusters starting with the word 'USER'
  zos_find:
    patterns:
      - USER.*
    file_type: VSAM
"""


RETURN = r"""
data_sets:
    description: All matches found with the specified criteria.
    returned: success
    type: list
    sample: [
      { name: "SOME.DATA.SET",
        "...": "...",
      },
      { name: "SAMPLE.DATA.SET,
        "...": "...",
      },
    ]
matched:
    description: The number of matched data sets found
    returned: success
    type: int
    sample: 49
examined:
    description: Number of data sets looked at
    returned: success
    type: int
    sample: 158
"""