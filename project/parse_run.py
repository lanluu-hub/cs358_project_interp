# CS358 Principles of Programming Languages -- Spring 2026
# Project: Tree-Walking Interpreter (Strings DSL) -- Parser + Driver
# Author: Lan Luu
#
# This file wires together the Lark grammar (expr.lark) and the evaluator
# (interp.py). It defines:
#   - parse()          raw Lark parse, raises ParseError on failure
#   - ToExpr           Transformer: parse tree -> AST
#   - genAST()         applies ToExpr, surfaces AmbiguousParse
#   - parse_and_run()  full pipeline: parse -> AST -> eval -> print
#   - just_parse()     parse -> AST only (used by test3.py)
#   - driver()         interactive REPL for development
#   - main()           demo entry point (DSL + core demos)
#
# Parser: Earley with ambiguity='explicit'
#   Earley is used because the grammar contains constructs (show, app) that
#   create ambiguity the Earley parser can surface and resolve via _ambig.
#   LALR is available for unambiguity checking (see commented-out parser line).
#
# Ambiguity: show(x) can be parsed as Show(App) or App(show, x).
#   Resolved in _ambig by preferring the Show interpretation.
#   A grammar-level fix was not found under Earley.
#
# VERBOSE flag: set to True to print raw parse tree and AST during
#   parse_and_run / just_parse (useful during development).

import ast

from interp import Add, Sub, Mul, Div, Neg, \
                    And, Or, Not, Let, Letfun, \
                    App, Name, Lit, Eq, Lt, If, \
                    Expr, Concat, Replace, run, \
                    Seq, Assign, Show, Read, \
                    Reverse, Uppercase, Lowercase

from lark import Lark, Token, ParseTree, Transformer
from lark.exceptions import VisitError
from pathlib import Path
import readline  # type: ignore  # enables line editing and history in input()

VERBOSE = False
# VERBOSE = True  # uncomment for verbose parse tree / AST output

parser = Lark(Path('expr.lark').read_text(), start='expr', parser='earley', ambiguity='explicit')
# parser = Lark(Path('expr.lark').read_text(), start='expr', parser='lalr', strict=True)  # unambiguity check

class ParseError(Exception):
    pass

def parse(s: str) -> ParseTree:
    """Parse concrete syntax string s into a Lark parse tree.

    Params:
        s: concrete syntax string to parse

    Returns:
        A Lark ParseTree rooted at the 'expr' start rule

    Raises:
        ParseError: wrapping any Lark exception on parse failure
    """
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParseError(e)

class AmbiguousParse(Exception):
    pass

