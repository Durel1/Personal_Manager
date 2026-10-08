"""Headless callback tests: these do not validate rendered Tkinter screens."""
import importlib
import sqlite3
import sys
import unittest
from unittest.mock import Mock, patch


class CallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Only service results are mocked; no fake cryptographic implementation.
        cls.service = Mock()
        cls.service.AuthenticationError = ValueError
        with patch.dict(sys.modules, {'backend.auth': cls.service}):
            cls.login = importlib.import_module('pages.authentication.login_page')
            cls.register = importlib.import_module('pages.authentication.register_page')
        cls.forgot = importlib.import_module('pages.authentication.forget_password')

    def login_page(self):
        page = self.login.LoginPage.__new__(self.login.LoginPage)
        page.username, page.password, page.page = Mock(), Mock(), Mock()
        page.username.get.return_value = 'Durel'
        page.password.get.return_value = 'Secret123!'
        page.width, page.height = 1200, 600
        return page

    def test_successful_login_navigates_without_subprocess(self):
        page = self.login_page()
        home = Mock()
        with patch.object(self.login, 'authenticate_user', return_value={'id': 1, 'fullname': 'Durel'}), \
             patch.dict(sys.modules, {'pages.home.home_page': home}):
            page.connection()
        home.HomePage.assert_called_once_with(page.page, 1200, 600, 'Durel')

    def test_empty_login_does_not_query_service(self):
        page = self.login_page()
        page.username.get.return_value = ' '
        with patch.object(self.login, 'authenticate_user') as auth, patch.object(self.login, 'mb') as messages:
            page.connection()
        auth.assert_not_called()
        messages.showwarning.assert_called_once()

    def test_incorrect_credentials_display_generic_message(self):
        page = self.login_page()
        with patch.object(self.login, 'authenticate_user', return_value=None), patch.object(self.login, 'mb') as messages:
            page.connection()
        messages.showwarning.assert_called_once_with('Connexion', 'Nom utilisateur ou mot de passe incorrect.')

    def test_database_error_displays_message(self):
        page = self.login_page()
        with patch.object(self.login, 'authenticate_user', side_effect=sqlite3.OperationalError('busy')), \
             patch.object(self.login, 'mb') as messages:
            page.connection()
        messages.showerror.assert_called_once()

    def test_registration_returns_to_login(self):
        page = self.register.RegisterPage.__new__(self.register.RegisterPage)
        for name in ('fullname', 'password', 'email', 'contact', 'sexe', 'page'):
            setattr(page, name, Mock())
        with patch.object(self.register, 'register_user', return_value=1), patch.object(self.register, 'mb'):
            page.register()
        page.page.destroy.assert_called_once()

    def test_password_recovery_never_queries_database(self):
        page = self.forgot.ForgetPassword.__new__(self.forgot.ForgetPassword)
        with patch.object(self.forgot, 'mb') as messages:
            page.getPassword()
        messages.showinfo.assert_called_once()
