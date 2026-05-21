# CS358 Interpreter
# Domain: Strings DSL
# Author: Lan Luu
#   Milestone 1 - due April 26

from dataclasses import dataclass

type Value = int | bool | str | Closure

type Expr = Add | Sub | Mul | Div | Neg | Or | And | Not | Let | Letfun | Fun | App | Name | Concat | Replace | Lit | Eq | Lt | If | Seq 

@dataclass
class Add():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"
    
@dataclass
class Sub():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} - {self.right})"
    
@dataclass
class Mul():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"
    
@dataclass
class Div():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} / {self.right})"
    
@dataclass
class Neg():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(- {self.subexpr})"
    
@dataclass
class Or():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} or {self.right})"
    
@dataclass
class And():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} and {self.right})"
    
@dataclass
class Not():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(not {self.subexpr})"
    
@dataclass
class Let():
    name: str
    defexpr: Expr
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})" 
    
@dataclass
class Letfun():
    name: str
    arg: str
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name}({self.arg}) = {self.bodyexpr} in {self.inexpr} end"

@dataclass
class App():
    fexpr: Expr
    arg: Expr
    def __str__(self) -> str:
        return f"{self.fexpr}({self.arg})"

@dataclass
class Name():
    name: str
    def __str__(self) -> str:
        return self.name
    
@dataclass
class Concat():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"(concatenate {self.left} {self.right})"
    
@dataclass
class Replace():
    source: Expr
    target: Expr
    replacement: Expr
    def __str__(self) -> str:
        return f"(replace {self.source} {self.target} with {self.replacement})"

@dataclass
class Lit():
    value: Value
    def __str__(self) -> str:
        return f"{self.value}"
    
@dataclass
class Eq():
    left: Expr
    right: Expr
    def __str__(self):
        return f"({self.left} = {self.right})"

@dataclass
class Lt():
    left: Expr
    right: Expr
    def __str__(self):
        return f"{self.left} < {self.right}"

@dataclass
class If():
    boolopr: Expr
    thenexpr: Expr
    elseexpr: Expr
    def __str__(self):
        return f"if {self.boolopr} then {self.thenexpr} else {self.elseexpr}"
    
@dataclass
class Fun():
    arg: str
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"{self.arg} -> {self.bodyexpr}"

@dataclass
class Closure():
    arg: str
    bodyexpr: Expr
    env: Env[Loc[Value]]

@dataclass
class Seq():
    expr1: Expr
    expr2: Expr
    def __str__(self) -> str:
        return f"({self.expr1}; {self.expr2})" 

# Eval
type Binding[V] = tuple[str,V] # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # This tuple type has arbitrary length

from typing import Any
emptyEnv : Env[Any] = () # the empty enviroment has no bindings

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Return a new environment that extends the input environment env with a new binding from name to value'''
    return ((name,value),) + env
    
class EnvError(Exception):
    pass

def lookupEnv[V](name: str, env: Env[V]) -> V :
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    try:
        return next(v for (n,v) in env if n == name)   # use handy generator expression to search for name
    except StopIteration:
        raise EnvError('name is not in environment: ' + name)        

"""
# Alternative (simplier)
def lookupEnv[V](name: str, env: Env[V]) -> (V | None):
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    match env:
        case ((n,v), *rest) :
            if n == name:
                return v
            else:
                return lookupEnv(name, rest) # type:ignore
        case _:
            return None
"""
# model memory locations as (mutable) singleton lists
type Loc[V] = list[V] # always a singleton list
def newLoc[V](value: V) -> Loc[V]:
    return [value]
def getLoc[V](loc: Loc[V]) -> V:
    return loc[0]
def setLoc[V](loc: Loc[V], value: V) -> None:
    loc[0] = value

class EvalError(Exception):
    pass

def eval(e: Expr) -> Value:
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[Loc[Value]], e: Expr) -> Value:
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
        case _:
            raise EvalError(f"Unknow Expression type {e}")

def run(e: Expr) -> None:
    print(f"running {e}")
    try:
        match eval(e):
            case bool(b):
                print(f"result: {b}")
            case int(i):
                print(f"result: {i}")
            case str(s):
                print(f'result: "{s}"')
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

    test: Expr = Seq(Add(Lit(1), Lit(1)), Mul(Lit(2),Lit(2)))

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
    run(test)

if __name__=="__main__":
    main()