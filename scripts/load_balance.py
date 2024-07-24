import argparse
from enum import Enum
import itertools
import json
import math
import os
import sys, getopt
import subprocess
import pprint as pprint
from os.path import join
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from socket import error
import textwrap
from paramiko import SSHClient, AutoAddPolicy, BadHostKeyException, \
    AuthenticationException, SSHException, ssh_exception

# Thread pool
from os import makedirs
from os.path import basename
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from contextlib import contextmanager
import time
from datetime import datetime
import concurrent.futures
from collections import OrderedDict, namedtuple

from typing import List, Set, Type, Tuple
from prettytable import PrettyTable, ALL


# ==============================================================================
# Enums
# ==============================================================================
class Status (Enum):
    ONLINE=(1, "online")
    OFFLINE=(0, "offline")

    def __str__(self) -> str:
        return self.name.lower()

    def number(self) -> int:
        return self.value[0]

    def string(self) -> str:
        return self.value[1]

    def is_equal(self, other) -> bool:
        return self.number() == other.number()

    def is_online(self) -> bool:
        return self.number() == 1

    @classmethod
    def default(cls):
        """
        Return default status of ONLINE.

        Return
        ------
        Status
            Return the ONLINE status.
        """
        return cls.ONLINE

class State (Enum):
    SUCCESS=(1, "success")
    FAILURE=(0, "failure")
    EXCEEDED=(2, "exceeded-max-failure")

    def __str__(self) -> str:
        return self.name.upper()

    def number(self) -> int:
        return self.value[0]

    def string(self) -> str:
        return self.value[1]

    def is_equal(self, other) -> bool:
        return self.number() == other.number()

    def is_success(self) -> bool:
        return self.number() == 1

    def is_failure(self) -> bool:
        return self.number() == 0

    def is_balanced(self) -> bool:
        return self.number() == 2
# ==============================================================================
# Class definitions
# ==============================================================================

# ------------------------------------------------------------------------------
# Class Dictionary
# ------------------------------------------------------------------------------

class Dictionary():
    """
    This is a wrapper class around a dictionary that provides additional locks
    and logic when interacting with any of the dictionaries being accessed by
    a thread pool to ensure successful execution.
    """
    def __init__(self):
        self._shared_dictionary = dict()
        self._lock = Lock()

    @contextmanager
    def acquire_with_timeout(self, timeout=-1):
        result = self._lock.acquire(timeout=timeout)
        try:
            yield result
        finally:
            if result:
                self._lock.release()

    # Likely works but not tested but also saw no need for this.
    # def remove_items(self, remove):
    #     for key in list(remove.keys()):
    #         with self._lock:
    #             if key in self._shared_dictionary:
    #                 self._shared_dictionary.pop(key)

    def pop(self, key, timeout = 100):
        """
        Removes the entry from the dictionary and returns it. No longer in
        dictionary.
        """
        with self.acquire_with_timeout(timeout) as acquired:
            if acquired:
                if self._shared_dictionary:
                    if key in self._shared_dictionary:
                        return self._shared_dictionary.pop(key)
        return None

    def get(self, key, timeout=10):
        """
        Returns the value of the dictionary entry, entry remains in the dictionary
        """
        with self.acquire_with_timeout(timeout) as acquired:
            if acquired:
                return self._shared_dictionary[key]

    def update(self, key, obj):
        """
        Replace or add a dictionary entry. Same as add(...).
        """
        with self._lock:
            self._shared_dictionary[key]=obj

    def add(self, key, obj):
        """
        Replace or add a dictionary entry. Same as update(...).
        """
        with self._lock:
            self._shared_dictionary[key]=obj

    def items(self):
        """
        Returns a tuple (key, value) for each entry in the dictionary.
        """
        with self._lock:
            return self._shared_dictionary.items()

    def len(self):
        """
        Returns the length of the dictionary. Note its a member function to the
        class to be used such <dictionary>.len().
        """
        with self._lock:
             return len(self._shared_dictionary)

    def keys(self):
        with self._lock:
            return self._shared_dictionary.keys()

