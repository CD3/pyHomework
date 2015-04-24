#! /usr/bin/env python

import sys, os, subprocess, shlex

import sympy as sy
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

@for q in config['questions']:
\begin{minipage}{\linewidth}
\begin{easylist}
  & @q['star'] @q['text']
    @if 'parts' in q:
      @for p in q['parts']:
      && @p['star'] @p['text']
      @end
    @end
\end{easylist}
\end{minipage}
@end


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
                  }

    self.questions = self.config['questions']
    self.figures   = self.config['figures']

    self.blank_question = {'text' : "", 'star' : "" }
    self.blank_part     = {'text' : "", 'star' : "" }
    self.blank_figure   = {'filename' : "", 'caption' : "", 'label' : "", 'options' : "" }



    self.template_engine = Engine( loader=DictLoader( {'doc': self.latex_template} ) , extensions=[CoreExtension()] )

  def write_latex(self, filename=None):
    if not filename:
        filename = "/dev/stdout"
    with open(filename, 'w') as f:
      f.write( self.template_engine.get_template("doc").render( {'config': self.config} ) )

  def build_PDF( self, filename=None):
    if not filename:
      filename = "main.pdf"

    basename = os.path.splitext(filename)[0]

    self.write_latex(basename+".tex")

    with open("/dev/stdout",'w') as FNULL:
      ret = subprocess.call(shlex.split( 'latexmk -pdf '+basename), stdout=sys.stdout, stderr=subprocess.STDOUT)


    




  def add_question(self):
    self.questions.append( self.blank_question.copy() )

  def add_part(self):
    if not 'parts' in self.questions[-1]:
      self.questions[-1]['parts'] = list()
    self.questions[-1]['parts'].append( self.blank_part.copy() )

  def add_text(self,text=""):
    if 'parts' in self.questions[-1]:
      self.questions[-1]['parts'][-1]['text'] += text + " "
    else:
      self.questions[-1]['text']  += text + " "

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

