from c_lexer import CLexer
from c_parser import CExpressionParser
from c_interpreter import CInterpreter

def run_test(case_name, expr_str, init_vars):
    print(f"【测试用例: {case_name}】")
    print(f"Expression: {expr_str}")
    print(f"Initial variables: {init_vars}")
    print("-" * 50)

    try:
        # 1. 词法分析
        lexer = CLexer()
        lexer.text = expr_str
        lexer._build_regex()
        tokens = list(lexer.tokenize())

        # 2. 语法分析
        parser = CExpressionParser(tokens)
        ast = parser.parse()

        # 3. 解释执行
        interpreter = CInterpreter(init_vars.copy())
        result = interpreter.run(ast)

        print(f"Result: {result}")
        print("变量最终状态:")
        # 按变量名排序并逐行打印
        for name in sorted(interpreter.variables.keys()):
            value = interpreter.variables[name]
            print(f"{name}={value}")

    except Exception as e:
        print(f"Error: {e}")
    
    print("=" * 50 + "\n")

if __name__ == '__main__':
    print("=" * 50)
    print("C COMPILER COMPREHENSIVE TEST SUITE")
    print("=" * 50 + "\n")

    # --- 测试 1: 位运算与移位 (Bitwise & Shift) ---
    # 逻辑：(1 << 2) | (7 & 3) 
    #       (4)      | (3)      = 7
    expr1 = "res = (a << 2) | (b & c)"
    vars1 = {'a': 1, 'b': 7, 'c': 3}
    run_test("位运算综合", expr1, vars1)

    # --- 测试 2: 逻辑短路求值 (Logical Short-circuit) ---
    # 逻辑：a(5) > 10 为假。因为是 &&，右边 (b++) 不应该执行。
    # 预期：res=0, b 仍然是 10 (证明副作用未发生)
    expr2 = "res = (a > 10) && (b++ > 0)"
    vars2 = {'a': 5, 'b': 10}
    run_test("逻辑短路验证", expr2, vars2)

    # --- 测试 3: 前置/后置自增 (Pre/Post Increment) ---
    # 逻辑：x++ (取5, x变6) + ++y (y变6, 取6) = 11
    expr3 = "res = x++ + ++y"
    vars3 = {'x': 5, 'y': 5}
    run_test("自增自减差异", expr3, vars3)

    # --- 测试 4: 数组下标与赋值 (Array & Assignment) ---
    # 逻辑：arr[1] 是 20。 20 + 50 = 70。
    expr4 = "val = arr[idx] + 50"
    vars4 = {'arr': [10, 20, 30], 'idx': 1}
    run_test("数组访问", expr4, vars4)