# ------------------------------------------------------------------------------
# Class job
# ------------------------------------------------------------------------------
class Job:
    """
    Job represents a unit of work that the ThreadPoolExecutor will execute. A job
    maintains all necessary attributes to allow the test case to execute on a
    z/OS managed node.

    Parameters
    ----------
    hostname : str
        Full hostname for the z/OS manage node the Ansible workload
        will be executed on.
    nodes : str
        Node object that represents a z/OS managed node and all its
        attributes.
    testcase: str
        The USS absolute path to a testcase using '/path/to/test_suite.py::test_case'
    id: int
        The id that will be assigned to this job, a unique identifier. The id will
        be used as the key in a dictionary.
    """
    def __init__(self, hostname: str, nodes: Dictionary, testcase: str, id: int):
        """
        Parameters
        ----------
        hostname : str
            Full hostname for the z/OS manage node the Ansible workload
            will be executed on.
        nodes : str
            Node object that represents a z/OS managed node and all its
            attributes.
        testcase: str
            The USS absolute path to a testcase using '/path/to/test_suite.py::test_case'
        id: int
            The id that will be assigned to this job, a unique identifier. The id will
            be used as the key in a dictionary.

        TODO:
        - Consider instead of tracking failures as an integer, instead use a list and insert
          the host (node) it failed on for statistical purposes.
        """
        self._hostnames: list = list()
        self._hostnames.append(hostname)
        self.testcase: str = testcase
        self.capture: str = None
        self.failures: int = 0
        self.id: int = id
        self.rc: int = -1
        self.successful: bool = False
        self.elapsed: str = None
        self.hostpattern: str = "all"
        self.nodes: Dictionary = nodes
        self._stdout_and_stderr: list[Tuple[str, str, str]] = []
        self._stdout: list[Tuple[str, str, str]] = []
        self.verbose: str = None

    def __str__(self) -> str:
        temp = {
            "hostname": self.get_hostname(),
            "testcase": self.testcase,
            "capture": self.capture,
            "failures": self.failures,
            "id": self.id,
            "rc": self.rc,
            "successful": self.successful,
            "elapsed": self.elapsed,
            "pytest-command": self.get_command()
        }

        return str(temp)

    def get_command(self) -> str:
        """
        Returns a command designed to run with the projects pytest fixture. The command
        is created specifically based on the ags defined, such as ZOAU or test cases to run.

        Example
        -------
        str
            pytest tests/functional/modules/test_zos_operator_func.py --host-pattern=all --zinventory-raw='{"host": "some.host.at.ibm.com", "user": "ibmuser", "zoau": "/zoau/v1.3.1", "pyz": "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"}'

        """
        node_temp = self.nodes.get(self.get_hostname())
        node_inventory = node_temp.get_inventory_as_string()
        return f"pytest {self.testcase} --host-pattern={self.hostpattern}{self.capture if not None else ""}{self.verbose if not None else ""} --zinventory-raw='{node_inventory}'"


    def get_hostnames(self) -> list[str]:
        """
        Return all hostnames that have been assigned to this job over time as a list.
        Includes hostnames that later replaced with new hostnames because the host is
        considered no longer functioning.

        Return
        ------
        list[str]
            A list of all hosts.
        """
        return self._hostnames

    def get_hostname(self) -> str:
        """
        Return the current hostname assigned to this node, in other words, the active hostname.

        Return
        ------
        str
            The current hostname assigned to this job.
        """
        return self._hostnames[-1]

    def get_testcase(self) -> str:
        """
        Return a pytest parametrized testcase that is assigned to this job.
        Incudes absolute path, testcase, and parametrization, eg <path/test.py::test[parameter]>

        Return
        ------
        str
            Returns absolute path, testcase, and parametrization, eg <path/test.py::test[parameter]>
        """
        return self.testcase

    def get_failure_count(self) -> int:
        """
        Return the number of failed job executions that have occurred for this job.
        Failures can be a result of the z/OS managed node, a bug in the test case or even a
        connection issue. This is used for statistical purposes or reason to assign the test
        to a new hostname.

        Return
        ------
        int
            Number representing number of failed executions.
        """
        return self.failures

    def get_rc(self) -> int:
        """
        Get the return code for the jobs execution.

        Return
        ------
        int
            Return code 0 All tests were collected and passed successfully (pytest)
            Return code 1 Tests were collected and run but some of the tests failed (pytest)
            Return code 2 Test execution was interrupted by the user (pytest)
            Return code 3 Internal error happened while executing tests (pytest)
            Return code 4 pytest command line usage error (pytest)
            Return code 5 No tests were collected (pytest)
            Return code 6 No z/OS nodes available.
            Return code 7 Re-balancing of z/OS nodes were performed
            Return code 8 Job has exceeded permitted job failures
            Return code 9 Job has exceeded timeout
        """
        return self.rc

    def get_id(self) -> int:
        """
        Returns the job id used as the key in the dictionary to identify the job.

        Return
        ------
        int
            Id of the job
        """
        return self.id

    def get_successful(self) -> bool:
        """
        Returns True if the job has completed execution.

        Return
        ------
        bool
            True if the job completed, otherwise False.

        See Also
        --------
        get_rc
            Returns 0 for success, otherwise non-zero.
        """
        return self.successful

    def get_elapsed_time(self) -> str:
        """
        Returns the elapsed time for this job, in other words,
        how long it took this job to run.

        Return
        ------
        str
            Time formatted as <HH:MM:SS.ss> , eg 00:05:30.64
        """
        return self.elapsed

    def get_nodes(self) -> Dictionary:
        """
        Returns a dictionary of all the z/OS managed nodes available.
        z/OS managed nodes are passed to a job so that a job can
        interact with the nodes configuration, for example,
        if a job needs to mark the node as offline, it can easily
        access the dictionary of z/OS managed nodes to do so.

        Return
        ------
        Dictionary[str, node]
            Thread safe Dictionary of z/OS managed nodes.
        """
        return self.nodes

    def get_stdout_and_stderr_msgs(self) -> list[Tuple[str, str, str]]:
        """
        Return all stdout and stderr messages that have been assigned to this job over time as a list.

        Return
        ------
        list[str]
            A list of all stderr and stdout messages.
        """
        return self._stdout_and_stderr

    def get_stdout_msgs(self) -> list[Tuple[str, str, str]]:
        """
        Return all stdout messages that have been assigned to this job over time as a list.

        Return
        ------
        list[str]
            A list of all stderr and stdout messages.
        """
        return self._stdout

    def get_stdout_and_stderr_msg(self) -> Tuple[str, str, str]:
        """
        Return the current stdout and stderr message assigned to this node, in other words, the last message
        resulting from this jobs execution.

        Return
        ------
        str
            The current concatenated stderr and stdout message.
        """
        return self._stdout_and_stderr[-1]

    def get_stdout_msg(self) -> Tuple[str, str, str]:
        """
        Return the current stdout message assigned to this node, in other words, the last message
        resulting from this jobs execution.

        Return
        ------
        str
            The current concatenated stderr and stdout message.
        """
        return self._stdout[-1]

    def set_rc(self, rc: int) -> None:
        """
        Set the jobs return code obtained from execution.

        Parameters
        ----------
        rc : int
            Value that is returned from the jobs execution
        """
        self.rc = rc

    def set_success(self) -> None:
        """
        Mark the job as having completed successfully.

        Parameters
        ----------
        completed : bool
            True if the job has successfully returned with a RC 0,
            otherwise False.
        """
        self.successful = True

    def add_hostname(self, hostname: str) -> None:
        """
        Set the hostname of where the job will be run.

        Parameters
        ----------
        hostname : str
            Hostname of the z/OS managed node.
        """
        self._hostnames.append(hostname)

    def increment_failure(self) -> None:
        """
        Increment the failure by 1 for this jobs. Each time the job
        returns with a non-zero return code, increment the value
        so this statistic can be reused in other logic.
        """
        self.failures +=1

    def set_elapsed_time(self, start_time: time) -> None:
        """
        Set the start time to obtain the elapsed time this
        job took to run. Should only set this when RC is zero.

        Parameters
        ----------
        start_time : time
            The time the job started. A start time should be
            captured before the job is run, and passed to this
            function after the job completes for accuracy of
            elapsed time.
        """
        self.elapsed = elapsed_time(start_time)

    def set_capture(self, capture: bool) -> None:
        """
        Indicate if pytest should run with '-s', which will
        show output and not to capture any output. Pytest
        captures all output sent to stdout and stderr,
        so you won't see the printed output in the console
        when running tests unless a test fails.
        """
        if capture is True:
            self.capture = " -s"

    def set_verbose(self, verbosity: int) -> None:
        """
        Indicate if pytest should run with verbosity to show
        detailed console outputs and debug failing tests.
        Verbosity is defined by the number of v's passed
        to py test.

        If verbosity is outside of the numerical range, no
        verbosity is set.

        Parameters
        ----------
        int
            - Integer range 1 - 4
            - 1 = -v
            - 2 = -vv
            - 3 = -vvv
            - 4 = -vvvv
        """
        if verbosity == 1:
            self.verbose = " -v"
        elif verbosity == 2:
            self.verbose = " -vv"
        elif verbosity == 3:
            self.verbose = " -vvv"
        elif verbosity == 4:
            self.verbose = " -vvvv"

    def set_stdout_and_stderr(self, message: str, std_out_err: str, date_time: str) -> None:
        """
        Add a stdout and stderr concatenated message resulting from the jobs
        execution (generally std out/err resulting from pytest) the job.

        Parameters
        ----------
        stdout_stderr : str
            Stdout and stderr concatenated into one string.
        """
        Joblog = namedtuple('Joblog',['id', 'hostname', 'command', 'message', 'std_out_err', 'date_time'])

        joblog = Joblog(self.id, self._hostnames[-1], self.get_command(), message, std_out_err, date_time)
        self._stdout_and_stderr.append(joblog)

    def set_stdout(self, message: str, std_out_err: str, date_time: str) -> None:
        """
        Add a stdout concatenated message resulting from the jobs
        execution (generally std out/err resulting from pytest) the job.

        Parameters
        ----------
        stdout_stderr : str
            Stdout and stderr concatenated into one string.
        """
        Joblog = namedtuple('Joblog',['id', 'hostname', 'command', 'message', 'std_out_err', 'date_time'])

        joblog = Joblog(self.id, self._hostnames[-1], self.get_command(), message, std_out_err, date_time)
        self._stdout.append(joblog)

# ------------------------------------------------------------------------------
# Class Node
# ------------------------------------------------------------------------------


