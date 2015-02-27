from configuration.tags import TagRegistry


def test_TagRegistry_is_borg_style_singleton():
    tags1 = TagRegistry()
    tags2 = TagRegistry()
    default_constructors = {}
    default_constructors.update(tags1.tag_constructors)

    def test(*args): pass  # noqa

    tags1.register_tag(tag='test', constructor=test)

    assert tags1 is not tags2
    tag1_constructors = list(tags1.tag_constructors)
    tag2_constructors = list(tags2.tag_constructors)
    assert tag1_constructors == tag2_constructors
    tags1._TagRegistry__constructor = default_constructors


def test_TagRegistry_register_tag_representer():
    tags = TagRegistry()
    default_representers = {}
    default_representers.update(tags.tag_representers)

    def test(*args):
        pass

    tags.register_tag(None, object, None, test)

    for data_type, representer in tags.tag_representers:
        if data_type is object:
            assert representer is test

    tags._TagRegistry__representer = default_representers


def test_TagRegistry_register_tag_construct_single_tag():
    tags = TagRegistry()
    default_constructors = {}
    default_constructors.update(tags.tag_constructors)

    def test(*args):
        pass

    tags.register_tag(tag='test', constructor=test)

    for tag, constructor in tags.tag_constructors:
        if tag == 'test':
            assert constructor is test

    tags._TagRegistry__constructor = default_constructors


def test_TagRegistry_register_tag_construct_multi_tag():
    tags = TagRegistry()
    default_constructors = {}
    default_constructors.update(tags.tag_constructors)

    new_tags = ['test', 'test1', 'test2']

    def test(*args):
        pass

    tags.register_tag(tag=','.join(new_tags), constructor=test)

    found = []
    for tag, constructor in tags.tag_constructors:
        if tag in new_tags:
            assert constructor is test
            found.append(tag)

    assert len(found) == len(new_tags)

    tags._TagRegistry__constructor = default_constructors
