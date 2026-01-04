# C 语言表达式编译器 - 完整理论分析文档

## 第一部分：语法分析追踪过程（Parsing Trace）

### 表达式示例：`res = a + b * 3`

#### 追踪表格

| 步序 | 当前Token | 调用函数栈 | 操作 | 说明 |
|------|----------|----------|------|------|
| 1 | res (ID) | parse() → comma() → assignment() | 降级调用 logical_or() | 开始解析，检查赋值运算符 |
| 2 | res (ID) | assignment() → conditional() | 降级调用 logical_or() | 无三元条件，继续下降 |
| 3 | res (ID) | conditional() → logical_or() | 降级调用 logical_and() | 继续下降优先级 |
| 4 | res (ID) | logical_or() → logical_and() | 降级调用 bitwise_or() | 继续下降 |
| 5 | res (ID) | logical_and() → bitwise_or() | 降级调用 bitwise_xor() | 继续下降 |
| 6 | res (ID) | bitwise_or() → bitwise_xor() | 降级调用 bitwise_and() | 继续下降 |
| 7 | res (ID) | bitwise_xor() → bitwise_and() | 降级调用 equality() | 继续下降 |
| 8 | res (ID) | bitwise_and() → equality() | 降级调用 relational() | 继续下降 |
| 9 | res (ID) | equality() → relational() | 降级调用 shift() | 继续下降 |
| 10 | res (ID) | relational() → shift() | 降级调用 additive() | 继续下降 |
| 11 | res (ID) | shift() → additive() | 降级调用 multiplicative() | 继续下降 |
| 12 | res (ID) | additive() → multiplicative() | 降级调用 unary() | 继续下降 |
| 13 | res (ID) | multiplicative() → unary() | 降级调用 postfix() | 继续下降 |
| 14 | res (ID) | unary() → postfix() | 降级调用 primary() | 继续下降 |
| 15 | res (ID) | postfix() → primary() | **匹配 ID，消费 'res'** | **构建节点**：('ID', 'res') |
| 16 | = | postfix() 返回 | 无 postfix 运算符，返回 | 返回 ('ID', 'res') 上升 |
| 17 | = | unary() 返回 | 无 unary 运算符，返回 | 返回 ('ID', 'res') 上升 |
| 18 | = | multiplicative() 返回 | 检查 *, /, % → 不匹配 | 返回 ('ID', 'res')，无左递归 |
| 19 | = | additive() | 当前 expr = ('ID', 'res') | 检查 +, - → 不匹配，返回 |
| 20 | = | shift() 返回 | 返回 ('ID', 'res') | 继续上升 |
| ... | = | ... (各层返回) | 都不匹配符号，继续上升 | 回到 assignment() |
| N | = | assignment() | **匹配 '='，消费 '='** | **确认赋值操作符**，准备右操作数 |
| N+1 | a (ID) | assignment() 递归调用自身 | 降级调用 conditional() | 解析右侧表达式（右结合） |
| N+2 | a (ID) | assignment() → conditional() → ... | 同步骤 2-14 | 快速下降到 additive() |
| N+3 | a (ID) | additive() → multiplicative() → ... → primary() | **匹配 'a'，消费 'a'** | **构建**：('ID', 'a') |
| N+4 | + | multiplicative() 返回 ('ID', 'a') | 无 *, /, %，返回 | 返回 ('ID', 'a') |
| N+5 | + | additive() **检查 +, -** | **匹配 '+'，消费 '+'** | **进入 while 循环**，准备右操作数 |
| N+6 | b (ID) | additive() 调用 multiplicative() | 降级到 primary() | 解析 'b' |
| N+7 | b (ID) | multiplicative() → ... → primary() | **匹配 'b'，消费 'b'** | **构建**：('ID', 'b') |
| N+8 | * | multiplicative() **检查 *, /, %** | **匹配 '*'，消费 '*'** | **进入 multiplicative while 循环** |
| N+9 | 3 (NUM) | multiplicative() 调用 unary() | 降级到 primary() | 解析 '3' |
| N+10 | 3 (NUM) | unary() → ... → primary() | **匹配 '3'，消费 '3'** | **构建**：('NUMBER', '3') |
| N+11 | ; | multiplicative() | 无更多 *, /, %，退出 while | **构建节点**：('BINARY', '*', ('ID', 'b'), ('NUMBER', '3')) |
| N+12 | ; | additive() | 剩余表达式 = ('BINARY', '*', ...) | 检查 +, - → **不匹配 ';'**，退出 while |
| N+13 | ; | additive() 返回 | 返回 ('BINARY', '+', ('ID', 'a'), ('BINARY', '*', ...)) | **构建节点**：('BINARY', '+', ('ID', 'a'), ('BINARY', '*', ...)) |
| N+14 | ; | 上升到 assignment() | 右操作数完成 | **构建节点**：('ASSIGN', '=', ('ID', 'res'), ('BINARY', '+', ...)) |
| N+15 | ; | assignment() 返回到 comma() | 赋值完成 | 返回完整 AST |
| N+16 | ; | comma() 检查 ',' | 不匹配 ';'，退出 | **解析完成，返回根节点** |

