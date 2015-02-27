
import yaml
import collections

from .tags import TagRegistry
from .errors import ConfigurationError

__all__ = ['Configuration']


class Configuration(object):
    __raw = None
    __parsed = None

    def __init__(self, *cfg_files):
        super(Configuration, self).__init__()

        self.__raw = {}
        self.__parsed = _YAMLObj()

        for cfg_file in cfg_files:
            self.load(cfg_file)

    def load(self, cfg_file):
        tags = TagRegistry()
        tags.setup_yaml(yaml)

        with open(cfg_file) as f:
            data = f.read()
            # yaml.safe_load loads with none of the custom tags
            try:
                self.__raw.update(yaml.safe_load(data))
            except ValueError as e:
                raise ConfigurationError(*e.args)

            # yaml.load loads with all the custom tags we have registered
            try:
                self.__parsed.update(yaml.load(data))
            except yaml.YAMLError as e:
                raise ConfigurationError(e.problem)

    def __iter__(self):
        # py3 yield from self.__parsed.items()
        for k, v, in self.__parsed.items():
            yield (k, v)

    def __contains__(self, key):
        return key in self.__parsed

    def __len__(self):
        return len(self.__parsed)

    def __getattr__(self, name):
        if hasattr(self.__parsed, name):
            return getattr(self.__parsed, name)

        try:
            return super(Configuration, self).__getattribute__(name)
        except AttributeError as e:
            raise ConfigurationError(*e.args)

    def __str__(self):
        return yaml.dump(self.__parsed, default_flow_style=False, indent=2,
                         allow_unicode=True)

    def __repr__(self):
        return repr(self.__raw)


class _YAMLObj(dict):
    def __init__(self, obj=None, **kwargs):
        super(_YAMLObj, self).__init__()
        self.update(obj)
        self.update(**kwargs)

    def update(self, other=None, **kwargs):
        if isinstance(other, collections.Mapping):
            self.update(**other)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        if isinstance(value, collections.Mapping):
            value = self.__class__(value)
        elif isinstance(value, (list, tuple)):
            value = [self.__class__(x)
                     if isinstance(x, dict) else x for x in value]

        super(_YAMLObj, self).__setattr__(name, value)
        super(_YAMLObj, self).__setitem__(name, value)

    def __getattribute__(self, name):
        "Emulate type_getattro() in Objects/typeobject.c"
        v = super(_YAMLObj, self).__getattribute__(name)

        if hasattr(v, '__get__'):
            return v.__get__(self, _YAMLObj)

        return v

    __setitem__ = __setattr__
    __getitem__ = __getattribute__

yaml.add_representer(_YAMLObj, yaml.representer.SafeRepresenter.represent_dict)
