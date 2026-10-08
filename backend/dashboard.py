"""Read-only queries for the first modern interface; no GUI dependencies."""
from dataclasses import dataclass

from backend.connection import connect_database


@dataclass(frozen=True)
class Module:
    title: str
    table: str
    columns: tuple
    headings: tuple


MODULES = {
    'employees': Module('Employés', 'Employee',
                        ('id', 'fullname', 'email', 'phone', 'gender'),
                        ('ID', 'Nom', 'E-mail', 'Téléphone', 'Genre')),
    'clients': Module('Clients', 'Client',
                      ('id', 'fullname', 'email', 'phone', 'city', 'sector', 'gender', 'quater'),
                      ('ID', 'Nom', 'E-mail', 'Téléphone', 'Ville', 'Secteur', 'Genre', 'Quartier')),
    'events': Module('Rendez-vous', 'Event',
                     ('id', 'meet_with', 'gender', 'phone', 'place', 'event_status',
                      'reason_event', 'eventdate', 'hour_event'),
                     ('ID', 'Contact', 'Genre', 'Téléphone', 'Lieu', 'Statut', 'Motif', 'Date', 'Heure')),
    'finances': Module('Finances', 'Finance',
                       ('id', 'reason', 'amount', 'date', 'status', 'type'),
                       ('ID', 'Motif', 'Montant', 'Date', 'Statut', 'Type')),
}


def dashboard_counts():
    with connect_database() as connection:
        connection.execute('BEGIN')
        return {key: connection.execute(f'SELECT COUNT(*) FROM "{module.table}"').fetchone()[0]
                for key, module in MODULES.items()}


def list_records(module_key, page=0, page_size=25):
    module = MODULES[module_key]  # Identifiers come from this fixed catalog, never user input.
    if not isinstance(page, int) or page < 0:
        raise ValueError('Invalid page')
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValueError('Invalid page size')
    columns = ', '.join(f'"{column}"' for column in module.columns)
    with connect_database() as connection:
        connection.execute('BEGIN')
        total = connection.execute(f'SELECT COUNT(*) FROM "{module.table}"').fetchone()[0]
        rows = connection.execute(
            f'SELECT {columns} FROM "{module.table}" ORDER BY id DESC LIMIT ? OFFSET ?',
            (page_size, page * page_size)).fetchall()
    return rows, total


def user_profile(user_id):
    with connect_database() as connection:
        row = connection.execute('SELECT fullname,email,phone,gender FROM User WHERE id=?',
                                 (user_id,)).fetchone()
    if row is None:
        raise ValueError('Ce compte n’existe plus.')
    return dict(zip(('fullname', 'email', 'phone', 'gender'), row))
