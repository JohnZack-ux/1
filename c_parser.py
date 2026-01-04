import re
from collections import namedtuple
from typing import List, Union, Optional
from c_lexer import CLexer, Token

# AST Node type definitions using named tuples
ASTNode = namedtuple('ASTNode', ['type', 'value'], defaults=[None, None])

# Specialized AST node constructors for clarity
def binary_op(op: str, left, right):
    return ('BINARY', op, left, right)

def unary_op(op: str, operand):
    return ('UNARY', op, operand)

def assign_op(op: str, target, value):
    return ('ASSIGN', op, target, value)

def conditional_op(cond, true_branch, false_branch):
    return ('CONDITIONAL', cond, true_branch, false_branch)

def subscript_op(array_ref, index_expr):
    return ('SUBSCRIPT', array_ref, index_expr)

def primary_id(name: str):
    return ('ID', name)

def primary_number(value: str):
    return ('NUMBER', value)

def block_stmt(statements):
    """Create a block statement containing a list of statements."""
    return ('BLOCK', statements)

def declaration_stmt(type_name: str, declarators):
    """Create a declaration statement with type and list of declarators.
    
    declarators is a list of tuples:
    - ('ID', name): simple declaration like 'int a;'
    - ('INIT', name, init_expr): declaration with initialization like 'int a = 10;'
    """
    return ('DECLARATION', type_name, declarators)

def expression_stmt(expr):
    """Create an expression statement."""
    return ('EXPRESSION_STMT', expr)

def empty_stmt():
    """Create an empty statement (just a semicolon)."""
    return ('EMPTY_STMT',)


