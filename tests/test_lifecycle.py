import unittest
from tkinter import Tcl

from ui.lifecycle import cancel_pending_callbacks


class LifecycleTests(unittest.TestCase):
    def test_timers_and_idle_callbacks_are_cancelled_before_event_loop_runs(self):
        interpreter = Tcl()
        completed = []
        interpreter.after(0, lambda: completed.append('timer'))
        interpreter.after_idle(lambda: completed.append('idle'))
        commands = [interpreter.tk.call('after','info',identifier)[0]
                    for identifier in interpreter.tk.splitlist(interpreter.tk.call('after','info'))]
        self.addCleanup(lambda: [interpreter.deletecommand(command) for command in commands])
        cancel_pending_callbacks(interpreter)
        self.assertEqual(interpreter.tk.splitlist(interpreter.tk.call('after','info')), ())
        interpreter.tk.call('update')
        self.assertEqual(completed, [])
        cancel_pending_callbacks(interpreter)  # Safe when called twice.

    def test_cancellation_preserves_command_for_owner_cleanup(self):
        interpreter = Tcl()
        timer = interpreter.after(1000, lambda: None)
        command = interpreter.tk.call('after','info',timer)[0]
        self.addCleanup(lambda: interpreter.deletecommand(command))
        cancel_pending_callbacks(interpreter)
        self.assertTrue(interpreter.tk.call('info','commands',command))
