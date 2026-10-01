import ast
import math
import operator as op


class Calculator:

    def __init__(self, error_messages=None):
        self.ERROR_MESSAGES = error_messages or {}

        self.supported_operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.USub: op.neg,
            ast.UAdd: op.pos,
        }

        # Beschermt de calculator tegen extreem grote berekeningen.
        self.MAX_ABS_VALUE = 1e308
        self.MAX_EXPONENT = 1000

    # =========================================================
    # PUBLIC EVALUATOR
    # =========================================================

    def safe_eval(self, expression):
        """
        Veilig uitvoeren van een wiskundige expressie.

        Ondersteund:
        +  -  *  /  **
        haakjes
        positieve en negatieve getallen
        """

        if expression is None:
            raise ValueError("Empty expression")

        expression = str(expression).strip()

        if not expression:
            raise ValueError("Empty expression")

        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )
        except (SyntaxError, ValueError, TypeError) as exc:
            raise ValueError(
                "Invalid expression"
            ) from exc

        result = self._eval_node(
            tree.body
        )

        self._validate_result(result)

        return result

    # =========================================================
    # AST EVALUATOR
    # =========================================================

    def _eval_node(self, node):

        # -----------------------------------------------------
        # Numbers
        # -----------------------------------------------------

        if isinstance(node, ast.Constant):

            value = node.value

            if isinstance(value, bool):
                raise TypeError(
                    "Boolean values are not allowed"
                )

            if isinstance(value, (int, float)):

                if isinstance(value, float):
                    if not math.isfinite(value):
                        raise OverflowError(
                            "Invalid numeric value"
                        )

                self._validate_result(value)

                return value

            raise TypeError(
                "Invalid constant"
            )

        # -----------------------------------------------------
        # Binary operations
        # -----------------------------------------------------

        if isinstance(node, ast.BinOp):

            operator_type = type(node.op)

            if operator_type not in self.supported_operators:
                raise TypeError(
                    "Unsupported operator"
                )

            left = self._eval_node(
                node.left
            )

            right = self._eval_node(
                node.right
            )

            # -------------------------------------------------
            # Division
            # -------------------------------------------------

            if isinstance(node.op, ast.Div):

                if right == 0:
                    raise ZeroDivisionError(
                        "Division by zero"
                    )

            # -------------------------------------------------
            # Power
            # -------------------------------------------------

            if isinstance(node.op, ast.Pow):

                if abs(right) > self.MAX_EXPONENT:
                    raise OverflowError(
                        "Exponent too large"
                    )

                # 0 ** negative = error
                if left == 0 and right < 0:
                    raise ZeroDivisionError(
                        "Zero cannot be raised "
                        "to a negative power"
                    )

                # Voorkom extreem grote tussenresultaten.
                if abs(left) > 1 and right > 0:

                    try:
                        estimated = (
                            right
                            * math.log10(abs(left))
                        )

                        if estimated > 308:
                            raise OverflowError(
                                "Result too large"
                            )

                    except ValueError:
                        raise OverflowError(
                            "Invalid power operation"
                        )

            try:

                result = self.supported_operators[
                    operator_type
                ](
                    left,
                    right
                )

            except ZeroDivisionError:
                raise ZeroDivisionError(
                    "Division by zero"
                )

            except OverflowError:
                raise OverflowError(
                    "Result too large"
                )

            except (ValueError, TypeError) as exc:
                raise TypeError(
                    "Invalid mathematical operation"
                ) from exc

            self._validate_result(
                result
            )

            return result

        # -----------------------------------------------------
        # Unary operations
        # -----------------------------------------------------

        if isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in self.supported_operators:
                raise TypeError(
                    "Unsupported operator"
                )

            operand = self._eval_node(
                node.operand
            )

            try:

                result = self.supported_operators[
                    operator_type
                ](
                    operand
                )

            except (OverflowError, ValueError) as exc:
                raise OverflowError(
                    "Invalid numeric result"
                ) from exc

            self._validate_result(
                result
            )

            return result

        # -----------------------------------------------------
        # Alles anders blokkeren
        # -----------------------------------------------------

        raise TypeError(
            f"Unsupported operation: "
            f"{type(node).__name__}"
        )

    # =========================================================
    # RESULT VALIDATION
    # =========================================================

    def _validate_result(self, value):
        """
        Controleert of een resultaat nog een geldig
        numeriek resultaat is.
        """

        if isinstance(value, bool):
            raise TypeError(
                "Boolean values are not allowed"
            )

        if not isinstance(
            value,
            (int, float)
        ):
            raise TypeError(
                "Invalid numeric result"
            )

        if isinstance(value, float):

            if not math.isfinite(value):
                raise OverflowError(
                    "Result is not finite"
                )

        if abs(value) > self.MAX_ABS_VALUE:
            raise OverflowError(
                "Result too large"
            )

    # =========================================================
    # ERROR MESSAGE HELPER
    # =========================================================

    def get_error_message(
        self,
        error
    ):
        """
        Geeft een gebruikersvriendelijke foutmelding terug
        wanneer deze beschikbaar is in ERROR_MESSAGES.
        """

        error_type = type(error).__name__

        return self.ERROR_MESSAGES.get(
            error_type,
            str(error)
        )
