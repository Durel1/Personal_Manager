"""Versioned, transactional migration of the original project's schema."""
from backend.connection import connect_database
from backend.create_database import (
    Database, cree_table_utilisateur, cree_table_client, cree_table_employer,
)


class MigrationError(ValueError):
    pass


def migrate_schema(path=None):
    Database(path)
    with connect_database(path) as connection:
        connection.execute('BEGIN IMMEDIATE')
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        if version > 2:
            raise MigrationError('Cette base provient d’une version plus récente de PersonalManager.')
        if version >= 1:
            return
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

