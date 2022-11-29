# ==============================================================================
# Copyright (c) IBM Corporation 2022
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

## Encrypt the configuration files with a `.encrypt` suffix for files
## [make.env, mount-shr.sh, profile-shr] with user specified password.
## If no password is provided, you will be prompted to enter a password for each
## file being encrypted.
## Example:
##     $ make encrypt password=
##     $ make encrypt
## Note: This is not a common operation, unless you tend to edit the configuration, avoid using this feature.
encrypt:
	@# --------------------------------------------------------------------------
	@# Check to see if there is an unencrypted file(s) to encrypt, you would not
	@# want to delete the encrypted version if the original unecrypted is not
	@# present as there would be no recovery process then.
	@# --------------------------------------------------------------------------
	@if test ! -e make.env; then \
	    echo "File 'make.env' could not be found in $(CURR_DIR)"; \
		exit 1; \
	fi

	@if test ! -e scripts/mount-shr.sh; then \
	    echo "File 'mount-shr.sh' could not be found in $(CURR_DIR)/scripts. "; \
		exit 1; \
	fi

	@if test ! -e scripts/profile-shr; then \
	    echo "File 'profile-shr' could not found in $(CURR_DIR)/scripts. "; \
		exit 1; \
	fi

	@# --------------------------------------------------------------------------
	@# Check to see if there an encrypted version of the file, if so delete it
	@# so it can be encrypted.
	@# --------------------------------------------------------------------------

	@if test -e make.env.encrypt; then \
	    echo "Removing encrypted file 'make.env.encrypt' in $(CURR_DIR)."; \
		rm -rf make.env.encrypt; \
	fi

	@if test -e scripts/mount-shr.sh.encrypt; then \
	    echo "Remvoing encrypted file 'scripts/mount-shr.sh.encrypt' in $(CURR_DIR)/scripts."; \
		rm -rf scripts/mount-shr.sh.encrypt; \
	fi

	@if test -e scripts/profile-shr.encrypt; then \
	    echo "Remvoing encrypted file 'scripts/profile-shr.encrypt' in $(CURR_DIR)/scripts."; \
		rm -rf scripts/profile-shr.encrypt; \
	fi

	@# --------------------------------------------------------------------------
	@# Encrypt the files since we have verified the uncrypted versions exist
	@# Note: we should move make.env to scripts as well
	@# --------------------------------------------------------------------------

    ifdef password
		@echo "${password}" | openssl bf -a -in scripts/mount-shr.sh -out scripts/mount-shr.sh.encrypt -pass stdin
		# @openssl bf -a -in scripts/mount-shr.sh > scripts/mount-shr.sh.encrypt
		@rm -f scripts/mount-shr.sh

		@echo "${password}" | openssl bf -a -in scripts/profile-shr -out scripts/profile-shr.encrypt -pass stdin
		# @openssl bf -a -in scripts/profile-shr > scripts/profile-shr.encrypt
		@rm -f scripts/profile-shr

		@echo "${password}" | openssl bf -a -in make.env -out make.env.encrypt -pass stdin
		# @openssl bf -a -in make.env > make.env.encrypt
		@rm -f make.env
    else
		@openssl bf -a -in scripts/mount-shr.sh -out scripts/mount-shr.sh.encrypt
		# @openssl bf -a -in scripts/mount-shr.sh > scripts/mount-shr.sh.encrypt
		@rm -f scripts/mount-shr.sh

		@openssl bf -a -in scripts/profile-shr -out scripts/profile-shr.encrypt
		# @openssl bf -a -in scripts/profile-shr > scripts/profile-shr.encrypt
		@rm -f scripts/profile-shr

		@openssl bf -a -in make.env -out make.env.encrypt
		# @openssl bf -a -in make.env > make.env.encrypt
		@rm -f make.env
    endif
