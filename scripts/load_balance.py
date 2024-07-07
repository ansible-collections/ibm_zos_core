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
# TODO: list
# ==============================================================================
#  4. Reduce some of the cross product dependencies, for example can we remove
#  the dependencyfinder.py or other AC tools dependency. Another example the code
#  has this comment (below), while i can see value in using AC, should it be used
#  instead of code written in Python (see get_jobs_as_dictionary..)? DONE
#      # Instead of using get_all_files_in_dir_tree, use ./ac './ac --ac-test-discover'
       # files += get_all_files_in_dir_tree(collection_root + "/tests/functional")
# Document get_jobs_as_dictionary usage with more examples and explanation.
# remove files = get_all_files_in_dir_tree(directories) no need for it

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
    """

    def __init__(self, hostname: str, user: str, zoau: str, pyz: str):
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
        """
        self.state = state

    def increment_failure(self):
        """
        Increment a failure by 1.
        """
        self.failures += 1

    def get_state(self) -> Status:
        return self.state

    def get_hostname(self) -> str:
        return self.hostname

    def get_user(self) -> str:
        return self.user

    def get_zoau(self) -> str:
        return self.zoau

    def get_pyz(self) -> str:
        return self.pyz

    def get_inventory_as_string(self) -> str:
        return json.dumps(self.inventory)

    def get_inventory_as_dict(self) -> dict [str, str]:
        return self.inventory

