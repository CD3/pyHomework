#! /usr/bin/env python

import datetime
import string
import re
import pprint
import pyparsing as pp

def format_text(text, delimiters=('{','}'), try_eval=False, *args, **kwargs):

  context = {}
  for i in range(len(args)):
    context[i] = args[i]
  context.update(kwargs)

  def replaceToken(text, loc, toks):
    exp = toks[1]
    try:
      s = '{'+exp+'}'
      return s.format(**context)
    except Exception as e:
      print "WARNING: failed to replace '"+exp+"' using string.format(). reason:",type(e),str(e)
      if try_eval:
        try:
          return eval(exp,{'__builtins__':None},context)
        except Exception as ee:
          print "WARNING: failed to replace '"+exp+"' using eval()."
          return None


  token = pp.Literal(delimiters[0]) + pp.SkipTo(pp.Literal(delimiters[1]), failOn=pp.Literal(delimiters[0])) + pp.Literal(delimiters[1])

  token.setParseAction(replaceToken)
  text = token.transformString( text )

  return text

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

def dict2list( d ):
    l = [None]*len( d )
    for k in d:
      # we can't just append here because we won't get the index numbers in order
      l[int(k)] = d[k]
    return l

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

def generate_latex_image( filename, text, extra_opts = [], config = {} ):
  '''Generates an image file from LaTeX code using l2p (https://github.com/CD3/l2p)'''
  image_filename = os.path.join(  config.get('image_dir','./'), filename )
  latex_filename = os.path.join(  config.get('image_dir','./'), filename+'tmp.latex' )

  with open('tmp.latex','w') as f:
    f.write(text)

  packages = 'circuitikz/siunitx/amsmath/amsfonts/amssymb'

  call( ['l2p', '-p', packages, '-t', '-B', '10x10'] + extra_opts + ['-o', image_filename, latex_filename] )

def get_pairs( s, beg_str, end_str ):
  '''Return list containing index positions of beg/end strings. Only returns positions for outside pairs.'''
  pairs = list()
  beg_n = len(beg_str)
  end_n = len(end_str)
  depth = 0
  for i in range(len(s)):
    if s[i:i+beg_n] == beg_str:
      depth += 1
      if depth == 1:
        beg_i = i
    if s[i:i+end_n] == end_str:
      depth -= 1
      if depth == 0:
        end_i = i+end_n
        pairs.append( [beg_i, end_i] )

  return pairs

def extract( s, beg_str, end_str ):
    pairs = get_pairs( s, beg_str, end_str )
    substrings = list()
    for pair in pairs:
      substrings.append( s[pair[0]+len(beg_str): pair[1]-len(end_str)] )

    return substrings


def parse_aux(filename):
  aux_lines = []
  with open(filename,'r') as f:
    aux_lines = f.read().split('\n')

  entries = dict()
  for line in aux_lines:
    if line.startswith('\\newlabel'):
      lbl,ref = extract( line, '{', '}' )
      ref = extract( ref, '{', '}' )[0]
      ref = ref.replace( r'\bgroup', '' )
      ref = ref.replace( r'\egroup', '' )
      ref = ref.replace( r' ', '' )
      ref = ref.replace( r'.', '' )
      try:
        entries[int(lbl)] = ref
      except:
        entries[lbl] = ref
      
  return entries

class Bunch(dict):
    def __init__(self,**kw):
        dict.__init__(self,kw)
        self.__dict__ = self
    def fmt(self,text):
      return text.format( **self.__dict__ )
