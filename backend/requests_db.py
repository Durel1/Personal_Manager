"""Preserve the UI API without a shared cursor or connection."""
from backend.connection import connect_database


def get_execute_request_with_params(request, params):
    with connect_database() as connection:
        return connection.execute(request, params).fetchall()


def get_execute_request_without_params(request):
    return get_execute_request_with_params(request, ())


def set_execute_request_with_params(request, params):
    with connect_database() as connection:
        return connection.execute(request, params).lastrowid


def set_execute_request_without_params(request):
    return set_execute_request_with_params(request, ())
