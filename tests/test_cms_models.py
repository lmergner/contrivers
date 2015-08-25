# -*- coding: utf-8 -*-

import datetime
import unittest
import mock
from app.cms.models import Editor
from app.core.errors import ModelError
from app import db
from .fixtures import _create_app
from flask.ext.testing import TestCase

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
        """ Test that `app.cms.models.Editor.verify_password` calls `passlib.CryptContext.verify_and_update` """
        with mock.patch('app.cms.models.pass_context') as pass_ctx:
            pass_ctx.verify_and_update.return_value = (True, None)
            editor = Editor(**editor_params)
            self.assertTrue(editor.verify_password('testing'))

    def test_verify_and_update(self):
        with mock.patch('app.cms.models.pass_context') as pass_ctx:
            pass_ctx.verify_and_update.return_value = (True, 'new_hash')
            with mock.patch('app.cms.models.datetime_with_timezone') as MockTime:
                MockTime.return_value = now = datetime.datetime.utcnow()
                editor = Editor(**editor_params)
                self.assertTrue(editor.verify_password('any_hash_since_its_mocked'))
                self.assertEqual(editor.password, 'new_hash')
                self.assertEqual(editor.password_updated, now)


class PasswordWithAppTestCase(TestCase):

    def create_app(self):
        return _create_app()

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_commited_editor(self):
        editor = Editor(**editor_params)
        db.session.add(editor)
        db.session.commit()

        editor = Editor.query.first()
        self.assertTrue(editor.verify_password('testing'))
        self.assertIsNotNone(editor.password_updated)
        self.assertIsInstance(editor.password_updated, datetime.datetime)

    def test_password_updates(self):
        editor = Editor(**editor_params)

        bcrypt_prefix = '$2a$13'

        #Explicitly set password to plaintext
        editor.password = 'testing'

        # commit w/ plaintext
        db.session.add(editor)
        db.session.commit()

        editor = Editor.query.first()
        editor.verify_password('testing')

        self.assertTrue(editor.password.startswith(bcrypt_prefix))
