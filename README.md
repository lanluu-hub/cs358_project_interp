# CS358 Interpreter — Strings DSL

A tree-walking interpreter for a dynamically typed expression language, built as part of CS358: Principles of Programming Languages at Portland State University. The language includes a core expression sublanguage extended with a domain-specific string manipulation layer.

---

## Project Structure

```
CS358_Project_interp/
├── project/
│   └── interp.py       # AST definitions, evaluator, and test expressions
├── tests/
│   └── test_phase1_core.py  # Instructor-provided core test driver
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
- **Literals:** `Lit(value)` — accepts `int`, `bool`, or `str`

The language is **dynamically typed** — type errors are caught at eval time and raise an `EvalError`.

### Strings DSL Extension

The domain-specific extension adds string manipulation to the core language.

|Construct|Syntax|Description|
|---|---|---|
|String literal|`Lit("hello")`|Unicode string value|
|Concatenation|`Concat(l, r)`|Joins two strings|
|Replace|`Replace(source, target, replacement)`|Replaces first instance of target in source|

**Equality:** String equality is character-by-character via `==`.  
**Type errors:** All operators raise `EvalError` if operands are not strings.  
**No external packages required** — built entirely on Python's standard string library.

---

## How to Run

Requires **Python 3.12+**.

```bash
cd project
python3 interp.py
```

To run the core test suite (once provided):

```bash
cd tests
python3 test_phase1_core.py
```

---

## Example Output

```
running (Hello ++ World)
result: "HelloWorld"

running (replace Hello World! World with Banana)
result: "Hello Banana!"

running if (condition = condition) then (yes ++ !) else no
result: "yes!"
```

---

## Milestones

|Milestone|Due|Status|Description|
|---|---|---|---|
|1|April 26|Done|AST + evaluator for core and Strings DSL|
|2|May 15|In progress|Parser using Lark grammar|
|3|June 5|Upcoming|Functions, statements, expanded features|
|Final|Finals week|Upcoming|Corrections only|

---

## Design Notes

- Evaluation follows a **recursive tree-walking** pattern via `evalInEnv`, passing an immutable environment tuple through each recursive call.
- The `bool` subtype of `int` in Python requires explicit `isinstance` guards on all arithmetic operators to prevent booleans from being silently treated as integers.
- `And` and `Or` are short-circuiting: the right operand is only evaluated when necessary.
- The environment is represented as a tuple of `(name, value)` pairs, supporting lexical scoping and variable shadowing via `Let`.

---

## Tech Stack

- **Language:** Python 3.12
- **Parsing (Milestone 2):** Lark
- **Testing:** Instructor-provided test driver + manual test expressions

---

_Portland State University — CS358 Spring 2026_