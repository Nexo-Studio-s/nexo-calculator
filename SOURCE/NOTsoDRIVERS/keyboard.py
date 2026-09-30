class CalculatorKeyboard:

    def __init__(self, calculator_input):
        self.calculator_input = calculator_input

    def validate_keyboard(self, event):

        allowed_chars = "0123456789+-*/.()"

        if event.keysym in [
            "Return",
            "Tab",
            "Up",
            "Down",
            "Left",
            "Right"
        ]:
            return

        if event.keysym == "BackSpace":
            self.calculator_input.backspace()
            return "break"

        if (
            event.char
            and event.char in allowed_chars
        ):
            character = event.char

            if character == "*":
                character = "×"

            elif character == "/":
                character = "÷"

            self.calculator_input.input_num(
                character
            )

            return "break"

        return "break"
