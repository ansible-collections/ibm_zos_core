# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import PY3
from tempfile import NamedTemporaryFile
import shutil
import re

if PY3: 
    from shlex import quote
else:
    from pipes import quote


class EncodeUtils(object):
    def __init__(self, module):
        """Call the coded character set conversion utility iconv 
        to convert a USS file from one coded character set to another.

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object from currently running module.
        """
        self.module = module

    def run_uss_cmd(self, uss_cmd):
        """Call AnsibleModule.run_command() to execute USS command. 

        Arguments:
            uss_cmd {str} -- The USS command to be executed.
        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
        Returns:
            str -- The stdout after the USS command executed successfully.
        """
        rc, out, err = self.module.run_command(uss_cmd, use_unsafe_shell=True )
        if rc:
            raise USSCmdExecError(uss_cmd, rc, out, err)
        return out

    def get_codeset(self):
        """Get the list of supported encodings from the  USS command 'iconv -l' 

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
        Returns:
            list -- The code set list supported in current USS platform.
        """
        code_set = None
        iconv_list_cmd = ['iconv', '-l']
        out = self.run_uss_cmd(iconv_list_cmd)
        if out:
            code_set_list = list(filter(None, re.split(r'[\n|\t]', out)))
            code_set = [c for i, c in enumerate(code_set_list) if i > 0 and i % 2 == 0]
        return code_set

    def string_convert_encoding(self, src, blksize, from_encoding, to_encoding):
        """Convert the encoding of the data when the src is a normal string.

        Arguments:
            from_code_set: {str} -- The source code set of the string.
            to_code_set: {str} -- The destination code set for the string.
            src: {str} -- The input string content.
            blksize: {int} -- The maximum length, in bytes, of a data block.

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
        Returns:
            str -- The string content after the encoding.
        """
        #blksize = 1024
        #blksize = 27920
        converted = ''
        with NamedTemporaryFile(mode='w+') as temp:
            temp.write(src)
            temp.seek(0)
            while True:
                to_be_converted = temp.read(blksize)
                if not to_be_converted:
                    break
                iconv_cmd = 'printf {} | iconv -f {} -t {}'.format(\
                     quote(to_be_converted), quote(from_encoding), quote(to_encoding))
                out = run_uss_cmd(iconv_cmd)
                converted = converted + out
        return converted

    def uss_convert_encoding(self, src, dest, from_code_set, to_code_set):
        """Convert the encoding of the data in a USS file.

        Arguments:
            from_code_set: {str} -- The source code set of the input file.
            to_code_set: {str} -- The destination code set for the output file.
            src: {str} -- The input file name, it should be a uss file.
            dest: {str} -- The output file name, it should be a uss file.

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
            MoveFileError: When any exception is raised during moving files.
        Returns:
            boolean -- Indicate whether the conversion is successful or not.
        """
        convert_rc = False
        temp_fo = None
        if not src == dest:
            temp_fi = dest
        else:
            temp_fo = NamedTemporaryFile()
            temp_fi = temp_fo.name
        iconv_cmd = 'iconv -f {0} -t {1} {2} > {3}'.format(\
                    quote(from_code_set), quote(to_code_set), quote(src), quote(temp_fi))
        try:
            out = self.run_uss_cmd(iconv_cmd)
            if dest == temp_fi:
                convert_rc = True
            else:
                try:
                    shutil.move(temp_fi, dest)
                    convert_rc = True
                except (OSError, IOError, Error) as e:
                    raise MoveFileError(src, dest, e)
        except Exception:
            raise
        return convert_rc

    def mvs_convert_encoding(self, src, dest, from_code_set, to_code_set):
        """Convert the encoding of the data when the src is an MVS data set.

        Arguments:
            from_code_set: {str} -- The source code set of the input file.
            to_code_set: {str} -- The the destination code set for the output file.
            src: {str} -- The input data set name, it should be an MVS data set.
            dest: {str} -- The output file name, it should be a uss file.

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
            MoveFileError: When any exception is raised during moving files.
        Returns:
            boolean -- Indicate whether the conversion is successful or not.
        """
        convert_rc = False
        iconv_cmd = 'cat "//\'{0}\'" | iconv -f {1} -t {2} > {3}'.format(\
                    quote(src), from_code_set, to_code_set, dest)
        out = self.run_uss_cmd(iconv_cmd)
        convert_rc = True
        return convert_rc

class USSCmdExecError(Exception):
    def __init__(self, uss_cmd, rc, out, err):
        self.msg = ("Failed during execution of usscmd: {0}, Return code: {1}; "
                    "stdout: {2}; stderr: {3}".format(uss_cmd, rc, out, err)
        )
        super().__init__(self.msg)

class MoveFileError(Exception):
    def __init__(self, src, dest, e):
        self.msg = ("Failed when moving {0} to {1}: {2}".format(src, dest, e))
        super().__init__(self.msg)
