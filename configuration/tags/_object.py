
from yaml.constructor import (ScalarNode, SequenceNode,
                              MappingNode, ConstructorError)

from ._base import TagRegistry
from ..errors import ConfigurationError

__all__ = []


class PythonObject(object):
    _object = None
    _obj_path = None
    _args = None
    _kwargs = None
    _instance = None
    _call = False
    _lazy = False

    def __init__(self, obj_path, loader, node):
        self._obj_path = obj_path
        self._object = self._find_python_name(loader, obj_path,
                                              node.start_mark)

        args = []
        kwargs = {}

        if isinstance(node, MappingNode):
            data = loader.construct_mapping(node, deep=True)
            if any(item in data for item in ['args', 'kwargs']):
                args = data.get('args', [])
                kwargs = data.get('kwargs', {})
            else:
                kwargs = data
        elif isinstance(node, SequenceNode):
            args = loader.construct_sequence(node, deep=True)

        self._args = args
        self._kwargs = kwargs

    def __get__(self, instance, owner):
        if not self._instance:
            self._instance = self._object(*self._args, **self._kwargs)

        return self._instance

    def _find_python_name(self, loader, name, mark):
        try:
            obj = loader.find_python_name(name, mark)
        except ConstructorError as e:
            msg = 'Failed to import {}'.format(name)
            raise ConfigurationError(msg, *e.args)

        return obj

    @classmethod
    def _config_instance(cls, tag, instance):
        if tag.endswith('call'):
            instance._call = True
            instance.__get__(None, None)
        elif tag.endswith('lazy'):
            instance._lazy = True
        else:
            instance._instance = instance._object
            for name, value in instance._kwargs.items():
                setattr(instance._instance, name, value)

        return instance

    @classmethod
    def construct(cls, loader, suffix, node):
        tag = node.tag.split(':')[2]
        instance = cls(suffix, loader, node)

        return cls._config_instance(tag, instance)

    @classmethod
    def represent(cls, dumper, obj):
        tag = ['tag:yaml.org,2002:object']
        if obj._lazy:
            tag.append('lazy')
        elif obj._call:
            tag.append('call')

        tag = '/'.join(tag)

        tag += ':' + obj._obj_path

        if not obj._args and not obj._kwargs:
            return dumper.represent_mapping(tag, {})
        if obj._args and obj._kwargs:
            return dumper.represent_mapping(tag, {
                'args': obj._args,
                'kwargs': obj._kwargs,
            })
        elif obj._args and not obj._kwargs:
            return dumper.represent_sequence(tag, obj._args)
        else:  # obj._kwargs and not obj._args
            return dumper.represent_mapping(tag, obj._kwargs)

TagRegistry.register_multi_tag('object,object/call,object/lazy', PythonObject,
                               PythonObject.construct,
                               PythonObject.represent)
