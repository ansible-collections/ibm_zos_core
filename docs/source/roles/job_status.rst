
:github_url: https://github.com/IBM/ibm_zosmf/tree/master/plugins/roles/job_status

.. _job_status_module:


job_status -- Role creates a z/OS software instance
===================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The **IBM z/OSMF collection** provides an Ansible role, referred to as **job_status**, to create an instance of manually configured z/OS software such as IBM Customer Information Control System (CICS®), IBM Db2®, IBM Information Management System (IMS™), IBM MQ, and IBM WebSphere Application Server or any other z/OS Software in **IBM Cloud Provisioning and Management (CP&M**) registry.







Variables
---------


 

zmf_host
  Hostname of the z/OSMF server, specified in the inventory file or vars file.

  | **required**: True
  | **type**: str


 

zmf_port
  Port number of the z/OSMF server. If z/OSMF is not using the default port, you need to specify value for this parameter in the inventory file or vars file.

  | **required**: False
  | **type**: str
  | **default**: 443


 

zmf_user
  User name to be used for authenticating with the z/OSMF server.

  This variable can be specified in the inventory file or vars file, or prompted when playbook is run.


  | **required**: True
  | **type**: str


 

zmf_password
  Password to be used for authenticating with z/OSMF server.

  This variable can be specified in the inventory file or vars file, or prompted when playbook is run.


  | **required**: True
  | **type**: str


 

instance_record_dir
  Directory path that the provisioning role uses to capture various information (in JSON format) about the provisioned instance.

  On many system default value ``"/tmp"`` used for this variable may not be acceptable because ``"/tmp"`` directory can be transient on the system. In such cases it is recommended to specify non-default value for this variable. This variable can be specified in the inventory file or vars file.


  | **required**: False
  | **type**: str
  | **default**: /tmp


 

systems_name
  The name of the system where the software is currently manullay configured

  | **required**: True
  | **type**: str


 

sysplex_name
  The name of the sysplex where the software is currently manullay configured

  | **required**: True
  | **type**: str


 

external_name
  The external name associated with the manually configured software

  | **required**: True
  | **type**: str


 

vendor_name
  The vendor who proivded the software

  | **required**: True
  | **type**: str


 

software_type
  The software type of the configured software

  | **required**: True
  | **type**: str


 

product_version
  The software product version of the configured software

  | **required**: True
  | **type**: str


 

instance_description
  Description for the configured software

  | **required**: True
  | **type**: str


 

instance_provider
  User who provided the software instance information

  | **required**: True
  | **type**: str


 

instance_owner
  Owner of the software instance. Software instance can be removed only by this user

  | **required**: True
  | **type**: str


 

instance_var_json_path
  Directory path for the JSON file that holds variables associated with software instance. Specify the file name that includes variables associated with the configured softare instance e.g. /tmp/myVar.json. File contains json array of variables with name, value and visibility format where name identifies variable name, value identifies variable value and visibility identifies whether variable is "public" or "private". For example,

  ``[``

  ``{``

  ``"name":"VAR1",``

  ``"value":"VAR1_VALUE",``

  ``"visibility":"public"``

  ``},``

  ``{``

  ``"name":"VAR2",``

  ``"value":"VAR2_VALUE",``

  ``"visibility":"public"``

  ``},``

  ``....]``

  | **required**: False
  | **type**: dict


 

zmf_body
  Instead of specifying *system-name*, *sysplex-name*, *external_name*, *vendor_name*, *product_version*, *instance_description*, *instance_owner*, *instance_provider*, and *instance_var_json_path* individually, this parameter can be used to pass them as a dictionary variable. This variable needs to be in following format,

  ``{``

  ``"system-name":"{{ system_name }}",``

  ``"sysplex-name":"{{ sysplex_name }}",``

  ``"registry-type":"general",``

  ``"external-name":"{{ external_name }}",``

  ``"type":"{{ software_type }}",``

  ``"vendor":"{{ vendor_name }}",``

  ``"version":"{{ product_version }}",``

  ``"description":"{{ instance_description }}",``

  ``"owner":"{{ instance_owner }}",``

  ``"provider":"{{ instance_provider }}",``

  ``"state":"provisioned",``

  ``"actions":[ {"name":"deprovision","type":"instructions", "instructions":"perform this action to deprovision"} ],``

  ``"variables":{{ instance_variable_record }}``

  ``}``

  Note *instance_variable_record* is a dictionary object and needs to be in following format


  ``[``

  ``{``

  ``"name":"VAR1",``

  ``"value":"VAR1_VALUE",``

  ``"visibility":"public"``

  ``},``

  ``{``

  ``"name":"VAR2",``

  ``"value":"VAR2_VALUE",``

  ``"visibility":"public"``

  ``},``

  ``....]``

  | **required**: False
  | **type**: dict




Examples
--------

.. code-block:: yaml+jinja

   
   - name: create instance of z/OS software in software instance registry
     hosts: sampleHost
     gather_facts: no
     collections: 
       - ibm.ibm_zosmf
     tasks: 
       - include_role:
           name: job_status
         vars:
           system_name: "<fill-me>"
           sysplex_name: "<fill-me>" 
           external_name: "<fill-me>"
           software_type: "<fill-me>"
           vendor_name: "<fill-me>"
           product_version: "<fill-me>"
           instance_description: "<fill-me>"
           instance_owner: "<fill-me>"
           instance_provider: "<fill-me>"
           instance_var_json_path: "<fill-me-file-path-and-name>" 



Notes
-----

.. note::
   - The given example assumes that you have an inventory file *inventory.yml* and host vars *sampleHost.yml* with appropriate values to identify the target z/OSMF server end point.


   - When playbooks completes, a message shown in following example is displayed, ``"msg": "Instance record saved at: /tmp/xxx/xxx.json"``. This message includes a file path and file name where instance specific information is returned. This file is required for :ref:`zmf_cpm_manage_software_instance <zmf_cpm_manage_software_instance_module>` and :ref:`zmf_cpm_remove_software_instance <zmf_cpm_remove_software_instance_module>` roles.








