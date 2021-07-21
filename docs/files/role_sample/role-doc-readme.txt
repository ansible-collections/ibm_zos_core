# Copyright (c) IBM Corporation 2020, 2021

################################################################################
# Role metadata documentation readme
# This documents how to create the metadata for roles so that it can be used
# with the make file target `role-doc`
################################################################################

################################################################################
# Role metadata documentation is used to describe a role to be consumed by
# ansible-doc-extractor and generate ReStructuredText (RST).
#
# ansile-doc-extractor follows the same configuration options that apply to
# Ansible module documenting which can be reviewed at:
# https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html
#
# Role meta data file should be named:
#  Format: doc_<role_name>
#  In the example, the role name is 'role_sample' so the metadata is
#  named 'doc_role_sample'
#
# Role metadata file should be placed in a directory called `docs` inside the role:
#  <collection>/roles/<role_name>/docs/doc_<role_name>
#
# Role metadata documentation should:
#
# 1) Include a copyright in the metadata at the top.
#    Copyright (c) IBM Corporation 2020, 2021
#
# 2) Include DOCUMENTATION block (See example doc_role_sample).
#    DOCUMENTATION = """ properties """ where properties supported:
#    a) role:
#    b) short_description:
#    c) description:
#    d) author:
#    e) variables:
#       e.1) <name>:
#       e.2) description:
#       e.3) type:
#       e.4) required:
#       e.5) default:
#    f) dependencies:
# 3) Include EXAMPLES block (See example doc_role_sample).
#    EXAMPLES = """ valid YAML """:
# 4) Include an empty RETURN block (See example doc_role_sample).
#    RETURN = """ """
#    The RETURN block must be included and because roles don't return anything
#    it remain empty.
################################################################################