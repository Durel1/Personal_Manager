"""Deterministic chart data from real records; ambiguous legacy dates are excluded."""
import math
import re
from collections import Counter
from datetime import date

from backend.connection import connect_database
from backend.dashboard import MODULES


def month_keys(today, months=6):
    if not 1 <= months <= 24:
        raise ValueError('Invalid month range')
    index = today.year*12+today.month-1
    return [f'{value//12:04d}-{value%12+1:02d}' for value in range(index-months+1, index+1)]


def parse_event_date(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    try:
        if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
            return date.fromisoformat(value)
    except ValueError:
        pass
    return None  # Do not guess whether 10/9/26 means October 9 or September 10.


def positive_integer_amount(value):
    if isinstance(value, int):
        amount = value
    elif isinstance(value, float) and math.isfinite(value) and value.is_integer():
        amount = int(value)
    elif isinstance(value, str) and re.fullmatch(r'[0-9]{1,19}', value.strip()):
        amount = int(value.strip())
    else:
        return None
    return amount if 1 <= amount <= 9223372036854775807 else None


def statistics_snapshot(today=None):
    today = today or date.today()
    months = month_keys(today)
    monthly = dict.fromkeys(months, 0)
    with connect_database() as connection:
        connection.execute('BEGIN')
        counts = {key: connection.execute(f'SELECT COUNT(*) FROM "{module.table}"').fetchone()[0]
                  for key, module in MODULES.items()}
        events = connection.execute('SELECT eventdate FROM Event').fetchall()
        expenses = connection.execute("SELECT reason,amount FROM Finance WHERE TRIM(type)=? AND TRIM(status)=?",
                                      ('Décaissement', 'Payée')).fetchall()
    invalid_dates = 0
    outside_period = 0
    for (value,) in events:
        parsed = parse_event_date(value)
        if parsed is None:
            invalid_dates += 1
            continue
        key = parsed.strftime('%Y-%m')
        if key in monthly:
            monthly[key] += 1
        else:
            outside_period += 1
    spending = Counter()
    invalid_amounts = 0
    for reason, raw_amount in expenses:
        amount = positive_integer_amount(raw_amount)
        if amount is None:
            invalid_amounts += 1
            continue
        reason = str(reason).strip() if reason is not None else ''
        spending[reason or 'Sans motif'] += amount
    ordered = sorted(spending.items(), key=lambda item: (-item[1], item[0]))
    slices = ordered[:5]
    if len(ordered) > 5:
        slices.append((f'Autres motifs ({len(ordered)-5})', sum(amount for _, amount in ordered[5:])))
    return {'counts': counts, 'months': list(monthly.items()), 'invalid_dates': invalid_dates,
            'outside_period': outside_period, 'spending': slices,
            'spending_total': sum(spending.values()), 'invalid_amounts': invalid_amounts}
