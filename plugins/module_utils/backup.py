# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from os import path
from ansible.module_utils.six import PY3
from ansible.module_utils.basic import AnsibleModule
import time
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)

try:
    from zoautil_py import Datasets
except Exception:
    Datasets = MissingZOAUImport()
if PY3:
    from shlex import quote
else:
    from pipes import quote

BACKUP = """ COPY DATASET(INCLUDE( {0} )) -
    RENUNC({0}, -
    {1}) -
    CATALOG -
    OPTIMIZE(4) """


def _validate_data_set_name(ds):
    arg_defs = dict(ds=dict(arg_type="data_set"),)
    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args({"ds": ds})
    return parsed_args.get("ds")


def mvs_file_backup(self, dsn, bk_dsn):
    """Create a backup data set for an MVS data set

    Arguments:
        dsn {str} -- The name of the data set to backup.
                        It could be an MVS PS/PDS/PDSE/VSAM(KSDS), etc.
        bk_dsn {str} -- The name of the backup data set.

    Returns:
        str -- Name of the backup data set.
        err_msg -- A message indicating whether the backup was successful or not.
    """
    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
    dsn = _validate_data_set_name(dsn)
    bk_dsn = _validate_data_set_name(bk_dsn)
    err_msg = None
    out = None
    if not bk_dsn:
        hlq = Datasets.hlq()
        bk_dsn = Datasets.temp_name(hlq)
    bk_sysin = BACKUP.format(dsn, bk_dsn)
    bkup_cmd = "mvscmdauth --pgm=adrdssu --sysprint=stdout --sysin=stdin"
    rc, stdout, stderr = module.run_command(
        bkup_cmd, data=bk_sysin, use_unsafe_shell=True
    )
    if rc > 4:
        out = stdout
        if "DUPLICATE" in out:
            err_msg = "Backup data set {0} exists, please check".format(bk_dsn)
        else:
            err_msg = "Failed when creating the backup of the data set {0} : {1}".format(
                dsn, out
            )
            if Datasets.exists(bk_dsn):
                Datasets.delete(bk_dsn)
    return bk_dsn, err_msg


def uss_file_backup(file, bk_file):
    """Create a backup file for a USS file or path

    Arguments:
        file {str} -- The name of the USS file or path to backup.
        bk_file {str} -- The name of the backup file.

    Returns:
        str -- Name of the backup file.
        err_msg -- A message indicating whether the backup was successful or not.
    """
    module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
    err_msg = None
    out = None
    file_name = path.abspath(file)
    ext = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()).lower()
    backup_f = "{0}@{1}-bak.tar".format(file, ext)
    backup_base = path.basename(backup_f)
    if bk_file:
        bk_file_name = path.basename(bk_file)
        if not bk_file_name:
            if not path.exists(bk_file):
                backup_f = bk_file
                err_msg = "Path {0} for the backup does not exist.".format(bk_file)
            else:
                backup_f = path.join(bk_file, backup_base)
        else:
            if path.isdir(bk_file):
                backup_f = path.join(bk_file, backup_base)
            else:
                backup_f = bk_file
    if not err_msg:
        bk_cmd = "tar -cpf {0} {1}".format(quote(backup_f), quote(file_name))
        rc, out, err = module.run_command(bk_cmd)
        if rc:
            raise USSCmdExecError(bk_cmd, rc, out, err)
    return backup_f, err_msg


class USSCmdExecError(Exception):
    def __init__(self, uss_cmd, rc, out, err):
        self.msg = (
            "Failed during execution of usscmd: {0}, Return code: {1}; "
            "stdout: {2}; stderr: {3}".format(uss_cmd, rc, out, err)
        )
        super().__init__(self.msg)
