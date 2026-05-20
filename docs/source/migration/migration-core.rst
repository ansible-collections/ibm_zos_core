=====
Ansible z/OS Core Collection migration v1.x → v2.0.0
=====

This section covers breaking and recommended changes for upgrading playbooks and roles to ibm.ibm_zos_core **v2.0.0**, including updates to module options and return values.

Overview
==================================================

The changes introduced in version 2.0 enhance consistency and automation reliability through standardized naming conventions and predictable return structures.

Key improvements
--------------------------------------------------

- **Consistent naming**: Module option names and return values are standardized across the collection.
- **Predictable returns**: Return values are always present and tailored for automation, rather than being dynamically created based on module operation results.

Impact on existing playbooks
--------------------------------------------------

To achieve consistent naming across the collection, some module options and return values have been renamed:

- **Breaking changes**: Some module options and return values have new names with no backward compatibility.
- **Aliased changes**: Other module options have new primary names, with old names still supported as aliases.


Modules: Breaking and non-breaking changes
==================================================

Breaking changes are all the module options that have been renamed where the old names will no longer work. It also includes any return values which have been renamed. Any automation which relies on these values will need to be updated.

Non-breaking changes are all the module options that have been renamed for consistency across the collection, but still have the old module option name available as an alias. It is recommended to switch playbook tasks to use the new module names. This section also includes new return values.


zos_apf
--------------------------------------------------

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module sub-option renamed: ``persistent.data_set`` is renamed to ``persistent.name``.
  
  - ``persistent.data_set_name`` will remain functional.

- New return value: ``stdout_lines``.
- New return value: ``stderr_lines``.



zos_archive
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module sub-option renamed: ``format.name`` is renamed to ``format.type``.
- Module sub-option renamed: ``format.format_options`` is renamed to ``format.options``.
- Module sub-option renamed: ``format.use_adrdssu`` is renamed to ``format.adrdssu``.
- Module sub-option renamed: ``format.format_options`` is renamed to ``format.options.spack``.
  
  - The type has changed from ``string`` to ``bool``.
  - ``spack=True`` uses 'spack' as the compression algorithm, while ``spack=False`` uses the pack algorithm.

Required actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Before
   - name: Archive data set into a terse, specify pack algorithm and use adrdssu.
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         name: terse
         format_options:
           terse_pack: "spack"
           use_adrdssu: true

   # After
   - name: Archive data set into a terse, specify pack algorithm and use adrdssu
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         type: terse
         options:
           spack: true
           adrdssu: true

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- New return value: ``dest``.



zos_backup_restore
--------------------------------------------------

**TODO**: Documentation pending.



zos_blockinfile
--------------------------------------------------

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- New module option alias: ``insertafter`` can be referenced as ``after``.
- New module option alias: ``insertbefore`` can be referenced as ``before``.
- New return value: ``stdout_lines``.
- New return value: ``stderr_lines``.



zos_copy
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``is_binary`` is renamed to ``binary``.
- Module option renamed: ``force`` is renamed to ``replace``.
  
  - **NOTE**: Option ``force`` remains a valid module option with **different** functionality.

- Module option renamed: ``force_lock`` is renamed to ``force``.

Required actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Before
   - name: Copy a z/OS UNIX file to a sequential data set, overwriting content in the data set.
     ibm.ibm_zos_core.zos_copy:
       src: /path/to/uss/src
       dest: SAMPLE.SEQ.DATA.SET
       force: true
       remote_src: true

   # After
   - name: Copy a z/OS UNIX file to a sequential data set, overwriting content in the data set.
     ibm.ibm_zos_core.zos_copy:
       src: /path/to/uss/src
       dest: SAMPLE.SEQ.DATA.SET
       replace: true
       remote_src: true

   # Before
   - name: Copy binary content from a PDS member to a PDS/E member, bypassing the disposition (DISP) on the PDS/E member.
     ibm.ibm_zos_core.zos_copy:
       src: SAMPLE.PDS.DATA.SET(MEM)
       dest: SAMPLE.PDSE.DATA.SET(MEM)
       is_binary: true
       force_lock: true
       remote_src: true

   # After
   - name: Copy binary content from a PDS member to a PDS/E member, bypassing the disposition (DISP) on the PDS/E member.
     ibm.ibm_zos_core.zos_copy:
       src: SAMPLE.PDS.DATA.SET(MEM)
       dest: SAMPLE.PDSE.DATA.SET(MEM)
       binary: true
       force: true
       remote_src: true



zos_data_set
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Return value renamed: ``names`` is renamed to ``data_sets``.



