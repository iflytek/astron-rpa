"""Bounded native forms for managed Windows runs without a designer connection."""

import os
from datetime import datetime


class ManagedDialogError(RuntimeError):
    code = "DESKTOP_HUMAN_UNAVAILABLE"


def enabled():
    return os.environ.get("ASTRON_RPA_MANAGED_DESKTOP") == "1"


def time_value(values, format_string, multiple):
    format_python = format_string.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
    format_python = format_python.replace("HH", "%H").replace("mm", "%M").replace("ss", "%S")
    if len(values) != (2 if multiple else 1):
        raise ValueError("Invalid date selection")
    parsed = [datetime.strptime(value, format_python) for value in values]
    if multiple and parsed[0] > parsed[1]:
        raise ValueError("Invalid date range")
    normalized = [value.strftime(format_python) for value in parsed]
    return normalized if multiple else normalized[0]


def show(kind, *, title, **options):
    """The execution process owns the window; precise stop also closes the form.

    No HTML, Python, file selection or arbitrary widget definitions are accepted.
    The managed execution deadline bounds forms that require a human response.
    """
    root = None
    try:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title(title)
        root.geometry("480x300")
        root.attributes("-topmost", True)
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        result = None

        def finish(value=None):
            nonlocal result
            result = value
            root.quit()

        root.protocol("WM_DELETE_WINDOW", finish)
        if kind == "message":
            ttk.Label(frame, text=options["message"], wraplength=440).pack(fill="x", pady=12)
            buttons = {
                "confirm": ["confirm"],
                "confirm_cancel": ["confirm", "cancel"],
                "yes_no": ["yes", "no"],
                "yes_no_cancel": ["yes", "no", "cancel"],
            }[options["buttons"]]
            for value in buttons:
                ttk.Button(frame, text=value, command=lambda value=value: finish(value)).pack(side="left", padx=8)
            if options["auto"]:
                root.after(max(0, int(options["seconds"])) * 1000, lambda: finish(options["default"]))
        elif kind == "input":
            ttk.Label(frame, text=options["prompt"], wraplength=440).pack(fill="x")
            value = tk.StringVar(value=options["default"])
            entry = ttk.Entry(frame, textvariable=value, show="*" if options["password"] else "")
            entry.pack(fill="x", pady=12)
            entry.focus_set()
            ttk.Button(frame, text="OK", command=lambda: finish(value.get())).pack()
        elif kind == "select":
            ttk.Label(frame, text=options["prompt"], wraplength=440).pack(fill="x")
            items = options["items"]
            if not isinstance(items, list) or not 1 <= len(items) <= 1000:
                raise ValueError("Invalid selection options")
            values = [item.get("value", item.get("label")) if isinstance(item, dict) else item for item in items]
            listing = tk.Listbox(
                frame, selectmode="extended" if options["multiple"] else "browse", exportselection=False
            )
            for item in items:
                listing.insert("end", str(item.get("label", item.get("value")) if isinstance(item, dict) else item))
            listing.pack(fill="both", expand=True, pady=8)

            def select():
                chosen = [values[index] for index in listing.curselection()]
                if chosen:
                    finish(chosen if options["multiple"] else chosen[0])

            ttk.Button(frame, text="OK", command=select).pack()
        elif kind == "time":
            ttk.Label(frame, text=options["prompt"] + " (" + options["format"] + ")", wraplength=440).pack(fill="x")
            defaults = options["default"] if options["multiple"] else [options["default"]]
            values = [tk.StringVar(value=value) for value in defaults]
            for value in values:
                ttk.Entry(frame, textvariable=value).pack(fill="x", pady=8)
            error = ttk.Label(frame, text="")
            error.pack()

            def select_time():
                try:
                    finish(time_value([value.get() for value in values], options["format"], options["multiple"]))
                except ValueError:
                    error.configure(text="Enter a valid date or ascending date range.")

            ttk.Button(frame, text="OK", command=select_time).pack()
        else:
            raise ValueError("Unsupported managed form")
        root.mainloop()
        return result
    except Exception:
        raise ManagedDialogError("Desktop interaction is unavailable") from None
    finally:
        if root is not None:
            root.destroy()
