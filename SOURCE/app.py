import threading
import tkinter as tk
from tkinter import messagebox

from Updates.update_manager import (
    get_latest_release,
    download_update,
    get_pending_update,
    install_and_restart,
)


# ============================================================
# NEXO CALCULATOR VERSION
# ============================================================

PUBLIC_VERSION = "0.2026.00009PR3"
INTERNAL_BUILD = "INT01"


# ============================================================
# NEXO CALCULATOR
# ============================================================

class NexoCalculator(tk.Tk):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # Window
        # ----------------------------------------------------

        self.title(
            f"Nexo Calculator v{PUBLIC_VERSION}"
        )

        self.geometry(
            "420x600"
        )

        self.minsize(
            360,
            500
        )

        self.configure(
            bg="#111111"
        )

        # ----------------------------------------------------
        # Update System state
        # ----------------------------------------------------

        self.update_check_running = False
        self.update_dialog_open = False

        # ----------------------------------------------------
        # Build interface
        # ----------------------------------------------------

        self.create_interface()

        # ----------------------------------------------------
        # Nexo Studios Update System
        # ----------------------------------------------------

        self.initialize_updates()

    # ========================================================
    # USER INTERFACE
    # ========================================================

    def create_interface(self):

        header = tk.Frame(
            self,
            bg="#111111"
        )

        header.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        title = tk.Label(
            header,
            text="Nexo Calculator",
            font=(
                "Segoe UI",
                24,
                "bold"
            ),
            fg="#ff7a00",
            bg="#111111"
        )

        title.pack()

        version_label = tk.Label(
            header,
            text=(
                f"v{PUBLIC_VERSION} • "
                f"{INTERNAL_BUILD}"
            ),
            font=(
                "Segoe UI",
                10
            ),
            fg="#aaaaaa",
            bg="#111111"
        )

        version_label.pack(
            pady=(2, 0)
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        display_frame = tk.Frame(
            self,
            bg="#1c1c1c",
            highlightthickness=1,
            highlightbackground="#333333"
        )

        display_frame.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.display = tk.Entry(
            display_frame,
            font=(
                "Segoe UI",
                28
            ),
            justify="right",
            bd=0,
            relief="flat",
            bg="#1c1c1c",
            fg="white",
            insertbackground="white"
        )

        self.display.pack(
            fill="x",
            padx=15,
            pady=20
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        buttons_frame = tk.Frame(
            self,
            bg="#111111"
        )

        buttons_frame.pack(
            expand=True,
            fill="both",
            padx=20,
            pady=10
        )

        buttons = [
            ("7", 0, 0),
            ("8", 0, 1),
            ("9", 0, 2),
            ("/", 0, 3),

            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("*", 1, 3),

            ("1", 2, 0),
            ("2", 2, 1),
            ("3", 2, 2),
            ("-", 2, 3),

            ("0", 3, 0),
            (".", 3, 1),
            ("=", 3, 2),
            ("+", 3, 3),

            ("C", 4, 0),
        ]

        for text, row, column in buttons:

            button = tk.Button(
                buttons_frame,
                text=text,
                font=(
                    "Segoe UI",
                    16,
                    "bold"
                ),
                bg=(
                    "#ff7a00"
                    if text == "="
                    else "#242424"
                ),
                fg="white",
                activebackground="#ff8c26",
                activeforeground="white",
                bd=0,
                relief="flat",
                command=lambda value=text: (
                    self.button_pressed(value)
                )
            )

            button.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=4,
                pady=4
            )

        for row in range(5):
            buttons_frame.rowconfigure(
                row,
                weight=1
            )

        for column in range(4):
            buttons_frame.columnconfigure(
                column,
                weight=1
            )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        footer = tk.Label(
            self,
            text=(
                "Nexo Studios • "
                "Building Tomorrow Together"
            ),
            font=(
                "Segoe UI",
                9
            ),
            fg="#666666",
            bg="#111111"
        )

        footer.pack(
            pady=(5, 15)
        )

    # ========================================================
    # CALCULATOR
    # ========================================================

    def button_pressed(self, value):

        if value == "C":
            self.display.delete(
                0,
                tk.END
            )
            return

        if value == "=":
            self.calculate()
            return

        self.display.insert(
            tk.END,
            value
        )

    # ========================================================

    def calculate(self):

        expression = self.display.get()

        if not expression:
            return

        try:

            allowed_characters = (
                "0123456789"
                "+-*/(). "
            )

            if any(
                character not in allowed_characters
                for character in expression
            ):
                raise ValueError

            result = eval(
                expression,
                {
                    "__builtins__": {}
                },
                {}
            )

            self.display.delete(
                0,
                tk.END
            )

            self.display.insert(
                0,
                str(result)
            )

        except Exception:

            self.display.delete(
                0,
                tk.END
            )

            self.display.insert(
                0,
                "Error"
            )

    # ========================================================
    # NEXO STUDIOS UPDATE SYSTEM
    # ========================================================

    def initialize_updates(self):

        self.after(
            500,
            self.check_pending_update
        )

    # ========================================================

    def check_pending_update(self):

        pending = get_pending_update()

        if pending:

            version = pending.get(
                "version",
                ""
            )

            if version:
                self.show_downloaded_update(
                    version
                )

        self.after(
            300,
            self.check_for_updates
        )

    # ========================================================

    def check_for_updates(self):

        if self.update_check_running:
            return

        self.update_check_running = True

        def update_check_worker():

            try:

                release = get_latest_release(
                    PUBLIC_VERSION
                )

            except Exception:

                release = None

            self.after(
                0,
                lambda: self.process_update_result(
                    release
                )
            )

        threading.Thread(
            target=update_check_worker,
            daemon=True
        ).start()

    # ========================================================

    def process_update_result(
        self,
        release
    ):

        self.update_check_running = False

        if not release:
            return

        version = (
            release.get("tag_name")
            or ""
        )

        if not version:
            return

        self.show_update_available(
            version,
            release
        )

    # ========================================================
    # UPDATE AVAILABLE POPUP
    # ========================================================

    def show_update_available(
        self,
        version,
        release
    ):

        if self.update_dialog_open:
            return

        self.update_dialog_open = True

        release_name = (
            release.get("name")
            or version
        )

        release_body = (
            release.get("body")
            or ""
        ).strip()

        # ----------------------------------------------------
        # Popup
        # ----------------------------------------------------

        popup = tk.Toplevel(
            self
        )

        popup.title(
            "Nexo Calculator Update"
        )

        popup.geometry(
            "450x330"
        )

        popup.resizable(
            False,
            False
        )

        popup.configure(
            bg="#111111"
        )

        popup.transient(
            self
        )

        popup.grab_set()

        # ----------------------------------------------------
        # Sluiten
        # ----------------------------------------------------

        def close_popup():

            self.update_dialog_open = False

            try:
                popup.grab_release()
            except tk.TclError:
                pass

            try:
                popup.destroy()
            except tk.TclError:
                pass

        popup.protocol(
            "WM_DELETE_WINDOW",
            close_popup
        )

        # ----------------------------------------------------
        # Titel
        # ----------------------------------------------------

        title = tk.Label(
            popup,
            text="Update beschikbaar!",
            font=(
                "Segoe UI",
                20,
                "bold"
            ),
            fg="#ff7a00",
            bg="#111111"
        )

        title.pack(
            pady=(25, 8)
        )

        # ----------------------------------------------------
        # Versie
        # ----------------------------------------------------

        version_text = tk.Label(
            popup,
            text=f"Nieuwe versie: {version}",
            font=(
                "Segoe UI",
                13,
                "bold"
            ),
            fg="white",
            bg="#111111"
        )

        version_text.pack()

        # ----------------------------------------------------
        # Release naam
        # ----------------------------------------------------

        release_text = tk.Label(
            popup,
            text=release_name,
            font=(
                "Segoe UI",
                10
            ),
            fg="#bbbbbb",
            bg="#111111"
        )

        release_text.pack(
            pady=(3, 10)
        )

        # ----------------------------------------------------
        # Release notes
        # ----------------------------------------------------

        if release_body:

            notes = release_body

            if len(notes) > 220:
                notes = (
                    notes[:220]
                    + "..."
                )

            notes_label = tk.Label(
                popup,
                text=notes,
                font=(
                    "Segoe UI",
                    9
                ),
                fg="#999999",
                bg="#111111",
                wraplength=390,
                justify="center"
            )

            notes_label.pack(
                padx=25,
                pady=(0, 15)
            )

        else:

            no_notes = tk.Label(
                popup,
                text=(
                    "Er zijn nieuwe verbeteringen "
                    "beschikbaar."
                ),
                font=(
                    "Segoe UI",
                    9
                ),
                fg="#999999",
                bg="#111111"
            )

            no_notes.pack(
                pady=(0, 15)
            )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        button_frame = tk.Frame(
            popup,
            bg="#111111"
        )

        button_frame.pack(
            pady=5
        )

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        def download():

            download_button.config(
                state="disabled",
                text="Downloaden..."
            )

            later_button.config(
                state="disabled"
            )

            def worker():

                try:

                    success = download_update(
                        release
                    )

                except Exception:

                    success = False

                self.after(
                    0,
                    lambda: self.finish_download(
                        popup,
                        version,
                        success
                    )
                )

            threading.Thread(
                target=worker,
                daemon=True
            ).start()

        download_button = tk.Button(
            button_frame,
            text="Download nu",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg="#ff7a00",
            fg="white",
            activebackground="#ff8c26",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=22,
            pady=9,
            cursor="hand2",
            command=download
        )

        download_button.grid(
            row=0,
            column=0,
            padx=5
        )

        # ----------------------------------------------------
        # LATER
        # ----------------------------------------------------

        later_button = tk.Button(
            button_frame,
            text="Later",
            font=(
                "Segoe UI",
                10
            ),
            bg="#292929",
            fg="white",
            activebackground="#383838",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=22,
            pady=9,
            cursor="hand2",
            command=close_popup
        )

        later_button.grid(
            row=0,
            column=1,
            padx=5
        )

    # ========================================================
    # DOWNLOAD FINISHED
    # ========================================================

    def finish_download(
        self,
        popup,
        version,
        success
    ):

        self.update_dialog_open = False

        try:
            popup.grab_release()
        except tk.TclError:
            pass

        try:
            popup.destroy()
        except tk.TclError:
            pass

        if not success:

            messagebox.showerror(
                "Nexo Calculator Update",
                (
                    "De update kon niet worden "
                    "gedownload.\n\n"
                    "Controleer je internetverbinding "
                    "en probeer het later opnieuw."
                ),
                parent=self
            )

            return

        self.show_downloaded_update(
            version
        )

    # ========================================================
    # UPDATE DOWNLOADED
    # ========================================================

    def show_downloaded_update(
        self,
        version
    ):

        result = messagebox.askyesno(
            "Update klaar",
            (
                f"Nexo Calculator {version} "
                "is gedownload.\n\n"
                "Wil je de update nu installeren "
                "en Nexo Calculator opnieuw starten?"
            ),
            parent=self
        )

        if not result:
            return

        success = install_and_restart()

        if success:

            self.destroy()

        else:

            messagebox.showerror(
                "Installatie mislukt",
                (
                    "De update kon niet worden "
                    "geïnstalleerd.\n\n"
                    "Probeer de applicatie opnieuw "
                    "te starten."
                ),
                parent=self
            )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app = NexoCalculator()

    app.mainloop()
