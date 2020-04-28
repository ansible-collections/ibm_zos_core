# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from tempfile import NamedTemporaryFile, TemporaryDirectory, mkstemp
from math import floor, ceil
from os import path, walk, makedirs, unlink
from ansible.module_utils.six import PY3

import shutil
import errno
import os
import re
import time

try:
    from zoautil_py import Datasets, MVSCmd
except Exception:
    Datasets = ""
    MVSCmd = ""


if PY3:
    from shlex import quote
else:
    from pipes import quote


REPRO = '''  REPRO INDATASET({}) -
    OUTDATASET({}) REPLACE '''
BACKUP = ''' COPY DATASET(INCLUDE( {0} )) -
    RENUNC({0}, -
    {1}) -
    CATALOG -
    OPTIMIZE(4) '''
LISTCAT = " LISTCAT ENT('{}') ALL"


class EncodeUtils(object):
    def __init__(self, module):
        """Call the coded character set conversion utility iconv
        to convert a USS file from one coded character set to another

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object from currently running module
        """
        self.module = module

    def run_uss_cmd(self, uss_cmd, data=None):
        """Call AnsibleModule.run_command() to execute USS command

        Arguments:
            uss_cmd {str} -- The USS command to be executed.
        Raises:
            USSCmdExecError: When any exception is raised during the conversion
        Returns:
            boolean -- The return code after the USS command executed successfully
            str -- The stdout after the USS command executed successfully
            str -- The stderr after the USS command executed successfully
        """
        out = None
        err = None
        rc, stdout, stderr = self.module.run_command(uss_cmd, data=data, use_unsafe_shell=True)
        if rc:
            out = stdout
            err = stderr
            raise USSCmdExecError(uss_cmd, rc, out, err)
        else:
            out = stdout
            err = stderr
        return rc, out, err

    def listdsi_data_set(self, ds):
        """Invoke IDCAMS LISTCAT command to get the record length and space used
        to estimate the space used by the VSAM data set

        Arguments:
            ds: {str} -- The VSAM data set to be checked.

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
        Returns:
            int -- The maximum record length of the VSAM data set.
            int -- The space used by the VSAM data set(KB).
        """
        reclen = 80
        space_u = 1024
        listcat_cmd = LISTCAT.format(ds)
        cmd = 'mvscmdauth --pgm=ikjeft01 --systsprt=stdout --systsin=stdin'
        rc, out, err = self.run_uss_cmd(cmd, data=listcat_cmd)
        if out:
            find_reclen = re.findall(r'MAXLRECL-*\d+', out)
            find_cisize = re.findall(r'CISIZE-*\d+', out)
            find_recnum = re.findall(r'REC-TOTAL-*\d+', out)
            find_freeci = re.findall(r'FREESPACE-%CI-*\d+', out)
            find_freeca = re.findall(r'FREESPACE-%CA-*\d+', out)
            find_cioca = re.findall(r'CI/CA-*\d+', out)
            find_trkoca = re.findall(r'TRACKS/CA-*\d+', out)
            if find_reclen:
                reclen = int(''.join(re.findall(r'\d+', find_reclen[0])))
            if find_cisize:
                cisize = int(''.join(re.findall(r'\d+', find_cisize[0])))
            if find_recnum:
                recnum = int(''.join(re.findall(r'\d+', find_recnum[0])))
            if find_freeci:
                freeci = int(''.join(re.findall(r'\d+', find_freeci[0])))
            if find_freeca:
                freeca = int(''.join(re.findall(r'\d+', find_freeca[0])))
            if find_cioca:
                cioca = int(''.join(re.findall(r'\d+', find_cioca[0])))
            if find_trkoca:
                trkoca = int(''.join(re.findall(r'\d+', find_trkoca[0])))

            # Algorithm used for VSAM data set space evaluation
            # Step01. Get the number of records in each VSAM CI
            # Step02. The CI used by the VSAM data set
            # Step03. The CA used by the VSAM data set
            # Step04. Calculate the VSAM data set space using the CA number
            # This value will be used by the temporary PS when coping a VSAM data set
            # For DASD volume type 3390, 56664 bytes per track
            rec_in_ci = floor((cisize - cisize * freeci - 10) / reclen)
            ci_num = ceil(recnum / rec_in_ci)
            ca_num = ceil(ci_num / (cioca * (1 - freeca)))
            if ca_num > 0:
                space_u = ceil(ca_num * trkoca * 566664 / 1024)
        return reclen, space_u

    def temp_data_set(self, reclen, space_u):
        """Creates a temporary data set with the given record length and size

        Arguments:
            size {str} -- The size of the data set
            lrecl {int} -- The record length of the data set

        Returns:
            str -- Name of the allocated data set

        Raises:
            OSError: When any exception is raised during the data set allocation
        """
        size = str(space_u * 2) + 'K'
        hlq = Datasets.hlq()
        temp_ps = Datasets.temp_name(hlq)
        rc = Datasets.create(temp_ps, 'SEQ', size, 'FB', '', reclen)
        if rc:
            raise OSError("Failed when allocating temporary sequential data set!")
        return temp_ps

    def mvs_file_backup(self, dsn, bk_dsn):
        """Create a backup data set for an MVS data set

        Arguments:
            dsn {str} -- The name of the data set to be backuped.
                         It could be an MVS PS/PDS/PDSE/VSAM(KSDS), etc.
            bk_dsn {str} -- The name of the backup data set.

        Returns:
            str -- Name of the backup data set.
            err_msg -- The message to indicate the backup is successfully or not.
        """
        err_msg = None
        out = None
        if not bk_dsn:
            hlq = Datasets.hlq()
            bk_dsn = Datasets.temp_name(hlq)
        bk_sysin = BACKUP.format(dsn, bk_dsn)
        bkup_cmd = "mvscmdauth --pgm=adrdssu --sysprint=stdout --sysin=stdin"
        rc, stdout, stderr = self.module.run_command(bkup_cmd, data=bk_sysin, use_unsafe_shell=True)
        if rc > 4:
            out = stdout
            if 'DUPLICATE' in out:
                err_msg = 'Backup data set {0} exists, please check'.format(bk_dsn)
            else:
                err_msg = "Failed when creating the backup of the data set {0} : {1}". format(dsn, out)
                if Datasets.exists(bk_dsn):
                    Datasets.delete(bk_dsn)
        return bk_dsn, err_msg

    def uss_file_backup(self, file, bk_file):
        """Create a backup file for a USS file or path

        Arguments:
            file {str} -- The name of the USS file or path to be backuped.
            bk_file {str} -- The name of the backup file.

        Returns:
            str -- Name of the backup file.
            err_msg -- The message to indicate the backup is successfully or not.
        """
        err_msg = None
        out = None
        file_name = path.abspath(file)
        ext = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()).lower()
        backup_f = '{0}@{1}-bak.tar'.format(file, ext)
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
            bk_cmd = 'tar -cpf {0} {1}'.format(quote(backup_f), quote(file_name))
            rc, out, err = self.run_uss_cmd(bk_cmd)
        return backup_f, err_msg

    def copy_uss2mvs(self, src, dest, ds_type):
        """Copy uss a file or path to an MVS data set

        Arguments:
            src: {str} -- The uss file or path to be copied
            dest: {str} -- The destination MVS data set, it must be a PS or PDS(E)
            ds_type: {str} -- The dsorg of the dest.

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
        Returns:
            boolean -- The return code after the copy command executed successfully
            str -- The stdout after the copy command executed successfully
            str -- The stderr after the copy command executed successfully
        """

        if ds_type == 'PO':
            cp_uss2mvs = 'cp -CM -F rec {0} "//\'{1}\'"'.format(quote(src), dest)
        else:
            cp_uss2mvs = 'cp -F rec {0} "//\'{1}\'" '.format(quote(src), dest)
        rc, out, err = self.run_uss_cmd(cp_uss2mvs)
        return rc, out, err

    def copy_ps2uss(self, src, dest):
        """Copy a PS data set to a uss file

        Arguments:
            src: {str} -- The MVS data set to be copied, it must be a PS data set
            or a PDS(E) member
            dest: {str} -- The destination uss file

        Raises:
            USSCmdExecError: When any exception is raised during the conversion
        Returns:
            boolean -- The return code after the copy command executed successfully
            str -- The stdout after the copy command executed successfully
            str -- The stderr after the copy command executed successfully
        """
        cp_ps2uss = 'cp -F rec "//\'{0}\'" {1}'.format(src, quote(dest))
        rc, out, err = self.run_uss_cmd(cp_ps2uss)
        return rc, out, err

    def copy_pds2uss(self, src, dest):
        """Copy the whole PDS(E) to a uss path

        Arguments:
            src: {str} -- The MVS data set to be copied, it must be a PDS(E) data set
            dest: {str} -- The destination uss path

        Raises:
            USSCmdExecError: When any exception is raised during the conversion.
        Returns:
            boolean -- The return code after the USS command executed successfully
            str -- The stdout after the USS command executed successfully
            str -- The stderr after the USS command executed successfully
        """
        cp_pds2uss = 'cp -U -F rec "//\'{0}\'" {1}'.format(src, quote(dest))
        rc, out, err = self.run_uss_cmd(cp_pds2uss)
        return rc, out, err

    def copy_vsam_ps(self, src, dest):
        """Copy a VSAM(KSDS) data set to a PS data set vise versa

        Arguments:
            src: {str} -- The VSAM(KSDS) or PS data set to be copied
            dest: {str} -- The PS or VSAM(KSDS) data set

        Raises:
            USSCmdExecError: When any exception is raised during the conversion
        Returns:
            boolean -- The return code after the USS command executed successfully
            str -- The stdout after the USS command executed successfully
            str -- The stderr after the USS command executed successfully
        """
        repro_cmd = REPRO.format(src, dest)
        cmd = 'mvscmdauth --pgm=idcams --sysprint=stdout --sysin=stdin'
        rc, out, err = self.run_uss_cmd(cmd, data=repro_cmd)
        return rc, out, err

    def get_codeset(self):
        """Get the list of supported encodings from the  USS command 'iconv -l'

        Raises:
            USSCmdExecError: When any exception is raised during the conversion
        Returns:
            list -- The code set list supported in current USS platform
        """
        code_set = None
        iconv_list_cmd = ['iconv', '-l']
        rc, out, err = self.run_uss_cmd(iconv_list_cmd)
        if out:
            code_set_list = list(filter(None, re.split(r'[\n|\t]', out)))
            code_set = [c for i, c in enumerate(code_set_list) if i > 0 and i % 2 == 0]
        return code_set

    def string_convert_encoding(self, src, from_encoding, to_encoding):
        """Convert the encoding of the data when the src is a normal string

        Arguments:
            from_code_set: {str} -- The source code set of the string
            to_code_set: {str} -- The destination code set for the string
            src: {str} -- The input string content

        Raises:
            USSCmdExecError: When any exception is raised during the conversion
        Returns:
            str -- The string content after the encoding
        """
        iconv_cmd = 'printf {0} | iconv -f {1} -t {2}'.format(
            quote(src), quote(from_encoding), quote(to_encoding))
        rc, out, err = self.run_uss_cmd(iconv_cmd)
        return out

    def uss_convert_encoding(self, src, dest, from_code, to_code):
        """Convert the encoding of the data in a USS file

        Arguments:
            from_code: {str} -- The source code set of the input file
            to_code: {str} -- The destination code set for the output file
            src: {str} -- The input file name, it should be a uss file
            dest: {str} -- The output file name, it should be a uss file

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
            temp_fo, temp_fi = mkstemp()
        iconv_cmd = 'iconv -f {0} -t {1} {2} > {3}'.format(
                    quote(from_code), quote(to_code), quote(src), quote(temp_fi))
        try:
            rc, out, err = self.run_uss_cmd(iconv_cmd)
            if dest == temp_fi:
                convert_rc = True
            else:
                try:
                    src_mode = os.stat(src).st_mode
                    temp_mode = os.stat(temp_fi).st_mode
                    if src_mode != temp_mode:
                        os.chmod(temp_fi, src_mode)
                    shutil.move(temp_fi, dest)
                    convert_rc = True
                except (OSError, IOError) as e:
                    raise MoveFileError(src, dest, e)
        except Exception:
            raise
        finally:
            if temp_fo:
                try:
                    unlink(temp_fi)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
        return convert_rc

    def uss_convert_encoding_prev(self, src, dest, from_code, to_code):
        """ For multiple files conversion, such as a USS path or MVS PDS data set,
        use this method to split then do the conversion

        Arguments:
            from_code: {str} -- The source code set of the input path
            to_code: {str} -- The destination code set for the output path
            src: {str} -- The input uss path or a file
            dest: {str} -- The output uss path or a file

        Raises:
            OSError: When direcotry is empty or copy multiple files to a single file
        Returns:
            boolean -- Indicate whether the conversion is successful or not
            str -- Returned error messages
        """
        convert_rc = False
        err_msg = None
        file_list = list()
        try:
            if path.isdir(src):
                for (dir, subdir, files) in walk(src):
                    for file in files:
                        file_list.append(path.join(dir, file))
                if len(file_list) == 0:
                    err_msg = "Directory {0} is empty. Please check the path.".format(src)
                elif len(file_list) == 1:
                    if path.isdir(dest):
                        file_name = path.basename(file_list[0])
                        src_f = path.join(src, file_name)
                        dest_f = path.join(dest, file_name)
                    convert_rc = self.uss_convert_encoding(src_f, dest_f, from_code, to_code)
                else:
                    if path.isfile(dest):
                        err_msg = (
                            "Can't convert multiple files (src) {0} to a single file"
                            " (dest) {1}.".format(src, dest)
                        )
                    else:
                        for file in file_list:
                            if dest == src:
                                dest_f = file
                            else:
                                dest_f = file.replace(src, dest, 1)
                                dest_dir = path.dirname(dest_f)
                                if not path.exists(dest_dir):
                                    makedirs(dest_dir)
                            convert_rc = self.uss_convert_encoding(file, dest_f, from_code, to_code)
            else:
                if path.isdir(dest):
                    file_name = path.basename(path.abspath(src))
                    dest = path.join(dest, file_name)
                convert_rc = self.uss_convert_encoding(src, dest, from_code, to_code)
        except Exception:
            raise
        return convert_rc, err_msg

    def mvs_convert_encoding(self, src, dest, src_type, dest_type, from_code, to_code):
        """Convert the encoding of the data from
           1) USS to MVS(PS, PDS/E VSAM)
           2) MVS to USS
           3) MVS to MVS

        Arguments:
            src: {str} -- The input MVS data set to be converted
            dest: {str} -- The output MVS data set
            src_type: {str} -- The input MVS data set type: PS, PDS, PDSE, VSAM(KSDS)
            dest_type: {str} -- The output MVS data set type
            from_code: {str} -- The source code set of the input MVS data set
            to_code: {str} -- The destination code set of the output MVS data set

        Returns:
            boolean -- Indicate whether the conversion is successful or not
            str -- Returned error messages
        """
        convert_rc = False
        temp_ps = None
        temp_src = src
        temp_dest = dest
        try:
            if src_type == 'PS':
                temp_src_fo = NamedTemporaryFile()
                temp_src = temp_src_fo.name
                rc, out, err = self.copy_ps2uss(src, temp_src)
            if src_type == 'PO':
                temp_src_fo = TemporaryDirectory()
                temp_src = temp_src_fo.name
                rc, out, err = self.copy_pds2uss(src, temp_src)
            if src_type == 'VSAM':
                reclen, space_u = self.listdsi_data_set(src.upper())
                temp_ps = self.temp_data_set(reclen, space_u)
                rc, out, err = self.copy_vsam_ps(src.upper(), temp_ps)
                temp_src_fo = NamedTemporaryFile()
                temp_src = temp_src_fo.name
                rc, out, err = self.copy_ps2uss(temp_ps, temp_src)
            if dest_type == 'PS' or dest_type == 'VSAM':
                temp_dest_fo = NamedTemporaryFile()
                temp_dest = temp_dest_fo.name
            if dest_type == 'PO':
                temp_dest_fo = TemporaryDirectory()
                temp_dest = temp_dest_fo.name
            rc, err_msg = self.uss_convert_encoding_prev(temp_src, temp_dest, from_code, to_code)
            if rc:
                if not dest_type:
                    convert_rc = True
                else:
                    if dest_type == 'VSAM':
                        reclen, space_u = self.listdsi_data_set(dest.upper())
                        temp_ps = self.temp_data_set(reclen, space_u)
                        rc, out, err = self.copy_uss2mvs(temp_dest, temp_ps, 'PS')
                        rc, out, err = self.copy_vsam_ps(temp_ps, dest.upper())
                        convert_rc = True
                    elif dest_type == 'PO':
                        for (dir, subdir, files) in walk(temp_dest):
                            for file in files:
                                temp_file = path.join(dir, file)
                                rc, out, err = self.copy_uss2mvs(temp_file, dest, 'PO')
                                convert_rc = True
                    else:
                        rc, out, err = self.copy_uss2mvs(temp_dest, dest, dest_type)
                        convert_rc = True
        except Exception:
            raise
        finally:
            if temp_ps:
                Datasets.delete(temp_ps)
        return convert_rc, err_msg


class USSCmdExecError(Exception):
    def __init__(self, uss_cmd, rc, out, err):
        self.msg = (
            "Failed during execution of usscmd: {0}, Return code: {1}; "
            "stdout: {2}; stderr: {3}".format(uss_cmd, rc, out, err)
        )
        super().__init__(self.msg)


class MoveFileError(Exception):
    def __init__(self, src, dest, e):
        self.msg = ("Failed when moving {0} to {1}: {2}".format(src, dest, e))
        super().__init__(self.msg)
