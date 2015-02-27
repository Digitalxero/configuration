from ._base import TagRegistry
from ..errors import ConfigurationError

__all__ = []


class Ref(object):
    def __init__(self, ref):
        self.suffix = ''
        self.ref = ref
        if ':' in ref:
            parts = ref.split(':')
            if len(parts) == 2:
                self.ref, self.suffix = parts
            else:
                self.ref = parts[0]
                self.suffix = Ref(':'.join(parts[2:]))

    @classmethod
    def construct(cls, loader, suffix, node):
        return cls(suffix)

    @classmethod
    def represent(cls, dumper, ref):
        if isinstance(ref.suffix, Ref):
            ref.suffix = '{}'.format(cls.represent(dumper, ref.suffix))

        return dumper.represent_scalar('tag:yaml.org,2002:ref:',
                                       ''.join([ref.ref, ':', ref.suffix]))

    # Python Descriptor syntax
    def __get__(self, instance, owner):
        base = instance
        parts = self.ref.split(".")
        parts.reverse()
        while parts:
            s = parts.pop()
            try:
                instance = getattr(instance, s)
            except AttributeError:
                msg = 'Unable to find {}'.format(self.ref)
                raise ConfigurationError(msg)

        if isinstance(instance, str):
            suffix = self.suffix
            if isinstance(self.suffix, Ref):
                suffix = self.suffix.__get__(base, owner)

            instance += '{}'.format(suffix)

        return instance

TagRegistry.register_multi_tag('ref', Ref, Ref.construct, Ref.represent)
