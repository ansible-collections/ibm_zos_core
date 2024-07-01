# Copyright (c) IBM Corporation 2019, 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible.module_utils.six import PY3
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.mvs_cmd import (
    ikjeft01
)

from shlex import quote


REPRO = """  REPRO INDATASET({}) -
    OUTDATASET({}) REPLACE """


def _validate_data_set_name(ds):
    """Validate data set name using BetterArgParser.

    Parameters
    ----------
    ds : str
        The source dataset.

    Returns
    -------
    str
        Parsed dataset.
    """
    arg_defs = dict(ds=dict(arg_type="data_set"),)
    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args({"ds": ds})
    return parsed_args.get("ds")


def _validate_path(path):
    """Validate path using BetterArgParser.

    Parameters
    ----------
    path : str
        The path.

    Returns
    -------
    str
        Parsed path.
    """
    arg_defs = dict(path=dict(arg_type="path"),)
    parser = BetterArgParser(arg_defs)
    parsed_args = parser.parse_args({"path": path})
    return parsed_args.get("path")


def copy_uss2mvs(src, dest, ds_type, is_binary=False):
    """Copy uss a file or path to an MVS data set.

    Parameters
    ----------
    src : str
        The uss file or path to be copied.
    dest : str
        The destination MVS data set, it must be a PS or PDS(E).
    ds_type : str
        The dsorg of the dest.

    Keyword Parameters
    ------------------
    is_binary : bool
        Whether the file to be copied contains binary data.

    Returns
    -------
    bool
        The return code after the copy command executed successfully.
    str
        The stdout after the copy command executed successfully.
    str
        The stderr after the copy command executed successfully.

    Raises
    ------
    USSCmdExecError
        When any exception is raised during the conversion.
    """
    module = AnsibleModuleHelper(argument_spec={})
    src = _validate_path(src)
    dest = _validate_data_set_name(dest)
    if ds_type == "PO":
        cp_uss2mvs = "cp -CM -F rec {0} \"//'{1}'\"".format(quote(src), dest)
    else:
        cp_uss2mvs = "cp -F rec {0} \"//'{1}'\"".format(quote(src), dest)
    if is_binary:
        cp_uss2mvs = cp_uss2mvs.replace("rec", "bin", 1)
    rc, out, err = module.run_command(cp_uss2mvs)
    if rc:
        raise USSCmdExecError(cp_uss2mvs, rc, out, err)
    return rc, out, err


def copy_ps2uss(src, dest, is_binary=False):
    """Copy a PS data set to a uss file.

    Parameters
    ----------
    src : str
        The MVS data set to be copied, it must be a PS data set
        or a PDS(E) member.
    dest : str
        The destination uss file.

    Keyword Parameters
    ------------------
    is_binary : bool
        Whether the file to be copied contains binary data.

    Returns
    -------
    bool
        The return code after the copy command executed successfully.
    str
        The stdout after the copy command executed successfully.
    str
        The stderr after the copy command executed successfully.

    Raises
    ------
    USSCmdExecError
        When any exception is raised during the conversion.
    """
    module = AnsibleModuleHelper(argument_spec={})
    src = _validate_data_set_name(src)
    dest = _validate_path(dest)
    cp_ps2uss = "cp -F rec \"//'{0}'\" {1}".format(src, quote(dest))
    if is_binary:
        cp_ps2uss = cp_ps2uss.replace("rec", "bin", 1)
    rc, out, err = module.run_command(cp_ps2uss)
    if rc:
        raise USSCmdExecError(cp_ps2uss, rc, out, err)
    return rc, out, err


def copy_pds2uss(src, dest, is_binary=False, asa_text=False):
    """Copy the whole PDS(E) to a uss path.

    Parameters
    ----------
    src : str
        The MVS data set to be copied, it must be a PDS(E) data set.
    dest : str
        The destination uss path.

    Keyword Parameters
    ------------------
    is_binary : bool
        Whether the file to be copied contains binary data.
    asa_text : bool
        Whether the file to be copied contains ASA control
        characters.

    Returns
    -------
    bool
        The return code after the USS command executed successfully.
    str
        The stdout after the USS command executed successfully.
    str
        The stderr after the USS command executed successfully.

    Raises
    ------
    USSCmdExecError
        When any exception is raised during the conversion.
    """
    module = AnsibleModuleHelper(argument_spec={})
    src = _validate_data_set_name(src)
    dest = _validate_path(dest)

    cp_pds2uss = "cp -U -F rec \"//'{0}'\" {1}".format(src, quote(dest))

    # When dealing with ASA control chars, each record follows a
    # different format than what '-F rec' means, so we remove it
    # to allow the system to leave the control chars in the
    # destination.
    if asa_text:
        cp_pds2uss = cp_pds2uss.replace("-F rec", "", 1)
    elif is_binary:
        cp_pds2uss = cp_pds2uss.replace("rec", "bin", 1)

    rc, out, err = module.run_command(cp_pds2uss)
    if rc:
        raise USSCmdExecError(cp_pds2uss, rc, out, err)

    return rc, out, err


def copy_uss2uss_binary(src, dest):
    """Copy a USS file to a USS location in binary mode.

    Parameters
    ----------
    src : str
        The source USS path.
    dest : str
        The destination USS path.

    Returns
    -------
    bool
        The return code after the USS command executed successfully.
    str
        The stdout after the USS command executed successfully.
    str
        The stderr after the USS command executed successfully.

    Raises
    ------
    USSCmdExecError
        When any exception is raised during the conversion.
    """
    module = AnsibleModuleHelper(argument_spec={})
    src = _validate_path(src)
    dest = _validate_path(dest)
    cp_uss2uss = "cp -F bin {0} {1}".format(quote(src), quote(dest))
    rc, out, err = module.run_command(cp_uss2uss)
    if rc:
        raise USSCmdExecError(cp_uss2uss, rc, out, err)
    return rc, out, err


