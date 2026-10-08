"""Real Windows widget smoke tests; layout still needs human visual review."""
import importlib.util
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ('bcrypt', 'customtkinter'))


@unittest.skipUnless(AVAILABLE, 'bcrypt/customtkinter unavailable: modern widget checks pending')
class ModernWidgetTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(Path(directory.name)/'widgets.db')})
        env.start()
        self.addCleanup(env.stop)
        from ui.application import PersonalManager
        self.app = PersonalManager()
        self.addCleanup(self.shutdown)
        self.wait_for(lambda: self.app.generation >= 2)

    def shutdown(self):
        # Poll completion before releasing the temporary directory on Windows.
        self.app.executor.shutdown(wait=True, cancel_futures=True)
        self.app.close()

    def wait_for(self, condition):
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            self.app.update()
            if condition():
                return
            time.sleep(0.01)
        self.fail('Modern UI operation did not finish within five seconds')

    def drain_tasks(self):
        self.wait_for(lambda: not self.app.polls)

    def test_login_and_registration_render_in_one_root(self):
        root_id = str(self.app)
        self.app.show_register()
        self.app.update()
        self.app.show_login()
        self.app.update()
        self.assertEqual(str(self.app), root_id)
        self.assertIsNone(self.app.user)

    def test_sidebar_lists_theme_and_logout(self):
        from backend.auth import register_user
        identifier = register_user('UITest', 'Secret123!', 'test@example.com', '00123', 'Homme')
        self.app.user = {'id': identifier, 'fullname': 'UITest'}
        self.app.show_shell()
        self.drain_tasks()
        for key in ('employees', 'clients', 'events', 'finances', 'profile'):
            self.app.navigate(key)
            self.drain_tasks()
        self.app.change_theme('Clair')
        self.app.update()
        self.app.change_theme('Sombre')
        self.app.update()
        self.app.show_login()
        self.assertIsNone(self.app.user)

    def test_navigation_ignores_obsolete_worker_result(self):
        completed = []
        self.app.run_task(lambda: 42, completed.append)
        self.app.show_register()
        self.drain_tasks()
        self.assertEqual(completed, [])
