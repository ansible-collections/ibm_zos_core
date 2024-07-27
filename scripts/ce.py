#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
import threading
from paramiko import SSHClient, AutoAddPolicy, BadHostKeyException, \
    AuthenticationException, SSHException, ssh_exception

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


# ------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------
class Status (Enum):
    """
    Represents the online/offline status of a managed node.

    Attributes:
        ONLINE : Status - The node is online.
        OFFLINE : Status - The node is offline.

    Methods:
        number() - Returns the integer value of the status.
        string() - Returns the string representation of the status.
        is_equal(other) - Checks if this status is equal to another status.
        is_online() - Checks if this status is online.
        default() - Returns the default status (ONLINE).
    """

    ONLINE=(1, "online")
    OFFLINE=(0, "offline")

    def __str__(self) -> str:
        """
        Convert the name of the project to lowercase when converting it to a string.

        Return:
            str: The lowercase name of the project.
        """
        return self.name.lower()

    def number(self) -> int:
        """
        Returns the numerical element of the tuple.
        1 for ONLINE and 0 for OFFLINE.

        Return:
            int: The numerical element of the tuple.
                1 for ONLINE and 0 for OFFLINE.
        """
        return self.value[0]

    def string(self) -> str:
        """
        Returns the string value contained in the tuple.
        'online' for ONLINE and 'offline' for OFFLINE.

        Return:
            str: The string value contained in the tuple.
                'online' for ONLINE and 'offline' for OFFLINE.
        """
        return self.value[1]

    def is_equal(self, other) -> bool:
        """
        Checks if two tuples numerical value are the same.

        Parameters:
            other (status): The other tuple to compare to.

        Return:
            bool: True if the numerical tuple values are the same, False otherwise.
        """
        return self.number() == other.number()

    def is_online(self) -> bool:
        """
        Checks if the tuple is ONLINE, if it equates to 1

        Return:
            bool: True if the tuple is ONLINE, False otherwise.
        """
        return self.number() == 1

    @classmethod
    def default(cls):
        """
        Return default status of ONLINE.

        Return:
            Status: Return the ONLINE status.
        """
        return cls.ONLINE

class State (Enum):
    """
    This class represents the state of a job. It has three
    possible values: success, failure, and exceeded-max-failure.

    Attributes:
        SUCCESS (State): A job succeeded execution.
        FAILURE (State): A job failed to execute.
        EXCEEDED (State): A job has exceeded its maximum allowable.
        failures and will no longer be run in the thread pool.
    """
    SUCCESS=(1, "success")
    FAILURE=(0, "failure")
    EXCEEDED=(2, "exceeded-max-failure")

    def __str__(self) -> str:
        """
        Returns the name of the state in uppercase letters.

        Return:
            str: The name of the state in uppercase letters.
                'SUCCESS' a job succeeded execution.
                'FAILURE' a job failed to execute.
                'EXCEEDED' a job has exceeded its maximum allowable failures.
        """
        return self.name.upper()


    def number(self) -> int:
        """
        Returns the numeric value of the state.

        Return:
            int: The numeric value of the state.
                1 for 'SUCCESS' a job succeeded execution.
                2 for 'FAILURE' a job failed to execute.
                3 for 'EXCEEDED' a job has exceeded its maximum allowable failures.
        """
        return self.value[0]

    def string(self) -> str:
        """
        Returns the string representation of the state.

        Return:
            str: The string value of the state.
                'success' a job succeeded execution.
                'failure' a job failed to execute.
                'exceeded-max-failure' a job has exceeded its maximum allowable failures.
        """
        return self.value[1]

    def is_equal(self, other: Enum) -> bool:
        """
        Checks if this state is equal to another state by comparing
        the numerical values for the two states.

        Args:
            other (State): The other state to compare to.

        Return:
            bool: True if the states are equal, False otherwise.
        """
        return self.number() == other.number()

    def is_success(self) -> bool:
        """
        Checks if this state is successful (SUCCESS) by
        ensuring the numerical value is 1.

        Return:
            bool: True if the state is successful, False otherwise.
        """
        return self.number() == 1

    def is_failure(self) -> bool:
        """
        Checks if this state is a failure (FAILURE) by
        ensuring the numerical value is 0.

        Return:
            bool: True if the state is a failure, False otherwise.
        """
        return self.number() == 0

    def is_balanced(self) -> bool:
        """
        Checks if this state has exceeded (EXCEEDED) by
        ensuring the numerical value is 2.

        Return:
            bool: True if the state has exceeded, False otherwise.
        """
        return self.number() == 2

# ------------------------------------------------------------------------------
# Class Dictionary
# ------------------------------------------------------------------------------