class CExpressionParser:
    """
    Recursive Descent Parser for C expressions.
    
    Priority levels (lowest to highest):
     1. Comma (,) - left-associative
     2. Assignment (=, +=, -=, *=, /=, %=, <<=, >>=, &=, ^=, |=) - right-associative
     3. Conditional (?:) - right-associative
     4. Logical OR (||) - left-associative
     5. Logical AND (&&) - left-associative
     6. Bitwise OR (|) - left-associative
     7. Bitwise XOR (^) - left-associative
     8. Bitwise AND (&) - left-associative
     9. Equality (==, !=) - left-associative
    10. Relational (<, <=, >, >=) - left-associative
    11. Shift (<<, >>) - left-associative
    12. Additive (+, -) - left-associative
    13. Multiplicative (*, /, %) - left-associative
    14. Unary (!, ~, ++, --, +, -) - right-associative
    15. Postfix ([], ++, --) - left-associative
    16. Primary (ID, NUMBER, ())
    """

    # Token type constants
    ASSIGNMENT_OPS = {'=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|='}
    UNARY_OPS = {'!', '~', '++', '--', '+', '-'}
    POSTFIX_OPS = {'++', '--'}

    def __init__(self, tokens: List[Token]):
        """Initialize parser with a list of tokens from lexer."""
        self.tokens = tokens
        self.pos = 0

    def _current_token(self) -> Optional[Token]:
        """Return the current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _peek_token(self, offset: int = 1) -> Optional[Token]:
        """Peek at token at current position + offset."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _advance(self) -> Optional[Token]:
        """Consume and return current token, then move to next."""
        tok = self._current_token()
        if tok is not None:
            self.pos += 1
        return tok

    def _match(self, *expected_types) -> bool:
        """Check if current token type matches any of expected_types."""
        tok = self._current_token()
        if tok is None:
            return False
        return tok.type in expected_types

    def _expect(self, expected_type: str) -> Token:
        """Consume a token of expected type, raise SyntaxError if mismatch."""
        tok = self._current_token()
        if tok is None:
            raise SyntaxError(f"Unexpected end of input, expected {expected_type!r}")
        if tok.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type!r}, got {tok.type!r} ({tok.value!r}) "
                f"at line {tok.line}, column {tok.column}"
            )
        self._advance()
        return tok

    def _error(self, message: str) -> None:
        """Raise a SyntaxError with current token info."""
        tok = self._current_token()
        if tok:
            raise SyntaxError(f"{message} at line {tok.line}, column {tok.column}")
        raise SyntaxError(f"{message} at end of input")

    # ===== PARSING METHODS (from Primary to Comma) =====

    def primary(self):
        """
        Primary level: handles ID, NUMBER, and parenthesized expressions.
        """
        tok = self._current_token()
        if tok is None:
            self._error("Unexpected end of input in primary expression")

        if tok.type == 'ID':
            tok = self._advance()
            return primary_id(tok.value)

        if tok.type == 'NUMBER':
            tok = self._advance()
            return primary_number(tok.value)

        if tok.type == '(':
            self._advance()  # consume '('
            expr = self.comma()  # parse the full expression inside parentheses
            self._expect(')')
            return expr

        self._error(f"Unexpected token {tok.type!r} in primary expression")

    def postfix(self):
        """
        Postfix level: handles array subscript ([]), post-increment (++), post-decrement (--).
        Left-associative (uses while loop).
        """
        expr = self.primary()

        while True:
            tok = self._current_token()
            if tok is None:
                break

            if tok.type == '[':
                self._advance()  # consume '['
                index_expr = self.comma()  # allow full expressions in subscripts
                self._expect(']')
                expr = subscript_op(expr, index_expr)

            elif tok.type in self.POSTFIX_OPS:
                op = tok.type
                self._advance()
                expr = unary_op(f"post{op}", expr)  # e.g., 'post++', 'post--'

            else:
                break

        return expr

    def unary(self):
        """
        Unary level: handles prefix operators (!, ~, ++, --, unary +, unary -).
        Right-associative (uses recursion).
        """
        tok = self._current_token()
        if tok is not None and tok.type in self.UNARY_OPS:
            op = tok.type
            self._advance()
            operand = self.unary()  # recursive call for right-associativity
            return unary_op(op, operand)

        return self.postfix()

    def multiplicative(self):
        """
        Multiplicative level: *, /, %
        Left-associative (uses while loop).
        """
        expr = self.unary()

        while self._match('*', '/', '%'):
            op = self._advance().type
            right = self.unary()
            expr = binary_op(op, expr, right)

        return expr

    def additive(self):
        """
        Additive level: +, -
        Left-associative (uses while loop).
        """
        expr = self.multiplicative()

        while self._match('+', '-'):
            op = self._advance().type
            right = self.multiplicative()
            expr = binary_op(op, expr, right)

        return expr

    def shift(self):
        """
        Shift level: <<, >>
        Left-associative (uses while loop).
        """
        expr = self.additive()

        while self._match('<<', '>>'):
            op = self._advance().type
            right = self.additive()
            expr = binary_op(op, expr, right)

        return expr

    def relational(self):
        """
        Relational level: <, <=, >, >=
        Left-associative (uses while loop).
        """
        expr = self.shift()

        while self._match('<', '<=', '>', '>='):
            op = self._advance().type
            right = self.shift()
            expr = binary_op(op, expr, right)

        return expr

    def equality(self):
        """
        Equality level: ==, !=
        Left-associative (uses while loop).
        """
        expr = self.relational()

        while self._match('==', '!='):
            op = self._advance().type
            right = self.relational()
            expr = binary_op(op, expr, right)

        return expr

    def bitwise_and(self):
        """
        Bitwise AND level: &
        Left-associative (uses while loop).
        """
        expr = self.equality()

        while self._match('&'):
            op = self._advance().type
            right = self.equality()
            expr = binary_op(op, expr, right)

        return expr

    def bitwise_xor(self):
        """
        Bitwise XOR level: ^
        Left-associative (uses while loop).
        """
        expr = self.bitwise_and()

        while self._match('^'):
            op = self._advance().type
            right = self.bitwise_and()
            expr = binary_op(op, expr, right)

        return expr

    def bitwise_or(self):
        """
        Bitwise OR level: |
        Left-associative (uses while loop).
        """
        expr = self.bitwise_xor()

        while self._match('|'):
            op = self._advance().type
            right = self.bitwise_xor()
            expr = binary_op(op, expr, right)

        return expr

    def logical_and(self):
        """
        Logical AND level: &&
        Left-associative (uses while loop).
        """
        expr = self.bitwise_or()

        while self._match('&&'):
            op = self._advance().type
            right = self.bitwise_or()
            expr = binary_op(op, expr, right)

        return expr

    def logical_or(self):
        """
        Logical OR level: ||
        Left-associative (uses while loop).
        """
        expr = self.logical_and()

        while self._match('||'):
            op = self._advance().type
            right = self.logical_and()
            expr = binary_op(op, expr, right)

        return expr

    def conditional(self):
        """
        Conditional level: ? :
        Right-associative (uses recursion).
        
        C standard: logical-or-expression ? expression : conditional-expression
        
        CRITICAL FIX: The middle expression (between '?' and ':') must be able to
        include commas and assignments. We parse it by:
        1. Starting with assignment()
        2. Manually handling commas in a loop until we hit ':'
        
        This allows expressions like: a > 5 ? b += 5, b : c
        """
        expr = self.logical_or()

        if self._match('?'):
            self._advance()  # consume '?'
            
            # Parse middle expression with manual comma handling
            # This is like comma() but bounded by ':'
            true_branch = self.assignment()
            while self._match(','):
                self._advance()  # consume ','
                right = self.assignment()
                true_branch = binary_op(',', true_branch, right)
            
            self._expect(':')
            false_branch = self.conditional()  # right-associative: recursive call
            expr = conditional_op(expr, true_branch, false_branch)

        return expr

    def assignment(self):
        """
        Assignment level: =, +=, -=, *=, /=, %=, <<=, >>=, &=, ^=, |=
        Right-associative (uses recursion).
        """
        expr = self.conditional()

        if self._match(*self.ASSIGNMENT_OPS):
            op = self._advance().type
            value = self.assignment()  # right-associative: recursive call
            expr = assign_op(op, expr, value)

        return expr

    def comma(self):
        """
        Comma level (lowest precedence): ,
        Left-associative (uses while loop).
        """
        expr = self.assignment()

        while self._match(','):
            self._advance()  # consume ','
            right = self.assignment()
            expr = binary_op(',', expr, right)

        return expr

    def _parse_conditional_middle(self):
        """
        Special helper for parsing the middle expression in conditional.
        This handles the expression between '?' and ':' which can include
        commas and assignments.
        
        Returns to conditional() to maintain proper recursion bounds.
        """
        return self.assignment()  # Start at assignment, commas handled by loop detection

    def parse(self):
        """
        Main entry point: parse the entire program and return the AST root.
        Now supports multiple statements (declarations and expressions).
        """
        return self.program()

    def program(self):
        """
        program -> { statement }
        Parse a sequence of statements and return a BLOCK node.
        """
        statements = []
        
        # Parse statements until end of input
        while self._current_token() is not None:
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
        
        # Return a BLOCK containing all statements
        return block_stmt(statements)

    def statement(self):
        """
        statement -> declaration | expression_stmt
        
        Check if next token is a type keyword (int, float, char, etc.)
        to distinguish declaration from expression statement.
        """
        tok = self._current_token()
        if tok is None:
            return None
        
        # Check for type keyword
        if tok.type == 'KEYWORD' and tok.value in {'int', 'float', 'char', 'void', 'double', 'long', 'short', 'signed', 'unsigned'}:
            return self.declaration()
        else:
            return self.expression_stmt()

    def declaration(self):
        """
        declaration -> type_keyword ID [ = expression ] { , ID [ = expression ] } ;
        
        Examples:
        - int a;
        - int a = 10;
        - int a, b = 5, c;
        - float x = 3.14;
        """
        # Get the type keyword
        type_tok = self._expect('KEYWORD')
        type_name = type_tok.value
        
        # Parse declarators (one or more)
        declarators = []
        
        while True:
            # Expect an ID
            id_tok = self._expect('ID')
            id_name = id_tok.value
            
            # Check for initialization
            if self._match('='):
                self._advance()  # consume '='
                init_expr = self.assignment()  # parse the initialization expression
                declarators.append(('INIT', id_name, init_expr))
            else:
                declarators.append(('ID', id_name))
            
            # Check for more declarators (comma-separated)
            if self._match(','):
                self._advance()  # consume ','
                continue
            else:
                break
        
        # Expect semicolon at end of declaration
        self._expect(';')
        
        return declaration_stmt(type_name, declarators)

    def expression_stmt(self):
        """
        expression_stmt -> [ expression ] ;
        
        Allows empty statements (just ';') and expression statements.
        """
        # Check for empty statement
        if self._match(';'):
            self._advance()  # consume ';'
            return empty_stmt()
        
        # Parse expression
        expr = self.comma()
        
        # Expect semicolon
        self._expect(';')
        
        return expression_stmt(expr)


