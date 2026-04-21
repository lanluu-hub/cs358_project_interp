#TODO: Add header comment
#TODO: Add Bool ast Expr
#TODO: Add Let, Name
#TODO: Add Eval, EvalInEnv


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
    
def main():
    a : Expr = Add(Lit(1), Lit(1))
    b : Expr = Mul(Lit(2), Add(Lit(1), Neg(Lit(1))))
    c : Expr = Let('x', Lit(2), Div(Lit(4), Name('x')))

    print(a)
    print(b)
    print(c)

if __name__=="__main__":
    main()