# ------------------------------------------------------------------------------
# Class job
# ------------------------------------------------------------------------------
class Job:
    """
    Job object represents a unit of work that the threads will execute, it includes a command
    and stateful fields.
    """
    def __init__(self, hostname: str, nodes: Dictionary, testcase: str, id: int):
        """
        TODO:
        - Consider instead of tracking failures as an integer, instead use a list and insert
          the host (node) it failed on for statistical purposes.
        - Consider removing completed because the return code can provide the same level of information.
        """
        self.args: str = None
        self._hostnames: list = list()
        self._hostnames.append(hostname)
        self.testcase: str = testcase
        self.debug: bool = True
        self.failures: int = 0
        self.id: int = id
        self.rc: int = -1
        self.completed: bool = False
        self.cmd: str = "./ac --ac-test"
        self.elapsed: str = None
        self.hostpattern: str = "all"
        self.nodes = nodes

    def __str__(self) -> str:
        temp = {
            "args": self.args,
            "hostname": self.get_hostname(),
            "testcase": self.testcase,
            "debug": self.debug,
            "failures": self.failures,
            "id": self.id,
            "rc": self.rc,
            "completed": self.completed,
            "cmd":  self.cmd,
            "elapsed": self.elapsed,
            "pytest-command": self.get_command()
        }

        return str(temp)

    def get_command(self) -> str:
       # we should build this:
       # pytest tests/functional/modules/test_zos_operator_func.py --host-pattern=all --zinventory-raw='{"host": "ibm.com", "user": "root", "zoau": "/usr/lpp/zoau", "pyz": "/usr/lpp/IBM/pyz"}'
       # return self.args + self.cmd + " --host " + self.hosts[-1] + " --python " + self.python + " --zoau " + self.zoau + " --file " + self.file + " --test " + self.test + " --debug " + str(self.debug)
        #temp = self.test.split("::")
        #print(self.args + self.cmd + " --host " + self.hosts[-1] + " --python " + self.python + " --zoau " + self.zoau + " --file " + temp[0] + " --test " + temp[1] + " --debug " + str(self.debug))
        #return self.args + self.cmd + " --host " + self.hosts[-1] + " --python " + self.python + " --zoau " + self.zoau + " --file " + temp[0] + " --test " + temp[1] + " --debug " + str(self.debug)
        #pytest tests/functional/modules/test_zos_operator_func.py --host-pattern=all --zinventory-raw='{"host": "ec33026a.vmec.svl.ibm.com", "user": "omvsadm", "zoau": "/zoau/v1.3.1", "pyz": "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"}'
        node_temp = self.nodes.get(self.get_hostname())
        node_inventory = node_temp.get_inventory_as_string()
        return f"pytest {self.testcase} --host-pattern={self.hostpattern} --zinventory-raw='{node_inventory}'"

    def get_hostnames(self) -> list[str]:
        """
        Return all hostnames assigned to this job as a list.
        Returns:
            list[str]: A list of all hosts.
        """
        return self._hostnames

    def get_hostname(self) -> str:
        """
        Return the last hostname assigned to this node, the active hostname.
        Returns:
            str: host args
        """
        return self._hostnames[-1]

    def get_testcase(self) -> str:
        """
        Return the testcase that is assigned to this job.
        Returns:
            str: test case name
        """
        return self.testcase

    def get_failures(self) -> int:
        """
        Return the number of failed executions that have occurred for this job.
        Often used for statistical purposes or reason to assign the test to a new
        hostname.
        Returns:
            int: Numerical value greater than 0 or equal to 0.
        """
        return self.failures

    def get_rc(self) -> int:
        """
        Get the return code from the jobs execution.
        Return code 0 All tests were collected and passed successfully
        Return code 1 Tests were collected and run but some of the tests failed
        Return code 2 Test execution was interrupted by the user
        Return code 3 Internal error happened while executing tests
        Return code 4 pytest command line usage error
        Return code 5 No tests were collected

        Returns:
            int: Return code 1 - 5
        """
        return self.rc

    def get_id(self) -> int:
        """
        Returns the job id used as the key in the dictionary to identify the job.
        Returns:
            int: Id of the job
        """
        return self.id

    def get_completed(self) -> bool:
        """
        Returns True if the job has completed execution, this
        aligns to a return code of 0.
        Returns:
            Bool: True if the job completed, otherwise False.
        """
        return self.completed

    def get_elapsed_time(self) -> str:
        """
        Returns the elapsed formatted time for this job.
        Returns:
            str: time
        """
        return self.elapsed

    def get_nodes(self) -> Dictionary:
        return self.nodes

    def set_rc(self, rc: int):
        """
        Set the jobs return code obtained during execution.
        Args:
            int: Value that is returned from the jobs execution, it should be
                 transparent to read and set the value, the values should remain
                 between 0 - 5.
        """
        self.rc = rc

    def set_completed(self, completed: bool):
        self.completed = completed

    def add_hostname(self, hostname: str):
        self.hostnames.append(hostname)

    def add_failure(self):
        self.failures +=1

    def add_args(self,args: str):
        self.args = args

    def set_elapsed_time(self, start_time: time):
        self.elapsed = elapsed_time(start_time)

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


    def __to_dict(self):
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

    def connect(self):
        """
        Create the connection after the connection class has been initialized.

        Returns:
            object: paramiko SSHClient, client used the execution of commands.

        Raises
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
# Helpers to collect test status
# ------------------------------------------------------------------------------
def get_all_files_in_dir_tree(directories):
    """
    Recursively search subdirectories for files according to location.

    Args:
        base_path (str): The directory to recursively search.
    Returns:
        list[str]: A list of file paths.
    """
    directories=directories.strip().replace(',', ' ').split()
    found_files = []

    for directory in directories:
        for root, subdirs, files in os.walk(directory):
            for file in files:
                found_files.append(os.path.join(root, file))

    return found_files

# TODO: Unsure why this is not used and if it needs to remain
def get_all_test_suites(collection_root):
    """
    Build a list of all test suites that correspond to a collections
    root path. For example collection_root could be the path + sub directories:
    <path>/github/ibm_zos_core/

    Args:
        collection_root (str): Path to collections root folder, not the tests folder.
    Returns:
        list[tests]: A list of test cases.

    Example:
        suites = get_all_test_suites("/Users/ddimatos/git/gh/ibm_zos_core/")
        print(suites)
    """

    files = []
    test_suit_path = (collection_root + "/tests/functional")

    if not os.path.exists(test_suit_path):
        raise FileNotFoundError(f"Test case directory {test_suit_path} doesn't exist.")

    files += get_all_files_in_dir_tree(test_suit_path)

    test_suites = []
    for file in files:
        if file.endswith(".py"):
            path, filename = os.path.split(file)
            if filename.startswith('test'):
                test_suites.append(file)
    return test_suites

# TODO: Unsure why this is not used and if it needs to remain
def get_all_test_cases(collection_root):
    """
    Build a list of all test cases found in test suites, unlike `get_all_test_suites`
    which builds a list of test suites, this method will return a list of all test
    cases found in all test suites given the collections project root.

    Args:
        collection_root (str): Path to collections root folder, not the tests folder.

    Returns:
        list[tests]: A list of test cases.
    """

    test_suites = []
    files = []
    test_suit_path = (collection_root + "/tests/functional")

    if not os.path.exists(test_suit_path):
        raise FileNotFoundError(f"Test case directory {test_suit_path} doesn't exist.")

    files += get_all_files_in_dir_tree(test_suit_path)

    for file in files:
        if file.endswith(".py"):
            path, filename = os.path.split(file)
            if filename.startswith('test'):
                with open (file) as test:
                    lines = test.readlines()
                    for line in lines:
                        if line.find("def test_") != -1: # Is string present
                            test_suites.append(line.partition(" ")[2].partition("(")[0])
    return test_suites

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
    if testsuite:
        files = " ".join(files.split())
        files = testsuite.strip().replace(',', ' ').split()
    else:
        tests=" ".join(tests.split())
        files = tests.strip().replace(',', ' ').split()
        # TODO: Check if directories exist

        if skip:
            skip=" ".join(skip.split())
            skip = skip.strip().replace(',', ' ').split()
            # TODO: Check if directories exist

    # Build a command that will yield all test cases included parametrized tests.
    cmd = ['pytest', '--collect-only', '-q']
    cmd.extend(files)
    if skip:
        cmd.extend(['--ignore'])
        cmd.extend(skip)
    cmd.extend(['| grep ::'])
    cmd_str = ' '.join(cmd)

    # Run the pytest collect-only command and grep on :: so to avoid warnings
    parametrized_test_cases = subprocess.run([cmd_str], shell=True, capture_output=True, text=True)
    parametrized_test_cases = parametrized_test_cases.stdout.split()
    parametrized_test_cases_count = len(parametrized_test_cases)
    print("TESTS " + str(parametrized_test_cases))
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
        jobs.update(index, _job)
        index += 1
        hostnames_index += 1
    return jobs


def assign_new_node_to_job(job_entry):
    """
    This will review the list of z/OS zos_nodes that are online and compare them
    to the z/OS zos_nodes assigned in a job, then it will append a new z/OS node to
    the job which is different from the prior assigned z/OS zos_nodes used in the
    job. Essentially it will assign the job to a new target to run on.

    This method is used to re-balance a jobs z/OS hosts, this is done when
    a job consistently fails with a RC of 3, indicating that possibly the
    originally assigned z/OS node is no longer responding well thus the job
    needs a new node assigned to it.

    Note: Leaving this comment here to follow up on, not particularly sure
    what the thinking was about, sounds like maybe we should mark z/OS notes
    as active - meaning functional and others as inactive to mark them as
    problematic to avoid them.
    To do this correctly, the code should really should be monitoring the host
    state where the connection is put into an object with host name and
    state (active or not). (not sure how this will help, leaving the comment for now)
    """

    # Get a list of all the active zos_nodes again
    # zos_nodes = get_active_zos_nodes_as_list()
    zos_nodes = list(job_entry.get_nodes().keys())

    # The difference of all available z/OS zos_nodes and ones assigned to a job.
    zos_nodes_not_in_job = list(set(zos_nodes) - set(job_entry.get_hostnames()))
    # Unsure why index 1 and not 0 or better yet, a random based on length of zos_nodes_not_in_job
    job_entry.add_hostname(zos_nodes_not_in_job[1])


# def get_active_zos_nodes_as_list():
#     """Build a list of all z/OS zos_nodes that are online.
#     Returns:
#         list[tests]: A list of zos_nodes.
#     """

