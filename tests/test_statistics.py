import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from backend.connection import connect_database
from backend.create_database import Database
from backend.statistics import month_keys, parse_event_date, statistics_snapshot


class StatisticsTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(Path(directory.name)/'stats.db')})
        env.start()
        self.addCleanup(env.stop)
        Database()

    def event(self, event_date):
        with connect_database() as c:
            c.execute('INSERT INTO Event (meet_with,gender,phone,place,event_status,reason_event,eventdate,hour_event) '
                      'VALUES (?,?,?,?,?,?,?,?)', ('Client','Homme','001','Bureau','Non Effectué','Réunion',event_date,'09:00'))

    def expense(self, reason, amount, status='Payée', kind='Décaissement'):
        with connect_database() as c:
            c.execute('INSERT INTO Finance (reason,amount,date,status,type) VALUES (?,?,?,?,?)',
                      (reason, amount, '2026-10-09', status, kind))

    def test_empty_snapshot_and_year_boundary(self):
        data = statistics_snapshot(date(2026, 1, 9))
        self.assertEqual(month_keys(date(2026, 1, 9)),
                         ['2025-08','2025-09','2025-10','2025-11','2025-12','2026-01'])
        self.assertEqual([count for _, count in data['months']], [0]*6)
        self.assertEqual(data['spending'], [])
        self.assertEqual(data['spending_total'], 0)

    def test_month_counts_include_zero_months_and_handle_legacy_dates(self):
        for value in ('2026-10-09', '2026-10-10', '2026-09-30', '10/9/26', '2026-02-30', '2027-01-01'):
            self.event(value)
        data = statistics_snapshot(date(2026, 10, 9))
        self.assertEqual(dict(data['months'])['2026-10'], 2)
        self.assertEqual(dict(data['months'])['2026-09'], 1)
        self.assertEqual(data['invalid_dates'], 2)
        self.assertEqual(data['outside_period'], 1)
        self.assertEqual(data['counts']['events'], 6)

    def test_ambiguous_or_invalid_dates_are_not_guessed(self):
        for value in ('10/9/26', '09/10/2026', '2026-02-30', 'junk', None):
            self.assertIsNone(parse_event_date(value))
        self.assertEqual(parse_event_date('2026-10-09'), date(2026,10,9))

    def test_only_paid_expenses_are_aggregated(self):
        self.expense('Loyer', 1000)
        self.expense('Loyer', 500)
        self.expense('Matériel', 300)
        self.expense('Impayé', 999, status='Non Payée')
        self.expense('Recette', 999, kind='Encaissement')
        data = statistics_snapshot(date(2026,10,9))
        self.assertEqual(data['spending'], [('Loyer',1500), ('Matériel',300)])
        self.assertEqual(data['spending_total'], 1800)
        self.assertEqual(data['counts']['finances'], 5)

    def test_invalid_amounts_are_reported(self):
        for value in ('abc', -1, 0, 10.5):
            self.expense('Invalide', value)
        self.expense('Valide', 10)
        data = statistics_snapshot()
        self.assertEqual(data['invalid_amounts'], 4)
        self.assertEqual(data['spending_total'], 10)

    def test_small_categories_are_grouped_without_losing_total(self):
        for index in range(8):
            self.expense(f'Motif {index}', index+1)
        data = statistics_snapshot()
        self.assertEqual(len(data['spending']), 6)
        self.assertEqual(data['spending'][-1], ('Autres motifs (3)', 6))
        self.assertEqual(sum(amount for _,amount in data['spending']), 36)
        self.assertEqual(data['spending_total'], 36)
