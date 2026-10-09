"""Alerts from explicit dates: transaction dates are never treated as due dates."""
from datetime import date

from backend.connection import connect_database
from backend.dashboard import MODULES
from backend.permissions import allowed, require_access
from backend.statistics import parse_event_date


def record_alert(module_key, row, today=None):
    today = today or date.today()
    values = dict(zip(MODULES[module_key].columns, row))
    if module_key == 'events' and parse_event_date(values['eventdate']) == today:
        return 'today', 'Aujourd’hui'
    if module_key == 'finances' and str(values['status']).strip() == 'Non Payée':
        due = parse_event_date(values.get('due_date'))
        if due is not None and due < today:
            return 'overdue', 'En retard'
    return '', ''


def alerts_snapshot(actor_id, today=None):
    today = today or date.today()
    with connect_database() as connection:
        connection.execute('BEGIN')
        role = require_access(connection, actor_id, 'home')
        events = connection.execute('SELECT eventdate FROM Event').fetchall()
        finances = connection.execute('SELECT due_date FROM Finance WHERE TRIM(status)=?',
                                       ('Non Payée',)).fetchall() if allowed(role, 'finances') else []
    dates = [parse_event_date(row[0]) for row in events]
    due_dates = [parse_event_date(row[0]) for row in finances]
    return {'today_events': sum(value == today for value in dates),
            'invalid_event_dates': sum(value is None for value in dates),
            'overdue_invoices': sum(value is not None and value < today for value in due_dates),
            'unknown_due_dates': sum(not row[0] or not str(row[0]).strip() for row in finances),
            'invalid_due_dates': sum(bool(row[0]) and bool(str(row[0]).strip()) and parsed is None
                                     for row, parsed in zip(finances, due_dates)),
            'has_finances': allowed(role, 'finances')}