class Dictionary():
    """
    This is a wrapper class around a dictionary that provides additional locks
    and logic for when interacting with any of the entries being accessed by
    a thread pool to ensure safe access.
    """

    def __init__(self):
        self._shared_dictionary = dict()
        self._lock = Lock()

    @contextmanager
    def _acquire_with_timeout(self, timeout: int = -1) -> bool:
        """
        Acquires a lock with a timeout in milliseconds.

        Parameters:
            timeout (int): The maximum time to wait for the lock in milliseconds.
                If -1, waits indefinitely.

        Return:
            bool: True if the lock was acquired, False otherwise.
        """
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

    def pop(self, key, timeout: int = 100) -> object:
        """
        Removes the entry from the dictionary and returns it.
        Entry will no longer in remain in the dictionary.

        Parameters:
            key (str): The key of the item to remove.
            timeout (int): The maximum time to wait for acquiring the lock.
                Default is 100ms.

        Return:
            object: The value of the removed item.
        """
        with self._acquire_with_timeout(timeout) as acquired:
            if acquired:
                if self._shared_dictionary:
                    if key in self._shared_dictionary:
                        return self._shared_dictionary.pop(key)
        return None

    def get(self, key, timeout: int = 10) -> object:
        """
        Retrieves the value associated with the given key from the dictionary.

        Args:
            key (str): The key of the entry to retrieve.
            timeout (int): The maximum time to wait for the lock, in seconds.
                Defaults to 10 seconds.

        Return:
            Any: The value associated with the given key.

        Raises:
            KeyError: If the key does not exist in the dictionary.
            TimeoutError: If the lock cannot be acquired before the timeout expires.
        """
        with self._acquire_with_timeout(timeout) as acquired:
            if acquired:
                return self._shared_dictionary[key]

    def update(self, key, obj) -> None:
        """
        Update the dictionary with a new entry, functions same as add(...).
        If the entry exists, it will be replaced.

        Parameters:
            key (str): The key for the dictionary entry.
            obj (object): The object to be stored in the dictionary.
        """
        with self._lock:
            self._shared_dictionary[key]=obj

    def add(self, key, obj) -> None:
        """
        Add an entry to the dictionary, functions same as update(...).
        If the entry exists, it will be replaced.

        Parameters:
            key (str): The key for the dictionary entry.
            obj (object): The object to be stored in the dictionary.
        """
        with self._lock:
            self._shared_dictionary[key]=obj

    def items(self) -> None:
        """
        Returns a tuple (key, value) for each entry in the dictionary.

        Returns:
            A tuple containing the key and value of each entry in the dictionary.
        """
        with self._lock:
            return self._shared_dictionary.items()

    def len(self) -> int:
        """
        Returns the length of the dictionary.

        Returns:
            int: The length of the dictionary.

        Example:
            <dictionary>.len()
        """
        with self._lock:
             return len(self._shared_dictionary)

    def keys(self) -> List[str]:
        """
        Returns a list of all keys in the dictionary.

        Returns:
            List[str]: A list of all keys in the shared dictionary.
        """
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

    Parameters:
    hostname (str): Full hostname for the z/OS manage node the Ansible workload will be executed on.
    nodes (str): Node object that represents a z/OS managed node and all its attributes.
    testcase (str): The USS absolute path to a testcase using '/path/to/test_suite.py::test_case'
    id (int): The id that will be assigned to this job, a unique identifier. The id will be used
        as the key in a dictionary.
    """
    def __init__(self, hostname: str, nodes: Dictionary, testcase: str, id: int):
        """
        Parameters:
            hostname (str): Full hostname for the z/OS manage node the Ansible workload
                will be executed on.
            nodes (str): Node object that represents a z/OS managed node and all its attributes.
            testcase (str): The USS absolute path to a testcase using '/path/to/test_suite.py::test_case'
            id (int): The id that will be assigned to this job, a unique identifier. The id will
                be used as the key in a dictionary.
        """
        self._hostnames: list = list()
        self._hostnames.append(hostname)
        self._testcase: str = testcase
        self._capture: str = None
        self._failures: int = 0
        self._id: int = id
        self._rc: int = -1
        self._successful: bool = False
        self._elapsed: str = None
        self._hostpattern: str = "all"
        self._nodes: Dictionary = nodes
        self._stdout_and_stderr: list[Tuple[str, str, str]] = []
        self._stdout: list[Tuple[str, str, str]] = []
        self._verbose: str = None

    def __str__(self) -> str:
        """
        This function returns a string representation of the Job.

        Parameters:
            self (Job): The Job object to be represented as a string.

        Returns:
            A string representation of the Job object.
        """
        temp = {
            "_hostname": self.get_hostname(),
            "_testcase": self._testcase,
            "_capture": self._capture,
            "_failures": self._failures,
            "_id": self._id,
            "_rc": self._rc,
            "_successful": self._successful,
            "_elapsed": self._elapsed,
            "_hostpattern": self._hostpattern,
            "_pytest-command": self.get_command(),
            "verbose": self._verbose
        }

        return str(temp)

    def get_command(self) -> str:
        """
        Returns a command designed to run with the projects pytest fixture. The command
        is created specifically based on the args defined, such as ZOAU or test cases to run.

        Parameters:
        self (Job)  An instance of the class containing the method.

        Returns:
        str: A string representing the pytest command to be executed.

        Example Return:
            pytest tests/functional/modules/test_zos_job_submit_func.py::test_job_submit_pds[location1]\
              --host-pattern=allNoneNone --zinventory-raw='{"host": "ec33025a.vmec.svl.ibm.com",\
              "user": "omvsadm", "zoau": "/zoau/v1.3.1", "pyz": "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz",\
              "pythonpath": "/zoau/v1.3.1/lib/3.10", "extra_args": {"volumes": ["222222", "000000"]}}'

        """
        node_temp = self._nodes.get(self.get_hostname())
        node_inventory = node_temp.get_inventory_as_string()
        return f"pytest {self._testcase} --host-pattern={self._hostpattern}{self._capture if not None else ""}{self._verbose if not None else ""} --zinventory-raw='{node_inventory}'"


    def get_hostnames(self) -> list[str]:
        """
        Return all hostnames that have been assigned to this job over time as a list.
        Includes hostnames that later replaced with new hostnames because the host is
        considered no longer functioning.

        Return:
            list[str]: A list of all hosts.
        """
        return self._hostnames

    def get_hostname(self) -> str:
        """
        Return the current hostname assigned to this node, in other words, the active hostname.

        Return:
            str: The current hostname assigned to this job.
        """
        return self._hostnames[-1]

    def get_testcase(self) -> str:
        """
        Return a pytest parametrized testcase that is assigned to this job.
        Incudes absolute path, testcase, and parametrization, eg <path/test.py::test[parameter]>

        Return:
            str: Returns absolute path, testcase, and parametrization, eg <path/test.py::test[parameter]>
        """
        return self._testcase

    def get_failure_count(self) -> int:
        """
        Return the number of failed job executions that have occurred for this job.
        Failures can be a result of the z/OS managed node, a bug in the test case or even a
        connection issue. This is used for statistical purposes or reason to assign the test
        to a new hostname.

        Return:
            int: Number representing number of failed executions.
        """
        return self._failures

    def get_rc(self) -> int:
        """
        The return code for the jobs execution.

        Return:
            int:
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
        return self._rc

    def get_id(self) -> int:
        """
        Returns the job id used as the key in the dictionary to identify the job.

        Return:
            int: Id of the job
        """
        return self._id

    def get_successful(self) -> bool:
        """
        Returns True if the job has completed execution.

        Return:
            bool: True if the job completed, otherwise False.

        See Also:
            get_rc() - Returns 0 for success, otherwise non-zero.
        """
        return self._successful

    def get_elapsed_time(self) -> str:
        """
        Returns the elapsed time for this job, in other words,
        how long it took this job to run.

        Return:
            str: Time formatted as <HH:MM:SS.ss> , eg 00:05:30.64
        """
        return self._elapsed

    def get_nodes(self) -> Dictionary:
        """
        Returns a dictionary of all the z/OS managed nodes available.
        z/OS managed nodes are passed to a job so that a job can
        interact with the nodes configuration, for example,
        if a job needs to mark the node as offline, it can easily
        access the dictionary of z/OS managed nodes to do so.

        Return:
            Dictionary[str, node]: Thread safe Dictionary of z/OS managed nodes.
        """
        return self._nodes

    def get_stdout_and_stderr_msgs(self) -> list[Tuple[str, str, str]]:
        """
        Return all stdout and stderr messages that have been assigned to
        this job over time as a list.

        Return:
            list[str]: A list of all stderr and stdout messages.
        """
        return self._stdout_and_stderr

    def get_stdout_msgs(self) -> list[Tuple[str, str, str]]:
        """
        Return all stdout messages that have been assigned to this job
        over time as a list.

        Return:
            list[str]: A list of all stderr and stdout messages.
        """
        return self._stdout

    def get_stdout_and_stderr_msg(self) -> Tuple[str, str, str]:
        """
        Return the current stdout and stderr message assigned to this node, in
        other words, the last message resulting from this jobs execution.

        Return:
            str: The current concatenated stderr and stdout message.
        """
        return self._stdout_and_stderr[-1]

    def get_stdout_msg(self) -> Tuple[str, str, str]:
        """
        Return the current stdout message assigned to this node, in other
        words, the last message resulting from this jobs execution.

        Return:
            str: The current concatenated stderr and stdout message.
        """
        return self._stdout[-1]

    def set_rc(self, rc: int) -> None:
        """
        Set the jobs return code obtained from execution.

        Parameters:
            rc (int): Value that is returned from the jobs execution
        """
        self._rc = rc

    def set_success(self) -> None:
        """
        Mark the job as having completed successfully.

        Parameters:
            completed (bool): True if the job has successfully returned
            with a RC 0, otherwise False.
        """
        self._successful = True

    def add_hostname(self, hostname: str) -> None:
        """
        Set the hostname of where the job will be run.

        Parameters:
            hostname (str): Hostname of the z/OS managed node.
        """
        self._hostnames.append(hostname)

    def increment_failure(self) -> None:
        """
        Increment the failure by 1 for this jobs. Each time the job
        returns with a non-zero return code, increment the value
        so this statistic can be reused in other logic.
        """
        self._failures +=1

    def set_elapsed_time(self, start_time: time) -> None:
        """
        Set the start time to obtain the elapsed time this
        job took to run. Should only set this when RC is zero.

        Parameters:
            start_time (time): The time the job started. A start time should be
                captured before the job is run, and passed to this
                function after the job completes for accuracy of
                elapsed time.
        """
        self._elapsed = elapsed_time(start_time)

    def set_capture(self, capture: bool) -> None:
        """
        Indicate if pytest should run with '-s', which will
        show output and not to capture any output. Pytest
        captures all output sent to stdout and stderr,
        so you won't see the printed output in the console
        when running tests unless a test fails.
        """
        if capture is True:
            self._capture = " -s"

    def set_verbose(self, verbosity: int) -> None:
        """
        Indicate if pytest should run with verbosity to show
        detailed console outputs and debug failing tests.
        Verbosity is defined by the number of v's passed
        to py test.

        If verbosity is outside of the numerical range, no
        verbosity is set.

        Parameters:
            int: Integer range 1 - 4
                 1 = -v
                 2 = -vv
                 3 = -vvv
                 4 = -vvvv
        """
        if verbosity == 1:
            self._verbose = " -v"
        elif verbosity == 2:
            self._verbose = " -vv"
        elif verbosity == 3:
            self._verbose = " -vvv"
        elif verbosity == 4:
            self._verbose = " -vvvv"

    def set_stdout_and_stderr(self, message: str, std_out_err: str, date_time: str) -> None:
        """
        Add a stdout and stderr concatenated message resulting from the jobs
        execution (generally std out/err resulting from pytest) the job.

        Parameters:
            message (str): Message associated with the stdout and stderr output. Message
                describes the std_out_err entry.
            stdout_stderr (str): Stdout and stderr concatenated into one string.
            date_time (str): Date and time when the stdout and stderr output was generated.
        """

        Joblog = namedtuple('Joblog',['id', 'hostname', 'command', 'message', 'std_out_err', 'date_time'])

        joblog = Joblog(self._id, self._hostnames[-1], self.get_command(), message, std_out_err, date_time)
        self._stdout_and_stderr.append(joblog)

    def set_stdout(self, message: str, std_out_err: str, date_time: str) -> None:
        """
        Add a stdout concatenated message resulting from the jobs
        execution (generally std out/err resulting from pytest) the job.

        Parameters:
            message (str): Message associated with the stdout/stderr output.
            stdout_stderr (str): Stdout and stderr concatenated into one string.
            date_time (str): Date and time when the stdout/stderr was generated.
        """
        Joblog = namedtuple('Joblog',['id', 'hostname', 'command', 'message', 'std_out_err', 'date_time'])

        joblog = Joblog(self._id, self._hostnames[-1], self.get_command(), message, std_out_err, date_time)
        self._stdout.append(joblog)

