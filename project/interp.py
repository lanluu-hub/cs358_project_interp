# CS358 Principles of Programming Languages -- Spring 2026
# Project: Tree-Walking Interpreter (Strings DSL)
# Author: Lan Luu
#
# Milestones:
#   Milestone 1 (April 26): AST + evaluator for pure expressions
#   Milestone 2 (May 15):   Parser integration (expr.lark, parse_run.py)
#   Milestone 3 (June 5):   Mutable variables (Loc), Assign, Seq, Show, Read,
#                           + DSL extensions: Reverse, Uppercase, Lowercase
#
# Architecture:
#   - Three-file structure:
#       interp.py     -- AST node definitions, evaluator, Loc mutation model
#       expr.lark     -- Lark grammar (Earley parser)
#       parse_run.py  -- transformer, parse_and_run, driver, main
#   - Environment model: immutable tuple of (name, Loc[Value]) bindings
#   - Mutation via Loc (singleton mutable list): newLoc, getLoc, setLoc
#   - bool is a subtype of int in Python; all arithmetic ops guard with isinstance
#
# Domain-Specific Extension: Strings DSL
#   Values:    Python str (unicode)
#   Literals:  Lit("...") -- quoted string literals
#   Operators: Concat, Replace, Reverse, Uppercase, Lowercase (all pure)
#   Equality:  character-by-character via ==

from dataclasses import dataclass

type Value = int | bool | str | Closure

type Expr = Add | Sub | Mul | Div | Neg | Or | And | Not | Let | Letfun | Fun | App | Name | Concat | Replace | Lit | Eq | Lt | If | Seq | Assign | Show | Read | Reverse | Uppercase | Lowercase

@dataclass
class Add():
    """AST node for integer addition.

    Invariant: left and right must evaluate to int (not bool).
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"
    
@dataclass
class Sub():
    """AST node for integer subtraction.

    Invariant: left and right must evaluate to int (not bool).
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} - {self.right})"
    
@dataclass
class Mul():
    """AST node for integer multiplication.

    Invariant: left and right must evaluate to int (not bool).
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"
    
@dataclass
class Div():
    """AST node for integer division (floor division).

    Invariant: left and right must evaluate to int (not bool); right must be nonzero.
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} / {self.right})"
    
@dataclass
class Neg():
    """AST node for integer negation (unary minus).

    Invariant: subexpr must evaluate to int (not bool).
    """
    subexpr: Expr
    def __str__(self) -> str:
        return f"(- {self.subexpr})"
    
@dataclass
class Or():
    """AST node for short-circuit logical OR.

    Invariant: left must evaluate to bool; right is only evaluated if left is False.
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} or {self.right})"
    
@dataclass
class And():
    """AST node for short-circuit logical AND.

    Invariant: left must evaluate to bool; right is only evaluated if left is True.
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} and {self.right})"
    
@dataclass
class Not():
    """AST node for logical NOT.

    Invariant: subexpr must evaluate to bool.
    """
    subexpr: Expr
    def __str__(self) -> str:
        return f"(not {self.subexpr})"

@dataclass
class Let():
    """AST node for immutable let-binding (becomes mutable via Loc in eval).

    The bound name is wrapped in a Loc in evalInEnv, making it assignable
    within the body scope via Assign.

    Params:
        name:     variable name to bind
        defexpr:  expression whose value is bound to name
        bodyexpr: expression evaluated in the extended environment
    """
    name: str
    defexpr: Expr
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

@dataclass
class Letfun():
    """AST node for named recursive function definition.

    The closure is stored in a Loc to support recursion: the closure's env
    is patched (c.env = newEnv) after the Loc is created so that the function
    can refer to itself by name.

    Only supports single-argument functions. Multi-arg support is a planned extension.

    Params:
        name:     function name (bound in inexpr and recursively in bodyexpr)
        arg:      parameter name (bound in bodyexpr at call site)
        bodyexpr: function body
        inexpr:   expression evaluated in the scope where the function is bound
    """
    name: str
    arg: str
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name}({self.arg}) = {self.bodyexpr} in {self.inexpr} end"

