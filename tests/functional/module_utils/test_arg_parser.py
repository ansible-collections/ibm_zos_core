# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
import pytest
from ibm_zos_core.plugins.module_utils.better_arg_parser import BetterArgParser

arg_defs = {
    "batch":{
        "arg_type":"list",
        "elements":"dict",
        "options":{
            "name":{
                "required":True,
            },
            "state":{
                "arg_type":"str",
                "default":"present",
            },
            "type":{
                "arg_type":"str",
                "required":False,
            },
            "size":{
                "arg_type":"str",
                "required":False
            },
            "format":{
                "arg_type":"str",
                "required":False,
            },
            "data_class":{
                "arg_type":"str",
                "required":False,
            },
            "record_length":{
                "arg_type":"int",
            },
            "replace":{
                "arg_type":"bool",
                "default":False,
            },
        },
    },
    "name":{
        "arg_type":"str"
    },
    "state":{
        "arg_type":"str",
        "default":"present",
        # choices=['present','absent']
    },
    "type":{
        "arg_type":"str",
        "required":False,
    },
    "size":{
        "arg_type":"str",
        "required":False
    },
    "format":{
        "arg_type":"str",
        "required":False,
    },
    "data_class":{
        "arg_type":"str",
        "required":False,
        "aliases":["dataclas"],
        "dependencies":["record_length", "state"],
    },
    "record_length":{
        "arg_type":"int", "aliases":["length", "lrecl"], "dependencies":["replace", "size"]
    },
    "replace":{
        "arg_type":"bool",
        "default":False,
        "dependencies":[]
    },
}


def test_default_top_level():
    arg_defs = {
        "state":{
            "arg_type":"str",
            "default":"present"
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({})
    assert result.get("state") == "present"


def test_required_top_level_no_default():
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({})


def test_required_top_level_with_default():
    default_name = "samplename"
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":default_name
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({})
    assert result.get("name") == default_name


arg_defs_1 = {
    "name":{
        "arg_type":"str",
        "required":True,
        "default":"samplename",
        "dependencies":["date"]
    },
    "date":{
        "arg_type":"str",
        "default":"may 1, 2020",
        "dependencies":["name"]
    },
}

arg_defs_2 = {
    "name":{
        "arg_type":"str",
        "required":True,
        "default":"samplename",
        "dependencies":["time"]
    },
    "date":{
        "arg_type":"str",
        "default":"may 1, 2020",
        "dependencies":["name"]
    },
    "time":{
        "arg_type":"int",
        "default":"3945297",
        "dependencies":["date"]
    },
}


@pytest.mark.parametrize("arg_defs", [arg_defs_1, arg_defs_2])
def test_cyclic_dependency_catching(arg_defs):
    with pytest.raises(RuntimeError):
        BetterArgParser(arg_defs)


def test_unknown_arg_ignore():
    default_name = "samplename"
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":default_name
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"otherarg": "testing"})
    assert "otherarg" not in result.keys()


provided_args_1 = {
    "name": "somename",
    "dt": "jan 3 2017",
    "sometime": "97887"
}
provided_args_2 = {
    "date": "jan 3 2017",
    "sometime": "97887"
}
provided_args_3 = {
    "bestdate": "jan 3 2017",
    "datetime": "97887"
}
provided_args_4 = {
    "datetime": "97887"
}


@pytest.mark.parametrize(
    "provided_args",
    [provided_args_1, provided_args_2, provided_args_3, provided_args_4],
)
def test_alias_resolution(provided_args):
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":"samplename",
        },
        "date":{
            "arg_type":"str",
            "default":"may 1, 2020",
            "aliases":["bestdate", "dt"]
        },
        "time":{
            "arg_type":"int",
            "default":"3945297",
            "aliases":["sometime", "datetime"]
        },
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args(provided_args)
    result_simple = [str(x) for x in result.values()]
    for val in provided_args.values():
        assert str(val) in result_simple
    assert "name" in result.keys()
    assert "date" in result.keys()
    assert "time" in result.keys()


@pytest.mark.parametrize("arg_val", ["asdfadfa234", "#@#$@fasdfa"])
def test_str_type_validation_success(arg_val):
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"name": arg_val})
    assert result.get("name") == arg_val


def dummyfunc():
    pass


