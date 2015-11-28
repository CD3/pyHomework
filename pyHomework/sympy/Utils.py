
def expr_eval( expr, context = {} ):
  '''Evaluates a sympy expression with the given context.'''

  # if we have a list of expressions, evaluate each
  if isinstance( expr, list ):
    results = [ expr_eval(x,context) for x in expr ]
    return results

  # symbols that we have values for
  symbols = context.keys()
  # values of the symbols (these can be pint quantities!)
  vals = [ context[k] for k in symbols ]
  # create a lambda function that can be evaluated
  f = lambdify( symbols, expr, "numpy" )
  # evaluate and return
  return f( *vals )

# def eval(self, expr, var, context, soli = 0 ):
  # solution = solve( expr, var )[soli]
  # s = self.s
  # c = self.consts
  # context.update( { s.pi_ : math.pi,
                    # s.k_  : c.CoulombsConstant,
                    # s.mu0_  : c.VacuumPermeability,
                    # s.ep0_  : c.VacuumPermittivity,
                # } )

  # ans = expr_eval( solution, context )

  # return ans

# def subs(self, toexpr, fromexpr, var, soli = 0 ):
  # sol = solve( fromexpr, var )[soli]
  # ret = toexpr.subs( var, sol )
  # return ret






