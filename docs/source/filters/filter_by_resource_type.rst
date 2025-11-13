
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/filter_by_resource_type.py

.. _filter_by_resource_type_module:


filter_by_resource_type -- Filter returned fields from zos_stat
===============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Extract only the relevant fields for a resource from the output of zos_stat.
- Choose between data set, file, aggregate or GDG fields.





Parameters
----------


attributes
  Output from zos_stat.

  | **required**: True
  | **type**: dict


resource
  Type of resource which fields should be filtered from the returned JSON of zos_stat.

  If the resource is a data set, the filter will only include the relevant fields for the specific type of data set queried by zos_stat. When ``isdataset=False``, only common data sets attribute fields will be returned.

  | **required**: True
  | **type**: str
  | **choices**: data_set, file, aggregate, gdg






Examples
--------

.. code-block:: yaml+jinja

   
   - name: Get only data set specific attributes.
     set_fact:
       clean_output: "{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('data_set') }}"










Return Values
-------------


_value
  Stripped-down dictionary containing the fields relevant for the selected resource.

  | **type**: dict