# ------------------------------------------------------------------------------
# Class Node
# ------------------------------------------------------------------------------


class Node:
    """
    A z/OS node suitable for Ansible tests to execute. Attributes such as 'host',
    'zoau', 'user' and 'pyz' , etc are maintained in this class instance because
    these attributes can vary between nodes. These attributes are then used to
    create a  dictionary for use with pytest fixture 'zinventory-raw'.

    This node will also track the health of the node, whether its status.ONLINE
    meaning its discoverable and useable or status.OFFLINE meaning over time,
    since being status.ONLINE, it has been determined unusable and thus marked
    as status.OFFLINE.

    Parameters:
        hostname (str): Hostname for the z/OS managed node the Ansible workload
            will be executed on.
        user (str): The USS user who will run the Ansible workload on z/OS.
        zoau (str): The USS absolute path to where ZOAU is installed.
        pyz( str): The USS absolute path to where python is installed.
    """

    def __init__(self, hostname: str, user: str, zoau: str, pyz: str):
        """

        Parameters:
            hostname (str): Hostname for the z/OS managed node the Ansible workload
                will be executed on.
            user (str): The USS user who will run the Ansible workload on z/OS.
            zoau (str): The USS absolute path to where ZOAU is installed.
            pyz( str): The USS absolute path to where python is installed.

        """
        self._hostname: str = hostname
        self._user: str = user
        self._zoau: str = zoau
        self._pyz: str = pyz
        self._state: Status = Status.ONLINE
        self._failures: set[int] = set()
        self._balanced: set[int] = set()
        self._inventory: dict [str, str] = {}
        self._inventory.update({'host': hostname})
        self._inventory.update({'user': user})
        self._inventory.update({'zoau': zoau})
        self._inventory.update({'pyz': pyz})
        self._inventory.update({'pythonpath': '/zoau/v1.3.1/lib/3.10'})
        self._extra_args = dict()
        self._extra_args.update({'extra_args':{'volumes':['222222','000000']}})
        self._inventory.update(self._extra_args)
        self._assigned: Dictionary[int, Job] = Dictionary()
        self.failure_count: int = 0
        self._assigned_count: int = 0
        self._balanced_count: int = 0
        self._running_job_id: int = -1

    def __str__(self) -> str:
        """
        String representation of the Node class. Not every class
        variable is returned, some of the dictionaries which track
        state are large and should be accessed directly from those
        class members.
        """
        temp = {
            "_hostname": self._hostname,
            "_user": self._user,
            "_zoau": self._zoau,
            "_pyz": self._pyz,
            "_state": str(self._state),
            "inventory": self.get_inventory_as_string(),
            "failure_count": str(self.failure_count),
            "assigned_count": str(self._assigned_count),
            "_balanced_count": str(self._balanced_coun),
            "_running_job_id": str(self._running_job_id)
        }
        return str(temp)

    def set_state(self, state: Status) -> None:
        """
        Set status of the node, is the z/OS node ONLINE (useable)
        or OFFLINE (not usable).

        Parameters:
        state (Status): Set state to Status.ONLINE or Status.OFFLINE.
            Use Status.ONLINE to signal the managed node is healthy, use
            Status.OFFLINE to signal the managed node should not used
            to run any jobs.
        """
        self._state = state

    def set_failure_job_id(self, id: int) -> None:
        """
        Update the node with any jobs which fail to run. If a job fails to run,
        add the job ID to the nodes class. A Job failure occurs when the
        execution of the job is a non-zero return code.

        Parameters:
            id (int): The ID of the job that failed to run.
        """
        self._failures.add(id)
        self.failure_count = len(self._failures)

    def set_assigned_job(self, job: Job) -> None:
        """
        Add a job to the Node that has been assigned to this node (z/OS managed node).

        Parameters:
            job (Job): The job that has been assigned to this node.
        """
        self._assigned.add(job.get_id(),job)
        self._assigned_count +=1

    def set_balanced_job_id(self, id: int) -> None:
        """
        Add a jobs ID to the node, when a job has been rebalanced.

        Parameters:
            id (int): The job ID to add to the set of balanced jobs.
        """
        self._balanced.add(id)

    def set_running_job_id(self, running_job_id: int) -> None:
        """
        Set the ID of the currently running job.

        Parameters:
            running_job_id (int): The ID of the currently running job.
        """
        self._running_job_id = running_job_id

    def get_state(self) -> Status:
        """
        Get the z/OS manage node status.

        Return:
            Status.ONLINE: If the  z/OS managed node state is usable.
            Status.OFFLINE: If the z/OS managed node state is unusable.
        """
        return self._state

    def get_hostname(self) -> str:
        """
        Get the hostname for this managed node. A node is a
        z/OS host capable of running an Ansible unit of work.

        Return:
            str: The managed nodes hostname.
        """
        return self._hostname

    def get_user(self) -> str:
        """
        Get the users id that is permitted to run an Ansible workload on
        the managed node.

        Return:
        str: Unix System Services (USS) user name
        """
        return self._user

    def get_zoau(self) -> str:
        """
        Get the ZOAU home directory path found on the managed node.

        Return:
            str: Unix System Services (USS) absolute path of where
                ZOAU is installed.
        """
        return self._zoau

    def get_pyz(self) -> str:
        """
        Get the Python home directory path found on the managed node.

        Return:
            str: Unix System Services (USS) absolute path of where
                python is installed.
        """
        return self._pyz

    def get_inventory_as_string(self) -> str:
        """
        Get a JSON string of the inventory that can be used with
        the 'zinventory-raw' pytest fixture. This JSON string can be
        passed directly to the option 'zinventory-raw', for example:

        pytest .... --zinventory-raw='{.....}'

        Return:
            str: A JSON string of the managed node inventory attributes.
        """
        return json.dumps(self._inventory)

    def get_inventory_as_dict(self) -> dict [str, str]:
        """
        Get a dictionary that can be used with the 'zinventory-raw'
        pytest fixture. This is the dict() not a string, you might
        choose this so you can dynamically update the dictionary and
        then use json.dumps(...) to convert it to string and pass it
        to zinventory-raw'.

        Return:
            dict [str, str]: A dictionary of the managed node
                inventory attributes.
        """
        return self._inventory

    def get_failure_jobs_as_dictionary(self) -> Dictionary:
        """
        Get a Dictionary() of all jobs which have failed on this node.

        Return:
            Dictionary[int, Job]: A Dictionary() of all Job(s) that have
                been assigned and failed on this Node.
        """
        return self._failures

    def get_assigned_jobs_as_string(self) -> str:
        """
        Get a JSON string of all jobs which have been assigned to this node.

        Return:
            str: A JSON string representation of a job.
        """
        return json.dumps(self._assigned)

    def get_assigned_jobs_as_dictionary(self) -> Dictionary:
        """
        Get a Dictionary of all jobs which have been assigned to this node.

        Return:
            Dictionary[int, Job]: A Dictionary of all jobs which have
                failed on this node.
        """
        return self._assigned

    def get_failure_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have failed on this
        Node with a non-zero return code.

        Returns:
            int: The number of failed Jobs.
        """
        return self.failure_count

    def get_assigned_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have been assigned
        to this Node.

        Returns:
            int: The number of Jobs assigned to this Node.
        """
        return self._assigned_count

    def get_balanced_job_count(self) -> int:
        """
        Get the numerical count of how many Job(s) have been
        reassigned (balanced) to this Node.

        Returns:
            int: The number of jobs which have been balanced onto
                this node.
        """
        self._balanced_count = len(self._balanced)
        return self._balanced_count

    def get_running_job_id(self) -> int:
        """
        Get the job id of the currently running job.

        Returns:
            int: The job id of the currently running job.
        """
        return self._running_job_id

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
        self._hostname = hostname
        self.port = port
        self._username = username
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
            "hostname": self._hostname,
            "port": self.port,
            "username": self._username,
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
        hostname = list(sorted_items_by_assigned)[0]
        job.add_hostname(hostname)
        nodes.get(hostname).set_assigned_job(job)


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

