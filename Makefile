# ==============================================================================
# © Copyright IBM Corporation 2022
#
# Makefile is used to assist with development tasks that can be a bit tedious to
# create and often recreate. This provides a simple repeatable means to perform
# regular development actions and encourages better practices by simplifying
# tasks
# This makefile relies heavily on a paired shell script `make.env` which should
# not be renamed. The contents of the `make.env` are encrypted to adhere to
# coporate operational requiements. The format will be published should you wish
# to edit or create your own version of `make.env`. If you need to edit the
# `make.env` be sure to use this makefile to manage it by:
#    (1) make decrypt <enter password at prompt>
#    (2) vi/edit the contents as needed
#    (3) make encrypt <enter same password used to decrypt
# The first time general execution order is:
#    (1) make vsetup
#    (2) make build
#    (3) make bandit sev=ll
#    (4) make sanity version=3.8
#    (5) make test host=<val> python=<val> zoau=<val> name=<val> debug=true
# ==============================================================================

# ==============================================================================
# GLOBAL VARS
# ==============================================================================

CURR_DIR := $(shell pwd)
WHO := $(shell whoami)
HOST_PYTHON = python3
VENV = venv
VENV_BIN=$(VENV)/bin
ZOS_PYTHON_DEFAULT=3.8
ZOAU_DEFAULT=1.1.1
# Test if docker is running
DOCKER_INFO := $(shell docker info> /dev/null 2>&1;echo $$?)
divider="===================================================================="

.PHONY: help Makefile

## Encrypt the `make.env` configuration file as `make.env.encrypt` with user specified password
## Example:
##     $ make encrypt
## Note: This is not a common operation, unless you tend to edit the configuration, avoid using this feature.
encrypt:
	@# --------------------------------------------------------------------------
	@# Check configuration exits
	@# --------------------------------------------------------------------------
	@if test ! -e make.env; then \
	    echo "No configuration file 'make.env' found in $(CURR_DIR) "; \
		exit 1; \
	fi

	@openssl bf -a -in make.env > make.env.encrypt
	@rm -f make.env

## Decrypt the `make.env.encrypt` configuration file as `make.env` with user specified password
## Example:
##     $ make decrypt
decrypt:
	@# --------------------------------------------------------------------------
	@# Check configuration exits
	@# --------------------------------------------------------------------------
	@if test ! -e make.env.encrypt; then \
	    echo "No configuration file 'make.env.encrypt' found in $(CURR_DIR) "; \
		exit 1; \
	fi

	@openssl bf -d -a -in make.env.encrypt > make.env
	@chmod 700 make.env
	@rm -f make.env.encrypt

# ==============================================================================
# Set up your venv, currently its hard coded to `venv` and designed to look first
# to see if you have one before trying to create one.
# @test -d $(VENV) || $(HOST_PYTHON) -m venv $(VENV)
# ==============================================================================
## Create a python virtual environment (venv) based on the systems python3
## $ make vsetup
vsetup:

	@if test ! -e $(VENV)/config.yml; then \
	    echo "No configuration created in $(VENV)/config.yml "; \
	fi

	@if test ! -d $(VENV); then \
		echo $(divider); \
		echo "Creating python virtual environment 'venv'."; \
		echo $(divider); \
		$(HOST_PYTHON) -m venv $(VENV); \
	else \
		echo "Virtual environment already exists, no changes made."; \
	fi

	@if test ! -e $(VENV)/make.env; then \
		echo $(divider); \
		echo "Decrypting configuration file into $(VENV)/make.env."; \
		echo $(divider); \
		make decrypt; \
		mv make.env $(VENV)/; \
	else \
		echo "Configuration file $(VENV)/make.env already exists, no changes made."; \
	fi

	@if test ! -e $(VENV)/requirements.txt; then \
		echo $(divider); \
		echo "Installing python requirements into 'venv'."; \
		echo $(divider); \
		echo $$(${VENV}/./make.env --req)>${VENV}/requirements.txt; \
		. $(VENV_BIN)/activate && pip install -r $(VENV)/requirements.txt; \
	else \
		echo "Requirements file $(VENV)/requirements.txt already exists, no new packages installed."; \
	fi

