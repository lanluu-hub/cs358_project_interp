# testing parser for core of milestone 2

import unittest
import interp
from interp import Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, \
    Let, Name, Eq, Lt, If, Letfun, App

from contextlib import redirect_stdout, redirect_stderr
with redirect_stdout(None), redirect_stderr(None):
    from parse_run import just_parse


class TestParsing(unittest.TestCase):
    def parse(self, concrete:str, expected):
        got = just_parse(concrete)
        self.assertEqual(
            got,
            expected,
            f'parser error: "{concrete}" got: {got} expected: {expected}'
        )

    def test_00(self):
        self.parse("false", Lit(False))

    def test_01(self):
        self.parse("true", Lit(True))

    def test_02(self):
        self.parse("xyz", Name("xyz"))

    def test_03(self):
        self.parse("123", Lit(123))

    def test_04(self):
        self.parse("123 + 456", Add(Lit(123), Lit(456)))

    def test_05(self):
        self.parse("123 - 456", Sub(Lit(123), Lit(456)))

    def test_06(self):
        self.parse("123 * 456", Mul(Lit(123), Lit(456)))

    def test_07(self):
        self.parse("123 / 456", Div(Lit(123), Lit(456)))

    def test_08(self):
        self.parse("-123", Neg(Lit(123)))

    def test_09(self):
        self.parse("x && y", And(Name("x"), Name("y")))

    def test_10(self):
        self.parse("x || y", Or(Name("x"),Name("y")))

    def test_11(self):
        self.parse("! x", Not(Name("x")) )

    def test_12(self):
        self.parse("x == y", Eq(Name("x"), Name("y")))

    def test_13(self):
        self.parse("x < y", Lt(Name("x"), Name("y")))

    def test_14(self):
        self.parse(
            "let x = 123 in x end",
            Let("x", Lit(123), Name("x")),
        )

    def test_15(self):
        self.parse(
            "if x then y else z",
            If(Name("x"), Name("y"), Name("z")),
        )

    def test_16(self):
          self.parse(
              "letfun f(x) = y in z end",
              Letfun("f", "x", Name("y"), Name("z")),
          )

    def test_17(self):
        self.parse("f(x)", App(Name("f"), Name("x")))

    def test_18(self):
        self.parse("(x)", Name("x"))

    def test_19(self):
        self.parse(
            "if x then y else z || w",
            If(Name("x"), Name("y"), Or(Name("z"), Name("w"))),
        )

    def test_20(self):
        self.parse(
            "x || y || z",
            Or(Or(Name("x"), Name("y")), Name("z")),
        )

    def test_21(self):
        self.parse(
            "x || y && z",
            Or(Name("x"), And(Name("y"), Name("z"))),
        )

    def test_22(self):
        self.parse(
            "x && y || z",
            Or(And(Name("x"), Name("y")), Name("z")),
        )

    def test_23(self):
        self.parse(
            "x && y && z",
            And(And(Name("x"), Name("y")), Name("z")),
        )

    def test_24(self):
        self.parse(
            "! x && y",
            And(Not(Name("x")), Name("y")),
        )

    def test_25(self):
        self.parse(
            "x && ! y",
            And(Name("x"), Not(Name("y"))),
        )

    def test_26(self):
        self.parse("x == y == z", None)

    def test_26_1(self):
        self.parse(
            "(x == y) == z",
            Eq(Eq(Name("x"), Name("y")), Name("z")),
        )

    def test_26_2(self):
        self.parse(
            "x == (y == z)",
            Eq(Name("x"), Eq(Name("y"), Name("z"))),
        )

    def test_27(self):
        self.parse("x == y < z", None)

    def test_27_1(self):
        self.parse(
            "(x == y) < z",
            Lt(Eq(Name("x"), Name("y")), Name("z")),
        )

    def test_27_2(self):
        self.parse(
            "x == (y < z)",
            Eq(Name("x"), Lt(Name("y"), Name("z"))),
        )

    def test_28(self):
        self.parse("x < y == z", None)

    def test_28_1(self):
        self.parse(
            "(x < y) == z",
            Eq(Lt(Name("x"), Name("y")), Name("z")),
        )

    def test_28_2(self):
        self.parse(
            "x < (y == z)",
            Lt(Name("x"), Eq(Name("y"), Name("z"))),
        )

    def test_29(self):
        self.parse("x < y < z", None)

    def test_29_1(self):
        self.parse(
            "(x < y) < z",
            Lt(Lt(Name("x"), Name("y")), Name("z")),
        )

    def test_29_2(self):
        self.parse(
            "x < (y < z)",
            Lt(Name("x"), Lt(Name("y"), Name("z"))),
        )

    def test_30(self):
        self.parse(
            "!x == y",
            Not(Eq(Name("x"), Name("y"))),
        )

    def test_30_1(self):
        self.parse(
            "(!x) == y",
            Eq(Not(Name("x")), Name("y")),
        )

    def test_31(self):
        self.parse("x == !y", None)

    def test_31_1(self):
        self.parse(
            "x == (!y)",
            Eq(Name("x"), Not(Name("y"))),
        )

    def test_32(self):
        self.parse(
            "!x < y",
            Not(Lt(Name("x"),Name("y"))),
        )

    def test_32_1(self):
        self.parse(
            "(!x) < y",
            Lt(Not(Name("x")), Name("y")),
        )

    def test_33(self):
        self.parse("x < !y", None)

    def test_33_1(self):
        self.parse(
            "x < (!y)",
            Lt(Name("x"), Not(Name("y"))),
        )

    def test_34(self):
        self.parse(
            "x + y + z",
            Add(Add(Name("x"), Name("y")), Name("z")),
        )

    def test_35(self):
        self.parse(
            "x + y - z",
            Sub(Add(Name("x"), Name("y")), Name("z")),
        )

    def test_36(self):
        self.parse(
            "x - y + z",
            Add(Sub(Name("x"), Name("y")), Name("z")),
        )

    def test_37(self):
        self.parse(
            "x - y - z",
            Sub(Sub(Name("x"), Name("y")), Name("z")),
        )

    def test_38(self):
        self.parse(
            "x + y < z",
            Lt(Add(Name("x"), Name("y")), Name("z")),
        )

    def test_39(self):
        self.parse(
            "x < y + z",
            Lt(Name("x"), Add(Name("y"), Name("z"))),
        )

    def test_40(self):
        self.parse(
            "x - y < z",
            Lt(Sub(Name("x"), Name("y")), Name("z")),
        )

    def test_41(self):
        self.parse(
            "x < y - z",
            Lt(Name("x"), Sub(Name("y"), Name("z"))),
        )

    def test_42(self):
        self.parse(
            "x + y == z",
            Eq(Add(Name("x"), Name("y")), Name("z")),
        )

    def test_43(self):
        self.parse(
            "x == y + z",
            Eq(Name("x"), Add(Name("y"), Name("z"))),
        )

    def test_44(self):
        self.parse(
            "x - y == z",
            Eq(Sub(Name("x"), Name("y")), Name("z")),
        )

    def test_45(self):
        self.parse(
            "x == y - z",
            Eq(Name("x"), Sub(Name("y"), Name("z"))),
        )

    def test_46(self):
        self.parse(
            "x * y * z",
            Mul(Mul(Name("x"), Name("y")), Name("z")),
        )

    def test_47(self):
        self.parse(
            "x * y / z",
            Div(Mul(Name("x"), Name("y")), Name("z")),
        )

    def test_48(self):
        self.parse(
            "x / y * z",
            Mul(Div(Name("x"), Name("y")), Name("z")),
        )

    def test_49(self):
        self.parse(
            "x / y / z",
            Div(Div(Name("x"), Name("y")), Name("z")),
        )

    def test_50(self):
        self.parse(
            "x * y + z",
            Add(Mul(Name("x"), Name("y")), Name("z")),
        )

    def test_51(self):
        self.parse(
            "x + y * z",
            Add(Name("x"), Mul(Name("y"), Name("z"))),
        )

    def test_52(self):
        self.parse(
            "x - y * z",
            Sub(Name("x"), Mul(Name("y"), Name("z"))),
        )

    def test_53(self):
        self.parse(
            "x * y - z",
            Sub(Mul(Name("x"), Name("y")), Name("z")),
        )

    def test_54(self):
        self.parse(
            "x + y / z",
            Add(Name("x"), Div(Name("y"), Name("z"))),
        )

    def test_55(self):
        self.parse(
            "x / y + z",
            Add(Div(Name("x"), Name("y")), Name("z")),
        )

    def test_56(self):
        self.parse(
            "x - y / z",
            Sub(Name("x"), Div(Name("y"), Name("z"))),
        )

    def test_57(self):
        self.parse(
            "x / y - z",
            Sub(Div(Name("x"), Name("y")), Name("z")),
        )

    def test_58(self):
        self.parse(
            "!!x",
            Not(Not(Name("x"))),
        )

    def test_59(self):
        self.parse(
            "--x",
            Neg(Neg(Name("x"))),
        )

    def test_60(self):
        self.parse(
            "x * -y",
            Mul(Name("x"), Neg(Name("y"))),
        )

    def test_61(self):
        self.parse(
            "-x * y",
            Mul(Neg(Name("x")), Name("y")),
        )

    def test_62(self):
        self.parse(
            "x / -y",
            Div(Name("x"), Neg(Name("y"))),
        )

    def test_63(self):
        self.parse(
            "-x / y",
            Div(Neg(Name("x")), Name("y")),
        )

    def test_64(self):
        self.parse(
            "- f(x)",
            Neg(App(Name("f"), Name("x"))),
        )

    def test_65(self):
        self.parse(
            "-23",
            Neg(Lit(23)),
        )

    def test_66(self):
        self.parse(
            "f(g)(x)",
            App(App(Name("f"), Name("g")), Name("x")),
        )

    def test_67(self):
        self.parse(
            "if if a then b else c then d else e",
            If(If(Name("a"), Name("b"), Name("c")), Name("d"), Name("e")),
        )

    def test_68(self):
        self.parse(
            "if a then if b then c else d else e",
            If(Name("a"), If(Name("b"), Name("c"), Name("d")), Name("e")),
        )

    def test_69(self):
        self.parse(
            "if a then b else if c then d else e",
            If(Name("a"), Name("b"), If(Name("c"), Name("d"), Name("e"))),
        )

    def test_70(self):
        self.parse(
            "if a || b then c else d",
            If(Or(Name("a"), Name("b")), Name("c"), Name("d")),
        )

    def test_71(self):
        self.parse(
            "if a then b || c else d",
            If(Name("a"), Or(Name("b"), Name("c")), Name("d")),
        )

    def test_72(self):
        self.parse(
            "if a then b else c || d",
            If(Name("a"), Name("b"), Or(Name("c"), Name("d"))),
        )

    def test_73(self):
        self.parse(
            "(if a then b else c)",
            If(Name("a"), Name("b"), Name("c")),
        )

    def test_74(self):
        self.parse(
            "true(false)",
            App(Lit(True), Lit(False)),
        )

    def test_75(self):
        self.parse(
            "let a = if b then c else d in e end",
            Let("a", If(Name("b"), Name("c"), Name("d")), Name("e")),
        )

    def test_76(self):
        self.parse(
            "letfun a(x) = if b then c else d in e end",
            Letfun("a", "x", If(Name("b"), Name("c"), Name("d")), Name("e")),
        )

    def test_77(self):
        self.parse(
            "let a = b in if c then d else e end",
            Let("a", Name("b"), If(Name("c"), Name("d"), Name("e"))),
        )

    def test_78(self):
        self.parse(
            "letfun a(x) = b in if c then d else e end",
            Letfun("a", "x", Name("b"), If(Name("c"), Name("d"), Name("e"))),
        )

    def test_80(self):
        self.parse(
            "a || let b = c in d end",
            Or(Name("a"), Let("b", Name("c"), Name("d"))),
        )

    def test_81(self):
        self.parse(
            "a || letfun b(x) = c in d end",
            Or(Name("a"), Letfun("b", "x", Name("c"), Name("d"))),
        )

    def test_82(self):
        self.parse(
            "let b = c || x in d end",
            Let("b", Or(Name("c"), Name("x")), Name("d")),
        )

    def test_83(self):
        self.parse(
            "letfun b(y) = c || x in d end",
            Letfun("b", "y", Or(Name("c"), Name("x")), Name("d")),
        )

    def test_84(self):
        self.parse(
            "let b = c in x || d end",
            Let("b", Name("c"), Or(Name("x"), Name("d"))),
        )

    def test_85(self):
        self.parse(
            "letfun b(y) = c in x || d end",
            Letfun("b", "y", Name("c"), Or(Name("x"), Name("d"))),
        )

    def test_86(self):
        self.parse(
            "f(x)(y)",
            App(App(Name("f"), Name("x")), Name("y")),
        )

