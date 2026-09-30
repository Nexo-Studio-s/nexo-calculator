class CalculatorInput:

    def __init__(self, input_box, error_messages):
        self.input_box = input_box
        self.ERROR_MESSAGES = error_messages

        self.calculator = None

    def set_calculator(self, calculator):
        self.calculator = calculator

    def input_num(self, value):
        current = self.input_box.get()

        if current in self.ERROR_MESSAGES:
            self.clear_display()
            current = ""

        operators = [
            "+",
            "-",
            "×",
            "÷",
            "²",
            "."
        ]

        if (
            value in operators
            and current
            and current[-1] in operators
        ):
            self.input_box.delete(
                len(current) - 1,
                "end"
            )
            current = self.input_box.get()

        if value == ".":
            number_part = current

            last_operator = -1

            for character in [
                "+",
                "-",
                "×",
                "÷",
                "(",
                ")"
            ]:
                position = current.rfind(character)

                if position > last_operator:
                    last_operator = position

            if last_operator >= 0:
                number_part = current[last_operator + 1:]

            if "." in number_part:
                return

        self.input_box.insert(
            "end",
            str(value)
        )

    def clear_display(self):
        self.input_box.delete(0, "end")

    def clear_entry(self):
        current = self.input_box.get()

        if not current or current in self.ERROR_MESSAGES:
            self.clear_display()
            return

        for i in range(len(current) - 1, -1, -1):

            if current[i] in [
                "+",
                "-",
                "*",
                "/",
                "×",
                "÷",
                "("
            ]:
                self.input_box.delete(
                    i + 1,
                    "end"
                )
                return

        self.clear_display()

    def backspace(self):
        current = self.input_box.get()

        if current in self.ERROR_MESSAGES:
            self.clear_display()
            return

        if current:
            self.input_box.delete(
                len(current) - 1,
                "end"
            )

    def toggle_sign(self):
        current = self.input_box.get()

        if not current or current in self.ERROR_MESSAGES:
            return

        if current[-1] in [
            "+",
            "-",
            "×",
            "÷",
            "("
        ]:
            return

        try:
            value = float(current)

            if value.is_integer():
                value = int(value)

            self.clear_display()

            self.input_box.insert(
                "end",
                str(-value)
            )

        except ValueError:

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

    def percentage(self):
        current = self.input_box.get()

        if not current or current in self.ERROR_MESSAGES:
            return

        if current[-1] in [
            "+",
            "-",
            "×",
            "÷",
            "("
        ]:
            return

        try:
            value = float(current) / 100

            if value.is_integer():
                value = int(value)

            self.clear_display()

            self.input_box.insert(
                "end",
                str(value)
            )

        except ValueError:
            self.input_num("÷100")

    def answer(self):
        if not self.calculator:
            return

        expression = self.input_box.get().strip()

        if not expression:
            return

        if expression in self.ERROR_MESSAGES:
            return

        try:

            while expression and expression[-1] in "+-×÷":
                expression = expression[:-1]

            if not expression:
                return

            clean_expression = (
                expression
                .replace("×", "*")
                .replace("÷", "/")
                .replace("²", "**2")
            )

            result = self.calculator.safe_eval(
                clean_expression
            )

            if isinstance(result, float) and result.is_integer():
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

        except Exception:
            self.clear_display()

            self.input_box.insert(
                "end",
                "Error"
            )