@dataclass
class App():
    """AST node for function application.

    fexpr must evaluate to a Closure. The argument is wrapped in a newLoc
    before being added to the closure's environment, consistent with the
    uniform Loc-based environment model.

    Params:
        fexpr: expression that evaluates to a Closure
        arg:   argument expression passed to the function
    """
    fexpr: Expr
    arg: Expr
    def __str__(self) -> str:
        return f"{self.fexpr}({self.arg})"

@dataclass
class Name():
    """AST node for variable reference.

    Looks up name in the current environment and dereferences the Loc.

    Params:
        name: variable name to look up
    """
    name: str
    def __str__(self) -> str:
        return self.name

@dataclass
class Concat():
    """AST node for string concatenation (Strings DSL).

    Concrete syntax: left ++ right

    Invariant: left and right must evaluate to str.
    """
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"(concatenate {self.left} {self.right})"

@dataclass
class Replace():
    """AST node for first-instance substring replacement (Strings DSL).

    Concrete syntax: replace source target with replacement

    If target is not found in source, returns source unchanged.
    All operators are pure -- no mutation of the original string.

    Invariant: source, target, and replacement must all evaluate to str.

    Params:
        source:      string to search in
        target:      substring to find (first instance only)
        replacement: string to substitute in place of target
    """
    source: Expr
    target: Expr
    replacement: Expr
    def __str__(self) -> str:
        return f"(replace {self.source} {self.target} with {self.replacement})"

@dataclass
class Lit():
    """AST node for a literal value (int, bool, or str).

    Params:
        value: the literal value; must be int, bool, or str
    """
    value: Value
    def __str__(self) -> str:
        return f"{self.value}"

@dataclass
class Eq():
    """AST node for equality comparison.

    Returns False if operands are of different types (no implicit coercion).
    For str, equality is character-by-character.

    Invariant: operands may be any Value type, but must match types to be equal.
    """
    left: Expr
    right: Expr
    def __str__(self):
        return f"({self.left} = {self.right})"

@dataclass
class Lt():
    """AST node for less-than comparison.

    Invariant: left and right must evaluate to int (not bool).
    """
    left: Expr
    right: Expr
    def __str__(self):
        return f"{self.left} < {self.right}"

@dataclass
class If():
    """AST node for conditional expression.

    Only the taken branch is evaluated (short-circuit).

    Invariant: boolopr must evaluate to bool.

    Params:
        boolopr:  condition expression
        thenexpr: evaluated if boolopr is True
        elseexpr: evaluated if boolopr is False
    """
    boolopr: Expr
    thenexpr: Expr
    elseexpr: Expr
    def __str__(self):
        return f"if {self.boolopr} then {self.thenexpr} else {self.elseexpr}"

@dataclass
class Fun():
    """AST node for anonymous lambda expression (future extension).

    Not currently reachable from the parser. Reserved for a planned lambda
    syntax (e.g., `fun x -> body`). evalInEnv handles Fun by returning a
    Closure directly, without binding a name.

    Params:
        arg:      parameter name
        bodyexpr: function body
    """
    arg: str
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"{self.arg} -> {self.bodyexpr}"

@dataclass
class Closure():
    """Runtime value representing a captured function environment.

    Created by Letfun (and Fun) during evaluation. Not an AST node --
    never appears in source programs, only as an eval result.

    The env field is patched post-construction in the Letfun case to
    enable recursion (c.env = newEnv after the Loc is created).

    Params:
        arg:      parameter name
        bodyexpr: function body (unevaluated)
        env:      captured lexical environment at point of closure creation
    """
    arg: str
    bodyexpr: Expr
    env: Env[Loc[Value]]

@dataclass
class Seq():
    """AST node for expression sequencing (e1 ; e2).

    Evaluates expr1 for side effects only; its value is discarded.
    Returns the value of expr2.

    Concrete syntax: expr1 ; expr2 (right-associative, lowest precedence)
    """
    expr1: Expr
    expr2: Expr
    def __str__(self) -> str:
        return f"({self.expr1}; {self.expr2})"

