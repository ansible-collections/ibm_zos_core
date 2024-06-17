# IBM® z/OS® core collection

The **IBM z/OS core** collection enables Ansible to interact with z/OS Data Sets and USS files. The collection focuses on operating system fundamental operations such as managing encodings, creating data sets, and submitting jobs.

## Description

The **IBM z/OS core** collection is part of the **Red Hat® Ansible Certified Content for IBM Z®** offering that brings Ansible automation to IBM Z®. This collection brings forward the possibility to manage batch jobs, perform program authorizations, run operator operations, and execute both JES and MVS commands as well as execute shell, python, and REXX scripts. It supports data set creation, searching, copying, fetching, and encoding. It provides both archiving and unarchiving of data sets, initializing volumes, performing backups and supports Jinja templating.

System programmers can enable pipelines to setup, tear down and deploy applications while system administrators can automate time consuming repetitive tasks inevitably freeing up their time. New z/OS users can find comfort in Ansible's familiarity and expedite their proficiency in record time.

## Requirements

Before you install the IBM z/OS core collection, you must configure a control node and managed node with a minimum set of requirements.
The following [table](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/releases_maintenance.html) details the specific software requirements for the controller and managed node.

### Ansible Controller

This release of the collection requires **ansible-core >=2.15** (Ansible >=8.x), for additional requirements such as Python, review the [support matrix](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix).

### Managed Node

This release of the collection requires the following

