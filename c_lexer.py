import re
from collections import namedtuple
from typing import Generator

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])


class CLexer:
    """A simple C-expression lexer producing Token(type, value, line, column).

    Usage:
        lexer = CLexer()
        lexer.load_file('input_exp.txt')
        for tok in lexer.tokenize():
            print(tok)
    """

    def __init__(self):
        self.text = ''
        self._regex = None

    def load_file(self, filepath: str) -> None:
        """Load source text from a file into the lexer."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.text = f.read()
        self._build_regex()

    def _build_regex(self) -> None:
        # Keywords: int, float, char, void, etc.
        keywords = {'int', 'float', 'char', 'void', 'double', 'long', 'short', 'signed', 'unsigned'}
        
        # Operators and punctuators: list with multi-char tokens first for greedy matching
        ops = [
            '<<=', '>>=', '->', '++', '--', '<<', '>>', '<=', '>=', '==', '!=',
            '&&', '||', '+=', '-=', '*=', '/=', '%=', '&=', '^=', '|=',
            '+', '-', '*', '/', '%', '<', '>', '!', '~', '|', '^', '&', '=',
            '?', ':', ',', '[', ']', '(', ')', ';', '{', '}'
        ]
        # Sort by length descending to ensure greedy matching (longer first)
        ops_sorted = sorted(ops, key=lambda s: -len(s))
        # Escape operators for regex
        import re as _re
        op_pattern = '|'.join(_re.escape(op) for op in ops_sorted)

        token_specification = [
            ('WHITESPACE', r'\s+'),
            ('COMMENT', r'//[^\n]*|/\*.*?\*/'),
            ('NUMBER', r'0x[0-9A-Fa-f]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?'),
            ('KEYWORD', r'\b(' + '|'.join(keywords) + r')\b'),
            ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
            ('OP', op_pattern),
            ('MISMATCH', r'.'),
        ]

        parts = []
        for name, pattern in token_specification:
            parts.append('(?P<%s>%s)' % (name, pattern))

        self._regex = re.compile('|'.join(parts), re.DOTALL)

    def tokenize(self) -> Generator[Token, None, None]:
        """Generate tokens from loaded text.

        Raises SyntaxError with line/column info on illegal characters.
        """
        if self._regex is None:
            self._build_regex()

        line = 1
        col = 1
        last_end = 0

        for mo in self._regex.finditer(self.text):
            kind = mo.lastgroup
            value = mo.group()

            if kind == 'WHITESPACE' or kind == 'COMMENT':
                # Update line and column counters
                newlines = value.count('\n')
                if newlines:
                    line += newlines
                    col = len(value.rsplit('\n', 1)[-1]) + 1
                else:
                    col += len(value)
                last_end = mo.end()
                continue

            if kind == 'MISMATCH':
                # Compute column at error position
                # Use the substring from the last newline to the match start
                start_pos = mo.start()
                last_nl = self.text.rfind('\n', 0, start_pos)
                err_line = self.text.count('\n', 0, start_pos) + 1
                if last_nl == -1:
                    err_col = start_pos + 1
                else:
                    err_col = start_pos - last_nl
                raise SyntaxError(f"Illegal character {value!r} at line {err_line}, column {err_col}")

            # For operator tokens, set type to the exact operator string for clarity
            if kind == 'OP':
                token_type = value
            else:
                token_type = kind

            tok = Token(token_type, value, line, col)
            yield tok

            # advance column by token length (no newlines expected in these tokens)
            newlines = value.count('\n')
            if newlines:
                line += newlines
                col = len(value.rsplit('\n', 1)[-1]) + 1
            else:
                col += len(value)


if __name__ == '__main__':
    import sys
    path = 'input_exp.txt'
    if len(sys.argv) > 1:
        path = sys.argv[1]

    lexer = CLexer()
    try:
        lexer.load_file(path)
    except FileNotFoundError:
        print(f'File not found: {path}')
        sys.exit(1)

    try:
        tokens = list(lexer.tokenize())
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(str(tokens))
        print(f'Successfully wrote {len(tokens)} tokens to output.txt')
    except SyntaxError as e:
        print('Lexing error:', e)
        sys.exit(2)
