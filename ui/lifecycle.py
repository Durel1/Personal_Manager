"""Cancel an application's Tcl timers without deleting other widgets' commands."""
from tkinter import TclError


def cancel_pending_callbacks(window):
    """Use only when the entire root/interpreter is closing, never on navigation.

    Tkinter.after_cancel also deletes a Python/Tcl callback command. For a
    timer owned by a child widget, that widget still owns the command and
    will delete it during destruction. Cancel at Tcl level instead, leaving
    command disposal to the owning widget.
    """
    try:
        identifiers = window.tk.splitlist(window.tk.call('after', 'info'))
    except TclError:
        return
    for identifier in identifiers:
        try:
            window.tk.call('after', 'cancel', identifier)
        except TclError:
            pass  # Already completed/cancelled during shutdown.
