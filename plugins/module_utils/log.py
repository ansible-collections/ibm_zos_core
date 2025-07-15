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

class SingletonLogger:
    _instance = None

    def __new__(cls, log_file_path=None):
        if cls._instance is None:
            if not log_file_path:
                raise ValueError("You must provide a log file path when initializing the logger for the first time.")
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._temp_file_path = log_file_path
            cls._instance._initialize_logger(log_file_path)
        return cls._instance

    def _initialize_logger(self, log_file_path):
        self.logger = logging.getLogger("AnsibleCoreLogger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file_path, encoding="cp1047")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - line %(lineno)d - %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger


    def get_log_file_path(self):
        return self._temp_file_path