#     zos_nodes = []
#     active_zos_nodes = []
#     result = subprocess.run(["cd ..;./ac --host-nodes --all false"], shell=True, capture_output=True, text=True)

#     # Return a list
#     zos_nodes = result.stdout.split()
#     # print("The zos_nodes are: " + ' '.join(zos_nodes))
#     # Prune anything that is  not up from the list
#     for target in zos_nodes:
#         # Remove wait time, a bit fragile, found it to be W and also w on various OS's
#         # command = ['ping', '-c', '1', '-w2', target]
#         command = ['ping', '-c', '1', target]
#         result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#         if result.returncode == 0:
#             # hostname=target.split('.')
#             active_zos_nodes.append(target)
#     return active_zos_nodes


# def get_active_zos_nodes_as_dictionary():
#     """Build a dictionary of active z/OS zos_nodes.
#     Args:
#     Returns:
#         list[tests]: A list of test cases.
#     """

#     # Custom thread safe dictionary
#     zos_nodes = dictionary()

#     hosts = []
#     result = subprocess.run(["cd ..;./ac --host-nodes --all false"], shell=True, capture_output=True, text=True)

#     # Return a list
#     hosts = result.stdout.split()

#     # Prune anything that is  not up from the list
#     for host in hosts:
#         # command = ['ping', '-c', '1', '-w2', host]
#         command = ['ping', '-c', '1', host]
#         result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#         if result.returncode == 0:
#             hostname=host.split('.')
#             zos_nodes.update(hostname[0], node(host=hostname[0]))
#     return zos_nodes

