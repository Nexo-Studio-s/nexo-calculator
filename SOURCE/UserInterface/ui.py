import customtkinter as ctk


class CalculatorUI:

    def __init__(
        self,
        app,
        input_box,
        calculator,
        calculator_input
    ):
        self.app = app
        self.input_box = input_box
        self.calculator = calculator
        self.calculator_input = calculator_input

        self.font_buttons = ("Consolas", 16)

        self.bg_glass = "#161b22"
        self.border_glass = "#30363d"

        self.accent_color = "#19a8b2"
        self.accent_hover = "#14868e"

        self.delete_color = "#d9534f"
        self.delete_hover = "#b53f3c"

        self.equal_color = "#23c2ce"
        self.equal_hover = "#1ca2ad"

    def create_buttons(self):

        buttons = [
            ("%", 1, 0, None, None),
            ("CE", 1, 1, None, None),
            ("C", 1, 2, None, None),
            ("⌫", 1, 3, self.delete_color, self.delete_hover),

            ("(", 2, 0, None, None),
            ("𝑥²", 2, 1, None, None),
            (")", 2, 2, None, None),
            ("÷", 2, 3, self.accent_color, self.accent_hover),

            ("7", 3, 0, None, None),
            ("8", 3, 1, None, None),
            ("9", 3, 2, None, None),
            ("×", 3, 3, self.accent_color, self.accent_hover),

            ("4", 4, 0, None, None),
            ("5", 4, 1, None, None),
            ("6", 4, 2, None, None),
            ("-", 4, 3, self.accent_color, self.accent_hover),

            ("1", 5, 0, None, None),
            ("2", 5, 1, None, None),
            ("3", 5, 2, None, None),
            ("+", 5, 3, self.accent_color, self.accent_hover),

            ("+/-", 6, 0, None, None),
            ("0", 6, 1, None, None),
            (".", 6, 2, None, None),
            ("=", 6, 3, self.equal_color, self.equal_hover)
        ]

        for text, row, col, color, hover in buttons:

            if text == "=":
                command = self.calculator_input.answer

            elif text == "C":
                command = self.calculator_input.clear_display

            elif text == "CE":
                command = self.calculator_input.clear_entry

            elif text == "⌫":
                command = self.calculator_input.backspace

            elif text == "+/-":
                command = self.calculator_input.toggle_sign

            elif text == "%":
                command = self.calculator_input.percentage

            else:
                display_text = "²" if text == "𝑥²" else text

                command = (
                    lambda value=display_text:
                    self.calculator_input.input_num(value)
                )

            button = ctk.CTkButton(
                self.app,
                text=text,
                font=self.font_buttons,
                command=command,
                corner_radius=8,
                fg_color=color if color else self.bg_glass,
                border_color=self.border_glass if not color else None,
                border_width=1 if not color else 0,
                text_color="#f0f6fc",
                hover_color=hover if hover else "#21262d"
            )

            button.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=5,
                pady=5
            )
