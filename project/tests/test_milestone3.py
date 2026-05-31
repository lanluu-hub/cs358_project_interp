"""
test_milestone3.py -- Unit tests for CS358 Interpreter Project Milestone 3

Covers:
  - Mutable variables (Loc, Assign)
  - Sequencing (Seq)
  - Show (returns value, side effect only)
  - Read (mocked via unittest.mock.patch)
  - String DSL: Concat (++), Replace, Reverse, Uppercase, Lowercase
  - Error cases: type errors, assign-to-function, unbound vars, bad Read input

Assumes your project layout:
  project/interp.py    -- AST nodes, eval, run, EvalError, Loc helpers
  project/parse_run.py -- parse_and_run, just_parse

Run from the repo root:
  python -m pytest tests/test_milestone3.py -v
  -- or --
  python tests/test_milestone3.py
"""

import sys
import os
import unittest
from unittest.mock import patch
from io import StringIO

# Make sure project/ is importable regardless of where pytest is invoked
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'project'))

from interp import (
    Lit, Add, Sub, Mul, Div, Neg,
    And, Or, Not,
    Eq, Lt, If,
    Let, Name,
    Letfun, App,
    Assign, Seq, Show, Read,
    Concat, Replace, Reverse, Uppercase, Lowercase,
    EvalError,
    newLoc, getLoc, setLoc,
    eval, run,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EMPTY_ENV = ()


def ev(expr):
    """Evaluate expr in an empty environment."""
    return eval(expr, EMPTY_ENV)


def ev_env(expr, env):
    return eval(expr, env)


# ---------------------------------------------------------------------------
# 1. Core arithmetic & booleans (sanity / regression)
# ---------------------------------------------------------------------------

class TestCoreArith(unittest.TestCase):

    def test_lit_int(self):
        self.assertEqual(ev(Lit(5)), 5)

    def test_lit_bool(self):
        self.assertTrue(ev(Lit(True)))
        self.assertFalse(ev(Lit(False)))

    def test_add(self):
        self.assertEqual(ev(Add(Lit(3), Lit(4))), 7)

    def test_sub(self):
        self.assertEqual(ev(Sub(Lit(10), Lit(3))), 7)

    def test_mul(self):
        self.assertEqual(ev(Mul(Lit(3), Lit(4))), 12)

    def test_div(self):
        self.assertEqual(ev(Div(Lit(10), Lit(2))), 5)

    def test_div_by_zero(self):
        with self.assertRaises(EvalError):
            ev(Div(Lit(1), Lit(0)))

    def test_neg(self):
        self.assertEqual(ev(Neg(Lit(5))), -5)

    def test_arith_type_error_bool_operand(self):
        # bool is subtype of int in Python, but your guards should reject it
        with self.assertRaises(EvalError):
            ev(Add(Lit(True), Lit(1)))

    def test_and_short_circuit(self):
        # Second branch would raise if evaluated; if And short-circuits it won't
        # We can't easily test the side-effect here, but at least it should return False
        self.assertFalse(ev(And(Lit(False), Lit(True))))

    def test_or_short_circuit(self):
        self.assertTrue(ev(Or(Lit(True), Lit(False))))

    def test_not(self):
        self.assertFalse(ev(Not(Lit(True))))

    def test_bool_type_error(self):
        with self.assertRaises(EvalError):
            ev(And(Lit(1), Lit(True)))

    def test_eq_int(self):
        self.assertTrue(ev(Eq(Lit(3), Lit(3))))
        self.assertFalse(ev(Eq(Lit(3), Lit(4))))

    def test_eq_cross_type(self):
        # int vs bool -- always unequal per spec
        self.assertFalse(ev(Eq(Lit(1), Lit(True))))

    def test_lt(self):
        self.assertTrue(ev(Lt(Lit(2), Lit(5))))
        self.assertFalse(ev(Lt(Lit(5), Lit(2))))

    def test_lt_type_error(self):
        with self.assertRaises(EvalError):
            ev(Lt(Lit(True), Lit(1)))

    def test_if_true_branch(self):
        self.assertEqual(ev(If(Lit(True), Lit(1), Lit(2))), 1)

    def test_if_false_branch(self):
        self.assertEqual(ev(If(Lit(False), Lit(1), Lit(2))), 2)

    def test_if_type_error(self):
        with self.assertRaises(EvalError):
            ev(If(Lit(1), Lit(1), Lit(2)))


# ---------------------------------------------------------------------------
# 2. Let / Name / Letfun / App
# ---------------------------------------------------------------------------

class TestBindings(unittest.TestCase):

    def test_let_basic(self):
        self.assertEqual(ev(Let('x', Lit(10), Name('x'))), 10)

    def test_let_shadow(self):
        expr = Let('x', Lit(1), Let('x', Lit(2), Name('x')))
        self.assertEqual(ev(expr), 2)

    def test_name_unbound(self):
        with self.assertRaises(EvalError):
            ev(Name('z'))

    def test_letfun_apply(self):
        # letfun f x = x + 1 in f 5 end  => 6
        expr = Letfun('f', 'x', Add(Name('x'), Lit(1)), App(Name('f'), Lit(5)))
        self.assertEqual(ev(expr), 6)

    def test_letfun_recursion(self):
        # factorial
        fact = Letfun(
            'fact', 'n',
            If(Eq(Name('n'), Lit(0)),
               Lit(1),
               Mul(Name('n'), App(Name('fact'), Sub(Name('n'), Lit(1))))),
            App(Name('fact'), Lit(5))
        )
        self.assertEqual(ev(fact), 120)

    def test_closure_captures_env(self):
        # let x = 10 in letfun f _ = x in f 0 end end  => 10
        expr = Let('x', Lit(10),
                   Letfun('f', '_', Name('x'),
                          App(Name('f'), Lit(0))))
        self.assertEqual(ev(expr), 10)


# ---------------------------------------------------------------------------
# 3. Mutable variables: Loc, Assign
# ---------------------------------------------------------------------------

class TestMutableVars(unittest.TestCase):

    def test_loc_helpers(self):
        loc = newLoc(42)
        self.assertEqual(getLoc(loc), 42)
        setLoc(loc, 99)
        self.assertEqual(getLoc(loc), 99)

    def test_assign_returns_value(self):
        # let x = 0 in x := 7 end  => 7
        expr = Let('x', Lit(0), Assign('x', Lit(7)))
        self.assertEqual(ev(expr), 7)

    def test_assign_mutates(self):
        # let x = 0 in x := 5; x end  => 5
        expr = Let('x', Lit(0), Seq(Assign('x', Lit(5)), Name('x')))
        self.assertEqual(ev(expr), 5)

    def test_assign_unbound_raises(self):
        with self.assertRaises(EvalError):
            ev(Assign('y', Lit(1)))

    def test_assign_to_function_raises(self):
        # letfun f x = x in f := 0 end  => EvalError
        expr = Letfun('f', 'x', Name('x'), Assign('f', Lit(0)))
        with self.assertRaises(EvalError):
            ev(expr)

    def test_assign_chained(self):
        # let x = 0 in x := 1; x := x + 1; x end  => 2
        expr = Let('x', Lit(0),
                   Seq(Assign('x', Lit(1)),
                       Seq(Assign('x', Add(Name('x'), Lit(1))),
                           Name('x'))))
        self.assertEqual(ev(expr), 2)


# ---------------------------------------------------------------------------
# 4. Seq
# ---------------------------------------------------------------------------

class TestSeq(unittest.TestCase):

    def test_seq_returns_second(self):
        self.assertEqual(ev(Seq(Lit(1), Lit(2))), 2)

    def test_seq_evaluates_first_for_side_effects(self):
        # let x = 0 in (x := 5); x end  => 5
        expr = Let('x', Lit(0), Seq(Assign('x', Lit(5)), Name('x')))
        self.assertEqual(ev(expr), 5)

    def test_seq_right_associative_semantics(self):
        # a ; (b ; c)  => value of c
        expr = Let('x', Lit(0),
                   Seq(Assign('x', Lit(1)),
                       Seq(Assign('x', Lit(2)), Name('x'))))
        self.assertEqual(ev(expr), 2)


# ---------------------------------------------------------------------------
# 5. Show
# ---------------------------------------------------------------------------

class TestShow(unittest.TestCase):

    def test_show_returns_value(self):
        # show 42  => 42  (and prints something, which we ignore)
        with patch('sys.stdout', new_callable=StringIO):
            result = ev(Show(Lit(42)))
        self.assertEqual(result, 42)

    def test_show_string_returns_value(self):
        with patch('sys.stdout', new_callable=StringIO):
            result = ev(Show(Lit("hello")))
        self.assertEqual(result, "hello")

    def test_show_prints_something(self):
        buf = StringIO()
        with patch('sys.stdout', buf):
            ev(Show(Lit(99)))
        self.assertIn('99', buf.getvalue())

    def test_show_in_seq(self):
        # show 1; show 2  => 2
        with patch('sys.stdout', new_callable=StringIO):
            result = ev(Seq(Show(Lit(1)), Show(Lit(2))))
        self.assertEqual(result, 2)


# ---------------------------------------------------------------------------
# 6. Read
# ---------------------------------------------------------------------------

class TestRead(unittest.TestCase):

    def test_read_integer(self):
        with patch('builtins.input', return_value='42'):
            result = ev(Read())
        self.assertEqual(result, 42)

    def test_read_non_integer_raises(self):
        with patch('builtins.input', return_value='abc'):
            with self.assertRaises(EvalError):
                ev(Read())

    def test_read_float_raises(self):
        with patch('builtins.input', return_value='3.14'):
            with self.assertRaises(EvalError):
                ev(Read())

    def test_read_result_usable(self):
        # read + 1  => 6  when user types 5
        with patch('builtins.input', return_value='5'):
            result = ev(Add(Read(), Lit(1)))
        self.assertEqual(result, 6)


# ---------------------------------------------------------------------------
# 7. String DSL -- Concat
# ---------------------------------------------------------------------------

class TestConcat(unittest.TestCase):

    def test_concat_basic(self):
        self.assertEqual(ev(Concat(Lit("hello"), Lit(" world"))), "hello world")

    def test_concat_empty(self):
        self.assertEqual(ev(Concat(Lit(""), Lit("abc"))), "abc")
        self.assertEqual(ev(Concat(Lit("abc"), Lit(""))), "abc")

    def test_concat_type_error_left(self):
        with self.assertRaises(EvalError):
            ev(Concat(Lit(1), Lit("a")))

    def test_concat_type_error_right(self):
        with self.assertRaises(EvalError):
            ev(Concat(Lit("a"), Lit(1)))

    def test_concat_chained(self):
        self.assertEqual(
            ev(Concat(Lit("a"), Concat(Lit("b"), Lit("c")))),
            "abc"
        )

    def test_concat_eq(self):
        self.assertTrue(ev(Eq(Concat(Lit("ab"), Lit("c")), Lit("abc"))))


# ---------------------------------------------------------------------------
# 8. String DSL -- Replace
# ---------------------------------------------------------------------------

class TestReplace(unittest.TestCase):

    def test_replace_basic(self):
        # replace "ll" with "rr" in "hello"  => "herro"
        self.assertEqual(ev(Replace(Lit("hello"), Lit("ll"), Lit("rr"))), "herro")

    def test_replace_first_only(self):
        # per spec: replaces FIRST instance
        self.assertEqual(ev(Replace(Lit("aaa"), Lit("a"), Lit("b"))), "baa")

    def test_replace_no_match(self):
        self.assertEqual(ev(Replace(Lit("hello"), Lit("xyz"), Lit("abc"))), "hello")

    def test_replace_empty_target(self):
        # replacing "" inserts at start (Python str.replace behavior)
        result = ev(Replace(Lit("hi"), Lit(""), Lit("_")))
        self.assertIsInstance(result, str)

    def test_replace_type_error(self):
        with self.assertRaises(EvalError):
            ev(Replace(Lit(42), Lit("a"), Lit("b")))

    def test_replace_is_pure(self):
        # original variable unchanged after replace
        expr = Let('s', Lit("hello"),
                   Seq(Replace(Name('s'), Lit("l"), Lit("r")),
                       Name('s')))
        self.assertEqual(ev(expr), "hello")


# ---------------------------------------------------------------------------
# 9. String DSL -- Reverse
# ---------------------------------------------------------------------------

class TestReverse(unittest.TestCase):

    def test_reverse_basic(self):
        self.assertEqual(ev(Reverse(Lit("abc"))), "cba")

    def test_reverse_empty(self):
        self.assertEqual(ev(Reverse(Lit(""))), "")

    def test_reverse_palindrome(self):
        self.assertEqual(ev(Reverse(Lit("racecar"))), "racecar")

    def test_reverse_type_error(self):
        with self.assertRaises(EvalError):
            ev(Reverse(Lit(123)))

    def test_reverse_is_pure(self):
        expr = Let('s', Lit("abc"),
                   Seq(Reverse(Name('s')), Name('s')))
        self.assertEqual(ev(expr), "abc")


# ---------------------------------------------------------------------------
# 10. String DSL -- Uppercase / Lowercase
# ---------------------------------------------------------------------------

class TestUppercaseLowercase(unittest.TestCase):

    def test_uppercase_basic(self):
        self.assertEqual(ev(Uppercase(Lit("hello"))), "HELLO")

    def test_uppercase_already_upper(self):
        self.assertEqual(ev(Uppercase(Lit("HELLO"))), "HELLO")

    def test_uppercase_mixed(self):
        self.assertEqual(ev(Uppercase(Lit("Hello World"))), "HELLO WORLD")

    def test_uppercase_type_error(self):
        with self.assertRaises(EvalError):
            ev(Uppercase(Lit(1)))

    def test_lowercase_basic(self):
        self.assertEqual(ev(Lowercase(Lit("HELLO"))), "hello")

    def test_lowercase_mixed(self):
        self.assertEqual(ev(Lowercase(Lit("Hello World"))), "hello world")

    def test_lowercase_type_error(self):
        with self.assertRaises(EvalError):
            ev(Lowercase(Lit(1)))

    def test_upper_then_lower(self):
        self.assertEqual(ev(Lowercase(Uppercase(Lit("Hello")))), "hello")

    def test_uppercase_is_pure(self):
        expr = Let('s', Lit("abc"),
                   Seq(Uppercase(Name('s')), Name('s')))
        self.assertEqual(ev(expr), "abc")


# ---------------------------------------------------------------------------
# 11. String DSL -- Equality
# ---------------------------------------------------------------------------

class TestStringEquality(unittest.TestCase):

    def test_eq_same(self):
        self.assertTrue(ev(Eq(Lit("abc"), Lit("abc"))))

    def test_eq_different(self):
        self.assertFalse(ev(Eq(Lit("abc"), Lit("xyz"))))

    def test_eq_cross_type_str_int(self):
        self.assertFalse(ev(Eq(Lit("1"), Lit(1))))

    def test_eq_empty_strings(self):
        self.assertTrue(ev(Eq(Lit(""), Lit(""))))


# ---------------------------------------------------------------------------
# 12. Integration: DSL + imperative features
# ---------------------------------------------------------------------------

class TestIntegration(unittest.TestCase):

    def test_concat_in_let(self):
        expr = Let('greeting', Lit("hello"),
                   Concat(Name('greeting'), Lit(" world")))
        self.assertEqual(ev(expr), "hello world")

    def test_mutable_string_accumulator(self):
        # let s = "a" in s := s ++ "b"; s := s ++ "c"; s end  => "abc"
        expr = Let('s', Lit("a"),
                   Seq(Assign('s', Concat(Name('s'), Lit("b"))),
                       Seq(Assign('s', Concat(Name('s'), Lit("c"))),
                           Name('s'))))
        self.assertEqual(ev(expr), "abc")

    def test_reverse_in_if(self):
        expr = If(Eq(Reverse(Lit("abc")), Lit("cba")), Lit(1), Lit(0))
        self.assertEqual(ev(expr), 1)

    def test_show_string_in_seq(self):
        with patch('sys.stdout', new_callable=StringIO):
            result = ev(Seq(Show(Lit("step1")), Lit("done")))
        self.assertEqual(result, "done")

    def test_read_into_string_op(self):
        # read an int, verify it's usable in arithmetic (not string ops)
        with patch('builtins.input', return_value='10'):
            result = ev(Mul(Read(), Lit(2)))
        self.assertEqual(result, 20)

    def test_letfun_with_string_arg(self):
        # letfun shout s = uppercase s in shout "quiet" end  => "QUIET"
        expr = Letfun('shout', 's', Uppercase(Name('s')),
                      App(Name('shout'), Lit("quiet")))
        self.assertEqual(ev(expr), "QUIET")

    def test_replace_in_let(self):
        expr = Let('template', Lit("hello world"),
                   Replace(Name('template'), Lit("world"), Lit("CS358")))
        self.assertEqual(ev(expr), "hello CS358")

    def test_full_pipeline(self):
        # Mimics a DSL pipeline:
        # let s = "Hello World" in
        #   let s = reverse (lowercase s) in
        #     s ++ "!"
        #   end
        # end
        # => "dlrow olleh!"
        expr = Let('s', Lit("Hello World"),
                   Let('s', Reverse(Lowercase(Name('s'))),
                       Concat(Name('s'), Lit("!"))))
        self.assertEqual(ev(expr), "dlrow olleh!")


# ---------------------------------------------------------------------------
# 13. Parser integration (parse_and_run / just_parse)
# ---------------------------------------------------------------------------

class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            from parse_run import parse_and_run, just_parse
            cls.parse_and_run = staticmethod(parse_and_run)
            cls.just_parse = staticmethod(just_parse)
            cls.available = True
        except ImportError:
            cls.available = False

    def skip_if_unavailable(self):
        if not self.available:
            self.skipTest("parse_run not importable")

    def test_just_parse_returns_ast(self):
        self.skip_if_unavailable()
        ast = self.just_parse("1 + 2")
        self.assertIsNotNone(ast)

    def test_just_parse_bad_syntax_returns_none(self):
        self.skip_if_unavailable()
        ast = self.just_parse("let in")
        self.assertIsNone(ast)

    def test_parse_and_run_arithmetic(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run("3 + 4")
        self.assertEqual(result, 7)

    def test_parse_and_run_concat(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('"hello" ++ " world"')
        self.assertEqual(result, "hello world")

    def test_parse_and_run_reverse(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('reverse "abc"')
        self.assertEqual(result, "cba")

    def test_parse_and_run_uppercase(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('uppercase "hello"')
        self.assertEqual(result, "HELLO")

    def test_parse_and_run_lowercase(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('lowercase "HELLO"')
        self.assertEqual(result, "hello")

    def test_parse_and_run_replace(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('replace "hello" "ll" with "rr"')
        self.assertEqual(result, "herro")

    def test_parse_and_run_assign(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('let x = 0 in x := 5 end')
        self.assertEqual(result, 5)

    def test_parse_and_run_seq(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('let x = 0 in x := 1; x end')
        self.assertEqual(result, 1)

    def test_parse_and_run_show(self):
        self.skip_if_unavailable()
        buf = StringIO()
        with patch('sys.stdout', buf):
            result = self.parse_and_run('show 42')
        self.assertEqual(result, 42)
        self.assertIn('42', buf.getvalue())

    def test_parse_and_run_if(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('if true then 1 else 2')
        self.assertEqual(result, 1)

    def test_parse_and_run_letfun(self):
        self.skip_if_unavailable()
        with patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run(
                'letfun double x = x + x in double 5 end'
            )
        self.assertEqual(result, 10)

    def test_parse_and_run_read(self):
        self.skip_if_unavailable()
        with patch('builtins.input', return_value='7'), \
             patch('sys.stdout', new_callable=StringIO):
            result = self.parse_and_run('read + 1')
        self.assertEqual(result, 8)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main(verbosity=2)
