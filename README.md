# IBM Z Core Collection

The IBM Z core collection, referred to as `ibm_zos_core`, is part of the broader offering __Red Hat® Ansible Certified Content for IBM Z__. `ibm_zos_core` supports tasks such as creating data sets, submitting jobs, querying jobs, and retrieving job output.  

# Red Hat Ansible Certified Content for IBM Z
__Red Hat® Ansible Certified Content for IBM Z__ provides the ability to connect IBM Z® to clients' wider enterprise 
automation strategy through the Ansible Automation Platform ecosystem. This enables development and operations automation on Z through a seamless, unified workflow orchestration with configuration management, provisioning, and 
application deployment in one easy-to-use platform.  

Collections, as part of the broader offering __Red Hat® Ansible Certified Content for IBM Z__, will initially be made available
on Galaxy and later made available as certified content and accessable through Automation Hub. 

# Features
The The IBM Z core collection includes [connection plugins](https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/connection/), [action plugins](https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/action/), [modules](https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/modules/), [sample playbooks](https://github.com/ansible-collections/ibm_zos_core/tree/master/playbooks/), and ansible-doc to automate tasks on Z.  

# Plugins

## Action
* [normal](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-rexx-connection-plugin.md): A fork of [Ansible _normal.py_ action plugin](https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py) that is modified to allow a conditional shebang line in REXX modules.
* [zos_job_submit](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-job-submit.md): Used to submit a job from the controller and optionally monitor for job completion.  

## Connection
* [zos_ssh](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-rexx-connection-plugin.md): Enables the Ansible controller to communicate to a Z target machine by using ssh, with the added support to transfer ASCII as EBCDIC when transferring REXX modules. This connection plugin was forked from the [Ansible _ssh.py_ connection plugin](https://github.com/ansible/ansible/blob/480b106d6535978ae6ecab68b40942ca4fa914a0/lib/ansible/plugins/connection/ssh.py). 

# Modules 
*  [zos_data_set](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-data-set.md): Create, delete, and manage attributes for data sets.
*  [zos_job_query](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-job-query.md): Query Z for a list of jobs.
*  [zos_job_submit](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-job-submit.md): Submit a job and optionally monitor for its completion.
*  [zos_job_output](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-zos-job-output.md): Capture the job output for a submitted job.

# Playbooks
[Sample playbooks](https://github.com/ansible-collections/ibm_zos_core/tree/master/playbooks/) are included that demonstrate how to use the collection content in the `ibm_zos_core` collection.  
See the [playbooks README](https://github.com/ansible-collections/ibm_zos_core/blob/master/playbooks/README.md) for detailed instructions and configuration information.

# Requirements

A control node is any machine with Ansible installed. From the control node, you can run commands and playbooks from a laptop, desktop, or server machine. However, you cannot run them on a Windows machine. 

A managed node is often referred to as a target node, or host, and is the node that is managed by Ansible. Ansible does not need not need to be installed on a managed node, but SSH must be eanabled.

The following nodes require specific versions of software:

## Control node
* [Ansible version](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html): 2.9 or later
* [Python](https://www.python.org/downloads/release/latest): 2.7 or later
* [OpenSSH](https://www.openssh.com/)

## Managed node (target)
* [Python](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-python-zos.md): 3.6 or later
* [z/OS](https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2/zos-v2r2-home.html): V02.02.00 or later
* [IBM Z Open Automation Utilities](https://github.com/ansible-collections/ibm_zos_core/blob/master/docs/README-ZOAU.md): 1.0.1 (PTF UI66957 or later)
* [OpenSSH](https://www.openssh.com/) 

# Installation
You have several options when you are ready to install the Red Hat Ansible Certified Content for IBM Z core collection that includes Ansible Galaxy, Ansible Hub, and local. For more information on installing collections, see [Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html).

## Ansible Galaxy
You can use the [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) command with the option `install` to install a collection on your system (control node) hosted in Galaxy.  

Galaxy enables you to quickly configure your automation project with content from the Ansible community. Galaxy provides prepackaged units of work known as collections. 

Here's an example command for installing the Red Hat Ansible Certified Content for IBM Z core collection:
```
ansible-galaxy collection install ibm.ibm_zos_core
```

The collection installation progress will be output to the console. Note the location of the installation so that you can review other content included with the collection, such as the sample playbook. By default, collections are installed in `~/.ansible/collections`.

In this sample output of the collection installation, note the installation path to access the sample playbook:
```
Process install dependency map
Starting collection install process
Installing 'ibm.ibm_zos_core:0.0.4' to '/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core'
```

Installed collection content:
```
├── collections/
│  ├── ansible_collections/
│      ├── ibm/
│          ├── ibm_zos_core/
│              ├── docs/
│              ├── playbooks/
│              ├── plugins/
│                  ├── action/
│                  ├── connection/
│                  ├── module_utils/
│                  └── modules/
```

You can use the `-p` option with `anasible-galaxy` to specify the installation path such as `ansible-galaxy collection install ibm.ibm_zos_core -p /home/ansible/collections`. For more information on installing collections with Ansible Galaxy, see [Installing collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-collections-with-ansible-galaxy). 

## Private Galaxy server

Configuring access to a private Galaxy server follows the same instructions that you would use to configure your client to point to
Automation Hub. When hosting a private Galaxy server or pointing to Hub, available content is not always consistent with 
what is avaialable on the community Galaxy server. 

You can use the [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) command with 
option `install` to install a collection on your system (control node) hosted in Automation Hub or a private Galaxy server.  

By default, the `ansible-galaxy` command uses https://galaxy.ansible.com as the Galaxy server when you install a collection. 
The `ansible-galaxy` client can be configured to point to _HUB_ or other servers, such as a privately running Galaxy server, by configuring the server list in the `ansible.cfg` file.  

Ansible searches for `ansible.cfg` in these locations in this order:
* ANSIBLE_CONFIG (environment variable if set)
* ansible.cfg (in the current directory)
* ~/.ansible.cfg (in the home directory)
* /etc/ansible/ansible.cfg

To configure a Galaxy server list in the ansible.cfg file:
1. Add the server_list option under the [galaxy] section to one or more server names.
2. Create a new section for each server name.
3. Set the url option for each server name.
4. Set the auth_url option for each server name.
5. Set the API token for each server name. For more information on API tokens, see [Get API token from the version dropdown to copy your API token] (https://cloud.redhat.com/ansible/automation-hub/token/).

The following example shows a configuration for Hub, a private running Galaxy server, and Galaxy:
```
[galaxy]
server_list = automation_hub, release_galaxy, private_galaxy

[galaxy_server.automation_hub]
url=https://cloud.redhat.com/api/automation-hub/
auth_url=https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token
token=hub_token

[galaxy_server.release_galaxy]
url=https://galaxy.ansible.com/
token=release_token

[galaxy_server.private_galaxy]
url=https://galaxy-dev.ansible.com/
token=private_token
```

For more configuration information, see [Configuring the ansible-galaxy client](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#galaxy-server-config) and [Ansible Configuration Settings](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#ansible-configuration-settings).

## Local build
You can use the `ansible-galaxy collection install` command to install a collection built from source. To build your own collection, you must clone the Git repository, build the collection archive, and install the collection. The `ansible-galaxy collection build` command packages the collection into an archive that can later be installed locally without having to use Hub or Galaxy. 

To build your own collection: 

1. Clone the sample repository: 
```
git clone git@github.com:ansible-collections/ibm_zos_core.git
```

Collection archive names will change depending on the relase version. They adhere to this convention `<namespace>-<collection>-<version>.tar.gz`, for example, `ibm-ibm_zos_core-0.0.4.tar.gz`

2. Build the collection by running the `ansible-galaxy collection build` command, which must be run from inside the collection:
```
cd ibm_zos_core
ansible-galaxy collection build
```
Example output of a locally built collection:
```
user:[ ~/git/ibm/ibm_zos_core ]ansible-galaxy collection build
Created collection for ibm.ibm_zos_core at /Users/user/git/ibm/zos-ansible/ibm_zos_core/ibm-ibm_zos_core-0.0.4.tar.gz
```  

__Note__: If you build the collection with Ansible version 2.9 or earlier, you will see the following warning that you can ignore.
`[WARNING]: Found unknown keys in collection galaxy.yml at '/Users/user/git/ibm/zos-ansible/ibm_zos_core/galaxy.yml': build_ignore`

You can use the `-p` option with `anasible-galaxy` to specify the installation path, for example, `ansible-galaxy collection install ibm-ibm_zos_core-0.0.4.tar.gz -p /home/ansible/collections`. For more information, see [Installing collections with Ansible Galaxy](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-collections-with-ansible-galaxy). 

3. Install the locally built collection:
```
ansible-galaxy collection install ibm-ibm_zos_core-0.0.4.tar.gz
```

In the output of collection installation, note the installation path to access the sample playbook:
```
Process install dependency map
Starting collection install process
Installing 'ibm.ibm_zos_core:0.0.4' to '/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core'
```

# Usage
## Collection
After the collection is installed, you can access collection content for a playbook by referencing the name space `ibm` and collections fully qualified name `ibm_zos_core`, for example: 

```
- hosts: all

  tasks:
  - name: Query submitted job 'HELLO'
    ibm.ibm_zos_core.zos_job_query:
      job_name: HELLO
```

In Ansible 2.9, the `collections` keyword was added and reduces the need to refer to the collection repeatedly. For example, you can use the `collections` keyword in your playbook:  
```
- hosts: all
  collections:
   - ibm.ibm_zos_core
   
  tasks:
  - name: Query submitted job 'HELLO'
    zos_dataset:
       job_name: HELLO
```

## ansible-doc
Modules included in this collection provide additional documentation that is similar to a UNIX, or UNIX-like, operating system man page (manual page). This documentation can be accessed from the command line by using the `ansible-doc` command.

Here's how to use the Ansible-supplied command after you install the _Red Hat Ansible Certified Content for IBM Z core collection_:
`ansible-doc ibm.ibm_zos_core.zos_data_set`

```
> ZOS_DATA_SET    (/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core/plugins/modules/zos_data_set.py)

        Create, delete and set attributes of data sets. When forcing data set replacement, contents will not be
        preserved.

  * This module is maintained by The Ansible Community
OPTIONS (= is mandatory):

- batch
        Batch can be used to perform operations on multiple data sets in a single module call.
        Each item in the list expects the same options as zos_data_set.
        [Default: (null)]
        type: list
        version_added: 2.9

- data_class
        The data class name (required for SMS-managed data sets)
        [Default: (null)]
        type: str
        version_added: 2.9
```

# Helpful Links
* [Getting started Ansible guide](https://docs.ansible.com/ansible/latest/user_guide/intro_getting_started.html).

# Contributing
Currently we are not accepting community contributions. Though, you may periodically review this content to learn when and how contributions can be made in the future.

# Copyright
© Copyright IBM Corporation 2020  

# License
Some portions of this collection are licensed under [GNU General Public License, Version 3.0](https://opensource.org/licenses/GPL-3.0), 
and other portions of this collection are licensed under [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0).
See individual files for applicable licenses.

