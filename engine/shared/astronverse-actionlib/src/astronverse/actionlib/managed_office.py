"""Track only private Office processes created for a managed file execution."""

import json
import os
from atexit import register
from pathlib import Path


def create_application(progid, kind):
    import psutil
    import win32com.client
    import win32process

    before = set(psutil.pids())
    try:
        application = win32com.client.DispatchEx(progid)
    except Exception:
        return None
    owned = False
    probe = None
    try:
        collection = application.Workbooks if kind == "excel" else application.Documents
        if collection.Count:
            raise RuntimeError("Office did not provide an empty private instance")
        if kind == "excel":
            hwnd = application.Hwnd
        else:
            # Word/WPS has a document-window handle, not Application.Hwnd.
            # Disable template macros before creating the empty HWND probe.
            application.AutomationSecurity = 3
            if application.AutomationSecurity != 3:
                raise RuntimeError("Office macro isolation is unavailable")
            probe = application.Documents.Add()
            hwnd = probe.ActiveWindow.Hwnd
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        if pid in before:
            raise RuntimeError("Office reused an existing process")
        owned = True
        process = psutil.Process(pid)
        directory = os.environ.get("ASTRON_RPA_MANAGED_FILES_DIRECTORY")
        if directory:
            root = Path(directory)
            if root.suffix != ".files" or root.is_symlink() or root.resolve() != root.absolute():
                raise RuntimeError("Invalid managed Office workspace")
            path = root / f"office-{pid}.json"
            temporary = path.with_suffix(".part")
            temporary.write_text(json.dumps({"pid": pid, "created": process.create_time()}), encoding="utf-8")
            temporary.replace(path)
        if probe is not None:
            probe.Close(SaveChanges=0)
            probe = None
        # Establish and record ownership before configuring the provider so a
        # configuration failure can release this instance without touching a
        # user's existing process. No input document has been opened yet.
        application.AutomationSecurity = 3
        if application.AutomationSecurity != 3:
            raise RuntimeError("Office macro isolation is unavailable")
        if kind == "excel":
            application.AskToUpdateLinks = False
        else:
            application.Options.UpdateLinksAtOpen = False

        def close_private_instance():
            try:
                application.DisplayAlerts = False
                application.Quit()
            except Exception:
                pass  # The scheduler also checks the recorded PID after process exit.

        register(close_private_instance)
        return application
    except Exception:
        if probe is not None:
            try:
                probe.Close(SaveChanges=0)
            except Exception:
                pass
        if owned:
            try:
                application.DisplayAlerts = False
                application.Quit()
            except Exception:
                pass  # The recorded process identity allows scheduler cleanup.
        raise
