try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup

from sphinx_fakeinv import __author__, __license__, __version__


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        pass


setup(
    name='sphinx-fakeinv',
    description='Generate fake Intersphinx inventory',
    long_description=readme(),
    version=__version__,
    author=__author__.partition('<')[0].strip(),
    author_email=__author__.partition('<')[2].rstrip('>').strip(),
    license=__license__,
    py_modules=['sphinx_fakeinv'],
    scripts=['sphinx_fakeinv.py'],
    entry_points={
        'console_scripts': [
            'sphinx-fakeinv = sphinx_fakeinv:console_scripts_main',
        ],
    },
    keywords='docs sphinx intersphinx',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: Sphinx',
        'Intended Audience :: Developers',
        'License :: OSI Approved ::'
        ' GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Utilities',
    ]
)
