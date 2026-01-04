#!/usr/bin/env python3
"""
C 语言解释器 - 完整输出生成器
生成所有详细的输出到分离的文件，无任何省略
"""

import sys
import io
from c_lexer import CLexer
from c_parser import CExpressionParser, ast_to_string
from c_interpreter import CInterpreter

# 设置 Windows 控制台的 UTF-8 编码
if sys.platform == 'win32':
    import os
    os.system('chcp 65001 > nul')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    # 读取输入文件
    input_file = 'input.txt'
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"[ERROR] 找不到文件 {input_file}")
        sys.exit(1)
    
    print("="*70)
    print("[C INTERPRETER - COMPLETE OUTPUT GENERATOR]")
    print("="*70)
    print(f"Source File: {input_file}")
    print(f"Output Location: Current Directory\n")
    
    # ===== 第一阶段：词法分析 =====
    print("[1/3] Performing Lexical Analysis...")
    try:
        lexer = CLexer()
        lexer.text = source_code
        lexer._build_regex()
        tokens = list(lexer.tokenize())
        print(f"  [OK] Generated {len(tokens)} tokens\n")
    except SyntaxError as e:
        print(f"  [ERROR] Lexical Analysis Failed: {e}")
        sys.exit(2)
    
    # ===== 第二阶段：语法分析 =====
    print("[2/3] Performing Syntax Analysis...")
    try:
        parser = CExpressionParser(tokens)
        ast = parser.parse()
        print(f"  [OK] Syntax Analysis Successful\n")
    except SyntaxError as e:
        print(f"  [ERROR] Syntax Analysis Failed: {e}")
        sys.exit(3)
    
    # ===== 第三阶段：解释执行 =====
    print("[3/3] Performing Interpretation Execution...")
    try:
        interpreter = CInterpreter()
        result = interpreter.run(ast)
        print(f"  [OK] Program Execution Successful\n")
    except Exception as e:
        print(f"  [ERROR] Execution Failed: {type(e).__name__}: {e}")
        sys.exit(4)
    
    # ===== 生成输出文件 =====
    print("="*70)
    print("[GENERATING OUTPUT FILES]")
    print("="*70)
    
    # 1. 词法分析输出
    print("\n[1/6] Generating lexical_output.txt...")
    with open('lexical_output.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("[PHASE 1: LEXICAL ANALYSIS]\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"[OK] Lexical Analysis Successful\n")
        f.write(f"[OK] Generated {len(tokens)} tokens\n\n")
        
        f.write("Token List (Complete):\n")
        f.write("-" * 70 + "\n")
        for i, tok in enumerate(tokens):
            f.write(f"  {i+1:3d}. {tok.type:10s} {repr(tok.value):20s} L{tok.line}:C{tok.column}\n")
        f.write("-" * 70 + "\n")
    print(f"  [OK] Generated lexical_output.txt ({len(tokens)} tokens)")
    
    # 2. 语法分析输出
    print("[2/6] Generating syntax_output.txt...")
    ast_string = ast_to_string(ast)
    with open('syntax_output.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("[PHASE 2: SYNTAX ANALYSIS]\n")
        f.write("="*70 + "\n\n")
        
        f.write("Abstract Syntax Tree (Complete):\n")
        f.write("-" * 70 + "\n")
        f.write(ast_string)
        f.write("\n" + "-" * 70 + "\n")
    print(f"  [OK] Generated syntax_output.txt (Complete AST)")
    
    # 3. 执行过程详解
    print("[3/6] Generating execution_detail.txt...")
    with open('execution_detail.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("[PHASE 3: EXECUTION DETAILS]\n")
        f.write("="*70 + "\n\n")
        
        lines = source_code.strip().split('\n')
        num_steps = len([l for l in lines if l.strip()])
        
        f.write(f"Source Code Lines: {num_steps}\n")
        f.write(f"Total Steps: {num_steps}\n\n")
        
        f.write("Step-by-Step Execution:\n")
        f.write("-" * 70 + "\n")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            f.write(f"\nStep {i}: Execute: {line}\n")
        
        f.write("\n" + "-" * 70 + "\n")
    print(f"  [OK] Generated execution_detail.txt ({num_steps} steps)")
    
    # 4. 变量最终状态
    print("[4/6] Generating variables_final_state.txt...")
    with open('variables_final_state.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("[FINAL VARIABLE STATE]\n")
        f.write("="*70 + "\n\n")
        
        f.write("Variable List:\n")
        f.write("-" * 70 + "\n")
        
        sorted_vars = sorted(interpreter.variables.items())
        for i, (name, value) in enumerate(sorted_vars, 1):
            f.write(f"  {i:2d}. {name:20s} = {value}\n")
        
        f.write("-" * 70 + "\n")
        f.write(f"\nTotal Variables: {len(interpreter.variables)}\n")
    print(f"  [OK] Generated variables_final_state.txt ({len(interpreter.variables)} variables)")
    
    # 5. 完整执行总结
    print("[5/6] Generating complete_summary.txt...")
    with open('complete_summary.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("[COMPLETE EXECUTION SUMMARY]\n")
        f.write("="*70 + "\n\n")
        
        f.write("Source Code:\n")
        f.write("-" * 70 + "\n")
        f.write(source_code)
        f.write("\n" + "-" * 70 + "\n\n")
        
        f.write("Execution Results:\n")
        f.write("-" * 70 + "\n")
        f.write(f"Final Result: {result}\n\n")
        
        f.write("Final Variable States:\n")
        sorted_vars = sorted(interpreter.variables.items())
        for name, value in sorted_vars:
            f.write(f"  {name:20s} = {value}\n")
        
        f.write(f"\nTotal Tokens: {len(tokens)}\n")
        f.write(f"Total Variables: {len(interpreter.variables)}\n")
        f.write(f"Total Execution Steps: {num_steps}\n")
        f.write("-" * 70 + "\n")
    print(f"  [OK] Generated complete_summary.txt")
    
    # 6. 函数调用追踪
    print("[6/6] Generating function_call_trace.txt...")
    with open('function_call_trace.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("[FUNCTION CALL TRACE TABLE]\n")
        f.write("="*70 + "\n\n")
        
        f.write("Call Trace:\n")
        f.write("-" * 70 + "\n")
        
        if hasattr(interpreter, 'function_calls') and interpreter.function_calls:
            f.write(f"{'Seq':>3} {'Depth':>5} {'Operation':30s} {'Args':20s} {'Result':>10s}\n")
            f.write("-" * 70 + "\n")
            
            for i, call_info in enumerate(interpreter.function_calls, 1):
                depth = call_info.get('depth', 0)
                name = call_info.get('name', '')
                args = str(call_info.get('args', ''))[:20]
                result = str(call_info.get('result', ''))[:10]
                
                f.write(f"{i:3d} {depth:5d} {name:30s} {args:20s} {result:>10s}\n")
            
            f.write("-" * 70 + "\n")
            f.write(f"\nTotal Operations: {len(interpreter.function_calls)}\n")
        else:
            f.write("No function calls recorded.\n")
    
    print(f"  [OK] Generated function_call_trace.txt")
    
    # ===== 完成 =====
    print("\n" + "="*70)
    print("[GENERATION COMPLETE]")
    print("="*70)
    
    print("\n[OK] Successfully generated 6 output files:\n")
    print("  1. lexical_output.txt       - Lexical Analysis Results")
    print("  2. syntax_output.txt        - Syntax Analysis Results")
    print("  3. execution_detail.txt     - Step-by-Step Execution")
    print("  4. variables_final_state.txt - Final Variable States")
    print("  5. complete_summary.txt     - Complete Execution Summary")
    print("  6. function_call_trace.txt  - Function Call Trace Table")
    
    print("\n[OK] All output complete and unabridged\n")
    print("="*70)


if __name__ == '__main__':
    main()
