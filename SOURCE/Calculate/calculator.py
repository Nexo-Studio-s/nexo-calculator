import ast
import operator as op


class Calculator:

    def __init__(self, error_messages):
        self.ERROR_MESSAGES = error_messages

        self.supported_operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.USub: op.neg,
            ast.UAdd: op.pos
        }

    def safe_eval(self, expression):
        """Safely evaluate a mathematical expression using AST."""

        if not expression:
            raise ValueError("Empty expression")

        tree = ast.parse(expression, mode="eval")

        return self._eval_node(tree.body)

    def _eval_node(self, node):

        if isinstance(node, ast.Constant):

            if (
                isinstance(node.value, (int, float))
                and not isinstance(node.value, bool)
            ):
                return node.value

            raise TypeError("Invalid constant")

        if isinstance(node, ast.BinOp):

            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            operator_type = type(node.op)

            if operator_type not in self.supported_operators:
                raise TypeError("Unsupported operator")

            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Division by zero")

            if isinstance(node.op, ast.Pow):

                if not isinstance(right, (int, float)):
                    raise TypeError("Invalid exponent")

                if abs(right) > 1000:
                    raise OverflowError("Exponent too large")

            return self.supported_operators[operator_type](
                left,
                right
            )

        if isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in self.supported_operators:
                raise TypeError("Unsupported operator")

            operand = self._eval_node(node.operand)

            return self.supported_operators[operator_type](
                operand
            )

        raise TypeError(
            f"Unsupported operation: {type(node).__name__}"
        )