#### 追踪过程关键点

**下降阶段（步骤 1-14）**：
- 从最低优先级 `assignment()` 开始
- 逐级下降到 `primary()`（最高优先级）
- 消费第一个操作数 `res`

**上升阶段（步骤 16-19）**：
- 各层函数逐级返回
- 每层检查对应的运算符
- `res` 没有后缀运算符、一元运算符、乘法、加法等

**赋值处理（步骤 N）**：
- `assignment()` 匹配 `=` 运算符
- 递归调用自身以实现**右结合性**

**加法处理（步骤 N+5）**：
- `additive()` 进入 while 循环
- 消费 `+` 并解析右操作数 `b`
- 此时右操作数调用 `multiplicative()`（更高优先级）

**乘法优先级体现（步骤 N+8-12）**：
```
additive() 在 while 循环中:
  → 调用 multiplicative()
    → multiplicative() 进入自己的 while 循环
      → 消费 '*'
      → 解析 '3'
      → **先完成** ('BINARY', '*', ('ID', 'b'), ('NUMBER', '3'))
  → 返回完整的乘法表达式
  → additive 收到已完成的乘法，作为加法的右操作数
```

这正是**乘法优先级高于加法**的体现！

---

## 第二部分：抽象语法树（AST）可视化

### 原表达式
```
res = a + b * 3
```

### AST 元组形式
```python
('ASSIGN', '=', 
  ('ID', 'res'), 
  ('BINARY', '+', 
    ('ID', 'a'), 
    ('BINARY', '*', 
      ('ID', 'b'), 
      ('NUMBER', '3')
    )
  )
)
```

### 树形结构可视化

```
                        ASSIGN(=)
                       /         \
                    res           BINARY(+)
                                 /         \
                               ID(a)     BINARY(*)
                                        /         \
                                     ID(b)     NUMBER(3)
```

### 详细的树形缩进表示

```
ASSIGN
├─ Operator: =
├─ Left (LValue):
│  └─ ID
│     └─ name: 'res'
└─ Right (RValue):
   └─ BINARY
      ├─ Operator: +
      ├─ Left:
      │  └─ ID
      │     └─ name: 'a'
      └─ Right:
         └─ BINARY
            ├─ Operator: *
            ├─ Left:
            │  └─ ID
            │     └─ name: 'b'
            └─ Right:
               └─ NUMBER
                  └─ value: '3'
```

### 结构分析

#### 为什么 ASSIGN 在根部？
```
优先级链：
  comma(最低) → assignment → conditional → ...
                   ↑
                (最先匹配)
```

赋值 `=` 的优先级**最低**（除逗号外），所以它被最后消费，成为 AST 树的**根节点**。

#### 为什么 * 比 + 更深？
```
加法处理过程：
  additive() {
    expr = multiplicative()     ← 调用高优先级
    while (+, -) {
      expr = BINARY(+, expr, multiplicative())  ← 右操作数也来自 multiplicative
    }
  }

乘法处理过程：
  multiplicative() {
    expr = unary()
    while (*, /, %) {
      expr = BINARY(*, expr, unary())
    }
  }
```

关键：**multiplicative 被 additive 调用**，所以 `b * 3` 先于 `a + ...` 完成。

#### 消除歧义

原表达式中的优先级顺序可能有歧义：
- `a + b * 3` 是 `(a + (b * 3))` 还是 `((a + b) * 3)`？

AST 结构明确表示：
- 乘法 `*` 在树的**较深位置**（较晚构建）
- 加法 `+` 在树的**较浅位置**（较晚返回）
- 这确保了 `b * 3` 作为一个**完整的子表达式**被传递给加法

### 执行求值顺序

根据 AST **自底向上** 计算：
```
1. 求值 ID(b) = b 的值
2. 求值 NUMBER(3) = 3
3. 求值 BINARY(*, b, 3) = b * 3
4. 求值 ID(a) = a 的值
5. 求值 BINARY(+, a, b*3) = a + (b*3)
6. 求值 ASSIGN(=, res, a+b*3) = 赋给 res，返回值
```

---

## 第三部分：形式化文法（EBNF）

### 扩展巴科斯范式 (EBNF) 规则

