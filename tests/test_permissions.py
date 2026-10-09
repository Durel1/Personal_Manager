import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.connection import connect_database
from backend.create_database import Database
from backend.dashboard import dashboard_counts, export_records, list_records, user_profile
from backend.management import delete_record, get_record, save_record
from backend.migrations import migrate_roles
from backend.permissions import PermissionDenied, current_user, list_users, set_role
from backend.statistics import statistics_snapshot
from test_management import sample


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)/'roles.db'
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(self.path)})
        env.start()
        self.addCleanup(env.stop)
        Database()
        with connect_database() as connection:
            connection.executemany('INSERT INTO User (id,fullname,password,email,phone,gender) VALUES (?,?,?,?,?,?)',
                [(1, 'Admin', 'fixture-not-used-for-login', 'a@example.com', '01', 'Homme'),
                 (2, 'Employee', 'fixture-not-used-for-login', 'e@example.com', '02', 'Femme')])
            connection.execute('PRAGMA user_version=2')
        migrate_roles()
        set_role(1, 2, 'employee')

    def test_migration_preserves_accounts_hashes_and_legacy_finances(self):
        with connect_database() as connection:
            connection.execute('ALTER TABLE User DROP COLUMN role')
            connection.execute('ALTER TABLE Finance DROP COLUMN due_date')
            connection.execute('PRAGMA user_version=2')
            connection.execute("INSERT INTO Finance VALUES (7,'Legacy',100,'10/9/26','Non Payée','Encaissement')")
        migrate_roles()
        migrate_roles()
        with connect_database() as connection:
            self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 3)
            self.assertEqual(connection.execute('SELECT role,password FROM User').fetchall(),
                             [('admin', 'fixture-not-used-for-login')]*2)
            self.assertEqual(connection.execute('SELECT id,date,due_date FROM Finance').fetchone(), (7,'10/9/26',None))

    def test_migration_failure_rolls_back_and_keeps_version(self):
        with connect_database() as connection:
            connection.execute('PRAGMA user_version=2')
        with self.assertRaises(sqlite3.OperationalError):
            migrate_roles()  # Existing custom role column is not silently replaced.
        with connect_database() as connection:
            self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 2)

    def test_employee_reads_only_authorized_modules(self):
        for module in ('clients','events'):
            identifier = save_record(module, sample(module), actor_id=1)
            self.assertEqual(list_records(module, actor_id=2)[1], 1)
            self.assertEqual(get_record(module, identifier, actor_id=2)['id'], identifier)
            self.assertEqual(len(export_records(module, 2)), 1)
        for module in ('employees', 'finances'):
            identifier = save_record(module, sample(module), actor_id=1)
            for operation in (lambda: list_records(module, actor_id=2),
                              lambda: get_record(module, identifier, actor_id=2),
                              lambda: export_records(module, 2)):
                with self.assertRaises(PermissionDenied):
                    operation()

    def test_employee_cannot_write_or_delete_even_directly_in_backend(self):
        for module in ('employees','clients','events','finances'):
            identifier = save_record(module, sample(module), actor_id=1)
            for operation in (lambda: save_record(module, sample(module), actor_id=2),
                              lambda: save_record(module, sample(module), identifier, actor_id=2),
                              lambda: delete_record(module, identifier, actor_id=2)):
                with self.assertRaises(PermissionDenied):
                    operation()
            self.assertEqual(list_records(module, actor_id=1)[1], 1)

    def test_missing_or_invalid_actor_is_refused(self):
        for identifier in (None, True, '1', -1, 999):
            with self.subTest(identifier=identifier), self.assertRaises(PermissionDenied):
                list_records('finances', actor_id=identifier)
        with self.assertRaises(PermissionDenied):
            save_record('clients', sample('clients'))

    def test_dashboard_does_not_disclose_financial_or_employee_data(self):
        save_record('finances', sample('finances'), actor_id=1)
        self.assertEqual(set(dashboard_counts(actor_id=2)), {'clients','events'})
        data = statistics_snapshot(actor_id=2)
        self.assertEqual(set(data['counts']), {'clients','events'})
        self.assertEqual(data['spending'], [])
        self.assertEqual(data['spending_total'], 0)

    def test_role_changes_are_checked_again_for_existing_sessions(self):
        set_role(1, 2, 'admin')
        save_record('finances', sample('finances'), actor_id=2)
        set_role(1, 2, 'employee')
        with self.assertRaises(PermissionDenied):
            list_records('finances', actor_id=2)
        self.assertEqual(current_user(2)['role'], 'employee')

    def test_last_admin_is_protected_and_employees_cannot_assign_roles(self):
        with self.assertRaises(ValueError):
            set_role(1, 1, 'employee')
        with self.assertRaises(PermissionDenied):
            set_role(2, 2, 'admin')
        with self.assertRaises(PermissionDenied):
            list_users(2)
        set_role(1, 2, 'admin')
        set_role(1, 1, 'employee')
        self.assertEqual(current_user(1)['role'], 'employee')
        self.assertEqual(current_user(2)['role'], 'admin')
        self.assertNotIn('password', str(list_users(2)))

    def test_profile_is_private(self):
        self.assertEqual(user_profile(2, actor_id=2)['fullname'], 'Employee')
        with self.assertRaises(ValueError):
            user_profile(1, actor_id=2)

    def test_invalid_roles_are_rejected(self):
        with self.assertRaises(ValueError):
            set_role(1, 2, 'root')
