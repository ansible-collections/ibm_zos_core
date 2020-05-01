.. ...........................................................................
.. © Copyright IBM Corporation 2020                                          .
.. ...........................................................................

Filters
=======

Filters in Ansible are from Jinja2, and are used for transforming data inside
a template expression. Jinja2 ships with many filters as does Ansible and also
allows users to add their own custom filters.

It should be noted that templates operate on the Ansible controller, not on the
target host, so filters execute on the controller as they augment the data
locally.

The **IBM z/OS core collection** includes filters and their usage in sample
playbooks.

Unlike collections that can be identified at the top level using the
collections keyword and then simply accessing modules using module names,
filters even when included in a collection must always be specified in the
playbook with their fully qualified name.

Filters usage follows this pattern:

   .. note::
         * <namespace>.<collection>.<filter>
         * ibm.ibm_zos_core.filter_wtor_messages('IEE094D SPECIFY OPERAND')

For more details on filters, review the filters and documentation under
the `filter`_ directory included in the collection.

.. _filter:
   https://github.com/ansible-collections/ibm_zos_core/tree/master/plugins/filter/