def copy_mvs2mvs(src, dest, is_binary=False):
    """Copy an MVS source to MVS target.

    Parameters
    ----------
    src : str
        Name of source data set.
    dest : str
        Name of destination data set.

    Keyword Parameters
    ------------------
    is_binary : bool
        Whether the data set to be copied contains binary data.

    Returns
    -------
    bool
        The return code after the USS command executed successfully.
    str
        The stdout after the USS command executed successfully.
    str
        The stderr after the USS command executed successfully.

    Raises
    ------
    USSCmdExecError
        When any exception is raised during the conversion.
    """
    module = AnsibleModuleHelper(argument_spec={})
    src = _validate_data_set_name(src)
    dest = _validate_data_set_name(dest)
    cp_mvs2mvs = "cp -F rec \"//'{0}'\" \"//'{1}'\"".format(src, dest)
    if is_binary:
        cp_mvs2mvs = cp_mvs2mvs.replace("rec", "bin", 1)
    rc, out, err = module.run_command(cp_mvs2mvs)
    if rc:
        raise USSCmdExecError(cp_mvs2mvs, rc, out, err)
    return rc, out, err


def copy_vsam_ps(src, dest):
    """Copy a VSAM(KSDS) data set to a PS data set vise versa.

    Parameters
    ----------
    src : str
        The VSAM(KSDS) or PS data set to be copied.
    dest : str
        The PS or VSAM(KSDS) data set.

    Returns
    -------
    bool
        The return code after the USS command executed successfully.
    str
        The stdout after the USS command executed successfully.
    str
        The stderr after the USS command executed successfully.

    Raises
    ------
    USSCmdExecError
        When any exception is raised during the conversion.
    """
    module = AnsibleModuleHelper(argument_spec={})
    src = _validate_data_set_name(src)
    dest = _validate_data_set_name(dest)
    repro_cmd = REPRO.format(src, dest)
    cmd = "mvscmdauth --pgm=idcams --sysprint=stdout --sysin=stdin"
    rc, out, err = module.run_command(cmd, data=repro_cmd)
    if rc:
        raise USSCmdExecError(cmd, rc, out, err)
    return rc, out, err


def copy_asa_uss2mvs(src, dest):
    """Copy a file from USS to an ASA sequential data set or PDS/E member.

    Parameters
    ----------
    src : str
        Path of the USS file.
    dest : str
        The MVS destination data set or member.

    Returns
    -------
    bool
        The return code after the copy command executed successfully.
    str
        The stdout after the copy command executed successfully.
    str
        The stderr after the copy command executed successfully.
    """
    oget_cmd = "OGET '{0}' '{1}'".format(src, dest)
    rc, out, err = ikjeft01(oget_cmd, authorized=True)

    return TSOCmdResponse(rc, out, err)


def copy_asa_mvs2uss(src, dest):
    """Copy an ASA sequential data set or member to USS.

    Parameters
    ----------
    src : str
        The MVS data set to be copied.
    dest : str
        Destination path in USS.

    Returns
    -------
    bool
        The return code after the copy command executed successfully.
    str
        The stdout after the copy command executed successfully.
    str
        The stderr after the copy command executed successfully.
    """
    src = _validate_data_set_name(src)
    dest = _validate_path(dest)

    oput_cmd = "OPUT '{0}' '{1}'".format(src, dest)
    rc, out, err = ikjeft01(oput_cmd, authorized=True)

    return TSOCmdResponse(rc, out, err)


def copy_asa_pds2uss(src, dest):
    """Copy all members from an ASA PDS/E to USS.

    Parameters
    ----------
    src : str
        The MVS data set to be copied.
    dest : str
        Destination path in USS (must be a directory).

    Returns
    -------
    bool
        The return code after the copy command executed successfully.
    str
        The stdout after the copy command executed successfully.
    str
        The stderr after the copy command executed successfully.
    """
    from os import path
    import traceback
    from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
        ZOAUImportError,
    )

    try:
        from zoautil_py import datasets
    except Exception:
        datasets = ZOAUImportError(traceback.format_exc())

    src = _validate_data_set_name(src)
    dest = _validate_path(dest)

    for member in datasets.list_members(src):
        src_member = '{0}({1})'.format(src, member)
        dest_path = path.join(dest, member)

        oput_cmd = "OPUT '{0}' '{1}'".format(src_member, dest_path)
        rc, out, err = ikjeft01(oput_cmd, authorized=True)

        if rc != 0:
            return TSOCmdResponse(rc, out, err)

    return TSOCmdResponse(0, '', '')


class TSOCmdResponse():
    def __init__(self, rc, stdout, stderr):
        """Builds TSO cmd response.

        Parameters
        ----------
        rc : int
            Return code.
        stdout : str
            Standard output.
        stderr : str
            Standard error.

        Attributes
        ----------
        rc : int
            Return code.
        stdout : str
            Standard output.
        stderr : str
            Standard error.
        """
        self.rc = rc
        self.stdout_response = stdout
        self.stderr_response = stderr


class USSCmdExecError(Exception):
    def __init__(self, uss_cmd, rc, out, err):
        """Error during USS cmd execution.

        Parameters
        ----------
        uss_cmd : str
            USS command.
        rc : int
            Return code.
        out : str
            Standard output.
        err : str
            Standard error.

        Attributes
        ----------
        msg : str
            Human readable string describing the exception.
        """
        self.msg = (
            "Failed during execution of usscmd: {0}, Return code: {1}; "
            "stdout: {2}; stderr: {3}".format(uss_cmd, rc, out, err)
        )
        super().__init__(self.msg)