* [z/OS](https://www.ibm.com/docs/en/zos).
* [z/OS shell](https://www.ibm.com/support/knowledgecenter/en/SSLTBW_2.4.0/com.ibm.zos.v2r4.bpxa400/part1.htm).
* [IBM Open Enterprise SDK for Python](https://www.ibm.com/products/open-enterprise-python-zos).
* [IBM Z Open Automation Utilities](https://www.ibm.com/docs/en/zoau).

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```sh
ansible-galaxy collection install ibm.ibm_zos_core
```

<p>&nbsp;</p>
You can also include it in a requirements.yml file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```sh
collections:
  - name: ibm.ibm_zos_core
```

<p>&nbsp;</p>
Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```sh
ansible-galaxy collection install ibm.ibm_zos_core --upgrade
```

<p>&nbsp;</p>
You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version 1.0.0:

```sh
ansible-galaxy collection install ibm.ibm_zos_core:1.0.0
```

<p>&nbsp;</p>
You can also install a beta version of the collection. A beta version is only available on Galaxy and is only supported by the community until it is promoted to General Availability (GA). Use the following syntax to install a beta version:

```sh
ansible-galaxy collection install ibm.ibm_zos_core:1.10.0-beta.1
```

<p>&nbsp;</p>
As part of the installation, the collection [requirements](#Requirements) must be made available to Ansible through the use of [environment variables](https://github.com/IBM/z_ansible_collections_samples/blob/main/docs/share/zos_core/configuration_guide.md#environment-variables). The preferred configuration is to place the environment variables in `group_vars` and `host_vars`, you can find examples of this configuration under any [playbook project](https://github.com/IBM/z_ansible_collections_samples), for example, review the **data set** example [configuration](https://github.com/IBM/z_ansible_collections_samples/tree/main/zos_concepts/data_sets/data_set_basics#configuration) documentation.

<p>&nbsp;</p>
If you are testing a configuration, it can be helpful to set the environment variables in a playbook, an example of that can be reviewed [here](https://github.com/ansible-collections/ibm_zos_core/discussions/657).

<p>&nbsp;</p>
To learn more about the ZOAU Python wheel installation method, review the [documentation](https://www.ibm.com/docs/en/zoau/1.3.x?topic=installing-zoau#python-wheel-installation-method).

<p>&nbsp;</p>
If the wheel is installed using the `--target` option, it will install the package into the specified target directory. The environment variable `PYTHONPATH` will have to be configured to where the packages is installed, e.g; `PYTHONPATH: /usr/zoau/wheels`. Using `--target` is recommended, else the wheel will be installed in Python's home directory which may not have write permissions or persist
after an update.

<p>&nbsp;</p>
If the wheel is installed using the `--user` option, it will install the package into the user directory. The environment variable `PYTHONPATH` will have to be configured to where the packages is installed, e.g; `PYTHONPATH: /u/user`.

Environment variables:

```sh
PYZ: "path_to_python_installation_on_zos_target"
ZOAU: "path_to_zoau_installation_on_zos_target"
ZOAU_PYTHONPATH: "path_to_zoau_wheel_installation_directory"

ansible_python_interpreter: "{{ PYZ }}/bin/python3"

environment_vars:
  _BPXK_AUTOCVT: "ON"
  ZOAU_HOME: "{{ ZOAU }}"
  PYTHONPATH: "{{ ZOAU_PYTHONPATH }}"
  LIBPATH: "{{ ZOAU }}/lib:{{ PYZ }}/lib:/lib:/usr/lib:."
  PATH: "{{ ZOAU }}/bin:{{ PYZ }}/bin:/bin:/var/bin"
  _CEE_RUNOPTS: "FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)"
  _TAG_REDIR_ERR: "txt"
  _TAG_REDIR_IN: "txt"
  _TAG_REDIR_OUT: "txt"
  LANG: "C"
  PYTHONSTDINENCODING: "cp1047"
```

## Use Cases

* Use Case Name: Add a new z/OS User
  * Actors:
    * Application Developer
  * Description:
    * An application developer can submit a new user request for the system admin to approve.
  * Flow:
    * Verify user does not exist; create home directory, password, and passphrase
    * Create home directory and the user to the system
    * Provide access to resource, add to system groups, and define an alias
    * Create the users ISPROF data set
    * Create user private data set, mount with persistence
    * Generate email with login credentials
* Use Case Name: Automate certificate renewals
  * Actors:
    * System Admin
  * Description:
    * The system administrator can automate certificate renewals
  * Flow:
    * Setup, configure and run z/OS Health Checker to generate a report
    * Search the Health Checker report for expiring certificates
    * Renew expiring certificates
      * Collect expiring certificate attributes and backup certificate
      * Replicate certificate with a new label
      * Generate signing request and sign new certificate
      * Supersede the old with the new certificate
      * Delete old certificate and relabel new certificate with previous certificate name
* Use Case Name: Provision a Liberty Profile Instance
  * Actors:
    * Application Developer
  * Description:
    * An application developer can provision an application runtime that accelerates the delivery of cloud-native applications.
  * Flow:
    * Create and mount a file system for the Liberty profile.
    * Create a Liberty Profile instance with optional configurations.
    * Enable z/OS authorized services for the Liberty profile.
    * Start an angel process or a server process

## Testing

All releases, including betas will meet the following test criteria.

  * 100% success for [Functional](https://github.com/ansible-collections/ibm_zos_core/tree/dev/tests/functional) tests.
  * 100% success for [Sanity](https://docs.ansible.com/ansible/latest/dev_guide/testing/sanity/index.html#all-sanity-tests) tests as part of [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing.html#run-sanity-tests).
  * 100% success for [pyflakes](https://github.com/PyCQA/pyflakes/blob/main/README.rst).
  * 100% success for [ansible-lint](https://ansible.readthedocs.io/projects/lint/) allowing only false positives.

<p>&nbsp;</p>
This release of the collection was tested with following dependencies.

  * ansible-core v2.15.x
  * Python 3.9.x
  * IBM Open Enterprise SDK for Python 3.11.x
  * IBM Z Open Automation Utilities (ZOAU) 1.3.0.x
  * z/OS V2R5

This release introduces case sensitivity for option values and includes a porting guide in the [release notes](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html) to assist with which option values will need to be updated.

## Contributing

This community is not currently accepting contributions. However, we encourage you to open [git issues](https://github.com/ansible-collections/ibm_zos_core/issues) for bugs, comments or feature requests and check back periodically for when community contributions will be accepted in the near future.

Review the [development docs](https://ibm.github.io/z_ansible_collections_doc/zhmc-ansible-modules/docs/source/development.html#development) to learn how you can create an environment and test the collections modules.

## Communication

If you would like to communicate with this community, you can do so through the following options.

  * GitHub [discussions](https://github.com/ansible-collections/ibm_zos_core/discussions).
  * GitHub [issues](https://github.com/ansible-collections/ibm_zos_core/issues/new/choose).
  * [Ansible Forum](https://forum.ansible.com/), please use the `zos` tag to ensure proper awareness.
  * Discord [System Z Enthusiasts](https://forum.ansible.com/) room [ansible](https://discord.gg/nKC8F89v).
  * Matrix Ansible room [ansible-zos](#ansible-zos:matrix.org).
  * Ansible community Matrix [rooms](https://docs.ansible.com/ansible/latest/community/communication.html#general-channels).

## Support

As Red Hat Ansible [Certified Content](https://catalog.redhat.com/software/search?target_platforms=Red%20Hat%20Ansible%20Automation%20Platform), this collection is entitled to [support](https://access.redhat.com/support/) through [Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible) (AAP). After creating a Red Hat support case, if it is determined the issue belongs to IBM, Red Hat will instruct you to create an [IBM support case](https://www.ibm.com/mysupport/s/createrecord/NewCase) and share the case number with Red Hat so that a collaboration can begin between Red Hat and IBM.

<p>&nbsp;</p>
If a support case cannot be opened with Red Hat and the collection has been obtained either from [Galaxy](https://galaxy.ansible.com/ui/) or [GitHub](https://github.com/ansible-collections/ibm_zos_core), there is community support available at no charge. Community support is limited to the collection; community support does not include any of the Ansible Automation Platform components, [IBM Z Open Automation Utilities](https://www.ibm.com/docs/en/zoau), [IBM Open Enterprise SDK for Python](https://www.ibm.com/products/open-enterprise-python-zos) or [ansible-core](https://github.com/ansible/ansible).

<p>&nbsp;</p>
The current supported versions of this collection can be found listed under the [release section](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html).

## Release Notes and Roadmap

The collection's cumulative release notes can be reviewed [here](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html). Note, some collections release before an ansible-core version reaches End of Life (EOL), thus the version of ansible-core that is supported must be a version that is currently supported.

For AAP users, to see the supported ansible-core versions, review the [AAP Life Cycle](https://access.redhat.com/support/policy/updates/ansible-automation-platform).

For Galaxy and GitHub users, to see the supported ansible-core versions, review the [ansible-core support matrix](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix).

<p>&nbsp;</p>
The collection's changelogs can be reviewed in the following table.

| Version | Status                     |
|---------|----------------------------|
| 1.11.x  | In development (unreleased)|
| [1.10.x](https://github.com/ansible-collections/ibm_zos_core/blob/v1.10.0/CHANGELOG.rst)  | 21 June 2024                |
| [1.9.x](https://github.com/ansible-collections/ibm_zos_core/blob/v1.9.0/CHANGELOG.rst)   | 05 Feb 2024                |
| [1.8.x](https://github.com/ansible-collections/ibm_zos_core/blob/v1.8.0/CHANGELOG.rst)   | 13 Dec 2023                |
| [1.7.x](https://github.com/ansible-collections/ibm_zos_core/blob/v1.7.0/CHANGELOG.rst)   | 10 Oct 2023                |
| [1.6.x](https://github.com/ansible-collections/ibm_zos_core/blob/v1.6.0/CHANGELOG.rst)   | 28 June 2023               |
| [1.5.x](https://github.com/ansible-collections/ibm_zos_core/blob/v1.5.0/CHANGELOG.rst)   | 25 April 2023              |

## Related Information

Example playbooks and use cases can be be found in the [z/OS playbook repository](https://github.com/IBM/z_ansible_collections_samples).
Supplemental content on getting started with Ansible, architecture and use cases is available [here](https://ibm.github.io/z_ansible_collections_doc/reference/helpful_links.html).

## License Information

Some portions of this collection are licensed under [GNU General Public License, Version 3.0](https://opensource.org/licenses/GPL-3.0), and other portions of this collection are licensed under [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
See individual files for applicable licenses.