zos_fetch
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``is_binary`` is renamed to ``binary``.
- Return value renamed: ``file`` is renamed to ``src``.
- Return value renamed: ``is_binary`` is renamed to ``binary``.

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- New return value: ``encoding`` (from/to).
- New return value: ``stderr_lines``.
- New return value: ``stdout_lines``.



zos_find
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option removed: ``pds_patterns``.
  
  - **TODO**: Need to understand impact.



zos_job_output
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``ddname`` is renamed to ``dd_name``.
- Return value renamed: ``ddnames`` is renamed to ``dds``.
- Return value renamed: ``ddname.ddname`` is renamed to ``dds.dd_name``.
- Return value renamed: ``ret_code.steps`` is renamed to ``job.steps``.



zos_job_query
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Return value renamed: ``ret_code.steps`` is renamed to ``steps``.
- Return value removed: ``message``.



zos_job_submit
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option removed: ``location`` option removed.
  
  - Use new module option ``remote_src`` of type bool.

- Module option renamed: ``force`` is renamed to ``replace``.
- Module option renamed: ``wait_time_s`` is renamed to ``wait_time``.
- Return value renamed: ``ddnames`` is renamed to ``dds``.
- Return value renamed: ``ddnames.ddname`` is renamed to ``dds.dd_name``.
- Return value renamed: ``ret_code.steps`` is renamed to ``jobs.steps``.
- Return value removed: ``jobs.class`` (redundant to ``jobs.job_class``).



zos_lineinfile
--------------------------------------------------

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- New module option alias: ``insertafter`` can be referenced as ``after``.
- New module option alias: ``insertbefore`` can be referenced as ``before``.
- New return value: ``stdout_lines``.
- New return value: ``stderr_lines``.



zos_mount
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``persistent.data_store`` is renamed to ``persistent.name``.
- Module option renamed: ``persistent.comment`` is renamed to ``persistent.marker``.



zos_operator
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``wait_time_s`` is renamed to ``wait_time``.
  
  - Use in conjunction with new option ``time_unit`` to indicate seconds/centiseconds.



zos_operator_action_query
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``use_regex`` is renamed to ``literal``.
- Return value renamed: ``message_text`` is renamed to ``msg_text``.
- Return value renamed: ``message_id`` is renamed to ``msg_id``.

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``message_filter`` is renamed to ``msg_filter`` (alias remains).
- Module option renamed: ``message_id`` is renamed to ``msg_id`` (alias remains).



zos_tso_command
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Return value renamed: ``content`` is renamed to ``stdout``.
- Return value renamed: ``lines`` is renamed to ``line_count``.

Non-breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- New return value: ``stdout_lines``.
- New return value: ``stderr_lines``.



zos_unarchive
--------------------------------------------------

Breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Module option renamed: ``format.name`` is renamed to ``format.type``.
- Module option renamed: ``format.format_options`` is renamed to ``format.options``.
- Module option renamed: ``format.format_options.use_adrdssu`` is renamed to ``format.options.adrdssu``.



Testing and validation
==================================================

Recommended testing approach
--------------------------------------------------

1. **Review changes**: Identify all modules used in your playbooks and review the breaking changes listed in this section.

2. **Update playbooks**: Modify your playbooks to use the new module option names and return values.

3. **Test in non-production**: Thoroughly test updated playbooks in a non-production environment.

4. **Validate return values**: Verify that any tasks relying on return values work correctly with the new names.

5. **Update documentation**: Update your internal documentation to reflect the new module options and return values.

6. **Gradual rollout**: Deploy updated playbooks to production in phases, monitoring for issues.

Testing checklist
--------------------------------------------------

- [ ] Inventory all playbooks using ibm.ibm_zos_core modules.
- [ ] Identify breaking changes affecting your playbooks.
- [ ] Update module options to use new names.
- [ ] Update tasks that reference return values.
- [ ] Test updated playbooks in development environment.
- [ ] Validate results match expected outcomes.
- [ ] Update error handling for new return value structures.
- [ ] Document changes made to playbooks.
- [ ] Deploy to production with monitoring.



Resources and support
==================================================

Documentation
--------------------------------------------------

- **IBM Z Ansible Collections**: https://ibm.github.io/z_ansible_collections_doc/
- **ibm.ibm_zos_core Collection**: https://galaxy.ansible.com/ibm/ibm_zos_core
- **Ansible Documentation**: https://docs.ansible.com/

Community and support
--------------------------------------------------

- **GitHub Repository**: https://github.com/ansible-collections/ibm_zos_core
- **Issue Tracker**: https://github.com/ansible-collections/ibm_zos_core/issues
- **Ansible Community Forum**: https://forum.ansible.com/
- **IBM Z Community**: https://community.ibm.com/community/user/ibmz-and-linuxone/home
