#! /usr/bin/env python

import sys, os, os.path, subprocess, shlex, re, StringIO, datetime, time, tempfile, shutil, string
import yaml

from mako.template import Template

from .Utils import *

from pyErrorProp import *

# UTIL FUNCTIONS
def get_unit(x=None):
  if x is None:
    return x

  u = ""
  if not x is None:
    if isinstance( x, str ):
      u = x

    if isinstance( x, (pint.quantity._Quantity, pint.measurement._Measurement) ):
      u = str(x.units)

  return u


# ELEMENT CLASSES

class Question(object):
  '''A class representing a questions on a homework problem set.'''
  def __init__(self):
    self.text = ""
    self.label = ""
    self.starred = False
    self.parts = []
    self.answer = None

  def add_text(self, text):
    self.text += text + " "

  def num_parts(self):
    return len( self.parts )

  def set_answer(self, answer):
    self.answer = answer
    if isinstance( answer, NumericalAnswer ):
      self.unit = answer.unit

class Figure(object):
  def __init__(self):
    self.filename = ""
    self.label = ""
    self.caption  = ""
    self.options = ""

class QuizQuestion(Question):
  '''A class representing a quiz question about homework.'''
  def __init__(self):
    super(QuizQuestion,self).__init__()
    self.instructions = ""
    self.unit = None
    self.image = None

  def add_instruction(self, text):
    self.instructions += text + " "

  def add_image(self, name):
    self.image = name

  def set_unit(self, unit):
    self.unit = ""
    if not unit is None:
      if isinstance( unit, str ):
        self.unit = unit
      if isinstance( x, (pint.quantity._Quantity, pint.measurement._Measurement) ):
        self.unit = str(unit.units)




  def dict(self):
    text = self.text
    if self.unit and ("%s" % self.unit != 'dimensionless'):
      text += 'Give your answer in %s. ' % self.unit
    text += self.instructions

    d = {'text': text, 'answer': self.answer.dict() }
    if self.image:
      d.update( {'image' : self.image} )

    return d

class Paragraph(object):
  def __init__(self, text = ""):
    self.text = text

  def add_text(self, text):
    self.text += text + " "



# ANSWER CLASSES


# ASSIGNMENT CLASSES

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
\usepackage{hyperref}


\DeclareSIUnit \mile {mi}
\DeclareSIUnit \inch {in}
\DeclareSIUnit \foot {ft}
\DeclareSIUnit \yard {yd}
\DeclareSIUnit \acre {acre}
\DeclareSIUnit \lightyear {ly}
\DeclareSIUnit \parcec {pc}
\DeclareSIUnit \teaspoon {tsp.}
\DeclareSIUnit \tablespoon {tbsp.}
\DeclareSIUnit \gallon {gal}
\DeclareSIUnit \fluidounce{fl oz}
\DeclareSIUnit \ounce{oz}
\DeclareSIUnit \pound{lb}
\DeclareSIUnit \hour{hr}


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

%for line in config['preamble']:
${line}
%endfor

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
%if config['isParagraph']( item ):

${item.text}

%endif
%endfor

\clearpage

%if config.get('make_key',False):
\textbf{Answers:} \\\

%for item in config['stack']:
%if config['isQuestion']( item ):
%if not item.answer is None:
  \ref{${item.label}} ${str(item.answer)} \\\
%endif
%for p in item.parts:
%if not p.answer is None:
  \ref{${p.label}} ${str(p.answer)} \\\
