# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class MissingZOAUImport(object):
    def __getattr__(self, name):
        def method(*args, **kwargs):
            raise ImportError(
                (
                    "ZOAU is not properly configured for Ansible. Unable to import zoautil_py. "
                    "Ensure environment variables are properly configured in Ansible for use with ZOAU."
                )
            )

        return method
