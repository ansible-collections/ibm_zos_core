
:github_url: https://github.com/IBM/ibm_zosmf/tree/master/plugins/roles/gather_diagnostics

.. _gather_diagnostics_module:


gather_diagnostics -- Gathers diagnostic data from z/OS managed nodes and the control node
==========================================================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The **gather_diagnostics** role gathers a comprehensive set of diagnostic facts from both the z/OS managed node and the Ansible control node.

- **Managed Node (z/OS**:) Gathers ZOAU version, Python version, locale, environment variables, user limits, pip packages, z/OS system facts, OMVS segment, filesystem mount status, ZOAU APF attributes, and optionally SSH configuration files and operator command output.

- **Control Node:** Gathers Ansible version, SSH version, Ansible config, locale, installed collections, environment, and system facts.

- This role can create separate YAML report files for the z/OS node (``gather_diagnostics_report_managed_node_<hostname>.yml``) and the control node (``gather_diagnostics_report_control.yml``) in the specified output directory.

- Facts are set on the respective hosts: ``gather_diagnostics_managed_results`` on the z/OS host and ``gather_diagnostics_control_results`` on localhost.







Variables
---------


 

gather_diagnostics_gather_control
  Controls whether the role gathers diagnostic facts from the Ansible control node.


  | **required**: False
  | **type**: bool
  | **default**: True


 

gather_diagnostics_gather_managed_node
  Controls whether the role gathers diagnostic facts from the z/OS managed node.


  | **required**: False
  | **type**: bool
  | **default**: True


 

gather_diagnostics_save_control_log
  Controls whether the role creates a YAML report file for the control node and hides sensitive data (``no_log=true``) from the console for control node tasks.


  | **required**: False
  | **type**: bool
  | **default**: True


 

gather_diagnostics_save_managed_node_log
  Controls whether the role creates a YAML report file for the z/OS managed node and hides sensitive data (``no_log=true``) from the console for z/OS tasks.


  | **required**: False
  | **type**: bool
  | **default**: True


 

gather_diagnostics_gather_syslog
  Controls whether the role attempts to run authorized MVS operator commands (``D A,L``, ``D OMVS,LIMITS``, ``D OMVS,OPTIONS``) to gather system activity. Requires operator authority.


  | **required**: False
  | **type**: bool
  | **default**: True


 

gather_diagnostics_gather_ssh_config
  Controls whether to gather contents of ~/.ssh/rc, /etc/ssh/sshrc, /etc/ssh/ssh_config, and /etc/ssh/sshd_config from the z/OS managed node.


  | **required**: False
  | **type**: bool
  | **default**: False


 

gather_diagnostics_output_dir
  Directory where diagnostic report files are created. In AAP, defaults to the artifacts directory. In standalone mode, defaults to the control node's home directory.


  | **required**: False
  | **type**: str


 

gather_diagnostics_environment_vars
  Dictionary of environment variables to set for z/OS tasks. Empty by default to allow test cases and playbooks to define their own.


  | **required**: False
  | **type**: dict




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Run gather_diagnostics to gather z/OS and control node diagnostics (default)
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics

   - name: Run gather_diagnostics and print all sensitive data to console (no log file)
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics
         vars:
           gather_diagnostics_save_control_log: false
           gather_diagnostics_save_managed_node_log: false

   - name: Run gather_diagnostics and not execute operator commands
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics
         vars:
           gather_diagnostics_gather_syslog: false

   - name: Run gather_diagnostics and collect SSH configuration files
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics
         vars:
           gather_diagnostics_gather_ssh_config: true

   - name: Run gather_diagnostics only for z/OS node diagnostics
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics
         vars:
           gather_diagnostics_gather_control: false

   - name: Run gather_diagnostics only for control node diagnostics
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics
         vars:
           gather_diagnostics_gather_managed_node: false

   - name: Run gather_diagnostics with custom output directory
     hosts: zos_host
     gather_facts: false
     collections:
       - ibm.ibm_zos_core
     tasks:
       - include_role:
           name: gather_diagnostics
         vars:
           gather_diagnostics_output_dir: /tmp/diagnostics



Notes
-----

.. note::
   - When ``gather_diagnostics_gather_syslog`` is ``True``, the user must have operator authority to execute MVS operator commands. If the user lacks authority, these tasks will fail but the role will continue with other diagnostic gathering.


   - SSH configuration file gathering (``gather_diagnostics_gather_ssh_config``) is disabled by default to avoid exposing sensitive security configurations. Enable only when needed for troubleshooting SSH connectivity issues.


   - Diagnostic files are written to the control node. By default, files are saved to the home directory or AAP artifacts directory. Use ``gather_diagnostics_output_dir`` to specify an alternate location with sufficient disk space.








