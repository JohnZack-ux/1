# C 语言表达式编译器 - 完整理论与实践文档

## 📚 文档目录

- [Part 1: 语法分析追踪过程](#part-1-语法分析追踪过程)
- [Part 2: AST 可视化展示](#part-2-ast-可视化展示)
- [Part 3: 形式化文法 EBNF](#part-3-形式化文法-ebnf)
- [附录：实现细节](#附录实现细节)

---

## Part 1: 语法分析追踪过程

### 目标表达式
```
res = a + b * 3
```

### 核心概念

**递归下降解析（Recursive Descent Parsing）** 的关键：
- 从最低优先级开始解析
- 逐级下降到最高优先级
- 通过函数调用栈体现优先级关系

### 追踪表总结

| 阶段 | 过程 | 关键点 |
|------|------|--------|
| **下降** | comma → assignment → conditional → ... → primary | 消费第一个操作数 `res` |
| **返回** | primary → postfix → unary → ... → assignment | 各层检查对应运算符，遇到 `=` 时停止 |
| **赋值** | assignment 匹配 `=`，递归调用自身 | 实现右结合性 |
| **加法** | additive 进入 while 循环，消费 `+` | 调用 multiplicative() 处理右操作数 |
| **乘法优先** | multiplicative 先完成 `b * 3` | 作为加法的完整子表达式 |

### 优先级体现

```
调用链（从低到高）：
comma
  └─> assignment (匹配 = )
       └─> conditional (无 ?)
            └─> logical_or
                 └─> ... 
                      └─> additive (匹配 + )
                           └─> multiplicative (匹配 *)
                                └─> ... 
                                     └─> primary
```

**关键：multiplicative 被 additive 调用**
- `multiplicative()` 返回 `BINARY(*, b, 3)` 作为**完整的单元**
- `additive()` 将这个单元作为右操作数：`BINARY(+, a, BINARY(*, b, 3))`
- 这确保了 `*` 优先于 `+`

---

## Part 2: AST 可视化展示

### 示例 1: `res = a + b * 3`

#### 树形结构
```
ASSIGN
├── Operator: =
├── Target:
│   └── ID('res')
└── Value:
    └── BINARY
        ├── Operator: +
        ├── Left:
        │   └── ID('a')
        └── Right:
            └── BINARY
                ├── Operator: *
                ├── Left:
                │   └── ID('b')
                └── Right:
                    └── NUMBER('3')
```

#### 为什么这样结构化？

1. **ASSIGN 在根** → `=` 优先级最低，最后消费
2. `+` 在 `*` 之上 → `+` 比 `*` 优先级低，所以出现在较浅的位置
3. `*` 在 `+` 之下 → `*` 优先级高，先完成，作为 `+` 的右子树

#### 消除歧义

| 歧义 | 原表达式 | 错误解释 | **正确 AST** | 正确计算 |
|------|---------|---------|-----------|---------|
| 哪个先算？ | `a + b * 3` | `(a + b) * 3 = 5 * 3 = 15` | `BINARY(+, a, BINARY(*, b, 3))` | `a + (b * 3)` |

### 示例 2: `a > 5 ? b += 5, b : c`

#### 树形结构
```
CONDITIONAL
├── Condition:
│   └── BINARY(>, a, 5)
├── True Branch:
│   └── BINARY(,
│       ├── ASSIGN(+=, b, 5)
│       └── ID(b)
│       )
└── False Branch:
    └── ID(c)
```

#### 关键特性

- **三元运算符中间部分支持逗号和赋值**：
  - 中间部分 `b += 5, b` 包含赋值和逗号
  - 需要手动处理逗号以避免优先级冲突
  
- **结构体现的语义**：
  ```
  if (a > 5)
    return (b += 5), b    // 赋值给 b，然后返回 b 的值
  else
    return c
  ```

---

## Part 3: 形式化文法 EBNF

### EBNF 语法规则（所有 16 个优先级）

```ebnf
(* 优先级从低到高 *)

Expression          = CommaExpr ;

CommaExpr           = AssignExpr { ',' AssignExpr } ;

AssignExpr          = ConditionalExpr 
                    | ConditionalExpr AssignOp AssignExpr
                    ;

AssignOp            = '=' | '+=' | '-=' | '*=' | '/=' | '%=' 
                    | '<<=' | '>>=' | '&=' | '^=' | '|='
                    ;

ConditionalExpr     = LogicalOrExpr 
                    | LogicalOrExpr '?' AssignExpr ':' ConditionalExpr
                    ;

LogicalOrExpr       = LogicalAndExpr { '||' LogicalAndExpr } ;

LogicalAndExpr      = BitwiseOrExpr { '&&' BitwiseOrExpr } ;

BitwiseOrExpr       = BitwiseXorExpr { '|' BitwiseXorExpr } ;

BitwiseXorExpr      = BitwiseAndExpr { '^' BitwiseAndExpr } ;

BitwiseAndExpr      = EqualityExpr { '&' EqualityExpr } ;

EqualityExpr        = RelationalExpr { EqualityOp RelationalExpr } ;

EqualityOp          = '==' | '!=' ;

RelationalExpr      = ShiftExpr { RelationalOp ShiftExpr } ;

RelationalOp        = '<' | '<=' | '>' | '>=' ;

ShiftExpr           = AdditiveExpr { ShiftOp AdditiveExpr } ;

ShiftOp             = '<<' | '>>' ;

AdditiveExpr        = MultiplicativeExpr { AdditiveOp MultiplicativeExpr } ;

AdditiveOp          = '+' | '-' ;

MultiplicativeExpr  = UnaryExpr { MultiplicativeOp UnaryExpr } ;

MultiplicativeOp    = '*' | '/' | '%' ;

UnaryExpr           = PostfixExpr | UnaryOp UnaryExpr ;

UnaryOp             = '!' | '~' | '++' | '--' | '+' | '-' ;

PostfixExpr         = PrimaryExpr { PostfixOp } ;

PostfixOp           = '[' Expression ']' | '++' | '--' ;

PrimaryExpr         = Identifier | Number | '(' Expression ')' ;

Identifier          = Letter { Letter | Digit | '_' } ;

Number              = Digit { Digit } 
                    | '0x' HexDigit { HexDigit }
                    | '0' OctalDigit { OctalDigit }
                    ;
```

### EBNF 符号解释

| 符号 | 含义 | 示例 |
|------|------|------|
| `A B` | 序列（A 后跟 B） | `'a' 'b'` 匹配 `ab` |
| `A \| B` | 选择（A 或 B） | `'a' \| 'b'` 匹配 `a` 或 `b` |
| `{ A }` | 重复 0 次或多次（*） | `{ 'a' }` 匹配 `ε`, `a`, `aa`, ... |
| `[ A ]` | 可选（0 或 1 次） | `[ 'a' ]` 匹配 `ε` 或 `a` |
| `( A )` | 分组 | `( 'a' \| 'b' ) 'c'` |

### 文法的关键特性

#### 1. 左结合实现

```ebnf
AdditiveExpr = MultiplicativeExpr { '+' MultiplicativeExpr } ;
```

对应代码：
```python
expr = multiplicative()
while match('+'):
    advance()
    right = multiplicative()
    expr = BINARY('+', expr, right)  # 左结合：expr 成为新节点的左子树
```

解析 `a + b + c`：
```
第一次循环：expr = BINARY(+, a, b)
第二次循环：expr = BINARY(+, BINARY(+, a, b), c)
```

#### 2. 右结合实现

```ebnf
AssignExpr = ConditionalExpr | ConditionalExpr AssignOp AssignExpr ;
```

对应代码：
```python
expr = conditional()
if match(AssignOp):
    op = advance()
    value = assignment()  # 递归调用：右结合
    expr = ASSIGN(op, expr, value)
```

解析 `a = b = c`：
```
第一次调用：assignment() 对整个表达式
  ├─ 识别 'a' 和 '='
  └─ 递归调用 assignment() 处理 'b = c'
      ├─ 识别 'b' 和 '='
      └─ 递归调用 assignment() 处理 'c'
          └─ 返回 'c'
      └─ 返回 ASSIGN(=, b, c)
  └─ 返回 ASSIGN(=, a, ASSIGN(=, b, c))
```

#### 3. 优先级的文法体现

文法的递归链体现了优先级：

```
低优先级 ──调用──> 高优先级
CommaExpr  →  AssignExpr  →  ConditionalExpr  → ... → PrimaryExpr
   (1)           (2)           (3)                    (最高)
```

**重要**：一个级别的规则调用下一个级别的规则，确保了更高优先级的运算符先完成。

---

## 附录：实现细节

### 递归下降算法的三个关键步骤

#### 1. Token 流

```
位置:  0      1    2    3    4    5   6
Token: res    =    a    +    b    *   3
```

#### 2. 函数调用栈演化

```
开始：                  parse()
                        └─ comma()
                           └─ assignment()
                              └─ conditional()
                                 └─ ... (下降到 primary)

识别 res：              assignment() 识别到 '='
                        └─ 递归调用 assignment()
                           └─ ... (下降到 additive)

识别 +：                additive() 匹配 '+'
                        └─ 调用 multiplicative()
                           └─ ... (下降到 primary 识别 b)

识别 *：                multiplicative() 匹配 '*'
                        └─ 调用 unary()
                           └─ ... (下降到 primary 识别 3)

返回：                  乘法完成 → 加法完成 → 赋值完成 → 返回根节点
```

#### 3. 节点构建顺序

```
1. primary() 消费 res      → ('ID', 'res')
2. primary() 消费 a        → ('ID', 'a')
3. primary() 消费 b        → ('ID', 'b')
4. primary() 消费 3        → ('NUMBER', '3')
5. multiplicative() 组合   → ('BINARY', '*', ('ID', 'b'), ('NUMBER', '3'))
6. additive() 组合         → ('BINARY', '+', ('ID', 'a'), <result of 5>)
7. assignment() 组合       → ('ASSIGN', '=', ('ID', 'res'), <result of 6>)
```

### 复杂情况：三元运算符

**表达式**: `a ? b += 5, b : c`

**问题**：中间部分可包含赋值和逗号，导致优先级冲突。

**解决**：手动处理逗号而不是递归调用 `conditional()`

```python
def conditional(self):
    expr = self.logical_or()
    
    if self._match('?'):
        self._advance()
        
        # 关键：手动处理逗号，不递归到 conditional
        true_branch = self.assignment()
        while self._match(','):
            self._advance()
            right = self.assignment()
            true_branch = binary_op(',', true_branch, right)
        
        self._expect(':')
        false_branch = self.conditional()
        expr = conditional_op(expr, true_branch, false_branch)
    
    return expr
```

---

## 总结

| 文档部分 | 重点 | 应用 |
|---------|------|------|
| **追踪过程** | 理解递归下降如何消费 Token | 调试编译器、理解优先级 |
| **AST 可视化** | 查看树形结构，理解语义 | 代码优化、语义分析 |
| **形式化文法** | 理论基础，便于扩展语言 | 论文撰写、编译原理教学 |

这三个部分相互配合，全面展示了编译原理中**优先级处理和语法分析**的核心机制。
