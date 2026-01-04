#!/usr/bin/env python3
"""
C 语言解释器 - GUI 界面运行脚本
直接运行此脚本即可启动交互式界面
"""

import subprocess
import sys
import os

def run_gui():
    """启动 GUI 界面"""
    print("="*70)
    print("【C 语言解释器 - 交互式 GUI 界面】")
    print("="*70)
    print("\n正在启动交互界面...")
    print("请在弹出的窗口中操作:\n")
    print("1. 【选择文件】- 选择 input.txt（或其他 C 代码文件）")
    print("2. 【执行解释器】- 运行解释器生成所有输出文件")
    print("3. 【切换标签页】- 查看 6 个输出文件的内容:")
    print("   - 词法分析: 令牌列表")
    print("   - 语法分析: 抽象语法树")
    print("   - 执行过程: 逐行执行详解")
    print("   - 变量状态: 所有变量的最终值")
    print("   - 执行总结: 完整的执行报告")
    print("   - 调用追踪: 函数和操作的追踪表")
    print("\n" + "="*70 + "\n")
    
    try:
        # 运行 GUI 程序
        result = subprocess.run([sys.executable, "interpreter_gui.py"], cwd=os.getcwd())
        
        if result.returncode == 0:
            print("\n✓ GUI 程序正常关闭")
        else:
            print(f"\n⚠ GUI 程序异常退出 (代码: {result.returncode})")
    
    except FileNotFoundError:
        print("❌ 错误: 找不到 interpreter_gui.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run_gui()
