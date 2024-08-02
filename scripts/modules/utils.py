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

"""
Utility classes
"""

# pylint: disable=too-many-locals, modified-iterating-list, too-many-nested-blocks
# pylint: disable=too-many-branches, too-many-statements, line-too-long

from pathlib import Path
import subprocess


def get_test_cases(paths: str, skip: str = None) -> list[str]:
    """
    Returns a list of test cases suitable for pytest to execute. Can discover test
    cases from either a directory of test suites or a list of test suites. Will also
    remove any skipped tests if specified , wether a directory or a specific test.

    Parameters:
    paths (str): Absolute path of directories containing test suites or absolute
        path of individual test suites comma or space delimited.
        A directory of test cases is such that it contains test suites.
        A test suite is a collection of test cases in a file that starts with
        'test' and ends in '.py'.
    skip (str): (Optional) Absolute path of either test suites, or test cases.
        Test cases can be parametrized such they use the '::' syntax or not.
        Skip does not support directories.

    Returns:
    list[str] A list of strings containing a modified path to each test suite.
    The absolute path is truncated to meet the needs of pytest which starts at
    the `tests` directory.

    Raises:
    FileNotFoundError : If a test suite, test case or skipped test cannot be found.
    ValueError: If paths is not provided.

    Examples:
        Example collects all test cases for test suites`test_zos_job_submit_func.py` , `test_zos_copy_func.py`, all
        unit tests in directory `tests/unit/` then skips all tests in test suite `test_zos_copy_func.py`
        (for demonstration) and parametrized tests `test_zos_backup_restore_unit.py::test_invalid_operation[restorE]`
        and test_zoau_version_checker_unit.py::test_is_zoau_version_higher_than[True-sys_zoau1-1.2.1]/
        - get_test_cases(paths="/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_job_submit_func.py,\\
                /Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_copy_func.py,\\
                /Users/ddimatos/git/gh/ibm_zos_core/tests/unit/",\\
                skip="/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_copy_func.py,\\
                /Users/ddimatos/git/gh/ibm_zos_core/tests/unit/test_zos_backup_restore_unit.py::test_invalid_operation[restorE],\\
                /Users/ddimatos/git/gh/ibm_zos_core/tests/unit/test_zoau_version_checker_unit.py::test_is_zoau_version_higher_than[True-sys_zoau1-1.2.1]")
    """

    files =[]
    parametrized_test_cases = []
    parametrized_test_cases_filtered_test_suites = []
    parametrized_test_cases_filtered_test_cases = []
    parameterized_tests = []
    ignore_test_suites = []
    ignore_test_cases = []

    # Remove whitespace and replace CSV with single space delimiter.
    # Build a command that will yield all test cases including parametrized tests.
    cmd = ['pytest', '--collect-only', '-q']
    if paths:
        files = " ".join(paths.split())
        files = files.strip().replace(',', ' ').split()

        for file in files:
            file_path = Path(file)
            try:
                file_path.resolve(strict=True)
            except FileNotFoundError as e:
                raise FileNotFoundError(f'{file_path} does not exist.') from e
        cmd.extend(files)
    else:
        raise ValueError("Required files have not been provided.")

    cmd.append('| grep ::')
    cmd_str = ' '.join(cmd)

    # Run the pytest collect-only command and grep on '::' so to avoid warnings
    parametrized_test_cases = subprocess.run([cmd_str], shell=True, capture_output=True, text=True, check=False)
    # Remove duplicates in case test_suites or test_directories were repeated
    parametrized_test_cases = list(set(parametrized_test_cases.stdout.split('\n')))
    # Remove the trailing line feed from the list else it will leave an empty list index and error.
    parametrized_test_cases = list(filter(None, parametrized_test_cases))

    # Skip can take any input, but note that test suites which start with 'test' and in in `.py`
    # will supersede individual test cases. That is because if a test suite is being skipped it
    # it should remove all test cases that match that test suite, hence the skipped are put into
    # two buckets, 'ignore_test_cases' and 'ignore_test_suites' and 'ignore_test_suites' is evaluated
    # first.
    if skip:
        skip=" ".join(skip.split())
        skip = skip.strip().replace(',', ' ').split()
        for skipped in skip:
            if '::' in skipped:  # it's a test case
                skipped_path = Path(skipped.split('::')[0])
                try:
                    skipped_path.resolve(strict=True)
                except FileNotFoundError as e:
                    raise FileNotFoundError(f'{file_path} does not exist.') from e
                # Only retain the sub-str because that is what pytest collect-only will yield
                skipped = skipped.split("tests/")[1]
                ignore_test_cases.append(skipped)

            if skipped.endswith('.py'):  # it's a test suite
                skipped_path = Path(skipped)
                try:
                    skipped_path.resolve(strict=True)
                except FileNotFoundError as e:
                    raise FileNotFoundError(f'{file_path} does not exist.') from e
                # Only retain the sub-str because that is what pytest collect-only will yield
                skipped = skipped.split("tests/")[1]
                ignore_test_suites.append(skipped)

        # pytest --ignore,--deselect did not work as expected, will manually replicate the functionality
        # If a path is in ignore_test_suites, it supersedes any ignore_test_cases substrings.
        if len(ignore_test_suites) > 0:
            parametrized_test_cases_filtered_test_suites = [p for p in parametrized_test_cases if all(t not in p for t in ignore_test_suites)]
        if len(ignore_test_cases) > 0:
            parametrized_test_cases_filtered_test_cases = [p for p in parametrized_test_cases if all(t not in p for t in ignore_test_cases)]

        if len(parametrized_test_cases_filtered_test_suites) > 0 and len(parametrized_test_cases_filtered_test_cases) > 0:
            parametrized_test_cases_filtered_test_suites.extend(parametrized_test_cases_filtered_test_cases)
        elif len(parametrized_test_cases_filtered_test_cases) > 0:
            parameterized_tests = [f"tests/{parametrized}" for parametrized in parametrized_test_cases_filtered_test_cases]

        parameterized_tests = [f"tests/{parametrized}" for parametrized in parametrized_test_cases_filtered_test_suites]
        return parameterized_tests

    parameterized_tests = [f"tests/{parametrized}" for parametrized in parametrized_test_cases]

    return parameterized_tests

# Some adhoc testing until some test cases can be structured.
# def main():
#     print("Main")
#     # plist = get_test_cases(paths="/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_job_submit_func.py,\
#     #         /Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_copy_func.py,\
#     #         /Users/ddimatos/git/gh/ibm_zos_core/tests/unit/",\
#     #         skip="/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_copy_func.py,\
#     #         /Users/ddimatos/git/gh/ibm_zos_core/tests/unit/test_zos_backup_restore_unit.py::test_invalid_operation[restorE],\
#     #         /Users/ddimatos/git/gh/ibm_zos_core/tests/unit/test_zoau_version_checker_unit.py::test_is_zoau_version_higher_than[True-sys_zoau1-1.2.1]")
#     # plist = get_test_cases(paths="/Users/ddimatos/git/gh/ibm_zos_core/tests/unit/")
#     plist = get_test_cases(paths="/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_tso_command_func.py,/Users/ddimatos/git/gh/ibm_zos_core/tests/functional/modules/test_zos_operator_func.py")
#     print(str(plist))
# if __name__ == '__main__':
#     main()
