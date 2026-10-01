class CalculatorKeyboard:

    def __init__(self, calculator_input):
        self.calculator_input = calculator_input

    # =========================================================
    # KEYBOARD VALIDATION
    # =========================================================

    def validate_keyboard(self, event):
        """
        Verwerkt toetsenbordinvoer voor Nexo Calculator.

        Ondersteund:
        - 0 t/m 9
        - + - * /
        - .
        - ( )
        - Enter
        - Backspace
        - Escape
        - Delete
        - % 
        - ^ / ²
        """

        # -----------------------------------------------------
        # ENTER = BEREKENEN
        # -----------------------------------------------------

        if event.keysym in [
            "Return",
            "KP_Enter"
        ]:

            self.calculator_input.answer()

            return "break"

        # -----------------------------------------------------
        # BACKSPACE
        # -----------------------------------------------------

        if event.keysym == "BackSpace":

            self.calculator_input.backspace()

            return "break"

        # -----------------------------------------------------
        # DELETE = CLEAR ENTRY
        # -----------------------------------------------------

        if event.keysym == "Delete":

            self.calculator_input.clear_entry()

            return "break"

        # -----------------------------------------------------
        # ESCAPE = CLEAR
        # -----------------------------------------------------

        if event.keysym == "Escape":

            self.calculator_input.clear_display()

            return "break"

        # -----------------------------------------------------
        # FUNCTION KEYS / NAVIGATION
        # -----------------------------------------------------

        if event.keysym in [
            "Tab",
            "Up",
            "Down",
            "Left",
            "Right",
            "Home",
            "End",
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R"
        ]:

            return

        # -----------------------------------------------------
        # Geen karakter
        # -----------------------------------------------------

        if not event.char:
            return "break"

        character = event.char

        # -----------------------------------------------------
        # Normale cijfers
        # -----------------------------------------------------

        if character.isdigit():

            self.calculator_input.input_num(
                character
            )

            return "break"

        # -----------------------------------------------------
        # PLUS
        # -----------------------------------------------------

        if character == "+":

            self.calculator_input.input_num(
                "+"
            )

            return "break"

        # -----------------------------------------------------
        # MIN
        # -----------------------------------------------------

        if character == "-":

            self.calculator_input.input_num(
                "-"
            )

            return "break"

        # -----------------------------------------------------
        # MULTIPLICATION
        # -----------------------------------------------------

        if character in [
            "*",
            "×"
        ]:

            self.calculator_input.input_num(
                "×"
            )

            return "break"

        # -----------------------------------------------------
        # DIVISION
        # -----------------------------------------------------

        if character in [
            "/",
            "÷"
        ]:

            self.calculator_input.input_num(
                "÷"
            )

            return "break"

        # -----------------------------------------------------
        # DECIMAL
        # -----------------------------------------------------

        if character in [
            ".",
            ","
        ]:

            self.calculator_input.input_num(
                "."
            )

            return "break"

        # -----------------------------------------------------
        # PARENTHESES
        # -----------------------------------------------------

        if character in [
            "(",
            ")"
        ]:

            self.calculator_input.input_num(
                character
            )

            return "break"

        # -----------------------------------------------------
        # PERCENTAGE
        # -----------------------------------------------------

        if character == "%":

            self.calculator_input.percentage()

            return "break"

        # -----------------------------------------------------
        # SQUARE
        # -----------------------------------------------------

        if character in [
            "^",
            "²"
        ]:

            if character == "^":

                self.calculator_input.input_num(
                    "²"
                )

            else:

                self.calculator_input.input_num(
                    "²"
                )

            return "break"

        # -----------------------------------------------------
        # Alles wat niet ondersteund wordt blokkeren
        # -----------------------------------------------------

        return "break"
