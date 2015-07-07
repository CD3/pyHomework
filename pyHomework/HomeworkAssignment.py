#! /usr/bin/env python

import sys, os, os.path, subprocess, shlex, re

import time
import tempfile
import shutil
import yaml
import sympy as sy
import sympy.assumptions as assumptions
import numpy as np
import pint

from mako.template import Template

units = pint.UnitRegistry()

class Question(object):
  def __init__(self):
    self.text = ""
    self.label = ""
    self.starred = False
    self.parts = []

  def add_text(self, text):
    self.text += text + " "

  def num_parts(self):
    return len( self.parts )

class Figure(object):
  def __init__(self):
    self.filename = ""
    self.label = ""
    self.caption  = ""
    self.options = ""

class QuizQuestion(Question):
  def __init__(self):
    super(QuizQuestion,self).__init__()
    self.answer = None
    self.instructions = ""
    self.unit = None

  def add_instruction(self, text):
    self.instructions += text + " "

  def set_unit(self, unit):
    unit = get_unit( unit )

  def set_answer(self, answer):
    self.answer = answer
    if isinstance( answer, NumericalAnswer ):
      self.unit = answer.unit


  def dict(self):
    text = self.text
    if self.unit and ("%s" % self.unit != 'dimensionless'):
      text += 'Give your answer in %s. ' % self.unit
    text += self.instructions

    return {'text': text, 'answer': self.answer.dict() }

class NumericalAnswer(object):
  def __init__(self, value=None):
    self.raw = None
    self.value = None
    self.uncertainty = '1%'
    self.unit = None

    self.set_value( value )

  def set_value( self, value ):
    if value:
      self.raw = str(value)
      self.value = get_value(value)
      self.unit = get_unit(value)

  def set_uncertainty( self, uncertainty ):
    self.uncertainty = uncertainty

  def dict(self):
    return {'raw' : self.raw,
            'unit' : self.unit,
            'value' : self.value,
            'uncertainty' : self.uncertainty }

class MultipleChoiceAnswer(object):
  def __init__(self):
    self.choices = []
    self.correct = -1

  def filter( self, text ):
    filtered_text = re.sub('^\s*\*\s*','',text)
    return (filtered_text != text, filtered_text)
    
  def add_choice( self, text ):
    self.choices.append( text )

  def dict(self):
    return {'choices' : self.choices }



  def set_correct( self, i = None):
    if i:
      self.correct = i
    else:
      self.correct = len(self.choices)-1




