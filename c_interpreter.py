"""
C Expression Interpreter - Evaluates AST and computes expression results.

This module provides a recursive AST evaluator that:
- Maintains a symbol table (variable environment)
- Handles all C operators with correct semantics
- Implements short-circuit logic for && and ||
- Manages side effects (assignment, increment/decrement)
"""


class CInterpreter:
    """
    Recursive AST interpreter for C expressions.
    
    Maintains a symbol table and evaluates AST nodes to produce values.
    """

    def __init__(self, variables=None):
        """
        Initialize interpreter with optional initial variables.
        
        Args:
            variables: dict of initial variable bindings (e.g., {'a': 10, 'b': 20})
        """
        self.variables = variables if variables is not None else {}

    def _lookup(self, name: str):
        """
        Look up a variable in the symbol table.
        
        Raises NameError if variable not found.
        """
        if name not in self.variables:
            raise NameError(f"Undefined variable: {name!r}")
        return self.variables[name]

    def _update(self, name: str, value):
        """Update a variable in the symbol table."""
        self.variables[name] = value

    def _to_int(self, value):
        """Convert value to integer (for bitwise operations)."""
        if isinstance(value, float):
            return int(value)
        return value

    def _to_bool(self, value):
        """Convert value to boolean (for logical operations)."""
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, bool):
            return value
        return bool(value)

    def evaluate(self, node):
        """
        Recursively evaluate an AST node and return its value.
        
        Node types:
        - ('ID', name): variable lookup
        - ('NUMBER', value): numeric literal
        - ('BINARY', op, left, right): binary operation
        - ('UNARY', op, operand): unary operation
        - ('ASSIGN', op, target, value): assignment
        - ('CONDITIONAL', cond, true_branch, false_branch): ternary operator
        - ('SUBSCRIPT', array_ref, index): array subscript
        """
        if not isinstance(node, tuple) or len(node) < 2:
            raise TypeError(f"Invalid AST node: {node!r}")

        node_type = node[0]

        # ===== Primary Nodes =====
        if node_type == 'ID':
            _, name = node
            return self._lookup(name)

        if node_type == 'NUMBER':
            _, value = node
            # Parse numeric literal
            if value.startswith(('0x', '0X')):
                return int(value, 16)
            elif value.startswith(('0b', '0B')):
                return int(value, 2)
            elif value.startswith('0') and len(value) > 1 and '.' not in value:
                return int(value, 8)  # octal
            elif '.' in value or 'e' in value.lower():
                return float(value)
            else:
                return int(value)

        # ===== Binary Operators =====
        if node_type == 'BINARY':
            _, op, left, right = node
            return self._evaluate_binary(op, left, right)

        # ===== Unary Operators =====
        if node_type == 'UNARY':
            _, op, operand = node
            return self._evaluate_unary(op, operand)

        # ===== Assignment Operators =====
        if node_type == 'ASSIGN':
            _, op, target, value = node
            return self._evaluate_assignment(op, target, value)

        # ===== Conditional Operator =====
        if node_type == 'CONDITIONAL':
            _, cond, true_branch, false_branch = node
            cond_val = self.evaluate(cond)
            if self._to_bool(cond_val):
                return self.evaluate(true_branch)
            else:
                return self.evaluate(false_branch)

        # ===== Subscript Operator =====
        if node_type == 'SUBSCRIPT':
            _, array_ref, index_expr = node
            array_val = self.evaluate(array_ref)
            index_val = self.evaluate(index_expr)
            try:
                return array_val[int(index_val)]
            except (IndexError, KeyError, TypeError) as e:
                raise RuntimeError(f"Subscript error: {e}")

        raise TypeError(f"Unknown AST node type: {node_type!r}")

    def _evaluate_binary(self, op: str, left, right):
        """Evaluate binary operators."""
        # Short-circuit evaluation for logical operators
        if op == '&&':
            left_val = self.evaluate(left)
            if not self._to_bool(left_val):
                return 0  # short-circuit: return false without evaluating right
            right_val = self.evaluate(right)
            return 1 if self._to_bool(right_val) else 0

        if op == '||':
            left_val = self.evaluate(left)
            if self._to_bool(left_val):
                return 1  # short-circuit: return true without evaluating right
            right_val = self.evaluate(right)
            return 1 if self._to_bool(right_val) else 0

        # Comma operator: evaluate both but return right
        if op == ',':
            self.evaluate(left)
            return self.evaluate(right)

        # For other operators, evaluate both sides
        left_val = self.evaluate(left)
        right_val = self.evaluate(right)

        # Arithmetic operators
        if op == '+':
            return left_val + right_val
        if op == '-':
            return left_val - right_val
        if op == '*':
            return left_val * right_val
        if op == '/':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            # Integer division for integers, float division otherwise
            if isinstance(left_val, int) and isinstance(right_val, int):
                return left_val // right_val
            else:
                return left_val / right_val
        if op == '%':
            if right_val == 0:
                raise ZeroDivisionError("Modulo by zero")
            return self._to_int(left_val) % self._to_int(right_val)

        # Shift operators
        if op == '<<':
            return self._to_int(left_val) << self._to_int(right_val)
        if op == '>>':
            return self._to_int(left_val) >> self._to_int(right_val)

        # Bitwise operators
        if op == '&':
            return self._to_int(left_val) & self._to_int(right_val)
        if op == '|':
            return self._to_int(left_val) | self._to_int(right_val)
        if op == '^':
            return self._to_int(left_val) ^ self._to_int(right_val)

        # Comparison operators (return 1 or 0 as in C)
        if op == '<':
            return 1 if left_val < right_val else 0
        if op == '<=':
            return 1 if left_val <= right_val else 0
        if op == '>':
            return 1 if left_val > right_val else 0
        if op == '>=':
            return 1 if left_val >= right_val else 0
        if op == '==':
            return 1 if left_val == right_val else 0
        if op == '!=':
            return 1 if left_val != right_val else 0

        raise NotImplementedError(f"Unknown binary operator: {op!r}")

    def _evaluate_unary(self, op: str, operand):
        """Evaluate unary operators."""
        # Postfix operators (++ and --) modify the variable and return old value
        if op == 'post++':
            if not isinstance(operand, tuple) or operand[0] != 'ID':
                raise TypeError("post++ requires an lvalue (variable)")
            var_name = operand[1]
            old_val = self._lookup(var_name)
            self._update(var_name, old_val + 1)
            return old_val  # return old value

        if op == 'post--':
            if not isinstance(operand, tuple) or operand[0] != 'ID':
                raise TypeError("post-- requires an lvalue (variable)")
            var_name = operand[1]
            old_val = self._lookup(var_name)
            self._update(var_name, old_val - 1)
            return old_val  # return old value

        # Prefix operators (++ and --) modify the variable and return new value
        if op == '++':
            if not isinstance(operand, tuple) or operand[0] != 'ID':
                raise TypeError("++ requires an lvalue (variable)")
            var_name = operand[1]
            new_val = self._lookup(var_name) + 1
            self._update(var_name, new_val)
            return new_val  # return new value

        if op == '--':
            if not isinstance(operand, tuple) or operand[0] != 'ID':
                raise TypeError("-- requires an lvalue (variable)")
            var_name = operand[1]
            new_val = self._lookup(var_name) - 1
            self._update(var_name, new_val)
            return new_val  # return new value

        # Logical NOT
        if op == '!':
            val = self.evaluate(operand)
            return 1 if not self._to_bool(val) else 0

        # Bitwise NOT
        if op == '~':
            val = self._to_int(self.evaluate(operand))
            return ~val

        # Unary plus
        if op == '+':
            return self.evaluate(operand)

        # Unary minus
        if op == '-':
            return -self.evaluate(operand)

        raise NotImplementedError(f"Unknown unary operator: {op!r}")

    def _evaluate_assignment(self, op: str, target, value):
        """Evaluate assignment operators."""
        rhs_val = self.evaluate(value)

        # Handle simple variable assignment
        if isinstance(target, tuple) and target[0] == 'ID':
            var_name = target[1]
            current_val = self._lookup(var_name) if var_name in self.variables else 0

            # Simple assignment
            if op == '=':
                self._update(var_name, rhs_val)
                return rhs_val

            # Compound assignments
            if op == '+=':
                new_val = current_val + rhs_val
            elif op == '-=':
                new_val = current_val - rhs_val
            elif op == '*=':
                new_val = current_val * rhs_val
            elif op == '/=':
                if rhs_val == 0:
                    raise ZeroDivisionError("Division by zero")
                new_val = current_val // rhs_val if isinstance(current_val, int) and isinstance(rhs_val, int) else current_val / rhs_val
            elif op == '%=':
                if rhs_val == 0:
                    raise ZeroDivisionError("Modulo by zero")
                new_val = self._to_int(current_val) % self._to_int(rhs_val)
            elif op == '<<=':
                new_val = self._to_int(current_val) << self._to_int(rhs_val)
            elif op == '>>=':
                new_val = self._to_int(current_val) >> self._to_int(rhs_val)
            elif op == '&=':
                new_val = self._to_int(current_val) & self._to_int(rhs_val)
            elif op == '|=':
                new_val = self._to_int(current_val) | self._to_int(rhs_val)
            elif op == '^=':
                new_val = self._to_int(current_val) ^ self._to_int(rhs_val)
            else:
                raise NotImplementedError(f"Unknown assignment operator: {op!r}")

            self._update(var_name, new_val)
            return new_val

        # Handle subscript assignment (e.g., arr[i] = value)
        elif isinstance(target, tuple) and target[0] == 'SUBSCRIPT':
            _, array_ref, index_expr = target
            if not isinstance(array_ref, tuple) or array_ref[0] != 'ID':
                raise TypeError("Subscript assignment target array must be a variable")

            array_name = array_ref[1]
            array_obj = self._lookup(array_name)
            index_val = int(self.evaluate(index_expr))

            if op == '=':
                array_obj[index_val] = rhs_val
                return rhs_val
            else:
                # Compound assignment on subscripted element
                current_val = array_obj[index_val]
                if op == '+=':
                    new_val = current_val + rhs_val
                elif op == '-=':
                    new_val = current_val - rhs_val
                elif op == '*=':
                    new_val = current_val * rhs_val
                elif op == '/=':
                    if rhs_val == 0:
                        raise ZeroDivisionError("Division by zero")
                    new_val = current_val // rhs_val if isinstance(current_val, int) and isinstance(rhs_val, int) else current_val / rhs_val
                elif op == '%=':
                    if rhs_val == 0:
                        raise ZeroDivisionError("Modulo by zero")
                    new_val = self._to_int(current_val) % self._to_int(rhs_val)
                elif op == '<<=':
                    new_val = self._to_int(current_val) << self._to_int(rhs_val)
                elif op == '>>=':
                    new_val = self._to_int(current_val) >> self._to_int(rhs_val)
                elif op == '&=':
                    new_val = self._to_int(current_val) & self._to_int(rhs_val)
                elif op == '|=':
                    new_val = self._to_int(current_val) | self._to_int(rhs_val)
                elif op == '^=':
                    new_val = self._to_int(current_val) ^ self._to_int(rhs_val)
                else:
                    raise NotImplementedError(f"Unknown assignment operator: {op!r}")
                array_obj[index_val] = new_val
                return new_val

        else:
            raise TypeError("Assignment target must be an lvalue (variable or subscript)")

    def run(self, ast):
        """
        Evaluate the AST and return the final value.
        """
        return self.evaluate(ast)


