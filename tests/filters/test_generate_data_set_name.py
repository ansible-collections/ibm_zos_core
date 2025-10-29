import jinja2
from filter_plugins.my_filters import repeat_as_list

def test_repeat_as_list_jinja2():
    env = jinja2.Environment()
    env.filters['repeat_as_list'] = repeat_as_list

    template = env.from_string("{{ 'core' | repeat_as_list(3) }}")
    result = template.render()
    assert result == "['core', 'core', 'core']"