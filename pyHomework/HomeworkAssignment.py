#! /usr/bin/env python

import os, StringIO, contextlib
from subprocess import call
from collections import OrderedDict

from .Quiz import *
from .Emitter import *
from .File import *
from .Utils import *
from pyErrorProp import *

import tempita

# ELEMENT CLASSES

class Figure(object):
  latex_template=r'''
\begin{figure}
\includegraphics[{{options}}]{{begb}}{{filename}}{{endb}}
\caption{ \label{{begb}}{{label}}{{endb}} {{caption}} }
\end{figure}
'''

  def __init__(self,filename=""):
    self._file = File(filename)
    self._label = []
    self._caption  = []
    self._options = []
  
  @property
  def filename(self):
    return self._file.filename

  def set_filename(self,fn):
    self._file._filename = fn

  def add_label(self,lbl,prepend=False):
    if prepend:
      self._label.insert(0,lbl)
    else:
      self._label.append(lbl)

  def add_option(self,opt):
    self._options.append(opt)

  def add_caption(self, cap, prepend=False):
    if prepend:
      self._caption.insert(0,cap)
    else:
      self._caption.append(cap)

  @property
  def latex(self):
    context = { 'filename' : self._file._filename
              , 'options'  : ','.join(self._options)
              , 'caption'  : ' '.join(self._caption)
              , 'label'    : ''.join(self._label)
              , 'begb'    : '{'
              , 'endb'    : '}'
              }
    return tempita.sub( self.latex_template, **context )
  
class Paragraph(object):
  def __init__(self, text = ""):
    self._texts = []
    self.add_text( text )

  def add_text(self, text):
    self._texts.append(text)

  @property
  def latex(self):
    return ' '.join(self._texts)

class Package(object):
  latex_template = r'\usepackage[{{opts}}]{ {{name}} }'
  def __init__(self, name = "", opts = ""):
    self.name = name
    self.opts = opts.split(',')

  def add_option(self, opt):
    self.opts.append( opt )

  @property
  def latex(self):
    return tempita.sub( self.latex_template, name=self.name, opts = ','.join(self.opts) )
    


# HOMEWORK ASSIGNMENT CLASS