```ebnf
(* 最低优先级 *)
Expression        = CommaExpr ;

CommaExpr         = AssignExpr { ',' AssignExpr } ;

AssignExpr        = ConditionalExpr 
                  | ConditionalExpr AssignOp AssignExpr  (* 右结合 *)
                  ;

AssignOp          = '='  | '+='  | '-='  | '*='  | '/='  | '%=' 
                  | '<<=' | '>>=' | '&=' | '|=' | '^=' 
                  ;

ConditionalExpr   = LogicalOrExpr 
                  | LogicalOrExpr '?' AssignExpr ':' ConditionalExpr  (* 右结合 *)
                  ;

LogicalOrExpr     = LogicalAndExpr { '||' LogicalAndExpr } ;

LogicalAndExpr    = BitwiseOrExpr { '&&' BitwiseOrExpr } ;

BitwiseOrExpr     = BitwiseXorExpr { '|' BitwiseXorExpr } ;

BitwiseXorExpr    = BitwiseAndExpr { '^' BitwiseAndExpr } ;

BitwiseAndExpr    = EqualityExpr { '&' EqualityExpr } ;

EqualityExpr      = RelationalExpr { EqualityOp RelationalExpr } ;

EqualityOp        = '==' | '!=' ;

RelationalExpr    = ShiftExpr { RelationalOp ShiftExpr } ;

RelationalOp      = '<' | '<=' | '>' | '>=' ;

ShiftExpr         = AdditiveExpr { ShiftOp AdditiveExpr } ;

ShiftOp           = '<<' | '>>' ;

AdditiveExpr      = MultiplicativeExpr { AdditiveOp MultiplicativeExpr } ;

AdditiveOp        = '+' | '-' ;

MultiplicativeExpr = UnaryExpr { MultiplicativeOp UnaryExpr } ;

MultiplicativeOp  = '*' | '/' | '%' ;

UnaryExpr         = PostfixExpr 
                  | UnaryOp UnaryExpr  (* 右结合 *)
                  ;

UnaryOp           = '!' | '~' | '++' | '--' | '+' | '-' ;

PostfixExpr       = PrimaryExpr 
                  { PostfixOp }  (* 左结合：逐个应用 *)
                  ;

PostfixOp         = '[' Expression ']'  (* 数组下标 *)
                  | '++' | '--'          (* 后缀递增/递减 *)
                  ;

PrimaryExpr       = Identifier 
                  | Number 
                  | '(' Expression ')'
                  ;

Identifier        = Letter { Letter | Digit | '_' } ;

Number            = Digit { Digit } 
                  | '0x' HexDigit { HexDigit }
                  | '0' OctalDigit { OctalDigit }
                  ;

Letter            = 'a' | 'b' | ... | 'z' | 'A' | ... | 'Z' | '_' ;
Digit             = '0' | '1' | ... | '9' ;
HexDigit          = '0' | ... | '9' | 'a' | ... | 'f' | 'A' | ... | 'F' ;
OctalDigit        = '0' | '1' | ... | '7' ;
```

### LaTeX 格式规则（用于学位论文）

```latex
\begin{align*}
\text{Expression}     &\to \text{CommaExpr} \\
\text{CommaExpr}      &\to \text{AssignExpr} \; (\text{`,` AssignExpr})^* \\
\text{AssignExpr}     &\to \text{ConditionalExpr} \\
                      &\mid \text{ConditionalExpr} \; \text{AssignOp} \; \text{AssignExpr} \\
\text{AssignOp}       &\to `=' \mid `+=' \mid `-=' \mid `*=' \mid `/=' \mid `\%=' \\
                      &\mid `<<=' \mid `>>=' \mid `\&=' \mid `|=' \mid `\text{\textasciicircum}=' \\
\text{ConditionalExpr} &\to \text{LogicalOrExpr} \\
                      &\mid \text{LogicalOrExpr} \; `?' \; \text{AssignExpr} \; `:' \; \text{ConditionalExpr} \\
