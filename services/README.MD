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
(ansible-test) ddimatos:[ ~/git/github/services/ibm_zos_core/services/examples ]python3 file_service.py
(1) EXAMPLE
(1.1) Create a dictionary representing the targeted host.
{'environment': {},
 'hostname': 'EC33017A.vmec.svl.ibm.com',
 'key_filename': '/Users/ddimatos/.ssh/id_dsa',
 'passphrase': 'changeme',
 'password': 'changeme',
 'port': 22,
 'username': 'omvsadm'}

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

