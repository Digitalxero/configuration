from threading import RLock

__all__ = ['TagRegistry']


class TagRegistry(object):
    """
    This is a Borg style singleton
    http://www.aleax.it/Python/5ep.html
    Basically since the __* attributes are defined as a mutable class attribute
    all instances of this class share the state of __*
    To make this threadsafe we wrap the only way to add tags in an RLock
    """
    __constructor = {}
    __representer = {}
    __multi_constructor = {}
    __multi_representer = {}
    __lock = RLock()

    @classmethod
    def register_tag(cls, tag=None, data_type=None,
                     constructor=None, representer=None):
        with cls.__lock:
            if data_type:
                cls.__representer[data_type] = representer

            if tag:
                tags = tag.split(',')
                for tag in tags:
                    cls.__constructor[tag] = constructor

    @classmethod
    def register_multi_tag(cls, tag=None, data_type=None,
                           constructor=None, representer=None):
        with cls.__lock:
            if data_type:
                cls.__multi_representer[data_type] = representer

            if tag:
                tags = tag.split(',')
                for tag in tags:
                    cls.__multi_constructor[tag] = constructor

    def setup_yaml(self, yaml):
        sc = yaml.constructor.SafeConstructor
        sc.add_constructor(None, _safe_unknown)

        for tag, constructor in self.tag_constructors:
            tag = ':'.join(['tag', 'yaml.org,2002', tag, ''])
            yaml.add_constructor(tag, constructor)

        for tag, constructor in self.multi_tag_constructors:
            tag = ':'.join(['tag', 'yaml.org,2002', tag, ''])
            yaml.add_multi_constructor(tag, constructor)

        for data_type, representer in self.tag_representers:
            yaml.add_representer(data_type, representer)

        for data_type, representer in self.multi_tag_representers:
            yaml.add_multi_representer(data_type, representer)

    @property
    def tag_constructors(self):
        # py3 yield from self.__constructor.items()
        for k, v, in self.__constructor.items():
            yield (k, v)

    @property
    def tag_representers(self):
        # py3 yield from self.__representer.items()
        for k, v, in self.__representer.items():
            yield (k, v)

    @property
    def multi_tag_constructors(self):
        # py3 yield from self.__multi_constructor.items()
        for k, v, in self.__multi_constructor.items():
            yield (k, v)

    @property
    def multi_tag_representers(self):
        # py3 yield from self.__multi_representer.items()
        for k, v, in self.__multi_representer.items():
            yield (k, v)


def _safe_unknown(loader, node):
    parts = node.tag.split(':')
    prefix = ''
    if parts[0] == 'tag':
        prefix += '!!'
        parts = parts[2:]

    tag = parts[0]
    parts = parts[1:]
    return ''.join([prefix, tag, ':'] + parts)
