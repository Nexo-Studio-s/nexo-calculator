import sys
import platform
import customtkinter as ctk
from tkinter import messagebox

from calculator import Calculator
from input import CalculatorInput
from keyboard import CalculatorKeyboard
from ui import CalculatorUI


# ============================================================
# Nexo Calculator
# Public Version:  v0.2026.00007
# Internal Build:  INT01
# ============================================================

PUBLIC_VERSION = "0.2026.00007"
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

        self.title(f"NEXO CALCULATOR v{PUBLIC_VERSION}")
        self.geometry("360x540")
        self.minsize(300, 450)
        self.configure(fg_color="#0d1117")

        self.grid_rowconfigure(0, weight=2)

        for i in range(1, 7):
            self.grid_rowconfigure(i, weight=1)

        for j in range(4):
            self.grid_columnconfigure(j, weight=1)

        self.font_display = ("Consolas", 26, "bold")
        self.font_buttons = ("Consolas", 16)

        self.bg_glass = "#161b22"
        self.border_glass = "#30363d"

        self.accent_color = "#19a8b2"
        self.accent_hover = "#14868e"

        self.delete_color = "#d9534f"
        self.delete_hover = "#b53f3c"

        self.equal_color = "#23c2ce"
        self.equal_hover = "#1ca2ad"

        self.input_box = ctk.CTkEntry(
            self,
            font=self.font_display,
            justify="right",
            height=65,
            corner_radius=12,
            fg_color=self.bg_glass,
            border_color=self.border_glass,
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

        self.calculator_keyboard = CalculatorKeyboard(
            calculator_input=self.calculator_input
        )

        ui = CalculatorUI(
            app=self,
            input_box=self.input_box,
            calculator=self.calculator,
            calculator_input=self.calculator_input
        )

        ui.create_buttons()

        self.bind(
            "<Return>",
            lambda event: self.calculator_input.answer()
        )

        self.bind(
            "<Key>",
            self.calculator_keyboard.validate_keyboard
        )

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
                win_ver = int(platform.release())

                if win_ver < self.MIN_WIN_VERSION:
                    messagebox.showwarning(
                        "Compatibility Warning",
                        f"Nexo Calculator is optimized for "
                        f"Windows {self.MIN_WIN_VERSION}+."
                    )

            except ValueError:
                pass

        elif os_name == "Darwin":
            pass

        elif os_name == "Linux":
            pass

        return True