class TestEval(unittest.TestCase):

    def eval_equal(self, expr, expected_result):
        result = interp.eval(expr)
        self.assertIs(type(result), type(expected_result))
        self.assertEqual(result, expected_result)

    def eval_except(self, expr):
        with self.assertRaises(BaseException):
            interp.eval(expr)

    def test_00(self):
        # !true
        #
        # => false
        self.eval_equal(
            Not(Lit(True)),
            False
        )

    def test_01(self):
        # !false
        #
        # => true
        self.eval_equal(
            Not(Lit(False)),
            True
        )

    def test_02(self):
        # !0
        #
        # => error
        self.eval_except(
            Not(Lit(0)),
        )

    def test_03(self):
        # !1
        #
        # => error
        self.eval_except(
            Not(Lit(1)),
        )

    def test_04(self):
        # !-1
        #
        # => error
        self.eval_except(
            Not(Lit(-1)),
        )

    def test_05(self):
        # !2
        #
        # => error
        self.eval_except(
            Not(Lit(2)),
        )

    def test_06(self):
        # (let x = 0 in letfun f(y) = x in f end end)(2)
        #
        # => 0
        self.eval_equal(
            App(Let("x", Lit(0), Letfun("f", "y", Name("x"), Name("f"))), Lit(2)),
            0,
        )

    def test_07(self):
        # letfun f(x) = x in let x in 0 in f(1) end end
        #
        # => 1
        self.eval_equal(
            Letfun("f", "x", Name("x"),
                   Let("x", Lit(0),
                       App(Name("f"), Lit(1)))),
            1,
        )

    def test_08(self):
        # (let x = 1 in letfun f(y) = x + y in f end end)(let x = 2 in 3 end)
        #
        # => 4
        self.eval_equal(
            App(Let("x", Lit(1),
                    Letfun("f", "y", Add(Name("x"), Name("y")),
                           Name("f"))),
                Let("x", Lit(2),
                    Lit(3))),
            4,
        )

    def test_09(self):
        # letfun f(x) = y in let y = 0 in f(y) end end
        #
        # => error
        self.eval_except(
            Letfun("f", "x", Name("y"),
                   Let("y", Lit(0),
                       App(Name("f"), Name("y")))),
        )

    def test_10(self):
        # letfun fac(x) = if x == 0 then 1 else x * fac(x - 1) in fac(3) end
        #
        # => 6
        self.eval_equal(
            Letfun("fac", "x", If(Eq(Name("x"), Lit(0)),
                                  Lit(1),
                                  Mul(Name("x"), App(Name("fac"), Sub(Name("x"), Lit(1))))),
                   App(Name("fac"), Lit(3))),
            6,
        )

    def test_11(self):
        # letfun y(f) =
        #   letfun g(x) =
        #     letfun h(v) = x(x)(v)
        #     in f(h) end
        #   in g(g) end
        # in letfun fac(r) =
        #      letfun g(x) = if x == 0 then 1 else x * r(x - 1)
        #      in g end
        #    in y(fac)(3) end
        # end
        #
        # => 6
        self.eval_equal(
            Letfun("y", "f",
                   Letfun("g", "x",
                          Letfun("h", "v",
                                 App(App(Name("x"), Name("x")), Name("v")),
                                 App(Name("f"), Name("h"))),
                          App(Name("g"), Name("g"))),
                   Letfun("fac", "r",
                          Letfun("g", "x",
                                 If(Eq(Name("x"), Lit(0)),
                                    Lit(1),
                                    Mul(Name("x"), App(Name("r"), Sub(Name("x"), Lit(1))))),
                                 Name("g")),
                          App(App(Name("y"), Name("fac")), Lit(3)))),
            6,
        )

    def test_12(self):
        # letfun f(x) = x / 0 in 10 end
        #
        # => 10
        self.eval_equal(
            Letfun("f", "x", Div(Name("x"), Lit(0)),
                   Lit(10)),
            10,
        )

    # If this test fails, you may have implemented multi-argument functions.
    # These tests expect single-argument functions.  You can fix this by
    # converting parameters/arguments to lists as necessary when evaluating
    # `Letfun` and `App`.
    def test_13(self):
        # letfun func(arg) = arg in func(0) end
        #
        # => 0
        self.eval_equal(
            Letfun("func", "arg", Name("arg"), App(Name("func"), Lit(0))),
            0,
        )

    def test_14(self):
        # let x = 1 in x + x end
        #
        # => 2
        self.eval_equal(
            Let("x", Lit(1), Add(Name("x"), Name("x"))),
            2,
        )

    def test_15(self):
        # 1 || false
        #
        # => error
        self.eval_except(
            Or(Lit(1), Lit(False)),
        )

    def test_16(self):
        # let x = (let x = 2 in x + x end) in x + x end
        # => 8
        self.eval_equal(
            Let("x",
                Let("x", Lit(2), Add(Name("x"), Name("x"))),
                Add(Name("x"), Name("x"))),
            8,
        )

    def test_17(self):
        # let x = 1 in let x = 2 in x end end
        # => 2
        self.eval_equal(
            Let("x", Lit(1), Let("x", Lit(2), Name("x"))),
            2,
        )

    def test_18(self):
        # let f = letfun f(x) = x + 2 in f end in f(2) end
        # => 4
        self.eval_equal(
            Let("f", Letfun("f", "x", Add(Name("x"), Lit(2)), Name("f")),
                App(Name("f"), Lit(2))),
            4,
        )

    def test_19(self):
        # let x = 1 in (let x = 2 in x end) + x end
        # => 3
        self.eval_equal(
            Let("x", Lit(1), Add(Let("x", Lit(2), Name("x")), Name("x"))),
            3,
        )

    def test_20(self):
        # (let x = 1 in x) + x end
        # => error
        self.eval_except(
            Add(Let("x", Lit(1), Name("x")), Name("x")),
        )


if __name__ == "__main__":
    unittest.main()
