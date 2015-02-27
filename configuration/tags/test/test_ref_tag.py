import os
import pytest
import tempfile

from configuration import Configuration, ConfigurationError


@pytest.fixture(scope='session')
def cfg_file(request):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tmp.write("""
ref_value: !!ref:some.dot.separated.path.to.a.value
re_value_with_suffix: !!ref:some.dot.separated.path.to.a.value:my_suffix
bad_ref_value: !!ref:some.dot.separated.path.to.a.bad.value
suffix_ref_value: !!ref:some.dot.separated.path.to.a.value:!!ref:ref_value

some:
  dot:
    separated:
      path:
        to:
          a:
            value: worked
    """)
    tmp.close()

    def fin():
        os.remove(tmp.name)

    request.addfinalizer(fin)

    return tmp.name


def test_ref_tag_raises_ConfigurationError_for_bad_refrence(cfg_file):
    config = Configuration(cfg_file)
    with pytest.raises(ConfigurationError):
        test = config.bad_ref_value


def test_ref_tag_pulls_value(cfg_file):
    config = Configuration(cfg_file)
    expected = config.some.dot.separated.path.to.a.value
    print(config)

    assert config.ref_value == expected


def test_ref_tag_allows_a_suffix(cfg_file):
    config = Configuration(cfg_file)
    expected = config.some.dot.separated.path.to.a.value + 'my_suffix'

    assert config.re_value_with_suffix == expected


def test_ref_tag_allows_a_ref_as_a_suffix(cfg_file):
    config = Configuration(cfg_file)
    expected = (config.some.dot.separated.path.to.a.value
                + config.some.dot.separated.path.to.a.value)

    assert config.suffix_ref_value == expected


def test_ref_tag_value_keeps_up_with_config_changes(cfg_file):
    config = Configuration(cfg_file)
    expected = config.some.dot.separated.path.to.a.value
    new_expected = 'new_value'

    assert config.ref_value == expected

    config.some.dot.separated.path.to.a.value = new_expected

    assert config.ref_value == new_expected
    assert config.ref_value != expected
