django-attest
=============

Provides the same testing helper functionality as Django's
``django.test.TestCase`` wrapper of ``unittest.TestCase``.

``django_attest.TestContext`` provides the most of the same functionality as
subclassing ``django.test.TestCase``, and
``django_attest.TransactionTestContext`` does the same as
``django.test.TransactionTestCase``.

Both contexts provide a ``django.test.TestClient`` object (normally accessed
via ``self.client`` in ``django.test.TestCase`` tests), which can be used to
make requests to views for testing.


Installation
============

Use pip::

    ``pip install django-attest``


Usage
=====

Create a test collection and optionally include one of ``django-attest``'s test
contexts. The result is that a ``client`` argument is passed to each test
within the collection. ``client`` is a ``django.test.TestClient`` object and
allows you to make HTTP requests to your project.

::

    from attest import Tests
    from django_attest import TestContext

    tests = Tests()
    tests.context(TestContext())

    @tests.test
    def can_add(client):
        client.get('/some-url/')  # same as self.client.get() if you were using
                                  # the standard django.test.TestCase approach

See the `TestCase.client documentation`__ for more details.

.. __: http://docs.djangoproject.com/en/1.3/topics/testing/#django.test.TestCase.client

When using a ``django.test.TestCase`` subclass, you're able to specify various
options that affect the environment in which your tests are executed.
``django-attest`` provides the same functionality via keyword arguments to the
``TestContext``. The following keyword arguments are supported:

- ``fixtures`` -- http://docs.djangoproject.com/en/1.3/topics/testing/#django.test.TestCase.fixtures
- ``urls`` -- http://docs.djangoproject.com/en/1.3/topics/testing/#django.test.TestCase.urls
- ``client_class`` -- http://docs.djangoproject.com/en/1.3/topics/testing/#django.test.TestCase.client_class
- ``multi_db`` -- http://docs.djangoproject.com/en/1.3/topics/testing/#django.test.TestCase.multi_db

For example if you want to specify fixtures, urls, a client_class,
or multi_db, simply pass
in these options when creating the ``django_tables.TestContext`` object:

::

    from attest import Tests
    from django_attest import TestContext

    tests = Tests()
    tests.context(TestContext(fixtures=['testdata.json'], urls='myapp.urls'))


Transaction management in tests
-------------------------------

If you need to test transaction management within your tests, use
``TransactionTestContext`` rather than ``TestContext``, e.g.::

    from attest import Tests
    from django_attest import TransactionTestContext

    tests = Tests()
    tests.context(TransactionTestContext())

    @tests.test
    def some_test(client):
        # test something
        ...

Testing a reusable Django app
-----------------------------

Often you'll want to test database or template related code. Django's built-in
test runner does some automatic setup and teardown of the environment to allow
you to do this (e.g. it creates a test database and patches ``Template`` to add
rendering signal hooks).

To get the same goodness in a reusable app, you should use one of
django-attest's patched Attest reporters. You must however ensure
``DJANGO_SETTINGS_MODULE`` is defined before importing anything from
``django_attest``.

A simple solution is to create a ``tests/__init__.py`` file that contains::

    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

    from attest import Tests
    from django_attest import FancyReporter
    from .templates import tests as template_tests
    from .models import tests as model_tests

    loader = FancyReporter.test_loader
    everything = Tests([template_tests, model_tests])

Next ensure your ``setup.py`` contains the following::

    from setuptools import setup

    setup(
        ...
        tests_require=['Django >=1.1', 'Attest >=0.4', 'django-attest'],
        test_loader='tests:loader',
        test_suite='tests.everything',
    )

Finally create ``tests/settings.py`` and populate it with the Django settings
you need for your app, e.g.::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

    INSTALLED_APPS = [
        'django.contrib.sessions',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'myapp',
        'tests.app',
    ]

    SECRET_KEY = 'abcdefghiljklmnopqrstuvwxyz'

    ROOT_URLCONF = 'tests.app.urls'


A few things to note:

- ``everything`` is the tests collection that contains all the separate test
  collections. The ``test_suite`` option in ``setup.py`` refers to this.
- The database is *in-memory* and uses the ``django.db.backends.sqlite3``
  backend.

Finally, the tests can be run via::

    python setup.py test


Testing non-reusable apps in a Django project
---------------------------------------------

To test non-reusable apps in a Django project, the app must contain either a
``tests`` or ``models`` module with a ``suite`` function that returns a
``unittest.TestCase`` (see `Django's documentation
<http://docs.djangoproject.com/en/1.3/topics/testing/#writing-unit-tests>`_ for
details).

As an example, an app that wants to test some of its templating code has a
``tests.py`` file containing::

    from attest import Tests

    template = Tests()

    @tests.test
    def filter():
        """Test the template filter."""
        # ...


    @template.test
    def tag():
        """Test the template tag."""
        # ...

    def suite():
        return template.test_suite()

Since you should be using Django's test runner, all test environment setup/tear
down is handled automatically, and there's no need for any of Attest's
reporters.