@pytest.mark.parametrize("arg_val", [dummyfunc, 32143, True])
def test_str_type_validation_failure(arg_val):
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"name": arg_val})


@pytest.mark.parametrize("arg_val", [231, "3124", 0])
def test_int_type_validation_success(arg_val):
    arg_defs = {
        "somenum":{
            "arg_type":"int",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"somenum": arg_val})
    assert result.get("somenum") == int(arg_val)


@pytest.mark.parametrize("arg_val", [dummyfunc, "3341h132j1231x", True])
def test_int_type_validation_failure(arg_val):
    arg_defs = {
        "somenum":{
            "arg_type":"int",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"somenum": arg_val})


@pytest.mark.parametrize("arg_val", [True, False])
def test_bool_type_validation_success(arg_val):
    arg_defs = {
        "somebool":{
            "arg_type":"bool",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"somebool": arg_val})
    assert result.get("somebool") == arg_val


@pytest.mark.parametrize(
    "arg_val", [dummyfunc, "3341h132j1231x", 0, 1, "True", "false"]
)
def test_bool_type_validation_failure(arg_val):
    arg_defs = {
        "somebool":{
            "arg_type":"bool",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"somebool": arg_val})


def always_returns_true(value, dependencies):
    return True


def always_returns_false(value, dependencies):
    return False


def always_returns_same_val(value, dependencies):
    return value


@pytest.mark.parametrize(
    ("arg_type", "expected"),
    [
        (always_returns_true, True),
        (always_returns_false, False),
        (always_returns_same_val, "testing"),
    ],
)
def test_basic_user_provided_type_func(arg_type, expected):
    arg_defs = {
        "someval":{
            "arg_type":arg_type,
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"someval": expected})
    assert result.get("someval") == expected


def make_uppercase(value, dependencies):
    return str(value).upper()


def is_dependency_uppercase(value, dependencies):
    if re.match(r"[^a-z]+", dependencies.get("uppername")):
        return True
    return False


def test_user_provided_type_func_with_dependencies():
    arg_defs = {
        "uppername":{
            "arg_type":make_uppercase,
            "required":True,
        },
        "verifier":{
            "arg_type":is_dependency_uppercase,
            "required":True,
            "dependencies":["uppername"]
        },
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"uppername": "dadafasdf", "verifier": "doesntmatter"})
    assert result.get("verifier")


def test_user_provided_type_func_with_dependencies_make_fail():
    arg_defs = {
        "uppername":{
            "arg_type":make_uppercase,
            "required":True,
            "dependencies":["verifier"]
        },
        "verifier":{
            "arg_type":is_dependency_uppercase,
            "required":True,
        },
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(TypeError):
        parser.parse_args({"uppername": "dadafasdf", "verifier": "doesntmatter"})


def test_dependent_required():
    arg_defs = {
        "uppername":{
            "arg_type":"str",
            "required":True,
        },
        "verifier":{
            "arg_type":"str",
            "required":is_dependency_uppercase,
            "dependencies":["uppername"]
        },
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"uppername": "dadafasdf"})
    assert result.get("verifier") is None


def test_dependent_required_fail():
    arg_defs = {
        "uppername":{
            "arg_type":"str",
            "required":True,
        },
        "verifier":{
            "arg_type":"str",
            "required":is_dependency_uppercase,
            "dependencies":["uppername"]
        },
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        result = parser.parse_args({"uppername": "DAFASDFA"})


@pytest.mark.parametrize(
    ("arg_val", "expected"), [("asdfafad", False), ("DFDAFFDSA", True)]
)
def test_dependent_default(arg_val, expected):
    arg_defs = {
        "uppername":{
            "arg_type":"str",
            "required":True,
        },
        "verifier":{
            "arg_type":"bool",
            "default":is_dependency_uppercase,
            "dependencies":["uppername"]
        },
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"uppername": arg_val})
    assert result.get("verifier") == expected


def test_list_of_strings_success():
    arg_defs = {
        "names":{
            "arg_type":"list",
            "elements":"str",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"names": ["name1", "name2", "name3", "name4"]})
    assert len(result.get("names")) == 4


def test_list_of_strings_failure():
    arg_defs = {
        "names":{
            "arg_type":"list",
            "elements":"str",
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"names": [1, True, "name3", "name4"]})


