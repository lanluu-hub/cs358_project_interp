# CS358 Interpreter — Strings DSL

A tree-walking interpreter for a dynamically typed expression language, built as part of CS358: Principles of Programming Languages at Portland State University. The language includes a core expression sublanguage extended with a domain-specific string manipulation layer, along with a parser built using the Lark parsing library.

---

## Project Structure

```
CS358_Project_interp/
├── project/
│   ├── interp.py           # AST definitions, evaluator, and test expressions
│   ├── expr.lark           # Lark grammar for the full language
│   └── parse_run.py        # Parser, transformer, and concrete syntax tests
├── tests/
│   └── test_phase1_core.py # Instructor-provided core test driver
└── README.md
```

---

## Language Overview

### Core Language

The interpreter supports a pure expression language with the following features:

- **Arithmetic:** `Add`, `Sub`, `Mul`, `Div`, `Neg` — integer operands only
- **Boolean:** `And`, `Or`, `Not` — short-circuiting, boolean operands only
- **Comparisons:** `Eq` (any type), `Lt` (integers only)
- **Conditional:** `If(condition, then, else)` — only evaluates the taken branch
- **Binding:** `Let(name, defexpr, bodyexpr)`, `Name(name)`
- **Functions:** `Letfun(name, arg, defexpr, bodyexpr)`, `App(fexpr, arg)` — lexically scoped, supports recursion via closures
- **Literals:** `Lit(value)` — accepts `int`, `bool`, or `str`

The language is **dynamically typed** — type errors are caught at eval time and raise an `EvalError`.

### Strings DSL Extension

The domain-specific extension adds string manipulation to the core language.

|Construct|Abstract Syntax|Concrete Syntax|Description|
|---|---|---|---|
|String literal|`Lit("hello")`|`"hello"`|Unicode string value|
|Concatenation|`Concat(l, r)`|`l ++ r`|Joins two strings|
|Replace|`Replace(source, target, replacement)`|`replace source target with replacement`|Replaces first instance of target in source|

**Equality:** String equality is character-by-character via `==`.  
**Type errors:** All operators raise `EvalError` if operands are not strings.  
**No external packages required** — built entirely on Python's standard string library.

---

## Concrete Syntax

The full language grammar is defined in `expr.lark`. Precedence from highest to lowest:

```
atom          -- literals, identifiers, parenthesized exprs, let, letfun, app
unary         -- - (negation)
mul           -- * /
add           -- + -
strcat        -- ++ (string concatenation)
compare       -- == < (non-associative)
logic_not     -- !
logic_and     -- &&
logic_or      -- ||
ifexpr        -- if-then-else
expr          -- replace ... with ... (top level)
```

### Example Programs

```
# Arithmetic and binding
let x = 10 in let y = 2 in x / y end end

# Functions and recursion
letfun fact(n) = if n == 0 then 1 else n * fact(n - 1) in fact(5) end

# String manipulation
"hello" ++ " world"
replace "hello world" "world" with "banana"

# DSL + core combined
letfun greet(x) = "hello " ++ x in greet("world") end
if "hello" ++ " world" == "hello world" then true else false
```

---

## How to Run

Requires **Python 3.12+** and the `lark` package:

```bash
pip install lark
```

**Run the interpreter directly (abstract syntax):**

```bash
cd project
python3 interp.py
```

**Run the parser and interpreter together (concrete syntax):**

```bash
cd project
python3 parse_run.py
```

**Run the core test suite:**

```bash
cd tests
python3 test_phase1_core.py
```

---

## Milestones

|Milestone|Due|Status|Description|
|---|---|---|---|
|1|April 26|Done|AST + evaluator for core and Strings DSL|
|2|May 15|Done|Lark grammar + parser + concrete syntax|
|3|June 5|Upcoming|Mutable variables, assignment, sequencing, Show, Read|
|Final|Finals week|Upcoming|Corrections only|

---

## Design Notes

- Evaluation follows a **recursive tree-walking** pattern via `evalInEnv`, passing an immutable environment tuple through each recursive call.
- The `bool` subtype of `int` in Python requires explicit `isinstance` guards on all arithmetic operators to prevent booleans from being silently treated as integers.
- `And` and `Or` are **short-circuiting**: the right operand is only evaluated when necessary.
- The environment is represented as a tuple of `(name, value)` pairs, supporting lexical scoping and variable shadowing via `Let`.
- Functions are implemented using **closures** -- the environment at the time of function definition is captured and used at call time, giving static (lexical) scoping.
- Recursive functions are supported by having the closure's environment point back to itself via `c.env = newEnv` after creation.
- `true` and `false` are parsed as ordinary identifiers and converted to `Lit(True)` / `Lit(False)` during the AST transformation step, keeping the grammar clean.
- String literals use Lark's `ESCAPED_STRING` terminal and are processed via `ast.literal_eval` to correctly handle escape sequences.

---

## Tech Stack

- **Language:** Python 3.12
- **Parsing:** [Lark](https://github.com/lark-parser/lark) (Earley parser)
- **Testing:** Instructor-provided test driver + manual test expressions

---

_Portland State University — CS358 Spring 2026_