class HomeworkAssignment(Quiz):
  latex_template= r'''
{{default author = ''}}
{{default date = ''}}
\documentclass[letterpaper,10pt]{article}

{{preamble}}

{{header}}

\title{ {{title}} }
\author{ {{author}} }
\date{ {{date}} }

\begin{document}
\maketitle

{{body}}

{{figures}}

\end{document}
'''

  def __init__(self):
    super( HomeworkAssignment,self ).__init__()
    self._config = { 'title' : "UNKNOWN"
                   , 'LH' : ""
                   , 'CH' : ""
                   , 'RH' : ""
                   , 'LF' : ""
                   , 'CF' : r"\thepage"
                   , 'RF' : r"powered by \LaTeX"
                   }

    self._packages = []
    self._preamble = []

    self._header = []

    self._paragraphs = OrderedDict()
    self._quizzes = OrderedDict()
    self._figures = OrderedDict()
    self.latex_refs = OrderedDict()
    
    
    self.add_package('amsmath')
    self.add_package('amsfonts')
    self.add_package('amssymb')
    self.add_package('graphicx')
    self.add_package('grffile')
    self.add_package('siunitx')
    self.add_package('fancyhdr')
    self.add_package('easylist', 'ampersand')
    self.add_package('hyperref')
    self.add_package('geometry', 'left=1in,right=1in,top=1in,bottom=1in')

    self.add_preamble(r'\ListProperties(Numbers1=a,Numbers2=l,Progressive*=0.5cm,Hang=true,Space=0.2cm,Space*=0.2cm)')
    self.add_preamble(r'\setlength{\parindent}{0cm}')
    self.add_preamble(r'\sisetup{per-mode=symbol}')
    self.add_preamble(r'\DeclareSIUnit \mile {mi}')
    self.add_preamble(r'\DeclareSIUnit \inch {in}')
    self.add_preamble(r'\DeclareSIUnit \foot {ft}')
    self.add_preamble(r'\DeclareSIUnit \yard {yd}')
    self.add_preamble(r'\DeclareSIUnit \acre {acre}')
    self.add_preamble(r'\DeclareSIUnit \lightyear {ly}')
    self.add_preamble(r'\DeclareSIUnit \parcec {pc}')
    self.add_preamble(r'\DeclareSIUnit \teaspoon {tsp.}')
    self.add_preamble(r'\DeclareSIUnit \tablespoon {tbsp.}')
    self.add_preamble(r'\DeclareSIUnit \gallon {gal}')
    self.add_preamble(r'\DeclareSIUnit \fluidounce{fl oz}')
    self.add_preamble(r'\DeclareSIUnit \ounce{oz}')
    self.add_preamble(r'\DeclareSIUnit \pound{lb}')
    self.add_preamble(r'\DeclareSIUnit \hour{hr}')

    self.add_header(r'\setlength{\headheight}{0.5in}')
    self.add_header(r'\pagestyle{fancyplain}')
    self.add_header(r'\fancyhead[L]{ {{LH}} }')
    self.add_header(r'\fancyhead[C]{ {{CH}} }')
    self.add_header(r'\fancyhead[R]{ {{RH}} }')
    self.add_header(r'\fancyfoot[L]{ {{LF}} }')
    self.add_header(r'\fancyfoot[C]{ {{CF}} }')
    self.add_header(r'\fancyfoot[R]{ {{RF}} }')
    self.add_header(r'\renewcommand{\headrulewidth}{0pt}')

    self.add_quiz('default')

  @property
  def body_latex(self):
    def insert_paragraph( i, question, **kwargs ):
      if i in self._paragraphs:
        tokens = []
        tokens.append(r'\end{easylist}')
        tokens.append('')
        for p in self._paragraphs[i]:
          tokens.append( p.latex )
        tokens.append('')
        tokens.append(r'\begin{easylist}')
        return '\n'.join(tokens)

      return None

    emitter = LatexEmitter(labels=True)
    emitter.sig_post_question.connect( insert_paragraph )
    text = self.emit(LatexEmitter(labels=True))
    emitter.sig_post_question.disconnect( insert_paragraph )
    return text

  @property
  def preamble_latex(self):
    tokens = []
    for p in self._packages:
      tokens.append( p.latex )
    tokens.append('')
    for p in self._preamble:
      tokens.append( p )

    return '\n'.join( tokens )

  @property
  def header_latex(self):
    context = self._config
    return tempita.sub( '\n'.join(self._header), **context )

  @property
  def figures_latex(self):
    tokens = []
    for k in self._figures:
      f = self._figures[k]
      tokens.append( f.latex )

    return '\n'.join( tokens )

  @property
  def last_ref(self):
    qp = self.last_question_or_part

    if qp is not None:
      return str(id(qp))

    return str("UNDEFINED")

  @property
  def last_question_or_part(self):
    q = self.last_question
    if q is not None:
      p = q.last_part
      if p is not None:
        return p
      return q
    return None

  @property
  def quiz(self):
    return self.get_quiz()


  @contextlib.contextmanager
  def _add_paragraph(self,p,i=None):
    if not isinstance(p,Paragraph):
      p = Paragraph(p)

    yield p

    # the position at which the paragraph should be inserted.
    if i is None:
      i = len(self._questions)

    if not i in self._paragraphs:
      self._paragraphs[i] = []

    self._paragraphs[i].append(p)

  def add_paragraph(self,*args,**kwargs):
    with self._add_paragraph(*args,**kwargs):
      pass

  @contextlib.contextmanager
  def _add_package(self,p,o=""):
    if not isinstance(p,Package):
      p = Package( p )
    p.add_option(o)

    yield p

    self._packages.append( p )

  def add_package(self,*args,**kwargs):
    with self._add_package(*args,**kwargs):
      pass

  @contextlib.contextmanager
  def _add_figure(self,f,name=None):
    if not isinstance(f,Figure):
      f = Figure(f)

    if name == None:
      name = f.filename

    yield f

    self._figures[name] = f

  def add_figure(self,*args,**kwargs):
    with self._add_figure(*args,**kwargs):
      pass


  @contextlib.contextmanager
  def _add_quiz(self, name='default',q = None):
    if q is None:
      q = BbQuiz()

    yield q

    if not name in self._quizzes:
      self._quizzes[name] = q

  def add_quiz(self,*args,**kwargs):
    with self._add_quiz(*args,**kwargs):
      pass


  def add_space(self,s):
    self.add_paragraph( r'\vspace{'+s+r'}' )

  def add_preamble(self,p):
    self._preamble.append( p )

  def add_header(self,h):
    self._header.append( h )

  @contextlib.contextmanager
  def _get_quiz(self,name='default'):
    yield self._quizzes[name]

  def get_quiz(self,name='default'):
    return self._quizzes[name]

  def get_fn(self, inputfn, type ):
    basename = os.path.splitext(inputfn)[0]
    if type.lower() == 'latex':
      return basename + '.tex'
    if type.lower() == 'tex':
      return basename + '.tex'
    if type.lower() == 'aux':
      return basename + '.aux'
    if type.lower() == 'pdf':
      return basename + '.pdf'

    return basename + '.' + type


  def write(self, stream):
    engine = tempita.Template(self.latex_template)
    context = { 'preamble'    : self.preamble_latex
              , 'header'      : self.header_latex
              , 'body'        : self.body_latex
              , 'figures'     : self.figures_latex
              }
    context.update( self._config )
    text = engine.substitute( **context )

    stream.write(text)

  def write_file(self, filename="/dev/stdout"):
    if filename.endswith('.pdf'):
      texfile = self.get_fn( filename, 'tex' )
    else:
      texfile = filename

    with open(texfile, 'w') as f:
      self.write( f )

    if filename.endswith( '.pdf' ):
      call( ['latexmk', '-silent', '-pdf', texfile ] )
      self.latex_refs.update( parse_aux( self.get_fn( texfile, 'aux' ) ) )
      call( ['latexmk', '-c', texfile ] )
        


  # LEGACY Interface

  def get_last_ref(self):
    return self.last_ref

  def add_part(self):
    q = self.last_question
    if q is not None:
      q.add_part()

  def add_text(self,text,prepend=False):
    self.last_question_or_part.add_text(text,prepend)

  def format_text(self,*args,**kwargs):
    self.last_question_or_part.format_text(*args,**kwargs)


  def add_quiz_question(self):
    self._quizzes['default'].add_question()

    self.quiz_add_text( "For problem #{{refs['%s']}}:" % id(self.last_question_or_part) )

  def quiz_add_text(self, text, prepend=False ):
    self.get_quiz('default').add_text(text,prepend)

  def quiz_add_instruction(self, text, prepend=False ):
    self.get_quiz('default').add_instruction(text,prepend)

  def quiz_set_answer(self, answer):
    self.get_quiz('default').set_answer(answer)
    if isinstance( answer, NumericalAnswer ):
      if answer.units != 'dimensionless':
        self.get_quiz('default').add_instruction('Give your answer in %s.' % answer.units,prepend=True)
    
  def write_latex(self,filename):
    if not filename.endswith('.tex'):
      filename = filename + '.tex'
    self.write_file(filename)

  def build_PDF(self,filename):
    if not filename.endswith('.pdf'):
      filename = filename + '.pdf'
    self.write_file(filename)

  def write_quiz(self,stream,name='default'):
    # we need to replace references before we write to file
    s = StringIO.StringIO()
    self.get_quiz(name).write(s)
    context = {'refs' : self.latex_refs}
    text = tempita.sub(s.getvalue(), **context)
    stream.write(text)

  def write_quiz_file(self,filename,name='default'):
    with open(filename,'w') as f:
      self.write_quiz(f,name)