class Node:
    """
    A z/OS node suitable for Ansible tests to execute. Attributes such as 'host',
    'zoau', 'user' and 'pyz' are maintained in this object because these attributes
    can be in different locations on the various z/OS nodes.

    A node instance will also generate a dictionary for use with pytest fixture
    'zinventory-raw'.

    This node will also track the health of the node, whether its status.ONLINE
    meaning its discoverable and useable or status.OFFLINE meaning over time,
    since being status.ONLINE, it has been determined unusable and thus marked
    as status.OFFLINE.


    Parameters
    ----------
    hostname : str
        Full hostname for the z/OS manage node the Ansible workload
        will be executed on.
    user : str
        The USS user name who will run the Ansible workload on z/OS.
    zoau: str
        The USS absolute path to where ZOAU is installed.
    pyz: str
        The USS absolute path to where python is installed.
    """

    def __init__(self, hostname: str, user: str, zoau: str, pyz: str):
        """

        Parameters
        ----------
        hostname : str
            Full hostname for the z/OS manage node the Ansible workload
            will be executed on.
        user : str
            The USS user name who will run the Ansible workload on z/OS.
        zoau: str
            The USS absolute path to where ZOAU is installed.
        pyz: str
            The USS absolute path to where python is installed.

        """
        self.hostname: str = hostname
        self.user: str = user
        self.zoau: str = zoau
        self.pyz: str = pyz
        self.state: Status = Status.ONLINE
        self.failures: set[int] = set()
        self.balanced: set[int] = set()
        self.inventory: dict [str, str] = {}
        self.inventory.update({'host': hostname})
        self.inventory.update({'user': user})
        self.inventory.update({'zoau': zoau})
        self.inventory.update({'pyz': pyz})
        self.assigned: Dictionary[int, Job] = Dictionary()
        self.failure_count: int = 0
        self.assigned_count: int = 0
        self.balanced_count: int = 0

    def __str__(self) -> str:
        """
        String representation of the Node class. Not every class
        variable is returned, some of the dictionaries which track
        state are large and should be accessed directly from those
        class members.
        """
        temp = {
            "hostname": self.hostname,
            "user": self.user,
            "zoau": self.zoau,
            "pyz": self.pyz,
            "state": str(self.state),
            "inventory": self.get_inventory_as_string(),
            "failure_count": str(self.failure_count),
            "assigned_count": str(self.assigned_count)
        }
        return str(temp)

    def set_state(self, state: Status):
        """
        Set status of the node, is the z/OS
        node ONLINE (useable) or OFFLINE (not usable)

        Parameters
        ----------
        state : Status
            Set state to Status.ONLINE if the  z/OS
            managed nodes state is usable, otherwise
            set it to Status.OFFLINE.
        """
        self.state = state

    def set_failure_job_id(self, id: int) -> None:
        """
        Add a job ID to the set maintaining jobs that have failed executing on this Node.
        This is used for statistical purposes.
        A Job failure occurs when the execution of the job is a non-zero return code.
        """
        self.failures.add(id)
        self.failure_count = len(self.failures)

    def set_assigned_job(self, job: Job) -> None:
        """
        Add a job to the Node that has been assigned to this node (z/OS managed node).
        This is used for statistical purposes.
        """
        self.assigned.add(job.get_id(),job)
        self.assigned_count +=1

    def set_balanced_job_id(self, id: int) -> None:
        """
        Add a job ID to the set maintaining jobs that have been rebalanced on this Node.
        This is used for statistical purposes.
        A Job failure occurs when the execution of the job is a non-zero return code.
        """
        self.balanced.add(id)

    def get_state(self) -> Status:
        """
        Get the z/OS manage node status.

        Returns
        -------
        Status.ONLINE
            If the  z/OS managed node state is usable.
        Status.OFFLINE
            If the z/OS managed node state is unusable.
        """
        return self.state

    def get_hostname(self) -> str:
        """
        Get the hostname for this z/OS managed node. A node is a
        z/OS endpoint capable of running an Ansible unit of work.

        Returns
        -------
        Str
            The z/OS managed node hostname.
        """
        return self.hostname

    def get_user(self) -> str:
        """
        Get the user ID permitted to run an Ansible workload on
        the z/OS managed node.

        Return
        ------
        Str
            USS users name
        """
        return self.user

    def get_zoau(self) -> str:
        """
        Get the ZOAU home directory on the z/OS managed node.

        Return
        ------
        str
            A USS path indicating where ZOAU is installed.
        """
        return self.zoau

    def get_pyz(self) -> str:
        """
        Get the python home directory on the z/OS managed node.

        Return
        ------
        str
            A USS path indicating where python is installed.
        """
        return self.pyz

    def get_inventory_as_string(self) -> str:
        """
        Get a JSON string that can be used with the 'zinventory-raw'
        pytest fixture. This JSON string can be passed directly
        to the option 'zinventory-raw', for example:

        pytest .... --zinventory-raw='{.....}'

        Return
        ------
        str
            A JSON string of necessary z/OS managed node attributes.
        """
        return json.dumps(self.inventory)

    def get_inventory_as_dict(self) -> dict [str, str]:
        """
        Get a dict() that can be used with the 'zinventory-raw'
        pytest fixture. This is the dict() so that it can be updated.
        To use it with the 'zinventory-raw', the dict() would have to
        be converted to a string with json.dumps(...) or equivalent.

        Return
        ------
        dict [str, str]
            A dict() of necessary z/OS managed node attributes.
        """
        return self.inventory

    def get_failure_jobs_as_dictionary(self) -> Dictionary:
        """
        Get a Dictionary() of all jobs which have failed on this node.

        Return
        ------
        Dictionary[int, Job]
            A Dictionary() of all Job(s) that have
            been assigned and failed on this Node.
        """
        return self.failures

    def get_assigned_jobs_as_string(self) -> str:
        """
        Get a JSON string of all jobs which have been assigned to this node.

        Return
        ------
        str
            A JSON string representation of a Job (a unit of work)
        """
        return json.dumps(self.assigned)

    def get_assigned_jobs_as_dictionary(self) -> Dictionary:
        """
        Get a Dictionary() of all jobs which have been assigned to this node.

        Return
        ------
        Dictionary[int, Job]
            A Dictionary() of all jobs which have failed on this node.
        """
        return self.assigned

    def get_failure_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have failed on this
        Node with a non-zero return code.
        """
        return self.failure_count

    def get_assigned_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have been assigned
        to this Node.
        """
        return self.assigned_count

    def get_balanced_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have been assigned
        to this Node.
        """
        self.balanced_count = len(self.balanced)
        return self.balanced_count

# def set_nodes_offline(nodes: Dictionary, maxnode: int) -> None:
#     for key, value in nodes.items():
#         if value.get_balanced_count() > maxnode:
#             value.set_state(Status.OFFLINE)

def set_node_offline(node: Node, maxnode: int) -> None:
    if node.get_balanced_job_count() > maxnode:
            node.set_state(Status.OFFLINE)


# ------------------------------------------------------------------------------
# Class Connection
# ------------------------------------------------------------------------------
class Connection:
    """
    Connection class wrapping paramiko. The wrapper provides methods allowing
    for remote environment variables be set up so that they can interact with
    ZOAU. Generally this is a wrapper to paramiko to be used to write files to
    z/OS. For example, consider writing a file that is managed by this load
    balancer that can know if there is another test running. The idea was to
    update our pytest fixture to look for that file so that a remote pipeline or
    other instance does not try to run concurrently until the functional tests
    can be properly vetted out for concurrent support.

    Usage:
        key_file_name = os.path.expanduser('~') + "/.ssh/id_dsa"
        connection = Connection(hostname="ibm.com", username="root", key_filename=key_file_name)
        client = connection.connect()
        result = connection.execute(client, "ls")
        print(result)
    """

    def __init__(self, hostname, username, password = None, key_filename = None,
                    passphrase = None, port=22, environment= None ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.passphrase = passphrase
        self.environment = environment
        self.env_str = ""
        if self.environment is not None:
            self.env_str = self.set_environment_variable(**self.environment)


    def __to_dict(self) -> str:
        """
        Method returns constructor arguments to a dictionary, must remain private to
        protect credentials.
        """
        temp =  {
            "hostname": self.hostname,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "key_filename": self.key_filename,
            "passphrase": self.passphrase,
        }

        for k,v  in dict(temp).items():
            if v is None:
                del temp[k]
        return temp

    def connect(self) -> SSHClient:
        """
        Create the connection after the connection class has been initialized.

        Return
        ------
        SSHClient
            paramiko SSHClient, client used the execution of commands.

        Raises
        ------
        BadHostKeyException
        AuthenticationException
        SSHException
        FileNotFoundError
        error
        """
        ssh = None

        n = 0
        while n <= 10:
            try:
                ssh = SSHClient()
                ssh.set_missing_host_key_policy(AutoAddPolicy())
                ssh.connect(**self.__to_dict(), disabled_algorithms=
                                {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                return ssh
            except BadHostKeyException as e:
                print(e)
                raise BadHostKeyException('Host key could not be verified.') # parentheses?
            except AuthenticationException as e:
                print(e)
                raise AuthenticationException('Authentication failed.')
            except ssh_exception.SSHException as e:
                print(e)
                raise ssh_exception.SSHException('SSH Error.')
            except FileNotFoundError as e:
                print(e)
                raise FileNotFoundError('Missing key filename.')
            except error as e:
                print(e)
                raise error('Socket error occurred while connecting.')

        raise Exception

    def execute(self, client, command):
        """
        Parameters
        ----------
        client : object, paramiko SSHClient
            SSH Client created through connection.connect()
        command: str, command to run

        Returns
        dict
            a dictionary with stdout, stderr and command executed

        Raises
        SSHException
        """

        response = None
        get_pty_bool = True
        out = ""
        error = ""
        try:
            # We may need to create a channel and make this synchronous
            # but get_pty should help avoid having to do that
            (stdin, stdout, stderr) = client.exec_command(self.env_str+command, get_pty=get_pty_bool)

            if get_pty_bool is True:
                out = stdout.read().decode().strip('\r\n')
                error = stderr.read().decode().strip('\r\n')
            else:
                out = stdout.read().decode().strip('\n')
                error = stderr.read().decode().strip('\n')

            # Don't shutdown stdin, we are reusing this connection in the services instance
            # client.get_transport().open_session().shutdown_write()

            response = {'stdout': out,
                        'stderr': error,
                        'command': command
            }

        except SSHException as e:
            # if there was any other error connecting or establishing an SSH session
            print(e)
        finally:
            client.close()

        return response

    def set_environment_variable(self, **kwargs):
        """
        Provide the connection with environment variables needed to be exported
        such as ZOAU env vars.

        Example:
            env={"_BPXK_AUTOCVT":"ON",
                "ZOAU_HOME":"/zoau/v1.2.0f",
                "PATH":"/zoau/v1.2.0f/bin:/python/usr/lpp/IBM/cyp/v3r8/pyz/bin:/bin:.",
                "LIBPATH":"/zoau/v1.2.0f/lib:/lib:/usr/lib:.",
                "PYTHONPATH":"/zoau/v1.2.0f/lib",
                "_CEE_RUNOPTS":"FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)",
                "_TAG_REDIR_ERR":"txt",
                "_TAG_REDIR_IN":"txt",
                "_TAG_REDIR_OUT":"txt",
                "LANG":"C"
            }
        connection = Connection(hostname="ibm.com", username="root",
                        key_filename=key_filename, environment=env)

        """
        env_vars = ""
        export="export"
        if kwargs is not None:
            for key, value in kwargs.items():
                env_vars = f"{env_vars}{export} {key}=\"{value}\";"
        return env_vars


# ------------------------------------------------------------------------------
# Helper methods
# ------------------------------------------------------------------------------


# def get_jobs(nodes: Dictionary, testsuite: str, tests: str, skip: str, capture: bool, verbosity: int, parametrized_test_cases = None) -> Dictionary:
def get_jobs(nodes: Dictionary, testsuite: str, tests: str, skip: str, capture: bool, verbosity: int, replay: bool = False) -> Dictionary:
    """
    Get a thread safe dictionary of job(s).
    A job represents a test case, a unit of work the ThreadPoolExecutor will run.
    A job manages the state of a test case as well as the necessary information
    to run on a z/OS managed node.

    Parameters
    ----------
    nodes : dictionary [ str, node]
        Thread safe dictionary z/OS managed nodes.
    testsuite : str
        Absolute path of testcase suites, comma or space delimited. A testsuite
        is a collection of test cases in a file that starts with 'test' and
        ends in '.py'.
        Option testsuite is mutually exclusive with both 'tests' and 'skip'.
    tests : str
        Absolute path to directories containing test suites, both functional
        and unit tests.
    skip : str
        Absolute path of testcase suites to skip, comma or space delimited.
        A testsuite is a collection of test cases in a file that starts
        with 'test' and ends in '.py'. Specifying skip will result in test
        cases not being included in the results, ensuring they are not
        executed by the ThreadPoolExecutor.
        This option (skip) is only used when option tests is defined.

    Returns
    -------
    Dictionary [int, Job]
        A thread safe Dictionary containing numeric keys (ID) with value
        type Job, each Dictionary item is a testcase with supporting
        attributes necessary to execute on a z/OS managed node.

    Raises
    ------
    RuntimeError : When no z/OS managed hosts were online.

    Note
    ----
    Option 'testsuite'
        Is mutually exclusive with both 'tests' and 'skip'. If you
        use 'skip' with testsuite' it will be ignored.
    """

    hostnames=list(nodes.keys())
    hostnames_length = nodes.len()
    parametrized_test_cases = []
    if hostnames_length == 0:
        raise RuntimeError('No z/OS managed hosts were online, please check host availability.')

    # List to contain absolute paths to comma/space delimited test suites or directories.
    files =[]

    # If testsuite, test suites were provided, else tests (directories) were passed.
    # Remove whitespace and replace CSV with single space delimiter.
    # Build a command that will yield all test cases included parametrized tests.
    cmd = ['pytest', '--collect-only', '-q']
    if testsuite:
        # print("testsuite is " + testsuite)
        files = " ".join(testsuite.split())
        files = testsuite.strip().replace(',', ' ').split()
        cmd.extend(files)
    else:
        tests=" ".join(tests.split())
        files = tests.strip().replace(',', ' ').split()
        cmd.extend(files)
        # TODO: Check if directories exist

        if skip:
            skip=" ".join(skip.split())
            skip = skip.strip().replace(',', ' ').split()
            cmd.extend(['--ignore'])
            cmd.extend(skip)
            # TODO: Check if directories exist

    cmd.extend(['| grep ::'])
    cmd_str = ' '.join(cmd)

    #print("CMD STRING " + cmd_str)
    # if parametrized_test_cases is None:
    #     # Run the pytest collect-only command and grep on :: so to avoid warnings
    #     parametrized_test_cases = subprocess.run([cmd_str], shell=True, capture_output=True, text=True)
    #     parametrized_test_cases = parametrized_test_cases.stdout.split()

    if replay:
        for f in files:
            parametrized_test_cases.append(f.replace('tests/','',1))
    else:
        # Run the pytest collect-only command and grep on :: so to avoid warnings
        parametrized_test_cases = subprocess.run([cmd_str], shell=True, capture_output=True, text=True)
        parametrized_test_cases = parametrized_test_cases.stdout.split()
        parametrized_test_cases_count = len(parametrized_test_cases)

    # Thread safe dictionary of Jobs
    jobs = Dictionary()
    index = 0
    hostnames_index = 0

    for parametrized_test_case in parametrized_test_cases:

        # Assign each job a hostname using round robin (modulus % division)
        if hostnames_index % hostnames_length == 0:
            hostnames_index = 0

        # Create a job, add it jobs Dictionary, update node reference
        hostname = hostnames[hostnames_index]
        _job = Job(hostname = hostname, nodes = nodes, testcase="tests/"+parametrized_test_case, id=index)
        _job.set_verbose(verbosity)
        _job.set_capture(capture)
        jobs.update(index, _job)
        nodes.get(hostname).set_assigned_job(_job)
        index += 1
        hostnames_index += 1

    # for key, value in jobs.items():
    #     print(f"The job count = {str(jobs.len())}, job id = {str(key)} , job = {str(value)}")

    return jobs


def update_job_hostname(job: Job):
    """
    Updates the job with a new hostname. Jobs rely on healthy hostnames and when
    its determine that the z/OS hostname that is being accessed has become
    incapable of addressing any unit of work, this method will append a new
    z/os hostname for the job to execute its job on. This method ensures
    that it is a randomly different node then the one previously assigned
    to the job.

    This is referred to as re-balancing a jobs hostname, this happens when
    a job has consistently failed N number of times.

    TODO:
    - Iterate over all jobs looking for inactive ones and balance all of the
      job nodes. - after giving this some thou
    """

    unsorted_items = dict()
    nodes = job.get_nodes()

    # We need the Jobs assigned host names (job.get_hostnames() -> list[str])
    set_of_nodes_assigned_to_job: set = set(job.get_hostnames())

    set_of_nodes_online: set = set()
    for key, value in job.get_nodes().items():
        if value.get_state().is_online():
            set_of_nodes_online.add(key)

    # The difference of all available z/OS zos_nodes and ones assigned to a job.
    nodes_available_and_online = list(set_of_nodes_online - set_of_nodes_assigned_to_job)

    for hostname in nodes_available_and_online:
        count = nodes.get(hostname).get_assigned_job_count()
        unsorted_items[hostname] = count

    sorted_items_by_assigned = OrderedDict(sorted(unsorted_items.items(), key=lambda x: x[1]))
    # for key, value in sorted_items_by_assigned.items():
    #     print(f" Sorted by assigned are; key = {key}, value = {value}.")

    # After being sorted ascending, assign the first index which will have been the lease used connection. 
    if len(sorted_items_by_assigned) > 0:
        job.add_hostname(list(sorted_items_by_assigned)[0])


def get_nodes(user: str, zoau: str, pyz: str, hostnames: list[str] = None) -> Dictionary:
    """
    Get a thread safe Dictionary of active z/OS managed nodes.

    Parameters
    ----------
    user : str
        The USS user name who will run the Ansible workload on z/OS.
    zoau: str
        The USS absolute path to where ZOAU is installed.
    pyz: str
        The USS absolute path to where python is installed.

    Returns
    -------
    Dictionary [str, Node]
        Thread safe Dictionary containing all the active z/OS managed nodes.
        The dictionary key will be the z/OS managed node's hostname and the value
        will be of type Node.
    """
    nodes: Dictionary [str, Node] = Dictionary()

    if hostnames is None:
        hostnames = []

        # Calling venv.sh directly to avoid the ac dependency, ac usually lives in project root so an
        # additional arg would have to be passed like so: "cd ..;./ac --host-nodes --all false"
        result = subprocess.run(["echo `./venv.sh --targets-production`"], shell=True, capture_output=True, text=True)
        hostnames = result.stdout.split()
    else:
        hostnames = hostnames[0].split(',')

    # Prune any production system that fails to ping
    for hostname in hostnames:
        command = ['ping', '-c', '1', hostname]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # TODO: Use the connection class to connection and validate ZOAU and Python before adding the nodes
        if result.returncode == 0:
            node=Node(hostname = hostname, user = user, zoau = zoau, pyz = pyz)
            node.set_state(Status.ONLINE)
            nodes.update(key = hostname, obj = node)

    # for key, value in nodes.items():
    #     print(f"The z/OS node count = {str(nodes.len())}, hostname = {key} , node = {str(value)}")

    return nodes

def get_nodes_online_count(nodes: Dictionary) -> int:
    """
    Get a count of how many managed Node(s) have status that is equal to Status.ONLINE.
    A value greater than or equal to 1 signifies that Job(s) can continue to execute,
    otherwise there are no managed nodes capable or running a job.

    A Node is set to Status.OFFLINE when the value used for --bal (balance) is
    surpassed. Balance (--bal) is used to signal that Job has run N number of times
    on a particular host and had a non-zero return code and should be used by any other Job.

    Parameters
    ----------
    nodes : dictionary [ str, node]
        Thread safe dictionary z/OS managed nodes.

    Returns
    -------
    int
        The numerical count of nodes that are online.
    """
    nodes_online_count = 0
    for key, value in nodes.items():
        if value.get_state().is_online():
            nodes_online_count += 1

    return nodes_online_count

def get_nodes_offline_count(nodes: Dictionary) -> int:
    """
    Get a count of how many managed Node(s) have status that is equal to Status.OFFLINE.
    A value greater than or equal to 1 signifies that Job(s) have failed to run on this
    node and that this node should not be used any further.

    A Node is set to Status.OFFLINE when the value used for --bal (balance) is
    surpassed. Balance (--bal) is used to signal that Job has run N number of times
    on a particular host and had a non-zero return code and should be used by any other Job.

    Parameters
    ----------
    nodes : dictionary [ str, node]
        Thread safe dictionary z/OS managed nodes.

    Returns
    -------
    int
        The numerical count of nodes that are offline.
    """
    nodes_offline_count = 0
    for key, value in nodes.items():
        if not value.get_state().is_online():
            nodes_offline_count += 1

    return nodes_offline_count


def get_jobs_statistics(jobs: Dictionary, maxjob: int) -> Tuple[int, int, list[str], int, list[str]]:
    """
    The get_jobs_statistics function is used to calculate statistics about the jobs that
    have been run. It takes in a dictionary of jobs and returns a tuple containing
    various statistics about the jobs.

    Parameters
    ----------
    jobs: Dictionary [int, job].

    Returns
    -------
    Tuple[int, int, list[str], int, list[str]]
        A tuple containing the following statistics about the jobs:
        - jobs_total_count: The total number of jobs collected, count includes both
          success and failures.
        - jobs_success_count: The number of jobs that have successfully executed.
        - jobs_success_tests: A list of testcases that succeeded.
        - jobs_failed_count: The number jobs that did not succeed and resulted in
          having never successfully executed.
        - jobs_failed_tests: A list of testcases that failed.

    Raises
    ------
    TypeError:
        - If the input argument jobs is not a dictionary
        - If any of the values in the jobs dictionary are not instances of the Job class
    """
    jobs_success_count = 0
    jobs_success_tests = []
    jobs_failed_count = 0
    jobs_failed_tests = []
    jobs_total_count = 0
    jobs_success_log = []
    jobs_failed_log = []
    jobs_rebalanced_count = 0
    jobs_failed_count_maxjob = 0
    jobs_failed_maxjob_tests =[]
    jobs_failed_maxjob_log = []

    for key, value in jobs.items():
        # Total count of jobs (same as len(jobs))
        jobs_total_count +=1

        # Total of jobs that have been rebalanced
        if len(value.get_hostnames()) > 1:
            jobs_rebalanced_count  +=1

        # Total of jobs have a successful status
        if value.get_successful():
            jobs_success_count += 1
            jobs_success_tests.append(value.get_testcase())
            jobs_success_log.extend(value.get_stdout_msgs())
        else:
            # Total of jobs that have a failure status
            if not value.get_successful():
                jobs_failed_count += 1
                jobs_failed_tests.append(value.get_testcase())
                jobs_failed_log.extend(value.get_stdout_and_stderr_msgs())
            # Total of jobs that have failure status and exceeded maxjob, this
            # differs from the total of that have a failure status in that maxjob
            # has exceeded, while a job can fail and never exceed maxjob because
            # there are no healthy z/OS managed nodes to execute on.
            if value.get_failure_count() >= maxjob:
                jobs_failed_count_maxjob += 1
                jobs_failed_maxjob_tests.append(value.get_testcase())
                jobs_failed_maxjob_log.extend(value.get_stdout_and_stderr_msgs())

    # TODO: the jobs_success_log is not used/populated, decide what to do with it. 
    Statistics = namedtuple('Statistics',
                            ['jobs_total_count',
                             'jobs_success_count',
                             'jobs_success_tests',
                             'jobs_success_log',
                             'jobs_failed_count',
                             'jobs_failed_tests',
                             'jobs_failed_log',
                             'jobs_rebalanced_count',
                             'jobs_failed_count_maxjob',
                             'jobs_failed_maxjob_tests',
                             'jobs_failed_maxjob_log'])
    result = Statistics(jobs_total_count,
                        jobs_success_count,
                        jobs_success_tests,
                        jobs_success_log,
                        jobs_failed_count,
                        jobs_failed_tests,
                        jobs_failed_log,
                        jobs_rebalanced_count,
                        jobs_failed_count_maxjob,
                        jobs_failed_maxjob_tests,
                        jobs_failed_maxjob_log)

    return result

def get_failed_count_gt_maxjob(jobs: Dictionary, maxjob: int) -> Tuple[int, list[str], dict[int, str], int]:
    jobs_failed_count = 0
    jobs_failed_list = []
    jobs_failed_log = []
    jobs_rebalanced = 0
    for key, value in jobs.items():
        if value.get_failure_count() >= maxjob:
            jobs_failed_count += 1
            jobs_failed_list.append(value.get_testcase())
            jobs_failed_log.append({key : value.get_stdout_and_stderr_msgs()})
        if len(value.get_hostnames()) > 1:
            jobs_rebalanced  +=1
    #TODO: refactor these tuples to include gt or max to not confused with get jobs statistics
    return (jobs_failed_count, jobs_failed_list, jobs_failed_log, jobs_rebalanced)

def run(id: int, jobs: Dictionary, nodes: Dictionary, timeout: int, maxjob: int, bal: int, extra: str, maxnode: int) -> Tuple[int, str]:
    """
    Runs a job (test case) on a z/OS managed node and ensures the job has the necessary
    managed node available. If not, it will manage the node and collect the statistics
    so that it can be properly run when a resource becomes available.

    Parameters
    ----------
    id : int
        Numerical ID assigned to a job.
    jobs: Dictionary
        A dictionary of jobs, the ID is paired to a job.
        A job is a test cased designed to be run by pytest.
    nodes: Dictionary
        Managed nodes that jobs will run on. These are z/OS
        managed nodes.
    timeout: int
        The maximum time in seconds a job should run on z/OS for,
        default is 300 seconds.
    maxjob: int
        The maximum number of times a job can fail before its
        disabled in the job queue
    bal: int
        The count at which a job is balanced from one z/OS node
        to another for execution.
    extra: str
        Extra commands passed to subprocess before pytest execution
    maxnode: int
        The maximum number of times a node can fail to run a
        job before its set to 'offline' in the node queue.

    Returns
    -------
    A tuple of (rc: int, message: str) is returned.

    rc: int
        - Return code 0 All tests were collected and passed successfully (pytest).
        - Return code 1 Tests were collected and run but some of the tests failed (pytest).
        - Return code 2 Test execution was interrupted by the user (pytest).
        - Return code 3 Internal error happened while executing tests (pytest).
        - Return code 4 pytest command line usage error (pytest).
        - Return code 5 No tests were collected (pytest).
        - Return code 6 No z/OS nodes available.
        - Return code 7 Re-balancing of z/OS nodes were performed.
        - Return code 8 Job has exceeded permitted job failures.
        - Return code 9 Job has exceeded timeout.
    message: str
        Description and details of the jobs execution, contains return code,
        hostname, job id, etc. Informational and useful when understanding
        the job's lifecycle.
    """

    job = jobs.get(id)
    hostname = job.get_hostname()
    id = str(job.get_id())
    elapsed = 0
    message = None
    rc = None
    result = None

    # node = nodes.get(host)
    node_count_online = get_nodes_online_count(nodes)
    if node_count_online >0:
        node = nodes.get(hostname)
        start_time = time.time()
        date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # print("Job information: " + "\n  z/OS hosts available = " + str(zos_nodes_len) + "\n  Job ID = " + str(job.get_id()) + "\n  Command = " + job.get_command())
        try:
            # Build command and strategically map stdout and stderr so that both are mapped to stderr and the pytest rc goes to stdout.
            cmd =  f"{extra};{job.get_command()} 1>&2; echo $? >&1"
            result = subprocess.run([cmd], shell=True, capture_output=True, text=True, timeout=timeout)
            job.set_elapsed_time(start_time)
            elapsed = job.get_elapsed_time()
            rc = int(result.stdout)

            if rc == 0:
                job.set_rc(int(rc))
                job.set_success()
                rc_msg = "Test collected and passed successfully."
                message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                pytest_std_out_err = result.stderr
                job.set_stdout(message, pytest_std_out_err, date_time)
            else:
                job_failures = job.get_failure_count()

                if job_failures >= maxjob:
                    rc = 8
                    job.set_rc(int(rc))
                    # Do node stuff
                    rc_msg = f"Test exceeded permitted failures = {maxjob}."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                elif job_failures == bal:
                    rc = 7
                    job.set_rc(int(rc))
                    node.set_balanced_job_id((id))
                    set_node_offline(node, maxnode)
                    update_job_hostname(job)
                    node.get_balanced_job_count()
                    rc_msg = f"Test has been assigned to a new z/OS managed node = {job.get_hostname()}, because it exceeded allowable balance = {bal}."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                elif rc == 1:
                    job.set_rc(int(rc))
                    rc_msg = "Test case was collected and failed with an error."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                elif rc == 2:
                    job.set_rc(int(rc))
                    rc_msg = "Test case execution was interrupted by the user."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                elif rc == 3:
                    job.set_rc(int(rc))
                    rc_msg = "Internal error occurred while executing test."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                elif rc == 4:
                    job.set_rc(int(rc))
                    rc_msg = "Pytest command line usage error."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"
                elif rc == 5:
                    job.set_rc(int(rc))
                    rc_msg = "No tests were collected ."
                    message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, msg = {rc_msg}"

                # Increment the job failure after evaluating all the RCs
                job.increment_failure()

                # Update the node with which jobs failed. A node has all assigned jobs so this ID can be used later for eval.
                node.set_failure_job_id(id)

                pytest_std_out_err = result.stderr
                job.set_stdout_and_stderr(message, pytest_std_out_err, date_time)

        except subprocess.TimeoutExpired as timeout_err:
            job.set_elapsed_time(start_time)
            elapsed = job.get_elapsed_time()
            rc = 9
            job.set_rc(int(rc))
            # pytest_std_out_err = timeout_err.stderr.decode()
            # pytest_std_out_err += timeout_err.stdout.decode()
            rc_msg = f"Job has exceeded subprocess timeout = {str(timeout)}"
            message = f"Job ID = {id}, host = {hostname}, start time = {date_time}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
            job.set_stdout_and_stderr(message, rc_msg, date_time)
            job.increment_failure()
            node.set_failure_job_id(id)
    else:
        rc = 6
        nodes_count = nodes.len()
        node_count_offline = get_nodes_offline_count(nodes)
        rc_msg = f"There are no z/OS managed nodes available to run jobs, node count = {nodes_count}, OFFLINE = {node_count_offline}, ONLINE = {node_count_online}."
        message = f"Job ID = {id}, host = {hostname}, elapsed time = {job.get_elapsed_time()}, rc = {str(rc)}, rc msg = {rc_msg}"
        job.set_stdout_and_stderr(message, rc_msg, date_time)
        job.increment_failure()
        node.set_failure_job_id(id)

    # print("STDERR/OUT = " + job.get_stdout_and_stderr_msg())
    # print("NODE IS " + str(node))
    # print(message)
    return rc, message


def runner(jobs: Dictionary, nodes: Dictionary, timeout: int, max: int, bal: int, extra: str, maxnode: int, workers: int) -> None:
    """
    Method creates an executor to run a job found in the jobs dictionary concurrently.
    This method is the key function that allows for concurrent execution of jobs.


    Parameters
    ----------
    jobs: Dictionary
        A dictionary of jobs, the ID is paired to a job.
        A job is a test cased designed to be run by pytest.
    nodes: Dictionary
        Managed nodes that jobs will run on. These are z/OS
        managed nodes.
    timeout: int
        The maximum time in seconds a job should run on z/OS for,
        default is 300 seconds.
    maxjob: int
        The maximum number of times a job can fail before its
        disabled in the job queue
    bal: int
        The count at which a job is balanced from one z/OS node
        to another for execution.
    extra: str
        Extra commands passed to subprocess before pytest execution
    maxnode: int
        The maximum number of times a node can fail to run a
        job before its set to 'offline' in the node queue.
    workers: int
        The numerical value used to increase the number of worker
        threads by proportionally. By default this is 3 that will
        yield one thread per node. With one thread per node, test
        cases run one at a time on a managed node. This value
        is used as a multiple to grow the number of threads and
        test concurrency. For example, if there are 5 nodes and
        the workers = 3, then 15 threads will be created
        resulting in 3 test cases running concurrently.

    """

    if workers > 1:
        number_of_threads = nodes.len() * workers
    else:
        number_of_threads = nodes.len()

    with ThreadPoolExecutor(number_of_threads) as executor:
        futures = [executor.submit(run, key, jobs, nodes, timeout, max, bal, extra, maxnode) for key, value in jobs.items() if not value.get_successful()]
        for future in as_completed(futures):
            rc, message = future.result()
            if future.exception() is not None:
                print(f"Thread pool exception occurred with error: {future.exception()}")
            elif future.cancelled():
                 print(f"Thread pool cancelled job with message: {message}")
            elif future.done():
                print(f"Thread pool completed job with message: {message}")
            elif future.running():
                print(f"Thread pool is still running job")

        # try:
        #     for future in as_completed(futures, timeout=200):
        #         rc, message = future.result()
        #         print("JOB RC is " + str(rc) + " with message " + message)
        # except concurrent.futures.TimeoutError:
        #         print("this took too long...")

def elapsed_time(start_time: time):
    """
    Given a start time, this will return a formatted string of time matching
    pattern HH:MM:SS.SS , eg 00:02:38.36

    Parameters
    ----------
    start_time: time
        The time the test case has began. This is generally captured
        before a test is run.

    Returns
    -------
    str
        The elapsed time, how long it took a job to run. A string
        is returned representing the elapsed time, , eg 00:02:38.36
    """

    hours, rem = divmod(time.time() - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    elapsed = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)
    return elapsed

def print_job_logs(log: list[Tuple[str, str, str]], state: State) -> None:
    if len(log) > 0:
        for entry in log:
            print("------------------------------------------------------------\n"\
                f"[START] [{state.string()}] log entry.\n"\
                "------------------------------------------------------------\n"\
                f"\tJob ID: {entry.id}\n"\
                f"\tHostname: {entry.hostname}\n"\
                f"\tDate time: {entry.date_time}\n"\
                f"\tCommand:  {entry.command}\n"\
                f"\tMessage:  {entry.message}\n"\
                f"\tStdout: \n\t{entry.std_out_err.replace('\n', '\n\t')}\n"\
                "------------------------------------------------------------\n"\
                f"[END] [{state.string()}] log entry.\n"\
                "------------------------------------------------------------")

def print_job_tests(tests: list[str], state: State) -> None:
    if len(tests) > 0:
        print("------------------------------------------------------------\n"\
            f"[START] [{state.string()}] test cases.\n"\
            "------------------------------------------------------------")
        for entry in tests:
            print(f"\t{entry}")
        print("------------------------------------------------------------\n"\
            f"[END] [{state.string()}] test cases.\n"\
            "------------------------------------------------------------")

def print_job_logs_to_html(log: list[Tuple[str, str, str]], state: State, replay: str) -> str:
    if len(log) > 0:
        table = PrettyTable()
        table.hrules=ALL
        table.format = False
        table.header = True
        table.left_padding_width = 1
        table.right_padding_width = 1
        table.field_names = ["Count", "Job ID", "z/OS Managed Node", "Pytest Command", "Message", "Standard Out & Error", "Date and Time"]
        table.align["Message"] = "l"
        table.align["Standard Out & Error"] = "l"
        table.sortby = "Job ID"

        count = 0
        for entry in log:
            table.add_row([count, entry.id,entry.hostname, entry.command, entry.message, entry.std_out_err, entry.date_time])
            count +=1

        html = table.get_html_string(attributes={'border': 1, "style":"white-space:nowrap;width:100%;border-collapse: collapse"})
        file = open(f"/tmp/{state.string()}-job-logs-replay-{replay}.html", "w")
        file.write(html)
        file.close()

def print_job_tests_to_html(tests: list[str], state: State, replay: str) -> None:
    if len(tests) > 0:
        table = PrettyTable()
        table.hrules=ALL
        table.format = False
        table.header = True
        table.left_padding_width = 1
        table.right_padding_width = 1
        table.field_names = ["Count", "Test Case"]
        table.align["Test Case"] = "l"
        table.sortby = "Count"

        count = 0
        for entry in tests:
            table.add_row([count, entry])
            count +=1

        html = table.get_html_string(attributes={'border': 1, "style":"white-space:nowrap;width:100%;border-collapse: collapse"})
        file = open(f"/tmp/{state.string()}-job-tests-replay-{replay}.html", "w")
        file.write(html)
        file.close()


def executor(args):
    count_play = 1
    tests=args.tests
    count = 1
    replay = False
    while count_play <= args.replay:
        print(f"\n=================================\nPLAY {count_play} has been initialized.\n=================================")

        start_time_full_run = time.time()

        # Get a dictionary of all active zos_nodes to run tests on
        nodes = get_nodes(user = args.user, zoau = args.zoau, pyz = args.pyz, hostnames = args.hostnames)

        # Get a dictionary of jobs containing the work to be run on a node.
        jobs = get_jobs(nodes, testsuite=args.testsuite, tests=tests, skip=args.skip, capture=args.capture, verbosity=args.verbosity, replay=replay)
        iterations_result=""
        number_of_threads = nodes.len() * args.workers

        stats = get_jobs_statistics(jobs, args.maxjob)
        job_count_progress = 0
        while stats.jobs_success_count != stats.jobs_total_count and count <= int(args.itr):
            start_time = time.time()
            runner(jobs, nodes, args.timeout, args.maxjob, args.bal, args.extra, args.maxnode, args.workers)
            stats = get_jobs_statistics(jobs, args.maxjob)
            iterations_result += f"\tThread pool iteration {count} completed {stats.jobs_success_count - job_count_progress} job(s) in {elapsed_time(start_time)} time, pending {stats.jobs_failed_count} job(s).\n"
            print(f"Thread pool iteration {str(count)} has pending {stats.jobs_failed_count} jobs.")
            count +=1
            job_count_progress = stats.jobs_success_count

        print("\n=================================\nRESULTS\n=================================")
        print(f"All {count - 1} thread pool iterations completed in {elapsed_time(start_time_full_run)} time, with {number_of_threads} threads running concurrently.")
        print(iterations_result)
        print("\n=================================\nSUMMARY\n=================================")
        print(f"\tNumber of jobs queued to be run = {stats.jobs_total_count}.")
        print(f"\tNumber of jobs that run successfully = {stats.jobs_success_count}.")
        print(f"\tTotal number of jobs that failed = {stats.jobs_failed_count}.")
        print(f"\tNumber of jobs that failed great than or equal to {str(args.maxjob)} times = {stats.jobs_failed_count_maxjob}.")
        print(f"\tNumber of jobs that failed less than {str(args.maxjob)} times = {stats.jobs_failed_count - stats.jobs_failed_count_maxjob}.")
        print(f"\tNumber of jobs that were balanced = {stats.jobs_rebalanced_count}.")

        # Print to stdout any failed test cases and their relevant pytest logs
        print_job_tests(stats.jobs_failed_tests, State.FAILURE)
        print_job_logs(stats.jobs_failed_log, State.FAILURE)
        print_job_tests_to_html(stats.jobs_failed_tests, State.FAILURE, count_play)
        print_job_logs_to_html(stats.jobs_failed_log, State.FAILURE, count_play)

        # Print to stdout any test cases that exceeded the value max number of times a job can fail.
        print_job_tests(stats.jobs_failed_maxjob_tests, State.EXCEEDED)
        print_job_logs(stats.jobs_failed_maxjob_log, State.EXCEEDED)
        print_job_tests_to_html(stats.jobs_failed_maxjob_tests, State.EXCEEDED, count_play)
        print_job_logs_to_html(stats.jobs_failed_maxjob_log, State.EXCEEDED, count_play)

        # Print to stdout all successful test cases and their relevant logs.
        print_job_tests(stats.jobs_success_tests, State.SUCCESS)
        print_job_logs(stats.jobs_success_log, State.SUCCESS)
        print_job_tests_to_html(stats.jobs_success_tests, State.SUCCESS, count_play)
        print_job_logs_to_html(stats.jobs_success_log, State.SUCCESS, count_play)

        # If replay is set, the retry this again with the test cases that failed
        if stats.jobs_failed_count > 0:
            tests = ','.join(stats.jobs_failed_tests)
            args.testsuite = None
            count_play +=1
            count = 1
            replay = True
        else:
            count_play = args.replay

def main():
    parser = argparse.ArgumentParser(
    prog='load_balance.py',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''
        Examples
        --------
        1)  Execute a single test suite for up to 5 iterations for ibmuser with shared zoau and python installations.
            Note, usage of --tests "../tests/functional/modules/test_zos_tso_command_func.py"
            $ python3 load_balance.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 5\\
                    --tests "../tests/functional/modules/test_zos_tso_command_func.py"\\
                    --user "ibmuser"\\
                    --timeout 100

        2)  Execute a multiple test suites for up to 10 iterations for ibmuser with shared zoau and python installations.
            Note, usage of --tests "../tests/functional/modules/test_zos_tso_command_func.py,../tests/functional/modules/test_zos_find_func.py"
            $ python3 load_balance.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 10\\
                    --tests "../tests/functional/modules/test_zos_tso_command_func.py,../tests/functional/modules/test_zos_find_func.py"\\
                    --user "ibmuser"\\
                    --timeout 100

        3)  Execute a test suites in a directory for up to 4 iterations for ibmuser with shared zoau and python installations.
            Note, usage of --directories "../tests/functional/modules/,../tests/unit/"
            $ python3 load_balance.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 4\\
                    --directories "../tests/functional/modules/,../tests/unit/"\\
                    --user "ibmuser"\\
                    --timeout 100

        4)  Execute test suites in multiple directories for up to 5 iterations for ibmuser with shared zoau and python installations.
            Note, usage of "--directories "../tests/functional/modules/,../tests/unit/"
            $ python3 load_balance.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 5\\
                    --directories "../tests/functional/modules/,../tests/unit/"\\
                    --user "ibmuser"\\
                    --timeout 100\\
                    --max 6\\
                    --bal 3

        5)  Execute test suites in multiple directories with up to 5 iterations for ibmuser with attributes, zoau, pyz using a max timeout of 100, max failures of 6 and balance of 3.
            Note, usage of "--directories "../tests/functional/modules/,../tests/unit/"
            $ python3 load_balance.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 5\\
                    --directories "../tests/functional/modules/,../tests/unit/"\\
                    --user "ibmuser"\\
                    --timeout 100\\
                    --maxjob 6\\
                    --bal 3\\
                    --maxnode 4\\
                    --hostnames "ec33025a.vmec.svl.ibm.com,ec33025a.vmec.svl.ibm"\\
                    --verbosity 3\\
                    --capture\\
                    --workers 3\\
                    --extra "cd .."
        '''))

    # Options
    parser.add_argument('--extra', type=str, help='Extra commands passed to subprocess before pytest execution', required=False, metavar='<str>', default="")
    parser.add_argument('--pyz', type=str, help='Python Z home directory.', required=True, metavar='<str,str>', default="")
    parser.add_argument('--zoau', type=str, help='ZOAU home directory.', required=True, metavar='<str,str>', default="")
    parser.add_argument('--itr', type=int, help='How many times to run the test suite, exists early if all succeed.', required=True, metavar='<int>', default="")
    parser.add_argument('--skip', type=str, help='Identify test suites to skip, only honored with option \'--directories\'', required=False, metavar='<str,str>', default="")
    parser.add_argument('--user', type=str, help='z/OS USS user authorized to run Ansible tests on the managed z/OS node', required=True, metavar='<str>', default="")
    parser.add_argument('--timeout', type=int, help='The maximum time in seconds a job should run on z/OS for, default is 300 seconds.', required=False, metavar='<int>', default="300")
    parser.add_argument('--maxjob', type=int, help='The maximum number of times a job can fail before its disabled in the job queue.', required=False, metavar='<int>', default="6")
    parser.add_argument('--bal', type=int, help='The count at which a job is balanced from one z/OS node to another for execution.', required=False, metavar='<int>', default="3")
    parser.add_argument('--hostnames', help='List of hostnames to use, overrides the auto detection.', required=False, metavar='<list[str]>', default=None, nargs='*')
    parser.add_argument('--maxnode', type=int, help='The maximum number of times a node can fail to run a job before its set to \'offline\' in the node queue.', required=False, metavar='<int>', default=6)
    parser.add_argument('--verbosity', type=int, help='The level of pytest verbosity, 1 = -v, 2 = -vv, 3 = -vvv, 4 = -vvvv.', required=False, metavar='<int>', default=0)
    parser.add_argument('--capture', action=argparse.BooleanOptionalAction, help='Instruct Pytest not to capture any output, equivalent of -s.', required=False, default=False)
    parser.add_argument('--workers', type=int, help='The numerical value used to increase the number of worker threads by proportionally.', required=False, metavar='<int>', default=1)
    parser.add_argument('--replay', type=int, help='The numerical value used to increase the number of worker threads by proportionally.', required=False, metavar='<int>', default=1)

    # Mutually exclusive options
    group_tests_or_dirs = parser.add_argument_group('Mutually exclusive', 'Absolute path to test suites. For more than one, use a comma or space delimiter.')
    exclusive_group_or_tests = group_tests_or_dirs.add_mutually_exclusive_group(required=True)
    exclusive_group_or_tests.add_argument('--testsuite', type=str, help='Space or comma delimited test suites, must be absolute path(s)', required=False, metavar='<str,str>', default="")
    exclusive_group_or_tests.add_argument('--tests', type=str, help='Space or comma delimited directories containing test suites, must be absolute path(s)', required=False, metavar='<str,str>', default=None)
    args = parser.parse_args()

    # Evaluate
    # TODO: Maxjob should always be less than itr else it makes no sense
    if int(args.maxjob) > int(args.itr):
        raise ValueError(f"Value '--maxjob' = {args.maxjob}, must be less than --itr = {args.itr}, else maxjob will have no effect.")

    if int(args.bal) > int(args.maxjob):
        raise ValueError(f"Value '--bal' = {args.bal}, must be less than --maxjob = {args.itr}, else balance will have no effect.")

    # Execute/begin running the concurrency testing with the provided args.
    executor(args)

if __name__ == '__main__':
    main()
