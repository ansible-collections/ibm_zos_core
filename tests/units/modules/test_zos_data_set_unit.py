# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division)
__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule
import pytest
import sys
from mock import call

# TODO: add back in testcases for currently removed safe and unsafe data set write functionality

# Used my some mock modules, should match import directly below
IMPORT_NAME = 'ibm_zos_core.plugins.modules.zos_data_set'


# * Tests for create_data_set()

dummy_dict = {
    'type': 'pds',
    'size': '50M'
}
test_data = [
    ('test1.tester.test', dummy_dict, 0, True),
    ('test1.tester.test', {}, 0, True),
    (None, {}, 1, False),
    ('test1.tester.test', None, 0, True),
    ('test1.tester.test', dummy_dict, 1, False)
]
@pytest.mark.parametrize("dsname,args,return_value,expected", test_data)
def test_create_data_set_various_args(zos_import_mocker, dsname, args, return_value, expected):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.Datasets.create',
                create=True, return_value=return_value)
    try:
        ds.create_data_set(dsname, args)
    except ds.DatasetCreateError:
        passed = False
    except TypeError as e:
        # MagicMock throws TypeError when input args is None
        # But if it gets that far we consider it passed
        if 'MagicMock' not in str(e):
            passed = False
    assert passed == expected


def test_create_data_set_missing_all_args(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.Datasets.create', create=True)
    with pytest.raises(TypeError):
        ds.create_data_set()


def test_create_data_set_missing_second_arg(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    patched_method = mocker.patch(
        'zoautil_py.Datasets.create', create=True, return_value=0)
    ds.create_data_set('testname')
    patched_method.assert_called_with('testname')


def test_create_data_set_arg_expansion(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    item1 = 'value1'
    item2 = 'value2'
    item3 = 'value3'
    to_expand = {
        'item1': item1,
        'item2': item2,
        'item3': item3
    }
    patched_method = mocker.patch(
        'zoautil_py.Datasets.create', create=True, return_value=0)
    ds.create_data_set('testname', to_expand)
    patched_method.assert_called_with(
        'testname', item1=item1, item2=item2, item3=item3)


def test_create_data_set_exception_receiving_name(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.Datasets.create', create=True, return_value=1)
    ds_name = 'testdsn'
    mocker.patch.object(
        ds.DatasetCreateError, '__init__', return_value=None)
    with pytest.raises(ds.DatasetCreateError):
        ds.create_data_set(ds_name)


# * Tests for delete_data_set()


def test_delete_data_set_missing_arg(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.Datasets.delete', create=True)
    with pytest.raises(TypeError):
        ds.delete_data_set()


test_data = [
    ('test1.tester.test', 0, True),
    ('test1.tester.test', 1, False)
]
@pytest.mark.parametrize("dsname,return_value,expected", test_data)
def test_delete_data_set_handle_rc(zos_import_mocker, dsname, return_value, expected):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.Datasets.delete',
                create=True, return_value=return_value)
    try:
        ds.delete_data_set(dsname)
    except ds.DatasetDeleteError:
        passed = False
    assert passed == expected


def test_delete_data_set_exception_receiving_name(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.Datasets.delete', create=True, return_value=1)
    ds_name = 'testdsn'
    patched_method = mocker.patch.object(
        ds.DatasetDeleteError, '__init__', return_value=None)
    try:
        ds.delete_data_set('testdsn')
    except ds.DatasetDeleteError:
        pass
    patched_method.assert_called_with(ds_name, 1)

# * Test rename_args_for_zoau()


ZOAU_DS_CREATE_ARGS = {
    'name': 'name',
    'type': 'type',
    'size': 'size',
    'format': 'format',
    'data_class': 'class_name',
    'record_length': 'length',
    'key_offset': 'offset'
}


def test_rename_args_for_zoau_missing_arg(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    assert ds.rename_args_for_zoau() == {}


test_data = [
    ({}, {}),
    ({'name': 'tester'}, {'name': 'tester'}),

    # ? is this the behavior that we want?
    ({'name': None}, {}),
    ({'key_offset': None}, {}),

    ({'invalidname': 'tester'}, {}),
    ({'invalidname': 'tester',
    'invalidname2': 'tester2'}, {}),
    ({'key_offset': 500}, {'offset': 500}),
    ({'key_offset': 500,
    'type': 'pds',
    'data_class': 'class1',
    'record_length': 1024},
    {'offset': 500,
    'class_name': 'class1',
    'length': 1024,
    'type': 'pds'}),
]
@pytest.mark.parametrize("args,expected", test_data)
def test_rename_args_for_zoau(zos_import_mocker, args, expected):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    assert ds.rename_args_for_zoau(args) == expected

# * Test replace_data_set()


# def test_replace_data_set_safe_writes_create_temp_succeed(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     errors = []
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     unsafe_writes = False
#     extra_args = {}
#     patched_temp_name = mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     patched_move = mocker.patch(
#         'zoautil_py.Datasets.move', create=True, return_value=0)
#     ds.replace_data_set(name=name,
#                     extra_args=extra_args)

#     if patched_temp_name.call_count != 1:
#         errors.append('Datasets.temp_name call count {0} != 1'.format(
#             str(patched_temp_name.call_count)))

#     if patched_create.mock_calls != [call(temp_name, extra_args)]:
#         errors.append(
#             'data set create not called with expected args. {0} == {1}'.format(
#                 str(patched_create.mock_calls),
#                 str([call(temp_name, extra_args)])
#             )
#         )
#     if patched_delete.mock_calls != [call(name)]:
#         errors.append(
#             'data set delete not called with expected args. {0} == {1}'.format(
#                 str(patched_delete.mock_calls),
#                 str([call(name)])
#             )
#         )
#     if patched_move.mock_calls != [call(temp_name, name)]:
#         errors.append(
#             'data set move not called with expected args. {0} == {1}'.format(
#                 str(patched_move.mock_calls),
#                 str([call(temp_name, name)])
#             )
#         )
#     assert not errors, '\n'.join(errors)


# def test_replace_data_set_safe_writes_create_temp_succeed_delete_original_fail(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     unsafe_writes = False
#     extra_args = {}
#     mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, side_effect=[ds.DatasetDeleteError(name, 1), 0])
#     with pytest.raises(Exception) as e:
#         ds.replace_data_set(name=name,
#                         extra_args=extra_args)
#     assert isinstance(e, ds.DatasetCreateError) == False


# def test_replace_data_set_safe_writes_create_temp_fail(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     unsafe_writes = False
#     extra_args = {}
#     mocker.patch('zoautil_py.Datasets.temp_name',
#                 create=True, return_value=temp_name)
#     mocker.patch('zoautil_py.Datasets.create', create=True, return_value=1)
#     with pytest.raises(ds.DatasetCreateError):
#         ds.replace_data_set(name=name,
#                         extra_args=extra_args)


# def test_replace_data_set_unsafe_writes_create_temp_succeed(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     errors = []
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     unsafe_writes = True
#     extra_args = {}
#     patched_temp_name = mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     patched_move = mocker.patch(
#         'zoautil_py.Datasets.move', create=True, return_value=0)
#     ds.replace_data_set(name=name,
#                     extra_args=extra_args)

#     if patched_temp_name.call_count != 1:
#         errors.append('Datasets.temp_name call count {0} != 1'.format(
#             str(patched_temp_name.call_count)))

#     if patched_create.mock_calls != [call(temp_name, extra_args)]:
#         errors.append(
#             'data set create not called with expected args. {0} == {1}'.format(
#                 str(patched_create.mock_calls),
#                 str([call(temp_name, extra_args)])
#             )
#         )
#     if patched_delete.mock_calls != [call(name)]:
#         errors.append(
#             'data set delete not called with expected args. {0} == {1}'.format(
#                 str(patched_delete.mock_calls),
#                 str([call(name)])
#             )
#         )
#     if patched_move.mock_calls != [call(temp_name, name)]:
#         errors.append(
#             'data set move not called with expected args. {0} == {1}'.format(
#                 str(patched_move.mock_calls),
#                 str([call(temp_name, name)])
#             )
#         )
#     assert not errors, '\n'.join(errors)


# def test_replace_data_set_unsafe_writes_create_temp_fail_unsafe_succeeds(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     errors = []
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     unsafe_writes = True
#     extra_args = {}
#     patched_temp_name = mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, side_effect=[ds.DatasetCreateError(temp_name, 1), 0])
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     ds.replace_data_set(name=name,
#                     extra_args=extra_args)

#     if patched_temp_name.call_count != 1:
#         errors.append('Datasets.temp_name call count {0} != 1'.format(
#             str(patched_temp_name.call_count)))

#     expected_create_calls = [
#         call(temp_name, extra_args), call(name, extra_args)]
#     if patched_create.mock_calls != expected_create_calls:
#         errors.append(
#             'data set create not called with expected args. {0} == {1}'.format(
#                 str(patched_create.mock_calls),
#                 str(expected_create_calls)
#             )
#         )
#     expected_delete_calls = [call(name)]
#     if patched_delete.mock_calls != expected_delete_calls:
#         errors.append(
#             'data set delete not called with expected args. {0} == {1}'.format(
#                 str(patched_delete.mock_calls),
#                 str(expected_delete_calls)
#             )
#         )

#     assert not errors, '\n'.join(errors)


# def test_replace_data_set_unsafe_writes_create_temp_fail_unsafe_fails(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     errors = []
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     unsafe_writes = True
#     extra_args = {}
#     patched_temp_name = mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(IMPORT_NAME), create=True, side_effect=[
#                                 ds.DatasetCreateError(temp_name, 1), ds.DatasetCreateError(name, 1)])
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)

#     data_set_create_fail = False
#     try:
#         ds.replace_data_set(name=name,
#                         extra_args=extra_args)
#     except ds.DatasetCreateError:
#         data_set_create_fail = True

#     if not data_set_create_fail:
#         errors.append(
#             'Datasets.create should raise Exception. Assertion failed.')

#     if patched_temp_name.call_count != 1:
#         errors.append('Datasets.temp_name call count {0} != 1'.format(
#             str(patched_temp_name.call_count)))

#     expected_create_calls = [
#         call(temp_name, extra_args), call(name, extra_args)]
#     if patched_create.mock_calls != expected_create_calls:
#         errors.append(
#             'data set create not called with expected args. {0} == {1}'.format(
#                 str(patched_create.mock_calls),
#                 str(expected_create_calls)
#             )
#         )
#     expected_delete_calls = [call(name)]
#     if patched_delete.mock_calls != expected_delete_calls:
#         errors.append(
#             'data set delete not called with expected args. {0} == {1}'.format(
#                 str(patched_delete.mock_calls),
#                 str(expected_delete_calls)
#             )
#         )

#     assert not errors, '\n'.join(errors)

# * Testing ensure_data_set_absent()


def test_ensure_data_set_absent_exists_prior_delete_succeeds(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=True)
    patched_delete = mocker.patch('{0}.delete_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_absent(name)
    assert patched_delete.call_count == 1
    assert result == True


def test_ensure_data_set_absent_does_not_exist_prior(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=False)
    patched_delete = mocker.patch('{0}.delete_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_absent(name)
    assert patched_delete.call_count == 0
    assert result == False


def test_ensure_data_set_absent_exists_prior_delete_fails(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=True)
    mocker.patch('zoautil_py.Datasets.delete', create=True, return_value=1)
    with pytest.raises(ds.DatasetDeleteError):
        ds.ensure_data_set_absent(name)

# * Testing ensure_data_set_present()


def test_ensure_data_set_present_exists_prior_no_replace(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    replace = False
    unsafe_writes = False
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=True)
    patched_replace = mocker.patch('{0}.replace_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_create = mocker.patch('{0}.create_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_present(
        name=name, replace=replace)
    assert patched_replace.call_count == 0
    assert patched_create.call_count == 0
    assert result == False


def test_ensure_data_set_present_exists_prior_no_replace_unsafe_writes(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    replace = False
    unsafe_writes = True
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=True)
    patched_replace = mocker.patch('{0}.replace_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_create = mocker.patch('{0}.create_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_present(
        name=name, replace=replace)
    assert patched_replace.call_count == 0
    assert patched_create.call_count == 0
    assert result == False


def test_ensure_data_set_present_does_not_exist_prior_no_replace(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    replace = False
    unsafe_writes = False
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=False)
    patched_replace = mocker.patch('{0}.replace_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_create = mocker.patch('{0}.create_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_present(
        name=name, replace=replace)
    assert patched_replace.call_count == 0
    assert patched_create.call_count == 1
    assert result == True


def test_ensure_data_set_present_does_not_exist_prior_replace(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    replace = True
    unsafe_writes = False
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=False)
    patched_replace = mocker.patch('{0}.replace_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_create = mocker.patch('{0}.create_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_present(
        name=name, replace=replace)
    assert patched_replace.call_count == 0
    assert patched_create.call_count == 1
    assert result == True


def test_ensure_data_set_present_exists_prior_replace_safe_writes_succeeds(zos_import_mocker):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    name = 'somename'
    replace = True
    unsafe_writes = False
    mocker.patch('{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=True)
    patched_replace = mocker.patch('{0}.replace_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_create = mocker.patch('{0}.create_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    result = ds.ensure_data_set_present(
        name=name, replace=replace)
    assert patched_replace.call_count == 1
    assert patched_create.call_count == 0
    assert result == True


# def test_ensure_data_set_present_exists_prior_replace_safe_writes_fails(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     replace = True
#     unsafe_writes = False
#     mocker.patch('{0}.data_set_exists'.format(
#         IMPORT_NAME), create=True, return_value=True)
#     mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, side_effect=[ds.DatasetCreateError(name, 1), 0])
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     with pytest.raises(ds.DatasetCreateError):
#         ds.ensure_data_set_present(name=name, replace=replace,
#                             unsafe_writes=unsafe_writes)
#     assert patched_delete.call_count == 0
#     assert patched_create.call_count == 1


# def test_ensure_data_set_present_exists_prior_replace_safe_writes_fails(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     replace = True
#     unsafe_writes = False
#     mocker.patch('{0}.data_set_exists'.format(
#        IMPORT_NAME), create=True, return_value=True)
#     patched_temp_name = mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, side_effect=[ds.DatasetCreateError(name, 1), 0])
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     with pytest.raises(ds.DatasetCreateError):
#         ds.ensure_data_set_present(name=name, replace=replace,
#                             unsafe_writes=unsafe_writes)
#     assert patched_delete.call_count == 0
#     assert patched_create.call_count == 1


# def test_ensure_data_set_present_exists_prior_replace_unsafe_writes_succeeds(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     replace = True
#     unsafe_writes = True
#     mocker.patch('{0}.data_set_exists'.format(
#         IMPORT_NAME), create=True, return_value=True)
#     mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, side_effect=[ds.DatasetCreateError(name, 1), 0])
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     result = ds.ensure_data_set_present(
#         name=name, replace=replace)
#     assert patched_delete.call_count == 1
#     assert patched_create.call_count == 2
#     assert result == True


# def test_ensure_data_set_present_exists_prior_replace_unsafe_writes_fails(zos_import_mocker):
#     mocker, importer = zos_import_mocker
#     ds = importer(IMPORT_NAME)
#     name = 'somename'
#     temp_name = 'tmpdsname'
#     replace = True
#     unsafe_writes = False
#     mocker.patch('{0}.data_set_exists'.format(
#         IMPORT_NAME), create=True, return_value=True)
#     mocker.patch(
#         'zoautil_py.Datasets.temp_name', create=True, return_value=temp_name)
#     patched_create = mocker.patch('{0}.create_data_set'.format(
#         IMPORT_NAME), create=True, side_effect=[ds.DatasetCreateError(name, 1), 0])
#     patched_delete = mocker.patch('{0}.delete_data_set'.format(
#         IMPORT_NAME), create=True, return_value=0)
#     with pytest.raises(ds.DatasetCreateError):
#         ds.ensure_data_set_present(name=name, replace=replace,
#                             unsafe_writes=unsafe_writes)
#     assert patched_delete.call_count == 0
#     assert patched_create.call_count == 1


# * Testing perform_data_set_operations()

# Commented out test_data items are no longer valid because 
# perform_data_set_operations() now expects to be provided a list of data sets 
test_data = [
    # ('somename', 'present', 1, 0),
    # ('', 'present', 0, 0),
    # (1234, 'present', 1, 0),
    ([], 'present', 0, 0),
    # (['', 'somename2', 'somename3'], 'present', 2, 0),
    # ([1231, 'somename2', ''], 'present', 2, 0),
    (['somename1', 'somename2', 'somename3'], 'present', 3, 0),
    # ('somename', 'absent', 0, 1),
    # ('', 'absent', 0, 0),
    # (1234, 'absent', 0, 1),
    ([], 'absent', 0, 0),
    (['somename1', 'somename2', 'somename3'], 'absent', 0, 3),
    # (['', 'somename2', 'somename3'], 'absent', 0, 2),
    ([1231, 'somename2'], 'absent', 0, 2),
]
@pytest.mark.parametrize("name,state,ensure_present_call_count,ensure_absent_call_count", test_data)
def test_perform_data_set_operations_correct_branches_taken(zos_import_mocker, name, state, ensure_present_call_count, ensure_absent_call_count):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    args = {
        'name': name,
        'state': state
    }
    patched_ensure_present = mocker.patch('{0}.ensure_data_set_present'.format(
        IMPORT_NAME), create=True, return_value=True)
    patched_ensure_absent = mocker.patch('{0}.ensure_data_set_absent'.format(
        IMPORT_NAME), create=True, return_value=True)
    ds.perform_data_set_operations(**args)
    assert patched_ensure_present.call_count == ensure_present_call_count
    assert patched_ensure_absent.call_count == ensure_absent_call_count


test_data = [
    (
        {
            'name': ['somename'],
            'state': 'present',
            'replace': True,
            'unsafe_writes': False,
            'some_other_arg1': 12,
            'some_other_arg2': 'somethinghere'
        }
    )
]
# TODO: add more testcases to this, expand arguments to ensure value propagation to correct functions
@pytest.mark.parametrize("args", test_data)
def test_perform_data_set_operations_dict_unpacking(zos_import_mocker, args):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    mocker.patch(
        '{0}.data_set_exists'.format(
        IMPORT_NAME), create=True, return_value=True)
    patched_create = mocker.patch('{0}.create_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_delete = mocker.patch('{0}.delete_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    patched_replace = mocker.patch('{0}.replace_data_set'.format(
        IMPORT_NAME), create=True, return_value=0)
    ds.perform_data_set_operations(**args)
    assert patched_create.call_count == 0
    assert patched_replace.call_count == 1
    assert patched_delete.call_count == 0
