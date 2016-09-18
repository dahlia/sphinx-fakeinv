import io
import pydoc
import re
import types
import zlib

from pytest import fixture, mark, raises

from sphinx_fakeinv import (console_scripts_main, main,
                            print_inventory, scan_objects, scan_package)

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


@fixture
def fx_stdouterr():
    def stream():
        s = io.BytesIO()
        if isinstance('', bytes):
            return s, lambda as_bytes=True: s.getvalue()
        t = io.TextIOWrapper(s)

        def getvalue(as_bytes=False):
            if as_bytes:
                return s.getvalue()
            offset = t.tell()
            t.seek(0)
            value = t.read()
            t.seek(offset)
            return value
        return t, getvalue
    stdout, out_getvalue = stream()
    stderr, err_getvalue = stream()
    return {'stdout': stdout, 'stderr': stderr}, out_getvalue, err_getvalue


@mark.parametrize('argv', [
    [],                          # too few
    ['testpkg', 'many'],         # too many
    ['testpkg', 'too', 'many'],  # too many
])
def test_main_wrong_argv_length(argv, fx_stdouterr):
    kwargs, out, err = fx_stdouterr
    with raises(SystemExit) as e:
        main(['prog'] + argv, **kwargs)
    assert e.value.code == 1
    assert out() == ''
    assert err() == 'usage: prog PACKAGE\n'


@mark.parametrize('path', ['foo/bar', 'foobar.py'])
def test_main_file_path_not_package_name(path, fx_stdouterr):
    kwargs, out, err = fx_stdouterr
    with raises(SystemExit) as e:
        main(['prog', path], **kwargs)
    assert e.value.code == 2
    assert out() == ''
    assert err() == ('error: {0} is not a valid Python package/module name, '
                     'but seems a file path.\n').format(path)


@mark.parametrize('invalid_pkgname', ['foo$bar', 'foo@bar', '^foobar'])
def test_main_invalid_package_name(invalid_pkgname, fx_stdouterr):
    kwargs, out, err = fx_stdouterr
    with raises(SystemExit) as e:
        main(['prog', invalid_pkgname], **kwargs)
    assert e.value.code == 2
    assert out() == ''
    assert err() == ('error: {0} is not a valid Python package/module '
                     'name.\n').format(invalid_pkgname)


def test_main_nonroot_package_name(fx_stdouterr):
    kwargs, out, err = fx_stdouterr
    with raises(SystemExit) as e:
        main(['prog', 'foo.bar'], **kwargs)
    assert e.value.code == 2
    assert out() == ''
    assert err() == 'error: foo.bar is not a root package.\n'


def test_console_scripts_main(fx_stdouterr):
    kwargs, out, err = fx_stdouterr
    with raises(SystemExit) as e:
        console_scripts_main(['/abs/path/prog'], **kwargs)
    assert e.value.code == 1
    assert out() == ''
    assert err() == 'usage: prog PACKAGE\n'


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
