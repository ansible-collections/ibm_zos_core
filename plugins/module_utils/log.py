# Copyright (c) IBM Corporation 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging


class SingleLineFormatter(logging.Formatter):
    """
    Formatter that guarantees every log record is emitted on a single line.

    Log messages from ZOAU can contain embedded newlines, and a continuation
    line can start with '{' (for example a printed dict). When stderr is merged
    into stdout, as it is on a forced pseudo-TTY (ssh -tt), Ansible's
    _filter_non_json_lines treats the first line starting with '{' as the start
    of the module JSON result, and deserialization fails. Joining the output of
    str.splitlines() (the same splitting Ansible uses) with a literal "\\n"
    keeps every record on one line that starts with the formatter header.

    This only covers records emitted through this formatter. Output written
    directly to stderr or stdout is not affected.
    """

    def format(self, record):
        return "\\n".join(super().format(record).splitlines())


class SingletonLogger:
    _instance = None

    def __new__(cls):
        """
        Create (or return) the singleton instance of the logger.

        Ensures only one instance of SingletonLogger exists across the application.
        When the first instance is created, the logger is initialized.

        Returns:
            SingletonLogger: The single shared instance of the logger class.
        """
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """
        Initialize the logger configuration.

        Creates and configures a root logger with a StreamHandler
        that outputs logs to stdout. Sets a standard log format
        and INFO as the default logging level.
        """
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            stream_handler = logging.StreamHandler()
            formatter = SingleLineFormatter("ibm_zos_core %(asctime)s - %(levelname)s - %(module)s - %(funcName)s - line %(lineno)d - %(message)s")
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

    def get_logger(self, verbosity):
        """
        Retrieve the configured logger instance, optionally adjusting verbosity.

        If verbosity is 3 or higher, the logger level is set to DEBUG to include
        detailed debug messages. Otherwise, it remains at INFO level.

        Args:
            verbosity (int): The verbosity level controlling the log detail.
                - 0-2: INFO level (default)
                - 3 or higher: DEBUG level

        Returns:
            logging.Logger: The configured logger instance.
        """
        if verbosity >= 3:
            # By default logger will only log messages that are
            # warnings, error or critical. One thing is the
            # logger and another the handler, the logger might log certain
            # message but if the handler is not configured to the same level
            # the message won't show up.
            self.logger.setLevel(logging.DEBUG)
        return self.logger
