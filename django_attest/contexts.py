# coding: utf-8
from django.test import Client, TestCase, TransactionTestCase
from .utils import contextdecorator


__all__ = ("TransactionTestContext", "TestContext")


class TransactionTestContext(TransactionTestCase):
    __name__ = 'blah_bada_boom'

    def __init__(self, fixtures=None, urls=None, client_class=None,
                 multi_db=None):
        if fixtures:
            self.fixtures = fixtures
        if urls:
            self.urls = urls
        if client_class:
            self.client_class = client_class
        if multi_db:
            self.multi_db = multi_db

    def __call__(self):
        """
        Wrapper around default __call__ method to perform common Django
        test set up. This means that user-defined Test Cases aren't required to
        include a call to super().setUp().
        """
        self._pre_setup()
        try:
            yield getattr(self, "client_class", Client)()
        finally:
            self._post_teardown()


class TestContext(TestCase, TransactionTestContext):
    """
    Does basically the same as TransactionTestContext, but surrounds every
    test with a transaction, monkey-patches the real transaction management
    routines to do nothing, and rollsback the test transaction at the end of
    the test. You have to use TransactionTestContext, if you need transaction
    management inside a test.
    """
