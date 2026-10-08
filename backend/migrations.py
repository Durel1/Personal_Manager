"""Versioned, transactional migration of the original project's schema."""
from backend.connection import connect_database
from backend.create_database import (
    cree_table_utilisateur, cree_table_client, cree_table_employer,
    cree_table_finance, cree_table_Event,
)


class MigrationError(ValueError):
    pass


def migrate_schema(path=None):
    with connect_database(path) as connection:
        connection.execute('BEGIN IMMEDIATE')
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        if version > 2:
            raise MigrationError('Cette base provient d’une version plus récente de PersonalManager.')
        if version >= 1:
            return
        for sql in (cree_table_utilisateur, cree_table_client, cree_table_employer,
                    cree_table_finance, cree_table_Event):
            connection.execute(sql)
        for table, sql in (('User', cree_table_utilisateur), ('Client', cree_table_client),
                           ('Employee', cree_table_employer)):
            current = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
            # Compare with the desired schema without making assumptions about columns.
            temp_sql = sql.replace(f'IF NOT EXISTS {table}', f'"{table}_migration"')
            connection.execute(temp_sql)
            desired = connection.execute(f'PRAGMA table_info("{table}_migration")').fetchall()
            if [row[1] for row in current] != [row[1] for row in desired]:
                raise MigrationError(f'Schéma personnalisé non pris en charge : {table}.')
            if current != desired:
                custom = connection.execute(
                    "SELECT name FROM sqlite_master WHERE tbl_name=? AND type IN ('index','trigger')",
                    (table,)).fetchall()
                if custom:
                    raise MigrationError(f'Index ou déclencheurs personnalisés à migrer : {table}.')
                columns = ', '.join(f'"{row[1]}"' for row in desired)
                connection.execute(f'INSERT INTO "{table}_migration" ({columns}) SELECT {columns} FROM "{table}"')
                connection.execute(f'DROP TABLE "{table}"')
                connection.execute(f'ALTER TABLE "{table}_migration" RENAME TO "{table}"')
            else:
                connection.execute(f'DROP TABLE "{table}_migration"')
        connection.execute('PRAGMA user_version = 1')

def migrate_passwords(path=None):
    # Version 1 stores legacy plaintext; version 2 always stores bcrypt hashes.
    # Do not guess from prefixes: a legacy plaintext password can start with "$2b$".
    from backend.auth import hash_password
    migrate_schema(path)
    with connect_database(path) as connection:
        connection.execute('BEGIN IMMEDIATE')
        if connection.execute('PRAGMA user_version').fetchone()[0] >= 2:
            return
        users = connection.execute('SELECT id, password FROM User').fetchall()
        for identifier, password in users:
            if not isinstance(password, str) or not password:
                raise MigrationError('Un compte possède un mot de passe invalide. Migration annulée.')
            hashed = hash_password(password)
            connection.execute('UPDATE User SET password=? WHERE id=?', (hashed, identifier))
        duplicates = connection.execute(
            'SELECT 1 FROM User GROUP BY fullname HAVING COUNT(*) > 1 LIMIT 1').fetchone()
        if duplicates:
            raise MigrationError('Des noms utilisateurs sont en double. Migration annulée.')
        connection.execute('CREATE UNIQUE INDEX IF NOT EXISTS user_fullname_unique ON User(fullname)')
        connection.execute('PRAGMA user_version = 2')
