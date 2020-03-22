# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

import re

try:
    from zoautil_py import Datasets, MVSCmd, types
except Exception:
    Datasets = ""
    MVSCmd = ""
    types = ""

__metaclass__ = type

LISTDS_COMMAND = "LISTDS {0}"
LISTCAT_COMMAND = "LISTCAT ENT({0}) ALL"

class DataSetUtils(object):
    def __init__(self, data_set):
        """A standard utility to gather information about
        a particular data set. Note that the input data set is assumed 
        to be cataloged.

        Arguments:
            data_set {str} -- Name of the input data set
        """
        self.data_set = data_set
        self.ds_info = self._gather_data_set_info(self.data_set)

    def data_set_exists(self):
        """Determines whether the input data set exists.

        Returns:
            bool -- If the data set was found
        """
        return self.ds_info['cataloged']

    def get_data_set_type(self):
        """Retrieves the data set type of the input data set.

        Returns:
            str -- Type of the input data set.

        Possible return values:
            'PS'   -- Physical Sequential
            'PO'   -- Partitioned (PDS or PDS(E))
            'VSAM' -- Virtual Storage Access Method
            'DA'   -- Direct Access
            'IS'   -- Indexed Sequential
            'USS'  -- Unix file or directory
        """
        return self.ds_info['dsorg']

    def get_data_set_volume(self):
        """Retrieves the volume of the input data set is stored.

        Returns:
            str -- Volume where the data set is stored
        """
        return self.ds_info['volser']

    def get_data_set_lrecl(self):
        """Retrieves the record length of the input data set. LRECL specifies 
        the length, in bytes, of each record in the data set.

        Returns:
            int -- The record length, in bytes, of each record
        """
        return self.ds_info['lrecl']

    def get_data_set_recfm(self):
        """Retrieves the record format of the input data set.

        Returns:
            str -- Record format
        
        Possible return values:
            'F'   -- Fixed
            'FB'  -- Fixed Blocked
            'V'   -- Variable
            'VB'  -- Variable Blocked
            'U'   -- Undefined
            'VBS' -- Variable Blocked Spanned
            'VS'  -- Variable Spanned
        """
        return self.ds_info['recfm']

    def create_temp_data_set(self):
        """Creates a temporary data set with the same high level qualifier
        as the input data set.

        Returns:
            str -- Name of the created data set

        Raises:
            RuntimeError: When non-zero return code is received from Datasets.create()
        """
        temp_ds_name = Datasets.temp_name(self.data_set.split(".")[0])
        rc = Datasets.create(
            temp_ds_name,
            {"type": "SEQ", "size": "5M", "format": "FB", "length": 80}
        )
        if rc != 0:
            raise RuntimeError(
                "Unable to create temprary data set while executing IDCAMS"
            )

        return temp_ds_name

    def _gather_data_set_info(self):
        """Retrieves information about the input data set using LISTDS and
        LISTCAT commands

        Returns:
            dict -- Dictionary containing data set attributes
        """
        result = dict()
        listds_out = self._run_mvs_cmd('ikjeft01', LISTDS_COMMAND.format(self.data_set))
        listcat_out = self._run_mvs_cmd('idcams', LISTCAT_COMMAND.format(self.data_set))
        result.update(self._process_listds_output(listds_out))
        result.update(self._process_listcat_output(listcat_out))
        return result

    def _run_mvs_cmd(self, pgm, input_cmd):
        """Executes MVSCmd with the given program and input command

        Returns:
            str -- The generated 'sysprint' of the executed command

        Raises:
            RuntimeError: When non-zero return code is received from 
                          Datasets.write() or Datasets.read()
            MVSCmdExecError: When non-zero return code is received while executing MVSCmd
        """
        try:
            sysin_ds = self.create_temp_data_set()
            sysprint_ds = self.create_temp_data_set()
            rc = Datasets.write(sysin_ds, input_cmd)
            if rc != 0:
                raise RuntimeError(
                    "Unable to write content to temporary dataset while executing IDCAMS"
                )

            if pgm == 'ikjeft01':
                sysin = 'systsin'
                sysprint = 'systsprt'
            else:
                sysin = 'sysin'
                sysprint = 'sysprint'
            
            dd_statements = []
            dd_statements.append(
                types.DDStatement(ddName=sysin, dataset=sysin_ds)
            )
            dd_statements.append(
                types.DDStatement(ddName=sysprint, dataset=sysprint_ds)
            )
            rc = MVSCmd.execute_authorized(pgm=pgm, args="", dds=dd_statements)
            if rc != 0:
                raise MVSCmdExecError(rc)
            return Datasets.read(sysprint_ds)
        except Exception:
            raise
        finally:
            Datasets.delete(sysin_ds)
            Datasets.delete(sysprint_ds)

    def _process_listds_output(self, output):
        """Parses the output generated by LISTDS command.

        Returns:
            dict -- Dictionary containing the output parameters of LISTDS
        """
        result = dict()
        ds_search = re.search(r"(-|--)DSORG(|-)\n(.*)", output, re.MULTILINE)
        if ds_search:
            pass

    def _process_listcat_output(self, output):
        """Parses the output generated by LISTCAT command.

        Returns:
            dict -- Dictionary containing the output parameters of LISTCAT
        """
        pass



class MVSCmdExecError(Exception):
    def __init__(self, rc):
        self.msg = "Unable to execute MVSCmd; Return code: {0}".format(rc)
        super().__init__(msg)


class UncatalogedDatasetError(Exception):
    def __init__(self, data_set):
        self.msg = "The data set {0} is not in catalog".format(data_set)
        super().__init__(msg)