%endif
%endfor
%endif
%endfor
%endif

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
                  , 'isParagraph' : lambda obj: isinstance( obj, Paragraph )
                  , 'stack' : [ ]
                  , 'preamble' : [ ]
                  , 'latex_aux' : None
                  , 'image_dir' : './'
                  , 'extra_files' : []
                  , 'quiz_config' : None
                  }

    self.stack     = self.config['stack']
    self.preamble  = self.config['preamble']

    self.template_engine = Template( self.latex_template )

  def write_latex(self, stream=None):
    if stream is None:
        stream = "/dev/stdout"

    if isinstance(stream,(str,unicode)):
      basename = os.path.splitext( os.path.basename(stream))[0]
      self.config['latex_aux'] = basename+'.aux'
      with open(stream, 'w') as f:
        self.write_latex( f )
      return

    stream.write( self.template_engine.render( config=self.config ) )

  def write_quiz(self, stream="quiz.yaml"):
    if stream is None:
        stream = "/dev/stdout"

    if isinstance(stream,(str,unicode)):
      with open(stream, 'w') as f:
        self.write_quiz( f )
      return

    # this will write a yaml file that can be processed by BbQuiz
    tree = {'questions' : [] }
    for item in self.stack:
      if self.config['isQuizQuestion'](item):
        tree['questions'].append( item.dict() )

    if not self.config['latex_aux'] is None:
      tree.update({ 'latex' : {'aux' : self.config['latex_aux']}})
    
    if not self.config['quiz_config'] is None:
      tree.update( {'configuration' : self.config['quiz_config'] } )

    stream.write( yaml.dump(tree, default_flow_style=False) )

  def build_PDF( self, basename="main"):
    basename = os.path.splitext(basename)[0]
    scratch = tempfile.mkdtemp()

    self.write_latex(os.path.join(scratch,basename+".tex") )

    # copy dependencies
    for item in self.config['extra_files']:
      fr  = item
      to  = os.path.join(scratch, os.path.basename( item ))
      print "Copying %s to %s" % (fr,to)
      shutil.copy( fr, to )


    p = subprocess.Popen(shlex.split( 'latexmk -interaction=nonstopmode -f -pdf '+basename), cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = p.communicate()
    ret = p.returncode
    if ret != 0:
      print "ERROR: LaTeX code failed to compile. Dumping output"
      print "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
      print stderr
      print stdout
      print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"

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

  def add_paragraph(self,para):
    self.stack.append( para )

  def add_preamble(self,line):
    self.preamble.append( line )

  def add_part(self):
    self.get_last_question().parts.append( Question() )
    self.get_last_part().label = r"prob_%d_%d" % (self.num_questions(), self.get_last_question().num_parts())

  def add_text(self,text=""):
    text = self.clean_text( text )
    q = self.get_last_question_or_part()
    if q:
      q.add_text( text )

  def format_text(self,*args,**kwargs):
    class SafeDict(dict):
      def __missing__(self,key):
        return '{'+key+'}'

    q = self.get_last_question_or_part()
    if q:
      if 'formatter' in kwargs and kwargs['formatter'] == 'template':
        q.text = string.Template(q.text).safe_substitute( **kwargs )
      else:
        q.text = string.Formatter().vformat( q.text, args, SafeDict( kwargs ) )

  def set_star(self, starred = True):
    q = self.get_last_question_or_part()
    if q:
      q.starred = starred

  def set_answer(self, answer = None):
    self.config['make_key'] = True
    self.get_last_question_or_part().set_answer(answer)

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

  def quiz_format_text(self,*args,**kwargs):
    class SafeDict(dict):
      def __missing__(self,key):
        return '{'+key+'}'

    q = self.get_last_quiz_question()
    if q:
      if 'formatter' in kwargs and kwargs['formatter'] == 'format':
        q.text = string.Formatter().vformat( q.text, args, SafeDict( kwargs ) )
      else:
        q.text = string.Template(q.text).safe_substitute( **kwargs )


  def quiz_add_image(self,name=None):
    q = self.get_last_quiz_question()
    if q:
      q.add_image( name )

  def quiz_add_instruction(self,text):
    self.get_last_quiz_question().add_instruction( text )

  def quiz_set_unit(self,unit=None):
    self.get_last_quiz_question().set_unit( unit )

  def quiz_set_answer(self, answer = None):
    self.get_last_quiz_question().set_answer(answer)

  def add_figure(self,filename=""):
    self.stack.append( Figure() )
    self.get_last_figure().filename = filename

    self.add_extra_file( os.path.join(self.config['image_dir'],filename) )




  def figure_set_data(self,data,text=""):
    f = self.get_last_figure()
    if f:
      setattr( f, data, text )


  def add_extra_file(self,filename):
    self.config['extra_files'].append( filename )


