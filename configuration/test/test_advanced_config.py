import os
import sys
import pytest
import tempfile

from configuration import Configuration, ConfigurationError


@pytest.fixture(scope='session')
def cfg_file(request):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tmp.write("""
#module attribute
python_name: !!python/name:sys.stdout

# object must be callable, but it does NOT call it
python_object1: !!python/object:test_advanced_config.MyTest1
  value: test passed

#test instantiating a class
python_object2: !!python/object/apply:test_advanced_config.MyTest2
  args:
    - positional value
  kwds:
    value: kwarg value

#test instantiating a class
python_object3: !!python/object/apply:test_advanced_config.MyTest2
    - positional value2
    - kwarg value2
    """)
    tmp.close()

    def fin():
        os.remove(tmp.name)

    request.addfinalizer(fin)

    return tmp.name


@pytest.fixture
def bad_cfg_file(request):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tmp.write("""
test: !!python/name:bad.yaml.format
    """)
    tmp.close()

    def fin():
        os.remove(tmp.name)

    request.addfinalizer(fin)

    return tmp.name


def test_config_raises_ConfigurationError_for_bad_tag_call(bad_cfg_file):
    with pytest.raises(ConfigurationError):
        config = Configuration(bad_cfg_file)


def test_config_parse_python_name(cfg_file):
    config = Configuration(cfg_file)

    assert config.python_name is sys.stdout


def test_config_parse_python_object_create_instance(cfg_file):
    config = Configuration(cfg_file)

    assert config.python_object1.value == 'test passed'


def test_config_parse_python_object_accepts_args_and_kwargs(cfg_file):
    config = Configuration(cfg_file)

    assert config.python_object2.kwarg_value == 'kwarg value'
    assert config.python_object2.positional_arg == 'positional value'


def test_config_parse_python_object_accepts_pure_positional(cfg_file):
    config = Configuration(cfg_file)

    assert config.python_object3.kwarg_value == 'kwarg value2'
    assert config.python_object3.positional_arg == 'positional value2'


# classes used for testing
class MyTest1:
    pass


class MyTest2:
    positional_arg = 'Bad'
    kwarg_value = 'Bad'

    def __init__(self, positional_arg, value=None):
        self.positional_arg = positional_arg
        self.kwarg_value = value
