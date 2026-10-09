"""Authentication logic independent of Tkinter, with bcrypt password storage."""
import re
import sqlite3

import bcrypt

from backend.connection import connect_database


class AuthenticationError(ValueError):
    pass


def password_bytes(password):
    if not isinstance(password, str) or not password or '\x00' in password:
        raise AuthenticationError('Mot de passe vide ou invalide.')
    encoded = password.encode('utf-8')
    if len(encoded) > 72:
        raise AuthenticationError('Le mot de passe ne doit pas dépasser 72 octets UTF-8.')
    return encoded


def hash_password(password):
    return bcrypt.hashpw(password_bytes(password), bcrypt.gensalt(rounds=12)).decode('ascii')


def verify_password(password, stored_hash):
    try:
        return bcrypt.checkpw(password_bytes(password), stored_hash.encode('ascii'))
    except (ValueError, UnicodeError, AttributeError, TypeError):
        return False


def require_migrated_database(connection):
    if connection.execute('PRAGMA user_version').fetchone()[0] not in (2, 3):
        raise AuthenticationError('La base doit être migrée avant toute authentification.')


def register_user(fullname, password, email, phone, gender):
    fullname, email, phone, gender = (value.strip() for value in (fullname, email, phone, gender))
    if not all((fullname, email, phone, gender)):
        raise AuthenticationError('Veuillez remplir tous les champs.')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise AuthenticationError('Adresse e-mail invalide.')
    if not re.fullmatch(r'\+?[0-9][0-9 ()-]*', phone):
        raise AuthenticationError('Numéro de téléphone invalide.')
    if gender not in ('Homme', 'Femme'):
        raise AuthenticationError('Genre invalide.')
    encoded = password_bytes(password)
    if len(password) < 8:
        raise AuthenticationError('Utilisez au moins 8 caractères pour le mot de passe.')
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=12)).decode('ascii')
    with connect_database() as connection:
        connection.execute('BEGIN IMMEDIATE')
        require_migrated_database(connection)
        try:
            if connection.execute('PRAGMA user_version').fetchone()[0] == 3:
                first = connection.execute('SELECT COUNT(*) FROM User').fetchone()[0] == 0
                cursor = connection.execute(
                    'INSERT INTO User (fullname,password,email,phone,gender,role) VALUES (?,?,?,?,?,?)',
                    (fullname, hashed, email, phone, gender, 'admin' if first else 'employee'))
            else:
                cursor = connection.execute(
                    'INSERT INTO User (fullname,password,email,phone,gender) VALUES (?,?,?,?,?)',
                    (fullname, hashed, email, phone, gender))
        except sqlite3.IntegrityError as error:
            raise AuthenticationError('Ce nom utilisateur est déjà utilisé ou les données sont invalides.') from error
        return cursor.lastrowid


def authenticate_user(fullname, password):
    with connect_database() as connection:
        require_migrated_database(connection)
        row = connection.execute('SELECT id,fullname,password FROM User WHERE fullname=?',
                                 (fullname.strip(),)).fetchone()
    if row is None or not verify_password(password, row[2]):
        return None
    # Never return the hash to the interface.
    return {'id': row[0], 'fullname': row[1]}
