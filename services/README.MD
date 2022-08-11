# Services Framework

This framework is intended to alleviate the effort needed for  test cases to
create artifacts such as files and data sets with specific attributes such as
record length, size and content to name a few examples.

The framework accepts a target to create the requested artifacts then manages
the lifecycle and destructs them.

## Examples
See <project>/examples and run with `python3 example.py`

## Notes

### Pytest
Pytest has some expected and known work items to follow up on, there are also
a number of ignored tests configured in `.pylintrc` that we may want to review
after some time, these are:
    [ C0114, E0401, C0103, R0902, R0913, C0114, E0401, W0621, R0903, C0413]

```
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services ]find . -type f -name "*.py" | xargs pylint
************* Module ibm_zos_core.services.operations.types
operations/types.py:144:29: W0622: Redefining built-in 'type' (redefined-builtin)
operations/types.py:211:4: W0102: Dangerous default value {} as argument (dangerous-default-value)
************* Module ibm_zos_core.services.operations.connection
operations/connection.py:123:0: C0303: Trailing whitespace (trailing-whitespace)
operations/connection.py:120:13: W0612: Unused variable 'stdin' (unused-variable)

------------------------------------------------------------------
Your code has been rated at 9.92/10 (previous run: 4.43/10, +5.49)
```

### Run the unit tests
```
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services ]cd tests/
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services/tests ]pytest *.py
==================================================== test session starts ====================================================
platform darwin -- Python 3.8.2, pytest-5.3.0, py-1.11.0, pluggy-0.13.1
ansible: 2.9.27
rootdir: /Users/ddimatos/git/github/services/ibm_zos_core/services/tests
plugins: ansible-2.2.2, mock-1.12.1
collected 23 items

test_cache.py ..........                                                                                              [ 21%]
test_connection.py ..ssssss..s.                                                                                       [ 73%]
test_operations.py .

============================================== 16 passed, 7 skipped in 13.15s ===============================================
```

Run the examples:
```
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services/tests ]cd ../examples/
```

Run the file creation service:
```
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services/examples ]python3 file_service.py
(1) EXAMPLE
(1.1) Create a dictionary representing the targeted host.
(1.2) Initialize the services with dictionary.
(1.3) Create a file on the targeted host.
(1.3) Result dictionary returned.
{'attributes': {'encoding': 'IBM-1047',
                'mode': {'group': 'R-X', 'other': '---', 'owner': 'RWX'},
                'name': 'test_1.txt',
                'path': '/tmp/',
                'record_length': 80,
                'size': 100,
                'size_type': 'GB',
                'status_group': 'SOME_GROUP',
                'status_owner': 'SOME_OWNER'},
 'hostname': 'ibm.com',
 'key': '9UkPV9ETasHhPw',
 'key_filename': 'ENCRYPTED_FILENAME',
 'name': 'test_1.txt',
 'passphrase': 'ENCRYPTED_PHRASE',
 'password': 'ENCRYPTED_PASS',
 'port': 22,
 'rc': 0,
 'stderr': '',
 'stdout': '',
 'time_created': datetime.datetime(2022, 8, 10, 16, 53, 58, 605992),
 'type': 'FILE',
 'username': 'ENCRYPTED_USER'}

(2) EXAMPLE
(2.1) Initialize the services with host arguments.
(2.3) Create a file on the targeted host.
(2.3) Result returned.
{'attributes': {'encoding': 'IBM-1047',
                'mode': {'group': 'R-X', 'other': '---', 'owner': 'RWX'},
                'name': 'test_2.txt',
                'path': '/tmp/',
                'record_length': 80,
                'size': 100,
                'size_type': 'GB',
                'status_group': 'SOME_GROUP',
                'status_owner': 'SOME_OWNER'},
 'hostname': 'ibm.com',
 'key': '-gBKddgmP9PyCg',
 'key_filename': 'ENCRYPTED_FILENAME',
 'name': 'test_2.txt',
 'passphrase': 'ENCRYPTED_PHRASE',
 'password': 'ENCRYPTED_PASS',
 'port': 22,
 'rc': 0,
 'stderr': '',
 'stdout': '',
 'time_created': datetime.datetime(2022, 8, 10, 16, 54, 1, 939926),
 'type': 'FILE',
 'username': 'ENCRYPTED_USER'}
(ansible-test) ddimatos:[ ~/git/github/services/ib
```

