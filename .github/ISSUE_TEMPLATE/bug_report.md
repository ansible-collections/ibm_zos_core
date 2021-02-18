---
name: Bug report
about: Create a bug report to share a problem with a module, plugin, task or feature
title: "[Bug] Report module, plugin, task or feature bugs"
labels: 'Type: Bug'
assignees: ''

---

<!--- Verify first that your issue is not already reported on GitHub. -->
<!--- Also, test if the latest release in Galaxy is experiencing the same bug. -->
<!--- Note: If the reviewer determines this is a dependency related bug such as
      IBM Z Open Automation Utilities (ZOAU), it will be stated in the issue,
      the issue will be closed and will require that the reporter of the issue
      follow the dependencies process to report bugs.
-->
<!--- Complete sections below as described. -->

##### SUMMARY
<!--- Explain the problem briefly below. -->
<!--- Example; when using module zos_xyz with options ABC I receive this
      message "some msg" , yet when I run the same scenario on x3270 it
      is successful.
-->

##### COMPONENT NAME
<!--- Specify the name of the module, plugin, task or feature you are
      experiencing a bug with if it applies.
-->

##### ANSIBLE VERSION
<!--- Paste verbatim output from "ansible --version" between quotes. -->
```
Ansible version output:
```

##### SPECIFY ANSIBLE COLLECTION VERSION
<!--- If you do not know the version or want to verify, you can use the
      command below to extract the collection version; replace PATH_PREFIX
      with where you installed the collection. Default is installation path is:
      `~/.ansible/collections/ansible_collections/ibm/ibm_zos_core`.

      `cat PATH_PREFIX/ibm/ibm_zos_core/MANIFEST.json | grep version
-->

##### SPECIFY THE Z OPEN AUTOMATION UTILITIES VERSION
<!-- If you do not know the version of ZOAU, you can run the version
     command on the target: `zoaversion -b`
-->

##### ENVIRONMENT
<!--- Provide all relevant information below, e.g. target z/OS version, network
      device firmware, etc.
-->

##### STEPS TO REPRODUCE
<!--- Describe how to reproduce the problem, using a minimal test-case
      or paste example playbook/yaml between below.
-->
<!--- For example:
         1. Enter command  '...'
         2. Press enter  '....'
         3. Scroll down to '....'
         4. See error '....'
-->
```yaml
Reproduction playbook/yaml
```

##### EXPECTED RESULTS
<!--- Describe what you expected to happen. -->


##### ACTUAL RESULTS
<!--- Describe what actually happened. If possible run with extra
      verbosity (-vvvv). An example of playbook with extra verbosity
      ansible-playbook -i <inventory> <playbook> -vvvv
-->

<!--- Paste verbatim command output between quotes. -->
```
Playbook output:
```

##### CONFIGURATION
#### Ansible.cfg
<!--- Paste verbatim output from "ansible-config dump --only-changed" or
      contents from `ansible.cfg`.  -->
```
'ansible-config dump --only-changed' output:
```

#### Inventory
<!--- Paste the contents of the inventory file removing any sensitive
      information. -->
```
Inventory content:
```

#### Vars
<!--- Paste the contents of group_vars or host_vars file removing any
      sensitive information. -->
```
'group_vars' or 'host_vars' content:
```

##### SCREENSHOTS
<!--- If applicable, add screenshots to help explain your problem. -->