# ==============================================================================
# Normally you don't need to activate your venv, but should you want to, you can
# ==============================================================================
## Start the venv if you plan to work in a python virtual environment
## Example:
##     $ make vstart
vstart:
	@echo $(divider)
	@echo "Activating python virtual environment 'venv', use 'vstop' to deactivate."
	@echo $(divider)
	@. $(VENV_BIN)/activate; exec /bin/sh -i

# ==============================================================================
# Deactivate your venv
# ==============================================================================
## Deactivate (stop) the venv
## Example:
##     $ make vstop
vstop:
	@echo $(divider)
	@echo "Deactivate python virtual environment 'venv'."
	@echo $(divider)
	@. deactivate

# ==============================================================================
# Build the current collection based on the git branch local to the computer.
# Currently, venv's only manage python packages, colleciton installation is managed
# with paths, if we wwanted to  install it in the venv to not dirty the host, we
# could try building a similar command to pythons venv:
# ansible-galaxy -vv collection install --force -p venv/lib/python3.8/site-packages/ansible_collections
# ==============================================================================
## Build and installa collection of the current branch checked out
## Example:
##     $ make build
build:
	@. $(VENV_BIN)/activate && rm -rf ibm-ibm_zos_core-*.tar.gz && \
		ansible-galaxy collection build && \
			ansible-galaxy collection install -f ibm-ibm_zos_core-*

# ==============================================================================
# Run functional tests:
# ==============================================================================
## Run collection functional tests inside the python virtual environment (venv)
## Options:
##     host - z/OS managed node to run test cases, no selection will default to
##            a system registerd to your user name, see make.env
##     python - IBM enterprise python version, choices are 3.8, 3.9, 3.10, 3.11
##              no selection defauls to 3.8
##     zoau - Z Open Automation Utilites to use with the collection, choices are 1.0.3, 1.1.1, 1.2.0, 1.2.1
##            no selection defaults to 1.1.1
##     name - the absoulte path to a particluar test case to run, no selection
##            will default to all test cases running.
##     debug - enable debug for pytest (-s), any value will result in true enabling
##             debug, default is to not define a value so that it evaluates to false
## Example:
##     $ make test (runs all tests using default users system and dependencies)
##     $ make test name=tests/functional/modules/test_zos_copy_func.py debug=true (run specific test and debug)
##     $ make test host=ec33012a python=3.9 zoau=1.1.1 name=tests/functional/modules/test_zos_copy_func.py debug=true (specify host, python, zoau, test name, and debug)
test:
	@# --------------------------------------------------------------------------
	@# Expecting the zOS host, python version and zoau version to use with
	@# generating a configuration for us with zTest helper.
	@# --------------------------------------------------------------------------

    ifdef host
        ifdef python
            ifdef zoau
				echo $$(${VENV}/./make.env --config ${host} ${python} ${zoau})>$(VENV)/config.yml
            else
		    	@echo "Option 'zoau=<version>' was not set, eg zoau=1.1.1"
				exit 1
            endif
        else
			@echo "No python version option was set, eg python=3.8"
			exit 1
        endif
    endif

	@# --------------------------------------------------------------------------
	@# When a quick test with no options and defaults are acceptable, the dummy
	@# variable does nothing, its meant to not evaluate and instead evaluate the
	@# usersname with whoami then use that to look up the users default configured
	@# zos host to run tests on.
	@# --------------------------------------------------------------------------
    ifndef dummy
		$(eval username := $(shell whoami))
		echo $$(${VENV}/./make.env --config ${username} ${ZOS_PYTHON_DEFAULT} ${ZOAU_DEFAULT})>$(VENV)/config.yml
    endif

	@# --------------------------------------------------------------------------
	@# Check configuration was created in venv/config.yml, else error and exit
	@# --------------------------------------------------------------------------
	@if test ! -e $(VENV)/config.yml; then \
	    echo "No configuration created in $(VENV)/config.yml "; \
		exit 1; \
	fi

	@# --------------------------------------------------------------------------
	@# Check if name='a specific test' and if debug was set, else run all tests
	@# --------------------------------------------------------------------------

	@if test -e tests/functional/modules/test_module_security.py; then \
		mv -f tests/functional/modules/test_module_security.py tests/functional/modules/test_module_security.txt; \
	fi

    ifdef name
        ifdef debug
			@. $(VENV_BIN)/activate && $(VENV_BIN)/pytest $(name) --host-pattern=all --zinventory=$(VENV)/config.yml -s
        else
			@. $(VENV_BIN)/activate && $(VENV_BIN)/pytest $(name) --host-pattern=all --zinventory=$(VENV)/config.yml
        endif
    else
        ifdef debug
			@. $(VENV_BIN)/activate && $(VENV_BIN)/pytest --host-pattern=all --zinventory=$(VENV)/config.yml -s
        else
			@. $(VENV_BIN)/activate && $(VENV_BIN)/pytest --host-pattern=all --zinventory=$(VENV)/config.yml
        endif
    endif

	@if test -e tests/functional/modules/test_module_security.txt; then \
		mv -f tests/functional/modules/test_module_security.txt tests/functional/modules/test_module_security.py; \
	fi