def test_list_of_strings_function_for_arg_type_success():
    arg_defs = {
        "names":{
            "arg_type":"list",
            "elements":make_uppercase,
            "required":True,
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"names": ["name1", "name2", "name3", "name4"]})
    assert len(result.get("names")) == 4
    for name in result.get("names"):
        assert name == name.upper()


def test_list_of_dicts_success():
    arg_defs = {
        "people":{
            "arg_type":"list",
            "elements":"dict",
            "options":{
                "name":{
                    "arg_type":"str",
                    "required":True,
                    "default":"testname"
                },
                "age":{
                    "arg_type":"int",
                    "required":False
                },
            },
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args(
        {
            "people": [
                {"name": "blake", "age": 23},
                {"name": "oldguy", "age": 95},
                {"age": 30},
            ]
        }
    )
    assert len(result.get("people")) == 3


def to_string(value, dependencies):
    return str(value)


def test_list_of_dicts_nested_function_arg_type():
    arg_defs = {
        "people":{
            "arg_type":"list",
            "elements":"dict",
            "options":{
                "name":{
                    "arg_type":"str",
                    "required":True,
                    "default":"testname"
                },
                "age":{
                    "arg_type":to_string,
                    "required":False
                },
            },
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args(
        {
            "people": [
                {"name": "blake", "age": 23},
                {"name": "oldguy", "age": 95},
                {"age": 30},
                {"name": "unknown age guy"},
            ]
        }
    )
    assert len(result.get("people")) == 4
    for person in result.get("people"):
        if person.get("age"):
            assert isinstance(person.get("age"), str)


def test_dict_of_dict():
    arg_defs = {
        "person":{
            "arg_type":"dict",
            "options":{
                "name":{
                    "arg_type":"str",
                    "required":True,
                    "default":"testname"
                },
                "age":{
                    "arg_type":"int",
                    "required":False
                },
                "address":{
                    "arg_type":"dict",
                    "options":{
                        "street":{
                            "arg_type":"str"
                        },
                        "number":{
                            "arg_type":"int"
                        }
                    },
                },
            },
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args(
        {
            "person": {
                "name": "blake",
                "age": 23,
                "address": {"street": "bailey ave", "number": 555},
            }
        }
    )
    assert result.get("person").get("address").get("number") == 555


def test_dict_of_dict_fail_on_nested_arg_type():
    arg_defs = {
        "person":{
            "arg_type":"dict",
            "options":{
                "name":{
                    "arg_type":"str",
                    "required":True,
                    "default":"testname"
                },
                "age":{
                    "arg_type":"int",
                    "required":False
                },
                "address":{
                    "arg_type":"dict",
                    "options":{
                        "street":{
                            "arg_type":"str"
                        },
                        "number":{
                            "arg_type":"str"
                        }
                    },
                },
            },
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args(
            {
                "person": {
                    "name": "blake",
                    "age": 23,
                    "address": {"street": "bailey ave", "number": 555},
                }
            }
        )


def test_cyclic_dependency_in_nested_dict():
    arg_defs = {
        "person":{
            "arg_type":"dict",
            "options":{
                "name":{
                    "arg_type":"str",
                    "required":True,
                    "default":"testname",
                    "dependencies":["age"],
                },
                "age":{
                    "arg_type":"int",
                    "required":False,
                    "dependencies":["name"]
                },
                "address":{
                    "arg_type":"dict",
                    "options":{
                        "street":{
                            "arg_type":"str"
                        },
                        "number":{
                            "arg_type":"str"
                        }
                    },
                },
            },
        }
    }
    with pytest.raises(RuntimeError):
        BetterArgParser(arg_defs)


def test_invalid_dependency_independent_does_not_exist():
    arg_defs = {
        "person":{
            "arg_type":"str",
            "dependencies":["nonexistent"]
        },
        "animal":{
            "arg_type":"str",
            "dependencies":["person"]
        },
    }
    with pytest.raises(ValueError):
        BetterArgParser(arg_defs)


def test_choices_success():
    arg_defs = {
        "person":{
            "arg_type":"str",
            "choices":["blake", "ping", "crystal"]
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"person": "blake"})
    assert result.get("person") == "blake"


def test_choices_fail():
    arg_defs = {
        "person":{
            "arg_type":"str",
            "choices":["blake", "ping", "crystal"]
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"person": "bob"})


arg_defs = {
    "name":{
        "arg_type":"str",
        "required":True,
        "default":"samplename",
        "dependencies":["time"]
    },
    "date":{
        "arg_type":"str",
        "default":"may 1, 2020",
        "dependencies":["name"]
    },
    "time":{
        "arg_type":"int",
        "default":"3945297",
        "dependencies":["date"]
    },
}


def test_second_level_defaults():
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":"samplename"
        },
        "date":{
            "arg_type":"dict",
            "options":{
                "month":{
                    "arg_type":"str",
                    "default":"hello"
                },
                "day":{
                    "arg_type":"int",
                    "default":1
                },
            },
        },
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"name": "blake", "date": {"month": "may"}})
    assert result.get("date").get("day") is not None


def test_mutually_exclusive_parameters_two_values_set_top_level():
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":"samplename"
        },
        "date":{
            "arg_type":"str",
            "default":"may 1, 2020"
        },
        "time":{
            "arg_type":"int",
            "default":"3945297"
        },
        "mutually_exclusive":[["date", "time"]],
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"date": "tuesday", "time": 5000})


def test_mutually_exclusive_parameters_two_values_set_top_level_defaults():
    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":"samplename"
        },
        "date":{
            "arg_type":"str",
            "default":"may 1, 2020"
        },
        "time":{
            "arg_type":"int",
            "default":"3945297"
        },
        "mutually_exclusive":[["date", "time"]],
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({})


def test_custom_defined_values_top_level():
    def special_names_get_uppercase(value, dependencies, kwargs):
        if value in kwargs.get("special_names", []):
            return value.upper()
        return value

    arg_defs = {
        "name":{
            "arg_type":special_names_get_uppercase,
            "required":True,
            "default":"samplename",
            "special_names":["blake", "demetri", "ping", "crystal", "asif", "luke"],
        },
        "date":{
            "arg_type":"str",
            "default":"may 1, 2020"
        },
        "time":{
            "arg_type":"int"
        },
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"name": "blake"})
    assert result.get("name") == "BLAKE"
    result = parser.parse_args({"name": "john"})
    assert result.get("name") == "john"


