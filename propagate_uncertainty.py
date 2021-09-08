from sympy import *
import math


def round_uncertainty(sig, unc):
    """
    Rounds significand and uncertainty to the format in which
    the uncertainty is rounded to the most significant digit
    and the significand is rounded to be consistent with the uncertainty
    :param sig: significand
    :param unc: uncertainty
    :return: rounded significand, rounded uncertainty, rounding place value
    """
    def sig_dig_pos(x):
        return math.ceil(-math.log10(x))

    assert(unc != 0), "Uncertainty is 0, please input value as a constant"

    n = sig_dig_pos(unc)
    # TODO: rounding errors, sketchy workaround to first cast as string and use normal randing rather than bankers
    n = min(sig_dig_pos(float(str(round(unc, n)))), n)
    return round(sig, n), round(unc, n), n


def parse_expression(equation, variables):
    """
    Parses the equation into sympy datatypes
    :param equation: String, equation for uncertainty propagation
    :param variables: Tuple or char, variables in the equation
    :return: function and variables as sympy equation and symbols
    """
    variables = symbols(variables)
    if type(variables) is not tuple:
        variables = [variables]
    f = sympify(equation, convert_xor=True, rational=True)
    return f, variables


def propagate_error(equation, variables, values):
    """
    Simple error propagation by method of quadrature where
    delta_z = sqrt(f_partial^2 * delta_x^2 + f_partial^2 * delta_y^2 + ...)
    :param equation: String, equation for propagation
    :param variables: String, variables in equation
    :param values: List of tuples, pairs of values and uncertainty corresponding to the variables
    :return: answer and uncertainty
    """
    f, syms = parse_expression(equation, variables)
    unc = 0
    for i in range(len(syms)):
        f_partial = diff(f, syms[i])
        for j in range(len(syms)):
            f_partial = f_partial.subs(syms[j], values[j][0])
        unc += (f_partial * values[i][1]) ** 2
    for i in range(len(syms)):
        f = f.subs(syms[i], values[i][0])
    return f, sqrt(unc)