@dataclass
class Assign():
    """AST node for mutable variable assignment.

    Looks up name in the current environment, checks that the Loc does
    not hold a Closure (function names are not assignable), then mutates
    the Loc in place and returns the assigned value.

    Concrete syntax: name := expr

    Params:
        name: variable name; must be bound in the current environment
        expr: expression whose value is stored into the Loc
    Raises:
        EvalError: if name is unbound or refers to a function (Closure)
    """
    name: str
    expr: Expr
    def __str__(self) -> str:
        return f"{self.name} := {self.expr}"

@dataclass
class Show():
    """AST node for mid-evaluation output.

    Evaluates expr, prints the value to stdout (bare, no prefix or quotes),
    and returns the value so it can be used further in the expression.

    Concrete syntax: show expr
    """
    expr: Expr
    def __str__(self) -> str:
        return f"show {self.expr}"

@dataclass
class Read():
    """AST node for integer input from stdin.

    Prompts the user and reads a line, converting it to int.

    Concrete syntax: read (parsed as an ID and special-cased in ToExpr.id)

    Raises:
        EvalError: if the input cannot be parsed as an integer
    """
    def __str__(self) -> str:
        return "read"

@dataclass
class Reverse():
    """AST node for string reversal (Strings DSL).

    Pure operator -- returns a fresh reversed string, leaves original unchanged.

    Concrete syntax: reverse atom  (atom-level precedence)

    Invariant: expr must evaluate to str.
    """
    expr: Expr
    def __str__(self) -> str:
        return f"reverse {self.expr}"

@dataclass
class Uppercase():
    """AST node for string uppercasing (Strings DSL).

    Pure operator -- returns a fresh uppercased string, leaves original unchanged.

    Concrete syntax: uppercase atom  (atom-level precedence)

    Invariant: expr must evaluate to str.
    """
    expr: Expr
    def __str__(self) -> str:
        return f"uppercase {self.expr}"

@dataclass
class Lowercase():
    """AST node for string lowercasing (Strings DSL).

    Pure operator -- returns a fresh lowercased string, leaves original unchanged.

    Concrete syntax: lowercase atom  (atom-level precedence)

    Invariant: expr must evaluate to str.
    """
    expr: Expr
    def __str__(self) -> str:
        return f"lowercase {self.expr}"

# ---------------------------------------------------------------------------
# Environment model
# ---------------------------------------------------------------------------
# An environment is an immutable tuple of (name, Loc[Value]) bindings.
# Shadowing is supported: lookupEnv returns the first (innermost) match.
# All values in the environment are wrapped in Loc to support mutation
# via Assign without changing the environment structure itself.
# ---------------------------------------------------------------------------

type Binding[V] = tuple[str,V]         # always a (name, value) pair
type Env[V] = tuple[Binding[V], ...]   # arbitrary-length tuple of bindings

from typing import Any
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

def extendEnv[V](name: str, value: V, env: Env[V]) -> Env[V]:
    """Return a new environment extending env with a binding from name to value.

    The new binding is prepended, so it shadows any existing binding for name.

    Params:
        name:  variable name to bind
        value: value (typically a Loc[Value]) to associate with name
        env:   existing environment to extend

    Returns:
        A new Env with the new binding at the front
    """
    return ((name, value),) + env

class EnvError(Exception):
    pass

def lookupEnv[V](name: str, env: Env[V]) -> V:
    """Return the first value bound to name in env (innermost scope wins).

    Params:
        name: variable name to look up
        env:  environment to search

    Returns:
        The value (typically Loc[Value]) bound to name

    Raises:
        EnvError: if name has no binding in env
    """
    try:
        return next(v for (n, v) in env if n == name)
    except StopIteration:
        raise EnvError('name is not in environment: ' + name)

"""
# Alternative (simpler recursive version, kept for reference)
def lookupEnv[V](name: str, env: Env[V]) -> (V | None):
    match env:
        case ((n,v), *rest) :
            if n == name:
                return v
            else:
                return lookupEnv(name, rest) # type:ignore
        case _:
            return None
"""

