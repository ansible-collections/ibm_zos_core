# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dd_statement import *
from ansible.module_utils.basic import AnsibleModule


class MVSCmd(object):
    """Provides an interface to execute authorized and unauthorized MVS commands.
    """

    @staticmethod
    def execute(pgm, dds, args=""):
        """Execute an unauthorized MVS command.

        Args:
            pgm (str): The name of the program to execute.
            dds (list[DDStatement]): A list of DDStatement objects.
            args (str, optional): Argument string if required by the program. Defaults to "".

        Returns:
            MVSCmdResponse: The response of the command.
        """
        module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
        command = "mvscmd " + MVSCmd._build_command(pgm, dds, args)
        rc, out, err = module.run_command(command)
        return MVSCmdResponse(rc, out, err)

    @staticmethod
    def execute_authorized(pgm, dds, args=""):
        """Execute an authorized MVS command.

        Args:
            pgm (str): The name of the program to execute.
            dds (list[DDStatement]): A list of DDStatement objects.
            args (str, optional): Argument string if required by the program. Defaults to "".

        Returns:
            MVSCmdResponse: The response of the command.
        """
        module = AnsibleModule(argument_spec={}, check_invalid_arguments=False)
        command = "mvscmdauth " + MVSCmd._build_command(pgm, dds, args)
        rc, out, err = module.run_command(command)
        return MVSCmdResponse(rc, out, err)

    @staticmethod
    def _build_command(pgm, dds, args):
        """Build the command string to be used by ZOAU mvscmd/mvscmdauth.

        Args:
            pgm (str): [description]
            dds (list[DDStatement]): A list of DDStatement objects.
            args (str, optional): Argument string if required by the program. Defaults to "".

        Returns:
            str: Command string formatted as expected by mvscmd/mvscmdauth.
        """
        args_string = ""
        if args:
            args_string = "--args='{0}'".format(args)
        pgm_string = "--pgm={0}".format(pgm)
        dds_string = ""
        for dd in dds:
            dds_string += " " + dd.get_mvscmd_string()
        command = "{0} {1} {2}".format(pgm_string, args_string, dds_string)
        return command


class MVSCmdResponse(object):
    """Holds response information for MVSCmd call.
    """

    def __init__(self, rc, stdout, stderr):
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
