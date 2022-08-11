# List of items that could be beneficial

[] Make the cache a singleton  
[] Make the cache thread safe  
[] Continue to add test cases in all test suites  
[x] Introduce a wrapper class for services (eg services(file, data set, etc))  
[x] Run linter over all this code, adhere to PEP8  
[] Add python doc to all methods, classes  
[] Add call back to the response class so the caller has access to it, call backshould take the response object itself as input to extract the key, the key correspond to an entry in the cache, cache entry contains enough information to recreate the connection and deconstruct an artifact
[] set up a keyring for the sensitive values in the response class (password, etc)  
[] Many methods could be private, need to sweep the code to ensure we are protected and private when needed
[x] Update the connection to support env vars and test with ZOAU  
- Note: I checked /etc/ssh/sshd_config for its use of `AcceptEnv` and saw it it is not enabled and tried it anyhow with `AcceptEnv ZOAU_HOME` and tested, the result was the environment var was not set in the connection. I tried to configure get_pty=False/True and testing with (below) and did not work.
  request = Request("echo $ZOAU_HOME")
  (stdin, stdout, stderr) = client.exec_command(cmd, get_pty=False, environment=env)
  Paramiko channel does have a `set_environment_variable` but don't see the need to drop to Paramiko channel, seems to low, we can write a method to prefix commands with exports.

[] Refactor code into more subpackages for clarity
[] Create a static or config file that the tests cases can read to obtain global information such as the connection stats so we are not repeating this in all tests  
[] Test test_operations_create_file needs an update, remove the hard coded 1047 expectation  
[] Create a command service based on the existing model we have now, should cover zoau and other USS commands  
[] Study the various attributes for data sets , see if there is a common subset for all of them,unsure DataSetAttributes will work for all types  
[] implement a dump cache method that could dump the contents of the cache less secure content so that it can be later reused in a batch mode  
[] create  a bach mode that does not use the constructor in the connection module, idea here is there would be a way to iterate over the dump of the cache and recreate it in  batch mode.  
[] support for paramiko sftp - add this as a connection and service  
[] fix types.py:211:4: W0102: Dangerous default value {} as argument (dangerous-default-value), consider using None  
[] consider renaming type types.py:144:29: W0622: Redefining built-in 'type' (redefined-builtin)  
[] add an OS check in __init__.py so that we don't run a data set request on a non z/OS platform will require we update the code to use the os check.  
[] remove the name attribute from the response, its in *attributes and does not make sense for command service
