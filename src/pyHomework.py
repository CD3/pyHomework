#! /usr/bin/env python

import sys, os, subprocess, shlex

import time
import yaml
import sympy as sy
import sympy.assumptions as ass
import numpy as np
import pint  as pn

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader

units = pn.UnitRegistry()

class HomeworkAssignment:

  def __init__(self):
    self.latex_template= r'''
@require(config)
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
\ListProperties(Numbers1=a,Numbers2=l,Hide2=1,Progressive*=0.5cm,Hang=true,Space2=0.2cm,Space1=0.4cm,Space1*=0.4cm)

\setlength{\headheight}{0.5in}
\pagestyle{fancyplain}
\fancyhead[L]{@config['LH']}
\fancyhead[C]{@config['CH']}
\fancyhead[R]{@config['RH']}
\fancyfoot[L]{@config['LF']}
\fancyfoot[C]{@config['CF']}
\fancyfoot[R]{@config['RF']}
\renewcommand{\headrulewidth}{0pt}

\setlength{\parindent}{0cm}

\title{@config['title']}
\author{}
\date{}

\begin{document}
\maketitle

\begin{enumerate}
@for q in config['questions']:
\begin{minipage}{\linewidth}
  \item @q['star'] \label{@q['label']} @q['text']
    @if 'parts' in q:
    \begin{enumerate}
      @for p in q['parts']:
      \item @p['star'] \label{@p['label']} @p['text']
      @end
    \end{enumerate}
    @end
\end{minipage}
@end
\end{enumerate}


\clearpage

@for f in config['figures']:
\begin{figure}
\includegraphics[@f['options']]{@f['filename']}
\caption{ \label{@f['label']} @f['caption']}
\end{figure}
@end

\end{document}
'''
    self.config = { 'title' : "UNKNOWN"
                  , 'LH' : ""
                  , 'CH' : ""
                  , 'RH' : ""
                  , 'LF' : ""
                  , 'CF' : r"\thepage"
                  , 'RF' : r"powered by \LaTeX"
                  , 'questions' : [ ]
                  , 'figures' : [ ]
                  , 'quiz_questions' : [ ]
                  }

    self.questions = self.config['questions']
    self.figures   = self.config['figures']
    self.quiz_questions = self.config['quiz_questions']

    self.blank_question = {'text' : "", 'label' : "", 'star' : "" }
    self.blank_part     = self.blank_question.copy()
    self.blank_figure   = {'filename' : "", 'caption' : "", 'label' : "", 'options' : "" }
    self.blank_quiz_question = {'text' : "", 'answer' : {}, 'instructions' : "" }



    self.template_engine = Engine( loader=DictLoader( {'doc': self.latex_template} ) , extensions=[CoreExtension()] )

  def write_latex(self, filename=None):
    if not filename:
        filename = "/dev/stdout"

    with open(filename, 'w') as f:
      f.write( self.template_engine.get_template("doc").render( {'config': self.config} ) )

    basename = os.path.splitext(filename)[0]
    self.config['latex_aux'] = basename+'.aux'

  def write_quiz(self, filename="quiz.yaml"):
    with open(filename,'w') as f:
      # this will write a yaml file that can be processed by BbQuiz
      for q in self.quiz_questions:
        if 'unit' in q and ("%s"%q['unit']) != 'dimensionless':
          q['text'] += 'Give your answer in %s. ' % q['unit']
        if 'instructions' in q:
          q['text'] += q['instructions']
      f.write( yaml.dump({ 'latex' : {'aux' : self.config['latex_aux']}, 'questions' : self.quiz_questions}, default_flow_style=False) )

  def build_PDF( self, basename="main"):
    basename = os.path.splitext(basename)[0]

    self.write_latex(basename+".tex")

    with open("/dev/stdout",'w') as FNULL:
      ret = subprocess.call(shlex.split( 'latexmk -pdf '+basename), stdout=sys.stdout, stderr=subprocess.STDOUT)

  def build_quiz(self, basename="quiz"):
    basename = os.path.splitext(basename)[0]

    self.write_quiz(basename+".yaml")

    with open("/dev/stdout",'w') as FNULL:
      ret = subprocess.call(shlex.split( 'BbQuiz.py '+basename+".yaml"), stdout=sys.stdout, stderr=subprocess.STDOUT)

    




  def add_question(self):
    self.questions.append( self.blank_question.copy() )
    self.questions[-1]['label'] = r"prob_%d" % len(self.questions)

  def add_part(self):
    if not 'parts' in self.questions[-1]:
      self.questions[-1]['parts'] = list()
    self.questions[-1]['parts'].append( self.blank_part.copy() )
    self.questions[-1]['parts'][-1]['label']  = r"prob_%d_%d" % (len(self.questions), len(self.questions[-1]['parts']))
    
  def get_ref(self):
    if 'parts' in self.questions[-1]:
      return self.questions[-1]['parts'][-1]['label']
    else:
      return self.questions[-1]['label']

  def add_text(self,text=""):
    if 'parts' in self.questions[-1]:
      self.questions[-1]['parts'][-1]['text'] += text + " "
    else:
      self.questions[-1]['text']  += text + " "


  def add_quiz_question(self):
    self.quiz_questions.append( self.blank_quiz_question.copy() )
    self.quiz_questions[-1]['text'] = "For problem #${/vars/%s}: "%self.get_ref()

  def quiz_add_text(self,text=""):
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    self.quiz_questions[-1]['text']  += text + " "

  def quiz_add_unit(self,unit=None):
    if unit:
      self.quiz_questions[-1]['unit'] = self.get_unit( unit )
    else:
      if 'unit' in self.quiz_questions[-1]:
        del self.quiz_questions[-1]['unit']

  def quiz_add_instruction(self,text):
    self.quiz_questions[-1]['instructions'] += text

  def quiz_add_answer(self, answer = None):
    self.quiz_questions[-1]['answer'] = answer

  def quiz_set_answer_value(self, value):
    self.quiz_add_answer( {'raw' : str(value), 'value' : self.get_value( value ), 'unit' : self.get_unit( value ) } )
    self.quiz_add_unit( value )


  def add_star(self, text="*"):
    if 'parts' in self.questions[-1]:
      self.questions[-1]['parts'][-1]['star'] = text
    else:
      self.questions[-1]['star'] = text

  def add_vars(self,vars={}):
    self.config.update( vars )

  def add_figure(self,filename=""):
    self.figures.append( self.blank_figure.copy() )
    self.figures[-1]['filename'] = filename

  def add_figure_data(self,data,text=""):
    if len(self.figures) > 0:
      self.figures[-1][data] = text


  def get_unit(self, x=None):
    u = ""
    if x:
      if isinstance( x, str ):
        u = x

      if isinstance( x, units.Quantity ):
        u = str(x.units)

    return u

  def get_value(self, x=None):
    if isinstance( x, str ):
      return x

    v = 0
    if x:
      if isinstance( x, units.Quantity ):
        v = x.magnitude

    return to_sigfig(v,3)


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
