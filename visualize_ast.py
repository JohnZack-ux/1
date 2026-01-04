"""
AST 可视化工具 - 生成树形和图形表示
AST Visualization Tool - Generate tree and graphical representations
"""

from c_lexer import CLexer
from c_parser import CExpressionParser


def ast_to_tree_visual(node, prefix="", is_last=True):
    """
    Convert AST tuple to tree visual using ASCII art.
    
    Outputs like:
    ASSIGN
    ├─ Operator: =
    ├─ Left:
    │  └─ ID('res')
    └─ Right:
       └─ BINARY...
    """
    if not isinstance(node, tuple):
        return f"{prefix}{'└── ' if is_last else '├── '}{repr(node)}\n"

    lines = []
    node_type = node[0]

    # Root
    lines.append(f"{prefix}{node_type}\n")

    # Handle different node types
    if node_type == 'ASSIGN':
        _, op, target, value = node
        prefix_child = prefix + ("    " if is_last else "│   ")
        lines.append(f"{prefix}├── Operator: {op}\n")
        lines.append(f"{prefix}├── Target:\n")
        lines.append(ast_to_tree_visual(target, prefix_child, False))
        lines.append(f"{prefix}└── Value:\n")
        lines.append(ast_to_tree_visual(value, prefix_child, True))

    elif node_type == 'BINARY':
        _, op, left, right = node
        prefix_child = prefix + ("    " if is_last else "│   ")
        lines.append(f"{prefix}├── Operator: {op}\n")
        lines.append(f"{prefix}├── Left:\n")
        lines.append(ast_to_tree_visual(left, prefix_child, False))
        lines.append(f"{prefix}└── Right:\n")
        lines.append(ast_to_tree_visual(right, prefix_child, True))

    elif node_type == 'UNARY':
        _, op, operand = node
        prefix_child = prefix + ("    " if is_last else "│   ")
        lines.append(f"{prefix}├── Operator: {op}\n")
        lines.append(f"{prefix}└── Operand:\n")
        lines.append(ast_to_tree_visual(operand, prefix_child, True))

    elif node_type == 'CONDITIONAL':
        _, cond, true_br, false_br = node
        prefix_child = prefix + ("    " if is_last else "│   ")
        lines.append(f"{prefix}├── Condition:\n")
        lines.append(ast_to_tree_visual(cond, prefix_child, False))
        lines.append(f"{prefix}├── True Branch:\n")
        lines.append(ast_to_tree_visual(true_br, prefix_child, False))
        lines.append(f"{prefix}└── False Branch:\n")
        lines.append(ast_to_tree_visual(false_br, prefix_child, True))

    elif node_type == 'SUBSCRIPT':
        _, array_ref, index = node
        prefix_child = prefix + ("    " if is_last else "│   ")
        lines.append(f"{prefix}├── Array:\n")
        lines.append(ast_to_tree_visual(array_ref, prefix_child, False))
        lines.append(f"{prefix}└── Index:\n")
        lines.append(ast_to_tree_visual(index, prefix_child, True))

    elif node_type in ('ID', 'NUMBER'):
        _, value = node
        lines.append(f"{prefix}└── Value: {value}\n")

    return "".join(lines)


def ast_to_mermaid(node, node_id=[0]):
    """Generate Mermaid diagram format for AST."""
    if not isinstance(node, tuple):
        node_id[0] += 1
        return f"  N{node_id[0]}[\"{repr(node)}\"]\n", f"N{node_id[0]}"

    node_type = node[0]
    current_id = node_id[0]
    node_id[0] += 1

    lines = []
    children = []

    if node_type == 'ASSIGN':
        _, op, target, value = node
        lines.append(f"  N{current_id}[\"ASSIGN({op})\"];\n")
        target_lines, target_id = ast_to_mermaid(target, node_id)
        value_lines, value_id = ast_to_mermaid(value, node_id)
        lines.append(target_lines)
        lines.append(value_lines)
        lines.append(f"  N{current_id} --> N{target_id};\n")
        lines.append(f"  N{current_id} --> N{value_id};\n")

    elif node_type == 'BINARY':
        _, op, left, right = node
        lines.append(f"  N{current_id}[\"BINARY({op})\"];\n")
        left_lines, left_id = ast_to_mermaid(left, node_id)
        right_lines, right_id = ast_to_mermaid(right, node_id)
        lines.append(left_lines)
        lines.append(right_lines)
        lines.append(f"  N{current_id} --> N{left_id};\n")
        lines.append(f"  N{current_id} --> N{right_id};\n")

    elif node_type == 'UNARY':
        _, op, operand = node
        lines.append(f"  N{current_id}[\"UNARY({op})\"];\n")
        operand_lines, operand_id = ast_to_mermaid(operand, node_id)
        lines.append(operand_lines)
        lines.append(f"  N{current_id} --> N{operand_id};\n")

    elif node_type == 'CONDITIONAL':
        _, cond, true_br, false_br = node
        lines.append(f"  N{current_id}[\"CONDITIONAL(?:)\"];\n")
        cond_lines, cond_id = ast_to_mermaid(cond, node_id)
        true_lines, true_id = ast_to_mermaid(true_br, node_id)
        false_lines, false_id = ast_to_mermaid(false_br, node_id)
        lines.append(cond_lines)
        lines.append(true_lines)
        lines.append(false_lines)
        lines.append(f"  N{current_id} --> |cond| N{cond_id};\n")
        lines.append(f"  N{current_id} --> |true| N{true_id};\n")
        lines.append(f"  N{current_id} --> |false| N{false_id};\n")

    elif node_type in ('ID', 'NUMBER'):
        _, value = node
        lines.append(f"  N{current_id}[\"{node_type}({value})\"];\n")

    return "".join(lines), f"N{current_id}"


def generate_ast_report(expr_str):
    """Generate complete AST visualization report."""
    # Parse
    lexer = CLexer()
    lexer.text = expr_str
    lexer._build_regex()
    tokens = list(lexer.tokenize())

    parser = CExpressionParser(tokens)
    ast = parser.parse()

    # Generate report
    report = []
    report.append("=" * 80)
    report.append(f"AST VISUALIZATION: {expr_str}")
    report.append("=" * 80)

    # Tree view
    report.append("\n【Tree Structure】")
    report.append("-" * 80)
    report.append(ast_to_tree_visual(ast))

    # Mermaid diagram
    report.append("\n【Mermaid Diagram Format】")
    report.append("-" * 80)
    report.append("graph TD\n")
    mermaid_lines, _ = ast_to_mermaid(ast)
    report.append(mermaid_lines)

    # Raw tuple
    report.append("\n【Raw Tuple Representation】")
    report.append("-" * 80)
    report.append(str(ast) + "\n")

    return "\n".join(report)


def main():
    test_cases = [
        "res = a + b * 3",
        "a > 5 ? b += 5, b : c",
        "!a && b || c",
        "x = y++",
    ]

    print("AST VISUALIZATION REPORT")
    print("=" * 80)

    for expr in test_cases:
        try:
            report = generate_ast_report(expr)
            print(report)
            print("\n" * 2)
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == '__main__':
    main()
