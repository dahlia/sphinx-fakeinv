``sphinx-fakeinv``: Generate fake Intersphinx_ inventory
=========================================================

Sometimes we create libraries so tiny that we don't need write docs using
Sphinx_ for them, but at the same time we may want to link them from
other docs written using Sphinx.

This utility helps us to generate a fake ``objects.inv`` file
(it's also known as Sphinx inventory) so that other Sphinx docs can link
it though the Intersphinx_ extension.

.. _Sphinx: http://www.sphinx-doc.org/
.. _intersphinx: http://www.sphinx-doc.org/en/stable/ext/intersphinx.html


Installation
------------

It's uploaded to PyPI_, so you can install it using ``pip``:

.. code-block:: console

   $ pip install sphinx-fakeinv

.. _PyPI: https://pypi.python.org/pypi/sphinx-fakeinv


Usage
-----

Suppose you've just written a tiny module named ``foobar``.  You can generate
a fake ``objects.inv`` for it by the following command:

.. code-block:: console

   $ sphinx-fakeinv foobar > objects.inv

The ``shinx-fakeinv`` program automatically scans the submodules, subpackages,
and classes/functions/exceptions/variables in all of scanned modules/packages.
(Note that it's aware of ``__all__`` list if there's one.)

If you want to link it from other Sphinx docs, you need to manually add the url
of it (of course you need to upload the generated fake ``objects.inv``
somewhere like gh-pages) to ``intersphinx_mapping`` configuration:

.. code-block:: python

   intersphinx_mapping = {
       'foobar': (
           'https://github.com/example/foobar',            # The project website
           'https://example.github.io/foobar/objects.inv'  # The fake inventory
       ),
   }

That's done!  If you make references to ``foobar`` e.g.:

.. code-block:: rst

   If :mod:`foobar` module is available at runtime this function will uses
   internally :func:`foobar.baz()`.

Links in the above example like ``foobar`` and ``foobar.baz()`` will refer
to ``https://github.com/example/foobar``.


Author and license
------------------

Written by `Hong Minhee`__.  Distributed under GPLv3_ or later.

__ https://hongminhee.org/
.. _GPLv3: http://www.gnu.org/licenses/gpl-3.0.html
