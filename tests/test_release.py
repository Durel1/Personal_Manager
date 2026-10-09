import logging
import importlib.util
import json
import os
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.connection import database_path
from backend.diagnostics import record_error

class ReleaseTests(unittest.TestCase):
    def test_git_cleanup_preserves_local_files_and_source_tracking(self):
        from tools.clean_git_tracking import untrack_local_files
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git','init','--quiet'],cwd=root,check=True)
            for name in ('private.db','cache/__pycache__/file.pyc','source.py'):
                path = root/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(b'preserved content')
            subprocess.run(['git','add','.'],cwd=root,check=True)
            self.assertEqual(set(untrack_local_files(root)),{'private.db','cache/__pycache__/file.pyc'})
            self.assertEqual((root/'private.db').read_bytes(),b'preserved content')
            tracked = subprocess.check_output(['git','ls-files'],cwd=root,text=True)
            self.assertEqual(tracked.strip(),'source.py')

    @unittest.skipUnless(all(importlib.util.find_spec(name) for name in ('bcrypt','customtkinter','matplotlib','openpyxl','reportlab')),
                         'Install application dependencies for the release self-test')
    def test_self_test_exercises_assets_and_preserves_personal_database(self):
        from tools.frozen_check import run_self_test
        with tempfile.TemporaryDirectory() as directory:
            personal = Path(directory)/'personal.db'
            personal.write_bytes(b'personal database marker')
            result = Path(directory)/'result.json'
            with patch.dict(os.environ,{'PERSONAL_MANAGER_DB':str(personal)}):
                self.assertEqual(run_self_test(result),0)
                self.assertEqual(os.environ['PERSONAL_MANAGER_DB'],str(personal))
            self.assertEqual(personal.read_bytes(),b'personal database marker')
            data = json.loads(result.read_text(encoding='utf-8'))
            self.assertTrue(data['ok'])
            self.assertEqual(len(data['checks']),4)

    def test_frozen_database_uses_writable_user_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sys,'frozen',True,create=True), patch.object(sys,'platform','win32'), \
                 patch.dict(os.environ,{'LOCALAPPDATA':directory},clear=True):
                expected = Path(directory)/'PersonalManager'/'projet_stage.db'
                self.assertEqual(database_path(),expected)
                self.assertTrue(expected.parent.is_dir())

    def test_override_is_preserved_even_in_frozen_application(self):
        with patch.object(sys,'frozen',True,create=True), \
             patch.dict(os.environ,{'PERSONAL_MANAGER_DB':'chosen.db'}):
            self.assertEqual(database_path(),Path('chosen.db'))

    def test_diagnostics_never_log_exception_values(self):
        with tempfile.TemporaryDirectory() as directory:
            logger = logging.getLogger('personalmanager')
            original = list(logger.handlers)
            logger.handlers.clear()
            try:
                with patch('backend.diagnostics.application_directory',return_value=Path(directory)):
                    try:
                        raise RuntimeError('SecretPassword! SELECT private_data')
                    except RuntimeError as error:
                        record_error('worker',error)
                text = (Path(directory)/'logs'/'application.log').read_text(encoding='utf-8')
                self.assertIn('RuntimeError',text)
                self.assertNotIn('SecretPassword',text)
                self.assertNotIn('private_data',text)
            finally:
                for handler in logger.handlers:
                    handler.close()
                logger.handlers[:] = original

    def test_logging_failure_does_not_raise(self):
        with patch('backend.diagnostics.application_directory',side_effect=OSError):
            record_error('worker',RuntimeError('not logged'))
