"""
动态解析追踪生成器 - 展示递归下降过程
Generates detailed parsing trace with function call stack and token consumption.
"""

from c_lexer import CLexer
from c_parser import CExpressionParser
import sys

class TracingParser(CExpressionParser):
    """Extended parser with detailed tracing."""

    def __init__(self, tokens):
        super().__init__(tokens)
        self.trace_log = []
        self.depth = 0

    def _log_trace(self, action, details=""):
        """Log a trace entry."""
        current_tok = self._current_token()
        tok_str = f"{current_tok.type}({current_tok.value})" if current_tok else "EOF"
        
        indent = "  " * self.depth
        entry = {
            'step': len(self.trace_log) + 1,
            'depth': self.depth,
            'function': sys._getframe(2).f_code.co_name,
            'token': tok_str,
            'action': action,
            'details': details,
            'display': f"{indent}[{self.depth}] {sys._getframe(2).f_code.co_name}(): {action} | Token: {tok_str} {details}"
        }
        self.trace_log.append(entry)

    def comma(self):
        self._log_trace("ENTER comma()")
        self.depth += 1
        result = super().comma()
        self.depth -= 1
        self._log_trace("RETURN comma()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def assignment(self):
        self._log_trace("ENTER assignment()")
        self.depth += 1
        result = super().assignment()
        self.depth -= 1
        self._log_trace("RETURN assignment()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def conditional(self):
        self._log_trace("ENTER conditional()")
        self.depth += 1
        result = super().conditional()
        self.depth -= 1
        self._log_trace("RETURN conditional()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def logical_or(self):
        self._log_trace("ENTER logical_or()")
        self.depth += 1
        result = super().logical_or()
        self.depth -= 1
        self._log_trace("RETURN logical_or()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def logical_and(self):
        self._log_trace("ENTER logical_and()")
        self.depth += 1
        result = super().logical_and()
        self.depth -= 1
        self._log_trace("RETURN logical_and()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def additive(self):
        self._log_trace("ENTER additive()")
        self.depth += 1
        result = super().additive()
        self.depth -= 1
        self._log_trace("RETURN additive()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def multiplicative(self):
        self._log_trace("ENTER multiplicative()")
        self.depth += 1
        result = super().multiplicative()
        self.depth -= 1
        self._log_trace("RETURN multiplicative()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def unary(self):
        self._log_trace("ENTER unary()")
        self.depth += 1
        result = super().unary()
        self.depth -= 1
        self._log_trace("RETURN unary()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def postfix(self):
        self._log_trace("ENTER postfix()")
        self.depth += 1
        result = super().postfix()
        self.depth -= 1
        self._log_trace("RETURN postfix()", f"→ {result[0] if isinstance(result, tuple) else result}")
        return result

    def primary(self):
        self._log_trace("ENTER primary()")
        self.depth += 1
        result = super().primary()
        self.depth -= 1
        self._log_trace("RETURN primary()", f"→ {result}")
        return result

    def _advance(self):
        tok = super()._advance()
        if tok:
            self._log_trace("CONSUME", f"Token: {tok.type}({tok.value})")
        return tok

    def _match(self, *types):
        result = super()._match(*types)
        if result:
            self._log_trace("MATCH", f"Operator: {self._current_token().type}")
        return result


def generate_trace(expr_str):
    """Generate parsing trace for an expression."""
    # Tokenize
    lexer = CLexer()
    lexer.text = expr_str
    lexer._build_regex()
    tokens = list(lexer.tokenize())

    # Parse with tracing
    parser = TracingParser(tokens)
    ast = parser.parse()

    return tokens, ast, parser.trace_log


def print_trace_report(expr_str, tokens, ast, trace_log):
    """Print formatted trace report."""
    print("=" * 80)
    print(f"PARSING TRACE: {expr_str}")
    print("=" * 80)
    
    # Token stream
    print("\n【Token Stream】")
    print("-" * 80)
    for i, tok in enumerate(tokens):
        print(f"  {i:2d}. {tok.type:15s} | {tok.value:10s} | Line {tok.line}, Col {tok.column}")
    
    # Execution trace
    print("\n【Execution Trace (Function Call Stack)】")
    print("-" * 80)
    for entry in trace_log:
        print(entry['display'])
    
    # Final AST
    print("\n【Final AST】")
    print("-" * 80)
    print(f"{ast}\n")


def main():
    test_cases = [
        "res = a + b * 3",
        "a > 5 ? b += 5, b : c",
        "a + b",
        "x * 2 + 3",
    ]

    for expr in test_cases:
        try:
            tokens, ast, trace_log = generate_trace(expr)
            print_trace_report(expr, tokens, ast, trace_log)
            print("\n" * 2)
        except Exception as e:
            print(f"Error parsing {expr}: {e}\n")


if __name__ == '__main__':
    main()
