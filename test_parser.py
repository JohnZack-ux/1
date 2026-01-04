"""
Integrated test: Read expressions from input file, tokenize with CLexer, 
parse with CExpressionParser, and write results to output file.
"""

import re
from c_lexer import CLexer
from c_parser import CExpressionParser, ast_to_string


def extract_expressions_from_file(filepath: str):
    """
    Extract individual C expressions from a file.
    Assumes each line is either an expression or a comment.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove block comments and line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)
    
    # Split by semicolons and filter out empty lines
    expressions = []
    for line in content.split('\n'):
        line = line.strip()
        if line:
            # Remove trailing semicolon if present
            if line.endswith(';'):
                line = line[:-1].strip()
            if line:
                expressions.append(line)
    
    return expressions


def parse_expression(expr_str: str):
    """
    Parse a single expression string and return (tokens, ast, error).
    """
    try:
        lexer = CLexer()
        lexer.text = expr_str
        lexer._build_regex()
        tokens = list(lexer.tokenize())
        
        parser = CExpressionParser(tokens)
        ast = parser.parse()
        
        return (tokens, ast, None)
    except Exception as e:
        return (None, None, str(e))


def main():
    input_file = 'input_exp.txt'
    output_file = 'parse_output.txt'
    
    # Extract expressions
    expressions = extract_expressions_from_file(input_file)
    
    # Parse each expression
    results = []
    for expr in expressions:
        tokens, ast, error = parse_expression(expr)
        results.append({
            'expr': expr,
            'tokens': tokens,
            'ast': ast,
            'error': error
        })
    
    # Write results to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("C Expression Parsing Results\n")
        f.write("=" * 70 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"Expression {i}: {result['expr']}\n")
            f.write("-" * 70 + "\n")
            
            if result['error']:
                f.write(f"ERROR: {result['error']}\n")
            else:
                f.write(f"Tokens ({len(result['tokens'])} total):\n")
                for tok in result['tokens']:
                    f.write(f"  {tok}\n")
                f.write("\nAST:\n")
                ast_str = ast_to_string(result['ast'], indent=2)
                f.write(ast_str + "\n")
            
            f.write("\n")
        
        f.write("=" * 70 + "\n")
        f.write(f"Total expressions: {len(results)}\n")
        f.write(f"Successful: {sum(1 for r in results if r['error'] is None)}\n")
        f.write(f"Failed: {sum(1 for r in results if r['error'] is not None)}\n")
    
    # Print summary to console
    print(f"Parsed {len(expressions)} expressions from {input_file}")
    print(f"Wrote detailed results to {output_file}")
    print(f"Successful: {sum(1 for r in results if r['error'] is None)}")
    print(f"Failed: {sum(1 for r in results if r['error'] is not None)}")


if __name__ == '__main__':
    main()
