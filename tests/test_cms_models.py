# -*- coding: utf-8 -*-

import datetime
import unittest
import mock
from app.cms.models import Editor
from app.core.errors import ModelError
from app import db
from .fixtures import _create_app

editor_params = dict(
    username='testing',
    password='testing',
    email='testing@example.com')

class PasswordTestCase(unittest.TestCase):

    def test_hashing(self):
        with mock.patch('app.cms.models.pass_context') as pass_ctx:
            pass_ctx.encrypt.return_value = 'hashed_password'
            editor = Editor(**editor_params)
            pass_ctx.encrypt.assert_called_with('testing')
            self.assertEqual(editor.password, 'hashed_password')

    def test_init_values(self):
        with self.assertRaises(ModelError):
            editor = Editor()

    def test_update_password(self):
        with mock.patch('app.cms.models.pass_context') as pass_ctx:
            editor = Editor(**editor_params)

    def test_verified(self):
        with mock.patch('app.cms.models.pass_context') as pass_ctx:
            editor = Editor(**editor_params)
            self.assertTrue(editor.verify_password('testing'))

    def test_verify_and_update(self):
        with mock.patch('app.cms.models.pass_context') as pass_ctx:
            pass_ctx.verify_and_update.return_value = (True, 'new_hash')
            with mock.patch('app.cms.models.datetime_with_timezone') as now:
                testdate = now.return_value = datetime.datetime.utcnow()
                editor = Editor(**editor_params)
                editor.password_updated = mock.Mock()
                self.assertTrue(editor.verify_password('any_hash_since_its_mocked'))
                self.assertEqual(editor.password, 'new_hash')
                self.assertEqual(editor.password_updated, testdate)


