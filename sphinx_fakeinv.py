import pkgutil
import types
import zlib

__author__ = 'Hong Minhee <hongminhee' "\x40" 'member.fsf.org>'
__version__ = '1.0.0'
__license__ = 'GPLv3 or later'
__all__ = ('print_inventory', 'scan_objects', 'scan_package',
           '__author__', '__license__', '__version__')


def scan_package(import_path, module=None):
    if module is None:
        module = __import__(import_path)
    basename = module.__name__ + '.'
    path = getattr(module, '__path__', None)
    yield module
    if path is None:
        return
    for importer, modname, ispkg in pkgutil.iter_modules(path):
        fullname = basename + modname
        __import__(fullname)
        submodule = getattr(module, modname)
        yield submodule
        if ispkg:
            for m in scan_package(fullname, submodule):
                yield m


def scan_objects(module):
    has_oldclass = hasattr(types, 'ClassType')
    if has_oldclass:
        type_types = (type, types.ClassType)
    else:
        type_types = type,

    def scan_obj(name, obj, cls=None):
        if isinstance(obj, type_types):
            if issubclass(obj, BaseException):
                kind = 'py:exception'
            else:
                kind = 'py:class'
            cls = ('old'
                   if has_oldclass and isinstance(obj, types.ClassType)
                   else 'new')
            for subname, subobj in obj.__dict__.items():
                if subname.startswith('_'):
                    continue
                for item in scan_obj(name + '.' + subname, subobj, cls=cls):
                    yield item
        elif cls == 'new' and isinstance(obj, property):
            kind = 'py:attribute'
        elif cls == 'new' and isinstance(obj, classmethod):
            kind = 'py:classmethod'
        elif cls == 'new' and isinstance(obj, staticmethod):
            kind = 'py:staticmethod'
        elif callable(obj):
            kind = 'py:method' if cls else 'py:function'
        elif cls:
            kind = 'py:attribute'
        else:
            kind = 'py:data'
        yield name, kind, 1, obj

    names = list(getattr(module, '__all__', dir(module)))
    prefix = module.__name__ + '.'
    yield module.__name__, 'py:module', 0, module
    for n in names:
        obj = getattr(module, n)
        for item in scan_obj(prefix + n, obj):
            yield item


def print_inventory(file_, package, version, objects):
    file_.write(b'# Sphinx inventory version 2\n')
    file_.write(b'# Project: ')
    file_.write(package.encode('utf-8'))
    file_.write(b'\n')
    file_.write(b'# Version: ')
    file_.write(version.encode('utf-8'))
    file_.write(b'\n')
    file_.write(b'# The remainder of this file is compressed using zlib.\n')
    codec = zlib.compressobj()
    fmt = '{0} {1} {2} . -\n'.format
    for name, kind, mysterious_number, _ in objects:
        line = fmt(name, kind, mysterious_number)
        code = codec.compress(line.encode('utf-8'))
        file_.write(code)
    file_.write(codec.flush())
    file_.flush()