class ToExpr(Transformer[Token, Expr]):
    """Lark Transformer that folds a parse tree into an AST.

    Each method corresponds to a named (aliased) grammar rule and receives
    the already-transformed children as its argument. Leaf nodes arrive as
    Lark Token objects; their string content is in Token.value.

    Special cases handled here rather than in the grammar:
        - true / false / read are parsed as ID tokens and dispatched in id()
          (Earley ignores terminal priority, so keyword reservation via
          terminal priority does not work reliably)
        - show(x) ambiguity is resolved in _ambig() by preferring Show

    Raises:
        AmbiguousParse: via _ambig() if an ambiguous parse cannot be resolved
    """
    def plus(self, args: tuple[Expr, Expr]) -> Expr:
        return Add(args[0], args[1])

    def minus(self, args: tuple[Expr, Expr]) -> Expr:
        return Sub(args[0], args[1])

    def times(self, args: tuple[Expr, Expr]) -> Expr:
        return Mul(args[0], args[1])

    def divide(self, args: tuple[Expr, Expr]) -> Expr:
        return Div(args[0], args[1])

    def neg(self, args: tuple[Expr]) -> Expr:
        return Neg(args[0])

    def lor(self, args: tuple[Expr, Expr]) -> Expr:
        return Or(args[0], args[1])

    def land(self, args: tuple[Expr, Expr]) -> Expr:
        return And(args[0], args[1])

    def lnot(self, args: tuple[Expr]) -> Expr:
        return Not(args[0])

    def let(self, args: tuple[Token, Expr, Expr]) -> Expr:
        return Let(args[0].value, args[1], args[2])

    def id(self, args: tuple[Token]) -> Expr:
        """Convert an ID token to a Name, or special-case true/false/read.

        true and false are parsed as IDs (Earley ignores terminal priority)
        and converted to Lit(True)/Lit(False) here. read is converted to Read().

        Params:
            args: single-element tuple containing the ID Token

        Returns:
            Lit(True), Lit(False), Read(), or Name(n) depending on token value
        """
        match args[0].value:
            case "true":
                return Lit(True)
            case "false":
                return Lit(False)
            case "read":
                return Read()
            case n:
                return Name(n)

    def int(self, args: tuple[Token]) -> Expr:
        return Lit(int(args[0].value))

    def string(self, args: tuple[Token]) -> Expr:
        """Convert a quoted STRING token to Lit(str).

        Uses ast.literal_eval to handle escape sequences correctly.

        Params:
            args: single-element tuple containing the STRING Token
        """
        return Lit(ast.literal_eval(args[0].value))

    def concat(self, args: tuple[Expr, Expr]) -> Expr:
        return Concat(args[0], args[1])

    def repl(self, args: tuple[Expr, Expr, Expr]) -> Expr:
        return Replace(args[0], args[1], args[2])

    def equal(self, args: tuple[Expr, Expr]) -> Expr:
        return Eq(args[0], args[1])

    def less(self, args: tuple[Expr, Expr]) -> Expr:
        return Lt(args[0], args[1])

    def letfun(self, args: tuple[Token, Token, Expr, Expr]) -> Expr:
        return Letfun(args[0].value, args[1].value, args[2], args[3])

    def app(self, args: tuple[Expr, Expr]) -> Expr:
        return App(args[0], args[1])

    def if_(self, args: tuple[Expr, Expr, Expr]) -> Expr:
        return If(args[0], args[1], args[2])

    def seq(self, args: tuple[Expr, Expr]) -> Expr:
        return Seq(args[0], args[1])

    def assign(self, args: tuple[Token, Expr]) -> Expr:
        return Assign(args[0].value, args[1])

    def show(self, args: tuple[Expr]) -> Expr:
        return Show(args[0])

    def reverse(self, args: tuple[Expr]) -> Expr:
        return Reverse(args[0])

    def uppercase(self, args: tuple[Expr]) -> Expr:
        return Uppercase(args[0])

    def lowercase(self, args: tuple[Expr]) -> Expr:
        return Lowercase(args[0])

    def _ambig(self, alternatives: list) -> Expr:
        """Resolve Earley ambiguity by preferring the Show interpretation.

        Called by Lark when the Earley parser produces multiple parse trees
        for the same input (ambiguity='explicit'). The known ambiguous case
        is show(x), which can be parsed as Show(App(...)) or App(show, x).
        We prefer Show.

        Params:
            alternatives: list of already-transformed candidate AST nodes

        Returns:
            The Show node if one is present among the alternatives

        Raises:
            AmbiguousParse: if no Show node is found (unresolvable ambiguity)
        """
        for expr in alternatives:
            if isinstance(expr, Show):
                return expr
        raise AmbiguousParse()

def genAST(t: ParseTree) -> Expr:
    """Apply ToExpr to convert a Lark parse tree into an AST.

    Wraps the transformer call to unwrap Lark's VisitError and re-raise
    AmbiguousParse cleanly when the _ambig handler cannot resolve ambiguity.

    Params:
        t: Lark ParseTree (output of parse())

    Returns:
        The root AST Expr node

    Raises:
        AmbiguousParse: if the parse tree contains an unresolvable ambiguity
        VisitError:     re-raised for any other transformer error
    """
    try:
        return ToExpr().transform(t)
    except VisitError as e:
        if isinstance(e.orig_exc, AmbiguousParse):
            raise AmbiguousParse()
        else:
            raise e

def driver() -> None:
    """Interactive REPL for development and manual testing.

    Reads expressions line by line (supports multi-line input via trailing
    backslash continuation). For each input, prints the raw parse tree,
    pretty-printed parse tree, raw AST (repr), and the evaluated result.

    Exits cleanly on EOF (Ctrl-D). readline is imported at module level to
    enable line editing and history.
    """
    while True:
        try:
            s = input('expr: ')
            while s[-1] == '\\':
                s = s[:-1] + '\n' + input('... ')
            t = parse(s)
            print("raw:", t)
            print("pretty:")
            print(t.pretty())
            ast = genAST(t)
            print("raw AST:", repr(ast))  # repr() avoids __str__ pretty-printing
            run(ast)
        except AmbiguousParse:
            print("ambiguous parse")
        except ParseError as e:
            print("parse error:")
            print(e)
        except EOFError:
            break

def parse_and_run(s: str) -> None:
    """Parse, evaluate, and print the result of concrete expression string s.

    Full pipeline: string -> parse tree -> AST -> eval -> stdout.
    Errors are caught and printed; execution continues (does not raise).

    If VERBOSE is True, also prints the raw parse tree and raw AST repr.

    Params:
        s: concrete syntax expression string

    Raises:
        Does not raise; ParseError and AmbiguousParse are caught and printed.
    """
    try:
        t = parse(s)
        if VERBOSE:
            print("raw:", t)
            print("pretty:")
            print(t.pretty())
        ast = genAST(t)
        if VERBOSE:
            print("raw AST:", repr(ast))  # repr() avoids __str__ pretty-printing
        run(ast)
    except AmbiguousParse:
        print("ambiguous parse")
    except ParseError as e:
        print("parse error:")
        print(e)