# def set_nodes_offline(nodes: Dictionary, maxnode: int) -> None:
#     for key, value in nodes.items():
#         if value.get_balanced_count() > maxnode:
#             value.set_state(Status.OFFLINE)

def set_node_offline(node: Node, maxnode: int) -> None:
    """
    Sets a node offline if it has exceeded maxnode, the number of permitted
    balanced jobs for a node. 'maxnode' is defined as the maximum number of
    times a node can fail to run a job before its set to 'offline' indicating
    the node is no longer suitable for job execution.

    Parameters:
        node (Node): The node to check for balanced jobs.
        maxnode (int): The maximum number of balanced jobs
        allowed on a node before it is set offline.
    """
    if node.get_balanced_job_count() > maxnode:
            node.set_state(Status.OFFLINE)

def get_jobs_statistics(jobs: Dictionary, maxjob: int) -> Tuple[int, list[str], int, list[str], int, list[str], list[str], int, int, list[str], list[str]]:
    """
    Collect result data that can be used to generate a log/history of the
    programs execution, such as how many jobs ran, how many failed, etc.

    Parameters:
    jobs (Dictionary [int, job]) - A dictionary of jobs keyed by their id.
    maxjob (int): The maximum number of times a job can fail before its disabled
    in the job queue.

    Returns
        jobs_total_count (int): The total number of jobs that have been run.
        jobs_success_tests (ist[str]): A list of test cases that were successful.
        jobs_success_log (list[str]): A list of log messages associated with the
            successful test cases.
        jobs_failed_count (int): The total number of jobs that failed.
        jobs_failed_tests (list[str]): A list of test cases that failed.
        jobs_failed_log: (list[str]): A list of log messages associated with the
            failed test cases.
        jobs_rebalanced_count (int): The total number of jobs that had their
            hostnames rebalanced.
        jobs_failed_count_maxjob (int): The total number of jobs that failed
            multiple times (exceeded maxjob).
        jobs_failed_maxjob_tests (list[str]): A list of test cases that failed
            multiple times (exceeded maxjob).
        jobs_failed_maxjob_log (list[str]): A list of log messages associated with
            the failed test cases that exceeded maxjob.

    Example:
        >>>> stats = get_jobs_statistics(jobs, args.maxjob)
        >>>> print(f" {stats.jobs_success_count}, {stats.jobs_total_count}, etc)

    Raises:
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
    """
    This function takes in a dictionary of jobs and a maximum job failure count threshold, and returns a tuple containing:
        1. The number of jobs that have failed more than the maximum job failure count threshold.
        2. A list of test cases for those jobs that have failed more than the maximum job failure count threshold.
        3. A dictionary mapping each failed job's ID to its stdout and stderr messages.
        4. The number of jobs that were rebalanced after the maximum job failure count threshold was exceeded.

    Parameters:
        jobs (Dictionary): A dictionary mapping job IDs to Job objects.
        maxjob (int): The maximum number of times a job can fail before it is considered a failure.

    Returns:
        Tuple[int, list[str], dict[int, str], int]: A tuple containing the number of jobs that have
            failed more than the maximum job failure count threshold, a list of test cases for those
            jobs that have failed more than the maximum job failure count threshold, a dictionary
            mapping each failed job's ID to its stdout and stderr messages, and the number of jobs
            that were rebalanced after the maximum job failure count threshold was exceeded.
    """
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
    Runs a job (test case) on a managed node and ensures the job has the necessary
    managed node available. If not, it will manage the node and collect the statistics
    so that it can be properly run when a resource becomes available.

    Parameters
    id (int): Numerical ID assigned to a job.
    jobs (Dictionary): A dictionary of jobs, the ID is paired to a job.
        A job is a test cased designed to be run by pytest.
    nodes (Dictionary): Managed nodes that jobs will run on. These are z/OS
        managed nodes.
    timeout (int):The maximum time in seconds a job should run on z/OS for,
        default is 300 seconds.
    maxjob (int): The maximum number of times a job can fail before its
        disabled in the job queue
    bal (int): The count at which a job is balanced from one z/OS node
        to another for execution.
    extra (str): Extra commands passed to subprocess before pytest execution
    maxnode (int): The maximum number of times a node can fail to run a
        job before its set to 'offline' in the node queue.

    Returns:
    A tuple of (rc: int, message: str) is returned.
    rc (int):
        Return code 0 All tests were collected and passed successfully (pytest).
        Return code 1 Tests were collected and run but some of the tests failed (pytest).
        Return code 2 Test execution was interrupted by the user (pytest).
        Return code 3 Internal error happened while executing tests (pytest).
        Return code 4 pytest command line usage error (pytest).
        Return code 5 No tests were collected (pytest).
        Return code 6 No z/OS nodes available.
        Return code 7 Re-balancing of z/OS nodes were performed.
        Return code 8 Job has exceeded permitted job failures.
        Return code 9 Job has exceeded timeout.
        Return code 10 Job is being passed over because the node that
          is going to run the job is executing another job.

    message (str): Description and details of the jobs execution, contains
        return code, hostname, job id, etc. Informational and useful when
        understanding the job's lifecycle.
    """

    job = jobs.get(id)
    hostname = job.get_hostname()
    #id = str(job.get_id())
    elapsed = 0
    message = None
    rc = None
    result = None

    node_count_online = get_nodes_online_count(nodes)
    if node_count_online >0:
        node = nodes.get(hostname)
        # Temporary solution to avoid nodes running concurrent work loads
        if get_nodes_offline_count(nodes) == 0 and node.get_running_job_id() == -1:
            node.set_running_job_id(id)
            start_time = time.time()
            date_time = datetime.now().strftime("%H:%M:%S") #"%d/%m/%Y %H:%M:%S")
            thread_name = threading.current_thread().name
            try:
                # Build command and strategically map stdout and stderr so that both are mapped to stderr and the pytest rc goes to stdout.
                cmd =  f"{extra};{job.get_command()} 1>&2; echo $? >&1"
                result = subprocess.run([cmd], shell=True, capture_output=True, text=True, timeout=timeout)
                node.set_running_job_id(-1)
                job.set_elapsed_time(start_time)
                elapsed = job.get_elapsed_time()
                rc = int(result.stdout)

                if rc == 0:
                    job.set_rc(rc)
                    job.set_success()
                    rsn = "Job successfully executed."
                    message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    pytest_std_out_err = result.stderr
                    job.set_stdout(message, pytest_std_out_err, date_time)
                else:
                    job_failures = job.get_failure_count()

                    if job_failures >= maxjob:
                        rc = 8
                        job.set_rc(rc)
                        rsn = f"Test exceeded allowable failures={maxjob}."
                        message = f"Job id={id}, host={hostname}, start time={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    elif job_failures == bal:
                        rc = 7
                        job.set_rc(rc)
                        node.set_balanced_job_id(id)
                        set_node_offline(node, maxnode)
                        update_job_hostname(job)
                        rsn = f"Job is reassigned to managed node={job.get_hostname()}, job exceeded allowable balance={bal}."
                        message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    elif rc == 1:
                        job.set_rc(rc)
                        rsn = "Test case failed with an error."
                        message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    elif rc == 2:
                        job.set_rc(int(rc))
                        rsn = "Test case execution was interrupted by the user."
                        message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    elif rc == 3:
                        job.set_rc(int(rc))
                        rsn = "Internal error occurred while executing test."
                        message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    elif rc == 4:
                        job.set_rc(int(rc))
                        rsn = "Pytest command line usage error."
                        message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                    elif rc == 5:
                        job.set_rc(int(rc))
                        rsn = "No tests were collected."
                        message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"

                    # Only increment a job failure after evaluating all the RCs
                    job.increment_failure()

                    # Update the node with which jobs failed. A node has all assigned jobs so this ID can be used later for eval.
                    node.set_failure_job_id(id)
                    job.set_stdout_and_stderr(message, result.stderr, date_time)

            except subprocess.TimeoutExpired as timeout_err:
                node.set_running_job_id(-1)
                rc = 9
                job.set_rc(rc)
                job.set_elapsed_time(start_time)
                elapsed = job.get_elapsed_time()
                rsn = f"Job has exceeded subprocess timeout={str(timeout)}"
                message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={elapsed}, rc={rc}, thread={thread_name}, msg={rsn}"
                job.set_stdout_and_stderr(message, rsn, date_time)
                job.increment_failure()
                node.set_failure_job_id(id)
        else:
            rc = 10
            job.set_rc(rc)
            nodes_count = nodes.len()
            node_count_offline = get_nodes_offline_count(nodes)
            #other = node.get_assigned_jobs_as_dictionary().get(id)
            date_time = datetime.now().strftime("%H:%M:%S") #("%d/%m/%Y %H:%M:%S")
            rsn = f"Managed node is not able to execute job id={node.get_running_job_id()}, nodes={nodes_count}, offline={node_count_offline}, online={node_count_online}."
            message = f"Job id={id}, host={hostname}, start={date_time}, elapsed={0}, rc={rc}, msg={rsn}"
            node.set_running_job_id(-1) # Set it to false after message string
            node.set_balanced_job_id(id)
            #set_node_offline(node, maxnode)
            update_job_hostname(job)
    else:
        node.set_running_job_id(-1)
        rc = 6
        nodes_count = nodes.len()
        node_count_offline = get_nodes_offline_count(nodes)
        rsn = f"There are no managed nodes online to run jobs, nodes={nodes_count}, offline={node_count_offline}, online={node_count_online}."
        message = f"Job id={id}, host={hostname}, elapsed={job.get_elapsed_time()}, rc={rc}, msg={rsn}"
        job.set_stdout_and_stderr(message, rsn, date_time)
        job.increment_failure()
        node.set_failure_job_id(id)

    return rc, message


