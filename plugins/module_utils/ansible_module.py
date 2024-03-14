# Copyright (c) IBM Corporation 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import shlex
import os
import re
import subprocess
import fcntl
import traceback
import tempfile
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import (
    PY2,
    PY3,
    binary_type,
    text_type,
)
from ansible.module_utils.six.moves import shlex_quote
from ansible.module_utils.common.text.converters import to_native, to_bytes, to_text
from ansible.module_utils.compat import selectors
from ansible.module_utils.common.parameters import (
    remove_values,
)

def heuristic_log_sanitize(data, no_log_values=None):
    ''' Remove strings that look like passwords from log messages '''
    # Currently filters:
    # user:pass@foo/whatever and http://username:pass@wherever/foo
    # This code has false positives and consumes parts of logs that are
    # not passwds

    # begin: start of a passwd containing string
    # end: end of a passwd containing string
    # sep: char between user and passwd
    # prev_begin: where in the overall string to start a search for
    #   a passwd
    # sep_search_end: where in the string to end a search for the sep
    data = to_native(data)

    output = []
    begin = len(data)
    prev_begin = begin
    sep = 1
    while sep:
        # Find the potential end of a passwd
        try:
            end = data.rindex('@', 0, begin)
        except ValueError:
            # No passwd in the rest of the data
            output.insert(0, data[0:begin])
            break

        # Search for the beginning of a passwd
        sep = None
        sep_search_end = end
        while not sep:
            # URL-style username+password
            try:
                begin = data.rindex('://', 0, sep_search_end)
            except ValueError:
                # No url style in the data, check for ssh style in the
                # rest of the string
                begin = 0
            # Search for separator
            try:
                sep = data.index(':', begin + 3, end)
            except ValueError:
                # No separator; choices:
                if begin == 0:
                    # Searched the whole string so there's no password
                    # here.  Return the remaining data
                    output.insert(0, data[0:prev_begin])
                    break
                # Search for a different beginning of the password field.
                sep_search_end = begin
                continue
        if sep:
            # Password was found; remove it.
            output.insert(0, data[end:prev_begin])
            output.insert(0, '********')
            output.insert(0, data[begin:sep + 1])
            prev_begin = begin

    output = ''.join(output)
    if no_log_values:
        output = remove_values(output, no_log_values)
    return output


