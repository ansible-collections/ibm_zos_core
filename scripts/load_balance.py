# download document files concurrently and save the files locally concurrently
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

# ------------------------------------------------------------------------------
# Helpers to collect test status
# ------------------------------------------------------------------------------
def get_all_files_in_dir_tree(base_path):
    """Recursively search subdirectories for files according to base_path.
    Args:
        base_path (str): The directory to recursively search.
    Returns:
    list[str]: A list of file paths.
        """

    found_files = []
    for root, subdirs, files in os.walk(base_path):
        for file in files:
            found_files.append(os.path.join(root, file))
    return found_files

def get_all_test_suites(collection_root):
    """Build a list of all test suites for collection_root which equates to
       <path>/github/ibm_zos_core/
    Args:
        collection_root (str): The path to the root of the collection
    Returns:
        list[tests]: A list of test cases.
    Example:
        suites = get_all_test_suites("/Users/ddimatos/git/github/ibm_zos_core/")
        print(suites)
    """

    files = []
    # Not support unit tests at this time
    # files += get_all_files_in_dir_tree(collection_root + "/tests/unit")
    files += get_all_files_in_dir_tree(collection_root + "/tests/functional")

    test_suites = []
    for file in files:
        if file.endswith(".py"):
            path, filename = os.path.split(file)
            if filename.startswith('test'):
                test_suites.append(file)
    return test_suites

def get_all_test_cases(collection_root):
    """Build a list of all test cases found in test suites
    Args:
        collection_root (str): The path to the root of the collection
    Returns:
        list[tests]: A list of test cases.
    """

    test_suites = []
    files = []
    files += get_all_files_in_dir_tree(collection_root + "/tests/functional")

    for file in files:
        if file.endswith(".py"):
            path, filename = os.path.split(file)
            if filename.startswith('test'):
                with open (file) as test:
                    lines = test.readlines()
                    for line in lines:
                        # Is string present
                        if line.find("def test_") != -1:
                            test_suites.append(line.partition(" ")[2].partition("(")[0])
    return test_suites


def get_jobs_as_dictionary(python=None, zoau=None, cmd_prefix=""):
    """Build a dictionary of job objects representing the test cases to be executed.
    Args:
        collection_root (str): The path to the root of the collection
    Returns:
        list[tests]: A list of test cases.
    Examples:
        tests = get_jobs_as_dictionary(python="3.11", zoau="1.2.2")
        for test in tests:
            print("Count: " + str(test.id) + " command: " + test.get_command())
    """

    nodes = get_active_nodes_as_list()
    nodes_len = len(nodes)

    files = []
    # files += get_all_files_in_dir_tree(collection_root + "/tests/functional")
    # Rely on ./ac for files because ./ac it is a regularly used flow over something custom coded
    result = subprocess.run(["cd ..;./ac --ac-test-discover --all true"], shell=True, capture_output=True, text=True)
    files = result.stdout.split()

    # files = ['/Users/ddimatos/git/github/ibm_zos_core/tests/functional/modules/test_load_balance.py']
    jobs = dictionary()
    index = 0
    for file in files:
        if file.endswith(".py"):
            path, filename = os.path.split(file)
            if filename.startswith('test'):
                with open (file) as test:
                    lines = test.readlines()
                    nodes_index = 0
                    for line in lines:
                        # Look for tests cases , they start with 'test_'
                        if line.find("def test_") != -1:
                            # Every time the end of the nodes dictionary is reached restart from the beginning
                            # to append nodes.
                            if (nodes_index % nodes_len) == 0:
                                nodes_index = 0
                            _job = job(host=nodes[nodes_index], python=python, zoau=zoau, file="tests/functional/modules/" + filename,test=line.partition(" ")[2].partition("(")[0], debug=False, id=index )
                            _job.add_cmd_prefix(cmd_prefix)
                            jobs.update(index, _job)
                            index += 1
                            nodes_index += 1
    return jobs