Run the command service:
```
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services/examples ]python3 command_service.py
(1) EXAMPLE
(1.1) Create a dictionary representing the targeted host.
(1.2) Initialize the services with dictionary.
(1.3) Run a command on the targeted host.
(1.4) Result dictionary returned.
{'attributes': None,
 'hostname': 'ibm.com',
 'key': 'XdleA6rFARLUOw',
 'key_filename': 'ENCRYPTED_FILENAME',
 'name': 'raw',
 'passphrase': 'ENCRYPTED_PHRASE',
 'password': 'ENCRYPTED_PASS',
 'port': 22,
 'rc': 0,
 'stderr': [],
 'stdout': ['total 352',
            'drwxr-xr-x  19 BPXROOT  SYS1        8192 Aug 10 14:10 .',
            'drwxr-xr-x  19 BPXROOT  SYS1        8192 Aug 10 14:10 ..',
            '-rw-------   1 BPXROOT  SYS1        1809 Aug 10 17:12 .sh_history',
            'drwx------   2 BPXROOT  SYS1        8192 Aug  8 06:08 .ssh',
            'drwxr-xr-x   6 BPXROOT  OMVSGRP     8192 Apr 27  2017 SYSTEM',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Aug 10 14:10 allpython',
            'drwxr-xr-x   4 BPXROOT  OMVSGRP     8192 Feb 10  2022 bin',
            '-rw-r--r--   1 BPXROOT  SYS1       18240 Nov 10  2020 clcivpgm.o',
            'lrwxrwxrwx   1 BPXROOT  OMVSGRP       12 May  9  2019 dev -> '
            '$SYSNAME/dev',
            'drwxr-xr-x  18 BPXROOT  OMVSGRP     8192 Oct 22  2020 etc',
            'drwxr-xr-x   4 BPXROOT  OMVSGRP     8192 Nov 22  2018 global',
            'drwxr-xr-x   2 BPXROOT  OMVSGRP     8192 Mar  8 16:49 lib',
            'drwxr-xr-x   2 BPXROOT  OMVSGRP        0 Apr  3  2019 opt',
            'drwxr-xr-x   5 BPXROOT  SYS1        8192 Sep 18  2020 python',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Sep 18  2020 python2',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Oct  7  2020 python3',
            'drwxr-xr-x   4 BPXROOT  OMVSGRP     8192 Aug  4  2021 samples',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Jun 11  2019 temp',
            'lrwxrwxrwx   1 BPXROOT  OMVSGRP       12 May  9  2019 tmp -> '
            '$SYSNAME/tmp',
            'drwxr-xr-x  29 BPXROOT  OMVSGRP     8192 May  2  2019 u',
            'drwxr-xr-x  10 BPXROOT  OMVSGRP     8192 Apr 27  2017 usr',
            'drwxrwxrwt  18 BPXROOT  OMVSGRP     8192 Aug  8 04:55 var',
            'drwxr-xr-x  17 BPXROOT  SYS1        8192 Aug 10 14:09 zoau'],
 'time_created': datetime.datetime(2022, 8, 10, 23, 23, 20, 603966),
 'type': 'COMMAND',
 'username': 'ENCRYPTED_USER'}

(2) EXAMPLE
(2.1) Initialize the services with host arguments.
(2.2) Run a command on the targeted host.
(2.3) Result dictionary returned.
{'attributes': None,
 'hostname': 'ibm.com',
 'key': 'KxpRIktWpPyL_g',
 'key_filename': 'ENCRYPTED_FILENAME',
 'name': 'raw',
 'passphrase': 'ENCRYPTED_PHRASE',
 'password': 'ENCRYPTED_PASS',
 'port': 22,
 'rc': 0,
 'stderr': [],
 'stdout': ['command 1',
            'total 352',
            'drwxr-xr-x  19 BPXROOT  SYS1        8192 Aug 10 14:10 .',
            'drwxr-xr-x  19 BPXROOT  SYS1        8192 Aug 10 14:10 ..',
            '-rw-------   1 BPXROOT  SYS1        1809 Aug 10 17:12 .sh_history',
            'drwx------   2 BPXROOT  SYS1        8192 Aug  8 06:08 .ssh',
            'drwxr-xr-x   6 BPXROOT  OMVSGRP     8192 Apr 27  2017 SYSTEM',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Aug 10 14:10 allpython',
            'drwxr-xr-x   4 BPXROOT  OMVSGRP     8192 Feb 10  2022 bin',
            '-rw-r--r--   1 BPXROOT  SYS1       18240 Nov 10  2020 clcivpgm.o',
            'lrwxrwxrwx   1 BPXROOT  OMVSGRP       12 May  9  2019 dev -> '
            '$SYSNAME/dev',
            'drwxr-xr-x  18 BPXROOT  OMVSGRP     8192 Oct 22  2020 etc',
            'drwxr-xr-x   4 BPXROOT  OMVSGRP     8192 Nov 22  2018 global',
            'drwxr-xr-x   2 BPXROOT  OMVSGRP     8192 Mar  8 16:49 lib',
            'drwxr-xr-x   2 BPXROOT  OMVSGRP        0 Apr  3  2019 opt',
            'drwxr-xr-x   5 BPXROOT  SYS1        8192 Sep 18  2020 python',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Sep 18  2020 python2',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Oct  7  2020 python3',
            'drwxr-xr-x   4 BPXROOT  OMVSGRP     8192 Aug  4  2021 samples',
            'drwxr-xr-x   3 BPXROOT  SYS1        8192 Jun 11  2019 temp',
            'lrwxrwxrwx   1 BPXROOT  OMVSGRP       12 May  9  2019 tmp -> '
            '$SYSNAME/tmp',
            'drwxr-xr-x  29 BPXROOT  OMVSGRP     8192 May  2  2019 u',
            'drwxr-xr-x  10 BPXROOT  OMVSGRP     8192 Apr 27  2017 usr',
            'drwxrwxrwt  18 BPXROOT  OMVSGRP     8192 Aug  8 04:55 var',
            'drwxr-xr-x  17 BPXROOT  SYS1        8192 Aug 10 14:09 zoau',
            'command                 2',
            'SYSTEM      dev         opt         samples     usr',
            'allpython   etc         python      temp        var',
            'bin         global      python2     tmp         zoau',
            'clcivpgm.o  lib         python3     u           ',
            'command 3',
            'Thu Aug 11 06:23:23  2022'],
 'time_created': datetime.datetime(2022, 8, 10, 23, 23, 23, 478080),
 'type': 'COMMAND',
 'username': 'ENCRYPTED_USER'}

(3) EXAMPLE
(3.1) Initialize the services with dictionary and environment variables.
(3.2) Run a command on the targeted host.
(3.3) Result dictionary returned.
{'attributes': None,
 'hostname': 'ibm.com',
 'key': '4sjKOdSGx5nc5Q',
 'key_filename': 'ENCRYPTED_FILENAME',
 'name': 'raw',
 'passphrase': 'ENCRYPTED_PHRASE',
 'password': 'ENCRYPTED_PASS',
 'port': 22,
 'rc': 0,
 'stderr': [],
 'stdout': ['2021/08/05 22:12:58 CUT V1.2.0'],
 'time_created': datetime.datetime(2022, 8, 10, 23, 23, 28, 961742),
 'type': 'COMMAND',
 'username': 'ENCRYPTED_USER'}

(3) EXAMPLE
(3.1) Initialize the services with dictionary and environment variables.
(3.2) Run a command on the targeted host.
(3.3) Result dictionary returned.
{'attributes': None,
 'hostname': 'ibm.com',
 'key': 'zB8YmroNamI6JQ',
 'key_filename': 'ENCRYPTED_FILENAME',
 'name': 'raw',
 'passphrase': 'ENCRYPTED_PHRASE',
 'password': 'ENCRYPTED_PASS',
 'port': 22,
 'rc': 0,
 'stderr': [],
 'stdout': ['SYSDSP   SSHSTRT  JOB00080 CC       0000',
            'SYSDSP   SSHSETUP JOB00079 CC       0000',
            'RACIMS   LOCALDSN JOB00049 CC       0000',
            'RACIMS   DEFNVSAM JOB00022 CC       0000',
            'RACF000  IRRDPTAB STC00004 CC       0000',
            '++++++++ $MASCOMM STC00001 ?        ?',
            'USRT001  USRT001  TSU00088 AC       ?',
            'USRT001  BPXAS    STC00252 AC       ?',
            'USRT001  BPXAS    STC00251 AC       ?'],
 'time_created': datetime.datetime(2022, 8, 10, 23, 23, 32, 375927),
 'type': 'COMMAND',
 'username': 'ENCRYPTED_USER'}
```
