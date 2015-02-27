import os
import pytest
import tempfile

from configuration import Configuration, ConfigurationError


@pytest.fixture(scope='session')
def cfg_file(request):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tmp.write("""
test_list:
  - item1
  - item2
test_str: this is a test string
test_bool1: true
test_bool2: false
test_bool3: yes
test_bool4: no
test_int: 10
test_float: 3.14159
test_dict:
  sub_item: true
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
test:bad yaml format
    """)
    tmp.close()

    def fin():
        os.remove(tmp.name)

    request.addfinalizer(fin)

    return tmp.name


def test_config_raises_ConfigurationError_for_bad_yaml_format(bad_cfg_file):
    with pytest.raises(ConfigurationError):
        config = Configuration(bad_cfg_file)


def test_config_raises_ConfigurationError_for_non_existent_item(cfg_file):
    config = Configuration(cfg_file)
    with pytest.raises(ConfigurationError):
        config.fake_item


def test_config_repr_is_set(cfg_file):
    config = Configuration(cfg_file)
    assert repr(config) == repr(config._Configuration__raw)


def test_can_iterate_over_config(cfg_file):
    config = Configuration(cfg_file)
    passed = False
    for key, value in config:
        if key == 'test_list':
            passed = True

    assert passed


def test_can_test_item_containment(cfg_file):
    config = Configuration(cfg_file)
    assert 'test_list' in config


def test_can_get_number_of_keys(cfg_file):
    config = Configuration(cfg_file)
    assert len(config) == 9


def test_config_parse_list(cfg_file):
    config = Configuration(cfg_file)

    assert config.test_list == ['item1', 'item2']


def test_config_parse_str(cfg_file):
    config = Configuration(cfg_file)

    assert config.test_str == 'this is a test string'


def test_config_parse_bool(cfg_file):
    config = Configuration(cfg_file)

    assert config.test_bool1 is True
    assert config.test_bool3 is True
    assert config.test_bool2 is False
    assert config.test_bool4 is False


def test_config_parse_int(cfg_file):
    config = Configuration(cfg_file)

    assert config.test_int == 10


def test_config_parse_float(cfg_file):
    config = Configuration(cfg_file)

    assert config.test_float == 3.14159


def test_config_parse_dict(cfg_file):
    config = Configuration(cfg_file)

    expected = {
        'sub_item': True,
    }

    assert config.test_dict == expected
    assert config.test_dict.sub_item is True
