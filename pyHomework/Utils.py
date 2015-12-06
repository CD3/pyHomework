#! /usr/bin/env python

import datetime
import string

class FormatterDict(dict):
  def __missing__(self,key):
    return '{'+key+'}'

def format_text(text, formatter, *args, **kwargs):
  if formatter == 'format':
    return string.Formatter().vformat( text, args, FormatterDict( kwargs ) )
  elif formatter == 'template':
    return string.Template( text ).safe_substitute( **kwargs )
  else:
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