## Decrypt all scripts used with this Makefile using the user specified password
## Files include: ["mount-shr.sh", "profile-shr", "make.env"]
## If no password is provided, you will be prompted to enter a password for each
## file being decrypted.
## Example:
##     $ make encrypt password=
##     $ make decrypt
decrypt:
	@# --------------------------------------------------------------------------
	@# Check configuration files exit
	@# --------------------------------------------------------------------------
	@if test ! -e scripts/mount-shr.sh.encrypt; then \
	    echo "File 'mount-shr.sh.encrypt' not found in  scripts/mount-shr.sh.encrypt"; \
		exit 1; \
	fi

	@if test ! -e scripts/profile-shr.encrypt; then \
	    echo "File 'scripts/profile-shr.encrypt' not found in scripts/profile-shr.encrypt"; \
		exit 1; \
	fi

	@if test ! -e make.env.encrypt; then \
	    echo "File 'make.env.encrypt' not found in $(CURR_DIR)"; \
		exit 1; \
	fi

	@# -------------------------------------------------------------------------
	@# Decrypt configuration files
	@# -------------------------------------------------------------------------
    ifdef password
		@echo "${password}" | openssl bf -d -a -in scripts/mount-shr.sh.encrypt  -out scripts/mount-shr.sh -pass stdin
		@chmod 700 scripts/mount-shr.sh

		@echo "${password}" | openssl bf -d -a -in scripts/profile-shr.encrypt  -out scripts/profile-shr -pass stdin
		@chmod 700 scripts/profile-shr

		@echo "${password}" | openssl bf -d -a -in make.env.encrypt  -out make.env -pass stdin
		@chmod 700 make.env
    else
		@openssl bf -d -a -in scripts/mount-shr.sh.encrypt  -out scripts/mount-shr.sh
		@chmod 700 scripts/mount-shr.sh

		@openssl bf -d -a -in scripts/profile-shr.encrypt  -out scripts/profile-shr
		@chmod 700 scripts/profile-shr

		@openssl bf -d -a -in make.env.encrypt  -out make.env
		@chmod 700 make.env
    endif

# ==============================================================================
# Set up your venv, currently its hard coded to `venv` and designed to look first
# to see if you have one before trying to create one.
# @test -d $(VENV) || $(HOST_PYTHON) -m venv $(VENV)
# ==============================================================================
## Create a python virtual environment (venv) based on the systems python3
## Options:
##     req - a user provided requirements.txt, if this is not set one will be
##     created for you.
## Example:
##     $ make vsetup
##     $ make vsetup req=tests/requirements.txt
vsetup:

	@# -------------------------------------------------------------------------
	@# Create the virtual environment directory if it does not exist
	@# -------------------------------------------------------------------------
	@if test ! -d $(VENV); then \
		echo $(divider); \
		echo "Creating python virtual environment directory $(VENV)."; \
		echo $(divider); \
		$(HOST_PYTHON) -m venv $(VENV); \
	else \
		echo "Virtual environment already exists, no changes made."; \
	fi

	@# -------------------------------------------------------------------------
	@# Check if files exist in venv, if they do we should not decrypt/replace
	@# them as they could have edits and risk losing them.
	@# -------------------------------------------------------------------------

	@if test ! -e $(VENV)/make.env && \
	    test ! -e $(VENV)/mount-shr.sh && \
		test ! -e $(VENV)/profile-shr; then \
		echo $(divider); \
		echo "Decrypting files into $(VENV)."; \
		echo $(divider); \
		make decrypt; \
		mv make.env $(VENV)/; \
		mv scripts/mount-shr.sh $(VENV)/; \
		mv scripts/profile-shr $(VENV)/; \
	else \
		echo "Files $(VENV)/[make.env, mount-shr.sh,profile-shr] already exist, no changes made."; \
	fi

    ifdef req
		@if test -f ${req}; then \
			echo $(divider); \
			echo "Installing user provided python requirements into $(VENV)."; \
			echo $(divider); \
			cp ${req} ${VENV}/requirements.txt; \
			. $(VENV_BIN)/activate && pip install -r $(VENV)/requirements.txt; \
		fi
    else
		@if test ! -e $(VENV)/requirements.txt; then \
			echo $(divider); \
			echo "Installing default python requirements into $(VENV)."; \
			echo $(divider); \
			echo $$(${VENV}/./make.env --req)>${VENV}/requirements.txt; \
			. $(VENV_BIN)/activate && pip install -r $(VENV)/requirements.txt; \
		else \
			echo "Requirements file $(VENV)/requirements.txt already exists, no new packages installed."; \
		fi
    endif

