# C 语言解释器 - 最终版本

## 项目概述

这是一个完整的 C 语言解释器，支持：
- ✓ 变量声明 (`int a = 10;`)
- ✓ 多语句程序 (`int a = 5; int b = 10; a = a + b;`)
- ✓ 所有 C 运算符（算术、逻辑、位运算等）
- ✓ 三目运算符 (`a ? b : c`)
- ✓ 递增/递减 (`a++`, `++a`)
- ✓ 浮点数和整数混合运算

## 文件结构

```
c_lexer.py          - 词法分析器（标记化）
c_parser.py         - 语法分析器（AST 生成）
c_interpreter.py    - 解释执行器（计算结果）
input.txt           - 测试程序源代码
run_test.py         - 统一测试脚本
```

## 文档

```
UPGRADE_SUMMARY.md       - 升级总结
CODE_CHANGES_DETAIL.md   - 代码修改详解
USER_MANUAL.md           - 完整使用手册
VERIFICATION_REPORT.py   - 验证报告
```

## 快速使用

### 方式 1：运行测试

```bash
python run_test.py
```

这会：
1. 读取 `input.txt` 中的 C 程序
2. 进行词法分析（生成 122 个令牌）
3. 进行语法分析（生成 AST）
4. 执行程序（显示所有变量的最终值）

### 方式 2：在 Python 中使用

```python
from c_lexer import CLexer
from c_parser import CExpressionParser
from c_interpreter import CInterpreter

# 源代码
code = """
int a = 10;
int b = a + 5;
"""

# 词法分析
lexer = CLexer()
lexer.text = code
lexer._build_regex()
tokens = list(lexer.tokenize())

# 语法分析
parser = CExpressionParser(tokens)
ast = parser.parse()

# 执行
interpreter = CInterpreter()
interpreter.run(ast)

print(f"a = {interpreter.variables['a']}")  # 10
print(f"b = {interpreter.variables['b']}")  # 15
```

## 测试程序示例 (input.txt)

```c
int a = 10;                    // 声明并初值
int b = 20, c;                 // 多变量声明
a = a + b;                     // 算术运算
c = a * 2;                     // 复杂表达式
int d = c - 5;                 // 声明和计算
d++;                           // 递增
int e = d > 50 ? 100 : 200;    // 三目运算
int flag = (a > 5) && (b < 30); // 逻辑运算
int result = a & b;            // 位运算
int shifted = a << 2;          // 移位
int xored = b ^ 7;             // 异或
float pi = 3.14159;            // 浮点数
float radius = 5.0;
float area = pi * radius * radius;  // 浮点计算
int x = 15;
int nested = x > 10 ? x < 20 ? x : 20 : 10;  // 嵌套三目
```

## 执行结果

```
变量最终状态:
  a               = 30 (int)
  area            = 78.53975 (float)
  b               = 20 (int)
  c               = 60 (int)
  d               = 56 (int)
  e               = 100 (int)
  flag            = 1 (int)
  nested          = 15 (int)
  pi              = 3.14159 (float)
  radius          = 5.0 (float)
  result          = 20 (int)
  shifted         = 120 (int)
  x               = 15 (int)
  xored           = 19 (int)
```

## 支持的运算符

| 类别 | 运算符 |
|------|--------|
| 算术 | `+` `-` `*` `/` `%` |
| 比较 | `<` `<=` `>` `>=` `==` `!=` |
| 逻辑 | `&&` `||` `!` |
| 位运算 | `&` `|` `^` `~` `<<` `>>` |
| 赋值 | `=` `+=` `-=` `*=` `/=` `%=` `&=` `|=` `^=` `<<=` `>>=` |
| 其他 | `?:` `++` `--` `,` |

## 关键特性

1. **三层架构**
   - 词法分析：源代码 → 令牌流
   - 语法分析：令牌流 → AST
   - 解释执行：AST → 结果

2. **完整的表达式支持**
   - 正确的运算符优先级和结合性
   - 短路求值（`&&` 和 `||`）
   - 类型混合运算（int 和 float）

3. **变量管理**
   - 符号表维护
   - 自动初值（默认 0）
   - 动态类型（Python 风格）

4. **错误处理**
   - 详细的语法错误报告
   - 行号和列号信息
   - 运行时错误捕获

## 修改 input.txt

要测试不同的程序，只需编辑 `input.txt` 文件：

```c
// 示例：计算阶乘和
int n = 5;
int sum = 0;
int i = 1;
sum = sum + 1;
sum = sum + 2;
sum = sum + 3;
sum = sum + 4;
sum = sum + 5;
// sum = 15
```

然后运行：
```bash
python run_test.py
```

## 性能

- **词法分析**：O(n)
- **语法分析**：O(n)
- **执行**：O(AST 大小)

对大多数程序足够快速。

## 已知限制

- ❌ 无函数定义
- ❌ 无块作用域
- ❌ 无指针
- ❌ 无数组声明
- ❌ 无控制流（if/while/for）

## 版本信息

- **版本**：2.0
- **日期**：2026-01-04
- **状态**：完成且通过所有测试

## 许可证

开源项目，自由使用和修改。

---

**最后更新**：2026-01-04
