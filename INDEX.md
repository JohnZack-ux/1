# 📖 C 语言表达式编译器 - 完整文档索引

## 📁 项目文件清单

```
c:\Users\qwert\Desktop\新建文件夹\
├── 【核心实现模块】
│   ├── c_lexer.py              词法分析器 (139 行)
│   ├── c_parser.py             语法分析器 (495 行)
│   ├── c_interpreter.py        解释执行器 (352 行)
│   │
│   ├── 【测试与集成】
│   ├── test_parser.py          语法分析测试
│   ├── test_interpreter.py     解释执行测试
│   └── generate_trace.py       追踪过程生成器
│
├── 【输入/输出数据】
│   ├── input_exp.txt           输入表达式
│   ├── output.txt              词法分析结果 (41 个 Token)
│   ├── parse_output.txt        语法分析结果 (AST)
│   ├── interpreter_output.txt  解释执行结果
│   │
│   ├── trace_output.txt        追踪过程输出
│   └── ast_visualization.txt   AST 可视化输出
│
├── 【理论文档】
│   ├── THEORY_ANALYSIS.md              (完整理论分析)
│   │   ├─ Part 1: 追踪过程详细表格
│   │   ├─ Part 2: AST 树形结构与分析
│   │   └─ Part 3: EBNF 形式化文法 (LaTeX)
│   │
│   ├── COMPREHENSIVE_DOCUMENT.md       (综合文档，推荐先读)
│   │   ├─ 目录导航
│   │   ├─ 核心概念总结
│   │   ├─ 追踪过程简化版
│   │   ├─ AST 结构分析
│   │   ├─ 优先级体现
│   │   └─ 实现细节
│   │
│   └── README_EXECUTION_FLOW.md        (执行流程说明)
│       └─ 三步执行管道说明
└
```

---

## 🚀 快速开始

### 步骤 1: 词法分析
```bash
python c_lexer.py
# 输出：output.txt (Token 列表)
```

### 步骤 2: 语法分析
```bash
python test_parser.py
# 输出：parse_output.txt (AST)
```

### 步骤 3: 解释执行
```bash
python test_interpreter.py
# 输出：interpreter_output.txt (计算结果)
```

### 可视化（可选）
```bash
python visualize_ast.py > ast_visualization.txt
python generate_trace.py > trace_output.txt
```

---

## 📚 文档阅读建议

### 对于学生（编译原理课程）

**推荐阅读顺序**：
1. ✅ [COMPREHENSIVE_DOCUMENT.md](COMPREHENSIVE_DOCUMENT.md) 
   - 快速了解全景
   - 15 分钟快速导入

2. ✅ [trace_output.txt](trace_output.txt)
   - 看实际追踪过程
   - 理解函数调用栈
   - 10 分钟直观体验

3. ✅ [ast_visualization.txt](ast_visualization.txt)
   - 查看树形结构
   - 理解 AST 节点
   - 5 分钟视觉化理解

4. ✅ [THEORY_ANALYSIS.md](THEORY_ANALYSIS.md)
   - 深入理论细节
   - 完整追踪表格
   - EBNF 文法规范

### 对于工程师（实现优化）

**推荐阅读顺序**：
1. 📄 [c_lexer.py](c_lexer.py) - 理解 Token 流
2. 📄 [c_parser.py](c_parser.py) - 理解递归下降细节
3. 📄 [c_interpreter.py](c_interpreter.py) - 理解 AST 执行
4. 📄 [THEORY_ANALYSIS.md](THEORY_ANALYSIS.md) - 参考文法和优先级

---

## 🎓 课程设计论文素材

### 可直接用于论文的部分

#### 1. 追踪过程表格
📄 **来源**: [THEORY_ANALYSIS.md](THEORY_ANALYSIS.md) - Part 1

**表格格式**：完整的追踪表，适合复制到论文附录

```markdown
| 步序 | 当前Token | 调用函数栈 | 操作 | 说明 |
|------|----------|----------|------|------|
| 1    | res (ID) | parse()  | ... | ... |
...
```

#### 2. AST 可视化
📄 **来源**: [ast_visualization.txt](ast_visualization.txt)

**格式**：
- ASCII 树形（可直接粘贴到文档）
- Mermaid 图（可生成 SVG/PNG）
- 原始 tuple 形式

#### 3. 形式化文法
📄 **来源**: [THEORY_ANALYSIS.md](THEORY_ANALYSIS.md) - Part 3

**格式**：
- EBNF 文法规则
- **LaTeX 数学公式**（直接可用于论文）

```latex
\begin{align*}
\text{AdditiveExpr} &\to \text{MultiplicativeExpr} \; (+' \; \text{MultiplicativeExpr})^* \\
\end{align*}
```

#### 4. 优先级表
📄 **来源**: [COMPREHENSIVE_DOCUMENT.md](COMPREHENSIVE_DOCUMENT.md) - Part 3

