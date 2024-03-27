.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Filters
=======

Filters are used to transform data inside a template expression. The templates
operate on the Ansible controller, not on the managed node. Therefore,
filters execute on the controller as they augment the data locally.

The **IBM z/OS core collection** includes filters and their usage in sample
playbooks. Unlike collections that can be identified at the top level using the
collections keyword, filters must always be specified in the playbook with their
fully qualified name even when included in a collection.

Filters usage follows this pattern:

   .. note::
         * <namespace>.<collection>.<filter>
         * ibm.ibm_zos_core.filter_wtor_messages('IEE094D SPECIFY OPERAND')

For more details on filters, review the filters and documentation under
the `filter`_ directory included in the collection.

.. _filter:
   https://github.com/ansible-collections/ibm_zos_core/tree/main/plugins/filter/