def get_managed_nodes_as_dictionary(user: str, zoau: str, pyz: str):
    """Build a dictionary of active z/OS zos_nodes.
    Args:
    Returns:
        list[tests]: A list of test cases.
    """
    # Thread safe dictionary
    nodes: Dictionary [str, Node] = Dictionary()
    hostnames = []

    # TODO: Figure out how to remove the AC dependency or ensure that the prefix (cd.../...) comes from the shell args
    result = subprocess.run(["cd ..;./ac --host-nodes --all false"], shell=True, capture_output=True, text=True)
    hostnames = result.stdout.split()

    # Prune any production system that fails to ping
    for hostname in hostnames:
        command = ['ping', '-c', '1', hostname]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # TODO: Use the connection class to connection and validate ZOAU and Python before adding the nodes
        if result.returncode == 0:
            # hostname=host.split('.')
            # zos_nodes.update(hostname[0], node(host = hostname[0], user = user, zoau = zoau, pyz = pyz))
            nodes.update(key=hostname, obj=Node(hostname = hostname, user = user, zoau = zoau, pyz = pyz))
    return nodes


def run(key, jobs, zos_nodes, completed):
    """
    Runs a job (test) on the node and ensures the job has the necessary
    resource available. If not, it will manage the node and collect the statistics
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

    # Remove the host from the zos_nodes dictionary so it can be used without concern of another thread
    # accessing it. This won't be needed when the tests can be run concurrently.

    # zos_node = zos_nodes.pop(host)
    # if zos_node is not None:
    if True:
        start_time = time.time()
        # print("Job information: " + "\n  z/OS hosts available = " + str(zos_nodes_len) + "\n  Job ID = " + str(job.get_id()) + "\n  Command = " + job.get_command())
        try:
            result = subprocess.run([job.get_command()], shell=True, capture_output=True, text=True, timeout=300)
            job.set_elapsed_time(start_time)
            rc = int(result.stdout)
            job.set_rc(int(rc))
        except subprocess.TimeoutExpired:
            job.set_elapsed_time(start_time)
            message = "Job " + str(job.get_id()) + " has exceed permitted execution timeout and returned with rc = " + str(rc) + " setting rc to 9"
            print(message)
            rc = 9


        # zos_nodes.update(zos_node.get_hostname(), zos_node)

        if rc == 0:
            message = "Test with job ID " + str(job.get_id()) + " ran on host " + str(job.get_hostname()) + " with RC " + str(rc) + " in time " + job.get_elapsed_time()
            print(message)
            job.set_completed(True)
            completed.update(job.get_id(), job)
        else:
            job.add_failure()
            job_failures = job.get_failures()

            if job_failures >= 6:
                # What do we do here with this job if it fails too many times, do we take it out of the job list? Put it elsewhere? 
                #jobs.update(job.get_id(), job)
                message = "Job no longer eligible for execution = " + str(job) + " returned with rc = " + str(rc) + " setting rc to 8"
                print(message)
                rc = 8
            elif job_failures == 3:
                # WHat do we do with invalid ECs at this point, take the EC out of the node list and traverse jobs and remove as well? 
                # maybe node list removal is enough. 
                # What do we do with the failed Nodes, store them in a dictionary
                message = "Job is being rebalanced = " + str(job) + " returned with rc = " + str(rc) + " setting rc to 7"
                print(message)
                assign_new_node_to_job(job)
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

        # else:
        #     job.add_failure()
        #     job_failures = job.get_failures()

        #     if job_failures >= 6:
        #         #jobs.update(job.get_id(), job)
        #         message = "Job no longer eligible for execution = " + str(job) + " returned with rc = " + str(rc) + " setting rc to 8"
        #         print(message)
        #         rc = 8
        #     elif job_failures == 3:
        #         message = "Job is being rebalanced = " + str(job) + " returned with rc = " + str(rc) + " setting rc to 7"
        #         print(message)
        #         assign_new_node_to_job(job)
        #         rc = 7

    else:
        # No zos_node was available, they are currently all in use
        message = "There are no z/OS nodes available to Job ID = " + str(job.get_id()) + " returned with rc = " + str(rc) + " setting rc to 6"
        rc = 6
        print(message)

    return rc, message


def runner(jobs, zos_nodes, completed):
    """Creates the thread pool to execute job in the dictionary using the run
    method.
    """
    # Set the number of threads as the number of zos_nodes we have, this is a limitation
    # that can be removed once the tests have been updated to support a concurrency model.
    number_of_threads = zos_nodes.len() * 3

    with ThreadPoolExecutor(number_of_threads) as executor:

        futures = [executor.submit(run, key, jobs, zos_nodes, completed) for key, value in jobs.items() if not value.get_completed()]
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

def main(argv):
    # Example usage:
    # python3 load_balance.py --python "3.9" --zoau "1.2.2" --itr 10 --args "cd /Users/ddimatos/git/gh/ibm_zos_core;"
    # python3 load_balance.py --python "3.10" --zoau "1.3.1" --itr 10 --args "cd /Users/ddimatos/git/gh/ibm_zos_core;" --tests "/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_tso_command_func.py"
    try:
      opts, args = getopt.getopt(argv,'-h',['pyz=','zoau=','itr=', 'args=', 'tests=', 'directories=', 'skip=', 'user='])
    except getopt.GetoptError:
      print ('load_balance.py --pyz <(str)python> --zoau <(str)zoau> --itr <int> --args <str> --directories <str>, --skip <str>', '--user <str>')
      print ('python load_balance.py --pyz \"3.9\" --zoau \"1.2.2\" --itr 10 --args \"cd /Users/ddimatos/git/gh/ibm_zos_core;\"')
      sys.exit(2)

    zoau = "1.2.2"
    pyz = "3.9"
    itr = 10
    args = ""
    tests = None
    directories = None
    skip = None
    user = ""
    for opt, arg in opts:
        if opt == '-h':
            print ('load_balance.py --pyz <python> --zoau <zoau> --itr <int> --args <str> --directories <str>')
            print ('python load_balance.py --pyz \"3.9\" --zoau \"1.2.2\" --itr 10 --args \"cd /Users/ddimatos/git/gh/ibm_zos_core;\" --tests \"test_load_balance.py\"')
            # Use argparse for real help, for now this works:
            print("--pyz - (str) z/OS python version ")
            print("--zoau - (str) zoau version")
            print("--args - (str) a prefix to be run before the generated command, optional")
            print("--tests - (str) space or comma delimited test suites, must be absolute path(s)")
            print("--directories - (str) project directory containing all the tests")
            print("--skip - (str) project directory containing all the tests")
            print("--user - (str) User running on z/OS USS")

            sys.exit()
        elif opt in '--pyz':
            pyz = arg or "3.9"
        elif opt in '--zoau':
            zoau = arg or "1.2.2"
        elif opt in '--itr':
            itr = arg or 10
        elif opt in '--args':
            args = arg or ""
        elif opt in '--tests':
            tests = arg or None
        elif opt in '--directories':
            directories = arg or None
        elif opt in '--skip':
            skip = arg or None
        elif opt in '--user':
            user = arg or None

    start_time_full_run = time.time()

    # Empty dictionary to start, will contain all completed jobs.
    completed = Dictionary()

    # Get a dictionary of all active zos_nodes to run tests on
    zos_nodes = get_managed_nodes_as_dictionary(user = user, zoau = zoau, pyz = pyz)

    for key, value in zos_nodes.items():
        print(f"The z/OS node count = {str(zos_nodes.len())}, hostname = {key} , node = {str(value)}")


    # Get a dictionary of jobs containing the work to be run on a node.
    jobs = get_jobs(zos_nodes, testsuite=tests, tests=directories, skip=skip)

    for key, value in jobs.items():
        print(f"The job count = {str(jobs.len())}, job id = {key} , job = {str(value)}")

    exit(0)
    count = 1
    iterations_result=""
    # print("completed.len() " + str(completed.len()))
    # print("jobs.len() " + str(jobs.len()))
    number_of_threads = zos_nodes.len()
    while completed.len() != jobs.len() and count < int(itr):
        print("Thread pool iteration " + str(count))
        print("Thread pool iteration " + str(count) + " has completed " + str(completed.len()) + " jobs.")
        print("Thread pool iteration " + str(count) + " has pending " + str(jobs.len() - completed.len()) + " jobs.")
        print("Thread pool has " + str(number_of_threads) + " threads running concurrently.")

        job_completed_before = completed.len();
        start_time = time.time()
        runner(jobs, zos_nodes, completed)
        jobs_completed_after = completed.len() - job_completed_before
        iterations_result += "Thread pool iteration " + str(count) + " completed " + str(jobs_completed_after) + " job(s) in " + elapsed_time(start_time) + " time. \n"

        # seconds and had " + str(failures) + "\n"
        count +=1
        #failures = 0

    fail_gt_eq_to_six=0
    fail_less_than_six=0
    total_failed=0
    total_balanced=0
    for key, job in jobs.items():
        fails=job.get_failures()
        bal = job.get_hostnames()
        if fails >= 6:
            fail_gt_eq_to_six+=1
            total_failed+=1
        if fails != 0 and fails <6:
            fail_less_than_six+=1
            total_failed+=1

        if len(bal) > 1:
            total_balanced+=1

    print("All " + str(count - 1) + " thread pool iterations completed in " +  elapsed_time(start_time_full_run) + " time.")
    print(iterations_result)
    print("Number of jobs queued to be run = " + str(jobs.len()))
    print("Number of jobs that run successfully = " + str(completed.len()))
    print("Total number of jobs that failed = " + str(total_failed))
    print("Number of jobs that failed 6 times = " + str(fail_gt_eq_to_six))
    print("Number of jobs that failed less than 6 times = " + str(fail_less_than_six))
    print("Number of jobs that had zos_nodes rebalanced = " + str(total_balanced))

if __name__ == '__main__':
     main(sys.argv[1:])


#./ac --venv-start
#cd /Users/ddimatos/git/gh/ibm_zos_core/scripts
#python load_balance.py --python "3.9" --zoau "1.2.2" --itr 10 --args "cd /Users/ddimatos/git/gh/ibm_zos_core;" --tests "test_load_balance_full.py"

# python3 load_balance.py --python "3.9" --zoau "1.2.2" --itr 10 --args "cd /Users/ddimatos/git/gh/ibm_zos_core;" --directories "/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/,/Users/ddimatos/git/gh/ibm_zos_core/tests/unit/"


