import sqlite3
import unittest

from backend.create_database import (
    cree_table_utilisateur, cree_table_client, cree_table_employer,
)


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.addCleanup(self.connection.close)
        for sql in (cree_table_utilisateur, cree_table_client, cree_table_employer):
            self.connection.execute(sql)

    def test_password_is_required_text(self):
        columns = {row[1]: row for row in self.connection.execute('PRAGMA table_info(User)')}
        self.assertEqual(columns['password'][2:4], ('TEXT', 1))
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute('INSERT INTO User VALUES (1, ?, NULL, ?, ?, ?)',
                                    ('test', 'test@example.com', '012345', 'Homme'))

    def test_phone_preserves_prefix_and_leading_zero(self):
        for table in ('Client', 'Employee'):
            columns = {row[1]: row for row in self.connection.execute(f'PRAGMA table_info({table})')}
            self.assertEqual(columns['phone'][2:4], ('TEXT', 1))
        self.connection.execute('INSERT INTO Employee VALUES (1, ?, ?, ?, ?)',
                                ('Test', 'test@example.com', '+33012345', 'Homme'))
        self.assertEqual(self.connection.execute('SELECT phone FROM Employee').fetchone()[0], '+33012345')


if __name__ == '__main__':
    unittest.main()
