import sys
import platform
import customtkinter as ctk
from tkinter import messagebox

from Calculate.calculator import Calculator
from Input.input import CalculatorInput
from NOTsoDRIVERS.keyboard import CalculatorKeyboard
from UserInterface.ui import CalculatorUI


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