def ast_to_string(node, indent=0):
    """Pretty-print AST for debugging."""
    if isinstance(node, str):
        return ' ' * indent + repr(node)

    if not isinstance(node, tuple):
        return ' ' * indent + repr(node)

    if len(node) == 0:
        return ' ' * indent + "(...)"

    node_type = node[0]

    # Handle 2-element nodes (simple value nodes)
    if len(node) == 2:
        if node_type == 'ID':
            return ' ' * indent + f"ID({repr(node[1])})"
        elif node_type == 'NUMBER':
            return ' ' * indent + f"NUMBER({repr(node[1])})"
        elif node_type == 'EMPTY_STMT':
            return ' ' * indent + "EMPTY_STMT"
        elif node_type == 'EXPRESSION_STMT':
            result = ' ' * indent + "EXPRESSION_STMT(\n"
            result += ast_to_string(node[1], indent + 2) + "\n"
            result += ' ' * indent + ")"
            return result
        elif node_type == 'BLOCK':
            result = ' ' * indent + "BLOCK[\n"
            for stmt in node[1]:
                result += ast_to_string(stmt, indent + 2) + "\n"
            result += ' ' * indent + "]"
            return result
        else:
            return ' ' * indent + repr(node)

    # Handle BINARY nodes
    if node_type == 'BINARY':
        _, op, left, right = node
        result = ' ' * indent + f"BINARY({op!r}\n"
        result += ast_to_string(left, indent + 2) + "\n"
        result += ast_to_string(right, indent + 2) + "\n"
        result += ' ' * indent + ")"
        return result

    # Handle UNARY nodes
    elif node_type == 'UNARY':
        _, op, operand = node
        result = ' ' * indent + f"UNARY({op!r}\n"
        result += ast_to_string(operand, indent + 2) + "\n"
        result += ' ' * indent + ")"
        return result

    # Handle ASSIGN nodes
    elif node_type == 'ASSIGN':
        _, op, target, value = node
        result = ' ' * indent + f"ASSIGN({op!r}\n"
        result += ast_to_string(target, indent + 2) + "\n"
        result += ast_to_string(value, indent + 2) + "\n"
        result += ' ' * indent + ")"
        return result

    # Handle CONDITIONAL nodes
    elif node_type == 'CONDITIONAL':
        _, cond, true_br, false_br = node
        result = ' ' * indent + "CONDITIONAL(\n"
        result += ast_to_string(cond, indent + 2) + "\n"
        result += ast_to_string(true_br, indent + 2) + "\n"
        result += ast_to_string(false_br, indent + 2) + "\n"
        result += ' ' * indent + ")"
        return result

    # Handle SUBSCRIPT nodes
    elif node_type == 'SUBSCRIPT':
        _, array_ref, index = node
        result = ' ' * indent + f"SUBSCRIPT(\n"
        result += ast_to_string(array_ref, indent + 2) + "\n"
        result += ast_to_string(index, indent + 2) + "\n"
        result += ' ' * indent + ")"
        return result

    # Handle DECLARATION nodes
    elif node_type == 'DECLARATION':
        _, type_name, declarators = node
        result = ' ' * indent + f"DECLARATION({type_name!r}\n"
        for decl in declarators:
            if decl[0] == 'ID':
                result += ' ' * (indent + 2) + f"ID({repr(decl[1])})\n"
            elif decl[0] == 'INIT':
                result += ' ' * (indent + 2) + f"INIT({repr(decl[1])}\n"
                result += ast_to_string(decl[2], indent + 4) + "\n"
                result += ' ' * (indent + 2) + ")\n"
        result += ' ' * indent + ")"
        return result

    # Default fallback
    return ' ' * indent + repr(node)


if __name__ == '__main__':
    import sys

    # Sample statements and declarations to parse
    test_statements = [
        "int a;",
        "int a = 10;",
        "int a = 10, b;",
        "int x = 5, y = 20, z;",
        "float pi = 3.14;",
        "a++;",
        "a = b + 1;",
        ";",
        "int a = 10; a++;",
        "int x; int y = 10; x = y + 5;",
        "int a, b = 5; a = b * 2; a++;",
    ]

    print("=" * 70)
    print("C Statement Parser - AST Generation Test (with Declarations)")
    print("=" * 70)

    for stmt_str in test_statements:
        print(f"\nParsing: {stmt_str}")
        print("-" * 70)
        try:
            # Tokenize
            lexer = CLexer()
            lexer.text = stmt_str
            lexer._build_regex()
            tokens = list(lexer.tokenize())

            # Parse
            parser = CExpressionParser(tokens)
            ast = parser.parse()

            # Print AST
            print("AST:")
            print(ast_to_string(ast))
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
