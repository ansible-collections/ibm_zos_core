import argparse
from enum import Enum
import itertools
import json
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
import concurrent.futures

from typing import Type


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
        - Consider removing completed because the return code can provide the same level of information.
        - add a job history list, to store each executions history, could be helpful if the test is marked as non-executable. 
        """
        self._hostnames: list = list()
        self._hostnames.append(hostname)
        self.testcase: str = testcase
        self.debug: bool = True
        self.failures: int = 0
        self.id: int = id
        self.rc: int = -1
        self.successful: bool = False
        self.elapsed: str = None
        self.hostpattern: str = "all"
        self.nodes: Dictionary = nodes
        self._stdout_and_stderr: list = list()
        self._stdout_and_stderr.append(hostname)

    def __str__(self) -> str:
        temp = {
            "hostname": self.get_hostname(),
            "testcase": self.testcase,
            "debug": self.debug,
            "failures": self.failures,
            "id": self.id,
            "rc": self.rc,
            "completed": self.completed,
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
        # f-string causing an undiagnosed error.
        #return f"pytest {self.testcase} --host-pattern={self.hostpattern} --zinventory-raw={node_inventory}"
        #return """pytest {0} --host-pattern={1} --zinventory-raw='{2}' >&2 ; echo $? >&1""".format(self.testcase,self.hostpattern,node_inventory)
        return """pytest {0} --host-pattern={1} --zinventory-raw='{2}'""".format(self.testcase,self.hostpattern,node_inventory)

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
        Return the number of failed job executions that have occurred. Failures can be
        a result of the z/OS managed node, a bug in the test case or even a connection issue.
        This is used for statistical purposes or reason to assign the test to a new hostname.

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

    def get_stdout_and_stderr_msgs(self) -> list[str]:
        """
        Return all stdout and stderr messages that have been assigned to this job over time as a list.

        Return
        ------
        list[str]
            A list of all stderr and stdout messages.
        """
        return self._stdout_and_stderr

    def get_stdout_and_stderr_msg(self) -> str:
        """
        Return the stdout and stderr message assigned to this node, in other words, the last message
        resulting from this jobs execution.

        Return
        ------
        str
            The current concatenated stderr and stdout message.
        """
        return self._stdout_and_stderr[-1]

    def set_rc(self, rc: int) -> None:
        """
        Set the jobs return code obtained during execution.

        Parameters
        ----------
        rc : int
            Value that is returned from the jobs execution
        """
        self.rc = rc

    def set_success(self) -> None:
        """
        Mark the job as having completed, or not.

        Parameters
        ----------
        completed : bool
            True if the job has successfully returned with a RC 0,
            otherwise False.
        """
        self.successful = True

    def add_hostname(self, hostname: str) -> None:
        """
        Set the hostname of where the job will be run. Jobs are
        run on z/OS managed nodes.

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

    def set_debug(self, debug: bool):
        """
        Indicate if pytest should run in debug mode, which is the
        equivalent of '-s'.

        Parameters
        ----------
        debug : bool
            True if pytest should run with debug , eg `-s` , else False.
        """
        self.debug = debug

    def set_stdout_and_stderr(self, stdout_stderr: str) -> None:
        """
        Add a stdout and stderr concatenated message resulting from the jobs
        execution (generally std out/err resulting from pytest) the job.

        Parameters
        ----------
        stdout_stderr : str
            Stdout and stderr concatenated into one string.
        """
        self._stdout_and_stderr.append(stdout_stderr)

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
        self.failures: Dictionary[int, Job] = Dictionary()
        self.inventory: dict [str, str] = {}
        self.inventory.update({'host': hostname})
        self.inventory.update({'user': user})
        self.inventory.update({'zoau': zoau})
        self.inventory.update({'pyz': pyz})
        self.assigned: Dictionary[int, Job] = Dictionary()
        self.failures_count: int = 0
        self.assigned_count: int = 0

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
            "failures_count": str(self.failures_count),
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

    def set_failure_job(self, job: Job):
        """
        Add a job to the dictionary that has failed. This is used for statistical
        purposes.
        A Job failure occurs when the execution of the job is a non-zero return code.
        """
        self.failures.add(job.get_id(),job)
        self.failures_count +=1

    def set_assigned(self, job: Job):
        """
        Add a job to the Node that has been assigned to this node (z/OS managed node).
        This is used for statistical purposes.
        """
        self.assigned.add(job.get_id(),job)
        self.assigned_count +=1

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

    def get_failure_jobs_as_string(self) -> str:
        """
        Get a JSON string of all jobs which have failed on this node.

        Return
        ------
        str
            A JSON string representation of all Job(s) that
            have been assigned and failed on this Node.
        """
        return json.dumps(self.failures)

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
        return self.failures_count

    def get_assigned_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have been assigned
        to this Node.
        """
        return self.assigned_count

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


def get_jobs(nodes: Dictionary, testsuite: str, tests: str, skip: str) -> Dictionary:
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

    if hostnames_length == 0:
        raise RuntimeError('No z/OS managed hosts were online, please check host availability.')

    # List to contain absolute paths to comma/space delimited test suites or directories.
    files =[]

    # If testsuite, test suites were provided, else tests (directories) were passed.
    # Remove whitespace and replace CSV with single space delimiter.
    # Build a command that will yield all test cases included parametrized tests.
    cmd = ['pytest', '--collect-only', '-q']
    if testsuite:
        print("testsuite is " + testsuite)
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
    # Run the pytest collect-only command and grep on :: so to avoid warnings
    parametrized_test_cases = subprocess.run([cmd_str], shell=True, capture_output=True, text=True)
    parametrized_test_cases = parametrized_test_cases.stdout.split()
    parametrized_test_cases_count = len(parametrized_test_cases)
    #print("TESTS " + str(parametrized_test_cases))
    # Thread safe dictionary of Jobs
    jobs = Dictionary()
    index = 0
    hostnames_index = 0

    for parametrized_test_case in parametrized_test_cases:

        # Assign each job a hostname using round robin (modulus % division)
        if hostnames_index % hostnames_length == 0:
            hostnames_index = 0

        # Create a temporary job object and add it to thread safe dictionary
        _job = Job(hostname = hostnames[hostnames_index], nodes = nodes, testcase="tests/"+parametrized_test_case, id=index)
        #print(_job)
        jobs.update(index, _job)
        index += 1
        hostnames_index += 1

    # for key, value in jobs.items():
    #     print(f"The job count = {str(jobs.len())}, job id = {key} , job = {str(value)}")

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
    - Mark the nodes state as offline so that no other tests will use the node.
    - Iterate over all jobs looking for inactive ones and balance all of the
      job nodes.
    """

    # List of all ONLINE z/OS active nodes hostnames.
    nodes = list(job.get_nodes().keys())

    # The difference of all available z/OS zos_nodes and ones assigned to a job.
    zos_nodes_not_in_job = list(set(nodes) - set(job.get_hostnames()))
    # TODO: Unsure why index 1 and not 0 or better yet, a random based on length of zos_nodes_not_in_job
    job.add_hostname(zos_nodes_not_in_job[1])


