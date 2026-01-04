"""
Full integration test: Lexer -> Parser -> Interpreter pipeline.
Reads expressions from input file, tokenizes, parses, and evaluates.
"""

import re
from c_lexer import CLexer
from c_parser import CExpressionParser
from c_interpreter import CInterpreter


def evaluate_expression_list(expressions, initial_vars=None):
    """
    Evaluate a list of expressions in sequence, with a shared symbol table.
    This allows expressions to reference variables modified by previous expressions.
    
    Returns list of (expr, result, error, final_vars)
    """
    if initial_vars is None:
        initial_vars = {}

    interpreter = CInterpreter(initial_vars.copy())
    results = []

    for expr in expressions:
        try:
            # Tokenize
            lexer = CLexer()
            lexer.text = expr
            lexer._build_regex()
            tokens = list(lexer.tokenize())

            # Parse
            parser = CExpressionParser(tokens)
            ast = parser.parse()

            # Evaluate
            result = interpreter.run(ast)

            results.append((expr, result, None, interpreter.variables.copy()))
        except Exception as e:
            results.append((expr, None, str(e), interpreter.variables.copy()))

    return results


def main():
    input_file = 'input_exp.txt'
    output_file = 'interpreter_output.txt'

    # Extract expressions from input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)

    # Extract expressions (split by semicolons)
    raw_exprs = []
    for line in content.split('\n'):
        line = line.strip()
        if line:
            if line.endswith(';'):
                line = line[:-1].strip()
            if line:
                raw_exprs.append(line)

    # Filter out the "int" declaration and evaluate in sequence
    # This tests variable persistence across expressions
    # Initialize with some variables for realistic testing
    initial_vars = {
        'a': 5,
        'b': 10,
        'c': 0,
        'x': 3,
        'y': 7,
        'z': 2,
        'arr': [1, 2, 3, 4, 5],
        'i': 0,
        'cond': 1,
        'expr1': 100,
        'expr2': 200,
        'flag': 0,
        'tern': 0,
        'val': 0,
    }
    all_results = []

    # First pass: evaluate all expressions with shared state
    print(f"Evaluating {len(raw_exprs)} expressions from {input_file}")
    print(f"Initial variables: {initial_vars}")
    print("-" * 70)

    interpreter = CInterpreter(initial_vars.copy())
    for expr in raw_exprs:
        try:
            if expr.startswith('int '):
                # Skip variable declarations
                continue

            lexer = CLexer()
            lexer.text = expr
            lexer._build_regex()
            tokens = list(lexer.tokenize())

            parser = CExpressionParser(tokens)
            ast = parser.parse()

            result = interpreter.run(ast)
            all_results.append({
                'expr': expr,
                'result': result,
                'error': None,
                'vars_after': interpreter.variables.copy()
            })
            print(f"✓ {expr} => {result}")
        except Exception as e:
            all_results.append({
                'expr': expr,
                'result': None,
                'error': str(e),
                'vars_after': interpreter.variables.copy()
            })
            print(f"✗ {expr} => Error: {e}")

    # Write results to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("C Expression Interpreter Results\n")
        f.write("=" * 70 + "\n\n")

        for i, result in enumerate(all_results, 1):
            f.write(f"Expression {i}: {result['expr']}\n")
            f.write("-" * 70 + "\n")

            if result['error']:
                f.write(f"ERROR: {result['error']}\n")
            else:
                f.write(f"Result: {result['result']}\n")

            f.write(f"Symbol table after: {result['vars_after']}\n")
            f.write("\n")

        f.write("=" * 70 + "\n")
        f.write(f"Total expressions: {len(all_results)}\n")
        f.write(f"Successful: {sum(1 for r in all_results if r['error'] is None)}\n")
        f.write(f"Failed: {sum(1 for r in all_results if r['error'] is not None)}\n")
        f.write(f"\nFinal symbol table: {interpreter.variables}\n")

    print("\n" + "=" * 70)
    print(f"Final symbol table: {interpreter.variables}")
    print(f"Results written to {output_file}")


if __name__ == '__main__':
    main()
