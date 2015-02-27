Configuration
==============

Configuration is a thin wrapper around PyYAML which extends already readable and powerful YAML with inheritance, composition and (so called) “object-graph configuration” features.

.. note::
    This is origionally based on `configure <http://configure.readthedocs.org/en/latest/>` but it did not work with py3 and had other design issues to my mind.

Basic Usage
-----------
Configuration uses YAML as a configuration format so you can refre to `Yaml specification <http://yaml.org/spec/>` for details

Config File
````````````
.. code-block:: yaml

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

Loading the Config
```````````````````
.. code-block:: python

    config = Configuration(cfg_file)
    assert 'test_list' in config
    assert config.test_list == ['item1', 'item2']
    assert config['test_list'] == ['item1', 'item2']

Advanced Usage
---------------
Configuration allows you to register your own special yaml tags, it comes with two by default !!ref & !!object

Ref Examples
`````````````
.. code-block:: yaml

    ref_value: !!ref:some.dot.separated.path.to.a.value
    re_value_with_suffix: !!ref:some.dot.separated.path.to.a.value:.log
    suffix_ref_value: !!ref:some.dot.separated.path.to.a.value:!!ref:ref_value

    some:
      dot:
        separated:
          path:
            to:
              a:
                value: worked

.. code-block:: python

    config = Configuration(cfg_file)
    assert config.ref_value == 'worked'
    assert config.re_value_with_suffix == 'worked.log'
    assert config.suffix_ref_value == 'workedworked'

Object Examples
````````````````
.. code-block:: yaml

    #module object/attribute
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

.. code-block:: python

    config = Configuration(cfg_file)
    assert config.python_object1 is sys.stdout
    assert config.python_object2.value == 'test passed'
    assert isinstance(config.python_instance1, MyTest2)
    assert isinstance(config.python_instance3, MyTest3)

    # Show lazy loading
    global X
    assert X == 10
    X = 'Test Bassed'
    assert config.python_lazy1 == 'Test Bassed'
    # Lazy loaded objects are NOT called more then once
    X = 10
    assert config.python_lazy1 == 'Test Bassed'

.. code-block:: python

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