class AnsibleModuleHelper(AnsibleModule):
    """Wrapper for AnsibleModule object that
    allows us to use AnsibleModule methods like
    run_command() without specifying a valid argument
    spec.
    """

    def fail_json(self, **kwargs):
        if "Unsupported parameters for" in kwargs.get("msg", ""):
            return
        else:
            super().fail_json(**kwargs)

    def run_command(self, args, check_rc=False, close_fds=True, executable=None, data=None, binary_data=False, path_prefix=None, cwd=None,
                    use_unsafe_shell=False, prompt_regex=None, environ_update=None, umask=None, encoding='utf-8', errors='surrogate_or_strict',
                    expand_user_and_vars=True, pass_fds=None, before_communicate_callback=None, ignore_invalid_cwd=True, handle_exceptions=True):
        '''
        Execute a command, returns rc, stdout, and stderr.

        The mechanism of this method for reading stdout and stderr differs from
        that of CPython subprocess.Popen.communicate, in that this method will
        stop reading once the spawned command has exited and stdout and stderr
        have been consumed, as opposed to waiting until stdout/stderr are
        closed. This can be an important distinction, when taken into account
        that a forked or backgrounded process may hold stdout or stderr open
        for longer than the spawned command.

        :arg args: is the command to run
            * If args is a list, the command will be run with shell=False.
            * If args is a string and use_unsafe_shell=False it will split args to a list and run with shell=False
            * If args is a string and use_unsafe_shell=True it runs with shell=True.
        :kw check_rc: Whether to call fail_json in case of non zero RC.
            Default False
        :kw close_fds: See documentation for subprocess.Popen(). Default True
        :kw executable: See documentation for subprocess.Popen(). Default None
        :kw data: If given, information to write to the stdin of the command
        :kw binary_data: If False, append a newline to the data.  Default False
        :kw path_prefix: If given, additional path to find the command in.
            This adds to the PATH environment variable so helper commands in
            the same directory can also be found
        :kw cwd: If given, working directory to run the command inside
        :kw use_unsafe_shell: See `args` parameter.  Default False
        :kw prompt_regex: Regex string (not a compiled regex) which can be
            used to detect prompts in the stdout which would otherwise cause
            the execution to hang (especially if no input data is specified)
        :kw environ_update: dictionary to *update* environ variables with
        :kw umask: Umask to be used when running the command. Default None
        :kw encoding: Since we return native strings, on python3 we need to
            know the encoding to use to transform from bytes to text.  If you
            want to always get bytes back, use encoding=None.  The default is
            "utf-8".  This does not affect transformation of strings given as
            args.
        :kw errors: Since we return native strings, on python3 we need to
            transform stdout and stderr from bytes to text.  If the bytes are
            undecodable in the ``encoding`` specified, then use this error
            handler to deal with them.  The default is ``surrogate_or_strict``
            which means that the bytes will be decoded using the
            surrogateescape error handler if available (available on all
            python3 versions we support) otherwise a UnicodeError traceback
            will be raised.  This does not affect transformations of strings
            given as args.
        :kw expand_user_and_vars: When ``use_unsafe_shell=False`` this argument
            dictates whether ``~`` is expanded in paths and environment variables
            are expanded before running the command. When ``True`` a string such as
            ``$SHELL`` will be expanded regardless of escaping. When ``False`` and
            ``use_unsafe_shell=False`` no path or variable expansion will be done.
        :kw pass_fds: When running on Python 3 this argument
            dictates which file descriptors should be passed
            to an underlying ``Popen`` constructor. On Python 2, this will
            set ``close_fds`` to False.
        :kw before_communicate_callback: This function will be called
            after ``Popen`` object will be created
            but before communicating to the process.
            (``Popen`` object will be passed to callback as a first argument)
        :kw ignore_invalid_cwd: This flag indicates whether an invalid ``cwd``
            (non-existent or not a directory) should be ignored or should raise
            an exception.
        :kw handle_exceptions: This flag indicates whether an exception will
            be handled inline and issue a failed_json or if the caller should
            handle it.
        :returns: A 3-tuple of return code (integer), stdout (native string),
            and stderr (native string).  On python2, stdout and stderr are both
            byte strings.  On python3, stdout and stderr are text strings converted
            according to the encoding and errors parameters.  If you want byte
            strings on python3, use encoding=None to turn decoding to text off.
        '''
        cmd_log = ""
        stdin_close_success = True

        # used by clean args later on
        self._clean = None

        if not isinstance(args, (list, binary_type, text_type)):
            msg = "Argument 'args' to run_command must be list or string"
            self.fail_json(rc=257, cmd=args, msg=msg)

        shell = False
        if use_unsafe_shell:

            # stringify args for unsafe/direct shell usage
            if isinstance(args, list):
                args = b" ".join([to_bytes(shlex_quote(x), errors='surrogate_or_strict') for x in args])
            else:
                args = to_bytes(args, errors='surrogate_or_strict')

            # not set explicitly, check if set by controller
            if executable:
                executable = to_bytes(executable, errors='surrogate_or_strict')
                args = [executable, b'-c', args]
            elif self._shell not in (None, '/bin/sh'):
                args = [to_bytes(self._shell, errors='surrogate_or_strict'), b'-c', args]
            else:
                shell = True
        else:
            # ensure args are a list
            if isinstance(args, (binary_type, text_type)):
                # On python2.6 and below, shlex has problems with text type
                # On python3, shlex needs a text type.
                if PY2:
                    args = to_bytes(args, errors='surrogate_or_strict')
                elif PY3:
                    args = to_text(args, errors='surrogateescape')
                args = shlex.split(args)

            # expand ``~`` in paths, and all environment vars
            if expand_user_and_vars:
                args = [to_bytes(os.path.expanduser(os.path.expandvars(x)), errors='surrogate_or_strict') for x in args if x is not None]
            else:
                args = [to_bytes(x, errors='surrogate_or_strict') for x in args if x is not None]

        cmd_log = "{0}\nArgs: {1}.".format(cmd_log, args)

        prompt_re = None
        if prompt_regex:
            if isinstance(prompt_regex, text_type):
                if PY3:
                    prompt_regex = to_bytes(prompt_regex, errors='surrogateescape')
                elif PY2:
                    prompt_regex = to_bytes(prompt_regex, errors='surrogate_or_strict')
            try:
                prompt_re = re.compile(prompt_regex, re.MULTILINE)
            except re.error:
                self.fail_json(msg="invalid prompt regular expression given to run_command")

        rc = 0
        msg = None
        st_in = None

        env = os.environ.copy()
        # We can set this from both an attribute and per call
        env.update(self.run_command_environ_update or {})
        env.update(environ_update or {})
        if path_prefix:
            path = env.get('PATH', '')
            if path:
                env['PATH'] = "%s:%s" % (path_prefix, path)
            else:
                env['PATH'] = path_prefix

        # If using test-module.py and explode, the remote lib path will resemble:
        #   /tmp/test_module_scratch/debug_dir/ansible/module_utils/basic.py
        # If using ansible or ansible-playbook with a remote system:
        #   /tmp/ansible_vmweLQ/ansible_modlib.zip/ansible/module_utils/basic.py

        # Clean out python paths set by ansiballz
        if 'PYTHONPATH' in env:
            pypaths = [x for x in env['PYTHONPATH'].split(':')
                       if x and
                       not x.endswith('/ansible_modlib.zip') and
                       not x.endswith('/debug_dir')]
            if pypaths and any(pypaths):
                env['PYTHONPATH'] = ':'.join(pypaths)

        cmd_log = "{0}\nEnv: {1}.".format(cmd_log, env)

        if data:
            st_in = subprocess.PIPE

        def preexec():
            self._restore_signal_handlers()
            if umask:
                os.umask(umask)

        kwargs = dict(
            executable=executable,
            shell=shell,
            close_fds=close_fds,
            stdin=st_in,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=preexec,
            env=env,
        )
        if PY3 and pass_fds:
            kwargs["pass_fds"] = pass_fds
        elif PY2 and pass_fds:
            kwargs['close_fds'] = False

        # make sure we're in the right working directory
        if cwd:
            cwd = to_bytes(os.path.abspath(os.path.expanduser(cwd)), errors='surrogate_or_strict')
            if os.path.isdir(cwd):
                kwargs['cwd'] = cwd
            elif not ignore_invalid_cwd:
                self.fail_json(msg="Provided cwd is not a valid directory: %s" % cwd)

        cmd_log = "{0}\nCWD: {1}.".format(cmd_log, cwd)

        try:
            if self._debug:
                self.log('Executing: ' + self._clean_args(args))
            cmd = subprocess.Popen(args, **kwargs)
            if before_communicate_callback:
                before_communicate_callback(cmd)

            stdout = b''
            stderr = b''

            # Mirror the CPython subprocess logic and preference for the selector to use.
            # poll/select have the advantage of not requiring any extra file
            # descriptor, contrarily to epoll/kqueue (also, they require a single
            # syscall).
            if hasattr(selectors, 'PollSelector'):
                selector = selectors.PollSelector()
            else:
                selector = selectors.SelectSelector()

            if data:
                if not binary_data:
                    data += '\n'
                if isinstance(data, text_type):
                    data = to_bytes(data)

            selector.register(cmd.stdout, selectors.EVENT_READ)
            selector.register(cmd.stderr, selectors.EVENT_READ)

            if os.name == 'posix':
                fcntl.fcntl(cmd.stdout.fileno(), fcntl.F_SETFL, fcntl.fcntl(cmd.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK)
                fcntl.fcntl(cmd.stderr.fileno(), fcntl.F_SETFL, fcntl.fcntl(cmd.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK)

            if data:
                cmd_log = "{0}\nData: {1}".format(cmd_log, data)
                cmd.stdin.write(data)
                try:
                    # Only closing the stream when it is still open, to avoid latency issues when a system
                    # is overwhelmed.
                    if not cmd.stdin.closed:
                        cmd.stdin.close()
                    else:
                        cmd_log = "{0}\nThe STDIN stream was closed by run_command.".format(cmd_log)
                except BrokenPipeError:
                    # run_command() will try to ignore broken pipe errors, just like Popen.communicate()
                    # does in base Python.
                    # Probably not needed as we're already checking that we're not closing a dead stream,
                    # but just to be sure.
                    stdin_close_success = False
                    cmd_log = "{0}\nrun_command encountered a BrokenPipeError.".format(cmd_log)

            while True:
                # A timeout of 1 is both a little short and a little long.
                # With None we could deadlock, with a lower value we would
                # waste cycles. As it is, this is a mild inconvenience if
                # we need to exit, and likely doesn't waste too many cycles
                events = selector.select(1)
                stdout_changed = False
                for key, event in events:
                    b_chunk = key.fileobj.read(32768)
                    if not b_chunk:
                        selector.unregister(key.fileobj)
                    elif key.fileobj == cmd.stdout:
                        stdout += b_chunk
                        stdout_changed = True
                    elif key.fileobj == cmd.stderr:
                        stderr += b_chunk

                # if we're checking for prompts, do it now, but only if stdout
                # actually changed since the last loop
                if prompt_re and stdout_changed and prompt_re.search(stdout) and not data:
                    if encoding:
                        stdout = to_native(stdout, encoding=encoding, errors=errors)

                    if not stdin_close_success:
                        log_fd, log_file_path = tempfile.mkstemp(suffix=time.time(), prefix="ibm_zos_core", text=True)
                        with os.fdopen(log_fd, "w", encoding="cp1047") as log:
                            log.write(cmd_log)

                    return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")

                # break out if no pipes are left to read or the pipes are completely read
                # and the process is terminated
                if (not events or not selector.get_map()) and cmd.poll() is not None:
                    break

                # No pipes are left to read but process is not yet terminated
                # Only then it is safe to wait for the process to be finished
                # NOTE: Actually cmd.poll() is always None here if no selectors are left
                elif not selector.get_map() and cmd.poll() is None:
                    cmd.wait()
                    # The process is terminated. Since no pipes to read from are
                    # left, there is no need to call select() again.
                    break

            cmd.stdout.close()
            cmd.stderr.close()
            selector.close()

            cmd_log = "{0}\nSTDOUT: {1}".format(cmd_log, stdout)
            cmd_log = "{0}\nSTDERR: {1}".format(cmd_log, stderr)

            rc = cmd.returncode
        except (OSError, IOError) as e:
            self.log("Error Executing CMD:%s Exception:%s" % (self._clean_args(args), to_native(e)))
            if handle_exceptions:
                self.fail_json(rc=e.errno, stdout=b'', stderr=b'', msg=to_native(e), cmd=self._clean_args(args))
            else:
                raise e
        except Exception as e:
            self.log("Error Executing CMD:%s Exception:%s" % (self._clean_args(args), to_native(traceback.format_exc())))
            if handle_exceptions:
                self.fail_json(rc=257, stdout=b'', stderr=b'', msg=to_native(e), exception=traceback.format_exc(), cmd=self._clean_args(args))
            else:
                raise e

        if rc != 0 and check_rc:
            msg = heuristic_log_sanitize(stderr.rstrip(), self.no_log_values)
            self.fail_json(cmd=self._clean_args(args), rc=rc, stdout=stdout, stderr=stderr, msg=msg)

        if not stdin_close_success:
            log_fd, log_file_path = tempfile.mkstemp(suffix=time.time(), prefix="ibm_zos_core", text=True)
            with os.fdopen(log_fd, "w", encoding="cp1047") as log:
                log.write(cmd_log)

        if encoding is not None:
            return (rc, to_native(stdout, encoding=encoding, errors=errors),
                    to_native(stderr, encoding=encoding, errors=errors))

        return (rc, stdout, stderr)
