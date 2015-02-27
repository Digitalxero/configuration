import os
import pytest
import tempfile

from configuration import Configuration, ConfigurationError


@pytest.fixture(scope='session')
def cfg_file(request):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tmp.write("""
bad_tag: !!blablabla: some value
    """)
    tmp.close()

    def fin():
        os.remove(tmp.name)

    request.addfinalizer(fin)

    return tmp.name


def test_config_raises_ConfigurationError_for_bad_tag(cfg_file):
    with pytest.raises(ConfigurationError):
        config = Configuration(cfg_file)