def test_custom_defined_values_top_level_required():
    def special_user(value, dependencies, kwargs):
        if dependencies.get("name") in kwargs.get("special_names", []):
            return True
        return False

    arg_defs = {
        "name":{
            "arg_type":"str",
            "required":True,
            "default":"samplename",
        },
        "date":{
            "arg_type":"str",
            "default":"may 1, 2020"
        },
        "time":{
            "arg_type":"int"
        },
        "age":{
            "arg_type":"int",
            "required":special_user,
            "dependencies":["name"],
            "special_names":["blake", "demetri", "ping", "crystal", "asif", "luke"],
        },
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"name": "blake"})
    result = parser.parse_args({"name": "john"})
    assert result.get("name") == "john"


def test_custom_defined_values_second_level():
    def special_names_get_uppercase(value, dependencies, kwargs):
        if value in kwargs.get("special_names", []):
            return value.upper()
        return value

    arg_defs = {
        "person":{
            "arg_type":"dict",
            "options":{
                "name":{
                    "arg_type":special_names_get_uppercase,
                    "required":True,
                    "default":"testname",
                    "special_names":[
                        "blake",
                        "demetri",
                        "ping",
                        "crystal",
                        "asif",
                        "luke",
                    ],
                },
                "age":{
                    "arg_type":"int",
                    "required":False
                },
                "address":{
                    "arg_type":"dict",
                    "options":{
                        "street":{
                            "arg_type":"str"
                        },
                        "number":{
                            "arg_type":"int"
                        }
                    },
                },
            },
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args(
        {
            "person": {
                "name": "blake",
                "age": 23,
                "address": {"street": "bailey ave", "number": 555},
            }
        }
    )
    assert result.get("person").get("name") == "BLAKE"
    result = parser.parse_args(
        {
            "person": {
                "name": "john",
                "age": 23,
                "address": {"street": "bailey ave", "number": 555},
            }
        }
    )
    assert result.get("person").get("name") == "john"


def test_username_type_valid():
    # Testing all valid characters for a TSO/RACF user.
    username = "@4$user#"

    # Mocking the arg definition from module_utils/job.py.
    arg_defs = {
        "job_id": {"arg_type": "str"},
        "owner": {"arg_type": "username_pattern"},
        "job_name": {"arg_type": "str"}
    }

    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({
        "job_id": "*",
        "owner": username,
        "job_name": "*"
    })

    # The parser should accept the username as a valid value.
    assert result.get("owner") == username


@pytest.mark.parametrize(
    ("arg_type", "name"),
    [
        ("data_set", "easy.data.set"),
        ("data_set", "$asy.d@ta.$et"),
        ("data_set", "easy.dat@.s$t"),
        ("data_set", "e##@y.dat#@.set(h$ll0)"),
        ("data_set", "easy.da-a.set(######)"),
        ("data_set", "easy.data.gdg(+2)"),
        ("data_set", "easy.data.gdg(-1)"),
        ("data_set", "easy.data.gdg(0)"),
        ("data_set_base", "easy.data.set"),
        ("data_set_base", "$asy.d@ta.$et"),
        ("data_set_base", "easy.dat@.s$t"),
        ("data_set_member", "e##@y.dat#@.set(h$ll0)"),
        ("data_set_member", "ea-y.data.set(######)"),
        ("data_set_or_path", "easy.data.set"),
        ("data_set_or_path", "$asy.d@ta.$et"),
        ("data_set_or_path", "easy.dat@.s$t"),
        ("data_set_or_path", "e##@y.d-t#@.s-t(h$ll0)"),
        ("data_set_or_path", "easy.data.set(######)"),
        ("data_set_or_path", "e##@y.dat#@.set(hello)"),
        ("data_set_or_path", "easy.data.set(helloo)"),
        ("data_set_or_path", "easy.data.gdg(+2)"),
        ("data_set_or_path", "easy.data.gdg(-1)"),
        ("data_set_or_path", "easy.data.gdg(0)"),
        ("data_set_or_path", "/usr/lpp/rsusr"),
    ],
)
def test_data_set_type_no_invalid(arg_type, name):
    arg_defs = {
        "dsname":{
            "arg_type":arg_type
        }
    }
    parser = BetterArgParser(arg_defs)
    result = parser.parse_args({"dsname": name})
    assert result.get("dsname") == name


# removing "../lpp" test, as localization fix allows this through


@pytest.mark.parametrize(
    ("arg_type", "name"),
    [
        ("data_set", "easy.data.set(helloworld)"),
        ("data_set", "$asy.d@ta.$et(--helo)"),
        ("data_set", "easy.dat@.s$t(@$%@)"),
        ("data_set", "$asy.d@ta.$et(0helo)"),
        ("data_set", "-##@y.dat#@.set(h$ll0)"),
        ("data_set", "1asy.da-a.set(######)"),
        ("data_set", "easy.data.gdg(+2+)"),
        ("data_set", "easy.data.gdg(--1)"),
        ("data_set", "easy.data.gdg(-+1)"),
        ("data_set_base", "-asy.data.set"),
        ("data_set_base", "$asy.d@ta.$etdafsfsdfad"),
        ("data_set_member", "e##@y.dat#@.set(h$l-l0)"),
        ("data_set_member", "ea-y.data.set(#########)"),
        ("data_set_or_path", "easy.data.seeeeeeeeeet"),
        ("data_set_or_path", "-asy.d@ta.$et"),
        ("data_set_or_path", "easy.dat@.s$t(-)"),
        ("data_set_or_path", "e##@y.d-t#@.s-t(h$dddll00)"),
        ("data_set_or_path", "3asy.data.set(######)"),
        ("data_set_or_path", "e#^#@y.dat#@.set(hello)"),
        ("data_set_or_path", "easy.5at@@a.set(helloo)"),
        ("data_set_or_path", "easy.data.gdg(+2+)"),
        ("data_set_or_path", "easy.data.gdg(--1)"),
        ("data_set_or_path", "easy.data.gdg(-+1)"),
        #        ("data_set_or_path", "../lpp/rsusr"),
    ],
)
def test_data_set_type_invalid(arg_type, name):
    arg_defs = {
        "dsname":{
            "arg_type":arg_type
        }
    }
    parser = BetterArgParser(arg_defs)
    with pytest.raises(ValueError):
        parser.parse_args({"dsname": name})
