import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.connection import connect_database
from backend.create_database import Database
from backend.dashboard import dashboard_counts
from backend.management import (
    ManagementError, delete_record, get_record, initial_values, save_record,
)


def sample(module):
    values = {
        'employees': dict(fullname='Alice', email='a@example.com', phone='+33 00123', gender='Femme'),
        'clients': dict(fullname='Client', email='c@example.com', phone='00123', city='Paris',
                        sector='Services', gender='Homme', quater='Centre'),
        'events': dict(meet_with='Client', gender='Homme', phone='00123', place='Bureau',
                       event_status='Non Effectué', reason_event='Réunion', eventdate='2026-10-09', hour_event='09:30'),
        'finances': dict(reason='Facture', amount='1000', date='2026-10-09', status='Non Payée', type='Encaissement'),
    }
    return values[module]


class ManagementTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(Path(directory.name)/'management.db')})
        env.start()
        self.addCleanup(env.stop)
        Database()

    def test_create_edit_delete_all_modules(self):
        for module in ('employees', 'clients', 'events', 'finances'):
            with self.subTest(module=module):
                values = sample(module)
                identifier = save_record(module, values)
                record = get_record(module, identifier)
                self.assertEqual(record['id'], identifier)
                key = 'reason' if module == 'finances' else 'meet_with' if module == 'events' else 'fullname'
                values[key] = 'Updated'
                self.assertEqual(save_record(module, values, identifier), identifier)
                self.assertEqual(get_record(module, identifier)[key], 'Updated')
                self.assertEqual(dashboard_counts()[module], 1)
                delete_record(module, identifier)
                self.assertEqual(dashboard_counts()[module], 0)
                with self.assertRaises(ManagementError):
                    get_record(module, identifier)

    def test_invoice_edit_updates_only_selected_row(self):
        first = save_record('finances', sample('finances'))
        second = save_record('finances', sample('finances'))
        edited = sample('finances')
        edited.update(amount='2500', status='Payée')
        save_record('finances', edited, first)
        self.assertEqual(dashboard_counts()['finances'], 2)
        self.assertEqual(get_record('finances', first)['amount'], 2500)
        self.assertEqual(get_record('finances', second)['amount'], 1000)
        self.assertEqual(get_record('finances', second)['status'], 'Non Payée')

    def test_generated_ids_avoid_collisions(self):
        ids = [save_record('employees', sample('employees')) for _ in range(120)]
        self.assertEqual(len(set(ids)), 120)

    def test_invalid_amounts_are_not_written(self):
        for amount in ('abc', '0', '-1', '10.50', '1e3', 'NaN', '9223372036854775808'):
            with self.subTest(amount=amount), self.assertRaises(ManagementError):
                save_record('finances', dict(sample('finances'), amount=amount))
        self.assertEqual(dashboard_counts()['finances'], 0)

    def test_invalid_event_dates_and_times_are_not_written(self):
        for key, value in [('eventdate', '2026-02-30'), ('eventdate', '09/10/26'),
                           ('hour_event', '24:00'), ('hour_event', '10:60'), ('hour_event', '-1:00')]:
            with self.subTest(key=key, value=value), self.assertRaises(ManagementError):
                save_record('events', dict(sample('events'), **{key: value}))
        identifier = save_record('events', dict(sample('events'), hour_event='9 : 5'))
        self.assertEqual(get_record('events', identifier)['hour_event'], '09:05')

    def test_validation_prevents_empty_fields_bad_choices_and_extra_columns(self):
        for values in [dict(sample('employees'), fullname='  '), dict(sample('employees'), email='bad'),
                       dict(sample('employees'), phone='abc'), dict(sample('employees'), gender='invalid'),
                       dict(sample('employees'), id='100')]:
            with self.subTest(values=values), self.assertRaises(ManagementError):
                save_record('employees', values)
        self.assertEqual(dashboard_counts()['employees'], 0)

    def test_parameters_preserve_apostrophes_and_zeroes(self):
        name = "O'Connor'); DROP TABLE Employee;--"
        identifier = save_record('employees', dict(sample('employees'), fullname=name, phone='00123'))
        row = get_record('employees', identifier)
        self.assertEqual(row['fullname'], name)
        self.assertEqual(row['phone'], '00123')

    def test_missing_records_and_bad_ids_do_not_create_rows(self):
        for identifier in (999, -1, '1', True):
            with self.subTest(identifier=identifier), self.assertRaises(ManagementError):
                save_record('employees', sample('employees'), identifier)
            with self.assertRaises(ManagementError):
                delete_record('employees', identifier)
        self.assertEqual(dashboard_counts()['employees'], 0)

    def test_legacy_invalid_date_is_preserved_until_explicit_edit(self):
        with connect_database() as c:
            c.execute('INSERT INTO Finance VALUES (1,?,?,?,?,?)',
                      ('Legacy', 1000, '10/9/26', 'Non Payée', 'Encaissement'))
        self.assertEqual(get_record('finances', 1)['date'], '10/9/26')
        with self.assertRaises(ManagementError):
            save_record('finances', dict(sample('finances'), date='10/9/26'), 1)
        self.assertEqual(get_record('finances', 1)['date'], '10/9/26')

    def test_defaults_match_form_fields(self):
        self.assertEqual(set(initial_values('finances')), set(sample('finances')))
        self.assertEqual(initial_values('finances')['status'], 'Non Payée')
