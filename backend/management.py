"""Validated CRUD services for the modern interface, independent of Tkinter."""
import re
from datetime import date
from dataclasses import dataclass

from backend.connection import connect_database
from backend.dashboard import MODULES


class ManagementError(ValueError):
    pass


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    kind: str = 'text'
    choices: tuple = ()


CHOICES = {
    'gender': ('Homme', 'Femme'),
    'event_status': ('Non Effectué', 'Effectué'),
    'status': ('Non Payée', 'Payée'),
    'type': ('Encaissement', 'Décaissement'),
}
KINDS = {'email': 'email', 'phone': 'phone', 'amount': 'amount',
         'date': 'date', 'eventdate': 'date', 'hour_event': 'time'}
LABELS = {'amount': 'Montant (nombre entier)', 'date': 'Date (AAAA-MM-JJ)',
          'eventdate': 'Date (AAAA-MM-JJ)', 'hour_event': 'Heure (HH:MM)'}


def form_fields(module_key):
    module = MODULES[module_key]
    return tuple(Field(column, LABELS.get(column, heading),
                       'choice' if column in CHOICES else KINDS.get(column, 'text'),
                       CHOICES.get(column, ()))
                 for column, heading in zip(module.columns[1:], module.headings[1:]))


def initial_values(module_key):
    return {field.key: (field.choices[0] if field.choices else
                       date.today().isoformat() if field.kind == 'date' else
                       '09:00' if field.kind == 'time' else '')
            for field in form_fields(module_key)}


def validate_values(module_key, values):
    fields = form_fields(module_key)
    if set(values) != {field.key for field in fields}:
        raise ManagementError('Le formulaire est incomplet ou contient des champs inconnus.')
    cleaned = {}
    for field in fields:
        value = values[field.key]
        if not isinstance(value, str):
            raise ManagementError(f'{field.label} : valeur invalide.')
        value = value.strip()
        if not value:
            raise ManagementError(f'{field.label} : veuillez remplir ce champ.')
        if len(value) > 500 or '\x00' in value:
            raise ManagementError(f'{field.label} : texte invalide ou trop long (500 caractères maximum).')
        if field.choices and value not in field.choices:
            raise ManagementError(f'{field.label} : choisissez une valeur proposée.')
        if field.kind == 'email' and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            raise ManagementError('Adresse e-mail invalide.')
        if field.kind == 'phone' and not re.fullmatch(r'\+?[0-9][0-9 ()-]*', value):
            raise ManagementError('Numéro de téléphone invalide.')
        if field.kind == 'amount':
            if not re.fullmatch(r'[0-9]+', value) or not 1 <= int(value) <= 9223372036854775807:
                raise ManagementError('Le montant doit être un entier positif, sans décimales.')
            value = int(value)
        if field.kind == 'date':
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
                raise ManagementError('Utilisez une date au format AAAA-MM-JJ, par exemple 2026-10-09.')
            try:
                date.fromisoformat(value)
            except ValueError as error:
                raise ManagementError('Cette date n’existe pas dans le calendrier.') from error
        if field.kind == 'time':
            match = re.fullmatch(r'([0-9]{1,2})\s*:\s*([0-9]{1,2})', value)
            if not match or int(match[1]) > 23 or int(match[2]) > 59:
                raise ManagementError('L’heure doit être comprise entre 00:00 et 23:59.')
            value = f'{int(match[1]):02d}:{int(match[2]):02d}'
        cleaned[field.key] = value
    return cleaned


def checked_id(identifier):
    if isinstance(identifier, bool) or not isinstance(identifier, int) or identifier < 1:
        raise ManagementError('Identifiant invalide.')
    return identifier


def get_record(module_key, identifier):
    module = MODULES[module_key]
    identifier = checked_id(identifier)
    columns = ', '.join(f'"{column}"' for column in module.columns)
    with connect_database() as connection:
        row = connection.execute(f'SELECT {columns} FROM "{module.table}" WHERE id=?',
                                 (identifier,)).fetchone()
    if row is None:
        raise ManagementError('Cet enregistrement n’existe plus. Actualisez la liste.')
    return dict(zip(module.columns, row))


def save_record(module_key, values, identifier=None):
    module = MODULES[module_key]
    cleaned = validate_values(module_key, values)
    columns = module.columns[1:]
    parameters = tuple(cleaned[column] for column in columns)
    with connect_database() as connection:
        if identifier is None:
            names = ', '.join(f'"{column}"' for column in columns)
            placeholders = ', '.join('?' for _ in columns)
            return connection.execute(f'INSERT INTO "{module.table}" ({names}) VALUES ({placeholders})',
                                      parameters).lastrowid
        identifier = checked_id(identifier)
        assignments = ', '.join(f'"{column}"=?' for column in columns)
        cursor = connection.execute(f'UPDATE "{module.table}" SET {assignments} WHERE id=?',
                                    parameters+(identifier,))
        if cursor.rowcount != 1:
            raise ManagementError('Cet enregistrement n’existe plus. Actualisez la liste.')
        return identifier


def delete_record(module_key, identifier):
    module = MODULES[module_key]
    identifier = checked_id(identifier)
    with connect_database() as connection:
        cursor = connection.execute(f'DELETE FROM "{module.table}" WHERE id=?', (identifier,))
        if cursor.rowcount != 1:
            raise ManagementError('Cet enregistrement n’existe plus. Actualisez la liste.')