def assign_new_node_to_job(job_entry):
    """This will review the list of z/OS nodes online and then compare the nodes
       in the job, then it will append a new node to the job which is different
       from the prior ones the job used. Essentially it will assign the job to a
       new target to run on.

       To do this correctly we really should be monitoring the host state where
       connection is put into an object with host name and state (active or not).

       For now, we can traverse the jobs queue at selected times and see if any job
       is not using a connection and assign it.
    """
    # Get a list of all the active nodes again
    nodes = get_active_nodes_as_list()

    # Take the difference the active nodes with nodes set in the job and assign
    # a new node.
    nodes_not_in_job = list(set(nodes) - set(job_entry.get_all_hosts()))
    job_entry.add_host(nodes_not_in_job[1])


def get_active_nodes_as_list():
    """Build a list of all z/OS nodes that are online.
    Returns:
        list[tests]: A list of nodes.
    """

    nodes = []
    active_nodes = []
    result = subprocess.run(["cd ..;./ac --host-nodes --all false"], shell=True, capture_output=True, text=True)

    # Return a list
    nodes = result.stdout.split()

    # Prune anything that is  not up from the list
    for target in nodes:
        command = ['ping', '-c', '1', '-w2', target]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if result.returncode == 0:
            hostname=target.split('.')
            active_nodes.append(hostname[0])
    return active_nodes