**表格**：16 个优先级，从低到高列举

---

## 🔍 具体应用示例

### 示例 1：为 `res = a + b * 3` 生成完整文档

```bash
# 1. 运行追踪
python generate_trace.py | grep -A 100 "res = a + b * 3"

# 2. 运行可视化
python visualize_ast.py | grep -A 50 "res = a + b * 3"

# 3. 检查结果
cat parse_output.txt  # 查看 AST
cat interpreter_output.txt  # 查看计算结果
```

### 示例 2：修改表达式测试

编辑 [input_exp.txt](input_exp.txt)：
```
res = a + b * 3;
```

改为想要的表达式，然后重新运行三个步骤。

---

## 📊 输出文件说明

### 1. output.txt
**内容**: Token 列表
**示例**:
```python
Token(type='ID', value='res', line=1, column=1)
Token(type='=', value='=', line=1, column=5)
Token(type='ID', value='a', line=1, column=7)
...
```
**用途**: 验证词法分析的正确性

### 2. parse_output.txt
**内容**: AST 结构
**示例**:
```
ASSIGN('=',
  ID('res'),
  BINARY('+',
    ID('a'),
    BINARY('*',
      ID('b'),
      NUMBER('3')
    )
  )
)
```
**用途**: 验证语法分析的正确性和优先级

### 3. interpreter_output.txt
**内容**: 执行结果和符号表
**示例**:
```
Result: 10
Final symbol table: {'a': 5, 'b': 10, 'c': 0, ...}
```
**用途**: 验证解释执行的正确性

### 4. trace_output.txt
**内容**: 详细的函数调用追踪
**格式**:
```
[深度] 函数名(): 操作 | Token: XXX
  [深度+1] 子函数(): ...
```
**用途**: 理解递归下降的执行流程

### 5. ast_visualization.txt
**内容**: 树形 AST 和 Mermaid 图
**格式**:
```
ASSIGN
├── Operator: =
├── Target:
│   └── ID('res')
└── Value:
    └── BINARY(+)
```
**用途**: 直观理解 AST 结构

---

## 🎯 常见问题解答

### Q1: 如何理解优先级？
**A**: 查看 [trace_output.txt](trace_output.txt)
- 看调用栈的深度
- 深度越大 = 优先级越高
- multiplicative 的深度比 additive 大

### Q2: 为什么乘法在加法下面？
**A**: 查看 [THEORY_ANALYSIS.md](THEORY_ANALYSIS.md) - Part 2
- AST 的深度体现优先级
- 高优先级的运算在树的**更深层**

### Q3: 三元运算符的特殊处理是什么？
**A**: 查看 [c_parser.py](c_parser.py) 的 `conditional()` 方法
- 中间部分需要手动处理逗号
- 否则会冲突

### Q4: 如何添加新运算符？
**A**: 
1. 在 [c_lexer.py](c_lexer.py) 的操作符列表中添加
2. 在 [c_parser.py](c_parser.py) 中创建对应的优先级函数
3. 在 [c_interpreter.py](c_interpreter.py) 中添加求值逻辑

---

## 📝 引用格式

如果在论文中引用本项目，建议格式：

```bibtex
@misc{C_Lexer_Parser_Interpreter,
  title={C Expression Lexer, Parser and Interpreter},
  author={Your Name},
  year={2026},
  howpublished={\url{c:\Users\qwert\Desktop\新建文件夹}},
  note={Complete implementation with theory analysis}
}
```

---

## 🔧 技术栈

- **语言**: Python 3.8+
- **核心库**: `re` (正则表达式), `collections` (namedtuple)
- **不需要外部依赖**

---

## ✅ 验证清单

使用本文档前，请确认：

- [ ] Python 环境已安装
- [ ] 所有 `.py` 文件在工作目录
- [ ] `input_exp.txt` 存在且包含有效表达式
- [ ] 三个主模块都能正常导入（`from c_lexer import CLexer`）
- [ ] 运行 `python test_parser.py` 无错误

---

## 🆘 获取帮助

### 如果遇到错误

1. **词法分析错误**：检查 `input_exp.txt` 中的字符
2. **语法分析错误**：查看 `parse_output.txt` 的错误消息
3. **执行错误**：检查 `interpreter_output.txt` 的变量初始化
4. **追踪问题**：查看 `trace_output.txt` 的函数调用顺序

### 调试技巧

```python
# 在 c_parser.py 中启用调试
parser = CExpressionParser(tokens)
parser._debug = True  # 添加调试输出

# 在 c_interpreter.py 中追踪执行
interpreter = CInterpreter(variables)
interpreter._trace = True  # 输出每一步求值
```

---

## 📄 许可

本项目为教学用途，可自由使用、修改和引用。

---

**最后更新**: 2026 年 1 月 4 日  
**文档版本**: 1.0  
**状态**: ✅ 完成

