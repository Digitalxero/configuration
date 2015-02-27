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
python_object1: !!object:sys.stdout

# object must be importable
python_object2: !!object:test_object_tag.MyTest1
    value: test passed

#test instantiating a class
python_instance1: !!object/call:test_object_tag.MyTest2
    args:
        - positional value
    kwargs:
        value: kwarg value

#test instantiating a class
python_instance2: !!object/call:test_object_tag.MyTest2
    - positional value2
    - kwarg value2

#test instantiating a class
python_instance3: !!object/call:test_object_tag.MyTest3
    kwarg1: kwargs value 1
    kwarg2: kwargs value 2
    kwarg4: kwargs value 4
    kwarg3: kwargs value 3

#test lazy instantiating a class
python_lazy1: !!object/lazy:test_object_tag.function
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
test: !!object:bad.item
    """)
    tmp.close()

    def fin():
        os.remove(tmp.name)

    request.addfinalizer(fin)

    return tmp.name


def test_object_raises_ConfigurationError_when_not_importable(bad_cfg_file):
    with pytest.raises(ConfigurationError) as e:
        config = Configuration(bad_cfg_file)

    assert '{}'.format(e.value.args[0]) == 'Failed to import bad.item'


def test_basic_object_tag(cfg_file):
    config = Configuration(cfg_file)
    print(config)

    assert config.python_object1 is sys.stdout


def test_object_tag_does_not_call_or_instantiate(cfg_file):
    config = Configuration(cfg_file)

    assert not isinstance(config.python_object2, MyTest1)


def test_object_tag_can_set_attributes(cfg_file):
    config = Configuration(cfg_file)

    assert config.python_object2.value == 'test passed'


def test_object_call_instantiates_with_args_and_kwargs(cfg_file):
    config = Configuration(cfg_file)

    assert isinstance(config.python_instance1, MyTest2)
    assert config.python_instance1.positional_arg == 'positional value'
    assert config.python_instance1.kwarg_value == 'kwarg value'


def test_object_call_only_creates_one_instance(cfg_file):
    config = Configuration(cfg_file)

    instance1 = config.python_instance1
    instance2 = config.python_instance1
    assert instance1 is instance2


def test_object_call_instantiates_with_args_only(cfg_file):
    config = Configuration(cfg_file)

    assert isinstance(config.python_instance2, MyTest2)
    assert config.python_instance2.positional_arg == 'positional value2'
    assert config.python_instance2.kwarg_value == 'kwarg value2'


def test_object_call_instantiates_with_kwargs_only(cfg_file):
    config = Configuration(cfg_file)

    assert isinstance(config.python_instance3, MyTest3)
    assert config.python_instance3.kwarg1 == 'kwargs value 1'
    assert config.python_instance3.kwarg2 == 'kwargs value 2'
    assert config.python_instance3.kwarg3 == 'kwargs value 3'
    assert config.python_instance3.kwarg4 == 'kwargs value 4'


def test_object_lazy_is_really_lazy(cfg_file):
    global X
    config = Configuration(cfg_file)

    assert X == 10

    X = 'Test Bassed'
    assert config.python_lazy1 == 'Test Bassed'
    X = 10


def test_object_lazy_does_not_call_more_then_once(cfg_file):
    global X
    config = Configuration(cfg_file)

    assert X == 10

    X = 'Test Bassed'
    assert config.python_lazy1 == 'Test Bassed'

    X = 10
    assert config.python_lazy1 == 'Test Bassed'


# classes used for testing
X = 10


class MyTest1:
    pass


class MyTest2:
    positional_arg = 'Bad'
    kwarg_value = 'Bad'

    def __init__(self, positional_arg, value=None):
        self.positional_arg = positional_arg
        self.kwarg_value = value


class MyTest3:
    def __init__(self, kwarg1=None, kwarg2=None, kwarg3=None, kwarg4=None):
        self.kwarg1 = kwarg1
        self.kwarg2 = kwarg2
        self.kwarg3 = kwarg3
        self.kwarg4 = kwarg4


def function():
    global X
    return X
