import io
import pydoc
import re
import types
import zlib

from sphinx_fakeinv import print_inventory, scan_objects, scan_package

__all__ = ('SAMPLE_DATA', 'SampleClass', 'SampleClass2', 'SampleError',
           'import_string',
           'test_print_inventory', 'test_scan_objects', 'test_scan_package')


def import_string(import_path):
    m, _ = pydoc.resolve(import_path)
    return m


def test_scan_package():
    def get_names(modules):
        result = set()
        for m in modules:
            assert isinstance(m, types.ModuleType)
            result.add(m.__name__)
        return result
    modules = list(scan_package('sphinx_fakeinv'))
    assert get_names(modules) == set(['sphinx_fakeinv'])
    assert modules[0] == __import__('sphinx_fakeinv')
    modules = scan_package('tests')
    assert get_names(modules) == set([
        'tests',
        'tests.sphinx_fakeinv_test',
        'tests.samplepkg',
        'tests.samplepkg.a',
        'tests.samplepkg.b',
        'tests.samplepkg.c',
        'tests.samplepkg.d',
        'tests.samplepkg.d.foo',
    ])


def test_scan_objects():
    mod = import_string(__name__)
    objects = frozenset(scan_objects(mod))
    assert objects == frozenset([
        (__name__, 'py:module', 0, mod),
        (__name__ + '.SAMPLE_DATA', 'py:data', 1, SAMPLE_DATA),
        (__name__ + '.SampleClass', 'py:class', 1, SampleClass),
        (__name__ + '.SampleClass.sample_attr', 'py:attribute', 1,
            SampleClass.sample_attr),
        (__name__ + '.SampleClass.sample_property', 'py:attribute', 1,
            SampleClass.__dict__['sample_property']),
        (__name__ + '.SampleClass.sample_method', 'py:method', 1,
            SampleClass.__dict__['sample_method']),
        (__name__ + '.SampleClass.sample_classmethod', 'py:classmethod', 1,
            SampleClass.__dict__['sample_classmethod']),
        (__name__ + '.SampleClass.sample_staticmethod', 'py:staticmethod', 1,
            SampleClass.__dict__['sample_staticmethod']),
        (__name__ + '.SampleClass2', 'py:class', 1, SampleClass2),
        (__name__ + '.SampleClass2.sample_attr', 'py:attribute', 1,
            SampleClass2.sample_attr),
        (__name__ + '.SampleClass2.sample_method', 'py:method', 1,
            SampleClass2.__dict__['sample_method']),
        (__name__ + '.SampleError', 'py:exception', 1, SampleError),
        (__name__ + '.SampleError.sample_attr', 'py:attribute', 1,
            SampleError.sample_attr),
        (__name__ + '.SampleError.sample_property', 'py:attribute', 1,
            SampleError.__dict__['sample_property']),
        (__name__ + '.SampleError.sample_method', 'py:method', 1,
            SampleError.__dict__['sample_method']),
        (__name__ + '.SampleError.sample_classmethod', 'py:classmethod', 1,
            SampleError.__dict__['sample_classmethod']),
        (__name__ + '.SampleError.sample_staticmethod', 'py:staticmethod', 1,
            SampleError.__dict__['sample_staticmethod']),
        (__name__ + '.import_string', 'py:function', 1, import_string),
        (__name__ + '.test_print_inventory', 'py:function', 1,
            test_print_inventory),
        (__name__ + '.test_scan_objects', 'py:function', 1, test_scan_objects),
        (__name__ + '.test_scan_package', 'py:function', 1, test_scan_package),
    ])


def test_print_inventory():
    mod = import_string(__name__)
    objects = [
        (__name__, 'py:module', 0, mod),
        (__name__ + '.SAMPLE_DATA', 'py:data', 1, SAMPLE_DATA),
        (__name__ + '.SampleClass', 'py:class', 1, SampleClass),
    ]
    buf = io.BytesIO()
    print_inventory(buf, __name__, '1.2.3', objects)
    bytes_ = buf.getvalue()
    match = re.match(br'^(#[^\n]*\n)*', bytes_)
    assert match.group(0) == b'''\
# Sphinx inventory version 2
# Project: ''' + __name__.encode('utf-8') + b'''
# Version: 1.2.3
# The remainder of this file is compressed using zlib.
'''
    assert zlib.decompress(bytes_[match.end(0):]) == b'''\
tests.sphinx_fakeinv_test py:module 0 . -
tests.sphinx_fakeinv_test.SAMPLE_DATA py:data 1 . -
tests.sphinx_fakeinv_test.SampleClass py:class 1 . -
'''


class SampleClass(object):
    """This new-style class is just for scanning tests."""

    sample_attr = 1

    @property
    def sample_property(self):
        pass

    def sample_method(self):
        pass

    @classmethod
    def sample_classmethod(self):
        pass

    @staticmethod
    def sample_staticmethod(self):
        pass


class SampleClass2:
    """This old-style class (new-style class in Python 3) is just for scanning
    tests.

    """

    sample_attr = 1

    def sample_method(self):
        pass


class SampleError(Exception):
    """This exception class is just for scanning tests."""

    sample_attr = 1

    @property
    def sample_property(self):
        pass

    def sample_method(self):
        pass

    @classmethod
    def sample_classmethod(self):
        pass

    @staticmethod
    def sample_staticmethod(self):
        pass


SAMPLE_DATA = 123
