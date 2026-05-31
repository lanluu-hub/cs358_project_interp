# testing parser for core of milestone 3

import unittest
import interp
from interp  import Expr, Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, \
                  Let, Name, Eq, Lt, If, Letfun, App, \
                  Read, Show, Assign, Seq


from io import StringIO
import re

import contextlib
from contextlib import redirect_stdout, redirect_stderr
with redirect_stdout(None), redirect_stderr(None):
    from parse_run import just_parse

class TestParsing(unittest.TestCase):
    def parse(self, concrete:str, expected:Expr|None):
        got = just_parse(concrete)
        self.assertEqual(
            got,
            expected,
            f'parser error: "{concrete}" got: {got} expected: {expected}')

    def test_0(self):
        self.parse("false", Lit(False))

    def test_1(self):
        self.parse("true", Lit(True))

    def test_2(self):
        self.parse("xyz", Name("xyz"))

    def test_3(self):
        self.parse("123", Lit(123))

    def test_4(self):
        self.parse("123 + 456", Add(Lit(123), Lit(456)))

    def test_5(self):
        self.parse("123 - 456", Sub(Lit(123), Lit(456)))

    def test_6(self):
        self.parse("123 * 456", Mul(Lit(123), Lit(456)))

    def test_7(self):
        self.parse("123 / 456", Div(Lit(123), Lit(456)))

    def test_8(self):
        self.parse("-123", Neg(Lit(123)))

    def test_9(self):
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
        self.parse("let x = 123 in x end", Let("x", Lit(123), Name("x")))

    def test_15(self):
        self.parse("if x then y else z", If(Name("x"), Name("y"), Name("z")))

    def test_16(self):
          self.parse("letfun f(x) = y in z end", Letfun("f", "x", Name("y"), Name("z")))

    def test_17(self):
        self.parse("read", Read())

    def test_18(self):
        self.parse("show x", Show(Name("x")))

    def test_19(self):
        self.parse("x := y", Assign("x", Name("y")))

    def test_20(self):
        self.parse("x; y", Seq(Name("x"), Name("y")))

    def test_21(self):
        self.parse("f(x)", App(Name("f"), Name("x")))

    def test_22(self):
        self.parse("(x)", Name("x"))

    def test_23(self):
        self.parse("x;y;z", Seq(Name("x"), Seq(Name("y"), Name("z"))))

    def test_24(self):
        self.parse("x := y; z", Seq(Assign("x", Name("y")), Name("z")))

    def test_25(self):
        self.parse("x; y:= z", Seq(Name("x"), Assign("y", Name("z"))) )

    def test_26(self):
        self.parse("show x; y", Seq(Show(Name("x")), Name("y")))

    def test_27(self):
        self.parse("x; show y", Seq(Name("x"), Show(Name("y"))))

    def test_28(self):
        self.parse("x := y; if x then y else z",
                   Seq(Assign("x", Name("y")), If(Name("x"), Name("y"), Name("z"))))

    def test_29(self):
        self.parse("if x then y else z; x := y",
                   Seq(If(Name("x"), Name("y"), Name("z")), Assign("x", Name("y"))))

    def test_30(self):
        self.parse("x := show y", Assign("x", Show(Name("y"))))

    def test_31(self):
        self.parse("show x := y", Show(Assign("x",Name("y"))))

    def test_32(self):
        self.parse("if x then y else show x",
                   If(Name("x"), Name("y"), Show(Name("x"))))

    def test_33(self):
        self.parse("show if x then y else z",
                     Show(If(Name("x"), Name("y"), Name("z"))))

    def test_34(self):
        self.parse("if x then y else z := 3",
                    If(Name("x"), Name("y"), Assign("z", Lit(3))))

    def test_35(self):
        self.parse("x := y || z",
                    Assign("x", Or(Name("y"), Name("z"))))

    def test_36(self):
        self.parse("show x || y",
                    Show(Or(Name("x"), Name("y"))))

    def test_37(self):
        self.parse("if x then y else z || w",
                    If(Name("x"), Name("y"), Or(Name("z"), Name("w"))))

    def test_38(self):
        self.parse("x || y || z",
                    Or(Or(Name("x"), Name("y")), Name("z")))

    def test_39(self):
        self.parse("x || y && z",
                    Or(Name("x"), And(Name("y"), Name("z"))))

    def test_40(self):
        self.parse("x && y || z",
                    Or(And(Name("x"), Name("y")), Name("z")))

    def test_41(self):
        self.parse("x && y && z",
                    And(And(Name("x"), Name("y")), Name("z")))

    def test_42(self):
        self.parse("! x && y",
                    And(Not(Name("x")), Name("y")))

    def test_43(self):
        self.parse("x && ! y",
                    And(Name("x"), Not(Name("y"))))

    def test_44(self):
        self.parse("x == y == z", None)

    def test_45(self):
        self.parse("x == y < z", None)

    def test_46(self):
        self.parse("x < y == z", None)

    def test_47(self):
        self.parse("x < y < z", None)

    def test_48(self):
        self.parse("!x == y",
                    Not(Eq(Name("x"), Name("y"))))

    def test_49(self):
        self.parse("x == !y", None)

    def test_50(self):
        self.parse("!x < y",
                    Not(Lt(Name("x"),Name("y"))))

    def test_51(self):
        self.parse("x < !y", None)

    def test_52(self):
        self.parse("x + y + z",
                    Add(Add(Name("x"), Name("y")), Name("z")))

    def test_53(self):
        self.parse("x + y - z",
                    Sub(Add(Name("x"), Name("y")), Name("z")))

    def test_54(self):
        self.parse("x - y + z",
                    Add(Sub(Name("x"), Name("y")), Name("z")))

    def test_55(self):
        self.parse("x - y - z",
                    Sub(Sub(Name("x"), Name("y")), Name("z")))

    def test_56(self):
        self.parse("x + y < z",
                    Lt(Add(Name("x"), Name("y")), Name("z")))

    def test_57(self):
        self.parse("x < y + z",
                    Lt(Name("x"), Add(Name("y"), Name("z"))))

    def test_58(self):
        self.parse("x - y < z",
                    Lt(Sub(Name("x"), Name("y")), Name("z")))

    def test_59(self):
        self.parse("x < y - z",
                    Lt(Name("x"), Sub(Name("y"), Name("z"))))

    def test_60(self):
        self.parse("x + y == z",
                    Eq(Add(Name("x"), Name("y")), Name("z")))

    def test_61(self):
        self.parse("x == y + z",
                    Eq(Name("x"), Add(Name("y"), Name("z"))))

    def test_62(self):
        self.parse("x - y == z",
                    Eq(Sub(Name("x"), Name("y")), Name("z")))

    def test_63(self):
        self.parse("x == y - z",
                    Eq(Name("x"), Sub(Name("y"), Name("z"))))

    def test_64(self):
        self.parse("x * y * z",
                    Mul(Mul(Name("x"), Name("y")), Name("z")))

    def test_65(self):
        self.parse("x * y / z",
                    Div(Mul(Name("x"), Name("y")), Name("z")))

    def test_66(self):
        self.parse("x / y * z",
                    Mul(Div(Name("x"), Name("y")), Name("z")))

    def test_67(self):
        self.parse("x / y / z",
                    Div(Div(Name("x"), Name("y")), Name("z")))

    def test_68(self):
        self.parse("x * y + z",
                    Add(Mul(Name("x"), Name("y")), Name("z")))

    def test_69(self):
        self.parse("x + y * z",
                    Add(Name("x"), Mul(Name("y"), Name("z"))))

    def test_70(self):
        self.parse("x - y * z",
                    Sub(Name("x"), Mul(Name("y"), Name("z"))))

    def test_71(self):
        self.parse("x * y - z",
                    Sub(Mul(Name("x"), Name("y")), Name("z")))

    def test_72(self):
        self.parse("x + y / z",
                    Add(Name("x"), Div(Name("y"), Name("z"))))

    def test_73(self):
        self.parse("x / y + z",
                    Add(Div(Name("x"), Name("y")), Name("z")))

    def test_74(self):
        self.parse("x - y / z",
                    Sub(Name("x"), Div(Name("y"), Name("z"))))

    def test_75(self):
        self.parse("x / y - z",
                    Sub(Div(Name("x"), Name("y")), Name("z")))

    def test_76(self):
        self.parse("!!x", Not(Not(Name("x"))))

    def test_77(self):
        self.parse("--x", Neg(Neg(Name("x"))))

    def test_78(self):
        self.parse("x * -y",
                    Mul(Name("x"), Neg(Name("y"))))

    def test_79(self):
        self.parse("-x * y",
                    Mul(Neg(Name("x")), Name("y")))

    def test_80(self):
        self.parse("x / -y",
                    Div(Name("x"), Neg(Name("y"))))

    def test_81(self):
        self.parse("-x / y",
                    Div(Neg(Name("x")), Name("y")))

    def test_82(self):
        self.parse("f(a;b)", App(Name("f"), Seq(Name("a"), Name("b"))))

    def test_83(self):
        self.parse("let x = a;b in c;d end",
                    Let("x", Seq(Name("a"), Name("b")), Seq(Name("c"), Name("d"))))

    def test_84(self):
        self.parse("letfun f(x) = a;b in c;d end",
                    Letfun("f", "x", Seq(Name("a"), Name("b")), Seq(Name("c"), Name("d"))))

    def test_85(self):
        self.parse("(a;b);c", Seq(Seq(Name("a"), Name("b")), Name("c")))

    def test_86(self):
        self.parse("- f(x)", Neg(App(Name("f"), Name("x"))))

    def test_87(self):
        self.parse("-23", Neg(Lit(23)))

    def test_88(self):
        self.parse("f(g)(x)", App(App(Name("f"), Name("g")), Name("x")))

    def test_89(self):
        self.parse("show(x)", Show(Name("x")))

    def test_90(self):
        self.parse(
            "if a; b then c else d",
            If(Seq(Name("a"), Name("b")), Name("c"), Name("d")),
        )

    def test_91(self):
        self.parse(
            "if a then b; c else d",
            If(Name("a"), Seq(Name("b"), Name("c")), Name("d")),
        )

    def test_92(self):
        self.parse(
            "if a then b else c; d",
            Seq(If(Name("a"), Name("b"), Name("c")), Name("d"))
        )

    def test_93(self):
        self.parse(
            "a := if b then c else d",
            Assign("a", If(Name("b"), Name("c"), Name("d"))),
        )

    def test_94(self):
        self.parse(
            "x := y := z",
            Assign("x", Assign("y", Name("z"))),
        )