def get_managed_nodes(user: str, zoau: str, pyz: str, hostnames: list[str] = None) -> Dictionary:
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

def get_nodes_online(nodes: Dictionary) -> int:
    """
    Get a count of how many managed Node(s) have status that is equal to Status.ONLINE.
    A value greater than or equal to 1 signifies that Job(s) can continue to execute,
    otherwise there are no managed nodes capable or running a job.

    A Node is set to Status.OFFLINE when the value used for --bal (balance) is
    surpassed. Balance (--bal) is used to signal that Job has run N number of times
    on a particular host and had a non-zero return code and should be used by any other Job.
    """
    nodes_online_count = 0
    for key, value in nodes.items():
        if value.get_state().is_online():
            nodes_online_count += 1

    return nodes_online_count

def get_nodes_offline(nodes: Dictionary) -> int:
    """
    Get a count of how many managed Node(s) have status that is equal to Status.OFFLINE.
    A value greater than or equal to 1 signifies that Job(s) have failed to run on this
    node and that this node should not be used any further.

    A Node is set to Status.OFFLINE when the value used for --bal (balance) is
    surpassed. Balance (--bal) is used to signal that Job has run N number of times
    on a particular host and had a non-zero return code and should be used by any other Job.
    """
    nodes_offline_count = 0
    for key, value in nodes.items():
        if not value.get_state().is_online():
            nodes_offline_count += 1

    return nodes_offline_count

