#!/usr/bin/env python3
"""
C 语言解释器 - 交互式 GUI 界面
支持输入文件选择和6个输出文件的查看
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import subprocess
from pathlib import Path

class InterpreterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("C 语言解释器 - 交互界面")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        # 当前工作目录
        self.work_dir = Path.cwd()
        self.input_file = self.work_dir / "input.txt"
        
        # 6个输出文件
        self.output_files = [
            ("词法分析", "lexical_output.txt"),
            ("语法分析", "syntax_output.txt"),
            ("执行过程", "execution_detail.txt"),
            ("变量状态", "variables_final_state.txt"),
            ("执行总结", "complete_summary.txt"),
            ("调用追踪", "function_call_trace.txt"),
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        
        # ===== 顶部工具栏 =====
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 输入文件选择
        ttk.Label(toolbar_frame, text="输入文件:").pack(side=tk.LEFT, padx=5)
        self.input_label = ttk.Label(toolbar_frame, text=str(self.input_file), 
                                      foreground="blue", relief=tk.SUNKEN)
        self.input_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(toolbar_frame, text="📂 选择文件", 
                  command=self.select_input_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar_frame, text="🔧 执行解释器", 
                  command=self.run_interpreter).pack(side=tk.LEFT, padx=5)
        
        # ===== 主界面分为两部分 =====
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：输入代码区
        left_frame = ttk.LabelFrame(main_paned, text="📝 输入代码 (input.txt)", height=350)
        main_paned.add(left_frame, weight=1)
        
        # 输入代码文本框
        input_scrollbar = ttk.Scrollbar(left_frame)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.input_text = tk.Text(left_frame, height=15, width=40, 
                                  yscrollcommand=input_scrollbar.set,
                                  font=("Consolas", 10))
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        input_scrollbar.config(command=self.input_text.yview)
        
        # 加载初始输入文件
        self.load_input_file()
        
        # 右侧：输出结果区
        right_frame = ttk.LabelFrame(main_paned, text="📊 输出结果", height=350)
        main_paned.add(right_frame, weight=2)
        
        # 输出文件选择标签页
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建6个标签页
        self.output_texts = {}
        for label, filename in self.output_files:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=label)
            
            # 文本框
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(frame, height=25, width=80,
                                 yscrollcommand=scrollbar.set,
                                 font=("Consolas", 9), wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            scrollbar.config(command=text_widget.yview)
            
            self.output_texts[filename] = text_widget
        
        # ===== 底部状态栏 =====
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="✓ 就绪", 
                                      relief=tk.SUNKEN, foreground="green")
        self.status_label.pack(fill=tk.X)
        
    def select_input_file(self):
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入文件",
            initialdir=self.work_dir,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.input_file = Path(file_path)
            self.input_label.config(text=str(self.input_file))
            self.load_input_file()
            self.update_status("✓ 已加载: " + self.input_file.name)
    
    def load_input_file(self):
        """加载输入文件内容到文本框"""
        try:
            if self.input_file.exists():
                with open(self.input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, content)
            else:
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, "# 文件不存在")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {e}")
    
    def run_interpreter(self):
        """执行解释器"""
        try:
            # 保存当前输入
            self.save_input_file()
            
            self.update_status("⏳ 正在执行解释器...")
            self.root.update()
            
            # 执行生成脚本
            result = subprocess.run(
                [sys.executable, "generate_complete_output.py"],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.update_status("✓ 执行成功")
                self.load_output_files()
                messagebox.showinfo("成功", "解释器执行成功！所有输出文件已生成。")
            else:
                self.update_status("❌ 执行失败")
                error_msg = result.stderr if result.stderr else result.stdout
                messagebox.showerror("执行错误", f"解释器执行失败:\n{error_msg}")
        
        except subprocess.TimeoutExpired:
            self.update_status("❌ 超时")
            messagebox.showerror("错误", "执行超时")
        except Exception as e:
            self.update_status("❌ 错误")
            messagebox.showerror("错误", f"执行失败: {e}")
    
    def save_input_file(self):
        """保存输入文件内容"""
        try:
            content = self.input_text.get(1.0, tk.END)
            with open(self.input_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def load_output_files(self):
        """加载所有输出文件内容到标签页"""
        for filename, text_widget in self.output_texts.items():
            file_path = self.work_dir / filename
            try:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(1.0, content)
                else:
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(1.0, f"# 文件不存在: {filename}")
            except Exception as e:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(1.0, f"# 读取文件失败: {e}")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update()


def main():
    root = tk.Tk()
    app = InterpreterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
