import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from backend.create_database import cree_table_utilisateur, cree_table_client, cree_table_employer
from backend.migrations import migrate_schema, MigrationError


class MigrationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / 'legacy.db'
        with closing(sqlite3.connect(self.path)) as c, c:
            c.execute(cree_table_utilisateur.replace('password TEXT NOT NULL', 'password MOT NULL'))
            c.execute(cree_table_client.replace('phone TEXT', 'phone interger'))
            c.execute(cree_table_employer.replace('phone TEXT', 'phone interger'))
            c.execute("INSERT INTO User VALUES (7,'Legacy','secret','e','00123','Homme')")
            c.execute("INSERT INTO Employee VALUES (9,'Employee','e','+33 0123','Femme')")

    def test_existing_data_survives_and_schema_is_corrected(self):
        migrate_schema(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:
            self.assertEqual(c.execute('SELECT * FROM User').fetchone(),
                             (7, 'Legacy', 'secret', 'e', '00123', 'Homme'))
            self.assertEqual(c.execute('SELECT phone FROM Employee').fetchone(), ('+33 0123',))
            password = next(row for row in c.execute('PRAGMA table_info(User)') if row[1] == 'password')
            self.assertEqual(password[2:4], ('TEXT', 1))
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0], 1)

    def test_migration_is_repeatable(self):
        migrate_schema(self.path)
        migrate_schema(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM User').fetchone()[0], 1)
        # Verify release explicitly: Linux can delete a file with an open handle.
        with self.assertRaises(sqlite3.ProgrammingError):
            c.execute('SELECT 1')

    def test_invalid_legacy_data_rolls_back(self):
        with closing(sqlite3.connect(self.path)) as c, c:
            c.execute('UPDATE User SET password=NULL')
        with self.assertRaises(sqlite3.IntegrityError):
            migrate_schema(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:
            self.assertIsNone(c.execute('SELECT password FROM User').fetchone()[0])
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0], 0)
            self.assertEqual(c.execute("SELECT name FROM sqlite_master WHERE name LIKE '%_migration'").fetchall(), [])

    def test_custom_schema_is_not_silently_dropped(self):
        with closing(sqlite3.connect(self.path)) as c, c:
            c.execute('ALTER TABLE Employee ADD COLUMN extra TEXT')
        with self.assertRaises(MigrationError):
            migrate_schema(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:
            self.assertIn('extra', [row[1] for row in c.execute('PRAGMA table_info(Employee)')])
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0], 0)