def run(key, jobs, nodes, completed, timeout, max, bal, extra):
    """
    Runs a job (test case) on a z/OS managed node and ensures the job has the necessary
    managed node available. If not, it will manage the node and collect the statistics
    so that it can be properly run when a resource becomes available.

    Returns:
        int:    Return code 0 All tests were collected and passed successfully (pytest)
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

    job = jobs.get(key)
    hostname = job.get_hostname()
    id = str(job.get_id())
    elapsed = 0
    message = None
    rc = None


    # node = nodes.get(host)
    node_count_online = get_nodes_online(nodes = nodes)
    if node_count_online >0:
        start_time = time.time()
        node = nodes.get(hostname)
        # print("Job information: " + "\n  z/OS hosts available = " + str(zos_nodes_len) + "\n  Job ID = " + str(job.get_id()) + "\n  Command = " + job.get_command())
        try:
            # Build command and strategically map stdout and stderr so that both are mapped to stderr and the pytest rc goes to stdout.
            cmd =  f"{extra};{job.get_command()} 1>&2; echo $? >&1"
            result = subprocess.run([cmd], shell=True, capture_output=True, text=True, timeout=timeout)
            job.set_elapsed_time(start_time)
            elapsed = job.get_elapsed_time()
            rc = int(result.stdout)
            pytest_std_out_err = result.stderr
            job.set_stdout_and_stderr(pytest_std_out_err)

            if rc == 0:
                job.set_rc(int(rc))
                job.set_success()
                # TODO: Now that the job class contains more states, do we really need completed? 
                completed.update(job.get_id(), job)
                rc_msg = "Test collected and passed successfully."
                message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
            else:
                job_failures = job.get_failure_count()

                if job_failures >= max:
                    rc = 8
                    job.set_rc(int(rc))
                    # Do node stuff
                    rc_msg = f"Test exceeded permitted failures = {max}."
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
                elif job_failures == bal:
                    rc = 7
                    job.set_rc(int(rc))
                    update_job_hostname(job) # TODO: eval the logic for balance
                    rc_msg = f"Test has been assigned to a new z/OS managed node = {job.get_hostname()}, because it exceeded balance = {bal}"
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
                elif rc == 1:
                    job.set_rc(int(rc))
                    rc_msg = "Test case was collected and failed with an error."
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
                elif rc == 2:
                    job.set_rc(int(rc))
                    rc_msg = "Test case execution was interrupted by the user."
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
                elif rc == 3:
                    job.set_rc(int(rc))
                    rc_msg = "Internal error occurred while executing test."
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
                elif rc == 4:
                    job.set_rc(int(rc))
                    rc_msg = "Pytest command line usage error."
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
                elif rc == 5:
                    job.set_rc(int(rc))
                    rc_msg = "No tests were collected ."
                    message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"

                # Increment the job failure afterwards, else it will skew the logic above.
                job.increment_failure()

                # Logic here to update nodes with failure information.
                

        except subprocess.TimeoutExpired:
            job.set_elapsed_time(start_time)
            elapsed = job.get_elapsed_time()
            rc = 9
            job.set_rc(int(rc))
            pytest_std_out_err = result.stderr
            job.set_stdout_and_stderr(pytest_std_out_err)
            rc_msg = f"Job has exceeded subprocess timeout = {str(timeout)}"
            message = f"Job ID = {id}, host = {hostname}, elapsed time = {elapsed}, rc = {str(rc)}, rc msg = {rc_msg}"
    else:
        rc = 6
        rc_msg = "There are no z/OS managed nodes available to run jobs."
        message = f"Job ID = {id}, host = {hostname}, elapsed time = {job.get_elapsed_time()}, rc = {str(rc)}, rc msg = {rc_msg}"

    print(message)
    return rc, message


def runner(jobs, zos_nodes, completed, timeout, max, bal, extra):
    """Creates the thread pool to execute job in the dictionary using the run
    method.
    """
    # Set the number of threads as the number of zos_nodes we have, this is a limitation
    # that can be removed once the tests have been updated to support a concurrency model.
    number_of_threads = zos_nodes.len() * 3

    with ThreadPoolExecutor(number_of_threads) as executor:

        futures = [executor.submit(run, key, jobs, zos_nodes, completed, timeout, max, bal, extra) for key, value in jobs.items() if not value.get_successful()]
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

def elapsed_time(start_time):
        """
        Given a start time, this will return a formatted string of time matching
        pattern HH:MM:SS.SS , eg 00:02:38.36
        """

        hours, rem = divmod(time.time() - start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)
        return elapsed

# def main(argv):
def main():
    # python3 load_balance.py --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz" --zoau "/zoau/v1.3.1" --itr 10 --args "cd /Users/ddimatos/git/gh/ibm_zos_core;"  --tests /Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_tso_command_func.py --user "omvsadm" --skip tests/functional/modules/test_module_security.py
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
                    --max 6\\
                    --bal 3\\
                    --hostnames "ec33025a.vmec.svl.ibm.com,ec33025a.vmec.svl.ibm"\\
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
    parser.add_argument('--max', type=int, help='The maximum number of times a job can fail before its removed from the job queue.', required=False, metavar='<int>', default="6")
    parser.add_argument('--bal', type=int, help='The count at which a job is balanced from one z/OS node to another for execution.', required=False, metavar='<int>', default="3")
    parser.add_argument('--hostnames', help='List of hostnames to use, overrides the auto detection.', required=False, metavar='<list[str]>', default=None, nargs='*')

    # Mutually exclusive options
    group_tests_or_dirs = parser.add_argument_group('Mutually exclusive', 'Absolute path to test suites. For more than one, use a comma or space delimiter.')
    exclusive_group_or_tests = group_tests_or_dirs.add_mutually_exclusive_group(required=True)
    exclusive_group_or_tests.add_argument('--testsuite', type=str, help='Space or comma delimited test suites, must be absolute path(s)', required=False, metavar='<str,str>', default="")
    exclusive_group_or_tests.add_argument('--tests', type=str, help='Space or comma delimited directories containing test suites, must be absolute path(s)', required=False, metavar='<str,str>', default=None)
    args = parser.parse_args()

    start_time_full_run = time.time()

    # Empty dictionary to start, will contain all completed jobs.
    completed = Dictionary()

    # Get a dictionary of all active zos_nodes to run tests on
    nodes = get_managed_nodes(user = args.user, zoau = args.zoau, pyz = args.pyz, hostnames = args.hostnames)

    # Get a dictionary of jobs containing the work to be run on a node.
    # TODO: get_jobs raises an runtime exception need to handle this.
    jobs = get_jobs(nodes, testsuite=args.testsuite, tests=args.tests, skip=args.skip)

    count = 1
    iterations_result=""
    number_of_threads = nodes.len()
    while completed.len() != jobs.len() and count < int(args.itr):
        print("Thread pool iteration " + str(count))
        print("Thread pool iteration " + str(count) + " has completed " + str(completed.len()) + " jobs.")
        print("Thread pool iteration " + str(count) + " has pending " + str(jobs.len() - completed.len()) + " jobs.")
        print("Thread pool has " + str(number_of_threads) + " threads running concurrently.")

        job_completed_before = completed.len()
        start_time = time.time()
        runner(jobs, nodes, completed, args.timeout, args.max, args.bal, args.extra)
        jobs_completed_after = completed.len() - job_completed_before
        iterations_result += "Thread pool iteration " + str(count) + " completed " + str(jobs_completed_after) + " job(s) in " + elapsed_time(start_time) + " time. \n"
        count +=1

    fail_gt_eq_to_max=0
    fail_less_than_max=0
    total_failed=0
    total_balanced=0
    for key, job in jobs.items():
        fails=job.get_failure_count()
        bal = job.get_hostnames()
        if fails >= args.max:
            fail_gt_eq_to_max+=1
            total_failed+=1
        if fails != 0 and fails <6:
            fail_less_than_max+=1
            total_failed+=1

        if len(bal) > 1:
            total_balanced+=1

    print("All " + str(count - 1) + " thread pool iterations completed in " +  elapsed_time(start_time_full_run) + " time.")
    print(iterations_result)
    print("Number of jobs queued to be run = " + str(jobs.len()))
    print("Number of jobs that run successfully = " + str(completed.len()))
    print("Total number of jobs that failed = " + str(total_failed))
    print("Number of jobs that failed 6 times = " + str(fail_gt_eq_to_max))
    print("Number of jobs that failed less than 6 times = " + str(fail_less_than_max))
    print("Number of jobs that had zos_nodes rebalanced = " + str(total_balanced))

if __name__ == '__main__':
    main()