# ==============================================================================
# Run the sanity test using docker given python version else default to venv
# ==============================================================================
## Run sanity tests either in the virtual environment (venv) or docker if there is a running docker engine
## Options:
##     version - choose from '2.6', '2.7', '3.5', '3.6', '3.7', '3.8', '3.9', no selection will run all available python versions
## Example:
##     $ make sanity version=3.8
##     $ make sanity
sanity:
    ifeq ($(DOCKER_INFO),0)
        ifdef version
			@. $(VENV_BIN)/activate && cd ~/.ansible/collections/ansible_collections/ibm/ibm_zos_core && \
				ansible-test sanity --python $(version) --requirements --docker default && \
					cd $(CURR_DIR);
        else
			@. $(VENV_BIN)/activate && cd ~/.ansible/collections/ansible_collections/ibm/ibm_zos_core && \
				ansible-test sanity --requirements --docker default && \
					cd $(CURR_DIR);
        endif
    else
        ifdef version
			@. $(VENV_BIN)/activate && cd ~/.ansible/collections/ansible_collections/ibm/ibm_zos_core && \
				ansible-test sanity --python $(version) --requirements && \
					cd $(CURR_DIR);
        else
			@. $(VENV_BIN)/activate && cd ~/.ansible/collections/ansible_collections/ibm/ibm_zos_core && \
				ansible-test sanity --requirements && \
					cd $(CURR_DIR);
        endif
    endif

