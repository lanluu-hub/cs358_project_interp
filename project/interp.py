#TODO: Add header comment
#TODO: Add Eq, Lt, If


from dataclasses import dataclass
from unittest import case

type Literal = int | bool

type Expr = Add | Sub | Mul | Div | Neg | Or | And | Not | Let | Name | Lit | Eq | Lt | If

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
class Name():
    name: str
    def __str__(self) -> str:
        return self.name
    
@dataclass
class Lit():
    value: Literal
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

class EvalError(Exception):
    pass

def eval(e: Expr) -> Literal:
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[Literal], e: Expr) -> Literal:
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
                case int(i):
                    return i
                case bool(b):
                    return b
                #TODO: add for Bool and Str later
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v
        case Let(n,d,b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b)
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


def main():
    a : Expr = Add(Lit(1), Lit(1))
    b : Expr = Mul(Lit(2), Add(Lit(1), Neg(Lit(1))))
    c : Expr = Let('x', Lit(2), Div(Lit(4), Name('x')))
    d : Expr = Div(Lit(1), Lit(0))
    e : Expr = Lit(True)
    f : Expr = Or(Lit(True), Lit(False))
    g : Expr = And(Lit(True), Lit(False))
    h : Expr = Let("x", Lit(True), Let("y", Name("x"), Not(Name("y"))))
    i : Expr = If(Eq(Lit(1), Lit(1)), Lit(1), Lit(0))
    j : Expr = Eq(Lit(1), Lit(1))
    k : Expr = Lt(Lit(1), Lit(2))



    print(f"{a} = {eval(a)}")
    print(f"{b} = {eval(b)}")
    print(f"{c} = {eval(c)}")
    #print(f"{d} = {eval(d)}")  # this will raise EvalError, div by zero
    print(f"{e} = {eval(e)}")
    print(f"{f} = {eval(f)}")
    print(f"{g} = {eval(g)}")
    print(f"{h} = {eval(h)}")
    print(f"{i} = {eval(i)}")
    print(f"{j} = {eval(j)}")
    print(f"{k} = {eval(k)}")


if __name__=="__main__":
    main()