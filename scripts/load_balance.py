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
    ONLINE=1
    OFFLINE=0

    def __str__(self) -> str:
        return self.name.lower()

    def num(self) -> int:
        return self.value

    @classmethod
    def default(cls):
        return cls.ONLINE.name.lower()

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
        self.failures: int = 0
        self.inventory: dict [str, str] = {}
        self.inventory.update({'host': hostname})
        self.inventory.update({'user': user})
        self.inventory.update({'zoau': zoau})
        self.inventory.update({'pyz': pyz})

    def __str__(self) -> str:
        temp = {
            "hostname": self.hostname,
            "user": self.user,
            "zoau": self.zoau,
            "pyz": self.pyz,
            "state": str(self.state),
            "failures": self.failures,
            "inventory": self.get_inventory_as_string()
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

    def increment_failure(self):
        """
        Increment the failure of this job by 1. Job failure occurs
        when the execution of the job is a non-zero return code.
        """
        self.failures += 1

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
        Get a JSON dict() that can be used with the 'zinventory-raw'
        pytest fixture. This is the dict() so that it can be updated.
        To use it with the 'zinventory-raw', the dict() would have to
        be converted to a string with json.dumps(...) or equivalent.

        Return
        ------
        str
            A JSON dict() of necessary z/OS managed node attributes.
        """
        return self.inventory

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
        self.completed: bool = False
        self.elapsed: str = None
        self.hostpattern: str = "all"
        self.nodes: Dictionary = nodes

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
        return """pytest {0} --host-pattern={1} --zinventory-raw='{2}' >&2 ; echo $? >&1""".format(self.testcase,self.hostpattern,node_inventory)


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

    def get_failures(self) -> int:
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

    def get_completed(self) -> bool:
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
        return self.completed

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
        Returns a dictionary of all z/OS managed nodes used in this
        runtime. z/OS managed nodes are identified and passed as a
        dictionary to a job for easy access and update, for example,
        if a job needs to mark the node as offline, it can easily
        access the dictionary of z/OS managed nodes to do so.

        Return
        ------
        Dictionary[str, node]
            Thread safe Dictionary of z/OS managed nodes.
        """
        return self.nodes

    def set_rc(self, rc: int) -> None:
        """
        Set the jobs return code obtained during execution.

        Parameters
        ----------
        rc : int
            Value that is returned from the jobs execution
        """
        self.rc = rc

    def set_completed(self, completed: bool) -> None:
        """
        Mark the job as having completed, or not.

        Parameters
        ----------
        completed : bool
            True if the job has successfully returned with a RC 0,
            otherwise False.
        """
        self.completed = completed

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

    def add_failure(self) -> None:
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


def get_managed_nodes(user: str, zoau: str, pyz: str) -> Dictionary:
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
    hostnames = []

    # Calling venv.sh directly to avoid the ac dependency, ac usually lives in project root so an
    # additional arg would have to be passed like so: "cd ..;./ac --host-nodes --all false"
    result = subprocess.run(["echo `./venv.sh --targets-production`"], shell=True, capture_output=True, text=True)
    hostnames = result.stdout.split()

    # Prune any production system that fails to ping
    for hostname in hostnames:
        command = ['ping', '-c', '1', hostname]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # TODO: Use the connection class to connection and validate ZOAU and Python before adding the nodes
        if result.returncode == 0:
            nodes.update(key=hostname, obj=Node(hostname = hostname, user = user, zoau = zoau, pyz = pyz))

    # for key, value in nodes.items():
    #     print(f"The z/OS node count = {str(nodes.len())}, hostname = {key} , node = {str(value)}")

    return nodes


def run(key, jobs, zos_nodes, completed, timeout, max, bal):
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

    message = None
    job = jobs.get(key)
    rc = job.get_rc()
    host = job.get_hostname()
    zos_nodes_len = zos_nodes.len()


    # if zos_node is not None:
    # TODO, remove True and determine if its needed, previously the node dictionary was continuously having nodes added
    # and remove to address that some test cases could not be run concurrently, now the tests can be run concurrently. 
    if True:
        start_time = time.time()
        # print("Job information: " + "\n  z/OS hosts available = " + str(zos_nodes_len) + "\n  Job ID = " + str(job.get_id()) + "\n  Command = " + job.get_command())
        try:
            result = subprocess.run(["cd ..;"+job.get_command()], shell=True, capture_output=True, text=True, timeout=timeout)
            job.set_elapsed_time(start_time)
            rc = int(result.stdout)
            job.set_rc(int(rc))
        except subprocess.TimeoutExpired:
            job.set_elapsed_time(start_time)
            message = "Job " + str(job.get_id()) + " has exceeded the configured execution timeout and returned with rc = " + str(rc) + "."
            print(message)
            rc = 9

        if rc == 0:
            message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time() + "."
            print(message)
            job.set_completed(True)
            completed.update(job.get_id(), job)
        else:
            job.add_failure()
            job_failures = job.get_failures()

            if job_failures >= max: #6:
                # What do we do here with this job if it fails too many times, do we take it out of the job list? Put it elsewhere? 
                #jobs.update(job.get_id(), job)
                message = "Job no longer eligible for execution = " + str(job) + " returned with rc = " + str(rc) + "."
                print(message)
                rc = 8
            elif job_failures == bal: #3:
                # WHat do we do with invalid ECs at this point, take the EC out of the node list and traverse jobs and remove as well? 
                # maybe node list removal is enough.
                # What do we do with the failed Nodes, store them in a dictionary
                message = "Job is being rebalanced = " + str(job) + " returned with rc = " + str(rc) + "."
                print(message)
                update_job_hostname(job)
                rc = 7
            elif rc == 1:
                message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time()
                print(message)
            elif rc == 2:
                message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time()
                print(message)
            elif rc == 3:
                message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time()
                print(message)
            elif rc == 4:
                message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time()
                print(message)
            elif rc == 5:
                message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time()
                print(message)
    else:
        # No zos_node was available, they are currently all in use
        message = "There are no z/OS nodes available to Job ID = " + str(job.get_id()) + " returned with rc = " + str(rc) + " setting rc to 6"
        rc = 6
        print(message)

    return rc, message


def runner(jobs, zos_nodes, completed, timeout, max, bal):
    """Creates the thread pool to execute job in the dictionary using the run
    method.
    """
    # Set the number of threads as the number of zos_nodes we have, this is a limitation
    # that can be removed once the tests have been updated to support a concurrency model.
    number_of_threads = zos_nodes.len() * 3

    with ThreadPoolExecutor(number_of_threads) as executor:

        futures = [executor.submit(run, key, jobs, zos_nodes, completed, timeout, max, bal) for key, value in jobs.items() if not value.get_completed()]
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
                    --bal 3
        '''))

    parser.add_argument('--pyz', type=str, help='Python Z home directory.', required=True, metavar='<str,str>', default="sss")
    parser.add_argument('--zoau', type=str, help='ZOAU home directory.', required=True, metavar='<str,str>', default="")
    parser.add_argument('--itr', type=int, help='How many times to run the test suite, exists early if all succeed.', required=True, metavar='<int>', default="")
    parser.add_argument('--skip', type=str, help='Identify test suites to skip, only honored with option \'--directories\'', required=False, metavar='<str,str>', default="")
    parser.add_argument('--user', type=str, help='z/OS USS user authorized to run Ansible tests on the managed z/OS node', required=True, metavar='<str>', default="")
    parser.add_argument('--timeout', type=int, help='The maximum time in seconds a job should run on z/OS for, default is 300 seconds.', required=False, metavar='<int>', default="300")
    parser.add_argument('--max', type=int, help='The maximum number of times a job can fail before its removed from the job queue.', required=False, metavar='<int>', default="6")
    parser.add_argument('--bal', type=int, help='The count at which a job is balanced from one z/OS node to another for execution.', required=False, metavar='<int>', default="3")

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
    nodes = get_managed_nodes(user = args.user, zoau = args.zoau, pyz = args.pyz)

    # Get a dictionary of jobs containing the work to be run on a node.
    jobs = get_jobs(nodes, testsuite=args.testsuite, tests=args.tests, skip=args.skip)

    count = 1
    iterations_result=""
    number_of_threads = nodes.len()
    while completed.len() != jobs.len() and count < int(args.itr):
        print("Thread pool iteration " + str(count))
        print("Thread pool iteration " + str(count) + " has completed " + str(completed.len()) + " jobs.")
        print("Thread pool iteration " + str(count) + " has pending " + str(jobs.len() - completed.len()) + " jobs.")
        print("Thread pool has " + str(number_of_threads) + " threads running concurrently.")

        job_completed_before = completed.len();
        start_time = time.time()
        runner(jobs, nodes, completed, args.timeout, args.max, args.bal)
        jobs_completed_after = completed.len() - job_completed_before
        iterations_result += "Thread pool iteration " + str(count) + " completed " + str(jobs_completed_after) + " job(s) in " + elapsed_time(start_time) + " time. \n"
        count +=1

    fail_gt_eq_to_max=0
    fail_less_than_max=0
    total_failed=0
    total_balanced=0
    for key, job in jobs.items():
        fails=job.get_failures()
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
