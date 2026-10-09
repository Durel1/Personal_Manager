import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.connection import connect_database
from backend.create_database import Database
from backend.dashboard import dashboard_counts, list_records, user_profile


class DashboardTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / 'dashboard.db'
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(self.path)})
        env.start()
        self.addCleanup(env.stop)
        Database()

    def test_empty_dashboard(self):
        self.assertEqual(dashboard_counts(), {'employees': 0, 'clients': 0, 'events': 0, 'finances': 0})
        self.assertEqual(list_records('employees'), ([], 0))

    def test_real_counts_and_pagination_without_missing_or_duplicate_rows(self):
        with connect_database() as c:
            c.executemany('INSERT INTO Employee (fullname,email,phone,gender) VALUES (?,?,?,?)',
                          [(f'Employee {i}', 'test@example.com', '00123', 'Homme') for i in range(60)])
        first, total = list_records('employees', 0)
        second, _ = list_records('employees', 1)
        third, _ = list_records('employees', 2)
        self.assertEqual(total, 60)
        self.assertEqual([len(first), len(second), len(third)], [25, 25, 10])
        self.assertEqual(len({row[0] for row in first+second+third}), 60)
        self.assertEqual(dashboard_counts()['employees'], 60)
        self.assertEqual(first[0][0], 60)
        self.assertEqual(first[0][3], '00123')

    def test_unknown_module_and_bad_pagination_rejected(self):
        with self.assertRaises(KeyError):
            list_records('User; DROP TABLE User;--')
        for page, size in [(-1, 25), (0, 0), (0, 101), ('0', 25)]:
            with self.subTest(page=page, size=size), self.assertRaises(ValueError):
                list_records('employees', page, size)

    def test_profile_excludes_password_and_uses_user_id(self):
        with connect_database() as c:
            c.execute('INSERT INTO User VALUES (1,?,?,?,?,?)',
                      ('Durel', 'secret-for-test', 'test@example.com', '00123', 'Homme'))
        self.assertEqual(user_profile(1), {'fullname': 'Durel', 'email': 'test@example.com',
                                         'phone': '00123', 'gender': 'Homme'})
        with self.assertRaises(ValueError):
            user_profile(99)