# ==============================================================================
# Run a bandit security scan on the plugin directory
# ==============================================================================
## Run a bandit security scan on the plugins directory, set the severity level.
## Options:
##     level - choose from 'l', 'll', 'lll'
##           - l all low, medium, high severity
##           - ll all medium, high severity
##           - lll all hight severity
## Example:
##     $ make bandit sev=ll
##     $ make bandit sev=l
bandit:
    ifdef sev
		@echo $(divider);
		@echo "Running Bandit scan with sev=${sev}";
		@echo $(divider);
		@. $(VENV_BIN)/activate && bandit -r plugins/* -${sev}
    else
		@echo "No bandit sev (severity) has been set."
    endif

# ==============================================================================
# Install an ibm_zos_core collection from galaxy (or how you have ansible.cfg configured)
# ==============================================================================
## Install a collection from galaxy and specify the version.
## Options:
##     version - any GA and beta versions currently on Galaxy
## Example:
##     $ make install 1.4.0-beta.1
##     $ make install
install:
    ifdef version
		@echo $(divider);
		@echo "Installing 'ibm.ibm_zos_core' collection version=${version}.";
		@echo $(divider);
		@. $(VENV_BIN)/activate && ansible-galaxy collection install -fc ibm.ibm_zos_core:${version}
    else
		@echo $(divider);
		@echo "Installing latest non-beta 'ibm.ibm_zos_core' collection.";
		@echo $(divider);
		@. $(VENV_BIN)/activate && ansible-galaxy collection install -fc ibm.ibm_zos_core
    endif

# ==============================================================================
# Cleanup and teardown based on user selection
# ==============================================================================
## Cleanup and teardown the environment based on the level selected.
## Options:
##     level - choose from 'min', 'all'
##           - 'all' will remove the venv, restore any temporarily located files
##             and ensure config is encrypted
##           - 'min' will restore any temporarily located files
##             and ensure config is encrypted
## Example:
##     $ make clean level=all
##     $ make clean level=min
clean:
	@echo $(divider)
	@echo "Deleting venv"
	@echo $(divider)
	@rm -rf $(VENV)

    ifdef level
        ifeq ($(level),all)
			@echo $(divider)
			@echo "Complete teardown selected."
			@echo $(divider)

			@echo $(divider)
			@echo "Deleting python virtual environment 'venv'."
			@echo $(divider)
			@rm -rf $(VENV)
        endif

        ifeq ($(level),min)
			@echo $(divider);
			@echo "Minimum teardown selected.";
			@echo $(divider);
        endif

		@if test -e tests/functional/modules/test_module_security.txt; then \
			echo $(divider); \
			echo "Restoring 'test_module_security.py', previously removed to avoid execution."; \
			echo $(divider); \
			mv -f tests/functional/modules/test_module_security.txt tests/functional/modules/test_module_security.py; \
		fi

		@if test -e make.env; then \
			echo $(divider); \
			echo "Encrypting 'make.env' to 'make.env.encrypt'"; \
			echo $(divider); \
			make encrypt; \
		fi
    else
		@echo "No clean level has been set, please set a level."
    endif

# ==============================================================================
# Cleanup and teardown based on user selection
# ==============================================================================
## Help on how how to use this Makefile, options and examples.
help:
	@awk '{ \
			if ($$0 ~ /^.PHONY: [a-zA-Z\-\_0-9]+$$/) { \
				helpCommand = substr($$0, index($$0, ":") + 2); \
				if (helpMessage) { \
					printf "\033[36m%-20s\033[0m %s\n", \
						helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^[a-zA-Z\-\_0-9.]+:/) { \
				helpCommand = substr($$0, 0, index($$0, ":")); \
				if (helpMessage) { \
					printf "\033[36m%-10s\033[0m %s\n", \
						helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^##/) { \
				if (helpMessage) { \
					helpMessage = helpMessage"\n           "substr($$0, 3); \
				} else { \
					helpMessage = substr($$0, 3); \
				} \
			} else { \
				if (helpMessage) { \
					print "\n                     "helpMessage"\n" \
				} \
				helpMessage = ""; \
			} \
		}' \
		$(MAKEFILE_LIST)


# ==============================================================================
# Unused but maybe can repurpose code snippets
# ==============================================================================
# Build the command, this is not run initially
# CMD_CONFIG := $(shell $(VENV)/./make.env --config ${host} ${python} ${zoau})
# Define the executible `GEN_CONFIG` and assign it to CONFIG
# GEN_CONFIG = $(eval CONFIG=$(CMD_CONFIG))

# ==============================================================================
# Makefile tip:
# ==============================================================================
# If you have formatting issues; try `cat -e -t -v Makefile`.
# ^I represent tabs and $'s represent end of the line.