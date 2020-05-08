# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

import re
from os import path
from random import choice
from string import ascii_uppercase
from ansible.module_utils._text import to_bytes

try:
    from zoautil_py import Datasets, MVSCmd, types
except Exception:
    Datasets = ""
    MVSCmd = ""
    types = ""

__metaclass__ = type

LISTDS_COMMAND = "  LISTDS '{0}'"
LISTCAT_COMMAND = "  LISTCAT ENT({0}) ALL"


class DataSetUtils(object):
    def __init__(self, module, data_set):
        """A standard utility to gather information about
        a particular data set. Note that the input data set is assumed
        to be cataloged.

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object from currently
                                      running module.
            data_set {str} -- Name of the input data set
        """
        self.module = module
        self.data_set = data_set
        self.uss_path = '/' in data_set
        self.ds_info = dict()
        if not self.uss_path:
            self.ds_info = self._gather_data_set_info()

    def data_set_exists(self):
        """Determines whether the input data set exists. The input data
        set can be VSAM or non-VSAM.

        Returns:
            bool -- If the data set exists
        """
        if self.uss_path:
            return path.exists(to_bytes(self.data_set))
        return self.ds_info.get('exists')

    def data_set_member_exists(self, member):
        """Determines whether the input data set contains the given member.

        Arguments:
            member {str} -- The name of the data set member

        Returns:
            bool -- If the member exists
        """
        if self.get_data_set_type() == "PO":
            rc, out, err = self.module.run_command(
                "head \"//'{0}({1})'\"".format(self.data_set, member)
            )
            if rc == 0 and not re.findall(r"EDC5067I", err):
                return True
        return False

    def get_data_set_type(self):
        """Retrieves the data set type of the input data set.

        Returns:
            str  -- Type of the input data set.
            None -- If the data set does not exist or a non-existent USS file

        Possible return values:
            'PS'   -- Physical Sequential
            'PO'   -- Partitioned (PDS or PDS(E))
            'VSAM' -- Virtual Storage Access Method
            'DA'   -- Direct Access
            'IS'   -- Indexed Sequential
            'USS'  -- USS file or directory
        """
        if self.uss_path and self.data_set_exists():
            return 'USS'
        return self.ds_info.get('dsorg')

    @staticmethod
    def create_temp_data_set(
        LLQ,
        ds_type="SEQ",
        size="5M",
        ds_format="FB",
        lrecl=80
    ):
        """Creates a temporary data set with the given low level qualifier.

        Arguments:
            LLQ {str} -- Low Level Qualifier to be used for temporary data set
            ds_type {str} -- The data set type, default: Sequential
            size {str} -- The size of the data set, default: 5M
            format {str} -- The record format of the data set, default: FB
            lrecl {int} -- The record length of the data set, default: 80

        Returns:
            str -- Name of the created data set

        Raises:
            OSError: When non-zero return code is received
            from Datasets.create()
        """
        chars = ascii_uppercase
        HLQ2 = ''.join(choice(chars) for i in range(5))
        HLQ3 = ''.join(choice(chars) for i in range(6))
        temp_ds_name = "{0}.{1}.{2}.{3}".format(Datasets.hlq(), HLQ2, HLQ3, LLQ)

        rc = Datasets.create(temp_ds_name, ds_type, size, ds_format, "", lrecl)
        if rc != 0:
            raise OSError("Unable to create temporary data set")

        return temp_ds_name

    def get_data_set_volume(self):
        """Retrieves the volume name where the input data set is stored.

        Returns:
            str -- Volume where the data set is stored
            None -- If the data set does not exist

        Raises:
            AttributeError -- When input data set is a USS file or directory
        """
        if self.uss_path:
            raise AttributeError(
                "USS file or directory has no attribute 'Volume'"
            )
        return self.ds_info.get('volser')

    def get_data_set_lrecl(self):
        """Retrieves the record length of the input data set. Record length
        specifies the length, in bytes, of each record in the data set.

        Returns:
            int -- The record length, in bytes, of each record
            None -- If the data set does not exist or the data set is VSAM

        Raises:
            AttributeError -- When input data set is a USS file or directory
        """
        if self.uss_path:
            raise AttributeError(
                "USS file or directory has no attribute 'lrecl'"
            )
        return self.ds_info.get('lrecl')

    def get_data_set_recfm(self):
        """Retrieves the record format of the input data set.

        Returns:
            str -- Record format
            None -- If the data set does not exist or the data set is VSAM

        Raises:
            AttributeError -- When input data set is a USS file or directory

        Possible return values:
            'F'   -- Fixed
            'FB'  -- Fixed Blocked
            'V'   -- Variable
            'VB'  -- Variable Blocked
            'U'   -- Undefined
            'VBS' -- Variable Blocked Spanned
            'VS'  -- Variable Spanned
        """
        if self.uss_path:
            raise AttributeError(
                "USS file or directory has no attribute 'recfm'"
            )
        return self.ds_info.get('recfm')

    def _gather_data_set_info(self):
        """Retrieves information about the input data set using LISTDS and
        LISTCAT commands.

        Returns:
            dict -- Dictionary containing data set attributes
        """
        result = dict()

        try:
            listds_out = self._run_mvs_cmd('IKJEFT01', LISTDS_COMMAND.format(self.data_set))
            listcat_out = self._run_mvs_cmd('IDCAMS', LISTCAT_COMMAND.format(self.data_set))
        except Exception:
            raise
        result.update(self._process_listds_output(listds_out))
        result.update(self._process_listcat_output(listcat_out))
        return result

    def _run_mvs_cmd(self, pgm, input_cmd):
        """Executes mvscmd with the given program and input command.

        Arguments:
            pgm {str} -- The name of the MVS program to execute
            input_cmd {str} -- The command to execute

        Returns:
            str -- The generated 'sysprint' of the executed command

        Raises:
            MVSCmdExecError: When non-zero return code is received while
            executing MVSCmd

            DatasetBusyError: When the data set is being edited by another user
        """
        sysprint = "sysprint"
        sysin = "sysin"
        if pgm == "IKJEFT01":
            sysprint = "systsprt"
            sysin = "systsin"

        rc, out, err = self.module.run_command(
            "mvscmdauth --pgm={0} --{1}=* --{2}=stdin".format(pgm, sysprint, sysin),
            data=input_cmd
        )
        if rc != 0:
            if (re.findall(r"ALREADY IN USE", out)):
                raise DatasetBusyError(self.data_set)
            if (re.findall(r"NOT IN CATALOG|NOT FOUND|NOT LISTED", out)):
                self.ds_info['exists'] = False
            else:
                raise MVSCmdExecError(rc, out, err)
        return out

    def _process_listds_output(self, output):
        """Parses the output generated by LISTDS command.

        Arguments:
            output {str} -- The output of LISTDS command

        Returns:
            dict -- Dictionary containing the output parameters of LISTDS
        """
        result = dict()
        if "NOT IN CATALOG" in output:
            result['exists'] = False
        else:
            result['exists'] = True
            ds_search = re.search(r"(-|--)DSORG(-\s*|\s*)\n(.*)", output, re.MULTILINE)
            if ds_search:
                ds_params = ds_search.group(3).split()
                result['dsorg'] = ds_params[-1]
                if result.get('dsorg') != "VSAM":
                    result['recfm'] = ds_params[0]
                    result['lrecl'] = ds_params[1]
        return result

    def _process_listcat_output(self, output):
        """Parses the output generated by LISTCAT command.

        Arguments:
            output {str} -- The output of LISTCAT command

        Returns:
            dict -- Dictionary containing the output parameters of LISTCAT
        """
        result = dict()
        if "NOT FOUND" not in output:
            volser_output = re.findall(r"VOLSER-*[A-Z|0-9]*", output)
            result['volser'] = ''.join(
                re.findall(r"-[A-Z|0-9]*", volser_output[0])
            ).replace('-', '')
        return result


class MVSCmdExecError(Exception):
    def __init__(self, rc, out, err):
        self.msg = (
            "Failure during execution of mvscmd; Return code: {0}; "
            "stdout: {1}; stderr: {2}".format(rc, out, err)
        )
        super().__init__(self.msg)


class DatasetBusyError(Exception):
    def __init__(self, data_set):
        self.msg = (
            "Dataset {0} may already be open by another user. "
            "Close the dataset and try again".format(data_set)
        )
        super().__init__(self.msg)