# ==============================================================================
# You don't need to activate your venv with this Makefile, but should you want
# to, you can with vstart.
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
	@echo $(divider)
	@echo "Building Ansible collection based on local branch and installing."
	@echo $(divider)

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
##     $ make test host=ec33012a python=3.9 zoau=1.1.1 name=tests/functional/modules/test_zos_copy_func.py debug=true
test:
	@# --------------------------------------------------------------------------
	@# Expecting the zOS host, python version and zoau version to use with
	@# generating a configuration for us with zTest helper.
	@# --------------------------------------------------------------------------

    ifdef host
        ifdef python
            ifdef zoau
				@echo $$(${VENV}/./make.env --config ${host} ${python} ${zoau})>$(VENV)/config.yml
            else
		    	@echo "Option 'zoau=<version>' was not set, eg zoau=1.1.1"
				@exit 1
            endif
        else
			@echo "No python version option was set, eg python=3.8"
			@exit 1
        endif
    else
		@# --------------------------------------------------------------------------
		@# When a quick test with no options and defaults are acceptable, a
		@# lookup using the users usersname is mapped to a default of known
		@# zos targets registered in make.env
		@# --------------------------------------------------------------------------

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
# Check the version of the ibm_zos_core collection installed
# ==============================================================================
## Get the version of the ibm_zos_core collection installed
## Example:
##     $ make version
version:
	@echo $(divider)
	@echo "Obtaining Ansible collection version installed on this controller."
	@echo $(divider)

	@cat ~/.ansible/collections/ansible_collections/ibm/ibm_zos_core/MANIFEST.json \
	|grep version|cut -d ':' -f 2 | sed "s/,*$\//g" | tr -d '"';

# ==============================================================================
# Print the configuration used to connect to the managed node for functional tests
# ==============================================================================
## Print the contents of the config file (venv/config.yml) which is used to
## connect to the managed z/OS node to run functional tests on. This will only
## be available if yo have set up a venv using `make vsetup` because a password
## is required to generate the config and is considered sensitive content per
## corporate policy.
## Example:
##     $ make printConfig
printConfig:
	@if test -e $(VENV)/config.yml; then \
	    cat $(VENV)/config.yml; \
	else \
		echo "No configuration was found, consider creating a venv using `make vsetup` first."; \
	fi

# ==============================================================================
# Print the make.env contents
# ==============================================================================
## Print the contents of the venv/make.env, this only works if
## you have set up a venv using `make vsetup` because a password is required to
## decrypt and a decrypted copy will be placed in the venv.
## Example:
##     $ make printEnv
printEnv:
	@if test -e $(VENV)/make.env; then \
	    cat $(VENV)/make.env; \
	else \
		echo "No configuration was found, consider creating a venv using `make vsetup` first."; \
	fi

# ==============================================================================
# Print the make.env contents
# ==============================================================================
## Print the contents of the venv/mount-shr.sh, this only works if
## you have set up a venv using `make vsetup` because a password is required to
## decrypt and a decrypted copy will be placed in the venv.
## Example:
##     $ make printMount
printMount:
	@if test -e $(VENV)/mount-shr.sh; then \
	    cat $(VENV)/mount-shr.sh; \
	else \
		echo "No configuration was found, consider creating a venv using `make vsetup` first."; \
	fi

# ==============================================================================
# Print the make.env contents
# ==============================================================================
## Print the contents of the venv/profile-shr, this only works if
## you have set up a venv using `make vsetup` because a password is required to
## decrypt and a decrypted copy will be placed in the venv.
## Example:
##     $ make printEnv
printProfile:
	@if test -e $(VENV)/profile-shr; then \
	    cat $(VENV)/profile-shr; \
	else \
		echo "No configuration was found, consider creating a venv using `make vsetup` first."; \
	fi

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
			@echo "Deleting files = [make.env, mount-shr.sh, profile-shr].";
			@echo $(divider);
			@rm -rf $(VENV)/make.env
			@rm -rf $(VENV)/mount-shr.sh
			@rm -rf $(VENV)/profile-shr
        endif

		@if test -e tests/functional/modules/test_module_security.txt; then \
			echo $(divider); \
			echo "Restoring 'test_module_security.py', previously removed to avoid execution."; \
			echo $(divider); \
			mv -f tests/functional/modules/test_module_security.txt tests/functional/modules/test_module_security.py; \
		fi

		# Unsure really need or even want to do this as part of cleanup
		# @if test -e make.env; then \
		# 	echo $(divider); \
		# 	echo "Found uncrypted files, encrypting them."; \
		# 	echo $(divider); \
		# 	make encrypt; \
		# fi
    else
		@echo $(divider)
		@echo "Default teardown, deleting $(VENV)"
		@echo $(divider)
		@rm -rf $(VENV)
    endif