def runner(jobs: Dictionary, nodes: Dictionary, timeout: int, max: int, bal: int, extra: str, maxnode: int, workers: int) -> None:
    """
    Method creates an executor to run a job found in the jobs dictionary concurrently.
    This method is the key function that allows for concurrent execution of jobs.

    Parameters:
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

    with ThreadPoolExecutor(number_of_threads,thread_name_prefix='ansible-test') as executor:
        futures = [executor.submit(run, key, jobs, nodes, timeout, max, bal, extra, maxnode) for key, value in jobs.items() if not value.get_successful()]
        for future in as_completed(futures):
            # TODO: Do we need to do anything with the future result?
            rc, message = future.result()
            if future.exception() is not None:
                print(f"Executor exception occurred with error: {future.exception()}")
            elif future.cancelled():
                 print(f"Executor cancelled job, message = {message}")
            elif future.done():
                print(f"Executor message = {message}")
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

    Parameters:
        start_time (time): The time the test case has began. This is generally
        captured before a test is run.

    Returns:
        str: The elapsed time, how long it took a job to run. A string
            is returned representing the elapsed time, , eg 00:02:38.36
    """

    hours, rem = divmod(time.time() - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    elapsed = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)
    return elapsed

def print_job_logs(log: list[Tuple[str, str, str]], state: State) -> None:
    """
    Prints job logs to the console.

    Parameters:
        log (list[Tuple[str, str, str]]): A list of tuples containing job log information.
            state (State): The current state of the program
    """
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
    """
    Prints the test cases for a job.

    Parameters:
        tests (list[str]): A list of strings representing the test cases for a job.
        state (State): The current state of the job.
    """

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
    """
    Prints job logs to an HTML file using the PrettyTable library.

    Parameters:
        log (list[Tuple[str, str, str]]): A list of tuples containing job information.
            state (State): The current state of the program.
        replay (str): A string indicating whether the user wants to replay the logs or not.

    Returns:
        str: An HTML string generated from the job logs.
    """
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
    """
    Prints job tests to HTML.

    Parameters:
        tests (list[str]): A list of test cases.
        state (State): The current state of the job.
        replay (str): The replay ID of the job.
    """
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