# NOTE In order to pass the tests, the interpreter should ONLY print to stdout
# when evaluating a Read or Show.  Show needs to print for obvious reasons; Read
# will probably print a prompt when calling input().
#
# If you want to print debug messages, you can print to stderr instead of
# stdout.  To do this, put the following near the top of your file:
#
# from sys import stderr
#
# Then, when you want to print a debug message:
#
# print("some message", file=stderr)
#
# (Just make sure not to accidentally do this when evaluating Show.)
#
# If you want to make it even easier on yourself, you could do something like
# this:
#
# def debug(*args, **kwargs):
#     print(*args, **kwargs, file=stderr)
#
# and then just call debug() whenever you want to print debug output.


class redirect_stdin(contextlib._RedirectStream):
    # https://stackoverflow.com/questions/5062895/how-to-use-a-string-as-stdin/69228101#69228101
    #
    # Why isn't this in the stdlib?
    _stream = "stdin"


# XXX This is purely to make tests easier to read.
prompt = None


class TestEval(unittest.TestCase):
    def eval_with(self, expr, inputs):
        with redirect_stdin(StringIO("\n".join(inputs) + "\n")):
            return interp.eval(expr)

    def eval_equal(self, expr, expected_result, inputs=[], expected_outputs=None):
        out = StringIO()
        with redirect_stdout(out):
            result = self.eval_with(expr, inputs)
        self.assertIs(type(result), type(expected_result))
        self.assertEqual(result, expected_result)
        self.check_outputs(inputs, expected_outputs, out)

    def eval_except(self, lhs, inputs=[], expected_outputs=None):
        out = StringIO()
        with redirect_stdout(out):
            with self.assertRaises(BaseException):
                self.eval_with(lhs, inputs)
        self.check_outputs(inputs, expected_outputs, out)

    def check_outputs(self, inputs, expected_outputs, out):
        if expected_outputs is None:
            expected_outputs = len(inputs) * [prompt]
        # Checking the output is tricky, because input() prompts also get
        # printed to stdout, and we haven't mandated any particular prompt
        # string.  To get around this, we build a regular expression in
        # which every input prompt is matched by an arbitrary sequence of
        # non-newline characters.  This isn't a 100% solution, but I think
        # it's the best solution that's realistically possible without a
        # mandated prompt string.
        #
        # NOTE If you (yes, YOU, the person running the tests) want to
        # tighten things up, replace [^\n]* below with your input prompt.
        # That should make the tests 100% accurate and precise.
        r = re.compile(
            "^" +
            "".join(
                "[^\n]*" if o is prompt else f"{re.escape(o)}\n"
                for o in expected_outputs
            ) +
            "$"
        )
        out.seek(0)
        self.assertRegex(out.read(), r)

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
        # let x = 1 in letfun f(y) = x := y in f(2); x end end
        # => 2
        self.eval_equal(
            Let("x", Lit(1),
                Letfun("f", "y", Assign("x", Name("y")),
                       Seq(App(Name("f"), Lit(2)),
                           Name("x")))),
            2,
        )

    def test_13(self):
        # let x = 0 in letfun f(y) = x := x + y in f(1); f(2); f(3); f(4); x end end
        #
        # => 10
        self.eval_equal(
            Let("x", Lit(0),
                Letfun("f", "y", Assign("x", Add(Name("x"), Name("y"))),
                       Seq(App(Name("f"), Lit(1)),
                           Seq(App(Name("f"), Lit(2)),
                               Seq(App(Name("f"), Lit(3)),
                                   Seq(App(Name("f"), Lit(4)),
                                       Name("x"))))))),
            10,
        )

    def test_14(self):
        # x := 0
        #
        # => error
        self.eval_except(
            Assign("x", Lit(0))
        )

    def test_15(self):
        # letfun f(y) = let x := 0 in x := y end in f(1); x end
        #
        # => error
        self.eval_except(
            Letfun("f", "y",
                   Let("x", Lit(0), Assign("x", Name("y"))),
                   Seq(App(Name("f"), Lit(1)),
                       Name("x")))
        )

    def test_16(self):
        # let x = 0 in let y = x := 1 in y end end
        #
        # => 1
        self.eval_equal(
            Let("x", Lit(0),
                Let("y", Assign("x", Lit(1)),
                    Name("y"))),
            1
        )

    def test_17(self):
        # letfun f(x) = let y = 0 in x end
        # in f(1); y end
        #
        # => error
        self.eval_except(
            Letfun("f", "x",
                   Let("y", Lit(0), Name("x")),
                   Seq(App(Name("f"), Lit(1)),
                       Name("y")))
        )

    def test_18(self):
        # let x = 0 in x := 1 end
        #
        # => 1
        self.eval_equal(
            Let("x", Lit(0),
                Assign("x", Lit(1))),
            1
        )

    def test_19(self):
        # let x = 0 in x := true end
        #
        # => true
        self.eval_equal(
            Let("x", Lit(0),
                Assign("x", Lit(True))),
            True
        )

    def test_20(self):
        # let x = 2 in (x := if x == 2 then 3 else 4) + (x := 10) end
        #
        # => 13
        self.eval_equal(
            Let('x', Lit(2),
                Add(Assign('x', If(Eq(Name('x'), Lit(2)), Lit(3), Lit(4))),
                    Assign('x', Lit(10)))),
            13
        )

    def test_21(self):
        # read
        #
        # => 39
        #
        # inputs: 39
        self.eval_equal(Read(), 39, inputs=["39"])

    def test_22(self):
        # read
        #
        # => -67
        #
        # inputs: -67
        self.eval_equal(Read(), -67, inputs=["-67"])

    def test_23(self):
        # show -58
        #
        # => -58
        #
        # outputs: -58
        self.eval_equal(
            Show(Lit(-58)),
            -58,
            expected_outputs=["-58"],
        )

    def test_24(self):
        # show 86
        #
        # => 86
        #
        # inputs: 86
        #
        # outputs: 86
        self.eval_equal(
            Show(Lit(86)),
            86,
            expected_outputs=["86"],
        )

    def test_25(self):
        # show read
        #
        # => -22
        #
        # inputs: -22
        #
        # outputs: -22
        self.eval_equal(
            Show(Read()),
            -22,
            inputs=["-22"],
            expected_outputs=[prompt, "-22"],
        )

    def test_26(self):
        # show read
        #
        # => 14
        #
        # inputs: 14
        #
        # outputs: 14
        self.eval_equal(
            Show(Read()),
            14,
            inputs=["14"],
            expected_outputs=[prompt, "14"],
        )

    def test_27(self):
        # show true
        #
        # => true
        #
        # outputs: True
        self.eval_equal(
            Show(Lit(True)),
            True,
            expected_outputs=["True"],
        )

    def test_28(self):
        # show false
        #
        # => false
        #
        # outputs: False
        self.eval_equal(
            Show(Lit(False)),
            False,
            expected_outputs=["False"],
        )

    def test_29(self):
        # let x = 0 in (x := read; show x) + (x := read; show x) end
        #
        # => 3
        #
        # inputs: 1, 2
        #
        # outputs: 1, 2
        self.eval_equal(
            Let("x", Lit(0),
                Add(Seq(Assign("x", Read()), Show(Name("x"))),
                    Seq(Assign("x", Read()), Show(Name("x"))))),
            3,
            inputs=["1", "2"],
            expected_outputs=[prompt, "1", prompt, "2"],
        )

    def test_30(self):
        # letfun f(x) = x := x + x; show x in let x = 1 in f(x); x end end
        #
        # => 1
        #
        # outputs: 2
        self.eval_equal(
            Letfun("f", "x",
                   Seq(Assign("x", Add(Name("x"), Name("x"))),
                       Show(Name("x"))),
                   Let("x", Lit(1),
                       Seq(App(Name("f"), Name("x")), Name("x")))),
            1,
            expected_outputs=["2"],
        )

    def test_31(self):
        # let f = let x = 2 in letfun f(y) = x := x * y in f end end
        # in let x = 3 in show(f(4)); x end end
        #
        # => 3
        #
        # outputs: 8
        self.eval_equal(
            Let("f", Let("x", Lit(2),
                         Letfun("f", "y",
                                Assign("x", Mul(Name("x"), Name("y"))),
                                Name("f"))),
                Let("x", Lit(3),
                    Seq(Show(App(Name("f"), Lit(4))), Name("x")))),
            3,
            expected_outputs=["8"],
        )

    def test_32(self):
        # let fac =
        #   let acc = 1
        #   in letfun go(x) = if x == 0 then acc else (acc := acc * x; go(x - 1))
        #      in letfun fac(x) =
        #        let r = go(x) in acc := 1; r end
        #        in fac
        #        end
        #      end
        #   end
        # in show(fac(3)); show(fac(4))
        # end
        #
        # => 24
        #
        # outputs: 6, 24
        self.eval_equal(
            Let("fac", Let("acc", Lit(1),
                           Letfun("go", "x",
                                  If(Eq(Name("x"), Lit(0)),
                                     Name("acc"),
                                     Seq(Assign("acc", Mul(Name("acc"), Name("x"))),
                                         App(Name("go"), Sub(Name("x"), Lit(1))))),
                                  Letfun("fac", "x",
                                         Let("r", App(Name("go"), Name("x")),
                                             Seq(Assign("acc", Lit(1)), Name("r"))),
                                         Name("fac")))),
                Seq(Show(App(Name("fac"), Lit(3))),
                    Show(App(Name("fac"), Lit(4))))),
            24,
            expected_outputs=["6", "24"],
        )
        
    def test_33(self):
        # letfun fac(n) =
        #   let acc = 1 in
        #     letfun loop(n) =
        #       if n == 0 then acc else (
        #         acc := acc * n;
        #         loop(n - 1)
        #       )
        #     in
        #       loop(n)
        #     end
        #   end
        # in
        #   fac(3)
        # end
        #
        # => 120
        self.eval_equal(
            Letfun("fac", "n",
                   Let("acc", Lit(1),
                       Letfun("loop", "n",
                              If(Eq(Name("n"), Lit(0)),
                                 Name("acc"),
                                 Seq(Assign("acc", Mul(Name("acc"), Name("n"))),
                                     App(Name("loop"), Sub(Name("n"), Lit(1))))),
                              App(Name("loop"), Name("n")))),
                   App(Name("fac"), Lit(5))),
            120,
        )

    def test_34(self):
        # letfun b(n) =
        #   if n < 2 then
        #     show n
        #   else (
        #     b(n / 2);
        #     show (n - (n / 2) * 2)
        #   )
        # in
        #   b(42)
        # end
        #
        # => 0
        #
        # outputs: 1, 0, 1, 0, 1, 0
        self.eval_equal(
            Letfun("b", "n",
                   If(Lt(Name("n"), Lit(2)),
                      Show(Name("n")),
                      Seq(App(Name("b"), Div(Name("n"), Lit(2))),
                          Show(Sub(Name("n"), Mul(Div(Name("n"), Lit(2)), Lit(2)))))),
                   App(Name("b"), Lit(42))),
            0,
            expected_outputs=["1", "0", "1", "0", "1", "0"],
        )

    def test_35(self):
        # letfun f(x) = x in f := 1 end
        #
        # => error
        self.eval_except(
            Letfun("f", "x", Name("x"),
                   Assign("f", Lit(1)))
        )

    def test_36(self):
        # letfun f(x) = x / 0 in 10 end
        #
        # => 10
        self.eval_equal(
            Letfun("f", "x", Div(Name("x"), Lit(0)),
                   Lit(10)),
            10,
        )

    def test_37(self):
        # let f = letfun f(x) = x in f end
        # in f := 1
        # end
        #
        # => error
        self.eval_except(
            Let("f", Letfun("f", "x", Name("x"), Name("f")),
                Assign("f", Lit(1))),
        )

    def test_38(self):
        # let u = 1 in
        #   u := letfun f(x) = x in f end;
        #   u(3)
        # end
        #
        # => 3
        self.eval_equal(
            Let("u", Lit(1),
                Seq(Assign("u", Letfun("f", "x", Name("x"), Name("f"))),
                    App(Name("u"), Lit(3)))),
            3,
        )

    def test_39(self):
        # letfun nil(_) = 0 / 0 in
        # letfun pair(a) =
        #   letfun inner(b) =
        #     letfun dispatch(flag) = if flag then a else b
        #     in dispatch
        #   end
        #   in inner
        # end in
        # letfun head(xs) = xs(true) in
        # letfun tail(xs) = xs(false) in
        # letfun nth(n) =
        #   letfun inner(xs) =
        #     if n == 0 then
        #       head(xs)
        #     else (
        #       n := n - 1;
        #       inner(tail(xs))
        #     )
        #   in inner
        # end in
        # let xs = pair(5)(pair(4)(pair(3)(pair(2)(pair(1)(pair(0)(nil)))))) in
        # (show(nth(0)(xs));
        #  show(nth(1)(xs));
        #  show(nth(2)(xs)));
        # (show(nth(3)(xs));
        #  show(nth(4)(xs));
        #  show(nth(5)(xs)))
        # end end end end end end
        #
        # => 0
        #
        # ouputs: 5, 4, 3, 2, 1, 0
        self.eval_equal(
            Letfun("nil", "_", Div(Lit(0), Lit(0)),
                   Letfun("pair", "a",
                          Letfun("inner", "b",
                                 Letfun("dispatch", "flag",
                                        If(Name("flag"), Name("a"), Name("b")),
                                        Name("dispatch")),
                                 Name("inner")),
                          Letfun("head", "xs",
                                 App(Name("xs"), Lit(True)),
                                 Letfun("tail", "xs",
                                        App(Name("xs"), Lit(False)),
                                        Letfun("nth", "n",
                                               Letfun("inner", "xs",
                                                      If(Eq(Name("n"), Lit(0)),
                                                         App(Name("head"),
                                                             Name("xs")),
                                                         Seq(Assign("n", Sub(Name("n"), Lit(1))),
                                                             App(Name("inner"),
                                                                 App(Name("tail"),
                                                                     Name("xs"))))),
                                                      Name("inner")),
                                               Let("xs", App(App(Name("pair"), Lit(5)),
                                                             App(App(Name("pair"), Lit(4)),
                                                                 App(App(Name("pair"), Lit(3)),
                                                                     App(App(Name("pair"), Lit(2)),
                                                                         App(App(Name("pair"), Lit(1)),
                                                                             App(App(Name("pair"), Lit(0)),
                                                                                 Name("nil"))))))),
                                                   Seq(Seq(Show(App(App(Name("nth"), Lit(0)), Name("xs"))),
                                                           Seq(Show(App(App(Name("nth"), Lit(1)), Name("xs"))),
                                                               Show(App(App(Name("nth"), Lit(2)), Name("xs"))))),
                                                       Seq(Show(App(App(Name("nth"), Lit(3)), Name("xs"))),
                                                           Seq(Show(App(App(Name("nth"), Lit(4)), Name("xs"))),
                                                               Show(App(App(Name("nth"), Lit(5)), Name("xs")))))))))))),
            0,
            expected_outputs=["5", "4", "3", "2", "1", "0"],
        )

    def test_40(self):
        # show (show 0) + 1
        self.eval_equal(
            Show(Add(Show(Lit(0)), Lit(1))),
            1,
            expected_outputs=["0", "1"],
        )

    def test_41(self):
        # (read == 0) || (0 / 0)
        #
        # => true
        #
        # inputs: 0
        self.eval_equal(
            Or(Eq(Read(), Lit(0)),
               Div(Lit(0), Lit(0))),
            True,
            inputs=["0"],
        )

    def test_42(self):
        # true || read
        #
        # => true
        self.eval_equal(
            Or(Lit(True), Read()),
            True,
        )

    def test_43(self):
        # show false || (0 / 0)
        #
        # => error
        #
        # outputs: False
        self.eval_except(
            Or(Show(Lit(False)), Div(Lit(0), Lit(0))),
            expected_outputs=["False"],
        )

    def test_44(self):
        # read / show 0
        #
        # => error
        #
        # inputs: 1
        self.eval_except(
            Div(Read(), Show(Lit(0))),
            inputs=["1"],
        )

    def test_45(self):
        # read || read
        #
        # => error
        #
        # inputs: 1
        self.eval_except(
            Or(Read(), Read()),
            inputs=["1"],
        )

    # If this test fails, you may have implemented multi-argument functions.
    # These tests expect single-argument functions.  You can fix this by
    # converting parameters/arguments to lists as necessary when evaluating
    # `Letfun` and `App`.
    def test_46(self):
        # letfun func(arg) = arg in func(0) end
        #
        # => 0
        self.eval_equal(
            Letfun("func", "arg", Name("arg"), App(Name("func"), Lit(0))),
            0,
        )

    def test_47(self):
        # let x = 1 in x + x end
        #
        # => 2
        self.eval_equal(
            Let("x", Lit(1), Add(Name("x"), Name("x"))),
            2,
        )

    def test_48(self):
        # 1 || false
        #
        # => error
        self.eval_except(
            Or(Lit(1), Lit(False)),
        )

    def test_49(self):
        # read
        #
        # => error
        #
        # inputs: x
        self.eval_except(
            Read(),
            inputs=["x"],
        )

    def test_50(self):
        # let counter =
        #   let x = 0 in
        #     letfun counter(y) = x := x + y in counter end
        #   end
        # in counter(1); counter(1); counter(1) end
        #
        # => 3
        self.eval_equal(
            Let("counter",
                Let("x", Lit(0),
                    Letfun("counter", "y",
                           Assign("x", Add(Name("x"), Name("y"))),
                           Name("counter"))),
                Seq(App(Name("counter"), Lit(1)),
                    Seq(App(Name("counter"), Lit(1)),
                        App(Name("counter"), Lit(1))))),
            3
        )

if __name__ == "__main__":
    unittest.main()
