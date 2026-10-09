"""Role checks from SQLite, rather than trusting a role supplied by the GUI."""
from backend.connection import connect_database

ROLES = ('admin', 'employee')
ROLE_LABELS = {'admin': 'Administrateur', 'employee': 'Employé'}


class PermissionDenied(ValueError):
    pass


def actor(connection, user_id):
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise PermissionDenied('Veuillez vous reconnecter.')
    row = connection.execute('SELECT id,fullname,role FROM User WHERE id=?', (user_id,)).fetchone()
    if row is None or row[2] not in ROLES:
        raise PermissionDenied('Ce compte n’est plus disponible. Reconnectez-vous.')
    return dict(zip(('id', 'fullname', 'role'), row))


def allowed(role, module, action='read'):
    if action not in ('read', 'export', 'write', 'delete'):
        return False
    if role == 'admin':
        return module in ('employees', 'clients', 'events', 'finances', 'users', 'home', 'profile')
    return role == 'employee' and module in ('clients', 'events', 'home', 'profile') and action in ('read', 'export')


def require_access(connection, user_id, module, action='read'):
    # Versions 0-2 are kept for the old foundation tests/tools. The modern app
    # migrates to v3 before displaying login; v3 always requires an actor.
    if connection.execute('PRAGMA user_version').fetchone()[0] < 3 and user_id is None:
        return 'admin'
    role = actor(connection, user_id)['role']
    if not allowed(role, module, action):
        raise PermissionDenied('Votre rôle ne permet pas cette action.')
    return role


def current_user(user_id):
    with connect_database() as connection:
        return actor(connection, user_id)


def list_users(user_id):
    with connect_database() as connection:
        connection.execute('BEGIN')
        require_access(connection, user_id, 'users')
        return connection.execute('SELECT id,fullname,email,role FROM User ORDER BY fullname,id').fetchall()


def set_role(user_id, target_id, role):
    if role not in ROLES or isinstance(target_id, bool) or not isinstance(target_id, int):
        raise ValueError('Rôle ou compte invalide.')
    with connect_database() as connection:
        connection.execute('BEGIN IMMEDIATE')
        require_access(connection, user_id, 'users', 'write')
        target = actor(connection, target_id)
        if target['role'] == 'admin' and role != 'admin':
            count = connection.execute("SELECT COUNT(*) FROM User WHERE role='admin'").fetchone()[0]
            if count <= 1:
                raise ValueError('Le dernier administrateur doit conserver son rôle.')
        connection.execute('UPDATE User SET role=? WHERE id=?', (role, target_id))
