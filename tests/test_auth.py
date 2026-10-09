import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import bcrypt
except ModuleNotFoundError:
    bcrypt = None

if bcrypt is not None:
    from backend.auth import (hash_password, verify_password, register_user,
                              authenticate_user, AuthenticationError)
    from backend.migrations import migrate_passwords
from backend.connection import connect_database
from backend.create_database import Database


@unittest.skipIf(bcrypt is None, 'bcrypt is not installed: real cryptographic tests pending')
class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / 'test.db'
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(self.path)})
        env.start()
        self.addCleanup(env.stop)
        migrate_passwords()

    def register(self, name='Durel', password='Secret123!'):
        return register_user(name, password, 'durel@example.com', '+33 012345', 'Homme')

    def test_hashing_uses_random_salt_and_verifies(self):
        first, second = hash_password('Secret123!'), hash_password('Secret123!')
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password('Secret123!', first))
        self.assertFalse(verify_password('wrong', first))

    def test_registration_and_login_do_not_expose_hash(self):
        identifier = self.register()
        with connect_database() as c:
            value = c.execute('SELECT password FROM User').fetchone()[0]
        self.assertNotEqual(value, 'Secret123!')
        self.assertTrue(value.startswith('$2b$12$'))
        self.assertEqual(authenticate_user(' Durel ', 'Secret123!'), {'id': identifier, 'fullname': 'Durel'})
        self.assertIsNone(authenticate_user('Durel', 'wrong'))
        self.assertIsNone(authenticate_user('absent', 'Secret123!'))

    def test_duplicate_username_rejected(self):
        self.register()
        with self.assertRaises(AuthenticationError):
            self.register()

    def test_ids_are_allocated_by_sqlite(self):
        first = self.register('First')
        second = self.register('Second')
        self.assertNotEqual(first, second)

    def test_invalid_registration_values(self):
        for args in [('', 'Secret123!', 'e@example.com', '0123', 'Homme'),
                     ('User', 'short', 'e@example.com', '0123', 'Homme'),
                     ('User', 'é' * 37, 'e@example.com', '0123', 'Homme'),
                     ('User', 'Secret123!', 'invalid', '0123', 'Homme'),
                     ('User', 'Secret123!', 'e@example.com', 'abc', 'Homme'),
                     ('User', 'Secret123!', 'e@example.com', '0123', '')]:
            with self.subTest(args=args), self.assertRaises(AuthenticationError):
                register_user(*args)

    def test_password_limits_and_malformed_hash(self):
        self.assertFalse(verify_password('x', 'not a bcrypt hash'))
        self.assertFalse(verify_password('x' * 73, hash_password('x')))
        self.assertFalse(verify_password('ab\x00cd', hash_password('ab')))
        self.assertTrue(verify_password('é' * 36, hash_password('é' * 36)))
        with self.assertRaises(AuthenticationError):
            hash_password('é' * 37)

    def test_legacy_migration_and_idempotence(self):
        with connect_database() as c:
            c.execute('DROP INDEX user_fullname_unique')
            c.execute('DELETE FROM User')
            c.execute('PRAGMA user_version = 1')
            c.execute("INSERT INTO User VALUES (42,'Legacy','old','e','01','Homme')")
        migrate_passwords()
        self.assertEqual(authenticate_user('Legacy', 'old')['id'], 42)
        with connect_database() as c:
            hashed = c.execute('SELECT password FROM User').fetchone()[0]
        migrate_passwords()
        with connect_database() as c:
            self.assertEqual(c.execute('SELECT password FROM User').fetchone()[0], hashed)

    def test_legacy_plaintext_looking_like_hash_is_still_migrated(self):
        value = '$2b$12$not-a-real-hash'
        with connect_database() as c:
            c.execute('PRAGMA user_version = 1')
            c.execute('INSERT INTO User VALUES (42,?,?,?,?,?)', ('Legacy', value, 'e', '01', 'Homme'))
        migrate_passwords()
        self.assertIsNotNone(authenticate_user('Legacy', value))

    def test_failed_password_migration_rolls_back_all_passwords(self):
        with connect_database() as c:
            c.execute('PRAGMA user_version = 1')
            c.execute("INSERT INTO User VALUES (1,'Valid','old','e','01','Homme')")
            c.execute('INSERT INTO User VALUES (2,?,?,?,?,?)', ('TooLong', 'x' * 73, 'e', '01', 'Homme'))
        with self.assertRaises(AuthenticationError):
            migrate_passwords()
        with connect_database() as c:
            self.assertEqual(c.execute('SELECT password FROM User WHERE id=1').fetchone()[0], 'old')
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0], 1)

    def test_duplicate_legacy_users_abort_migration(self):
        with connect_database() as c:
            c.execute('DROP INDEX user_fullname_unique')
            c.execute('PRAGMA user_version = 1')
            c.execute("INSERT INTO User VALUES (1,'Same','old','e','01','Homme')")
            c.execute("INSERT INTO User VALUES (2,'Same','old','e','01','Homme')")
        from backend.migrations import MigrationError
        with self.assertRaises(MigrationError):
            migrate_passwords()
        with connect_database() as c:
            self.assertEqual(c.execute('SELECT password FROM User').fetchall(), [('old',), ('old',)])

    def test_unmigrated_database_refuses_authentication(self):
        with connect_database() as c:
            c.execute('PRAGMA user_version = 1')
        with self.assertRaises(AuthenticationError):
            authenticate_user('Durel', 'Secret123!')

    def test_first_signup_is_admin_and_following_signups_are_employees(self):
        from backend.migrations import migrate_application
        from backend.permissions import current_user
        migrate_application()
        first = self.register('First')
        second = self.register('Second')
        self.assertEqual(current_user(first)['role'], 'admin')
        self.assertEqual(current_user(second)['role'], 'employee')
        self.assertEqual(authenticate_user('Second', 'Secret123!')['id'], second)