\text{LogicalOrExpr}  &\to \text{LogicalAndExpr} \; (`||' \; \text{LogicalAndExpr})^* \\
\text{LogicalAndExpr} &\to \text{BitwiseOrExpr} \; (`\&\&' \; \text{BitwiseOrExpr})^* \\
\text{BitwiseOrExpr}  &\to \text{BitwiseXorExpr} \; (`|' \; \text{BitwiseXorExpr})^* \\
\text{BitwiseXorExpr} &\to \text{BitwiseAndExpr} \; (`\text{\textasciicircum}' \; \text{BitwiseAndExpr})^* \\
\text{BitwiseAndExpr} &\to \text{EqualityExpr} \; (`\&' \; \text{EqualityExpr})^* \\
\text{EqualityExpr}   &\to \text{RelationalExpr} \; (\text{EqualityOp} \; \text{RelationalExpr})^* \\
\text{EqualityOp}     &\to `==' \mid `!=' \\
\text{RelationalExpr} &\to \text{ShiftExpr} \; (\text{RelationalOp} \; \text{ShiftExpr})^* \\
\text{RelationalOp}   &\to `<' \mid `<=' \mid `>' \mid `>=' \\
\text{ShiftExpr}      &\to \text{AdditiveExpr} \; (\text{ShiftOp} \; \text{AdditiveExpr})^* \\
\text{ShiftOp}        &\to `<<' \mid `>>' \\
\text{AdditiveExpr}   &\to \text{MultiplicativeExpr} \; (\text{AdditiveOp} \; \text{MultiplicativeExpr})^* \\
\text{AdditiveOp}     &\to `+' \mid `-' \\
\text{MultiplicativeExpr} &\to \text{UnaryExpr} \; (\text{MultiplicativeOp} \; \text{UnaryExpr})^* \\
\text{MultiplicativeOp}   &\to `*' \mid `/' \mid `\%' \\
\text{UnaryExpr}      &\to \text{PostfixExpr} \\
                      &\mid \text{UnaryOp} \; \text{UnaryExpr} \\
\text{UnaryOp}        &\to `!' \mid `\sim' \mid `++' \mid `--' \mid `+' \mid `-' \\
\text{PostfixExpr}    &\to \text{PrimaryExpr} \; (\text{PostfixOp})^* \\
\text{PostfixOp}      &\to `[' \; \text{Expression} \; `]' \mid `++' \mid `--' \\
\text{PrimaryExpr}    &\to \text{Identifier} \mid \text{Number} \mid `(' \; \text{Expression} \; `)' \\
\end{align*}
```

### 优先级表（从低到高）

| 优先级 | 运算符类别 | 运算符 | 结合性 | 示例 |
|--------|-----------|--------|--------|------|
| 1 (最低) | 逗号 | `,` | 左 | `a, b, c` |
| 2 | 赋值 | `=, +=, -=, *=, /=, %=, <<=, >>=, &=, ^=, \|=` | 右 | `a = b = c` |
| 3 | 条件 | `? :` | 右 | `a ? b : c ? d : e` |
| 4 | 逻辑或 | `\|\|` | 左 | `a \|\| b \|\| c` |
| 5 | 逻辑与 | `&&` | 左 | `a && b && c` |
| 6 | 位或 | `\|` | 左 | `a \| b \| c` |
| 7 | 位异或 | `^` | 左 | `a ^ b ^ c` |
| 8 | 位与 | `&` | 左 | `a & b & c` |
| 9 | 相等 | `==, !=` | 左 | `a == b != c` |
| 10 | 关系 | `<, <=, >, >=` | 左 | `a < b <= c` |
| 11 | 移位 | `<<, >>` | 左 | `a << 2 >> 1` |
| 12 | 加减 | `+, -` | 左 | `a + b - c` |
| 13 | 乘除模 | `*, /, %` | 左 | `a * b / c % d` |
| 14 | 一元 | `!, ~, ++, --, +, -` | 右 | `!a, ~b, ++c, -d` |
| 15 (最高) | 后缀 | `[], ++, --` | 左 | `a[i]++, b--` |

### 关键文法特性解析

#### 1. 左结合 vs 右结合

**左结合** (使用 `{...}*` 迭代)：
```ebnf
AdditiveExpr = MultiplicativeExpr { '+' MultiplicativeExpr } ;
```
解析 `a + b + c`：
- 第一步：识别 `a + b` → `BINARY(+, a, b)`
- 第二步：识别 `result + c` → `BINARY(+, BINARY(+, a, b), c)`

**右结合** (递归调用)：
```ebnf
AssignExpr = ConditionalExpr | ConditionalExpr '=' AssignExpr ;
```
解析 `a = b = c`：
- 第一步：识别 `b = c` → `ASSIGN(=, b, c)` （递归处理）
- 第二步：识别 `a = result` → `ASSIGN(=, a, ASSIGN(=, b, c))`

#### 2. 优先级编码

文法中的**调用顺序**编码了优先级：
```ebnf
AdditiveExpr → MultiplicativeExpr → UnaryExpr → PostfixExpr → PrimaryExpr
  ↓           ↓                     ↓          ↓             ↓
 (低)        (中)                 (高)       (高)        (最高)
```

越往下调用，优先级越高。这保证了高优先级的运算符**先完成**。

---

## 总结

这份文档展示了：
1. **追踪过程**：递归下降如何通过优先级链逐步构建 AST
2. **AST 结构**：树形表示如何消除表达式歧义
3. **形式化文法**：理论基础，可直接用于编译器设计论文

所有三个部分相互补充，共同说明了**编译原理中优先级处理的核心机制**。
