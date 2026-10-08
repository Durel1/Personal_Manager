import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.connection import connect_database, database_path
from backend.create_database import Database
from backend.requests_db import (
    get_execute_request_with_params, get_execute_request_without_params,
    set_execute_request_with_params, set_execute_request_without_params,
)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / 'test.db'
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(self.path)})
        env.start()
        self.addCleanup(env.stop)
        Database()

    def test_all_tables_and_repeated_initialization(self):
        Database()
        tables = get_execute_request_without_params("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertEqual({row[0] for row in tables}, {'User', 'Event', 'Client', 'Employee', 'Finance'})

    def test_crud_and_parameter_binding(self):
        name = "O'Connor'); DROP TABLE Employee;--"
        identifier = set_execute_request_with_params(
            'INSERT INTO Employee (fullname,email,phone,gender) VALUES (?,?,?,?)',
            (name, 'test@example.com', '00123', 'Homme'))
        self.assertEqual(get_execute_request_with_params('SELECT fullname,phone FROM Employee WHERE id=?',
                                                        (identifier,)), [(name, '00123')])
        set_execute_request_with_params('UPDATE Employee SET fullname=? WHERE id=?', ('Updated', identifier))
        self.assertEqual(get_execute_request_without_params('SELECT fullname FROM Employee'), [('Updated',)])
        set_execute_request_without_params('DELETE FROM Employee')
        self.assertEqual(get_execute_request_without_params('SELECT * FROM Employee'), [])

    def test_connection_closes_after_success(self):
        with connect_database() as connection:
            connection.execute('SELECT 1')
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute('SELECT 1')

    def test_transaction_rolls_back_and_closes_after_error(self):
        with self.assertRaises(RuntimeError):
            with connect_database() as connection:
                connection.execute("INSERT INTO Employee VALUES (1,'Test','e','01','Homme')")
                raise RuntimeError('simulate failure')
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute('SELECT 1')
        self.assertEqual(get_execute_request_without_params('SELECT * FROM Employee'), [])

    def test_sql_error_is_not_silenced(self):
        with self.assertRaises(sqlite3.OperationalError):
            get_execute_request_without_params('SELECT * FROM missing_table')
        self.assertEqual(get_execute_request_without_params('SELECT COUNT(*) FROM Employee'), [(0,)])

    def test_default_path_is_independent_of_working_directory(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(database_path(), Path(__file__).resolve().parents[1] / 'projet_stage.db')