class HomeworkAssignment:

  def __init__(self):
    self.latex_template= r'''
\documentclass[letterpaper,10pt]{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage[per-mode=symbol]{siunitx}
\usepackage[left=1in,right=1in,top=1in,bottom=1in]{geometry}
\usepackage{fancyhdr}
\usepackage{enumitem}
\usepackage[ampersand]{easylist}
\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)

\setlength{\headheight}{0.5in}
\pagestyle{fancyplain}
\fancyhead[L]{${config['LH']}}
\fancyhead[C]{${config['CH']}}
\fancyhead[R]{${config['RH']}}
\fancyfoot[L]{${config['LF']}}
\fancyfoot[C]{${config['CF']}}
\fancyfoot[R]{${config['RF']}}
\renewcommand{\headrulewidth}{0pt}

\setlength{\parindent}{0cm}

\title{${config['title']}}
\author{}
\date{}

\begin{document}
\maketitle

%for item in config['stack']:
%if config['isQuestion']( item ):
\begin{minipage}{\linewidth}
  \begin{easylist}
  & ${'*' if item.starred else ''} \label{${item.label}} ${item.text}
  %for p in item.parts:
    && ${'*' if p.starred else ''} \label{${p.label}} ${p.text}
  %endfor
  \end{easylist}
\end{minipage}
%endif
%if config['isFigure']( item ):
\begin{figure}
\includegraphics[${item.options}]{${item.filename}}
\caption{ \label{${item.label}} ${item.caption}}
\end{figure}
%endif
%endfor

\end{document}
'''
    self.config = { 'title' : "UNKNOWN"
                  , 'LH' : ""
                  , 'CH' : ""
                  , 'RH' : ""
                  , 'LF' : ""
                  , 'CF' : r"\thepage"
                  , 'RF' : r"powered by \LaTeX"
                  , 'isQuestion' : lambda obj: isinstance( obj, Question ) and not isinstance( obj, QuizQuestion )
                  , 'isQuizQuestion' : lambda obj: isinstance( obj, QuizQuestion )
                  , 'isFigure' : lambda obj: isinstance( obj, Figure )
                  , 'stack' : [ ]
                  , 'latex_aux' : None
                  }

    self.stack     = self.config['stack']

    self.template_engine = Template( self.latex_template )

  def write_latex(self, filename=None):
    if not filename:
        filename = "/dev/stdout"

    with open(filename, 'w') as f:
      f.write( self.template_engine.render( config=self.config ) )

    basename = os.path.splitext( os.path.basename(filename))[0]
    self.config['latex_aux'] = basename+'.aux'

  def write_quiz(self, filename="quiz.yaml"):
    with open(filename,'w') as f:
      # this will write a yaml file that can be processed by BbQuiz
      tree = {'questions' : [] }
      for item in self.stack:
        if self.config['isQuizQuestion'](item):
          tree['questions'].append( item.dict() )

      if self.config['latex_aux']:
        tree.update({ 'latex' : {'aux' : self.config['latex_aux']}})
      f.write( yaml.dump(tree, default_flow_style=False) )

  def build_PDF( self, basename="main"):
    basename = os.path.splitext(basename)[0]
    scratch = tempfile.mkdtemp()

    self.write_latex(os.path.join(scratch,basename+".tex") )

    # copy all the figure files
    for item in self.stack:
      if self.config['isFigure'](item):
        shutil.copy( item.filename, os.path.join(scratch,item.filename) )

    with open("/dev/stdout",'w') as FNULL:
      ret = subprocess.call(shlex.split( 'latexmk -f -pdf '+basename), cwd=scratch, stdout=sys.stdout, stderr=subprocess.STDOUT)

    for ext in ("pdf", "aux", "tex"):
      filename = "%s.%s"%(basename,ext)
      shutil.copy( os.path.join(scratch,filename), filename)

  def build_quiz(self, basename="quiz"):
    basename = os.path.splitext(basename)[0]

    self.write_quiz(basename+".yaml")

    with open("/dev/stdout",'w') as FNULL:
      ret = subprocess.call(shlex.split( 'BbQuiz.py '+basename+".yaml"), stdout=sys.stdout, stderr=subprocess.STDOUT)

    

  def clean_text( self, text ):
    return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

  def num_questions(self):
    count = 0
    for item in self.stack:
      if isinstance( item, Question ):
        count += 1

    return count

  # return last item in stack that check evaluates to true on
  def get_last( self, check ):
    i = len(self.stack)-1
    while i >= 0 and (not check( self.stack[i] ) ):
      i = i - 1

    if i >= 0:
      return self.stack[i]
    else:
      return None

  def get_last_question(self):
    return self.get_last( lambda x : isinstance( x, Question ) and not isinstance( x, QuizQuestion ) )

  def get_last_part(self):
    question = self.get_last_question()
    if len( question.parts ) == 0:
      return None
    else:
      return question.parts[-1]

  def get_last_question_or_part(self):
    q = self.get_last_part()
    if not q:
      q = self.get_last_question()
    return q

  def get_last_quiz_question(self):
    return self.get_last( lambda x : isinstance( x, QuizQuestion ) )

  def get_last_figure(self):
    return self.get_last( lambda x : isinstance( x, Figure ) )


  def get_last_ref(self):
    q = self.get_last_question_or_part()
    if q:
      return q.label
    else:
      return None
      

  def add_question(self):
    '''Add a new (empyt) question to the stack.'''
    self.stack.append( Question() )
    self.get_last_question().label = r"prob_%d" % self.num_questions()

  def add_part(self):
    self.get_last_question().parts.append( Question() )
    self.get_last_part().label = r"prob_%d_%d" % (self.num_questions(), self.get_last_question().num_parts())

  def add_text(self,text=""):
    text = self.clean_text( text )
    q = self.get_last_question_or_part()
    if q:
      q.add_text( text )

  def add_star(self, text="*"):
    q.get_last_question_or_part()
    if q:
      q.starred = True

  def add_vars(self,vars={}):
    self.config.update( vars )



  def add_quiz_question(self):
    self.stack.append( QuizQuestion() )
    self.get_last_quiz_question().add_text( 'For problem #${lbls.%s}: ' % self.get_last_ref() )

  def quiz_add_text(self,text=""):
    text = self.clean_text( text )
    q = self.get_last_quiz_question()
    if q:
      q.add_text( text )

  def quiz_add_instruction(self,text):
    self.get_last_quiz_question().add_instruction( text )

  def quiz_set_unit(self,unit=None):
    self.get_last_quiz_question().set_unit( unit )

  def quiz_set_answer(self, answer = None):
    self.get_last_quiz_question().set_answer(answer)

  def add_figure(self,filename=""):
    self.stack.append( Figure() )
    self.get_last_figure().filename = filename

  def set_figure_data(self,data,text=""):
    f = self.get_last_figure()
    if f:
      setattr( f, data, text )




def get_unit(x=None):
  if x is None:
    return x

  u = ""
  if x:
    if isinstance( x, str ):
      u = x

    if isinstance( x, units.Quantity ):
      u = str(x.units)

  return u

def get_value(x=None):
  if isinstance( x, str ):
    return x

  v = 0
  if x:
    if isinstance( x, units.Quantity ):
      v = x.magnitude

  return to_sigfig(v,3)

def get_semester():
  month = int(time.strftime("%m"))
  year  =     time.strftime("%Y")
  semester = "Spring" if month < 6 else "Fall"

  return (semester,year)


def to_sigfig(x,p):
    """
    This code was taken from here:
    http://randlet.com/blog/python-significant-figures-format/

    returns a string representation of x formatted with a precision of p
    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """


    import math
    x = float(x)

    if x == 0.:
        return "0." + "0"*(p-1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1

    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1


    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)