def get_active_nodes_as_dictionary():
    """Build a dictionary of active z/OS nodes.
    Args:
    Returns:
        list[tests]: A list of test cases.
    """

    # Custom thread safe dictionary
    nodes = dictionary()

    hosts = []
    result = subprocess.run(["cd ..;./ac --host-nodes --all false"], shell=True, capture_output=True, text=True)

    # Return a list
    hosts = result.stdout.split()

    # Prune anything that is  not up from the list
    for host in hosts:
        command = ['ping', '-c', '1', '-w2', host]
        result = subprocess.run(args=command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if result.returncode == 0:
            hostname=host.split('.')
            nodes.update(hostname[0], node(hostname=hostname[0]))
    return nodes


class dictionary():
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

class node:
        def __init__(self, hostname=None, in_use=False):
            # Failures is only a statistic in case a report is needed.
            # in_use is not used at this time but left behind.
            self.hostname = hostname
            self.in_use = in_use
            self.failures=0

        def __str__(self):
            temp = {
                "hostname": self.hostname,
                "in_use": self.in_use,
                "failures": self.failures,
            }
            return str(temp)

        def set_hostname(self, hostname):
            self.hostname = hostname

        def set_in_use(self, in_use):
            """
            Set if the node is in use, True or False
            """
            self.in_use = in_use

        def increment_failures(self):
            """
            Increment a failure by 1.
            """
            self.failures += 1

        def get_in_use(self):
            return self.in_use

        def get_hostname(self):
            return self.hostname

class job:
    """
    Job object represents a unit of work that the threads will execute, it includes a command
    and stateful fields.
    """
    def __init__(self, host=None, python=None, zoau=None, file=None, test=None, debug=False, id=0):
        """
        TODO:
        - Consider instead of tracking failures as an integer, instead use a list and insert
          the host (node) it failed on for statistical purposes.
        - Consider removing completed because the return code can provide the same level of information.
        """
        self.prefix = ""
        self.hosts = list()
        self.hosts.append(host)
        self.python = python
        self.zoau = zoau
        self.file = file
        self.test = test
        self.debug = debug
        self.failures=0
        self.id = id
        self.rc = -1
        self.completed = False
        self.cmd = "./ac --ac-test"

    def __str__(self):
        temp = {
            "prefix": self.prefix,
            "host": self.hosts,
            "python": self.python,
            "zoau": self.zoau,
            "file": self.file,
            "test": self.test,
            "debug": self.debug,
            "failures": self.failures,
            "id": self.id,
            "rc": self.rc,
            "completed": self.completed
        }

        return str(temp)

    def get_command(self):
        return self.prefix + self.cmd + " --host " + self.hosts[-1] + " --python " + self.python + " --zoau " + self.zoau + " --file " + self.file + " --test " + self.test + " --debug " + str(self.debug)

    def get_all_hosts(self):
        """Return all hosts assigned to this node as a list.
        Returns:
            list[str]: A list of all hosts.
        """
        return self.hosts

    def get_last_host(self):
        """Return the last host assigned to this node, the active host.
        Returns:
            str: hostname prefix
        """
        return self.hosts[-1]

    def get_test_suite(self):
        """The test suite the individual test is contained in.
        Returns:
            str: Fully qualified path of the test suite
        """
        return self.file

    def get_test(self):
        """The test that is assigned to the job.
        Returns:
            str: test case name
        """
        return self.test

    def get_failures(self):
        """Get the number of failed executions that have occurred for this job.
        Often used for statistical purposes or reason to assign the test to a new
        host.
        Returns:
            int: Numerical value greater than 0 or equal to 0.
        """
        return self.failures

    def get_rc(self):
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

    def get_id(self):
        """Returns the job id used as the key in the dictionary to identify the job.
        Returns:
            int: Id of the job
        """
        return self.id

    def get_completed(self):
        """Returns True or False, True if the job has completed execution, this
        aligns to a return code of 0.
        Returns:
            Bool: True if the job completed, otherwise False.
        Note: At this time, completed is generally not used as a the return code
        can serve the same purpose.
        """
        return self.completed

    def set_rc(self, rc):
        """Set the jobs return code obtained during execution.
        Args:
            int: Value that is returned from the jobs execution, it should be
                 transparent to read and set the value, the values should remain
                 between 0 - 5.
        """
        self.rc = rc

    def set_completed(self, completed):
        self.completed = completed

    def add_host(self, host=None):
        self.hosts.append(host)

    def add_failure(self):
        self.failures +=1

    def add_cmd_prefix(self,prefix):
        self.prefix = prefix

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


def run(key, jobs, nodes, completed):
    """Runs a job (test) on the node and ensures the job has the necessary
    resource available. If not, it will manage the node and collect the statistics
    so that it can be properly run when a resource becomes available.

    Returns:
        int:    Return code 0 All tests were collected and passed successfully
                Return code 1 Tests were collected and run but some of the tests failed
                Return code 2 Test execution was interrupted by the user
                Return code 3 Internal error happened while executing tests
                Return code 4 pytest command line usage error
                Return code 5 No tests were collected
    """
    # General but not complete logic:
    # 1) If job's RC is 0 (successful):
    #    - Update the completed jobs dictionary with this entry
    # 2) If jobs RC is non-zero (>0) (failed):
    #    A) If failures >=6
    #       - This is the current threshold where a job is needs to be considered
    #         for evaluation and ensure its not a bug. Thus simply return the
    #         return code and do nothing else.
    #    B) If failures == 3
    #       - Assign the job to a new z/OS host to run on, there is a chance it
    #        succeed on another node. After the assigning of a new new, do nothing
    #        else, it will fall through and be run by the thread. 
    #    c) If (failures >3  && <= 6) or (failures <3)
    #       - There is no need to check the failures match, this is simply the
    #         else case and the job will be run by a thread.
    #       - To run, pop a node to ensure it remains ineligible for another thread
    #         and use it to execute the job.

    rc = None
    job = jobs.get(key)
    job_rc = job.get_rc()

    if job_rc == 0:
        completed.update(job.get_id(), job)
        return job_rc
    elif job_rc > 0:
        print("RUN:: RC >0 " + str(0))
        job_failures = job.get_failures()

        if job_failures >= 6:
            print("RUN:: RC >= " + str(0))
            #jobs.update(job.get_id(), job)
            return job_rc
        else:
            if job_failures == 3:
                print("RUN:: RC == " + str(0))
                assign_new_node_to_job(job)

    # ----------------
    # Run the job
    # ----------------
    host = job.get_last_host()
    print("Accessing job: " + str(job.get_id()) + " is running on host: " + host)
    print("Nodes have a length of: " + str(nodes.len()))
    # Remove the host from the nodes dictionary so it can be used without concern of another thread
    # accessing it. This won't be needed when the tests can be run concurrently.
    node_entry = nodes.pop(host)

    if node_entry is not None:
        print("Command running is: " + job.get_command())
        result = subprocess.run([job.get_command()], shell=True, capture_output=True, text=True)
        rc = result.stdout

        if int(rc) == 0:
            print("Job: " + str(job.get_id()) + " + has a return code : "+ rc)
            job.set_rc(int(rc))
            completed.update(job.get_id(), job)
            nodes.update(node_entry.get_hostname(), node_entry)
            return rc
        else:
            print("Job failure " + result.stderr)
            print("RC for failure is " + rc)
            job.set_rc(int(rc))
            job.add_failure()
            jobs.update(job.get_id(), job)
            nodes.update(node_entry.get_hostname(), node_entry)
    else:
        # Were not able to obtain a node in the allocated default 100 seconds
        print("Not able to obtain access to a node.")
        return 2

    return int(rc)


def runner(jobs, nodes, completed):
    """Creates the thread pool to execute job in the dictionary using the run
    method.
    """
    # Set the number of threads as the number of nodes we have, this is a limitation
    # that can be removed once the tests have been updated to support a concurrency model.
    number_of_threads = nodes.len()

    with ThreadPoolExecutor(number_of_threads) as executor:
        # Run through all jobs and execute them
        futures = [executor.submit(run, key, jobs, nodes, completed) for key, value in jobs.items()]
         # process each result as it is available
        for future in as_completed(futures):
            rc = future.result()
            #print("Details " + str(rc))


def main(argv):
    # Example usage: python load_balance.py --python "3.9" --zoau "1.2.2" --itr 10 --prefix "cd /Users/ddimatos/git/github/ibm_zos_core;"
    try:
      opts, args = getopt.getopt(argv,'-h',['python=','zoau=','itr=', 'prefix='])
    except getopt.GetoptError:
      print ('load_balance.py --python <(str)python> --zoau <(str)zoau> --itr <int>')
      sys.exit(2)

    zoau = "1.2.2"
    pyz = "3.9"
    itr = 10
    cmd_prefix = ""
    for opt, arg in opts:
        if opt == '-h':
            print ('load_balance.py --python <python> --zoau <zoau>')
            sys.exit()
        elif opt in '--python':
            pyz = arg or "3.9"
        elif opt in '--zoau':
            zoau = arg or "1.2.2"
        elif opt in '--itr':
            itr = arg or 10
        elif opt in '--prefix':
            cmd_prefix = arg or ""

    start_time_full_run = time.time()

    # Empty dictionary to start, will contain all completed jobs.
    completed = dictionary()

    # Get a dictionary of all active nodes to run tests on
    nodes = get_active_nodes_as_dictionary()

    print("Hosts that will be used for execution:")
    for key, value in nodes.items():
        print("    " + key)

    # Get a dictionary of jobs containing the work to be run on a node.
    jobs = get_jobs_as_dictionary(python=pyz, zoau=zoau, cmd_prefix=cmd_prefix)

    count = 1
    while completed.len() != jobs.len() and count < int(itr):
        print("Thread pool iteration " + str(count))
        start_time = time.time()
        runner(jobs, nodes, completed)
        count +=1
        time_in_seconds= ((time.time() - start_time)/60)
        print("Thread pool iteration " + str(count) + " completed " + str(completed.len()) + " jobs in " + str(time_in_seconds) + " seconds.")

    time_in_seconds=((time.time() - start_time_full_run)/60)
    print("All " + str(count) + " thread pool iterations completed in " +  str(time_in_seconds) + " seconds.")

    print("Number of jobs that completed: " + str(jobs.len()))

    fail_gt_eq_to_six=0
    fail_less_than_six=0
    total_failed=0
    total_balanced=0
    for key, job in jobs.items():

        fails=job.get_failures()
        bal = job.get_all_hosts()
        if fails >= 6:
            fail_gt_eq_to_six+=1
        if fails != 0 and fails <6:
            fail_less_than_six+=1
        total_failed+=fails

        if len(bal) > 1:
            total_balanced+=1

    print("Number of jobs that failed with 6 or greater: " + str(fail_gt_eq_to_six))
    print("Number of jobs that failed with 6 or less: " + str(fail_less_than_six))
    print("Total number of jobs that failed: " + str(total_failed))
    print("Number of jobs that had nodes rebalanced: " + str(total_balanced))

if __name__ == '__main__':
     main(sys.argv[1:])