# ---------------------------------------------------------------------------
# Location (Loc) -- mutable memory cell model
# ---------------------------------------------------------------------------
# A Loc is a singleton list [value], giving us a stable reference cell
# that can be mutated in place via setLoc without touching the environment.
# This mirrors how imperative languages store variables in mutable heap cells.
# ---------------------------------------------------------------------------

type Loc[V] = list[V]  # always a singleton list

def newLoc[V](value: V) -> Loc[V]:
    """Allocate a new mutable location holding value.

    Params:
        value: initial value to store

    Returns:
        A new Loc[V] (singleton list) containing value
    """
    return [value]

def getLoc[V](loc: Loc[V]) -> V:
    """Read the current value stored in loc.

    Params:
        loc: a Loc[V] (singleton list)

    Returns:
        The value currently stored in loc
    """
    return loc[0]

def setLoc[V](loc: Loc[V], value: V) -> None:
    """Mutate loc in place to store value.

    Params:
        loc:   a Loc[V] (singleton list) to update
        value: new value to store
    """
    loc[0] = value

# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class EvalError(Exception):
    pass

def eval(e: Expr) -> Value:
    """Evaluate expression e in the empty environment.

    Entry point for top-level evaluation. Delegates to evalInEnv.

    Params:
        e: AST expression to evaluate

    Returns:
        The Value produced by evaluating e

    Raises:
        EvalError: on type errors, unbound names, division by zero, etc.
    """
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[Loc[Value]], e: Expr) -> Value:
    """Evaluate expression e in environment env.

    Dispatches on the AST node type via structural pattern matching.
    All variable lookups dereference through Loc (getLoc).
    bool is a subtype of int in Python, so all arithmetic and comparison
    ops explicitly guard with isinstance(v, bool) to reject booleans.

    Params:
        env: current environment mapping names to Loc[Value]
        e:   AST expression to evaluate

    Returns:
        The Value produced by evaluating e

    Raises:
        EvalError: on type mismatches, unbound names, division by zero,
                   non-integer Read input, or assignment to a function name
    """
    match e:
        case Add(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    if isinstance(lv, bool) or isinstance(rv, bool):
                        raise EvalError("addition of non-integers")
                    return lv + rv
                case _:
                    raise EvalError("addition of non-intergers")
        case Sub(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    if isinstance(lv, bool) or isinstance(rv, bool):
                        raise EvalError("subtraction of non-integers")
                    return lv - rv
                case _:
                    raise EvalError("subtraction of non-integers")
        case Mul(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    if isinstance(lv, bool) or isinstance(rv, bool):
                        raise EvalError("multiplication of non-integers")
                    return lv * rv
                case _:
                    raise EvalError("multiplication of non-integers")
        case Div(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    if isinstance(lv, bool) or isinstance(rv, bool):
                        raise EvalError("division of non-integers")
                    if rv == 0:
                        raise EvalError("division by zero")
                    return lv // rv
                case _:
                    raise EvalError("division of non-integers")
        case Neg(s):
            match evalInEnv(env,s):
                case int(i):
                    if isinstance(i, bool):
                        raise EvalError("negation of non-integer")
                    return -i
                case _:
                    raise EvalError("negation of non-integer")
        case Or(l,r):
            lv = evalInEnv(env, l)
            match lv:
                case bool(True):
                    return True
                case bool(False):
                    rv = evalInEnv(env, r)
                    match rv:
                        case bool(rv):
                            return rv   
                        case _:
                            raise EvalError("or of non-bools")
                case _:
                    raise EvalError("or of non-bools")
        case And(l,r):
            lv = evalInEnv(env, l)
            match lv:
                case bool(False):
                    return False
                case bool(True):
                    rv = evalInEnv(env, r)
                    match rv:
                        case bool(rv):
                            return rv
                        case _:
                            raise EvalError("and of non-bools")
                case _:
                    raise EvalError("and of non-bools")
        case Not(s):
            match evalInEnv(env, s):
                case bool(sv):
                    return not sv
                case _:
                    raise EvalError("not of non-bool")
        case Lit(lit):
            match lit: #n-level matching keeps type-checking happy
                case bool(b):
                    return b
                case int(i):
                    return i
                case str(s):
                    return s
                case _:
                    raise EvalError("Unknow Literal type") 
        case Concat(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (str(lv), str(rv)):
                    return lv + rv
                case _:
                    raise EvalError("concatenation of non-string")
        case Replace(s, t, r):
            match (evalInEnv(env, s), evalInEnv(env, t), evalInEnv(env, r)):
                case (str(src), str(tgt), str(repl)):
                    if tgt not in src:
                        return src # target not found, return source unchanged
                    else:
                        return src.replace(tgt, repl, 1)
                case _: 
                    raise EvalError("Replace of non-string")
        case Name(n):
            try: 
                l = lookupEnv(n, env)
                return getLoc(l)
            except EnvError:
                raise EvalError(f"unbound name {n}")
        case Let(n,d,b):
            v = evalInEnv(env, d)
            l = newLoc(v)
            newEnv = extendEnv(n, l, env)
            return evalInEnv(newEnv, b)
        case Letfun(n,a,b,i):
            c = Closure(a,b,env)
            l = newLoc(c)
            newEnv = extendEnv(n,l,env)
            c.env = newEnv  # type: ignore 
            return evalInEnv(newEnv, i) # type: ignore
        case Fun(arg, bodyexpr):
            return Closure(arg,bodyexpr,env)
        case App(f,e):
            n = evalInEnv(env, f)
            a = evalInEnv(env, e)
            l = newLoc(a)
            match n:
                case Closure(arg,body,cenv):
                    newEnv = extendEnv(arg,l,cenv)
                    return evalInEnv(newEnv,body)
                case _:
                    raise EvalError("Applying a non-function.")
        case Eq(l, r):
            lv = evalInEnv(env, l)
            rv = evalInEnv(env, r)
            if type(lv) != type(rv):
                return False
            return lv == rv
        case Lt(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (int(lv), int(rv)):
                    if isinstance(lv, bool) or isinstance(rv, bool):
                        raise EvalError("less-than of non-integers")
                    return lv < rv
                case _:
                    raise EvalError("less-than of non-integers")
        case If(b, t, e):
            match evalInEnv(env, b):
                case bool(True):
                    return evalInEnv(env, t)
                case bool(False):
                    return evalInEnv(env, e)
                case _:
                    raise EvalError("condition is not a boolean")
        case Seq(e1,e2):
            evalInEnv(env, e1)
            return evalInEnv(env, e2)
        case Assign(n,e):
            try:
                l = lookupEnv(n, env)
            except EnvError:
                raise EvalError(f"unbound name {n}")
            match getLoc(l):
                case Closure():
                    raise EvalError("cannot assign to function name")
                case _:
                    v = evalInEnv(env, e)
                    setLoc(l, v)
                    return v
        case Show(e):
            v = evalInEnv(env, e)
            match v:
                case bool(b):
                    print(f"{b}")
                case int(i):
                    print(f"{i}")
                case str(s):
                    print(f'{s}')
                case Closure():
                    print("<function>")
            return v
        case Read():
            try: 
                v = int(input())
                return v
            except ValueError:
                raise EvalError(f"Input not an integer")
        case Reverse(e):
            s = evalInEnv(env,e)
            match s:
                case str(s):
                    return s[::-1]
                case _:
                    raise EvalError("reverse of non-string expression")
        case Uppercase(e):
            s = evalInEnv(env,e)
            match s:
                case str(s):
                    return s.upper()
                case _:
                    raise EvalError("uppercase of non-string expression")
        case Lowercase(e):
            s = evalInEnv(env,e)
            match s:
                case str(s):
                    return s.lower()
                case _:
                    raise EvalError("Lowercase of non-string expression")
        case _:
            raise EvalError(f"Unknow Expression type {e}")

def run(e: Expr) -> None:
    """Evaluate e and print its value to stdout.

    Top-level runner used by parse_run.py and the interp.py test suite.
    Prints the expression (via __str__) before evaluating, then prints
    the resulting value in a type-appropriate format. Catches and reports
    EvalError without propagating it, so the test suite continues running.

    Output format:
        bool    -> "True" or "False"
        int     -> decimal string
        str     -> bare string (no quotes)
        Closure -> "<function>"

    Params:
        e: AST expression to evaluate and display

    Raises:
        Does not raise; EvalError is caught and printed as "[!] EvalError: ..."
    """
    print(f"running {e}")
    try:
        match eval(e):
            case bool(b):
                print(f"{b}")
            case int(i):
                print(f"{i}")
            case str(s):
                print(f'{s}')
            case Closure():
                print("<function>")
    except EvalError as err:
        print(f"[!] EvalError: {err}")

"""
Domain-Specific Extension: Strings
This DSL extends the core language with string manipulation.
Values: Python strings (unicode)
Literals: Lit("string") - quoted string literals
Operators:
    - Concat(l, r): concatenates two strings
    - Replace(source, target, replacement): replaces first instance 
    of target in source with replacement
    - Reverse(expr): returns a new string with characters in reverse order
    - Uppercase(expr): returns a new string with all characters uppercased
    - Lowercase(expr): returns a new string with all characters lowercased
All operators are pure -- original strings are never mutated.
Equality: string equality is character-by-character (==)
"""

def main():
    # arithmetic
    a : Expr = Add(Lit(1), Lit(1))
    b : Expr = Mul(Lit(2), Add(Lit(1), Neg(Lit(1))))
    c : Expr = Let('x', Lit(2), Div(Lit(4), Name('x')))
    d : Expr = Div(Lit(1), Lit(0))                          # EvalError: division by zero

    # boolean
    e : Expr = Lit(True)
    f : Expr = Or(Lit(True), Lit(False))
    g : Expr = And(Lit(True), Lit(False))
    h : Expr = Let("x", Lit(True), Let("y", Name("x"), Not(Name("y"))))
    i : Expr = Or(Lit(1), Lit(False))                       # EvalError: or of non-bools

    # Comparisons and conditionals
    j : Expr = Eq(Lit(1), Lit(1))
    k : Expr = Lt(Lit(1), Lit(2))
    l : Expr = If(Eq(Lit(1), Lit(1)), Lit(1), Lit(0))

    # String DSL 
    m : Expr = Concat(Lit("Hello"), Lit("World"))
    n : Expr = Let("s", Lit("Hello"), Concat(Name("s"), Lit(" World")))
    o : Expr = Replace(Lit("Hello World!"), Lit("World"), Lit("Banana"))
    p : Expr = Replace(Lit("aabbaa"), Lit("aa"), Lit("xx"))  # first instance only
    q : Expr = Replace(Lit("Hello World"), Lit("xyz"), Lit("Banana"))  # target not found
    r : Expr = Concat(Lit(1), Lit("string"))                # EvalError: concatenation of non-string
    s : Expr = Replace(Lit("Hello"), Lit(1), Lit("x"))      # EvalError: replace of non-string

    t : Expr = If(Eq(Lit("condition"), Lit("condition")), Concat(Lit("yes"), Lit("!")), Lit("no"))

    x : Expr = Letfun("double", "x", Mul(Lit(2), Name("x")), App(Name("double"), Lit(5)))
        # expected: 10
    y : Expr = Letfun("fact", "n",
            If(Eq(Name("n"), Lit(0)),
            Lit(1),
            Mul(Name("n"), App(Name("fact"), Sub(Name("n"), Lit(1))))),
            App(Name("fact"), Lit(5)))
        # expected: 120

    # test: Expr = Seq(Assign("x", Lit(1)), Mul(Name("x"),Lit(2)))

    run(a)
    run(b)
    run(c)
    run(d)
    run(e)
    run(f)
    run(g)
    run(h)
    run(i)
    run(j)
    run(k)
    run(l)
    run(m)
    run(n)
    run(o)
    run(p)
    run(q)
    run(r)
    run(s)
    run(t) 
    run(x)
    run(y)
    # run(test) # Uncomment for testing/dev only

if __name__=="__main__":
    main()