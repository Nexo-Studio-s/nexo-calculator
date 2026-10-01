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

        # =====================================================
        # STYLE
        # =====================================================

        self.font_buttons = (
            "Consolas",
            16
        )

        self.bg_glass = "#161b22"
        self.border_glass = "#30363d"

        self.accent_color = "#19a8b2"
        self.accent_hover = "#14868e"

        self.delete_color = "#d9534f"
        self.delete_hover = "#b53f3c"

        self.equal_color = "#23c2ce"
        self.equal_hover = "#1ca2ad"

        # =====================================================
        # INTERNAL STATE
        # =====================================================

        self.button_frame = None
        self.buttons = []

    # =========================================================
    # CLEAN START
    # =========================================================

    def create_buttons(self):
        """
        Bouwt de calculator-UI volledig opnieuw op.

        Er wordt bewust eerst alles verwijderd wat deze UI
        eerder heeft aangemaakt. Hierdoor ontstaan geen dubbele
        widgets of oude callbacks bij een nieuwe initialisatie.
        """

        self._clear_previous_ui()

        # -----------------------------------------------------
        # Container
        # -----------------------------------------------------

        self.button_frame = ctk.CTkFrame(
            self.app,
            fg_color="transparent"
        )

        self.button_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        # -----------------------------------------------------
        # Grid configuration
        # -----------------------------------------------------

        for column in range(4):

            self.button_frame.grid_columnconfigure(
                column,
                weight=1,
                uniform="calculator_column"
            )

        for row in range(6):

            self.button_frame.grid_rowconfigure(
                row,
                weight=1,
                uniform="calculator_row"
            )

        # -----------------------------------------------------
        # Button definitions
        # -----------------------------------------------------

        buttons = [
            ("%", 0, 0),
            ("CE", 0, 1),
            ("C", 0, 2),
            ("⌫", 0, 3),

            ("(", 1, 0),
            ("𝑥²", 1, 1),
            (")", 1, 2),
            ("÷", 1, 3),

            ("7", 2, 0),
            ("8", 2, 1),
            ("9", 2, 2),
            ("×", 2, 3),

            ("4", 3, 0),
            ("5", 3, 1),
            ("6", 3, 2),
            ("-", 3, 3),

            ("1", 4, 0),
            ("2", 4, 1),
            ("3", 4, 2),
            ("+", 4, 3),

            ("+/-", 5, 0),
            ("0", 5, 1),
            (".", 5, 2),
            ("=", 5, 3)
        ]

        # -----------------------------------------------------
        # Create buttons
        # -----------------------------------------------------

        for text, row, column in buttons:

            command = self._get_command(
                text
            )

            fg_color = self.bg_glass
            hover_color = "#21262d"

            # -------------------------------------------------
            # Operator buttons
            # -------------------------------------------------

            if text in [
                "÷",
                "×",
                "-",
                "+"
            ]:

                fg_color = self.accent_color
                hover_color = self.accent_hover

            # -------------------------------------------------
            # Delete button
            # -------------------------------------------------

            elif text == "⌫":

                fg_color = self.delete_color
                hover_color = self.delete_hover

            # -------------------------------------------------
            # Equals button
            # -------------------------------------------------

            elif text == "=":

                fg_color = self.equal_color
                hover_color = self.equal_hover

            # -------------------------------------------------
            # Button
            # -------------------------------------------------

            button = ctk.CTkButton(
                self.button_frame,
                text=text,
                font=self.font_buttons,
                command=command,
                corner_radius=8,
                fg_color=fg_color,
                hover_color=hover_color,
                text_color="#f0f6fc",
                border_color=(
                    self.border_glass
                    if fg_color == self.bg_glass
                    else fg_color
                ),
                border_width=(
                    1
                    if fg_color == self.bg_glass
                    else 0
                )
            )

            button.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=5,
                pady=5
            )

            self.buttons.append(
                button
            )

    # =========================================================
    # COMMAND ROUTING
    # =========================================================

    def _get_command(self, text):
        """
        Koppelt iedere knop aan exact één actie.

        Hierdoor zijn er geen losse lambda's met verkeerde
        waarden of onverwachte callbacks.
        """

        if text == "=":
            return self.calculator_input.answer

        if text == "C":
            return self.calculator_input.clear_display

        if text == "CE":
            return self.calculator_input.clear_entry

        if text == "⌫":
            return self.calculator_input.backspace

        if text == "+/-":
            return self.calculator_input.toggle_sign

        if text == "%":
            return self.calculator_input.percentage

        if text == "𝑥²":

            return lambda: (
                self.calculator_input.input_num(
                    "²"
                )
            )

        return lambda value=text: (
            self.calculator_input.input_num(
                value
            )
        )

    # =========================================================
    # CLEANUP
    # =========================================================

    def _clear_previous_ui(self):
        """
        Verwijdert uitsluitend de vorige button-container
        van deze CalculatorUI.

        De input_box en andere onderdelen van de applicatie
        worden hierdoor niet aangeraakt.
        """

        # -----------------------------------------------------
        # Oude knopreferenties opruimen
        # -----------------------------------------------------

        for button in self.buttons:

            try:
                button.destroy()
            except Exception:
                pass

        self.buttons.clear()

        # -----------------------------------------------------
        # Oude container verwijderen
        # -----------------------------------------------------

        if self.button_frame is not None:

            try:
                self.button_frame.destroy()
            except Exception:
                pass

            self.button_frame = None

    # =========================================================
    # DESTROY
    # =========================================================

    def destroy(self):
        """
        Handmatige cleanup wanneer de CalculatorUI
        volledig verwijderd moet worden.
        """

        self._clear_previous_ui()
