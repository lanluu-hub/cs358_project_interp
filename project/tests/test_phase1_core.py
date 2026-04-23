import unittest
from unittest import TestCase

import contextlib
with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
    import interp
    from interp import Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Let, Name, Eq, Lt, If


class TestEval(TestCase):
    def expect(self, expr, expected):
        try:
            got = interp.eval(expr)
        except BaseException as e:
            self.fail(f"eval({expr}) threw {type(e).__name__} (should be {expected})")
        self.assertEqual(got, expected, expr)

    def expect_error(self, expr):
        with self.assertRaises(BaseException, msg=expr):
            interp.eval(expr)

    def test_lit_true(self):
        # true
        # => true
        expr = Lit(False)
        self.expect(expr, False)

    def test_lit_false(self):
        # false
        # => false
        expr = Lit(False)
        self.expect(expr, False)

    def test_lit_int(self):
        # 11
        # => 11
        expr = Lit(11)
        self.expect(expr, 11)

    def test_add(self):
        # 44 + 92
        # => 136
        expr = Add(Lit(44), Lit(92))
        self.expect(expr, 136)

    def test_add_lhs_type_error(self):
        # false + -69
        # => error
        expr = Add(Lit(False), Lit(-69))
        self.expect_error(expr)

    def test_add_rhs_type_error(self):
        # 34 + true
        # => error
        expr = Add(Lit(34), Lit(True))
        self.expect_error(expr)

    def test_sub(self):
        # 15 - -27
        # => 42
        expr = Sub(Lit(15), Lit(-27))
        self.expect(expr, 42)

    def test_sub_lhs_type_error(self):
        # false - 87
        # => error
        expr = Sub(Lit(False), Lit(87))
        self.expect_error(expr)

    def test_sub_rhs_type_error(self):
        # -90 - true
        # => error
        expr = Sub(Lit(-90), Lit(True))
        self.expect_error(expr)

    def test_mul(self):
        # -34 * -73
        # => 2482
        expr = Mul(Lit(-34), Lit(-73))
        self.expect(expr, 2482)

    def test_mul_lhs_type_error(self):
        # false * -89
        # => error
        expr = Mul(Lit(False), Lit(-89))
        self.expect_error(expr)

    def test_mul_rhs_type_error(self):
        # -74 * true
        # => error
        expr = Mul(Lit(-74), Lit(True))
        self.expect_error(expr)

    def test_div(self):
        # 38 / -13
        # => -3
        expr = Div(Lit(38), Lit(-13))
        self.expect(expr, -3)

    def test_div_lhs_type_error(self):
        # false / 74
        # => error
        expr = Div(Lit(False), Lit(74))
        self.expect_error(expr)

    def test_div_rhs_type_error(self):
        # 51 * true
        # => error
        expr = Div(Lit(51), Lit(True))
        self.expect_error(expr)

    def test_div_zero(self):
        # -67 / 0
        # => error
        expr = Div(Lit(-67), Lit(0))
        self.expect_error(expr)

    def test_neg(self):
        # -13
        # => -13
        expr = Neg(Lit(13))
        self.expect(expr, -13)

    def test_neg_type_error(self):
        # - false
        # => error
        expr = Neg(Lit(False))
        self.expect_error(expr)

    def test_and(self):
        # true and true
        # => true
        expr = And(Lit(True), Lit(True))
        self.expect(expr, True)
        # true and false
        # => false
        expr = And(Lit(True), Lit(False))
        self.expect(expr, False)
        # false and true
        # => false
        expr = And(Lit(False), Lit(True))
        self.expect(expr, False)
        # false and false
        # => false
        expr = And(Lit(False), Lit(False))
        self.expect(expr, False)

    def test_and_lhs_type_error(self):
        # 98 and true
        # => error
        expr = And(Lit(98), Lit(True))
        self.expect_error(expr)

    def test_and_rhs_type_error(self):
        # true and 24
        # => error
        expr = And(Lit(True), Lit(24))
        self.expect_error(expr)

    def test_and_short_circuit_error(self):
        # false and -16 / 0
        # => false
        expr = And(Lit(False), Div(Lit(-16), Lit(0)))
        self.expect(expr, False)

    def test_and_short_circuit_type_error(self):
        # false and 86
        # => false
        expr = And(Lit(False), Lit(86))
        self.expect(expr, False)

    def test_or(self):
        # true or true
        # => true
        expr = Or(Lit(True), Lit(True))
        self.expect(expr, True)
        # true or false
        # => true
        expr = Or(Lit(True), Lit(False))
        self.expect(expr, True)
        # false or true
        # => true
        expr = Or(Lit(False), Lit(True))
        self.expect(expr, True)
        # false or false
        # => false
        expr = Or(Lit(False), Lit(False))
        self.expect(expr, False)

    def test_or_lhs_type_error(self):
        # 29 or false
        # => error
        expr = Or(Lit(29), Lit(False))
        self.expect_error(expr)

    def test_or_rhs_type_error(self):
        # false or -45
        # => error
        expr = Or(Lit(False), Lit(-45))
        self.expect_error(expr)

    def test_or_short_circuit_error(self):
        # true or 99 / 0
        # => true
        expr = Or(Lit(True), Div(Lit(99), Lit(0)))
        self.expect(expr, True)

    def test_or_short_circuit_type_error(self):
        # true or 4
        # => true
        expr = Or(Lit(True), Lit(4))
        self.expect(expr, True)

    def test_not(self):
        # not true
        # => false
        expr = Not(Lit(True))
        self.expect(expr, False)
        # not false
        # => true
        expr = Not(Lit(False))
        self.expect(expr, True)

    def test_not_type_error(self):
        # not -40
        # => error
        expr = Not(Lit(-40))
        self.expect_error(expr)

    def test_let(self):
        # let x = 2 in x
        # => 2
        expr = Let('x',
                   Lit(2),
                   Name('x')
                   )
        self.expect(expr, 2)

    def test_name_bare_error(self):
        # x
        # => error
        expr = Name('x')
        self.expect_error(expr)
        
    def test_lets(self):
        # let x = 1 in let y = 2 in y - x
        # => 1
        expr = Let('x',
                   Lit(1),
                   Let('y',
                       Lit(2),
                       Sub(Name('y'),
                           Name('x')
                           )
                       )
                   )
        self.expect(expr, 1)

    def test_lets_error(self):
        # let x = 1 in y
        # => error
        expr = Let('x',
                   Lit(1),
                   Name('y')
                   )
        self.expect_error(expr)

    def test_lets_shadowed(self):
        # let x = 2 in let x = false in x
        # => false
        expr = Let('x',
                   Lit(2),
                   Let('x',
                       Lit(False),
                       Name('x')
                       )
                   )
        self.expect(expr,False)

    def test_eq_int(self):
        # 10 == 10
        # => true
        expr = Eq(Lit(10), Lit(10))
        self.expect(expr, True)
        # 46 == -4
        # => false
        expr = Eq(Lit(46), Lit(-4))
        self.expect(expr, False)

    def test_eq_bool(self):
        # true == true
        # => true
        expr = Eq(Lit(True), Lit(True))
        self.expect(expr, True)
        # true == false
        # => false
        expr = Eq(Lit(True), Lit(False))
        self.expect(expr, False)
        # false == true
        # => false
        expr = Eq(Lit(False), Lit(True))
        self.expect(expr, False)
        # false == false
        # => true
        expr = Eq(Lit(False), Lit(False))
        self.expect(expr, True)

    def test_eq_type_mismatch(self):
        # false == 0
        # => False
        expr = Eq(Lit(False), Lit(0))
        self.expect(expr, False)
        # 1 == true
        # => False
        expr = Eq(Lit(1), Lit(True))
        self.expect(expr, False)

    def test_lt(self):
        # 24 < 61
        # => true
        expr = Lt(Lit(24), Lit(61))
        self.expect(expr, True)
        # 59 < 14
        # => false
        expr = Lt(Lit(59), Lit(14))
        self.expect(expr, False)
        # -70 < -70
        # => false
        expr = Lt(Lit(-70), Lit(-70))
        self.expect(expr, False)

    def test_lt_type_error(self):
        # -79 < true
        # => error
        expr = Lt(Lit(-79), Lit(True))
        self.expect_error(expr)
        # false < 42
        # => error
        expr = Lt(Lit(False), Lit(42))
        self.expect_error(expr)

    def test_if_true(self):
        # if true then 65 else 80
        # => 64
        expr = If(Lit(True), Lit(64), Lit(80))
        self.expect(expr, 64)

    def test_if_false(self):
        # if false then -31 else -22
        # => -22
        expr = If(Lit(False), Lit(-31), Lit(-22))
        self.expect(expr, -22)

    def test_if_cond_type_error(self):
        # if 89 then -84 else -78
        # => error
        expr = If(Lit(89), Lit(-84), Lit(-78))
        self.expect_error(expr)

    def test_if_fbranch_error(self):
        # if true then -39 else 61 / 0
        # => -39
        expr = If(Lit(True), Lit(-39), Div(Lit(61), Lit(0)))
        self.expect(expr, -39)

    def test_if_tbranch_error(self):
        # if false then -33 / 0 else 83
        # => 83
        expr = If(Lit(False), Div(Lit(-33), Lit(0)), Lit(83))
        self.expect(expr, 83)

    def test_if_diff_branch_types(self):
        # if false then -11 else false
        # => false
        expr = If(Lit(False), Lit(-11), Lit(False))
        self.expect(expr, False)

    def test_complex_1(self):
        # (-57 * 21) + (-95 - 97)
        # => 1389
        expr = Add(Mul(Lit(-57), Lit(21)), Sub(Lit(-95), Lit(97)))
        self.expect(expr, -1389)

    def test_complex_2(self):
        # ((-37 == -37) or false) and (-75 < 43)
        # => false
        expr = And(Or(Eq(Lit(-37), Lit(-37)), Lit(False)), Lt(Lit(-75), Lit(43)))
        self.expect(expr, True)

    def test_complex_3(self):
        # if true then (if false then -98 else 26) else -20
        # => 26
        expr = If(Lit(True), If(Lit(False), Lit(-98), Lit(26)), Lit(-20))
        self.expect(expr, 26)

    def test_complex_4(self):
        # if 30 + -33 < 31 then true and false else true
        # => false
        expr = If(Lt(Add(Lit(30), Lit(-33)), Lit(31)),
                  And(Lit(True), Lit(False)),
                  Lit(True))
        self.expect(expr, False)

    def test_complex_5(self):
        # not (-7 == -7) or (true and -88 < -22)
        # => true
        expr = Or(
            Not(Eq(Lit(-7), Lit(-7))),
            And(Lit(True), Lt(Lit(-88), Lit(-22)))
        )
        self.expect(expr, True)

    def test_complex_6(self):
        # if -32 * -29 == 928 and -77 < 64 then 72 + 34 else -96 - -75
        # => 106
        expr = If(
            And(
                Eq(Mul(Lit(-32), Lit(-29)), Lit(928)),
                Lt(Lit(-77), Lit(64))
            ),
            Add(Lit(72), Lit(34)),
            Sub(Lit(20), Lit(5))
        )
        self.expect(expr, 106)

    def test_complex_7(self):
        # if 38 < 51 then (if 22 == 22 then 50 + -9 else 23) else -52
        # => 41
        expr = If(
            Lt(Lit(38), Lit(51)),
            If(Eq(Lit(22), Lit(22)), Add(Lit(50), Lit(-9)), Lit(23)),
            Lit(-52)
        )
        self.expect(expr, 41)

    def test_complex_8(self):
        # if true or not false then (if false then 35 else 72) else -65
        # => 72
        expr = If(
            Or(Lit(True), Not(Lit(False))),
            If(Lit(False), Lit(35), Lit(72)),
            Lit(-65)
        )
        self.expect(expr, 72)

    def test_complex_9(self):
        # if -11 < 34 then true or false else -53 + -94
        # => true
        expr = If(
            Lt(Lit(-11), Lit(34)),
            Or(Lit(True), Lit(False)),
            Add(Lit(-53), Lit(-94))
        )
        self.expect(expr, True)

    def test_complex_10(self):
        # if -61 + 76 == 15 then true or false else true and false
        # => true
        expr = If(
            Eq(Add(Lit(-61), Lit(76)), Lit(15)),
            Or(Lit(True), Lit(False)),
            And(Lit(True), Lit(False))
        )
        self.expect(expr, True)

    def test_complex_11(self):
        # 9 + ((if -56 < 25 then 8 else 6) * -87)
        # => -687
        expr = Add(
            Lit(9),
            Mul(
                If(Lt(Lit(-56), Lit(25)), Lit(8), Lit(6)),
                Lit(-87)
            )
        )
        self.expect(expr, -687)

    def test_let_1(self):
        # let x = 21 in x + x
        # => 42
        expr = Let('x',
            Lit(21),
            Add(
                Name('x'),
                Name('x')
            )
        )
        self.expect(expr, 42)

    def test_let_2(self):
        # let x = 20 in let y = x + 2 in x + y
        # => 42
        expr = Let('x',
                   Lit(20),
                   Let('y',
                       Add(Name('x'),
                           Lit(2)
                       ),
                       Add(Name('x'),
                           Name('y')
                       )
                   )
               )
        self.expect(expr, 42)

    def test_let_3(self):
        # (let x = 1 in x + x) + (let x = 20 in x + x)
        # => 42
        expr = Add(
            Let('x',
                Lit(1),
                Add(Name('x'),
                    Name('x')
                    )
                ),
            Let('x',Lit(20),
                Add(Name('x'),
                    Name('x')
                    )
                )
        )
        self.expect(expr, 42)

    def test_let_4(self):
        # let x = 20 in let x = 21 in x + x
        # => 42
        expr = Let('x',
                   Lit(20),
                   Let('x',
                       Lit(21),
                       Add(Name('x'), Name('x')
                           )
                       )
                   )
        self.expect(expr, 42)
        
    def test_let_5(self):
        # let x = 20 in let x = x + 1 in x + x
        # => 42
        expr = Let('x',
                   Lit(20),
                   Let('x',
                       Add(Name('x'),
                           Lit(1)
                           ),
                       Add(Name('x'),
                           Name('x')
                           )
                       )
                   )
        self.expect(expr, 42)

    def test_let_6(self):
        # let x = 40 in x + (let x = 1 in x + x)
        # => 42
        expr = Let('x',
                   Lit(40),
                   Add(Name('x'),
                       Let('x',
                           Lit(1),
                           Add(Name('x'),
                               Name('x')
                               )
                           )
                       )
                   )
        self.expect(expr, 42)

if __name__ == "__main__":
    unittest.main()
