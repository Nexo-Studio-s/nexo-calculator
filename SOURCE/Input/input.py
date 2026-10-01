class CalculatorInput:

    def __init__(self, input_box, error_messages):
        self.input_box = input_box
        self.ERROR_MESSAGES = error_messages
        self.calculator = None

        self.operators = [
            "+",
            "-",
            "×",
            "÷"
        ]

    # =========================================================
    # CALCULATOR
    # =========================================================

    def set_calculator(self, calculator):
        self.calculator = calculator

    # =========================================================
    # HELPERS
    # =========================================================

    def is_error(self):
        return self.input_box.get() in self.ERROR_MESSAGES

    def get_current(self):
        return self.input_box.get()

    def clear_display(self):
        self.input_box.delete(
            0,
            "end"
        )

    def _clear_error_if_needed(self):
        if self.is_error():
            self.clear_display()
            return True

        return False

    def _last_number(self, expression):
        """
        Geeft het laatste getal uit een expressie terug.
        """

        if not expression:
            return ""

        index = len(expression) - 1

        while index >= 0:

            if expression[index] in [
                "+",
                "-",
                "×",
                "÷",
                "(",
                ")"
            ]:
                break

            index -= 1

        return expression[index + 1:]

    # =========================================================
    # INPUT
    # =========================================================

    def input_num(self, value):

        self._clear_error_if_needed()

        current = self.get_current()

        value = str(value)

        # -----------------------------------------------------
        # Vier standaard operatoren
        # -----------------------------------------------------

        if value in self.operators:

            # Geen operator aan het begin,
            # behalve min voor een negatief getal.
            if not current:

                if value == "-":
                    self.input_box.insert(
                        "end",
                        value
                    )

                return

            # Geen dubbele operatoren.
            if current[-1] in self.operators:

                self.input_box.delete(
                    len(current) - 1,
                    "end"
                )

            self.input_box.insert(
                "end",
                value
            )

            return

        # -----------------------------------------------------
        # Decimal point
        # -----------------------------------------------------

        if value == ".":

            number_part = self._last_number(
                current
            )

            # Eén punt per getal.
            if "." in number_part:
                return

            # Punt aan het begin -> 0.
            if not current or current[-1] in self.operators:

                self.input_box.insert(
                    "end",
                    "0."
                )

                return

            # Punt na een haakje.
            if current[-1] == "(":

                self.input_box.insert(
                    "end",
                    "0."
                )

                return

            self.input_box.insert(
                "end",
                "."
            )

            return

        # -----------------------------------------------------
        # Square
        # -----------------------------------------------------

        if value == "²":

            if not current:
                return

            if current[-1] in self.operators:
                return

            if current[-1] == "(":
                return

            self.input_box.insert(
                "end",
                "²"
            )

            return

        # -----------------------------------------------------
        # Normale waarde
        # -----------------------------------------------------

        self.input_box.insert(
            "end",
            value
        )

    # =========================================================
    # CLEAR ENTRY
    # =========================================================

    def clear_entry(self):

        current = self.get_current()

        if not current or self.is_error():
            self.clear_display()
            return

        # -----------------------------------------------------
        # Verwijder eerst een eventueel ²-symbool
        # -----------------------------------------------------

        if current.endswith("²"):
            self.input_box.delete(
                len(current) - 1,
                "end"
            )
            return

        # -----------------------------------------------------
        # Zoek einde van laatste invoer
        # -----------------------------------------------------

        depth = 0

        for index in range(
            len(current) - 1,
            -1,
            -1
        ):

            character = current[index]

            if character == ")":
                depth += 1

            elif character == "(":
                depth -= 1

            if depth == 0 and character in [
                "+",
                "-",
                "×",
                "÷"
            ]:

                # Min aan het begin van een getal
                # niet als operator behandelen.
                if (
                    character == "-"
                    and index > 0
                    and current[index - 1] in [
                        "+",
                        "-",
                        "×",
                        "÷",
                        "("
                    ]
                ):
                    continue

                self.input_box.delete(
                    index + 1,
                    "end"
                )

                return

        self.clear_display()

    # =========================================================
    # BACKSPACE
    # =========================================================

    def backspace(self):

        current = self.get_current()

        if self.is_error():
            self.clear_display()
            return

        if not current:
            return

        self.input_box.delete(
            len(current) - 1,
            "end"
        )

    # =========================================================
    # TOGGLE SIGN
    # =========================================================

    def toggle_sign(self):

        current = self.get_current()

        if not current or self.is_error():
            return

        if current[-1] in self.operators:
            return

        if current[-1] == "(":
            return

        # -----------------------------------------------------
        # Alleen één getal
        # -----------------------------------------------------

        try:

            value = float(current)

            if value.is_integer():
                value = int(value)

            self.clear_display()

            self.input_box.insert(
                "end",
                str(-value)
            )

            return

        except ValueError:
            pass

        # -----------------------------------------------------
        # Hele expressie
        # -----------------------------------------------------

        if (
            current.startswith("-(")
            and current.endswith(")")
        ):

            self.clear_display()

            self.input_box.insert(
                "end",
                current[2:-1]
            )

        else:

            self.clear_display()

            self.input_box.insert(
                "end",
                f"-({current})"
            )

    # =========================================================
    # PERCENTAGE
    # =========================================================

    def percentage(self):

        current = self.get_current()

        if not current or self.is_error():
            return

        if current[-1] in self.operators:
            return

        if current[-1] == "(":
            return

        # -----------------------------------------------------
        # Alleen een enkel getal
        # -----------------------------------------------------

        try:

            value = float(current) / 100

            if value.is_integer():
                value = int(value)

            self.clear_display()

            self.input_box.insert(
                "end",
                str(value)
            )

            return

        except ValueError:
            pass

        # -----------------------------------------------------
        # Laatste getal van een expressie
        # -----------------------------------------------------

        number = self._last_number(
            current
        )

        if not number:
            return

        try:

            value = float(number) / 100

            if value.is_integer():
                value = int(value)

            start = len(current) - len(number)

            self.input_box.delete(
                start,
                "end"
            )

            self.input_box.insert(
                "end",
                str(value)
            )

        except ValueError:
            return

    # =========================================================
    # ANSWER
    # =========================================================

    def answer(self):

        if not self.calculator:
            return

        expression = self.get_current().strip()

        if not expression:
            return

        if self.is_error():
            return

        # -----------------------------------------------------
        # Ongeldige afsluitende operatoren verwijderen
        # -----------------------------------------------------

        while (
            expression
            and expression[-1] in "+-×÷"
        ):
            expression = expression[:-1]

        if not expression:
            return

        # -----------------------------------------------------
        # Zet UI-symbolen om naar Python AST-symbolen
        # -----------------------------------------------------

        clean_expression = (
            expression
            .replace("×", "*")
            .replace("÷", "/")
            .replace("²", "**2")
        )

        try:

            result = self.calculator.safe_eval(
                clean_expression
            )

            # -------------------------------------------------
            # Mooie weergave van gehele floats
            # -------------------------------------------------

            if (
                isinstance(result, float)
                and result.is_integer()
            ):
                result = int(result)

            self.clear_display()

            self.input_box.insert(
                "end",
                str(result)
            )

        except ZeroDivisionError:

            self.clear_display()

            self.input_box.insert(
                "end",
                "Cannot divide by zero"
            )

        except OverflowError:

            self.clear_display()

            self.input_box.insert(
                "end",
                "Number too large"
            )

        except ValueError:

            self.clear_display()

            self.input_box.insert(
                "end",
                "Invalid expression"
            )

        except TypeError:

            self.clear_display()

            self.input_box.insert(
                "end",
                "Invalid expression"
            )

        except Exception:

            self.clear_display()

            self.input_box.insert(
                "end",
                "Error"
            )
