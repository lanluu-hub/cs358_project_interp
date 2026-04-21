#TODO: Add header comment
#TODO: Add Bool ast Expr


from dataclasses import dataclass

type Literal = int

type Expr = Add | Sub | Mul | Div | Neg | Let | Name | Lit

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
                    return lv + rv
                case _:
                    raise EvalError("addition of non-intergers")
        case Sub(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    return lv - rv
                case _:
                    raise EvalError("subtraction of non-integers")
        case Mul(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    return lv * rv
                case _:
                    raise EvalError("multiplication of non-integers")
        case Div(l,r):
            match (evalInEnv(env, l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    if rv == 0:
                        raise EvalError("division by zero")
                    return lv // rv
                case _:
                    raise EvalError("division of non-integers")
        case Neg(s):
            match evalInEnv(env,s):
                case int(i):
                    return -i
                case _:
                    raise EvalError("negation of non-integer")
        case Lit(lit):
            match lit: #n-level matching keeps type-checking happy
                case int(i):
                    return i
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

def main():
    a : Expr = Add(Lit(1), Lit(1))
    b : Expr = Mul(Lit(2), Add(Lit(1), Neg(Lit(1))))
    c : Expr = Let('x', Lit(2), Div(Lit(4), Name('x')))
    d : Expr = Div(Lit(1), Lit(0))

    print(f"{a} = {eval(a)}")
    print(f"{b} = {eval(b)}")
    print(f"{c} = {eval(c)}")
    #print(f"{d} = {eval(d)}")  # this will raise EvalError, div by zero

if __name__=="__main__":
    main()