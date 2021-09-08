import argparse
from propagate_uncertainty import *
import re
import numpy as np
import json


def expr_to_latex(expr, eva=True):
    """
    :param expr: String, mathematical expression
    :param eva: bool, evaluate expression
    :return: String, expression formatted for latex
    """
    return latex(parse_expr(str(expr), evaluate=eva))


def export_latex(s, txt=False, filepath='uncertainty.txt'):
    out = ['\\begin{equation}', s[0], '\\end{equation}', '\\begin{align}']
    out.extend(s[1:])
    out.append('\\end{align}')
    for i in out:
        print(i)
    if txt:
        f = open(filepath, 'a')
        np.savetxt(f, out, fmt='%s', newline='\n')
        f.write('\n')
        f.close()


def gen_quadrature_latex(final, variables):
    """
    Generate quadrature equation for latex
    :param final: String, variable whose uncertainty is being calculated
    :param variables: List (SymPy Symbols), variables from which uncertainty is propagated
    :return: String of LaTEX code for quadrature equation
    """
    s_quad = "\\delta_{" + final + "} &= " + "\\sqrt{"
    for i in range(len(variables)):
        s_quad += '\\left(\\frac{\\partial_{' + final + '}}{\\partial_{' + \
                      expr_to_latex(variables[i]) + '}}\\right)^2 ' '(\\delta_{' + expr_to_latex(variables[i]) + '})^2 + '
    return s_quad[:-2] + '} \\\\'


def propagate_error_latex(equation, variables, values, final=None, txt=False, fp=None):
    """
    Error propagation step by step, converted into latex
    TODO: Cleanup variable names
    :param equation: String, equation for propagation
    :param variables: String, variables in equation
    :param values: List of tuples, pairs of values and uncertainty corresponding to the variables
    :param final: String, symbol whose uncertainty is being calculated (optional)
    :param txt: Bool, output to text file (optional)
    :param fp: String, filepath of text file (optional)
    :return: answer and uncertainty
    """
    f, syms = parse_expression(equation, variables)
    # Initial Expression
    # vars = variables.split(', ')
    # for i in range(len(vars)):
    #     globals()[vars[i]] = symbols(vars[i])
    equation = equation.replace('^', '**')
    if final is None:
        final = 'f(x)'
    else:
        final = expr_to_latex(final)
    s_eq = final + ' = ' + expr_to_latex(equation)
    # Quadrature Equation
    s_quad = gen_quadrature_latex(final, syms)
    # Generate partial derivatives and evaluate with substituted values
    s_partials = s_subs = []
    unc = unc_s_subbed = unc_s_partials = 0
    # Uncertainty propagation
    for i in range(len(syms)):
        '''
        Keep track of:
        1. function with just partial derivatives, 
        2. partial substituted with evaluated partial derivative values
        3. function substituted with unevaluated partial derivative values,
        TODO: Cleanup
        '''
        f_partial = f_partial_v = f_partial_s = diff(f, syms[i])
        s_partials.append(expr_to_latex(f_partial))
        for j in range(len(syms)):
            f_partial_s = f_partial_s.subs(syms[j], UnevaluatedExpr(values[j][0]))
            f_partial_v = f_partial_v.subs(syms[j], values[j][0])
        s_subs.append(f_partial_s)
        unc_s_partials += (f_partial * symbols('delta_{}'.format(syms[i]))) ** UnevaluatedExpr(2)
        unc_s_subbed += (UnevaluatedExpr(f_partial_s) * UnevaluatedExpr(values[i][1])) ** UnevaluatedExpr(2)
        unc += (f_partial_v * values[i][1]) ** 2
    unc = float(sqrt(unc))
    # Quadrature equation with partial derivatives and their values substituted in
    s_partial = '&= \\sqrt{' + expr_to_latex(unc_s_partials, False) + '} \\\\'
    s_sub = '&= \\sqrt{' + expr_to_latex(unc_s_subbed, False) + '} \\\\'
    # Substitute into function for significand
    for i in range(len(syms)):
        f = f.subs(syms[i], values[i][0])
    # Format values and final answer
    s_delta = '&= ' + str(unc) + ' \\\\'
    sig, unc, n = round_uncertainty(float(f), unc)
    n = max(0, n)
    s_final = "\\therefore " + final + " &= " + "({0:.{2}f}\\pm{1:.{2}f})".format(sig, unc, int(n))
    # If preceded by 'm' and succeeded by '.' then remove the 0
    s_final = re.sub('(?<=[m])0(?=[.])', '', s_final)
    # Export
    export_latex([s_eq, s_quad, s_partial, s_sub, s_delta, s_final], txt, filepath=fp)
    return f, sqrt(unc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--eq', type=str, help='equation for evaluating uncertainty')
    parser.add_argument('--vars', type=str, help='list of variables in the form "x,y,z" (no spaces)')
    parser.add_argument('--values', type=json.loads,
                        help='values of variables and associated uncertainties in the form [[x,dx],[y,dy]...] '
                             '(no spaces')
    parser.add_argument('--degrees', type=list, default=None,
                        help='index of values inputted that are in radians')
    parser.add_argument('--result', type=str, default=None,
                        help='symbol or function name whose uncertainty is being calculated')
    parser.add_argument('--fp', type=str, default=None,
                        help='filepath')
    args = parser.parse_args()

    if args.degrees:
        for j in args.degrees:
            args.values[int(j)] = np.radians(args.values[int(j)])

    # TODO: doesn't work for measured value of 0
    # TODO: make formatting requirement less strict
    if args.fp is not None:
        propagate_error_latex(args.eq, args.vars, args.values, args.result, True, args.fp)
    else:
        propagate_error_latex(args.eq, args.vars, args.values, args.result)



