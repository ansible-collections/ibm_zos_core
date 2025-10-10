
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_operator_action_query.py

.. _zos_operator_action_query_module:


zos_operator_action_query -- Display messages requiring action
==============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Get a list of outstanding messages requiring operator action given one or more conditions.





Parameters
----------


system
  Return outstanding messages requiring operator action awaiting a reply for a particular system.

  If the system name is not specified, all outstanding messages for that system and for the local systems attached to it are returned.

  A trailing asterisk, (*) wildcard is supported.

  | **required**: False
  | **type**: str


msg_id
  Return outstanding messages requiring operator action awaiting a reply for a particular message identifier.

  If the message identifier is not specified, all outstanding messages for all message identifiers are returned.

  A trailing asterisk, (*) wildcard is supported.

  | **required**: False
  | **type**: str


job_name
  Return outstanding messages requiring operator action awaiting a reply for a particular job name.

  If the message job name is not specified, all outstanding messages for all job names are returned.

  A trailing asterisk, (*) wildcard is supported.

  | **required**: False
  | **type**: str


msg_filter
  Return outstanding messages requiring operator action awaiting a reply that match a regular expression (regex) filter.

  If the message filter is not specified, all outstanding messages are returned regardless of their content.

  | **required**: False
  | **type**: dict


  filter
    Specifies the substring or regex to match to the outstanding messages, see *literal*.

    All special characters in a filter string that are not a regex are escaped.

    Valid Python regular expressions are supported. See `the official documentation <https://docs.python.org/library/re.html>`_ for more information.

    Regular expressions are compiled with the flag **re.DOTALL** which makes the **'.'** special character match any character including a newline."

    | **required**: True
    | **type**: str


  literal
    Indicates that the value for *filter* is a regex or a string to match.

    If False, the module creates a regex from the *filter* string and matches it to the outstanding messages.

    If True, the module assumes that *filter* is not a regex and matches the *filter* substring on the outstanding messages.

    | **required**: False
    | **type**: bool
    | **default**: True





Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: none
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Display all outstanding messages issued on system MV2H
     zos_operator_action_query:
         system: mv2h

   - name: Display all outstanding messages whose job name begin with im5
     zos_operator_action_query:
         job_name: im5*

   - name: Display all outstanding messages whose message id begin with dsi*
     zos_operator_action_query:
         msg_id: dsi*

   - name: Display all outstanding messages that have the text IMS READY in them
     zos_operator_action_query:
         msg_filter:
             filter: IMS READY

   - name: Display all outstanding messages where the job name begins with 'mq',
           message ID begins with 'dsi', on system 'mv29' and which contain the
           pattern 'IMS'
     zos_operator_action_query:
         job_name: mq*
         msg_id: dsi*
         system: mv29
         msg_filter:
             filter: ^.*IMS.*$
             literal: true






See Also
--------

.. seealso::

   - :ref:`zos_operator_module`




Return Values
-------------


changed
  Indicates if any changes were made during module operation. Given operator action commands query for messages, True is always returned unless either a module or command failure has occurred.

  | **returned**: always
  | **type**: bool

count
  The total number of outstanding messages.

  | **returned**: always
  | **type**: int
  | **sample**: 12

actions
  The list of the outstanding messages.

  | **returned**: always
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "job_id": "STC01537",
                "job_name": "IM5HCONN",
                "msg_id": "HWSC0000I",
                "msg_txt": "*399 HWSC0000I *IMS CONNECT READY* IM5HCONN",
                "number": "001",
                "system": "MV27",
                "type": "R"
            },
            {
                "job_id": "STC01533",
                "job_name": "IM5HCTRL",
                "msg_id": "DFS3139I",
                "msg_txt": "*400 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5H",
                "number": "002",
                "system": "MV27",
                "type": "R"
            }
        ]

  number
    The message identification number.

    | **returned**: on success
    | **type**: int
    | **sample**: 1

  type
    The action type,'R' means request.

    | **returned**: on success
    | **type**: str
    | **sample**: R

  system
    System on which the outstanding message requiring operator action awaiting a reply.

    | **returned**: on success
    | **type**: str
    | **sample**: MV27

  job_id
    Job identifier for the outstanding message requiring operator action awaiting a reply.

    | **returned**: on success
    | **type**: str
    | **sample**: STC01537

  msg_txt
    Content of the outstanding message requiring operator action awaiting a reply. If *msg_filter* is set, *msg_txt* will be filtered accordingly.

    | **returned**: success
    | **type**: str
    | **sample**: *399 HWSC0000I *IMS CONNECT READY* IM5HCONN

  job_name
    Job name for outstanding message requiring operator action awaiting a reply.

    | **returned**: success
    | **type**: str
    | **sample**: IM5HCONN

  msg_id
    Message identifier for outstanding message requiring operator action awaiting a reply.

    | **returned**: success
    | **type**: str
    | **sample**: HWSC0000I