# ===== Test Harness =====

if __name__ == '__main__':
    from c_lexer import CLexer
    from c_parser import CExpressionParser, ast_to_string

    # Sample test cases with initial variables
    test_cases = [
        ("a + b", {'a': 5, 'b': 3}),
        ("a * 2 + b", {'a': 4, 'b': 10}),
        ("a < b && b < c", {'a': 1, 'b': 5, 'c': 10}),
        ("a = 10", {}),
        ("a = 10; b = a + 5", {'a': 0}),
        ("x = 5", {}),
        ("y = ++x", {'x': 5}),
        ("y = x++", {'x': 5}),
        ("a = 8", {}),
        ("b = a >>= 2", {'a': 8}),
        ("a ? b : c", {'a': 1, 'b': 100, 'c': 200}),
        ("flag = (a != 0) && (b >= 10) || !c", {'a': 5, 'b': 15, 'c': 0}),
    ]

    print("=" * 70)
    print("C Expression Interpreter - Test Results")
    print("=" * 70)

    for expr_str, init_vars in test_cases:
        print(f"\nExpression: {expr_str}")
        print(f"Initial variables: {init_vars}")
        print("-" * 70)

        try:
            # Tokenize and parse
            lexer = CLexer()
            lexer.text = expr_str
            lexer._build_regex()
            tokens = list(lexer.tokenize())

            parser = CExpressionParser(tokens)
            ast = parser.parse()

            # Interpret
            interpreter = CInterpreter(init_vars.copy())
            result = interpreter.run(ast)

            print(f"Result: {result}")
            
            # Print variables in alphabetical order
            if interpreter.variables:
                print("变量最终状态:")
                for var_name in sorted(interpreter.variables.keys()):
                    print(f"{var_name}={interpreter.variables[var_name]}")
            else:
                print("变量最终状态: (empty)")

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)
