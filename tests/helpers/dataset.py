from __future__ import absolute_import, division, print_function

__metaclass__ = type
import pytest
import string
import random
import re

# Function or test to ensure random names of datasets
    # Is need the hosts to call the shell in every test and for some cases of
    # long datasets names that will generate problems with jcl the hlq size can
    # change
def get_dataset(hosts, hlq_size=8):
    # Generate the first random hlq of size pass as parameter
    letters =  string.ascii_uppercase
    hlq =  ''.join(random.choice(letters)for iteration in range(hlq_size))
    # Ensure the hlq is correct for the dataset naming conventions, until then continue working
    while not re.fullmatch(
    r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})",
            hlq,
            re.IGNORECASE,
        ):
        hlq =  ''.join(random.choice(letters)for iteration in range(hlq_size))
    # Get the second part of the name with the ocmand mvstmp by time is give
    response = hosts.all.command(cmd="mvstmp {0}".format(hlq))
    for dataset in response.contacted.values():
        ds = dataset.get("stdout")
    return ds
