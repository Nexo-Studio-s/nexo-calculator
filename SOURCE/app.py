import sys
import platform

import customtkinter as ctk
from tkinter import messagebox

from Calculate.calculator import Calculator
from Input.input import CalculatorInput
from NOTsoDRIVERS.keyboard import CalculatorKeyboard
from UserInterface.ui import CalculatorUI

from Updates.update_manager import (
    get_latest_release,
    download_update,
    get_pending_update,
    install_and_restart
)


# ============================================================
# Nexo Calculator
# Public Version:  v0.2026.00009
# Internal Build:  INT01
# ============================================================

PUBLIC_VERSION = "0.2026.00009"
INTERNAL_BUILD = "INT01"


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NexoCalculator(ctk.CTk):

    MIN_PYTHON_VERSION = (3, 8)
    MIN_WIN_VERSION = 10

    ERROR_MESSAGES = [
        "Error",
        "Cannot divide by zero"
    ]

    def __init__(self):
        super().__init__()

        if not self.check_system_requirements():
            self.destroy()
            sys.exit(1)

        self.title(
            f"NEXO CALCULATOR v{PUBLIC_VERSION}"
        )

        self.geometry("360x540")
        self.minsize(300, 450)

        self.configure(
            fg_color="#0d1117"
        )

        self.grid_rowconfigure(0, weight=2)

        for i in range(1, 7):
            self.grid_rowconfigure(i, weight=1)

        for j in range(4):
            self.grid_columnconfigure(j, weight=1)

        self.input_box = ctk.CTkEntry(
            self,
            font=("Consolas", 26, "bold"),
            justify="right",
            height=65,
            corner_radius=12,
            fg_color="#161b22",
            border_color="#30363d",
            border_width=1,
            text_color="#f0f6fc"
        )

        self.input_box.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=15,
            pady=15
        )

        self.calculator = Calculator(
            error_messages=self.ERROR_MESSAGES
        )

        self.calculator_input = CalculatorInput(
            input_box=self.input_box,
            error_messages=self.ERROR_MESSAGES
        )

        self.calculator_input.set_calculator(
            self.calculator
        )

        self.calculator_keyboard = CalculatorKeyboard(
            calculator_input=self.calculator_input
        )

        self.ui = CalculatorUI(
            app=self,
            input_box=self.input_box,
            calculator=self.calculator,
            calculator_input=self.calculator_input
        )

        self.ui.create_buttons()

        self.bind(
            "<Return>",
            lambda event: self.calculator_input.answer()
        )

        self.bind(
            "<Key>",
            self.calculator_keyboard.validate_keyboard
        )

        # Nexo Studios Update System
        self.initialize_updates()

    # ========================================================
    # Nexo Studios Update System
    # ========================================================

    def initialize_updates(self):
        """Check for pending and available updates."""

        pending = get_pending_update()

        if pending:
            self.after(
                500,
                lambda: self.show_downloaded_update(
                    pending["version"]
                )
            )
            return

        self.after(
            1000,
            self.check_for_updates
        )

    def check_for_updates(self):
        """Check GitHub Releases for a newer Nexo version."""

        release = get_latest_release(
            PUBLIC_VERSION
        )

        if release is None:
            return

        version = release.get(
            "tag_name",
            ""
        )

        self.show_update_available(
            version,
            release
        )

    # ========================================================
    # Update Available
    # ========================================================

    def show_update_available(
        self,
        version,
        release
    ):
        """Show the available update dialog."""

        dialog = ctk.CTkToplevel(self)

        dialog.title(
            "Nexo Calculator Update"
        )

        dialog.geometry(
            "420x250"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Update available",
            font=("Arial", 22, "bold")
        ).pack(
            pady=(25, 10)
        )

        ctk.CTkLabel(
            dialog,
            text=(
                "A new version of Nexo Calculator "
                "is available:\n\n"
                f"{version}"
            ),
            font=("Arial", 15)
        ).pack(
            pady=10
        )

        buttons = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        buttons.pack(
            pady=15
        )

        def download():
            dialog.destroy()

            success = download_update(
                release
            )

            if success:
                self.show_downloaded_update(
                    version
                )
            else:
                messagebox.showerror(
                    "Update Error",
                    "The update could not be downloaded."
                )

        def later():
            dialog.destroy()

        ctk.CTkButton(
            buttons,
            text="Download Now",
            width=160,
            command=download
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        ctk.CTkButton(
            buttons,
            text="Notify me Later",
            width=160,
            command=later
        ).grid(
            row=0,
            column=1,
            padx=8
        )

    # ========================================================
    # Downloaded Update
    # ========================================================

    def show_downloaded_update(
        self,
        version
    ):
        """Show the pending installation dialog."""

        dialog = ctk.CTkToplevel(self)

        dialog.title(
            "Nexo Calculator Update"
        )

        dialog.geometry(
            "440x250"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Update downloaded",
            font=("Arial", 22, "bold")
        ).pack(
            pady=(25, 10)
        )

        ctk.CTkLabel(
            dialog,
            text=(
                f"{version} has been "
                "downloaded for you."
            ),
            font=("Arial", 15)
        ).pack(
            pady=15
        )

        buttons = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        buttons.pack(
            pady=15
        )

        def install():
            success = install_and_restart()

            if success:
                dialog.destroy()
                self.destroy()

        def later():
            dialog.destroy()

        ctk.CTkButton(
            buttons,
            text="Install & Restart now",
            width=180,
            command=install
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        ctk.CTkButton(
            buttons,
            text="Notify me later",
            width=160,
            command=later
        ).grid(
            row=0,
            column=1,
            padx=8
        )

    # ========================================================
    # System Requirements
    # ========================================================

    def check_system_requirements(self) -> bool:
        """Check minimum Python and OS requirements."""

        if sys.version_info < self.MIN_PYTHON_VERSION:
            messagebox.showerror(
                "System Error",
                f"Python "
                f"{self.MIN_PYTHON_VERSION[0]}."
                f"{self.MIN_PYTHON_VERSION[1]} "
                f"or newer is required!"
            )

            return False

        os_name = platform.system()

        if os_name == "Windows":
            try:
                win_ver = int(
                    platform.release()
                )

                if win_ver < self.MIN_WIN_VERSION:
                    messagebox.showwarning(
                        "Compatibility Warning",
                        f"Nexo Calculator is optimized "
                        f"for Windows "
                        f"{self.MIN_WIN_VERSION}+."
                    )

            except ValueError:
                pass

        elif os_name == "Darwin":
            pass

        elif os_name == "Linux":
            pass

        return True
