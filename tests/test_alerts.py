from datetime import date

from backend.alerts import alerts_snapshot, record_alert
from backend.dashboard import list_records
from backend.management import ManagementError, get_record, save_record
from test_management import sample
import test_permissions


# Reuse the fixture, not PermissionTests' test methods.
import unittest

class AlertTests(unittest.TestCase):
    setUp = test_permissions.PermissionTests.setUp

    def invoice(self, due_date='', status='Non Payée'):
        return save_record('finances', dict(sample('finances'), date='2026-10-01',
                           due_date=due_date, status=status), actor_id=1)

    def test_explicit_due_date_only_and_payment_clears_alert(self):
        past = self.invoice('2026-10-08')
        self.invoice('2026-10-09')
        self.invoice('2026-10-10')
        self.invoice()
        self.invoice('2026-10-08', 'Payée')
        result = alerts_snapshot(1, date(2026,10,9))
        self.assertEqual(result['overdue_invoices'], 1)
        self.assertEqual(result['unknown_due_dates'], 1)
        rows = list_records('finances', actor_id=1)[0]
        tags = {row[0]: record_alert('finances', row, date(2026,10,9))[0] for row in rows}
        self.assertEqual(tags[past], 'overdue')
        payload = {key: str(value or '') for key,value in get_record('finances',past,actor_id=1).items() if key != 'id'}
        payload['status'] = 'Payée'
        save_record('finances',payload,past,actor_id=1)
        self.assertEqual(alerts_snapshot(1,date(2026,10,9))['overdue_invoices'], 0)

    def test_today_events_and_invalid_dates(self):
        from backend.connection import connect_database
        for value in ('2026-10-09','2026-10-10'):
            save_record('events',dict(sample('events'),eventdate=value),actor_id=1)
        with connect_database() as c:
            c.execute("UPDATE Event SET eventdate='09/10/2026' WHERE eventdate='2026-10-10'")
        result = alerts_snapshot(2,date(2026,10,9))
        self.assertEqual(result['today_events'], 1)
        self.assertEqual(result['invalid_event_dates'], 1)
        self.assertFalse(result['has_finances'])
        self.assertEqual(result['overdue_invoices'], 0)

    def test_invalid_or_early_due_date_is_rejected(self):
        for value in ('2026-02-30','09/10/2026','2026-09-30'):
            with self.subTest(value=value), self.assertRaises(ManagementError):
                self.invoice(value)

    def test_due_date_can_be_cleared_and_invalid_legacy_value_is_reported(self):
        identifier = self.invoice('2026-10-08')
        values = dict(sample('finances'),due_date='',date='2026-10-01')
        save_record('finances',values,identifier,actor_id=1)
        self.assertIsNone(get_record('finances',identifier,actor_id=1)['due_date'])
        from backend.connection import connect_database
        with connect_database() as c:
            c.execute("UPDATE Finance SET due_date='invalid' WHERE id=?",(identifier,))
        self.assertEqual(alerts_snapshot(1,date(2026,10,9))['invalid_due_dates'], 1)
