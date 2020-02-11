# Ansible z/OS Connection Plugin 

Since EBCDIC encoding is used on z/OS, custom plugins are needed to determine the correct transport method when targeting a z/OS system.

- [Ansible z/OS Connection Plugin](#ansible-zos-connection-plugin)
  - [Summary of Changes](#summary-of-changes)
    - [Action Plugin: _normal.py_, forked from the Ansible _normal.py_ action plugin](#action-plugin-normalpy-forked-from-the-ansible-normalpy-action-plugin)
    - [Connection Plugin: _zos_ssh.py_, forked from the Ansible _ssh.py_ connection plugin](#connection-plugin-zossshpy-forked-from-the-ansible-sshpy-connection-plugin)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
      - [Ansible Host](#ansible-host)
      - [REXX Module Configuration](#rexx-module-configuration)

## Summary of Changes

### Action Plugin: _normal.py_, forked from the [Ansible _normal.py_ action plugin](https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py)

The _normal.py_ action plugin is called when preparing for module execution.
_normal.py_ defines the `ActionModule` class which inherits from `ActionBase`.

`ActionBase` has a method, `_configure_module()` which is called during module configuration.
One of the return values of `_configure_module()` is the shebang line for the module.

Since REXX does not have an ordinary shebang line like shell or python, a shebang line is not found when using REXX modules.
After `_configure_module()` is called, an exception is raised if no shebang line is found.

Our fork of _normal.py_ overrides `_configure_module()` by calling the parent method and adding a single space in place of an empty shebang line value.
A single space must be added in place of an empty string because python conditionals treat an empty string as a _NoneType_.

### Connection Plugin: _zos_ssh.py_, forked from the [Ansible _ssh.py_ connection plugin](https://github.com/ansible/ansible/blob/480b106d6535978ae6ecab68b40942ca4fa914a0/lib/ansible/plugins/connection/ssh.py)

The _zos_ssh.py_ connection plugin is a fork of the default _ssh.py_ plugin with added functionality for checking if a module is written in REXX.

Since REXX scripts need to be in EBCDIC encoding to run, they need to be handled differently during transfer.
If the string `__ANSIBLE_ENCODE_EBCDIC__` is found on the first line of the module, the module is transferred to the target system using SCP.
Otherwise, SFTP is used.
SCP treats files as text, automatically encoding as EBCDIC at transfer time.
SFTP treats files as binary, performing no encoding changes.

## Getting Started 

This repo includes any plugins written or modified to account for our use case.
When running a playbook, Ansible searches the working directory for `action_plugin` and `connection_plugin` folders.
If a plugin in one of these folders matches the name of a plugin Ansible is looking for, is it used in place of the installation's version.

### Prerequisites

#### Ansible Host

* Ansible 2.9 is the version the changes were based on, other versions may work but are untested.
  * [Reference Ansible's Installation Guide for OS specific installatoin instructions.](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#intro-installation-guide)
* Python 2.7 or 3.7

#### REXX Module Configuration

1. Ensure REXX modules first line is a comment containing the following:
   1. The string `rexx`, this value is __case insensitive__.
      * When running a REXX script from USS CLI, the word rexx needs to appear on the first line for interpreter recognition.
   2. The string `__ANSIBLE_ENCODE_EBCDIC__`, this value is __case sensitive__.
   * Example REXX module:

        ```rexx
        /* rexx  __ANSIBLE_ENCODE_EBCDIC__  */
        x = 55
        SAY '{"SYSTEM_VERSION":"' x '"}'
        RETURN 0
        ```

# Copyright
© Copyright IBM Corporation 2020  
