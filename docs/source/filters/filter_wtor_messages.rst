
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/filter_wtor_messages.py

.. _filter_wtor_messages_module:


filter_wtor_messages -- Filter a list of WTOR messages
======================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Filter a list of WTOR (write to operator with reply) messages found by module zos_operator_action_query.
- Filter using a string or regular expression.





Parameters
----------


wtor_response
  A list containing response property `message_text`, provided the module zos_operator_action_query.

  The list can be the outstanding messages found in the  modules response under the `actions` property or the entire module response.

  | **required**: True
  | **type**: list


text
  String of text to match or a regular expression to use as filter criteria.

  | **required**: True
  | **type**: str


ingore_case
  Should the filter enable case sensitivity when performing a match.

  | **required**: False
  | **type**: bool
  | **default**: False






Examples
--------

.. code-block:: yaml+jinja

   
   - name: Filter actionable messages that match 'IEE094D SPECIFY OPERAND' and if so, set is_specify_operand = true.
     set_fact:
       is_specify_operand: "{{ result | ibm.ibm_zos_core.filter_wtor_messages('IEE094D SPECIFY OPERAND') }}"
     when: result is defined and not result.failed

   - name: Evaluate if there are any existing dump messages matching 'IEE094D SPECIFY OPERAND'
     assert:
       that:
         - is_specify_operand is defined
         - bool_zos_operator_action_continue
       success_msg: "Found 'IEE094D SPECIFY OPERAND' message."
       fail_msg: "Did not find 'IEE094D SPECIFY OPERAND' message."










Return Values
-------------


_value
  A list containing dictionaries matching the WTOR.

  | **type**: list
  | **elements**: dict

