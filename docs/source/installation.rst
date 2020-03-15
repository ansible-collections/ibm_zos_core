.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Installation
============
You have several options you may use to install the **IBM Z Core
Collection**. These are Ansible Galaxy, Ansible Hub, and a local build.

For more information on installing collections, see `using collections`_.

.. _using collections:
   https://docs.ansible.com/ansible/latest/user_guide/collections_using.html

Ansible Galaxy
--------------

You can use the `ansible-galaxy`_ command with the option install to install
a collection on your system (control node) hosted in Galaxy.

Galaxy enables you to quickly configure your automation project with content
from the Ansible community. Galaxy provides prepackaged units of work known as
collections.

Here's an example command for installing the **IBM z/OS Core Collection**:

.. code-block:: sh

   $ ansible-galaxy collection install ibm.ibm_zos_core

The collection installation progress will be output to the console. Note the
location of the installation so that you can review other content included with
the collection, such as the sample playbook. By default, collections are
installed in ``~/.ansible/collections``, see the sample output.

.. _ansible-galaxy:
   https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html

.. code-block:: sh

   Process install dependency map
   Starting collection install process
   Installing 'ibm.ibm_zos_core:0.0.4' to '/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core'

After installation, the collection content will resemble this hierarchy: :

.. code-block:: sh

   ├── collections/
   │  ├── ansible_collections/
   │      ├── ibm/
   │          ├── ibm_zos_core/
   │              ├── docs/
   │              ├── playbooks/
   │              ├── plugins/
   │                  ├── action/
   │                  ├── connection/
   │                  ├── module_utils/
   │                  └── modules/


You can use the `-p` option with `ansible-galaxy` to specify the installation
path, such as:

.. code-block:: sh

   $ ansible-galaxy collection install ibm.ibm_zos_core -p /home/ansible/collections

For more information on installing collections with Ansible Galaxy,
see `installing collections`_.

.. _installing collections:
   https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-collections-with-ansible-galaxy

Private Galaxy server
---------------------
Configuring access to a private Galaxy server follows the same instructions
that you would use to configure your client to point to Automation Hub. When
hosting a private Galaxy server or pointing to Hub, available content is not
always consistent with what is available on the community Galaxy server.

You can use the `ansible-galaxy`_ command with option `install` to install a
collection on your system (control node) hosted in Automation Hub or a private
Galaxy server.

By default, the ``ansible-galaxy`` command is configured to access
``https://galaxy.ansible.com`` as the Galaxy server when you install a
collection. The `ansible-galaxy` client can be configured to point to HUB or
other servers, such as a privately running Galaxy server, by configuring the
server list in the ``ansible.cfg`` file.

Ansible searches for ``ansible.cfg`` in these locations in this order:

   * ANSIBLE_CONFIG (environment variable if set)
   * ansible.cfg (in the current directory)
   * ~/.ansible.cfg (in the home directory)
   * /etc/ansible/ansible.cfg

To configure a Galaxy server list in the ansible.cfg file:

  * Add the server_list option under the [galaxy] section to one or more server names.
  * Create a new section for each server name.
  * Set the url option for each server name.
  * Set the auth_url option for each server name.
  * Set the API token for each server name. For more information on API tokens, see `Get API token from the version dropdown to copy your API token`_.

.. _Get API token from the version dropdown to copy your API token:
   https://cloud.redhat.com/ansible/automation-hub/token/

The following example shows a configuration for Automation Hub, a private
running Galaxy server, and Galaxy:

.. code-block:: yaml

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

For more configuration information, see
`configuring the ansible-galaxy client`_ and Ansible Configuration Settings.

.. _configuring the ansible-galaxy client:
   https://cloud.redhat.com/ansible/automation-hub/token/

.. _ansible configuration Settings:
   https://cloud.redhat.com/ansible/automation-hub/token/


Local build
-----------

You can use the ``ansible-galaxy collection install`` command to install a
collection built from source. To build your own collection, you must clone the
Git repository, build the collection archive, and install the collection. The
``ansible-galaxy collection build`` command packages the collection into an
archive that can later be installed locally without having to use Hub or Galaxy
.

To build a collection from the git repository:

   1. Clone the sample repository:

      .. code-block:: sh

         $ git clone git@github.com:ansible-collections/ibm_zos_core.git

      .. note::
         * Collection archive names will change depending on the release version.
         * They adhere to this convention **<namespace>-<collection>-<version>.tar.gz**, for example, **ibm-ibm_zos_core-0.0.4.tar.gz**


   2. Build the collection by running the ``ansible-galaxy collection build``
   command, which must be run from inside the collection:

      .. code-block:: sh

         cd ibm_zos_core
         ansible-galaxy collection build

      Example output of a locally built collection:

      .. code-block:: sh

         $ ansible-galaxy collection build
         Created collection for ibm.ibm_zos_core at /Users/user/git/ibm/zos-ansible/ibm_zos_core/ibm-ibm_zos_core-0.0.4.tar.gz

      You can use the ``-p`` option with ``ansible-galaxy`` to specify the
      installation path, for example, ``ansible-galaxy collection install ibm-ibm_zos_core-0.0.4.tar.gz -p /home/ansible/collections``.

      For more information, see `installing collections with Ansible Galaxy`_.

      .. note::
         * If you build the collection with Ansible version 2.9 or earlier, you will see the following warning that you can ignore.
         * [WARNING]: Found unknown keys in collection galaxy.yml at '/Users/user/git/ibm/zos-ansible/ibm_zos_core/galaxy.yml': build_ignore

      .. _installing collections with Ansible Galaxy:
         https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-collections-with-ansible-galaxy

   3. Install the locally built collection:

      .. code-block:: sh

         $ ansible-galaxy collection install ibm-ibm_zos_core-0.0.4.tar.gz

      In the output of collection installation, note the installation path to access the sample playbook:

      .. code-block:: sh

         Process install dependency map
         Starting collection install process
         Installing 'ibm.ibm_zos_core:0.0.4' to '/Users/user/.ansible/collections/ansible_collections/ibm/ibm_zos_core'



