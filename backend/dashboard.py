"""Read-only queries for the first modern interface; no GUI dependencies."""
from dataclasses import dataclass

from backend.connection import connect_database
from backend.permissions import allowed, require_access


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
                       ('id', 'reason', 'amount', 'date', 'status', 'type', 'due_date'),
                       ('ID', 'Motif', 'Montant', 'Date', 'Statut', 'Type', 'Échéance')),
}


def dashboard_counts(*, actor_id=None):
    with connect_database() as connection:
        connection.execute('BEGIN')
        role = require_access(connection, actor_id, 'home')
        return {key: connection.execute(f'SELECT COUNT(*) FROM "{module.table}"').fetchone()[0]
                for key, module in MODULES.items() if allowed(role, key)}


SEARCH_COLUMNS = {
    'employees': ('fullname', 'email', 'phone'),
    'clients': ('fullname', 'email', 'phone', 'city', 'sector', 'quater'),
    'events': ('meet_with', 'phone', 'place', 'reason_event'),
    'finances': ('reason',),
}
FILTER_OPTIONS = {
    'events': ('Tous', 'Non Effectué', 'Effectué'),
    'finances': ('Tous', 'Non Payée', 'Payée'),
}


def filter_clause(module_key, search='', status=None):
    MODULES[module_key]  # Validate before using the internal column catalogue.
    if not isinstance(search, str) or len(search) > 200 or '\x00' in search:
        raise ValueError('Recherche invalide : 200 caractères maximum, sans caractère nul.')
    if status not in (None, 'Tous') and status not in FILTER_OPTIONS.get(module_key, ()):
        raise ValueError('Filtre de statut invalide.')
    clauses, parameters = [], []
    term = search.strip().casefold()
    if term:
        escaped = term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        clauses.append('('+ ' OR '.join(f"CASEFOLD(\"{column}\") LIKE ? ESCAPE '\\'"
                                        for column in SEARCH_COLUMNS[module_key])+')')
        parameters.extend(['%'+escaped+'%']*len(SEARCH_COLUMNS[module_key]))
    if status not in (None, 'Tous'):
        column = 'event_status' if module_key == 'events' else 'status'
        clauses.append(f'TRIM("{column}")=?')
        parameters.append(status)
    where = ' WHERE '+' AND '.join(clauses) if clauses else ''
    return where, parameters


def list_records(module_key, page=0, page_size=25, search='', status=None, *, actor_id=None):
    module = MODULES[module_key]
    if not isinstance(page, int) or page < 0:
        raise ValueError('Invalid page')
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValueError('Invalid page size')
    where, parameters = filter_clause(module_key, search, status)
    columns = ', '.join(f'"{column}"' for column in module.columns)
    with connect_database() as connection:
        connection.create_function('CASEFOLD', 1, lambda value: str(value or '').casefold(), deterministic=True)
        connection.execute('BEGIN')
        require_access(connection, actor_id, module_key)
        total = connection.execute(f'SELECT COUNT(*) FROM "{module.table}"'+where, parameters).fetchone()[0]
        rows = connection.execute(
            f'SELECT {columns} FROM "{module.table}"'+where+' ORDER BY id DESC LIMIT ? OFFSET ?',
            (*parameters, page_size, page * page_size)).fetchall()
    return rows, total


def export_records(module_key, actor_id, search='', status=None, limit=10000):
    """One consistent filtered snapshot, independent of the displayed page."""
    module = MODULES[module_key]
    where, parameters = filter_clause(module_key, search, status)
    columns = ', '.join(f'"{column}"' for column in module.columns)
    with connect_database() as connection:
        connection.create_function('CASEFOLD', 1, lambda value: str(value or '').casefold(), deterministic=True)
        connection.execute('BEGIN')
        require_access(connection, actor_id, module_key, 'export')
        rows = connection.execute(f'SELECT {columns} FROM "{module.table}"'+where+' ORDER BY id DESC LIMIT ?',
                                  (*parameters, limit+1)).fetchall()
        if len(rows) > limit:
            raise ValueError(f'Export limité à {limit} lignes. Affinez la recherche.')
    return rows


def user_profile(user_id, *, actor_id=None):
    with connect_database() as connection:
        connection.execute('BEGIN')
        require_access(connection, actor_id, 'profile')
        if actor_id is not None and actor_id != user_id:
            raise ValueError('Vous pouvez consulter uniquement votre propre profil.')
        row = connection.execute('SELECT fullname,email,phone,gender FROM User WHERE id=?',
                                 (user_id,)).fetchone()
    if row is None:
        raise ValueError('Ce compte n’existe plus.')
    return dict(zip(('fullname', 'email', 'phone', 'gender'), row))