def just_parse(s: str) -> Expr | None:
    """Parse concrete expression string s and return its AST, without evaluating.

    Used by the instructor test driver (test3.py) to test the parser
    independently of the evaluator.

    If VERBOSE is True, also prints the raw parse tree and raw AST repr.

    Params:
        s: concrete syntax expression string

    Returns:
        The root AST Expr node, or None if parsing or transformation fails

    Raises:
        Does not raise; ParseError and AmbiguousParse are caught, printed,
        and None is returned.
    """
    try:
        t = parse(s)
        if VERBOSE:
            print("raw:", t)
            print("pretty:")
            print(t.pretty())
        ast = genAST(t)
        if VERBOSE:
            print("raw AST:", repr(ast))  # repr() avoids __str__ pretty-printing
        return ast
    except AmbiguousParse:
        print("ambiguous parse")
        return None
    except ParseError as e:
        print("parse error:")
        print(e)
        return None

def unitTestSuite():
    # arithmetic
    parse_and_run("1 + 2")
    parse_and_run("let x = 2 in x * 3 end")
    parse_and_run("let x = 10 in let y = 2 in x / y end end")
    parse_and_run("-(3 + 4)")

    # boolean
    parse_and_run("true && false")
    parse_and_run("!true || false")
    parse_and_run("!(true && false)")

    # comparisons and conditionals
    parse_and_run("1 == 1")
    parse_and_run("1 < 2")
    parse_and_run("if 1 == 1 then 1 else 0")
    parse_and_run("if 1 < 2 then true else false")

    # functions
    parse_and_run("letfun double(x) = x * 2 in double(5) end")
    parse_and_run("letfun fact(n) = if n == 0 then 1 else n * fact(n - 1) in fact(5) end")

    # string DSL
    parse_and_run('"hello" ++ " world"')
    parse_and_run('"hello" ++ " " ++ "world"')
    parse_and_run('let s = "hello" in s ++ " world" end')
    parse_and_run('replace "hello world" "world" with "banana"')
    parse_and_run('replace "aabbaa" "aa" with "xx"')   # first instance only
    parse_and_run('replace "hello" "xyz" with "banana"')  # target not found
    parse_and_run('let s = reverse "abc" in s end')
    parse_and_run('uppercase "abc"')
    parse_and_run('lowercase "AbC"')

    # DSL + core combined
    parse_and_run('if "hello" == "hello" then "yes" else "no"')
    parse_and_run('if "hello" ++ " world" == "hello world" then true else false')
    parse_and_run('letfun greet(x) = "hello " ++ x in greet("world") end')

    # error cases
    parse_and_run("1 + true")       # EvalError: addition of non-integers
    parse_and_run("1 / 0")          # EvalError: division by zero
    
    # type error cases - strings
    parse_and_run('"hello" ++ 1')           # EvalError: concatenation of non-string
    parse_and_run('replace 1 "a" with "b"') # EvalError: replace of non-string
    parse_and_run('"hello" + "world"')      # EvalError: addition of non-integers

    # type error cases - boolean
    parse_and_run('1 && true')              # EvalError: and of non-bools
    parse_and_run('"hello" || false')       # EvalError: or of non-bools
    parse_and_run('!1')                     # EvalError: not of non-bool

    # type error cases - comparison
    parse_and_run('1 < true')              # EvalError: less-than of non-integers
    parse_and_run('"hello" < "world"')     # EvalError: less-than of non-integers

    # parse error cases
    parse_and_run('1 +')                   # ParseError: incomplete expression
    parse_and_run('let x = in x end')      # ParseError: missing definition

def demoDSL():
    parse_and_run(
        'show "DSL DEMO"; \
        letfun greet(x) = "hello, " ++ x in \
        let s = greet("world") in \
        let t = reverse s in \
        let u = uppercase t in \
        show "this is s:"; show s; \
        show "this is t:"; show t; \
        show "this is uppercase t:"; show u \
        end end end end'
    )
    parse_and_run('replace "hello world" "world" with "python"')

def demoCore():
    parse_and_run('show "CORE DEMO"; \
                  show "enter a number:"; \
                  letfun fact(n) = \
                    if n == 0 \
                        then 1 \
                        else n * fact(n - 1) \
                  in let x = read in show x; fact(x) end end') 
    
    parse_and_run('show "MUTATION DEMO"; \
                  let x = 0 in \
                    show x; \
                    x := x + 1; \
                    show x; \
                    x := x + 1; \
                    show x \
                  end')

def main():
    demoDSL()     # demo DSL
    demoCore()    # demo Core interp (int, bool,...) 
    # unitTestSuite()
    pass
    
if __name__ == "__main__":
    # main()      # Demo tests
    # driver()    # Uncomment for testing/dev
    pass