def print_nodes(nodes: Dictionary) -> None:
    """
    Prints the names of all z/OS nodes in the provided dictionary.

    Parameters:
        nodes (Dictionary): A dictionary containing z/OS node names as keys and values.
    """
    if nodes.len() > 0:
        print(f"There are {nodes.len()} managed nodes serving this play.")
    for key, value in nodes.items():
        print(f"z/OS node = {key}")

def executor(args):
    """
    This function is responsible for executing the tests on the nodes. It takes in several arguments such as the user,
    the tests to be run, the maximum number of times a job can fail, and more. The function returns no value.

    Args:
        args (Namespace): A Namespace object containing various arguments passed to the script.
    """
    count_play = 1
    tests=args.tests
    count = 1
    replay = False
    while count_play <= args.replay:
        print(f"\n=================================\nPLAY {count_play} has been initialized.\n=================================")

        start_time_full_run = time.time()

        # Get a dictionary of all active zos_nodes to run tests on
        nodes = get_nodes(user = args.user, zoau = args.zoau, pyz = args.pyz, hostnames = args.hostnames)
        print_nodes(nodes)

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
    prog='ce.py',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''
        Examples
        --------
        1)  Execute a single test suite for up to 5 iterations for ibmuser with shared zoau and python installations.
            Note, usage of --tests "../tests/functional/modules/test_zos_tso_command_func.py"
            $ python3 ce.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 5\\
                    --tests "../tests/functional/modules/test_zos_tso_command_func.py"\\
                    --user "ibmuser"\\
                    --timeout 100

        2)  Execute a multiple test suites for up to 10 iterations for ibmuser with shared zoau and python installations.
            Note, usage of --tests "../tests/functional/modules/test_zos_tso_command_func.py,../tests/functional/modules/test_zos_find_func.py"
            $ python3 ce.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 10\\
                    --tests "../tests/functional/modules/test_zos_tso_command_func.py,../tests/functional/modules/test_zos_find_func.py"\\
                    --user "ibmuser"\\
                    --timeout 100

        3)  Execute a test suites in a directory for up to 4 iterations for ibmuser with shared zoau and python installations.
            Note, usage of --directories "../tests/functional/modules/,../tests/unit/"
            $ python3 ce.py\\
                    --pyz "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"\\
                    --zoau "/zoau/v1.3.1"\\
                    --itr 4\\
                    --directories "../tests/functional/modules/,../tests/unit/"\\
                    --user "ibmuser"\\
                    --timeout 100

        4)  Execute test suites in multiple directories for up to 5 iterations for ibmuser with shared zoau and python installations.
            Note, usage of "--directories "../tests/functional/modules/,../tests/unit/"
            $ python3 ce.py\\
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
            $ python3 ce.py\\
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
    # parser.add_argument('--pythonpath', type=str, help='Absolute path where to find Python modules (ZOAU modules).', required=True, metavar='<str>', default="")
    # parser.add_argument('--volumes', type=str, help='The volumes to use with the test cases that are to be executed.', required=False, metavar='<str,str>', default="222222,000000")

        # self._inventory.update({'pythonpath': '/zoau/v1.3.1/lib/3.10'})
        # self._extra_args.update({'extra_args':{'volumes':['222222','000000']}})
    # Mutually exclusive options
    group_tests_or_dirs = parser.add_argument_group('Mutually exclusive', 'Absolute path to test suites. For more than one, use a comma or space delimiter.')
    exclusive_group_or_tests = group_tests_or_dirs.add_mutually_exclusive_group(required=True)
    exclusive_group_or_tests.add_argument('--testsuite', type=str, help='Space or comma delimited test suites, must be absolute path(s)', required=False, metavar='<str,str>', default="")
    exclusive_group_or_tests.add_argument('--tests', type=str, help='Space or comma delimited directories containing test suites, must be absolute path(s)', required=False, metavar='<str,str>', default=None)
    args = parser.parse_args()

    # Evaluate
    # Maxjob should always be less than itr else it makes no sense
    # if int(args.maxjob) > int(args.itr):
    #     raise ValueError(f"Value '--maxjob' = {args.maxjob}, must be less than --itr = {args.itr}, else maxjob will have no effect.")

    if int(args.bal) > int(args.maxjob):
        raise ValueError(f"Value '--bal' = {args.bal}, must be less than --maxjob = {args.itr}, else balance will have no effect.")

    # TODO: Lets find a way to default the workers to the number of ECs
    # Execute/begin running the concurrency testing with the provided args.
    executor(args)

if __name__ == '__main__':
    main()