## Copy your ssh key to a `host` or the default which is your username. If you are
## copying a key to a production server, a second key will be copied used by the
# jenkins node, this minimizes the number of times you must copy a key. You must
## have set up a venv `venv` as that is where the environment script and configurations
## get written to manage this make file. It avoids continued decryption prompts to
## force users to set up the venv via `vsetup`
## Options:
##     host - choose from a known host or don't set a value for the default operation
##            which is to user your username to look up your default system
## Example:
##     $ make copyKey host=ec33012a
##     $ make copyKey
copyKey:
	@echo $(divider)
	@echo "Copying SSH keys to the managed node authorized_keys."
	@echo $(divider)

    ifdef host
		@${VENV}/./make.env --cert ${host}
    else
		@$(eval username := $(shell whoami))
		@${VENV}/./make.env --cert ${username}
    endif

## Copy your ssh key to a `host` or the default which is your username. Then
## copy the super share mount script and profile for the mounts, execute the
## mount script and exit, upon rmote ssh, `profile-shr` will be located
## at `/u/${user} where user is defined in the make.env `host_list`. You must
## have set up a venv `venv` as that is where the environment script and configurations
## get written to manage this make file. It avoids continued decryption prompts to
## force users to set up the venv via `vsetup`
## Options:
##     host - choose from a known host or don't set a value for the default operation
##            which is to user your username to look up your default system
## Example:
##     $ make mountProfile host=ec33012a
##     $ make mountProfile
mountProfile:
    ifdef host
		@make copyKey host=${host}
		@echo $(divider)
		@echo "Copying mount script to managed node and executing."
		@echo "Copying profile-shr to managed node."
		@echo $(divider)
		@${VENV}/./make.env --files "${host}" "${VENV}/mount-shr.sh" "${VENV}/profile-shr"
    else
		@make copyKey
		@echo $(divider)
		@echo "Copying mount script to managed node and executing."
		@echo "Copying profile-shr to managed node."
		@echo $(divider)
		@$(eval username := $(shell whoami))
		@${VENV}/./make.env --files ${username} $(VENV)/mount-shr.sh $(VENV)/profile-shr
    endif

## Display the z/OS managed nodes available and configured. This will show which
## systems you can use in the host argument for `make test host<....>`
## Example:
##     $ make printTargets
printTargets:
	@${VENV}/./make.env --targets

## Build the changelog, this should be a release activity otherwise the generated
## files should not be checked in.
## Example:
##     $ make buildChglog
buildChglog:
	@. $(VENV_BIN)/activate && antsibull-changelog release

## Update the documentation for the collection after module doc changes have been
## made. This simply calls the make file in the docs directory, see the make file
## there for additional options.
## Example:
##     $ make buildDoc
buildDoc:
	@. $(VENV_BIN)/activate && make -C docs clean
	@. $(VENV_BIN)/activate && make -C docs module-doc
	@. $(VENV_BIN)/activate && make -C docs html
	@. $(VENV_BIN)/activate && make -C docs view-html

## Cleanup and remove geneated doc for the collection if its not going to be
## checked in
## Example:
##     $ make cleanDoc
cleanDoc:
	@. $(VENV_BIN)/activate && make -C docs clean

# ==============================================================================
# Self documenting code that when comments are created as expected, the help
# is auto generated. Supports multiline comments when comments are prefixed with
# 2 pound signs and a space, see examples in this makefile.
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
#
# If you need to debug your makefile command, use `-nd`, eg `make -nd vstop`