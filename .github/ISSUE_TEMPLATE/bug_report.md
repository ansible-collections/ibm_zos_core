---
name: Bug report
about: Create a bug report to share a problem with a module, plugin, task or feature
title: "[Bug] Report module, plugin, task or feature bugs"
labels: 'Type: Bug'
assignees: ''

---

<!--- Verify first that your issue is not already reported on GitHub -->
<!--- Also test if the latest release in Galaxy is experience the same bug -->
<!--- Note: If the reviewer determines this is a dependency bug such as IBM Z Open Automation Utilities (ZOAU), it will be stated in the issue, the issue will be closed and will require that the reporter of the issue follow the dependencies process to report bugs --> 
<!--- Complete *all* sections as described -->

##### SUMMARY
<!--- Explain the problem briefly below -->

##### COMPONENT NAME
<!--- Write the short name of the module, plugin, task or feature below, use your best guess if unsure -->

##### STEPS TO REPRODUCE
<!--- Describe exactly how to reproduce the problem, using a minimal test-case -->
<!--- For example:
         1. Enter command  '...' 
         2. Press enter  '....'
         3. Scroll down to '....'
         4. See error '....'
-->
<!--- Paste example playbooks or commands between quotes below -->
```yaml

```

##### EXPECTED RESULTS
<!--- Describe what you expected to happen when running the steps above -->


##### ACTUAL RESULTS
<!--- Describe what actually happened. If possible run with extra verbosity (-vvvv) -->
<!--- Example of playbook with extra verbosity ansible-playbook -i <inventory> <playbook> -vvvv -->

<!--- Paste verbatim command output between quotes -->
```
Playbook output
```

##### ANSIBLE VERSION
<!--- Paste verbatim output from "ansible --version" between quotes -->
```
Ansible version
```

##### CONFIGURATION
#### Ansible.cfg
<!--- Paste verbatim output from "ansible-config dump --only-changed"  -->
```
Paste verbatim output here
```

#### Inventory
<!--- Paste the contents of the inventory file --> 
```
Paste inventory content here
```

#### Vars
<!--- Paste the contents of group_vars or host_vars file --> 
```
Paste group_vars or host_vars  content here
```

##### OS / ENVIRONMENT
<!--- Provide all relevant information below, e.g. target OS versions, network device firmware, etc. -->

##### Screenshots
<!--- If applicable, add screenshots to help explain your problem -->
