#! /usr/bin/env python

import datetime

def toBool( v ):
    if isinstance(v,str):
      isTrue  = str(v).lower() in ('true', 'yes','1')
      isFalse = str(v).lower() in ('false','no','0')

      if isTrue:
          return True
      if isFalse:
          return False

    if isinstance(v,int):
        return not v == 0

    return False

def isBool(v):
  return str(v).lower() in ('true', 'yes','false','no','0','1')

def FindPairs( s, beg_str, end_str):
    curr = 0

    pairs = list()
    run = True
    while run:
        opair = None
        curr = s.find( beg_str, curr )
        beg = curr
        curr = s.find( end_str, curr )
        end = curr
        if beg >= 0 and end > 0:
            opair = [beg,end]

        if opair:
            ipair = [
            opair[0] + len(beg_str)
           ,opair[1] - len(end_str)
            ]

            pairs.append( [opair,ipair] )

        else:
            run = False

    return pairs

def dict2list( d ):
    l = [None]*len( d )
    for k in d:
      # we can't just append here because we won't get the index numbers in order
      l[int(k)] = d[k]
    return l

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
  f = sy.lambdify( symbols, expr, "numpy" )
  # evaluate and return
  return f( *vals )

def get_semester( day = datetime.date.today()):
  '''Return the semester string, i.e. 'Spring 2015', for a date.'''
  year = day.year
  month = day.month

  season = "Unknown"

  if month in range(1,5):
    season = "Spring"

  if month in range(6,7):
    season = "Summer"

  if month in range(8,12):
    season = "Fall"

  sem = '%s %s' % (year,season)
  return sem

class vector_quantity_calcs:
  '''A collection of unit enabled functions for numpy vectors.'''
  @staticmethod
  def modsquared( vec ):
    ret = sum( [ x*x for x in vec ] )
    return ret
  @staticmethod
  def mod( vec ):
    return np.sqrt( vector_quantity_calcs.modsquared( vec ) )

  @staticmethod
  def length( vec ):
    return vector_quantity_calcs.mod( vec )

  @staticmethod
  def direction( vec ):
    ret = np.arctan2( vec[1], vec[0] )
    if ret < 0*units.radian:
      ret += 2*3.14159*units.radian
    return ret

