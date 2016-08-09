#! /usr/bin/env python

import os, StringIO, contextlib, types
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
  '''Represents a LaTeX figure.

  This class stores information about a LaTeX figure (filename, options, caption, etc) and
  is produces the LaTeX code for the figure.

  Example:

    f = Figure('./myImage.png')
    f.add_option('width=2in')
    f.add_option('angle=90')
    f.add_label('fig:myImage')
    f.add_caption('This figure shows something interesting.')

  '''


  latex_template=r'''
\begin{figure}
\includegraphics[{{options}}]{{begb}}{{filename}}{{endb}}
\caption{ \label{{begb}}{{label}}{{endb}} {{caption}} }
\end{figure}
'''

  def __init__(self,filename=""):
    '''Initialize figure.

    Args:
      filename (str,Default=''): name of image file to be displayed in figure.
    '''
    self._file = File()
    self._label = []
    self._caption  = []
    self._options = []

    self.set_filename(filename)
  
  @property
  def filename(self):
    '''Return filename of figure.'''
    return self._file.filename

  def set_filename(self,filename):
    '''Set name of the figure's image file.
    
    Args:
      filename (str): name of image file to be displayed in figure.
      '''
    #todo check if file exists
    self._file._filename = filename

  def add_label(self,text,prepend=False):
    '''Set text to figure's label
    
    Args:
      text (str): The text to add to figures label.
      prepend (bool,default=False): Flag indicating whether text should be prepended (true) or appended (false) to current label text.

      The figure's label is generated by concatenation all text added by this method.
      '''
    if prepend:
      self._label.insert(0,text)
    else:
      self._label.append(text)

  def add_option(self,opt):
    r'''Add an option for the \includegraphic command.
    
    Args:
      opt (str): option text to inserted in the \includegraphic command's option brackets.
      
    The option string passed to the \includegraphic comman's option brackets generated by joining all text added by this method with a comma.
    '''
    self._options.append(opt)

  def add_caption(self, text, prepend=False):
    '''Add text to the figures caption.

    Args:
      text (str): The text to add to figure's caption.
      prepend (bool,default=False): Flag indicating whether test should be prepended (true) or appended (false) to current caption text.

      The figure's caption is generated by joining all text added by this method with a space.
      '''
    if prepend:
      self._caption.insert(0,text)
    else:
      self._caption.append(text)

  @property
  def latex(self):
    '''Return the LaTeX code for the figure.'''
    context = { 'filename' : self._file._filename
              , 'options'  : ','.join(self._options)
              , 'caption'  : ' '.join(self._caption)
              , 'label'    : ''.join(self._label)
              , 'begb'    : '{'
              , 'endb'    : '}'
              }
    return tempita.sub( self.latex_template, **context )
  
class Paragraph(object):
  '''Represent a LaTeX paragraph that can be inserted between questions.

  This class can actually contain arbitrary LaTeX code.
  '''

  def __init__(self, text = ""):
    '''Initialize paragraph.

    Args:
      text (str): Paragraph texts.
    '''
    self._texts = []
    self.add_text( text )

  def add_text(self, text):
    '''Add text to the paragraph.

    Args:
      text (str): Test to add to paragraph.

    The text of the paragraph is generated by joining all text added by this method with a space.
    '''
    self._texts.append(text)

  @property
  def latex(self):
    '''Return the LaTeX code for the paragraph.'''
    return ' '.join(self._texts)

class Package(object):
  '''Represents a LaTeX package.
  
  Example:
    
    p = Package('siunitx')
    p.add_option('per-mode=frac')
  '''

  latex_template = r'\usepackage[{{opts}}]{ {{name}} }'
  def __init__(self, name, opts = ""):
    '''Initialize the package.

    Args:
      name (str): The package name. This is the name that will be used in the \usepackage command.
      opts (str,default=''): The option string to pass to the \usepackage command's option brackets.
    '''
    self.name = name
    self.opts = opts.split(',')

  def add_option(self, opt):
    '''Add an option to the pacakage.

    Args:
      opt (str): The option string to add.

    The option string that is passed to the \usepackage command is generated by joining all options added with this command using a comma.
    '''
    for o in opt.split(','):
      self.opts.append( o )

  @property
  def latex(self):
    '''Return the LaTeX code for the paragraph.'''
    return tempita.sub( self.latex_template, name=self.name, opts = ','.join(self.opts) )
    
# HOMEWORK ASSIGNMENT CLASS

class HomeworkAssignment(Quiz):
  ''' Represents a homework assignment.

  This class can create a PDF or LaTeX file for a homework assignment and an option Blackboard quiz over the assignment.
  '''

  latex_template= r'''
{{default author = ''}}
{{default date = ''}}
\documentclass[letterpaper,10pt]{article}


{{preamble}}


\usepackage{fancyhdr}
\setlength{\headheight}{0.5in}
\pagestyle{fancyplain}
\fancyhead[L]{ {{LH}} }
\fancyhead[C]{ {{CH}} }
\fancyhead[R]{ {{RH}} }
\fancyfoot[L]{ {{LF}} }
\fancyfoot[C]{ {{CF}} }
\fancyfoot[R]{ {{RF}} }
\renewcommand{\headrulewidth}{0pt}

\title{ {{title}} }
\author{ {{author}} }
\date{ {{date}} }

\begin{document}
\maketitle

{{body}}

{{figures}}

\clearpage
{{key}}

\end{document}
'''

  '''The Tempita template string used to generate the assignment document. The assignment document can be customized by setting this string.
  '''

  def __init__(self):
    '''Initialize the assignment.'''
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

    self.refstack = []  # reference stack

    self._paragraphs = OrderedDict()
    self._quizzes = OrderedDict()
    self._figures = OrderedDict()
    self._latex_refs = OrderedDict()
    self._labels = OrderedDict()
    
    
    self.add_package('amsmath')
    self.add_package('amsfonts')
    self.add_package('amssymb')
    self.add_package('graphicx')
    self.add_package('grffile')
    self.add_package('siunitx')
    self.add_package('fancyhdr')
    self.add_package('easylist', 'at')
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

    self.add_quiz('default')

  @property
  def body_latex(self):
    '''Returns the LaTeX code for the assignment body (the list of questions in the assignment).'''
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
    '''Returns the LaTeX code for the assignment preamble.'''
    tokens = []
    for p in self._packages:
      tokens.append( p.latex )
    tokens.append('')
    for p in self._preamble:
      tokens.append( p )

    return '\n'.join( tokens )

  @property
  def figures_latex(self):
    '''Returns the LaTeX code for the assignment figures.'''
    tokens = []
    for k in self._figures:
      f = self._figures[k]
      tokens.append( f.latex )

    return '\n'.join( tokens )

  @property
  def last_ref(self):
    '''Returns the label/ref string for the last question or question part in the assignment.'''
    qp = self.last_question_or_part

    if qp is not None:
      return str(id(qp))

    return str("UNDEFINED")

  @property
  def last_question_or_part(self):
    '''Returns the last question or question part.'''
    q = self.last_question
    if q is not None:
      p = q.last_part
      if p is not None:
        return p
      return q
    return None

  @property
  def last_figure(self):
    '''Returns the last figure.'''
    if len( self._figures) > 0:
      key = self._figures.keys()[-1]
      return self._figures[key]
    else:
      return None

  @property
  def quiz(self):
    '''Returns the default quiz.'''
    return self.get_quiz()

  @property
  def key_latex(self):
    tokens = []
    num = 0
    for q in self._questions:
      answer = []
      answer.append( r'\ref{'+str(id(q))+r'}')
      if len(q._answers) > 0:
        num += 1
        for a in q._answers:
          answer.append( a.latex )
      tokens.append( ' '.join(answer) )

      for p in q._parts:
        answer = []
        answer.append( r'\ref{'+str(id(p))+r'}')
        if len(p._answers) > 0:
          num += 1
          for a in p._answers:
            answer.append( a.latex )
        tokens.append( ' '.join(answer) )

    if num == 0:
      return ""
    return '\n\n'.join(tokens)

  @contextlib.contextmanager
  def _add_paragraph(self,p,i=None):
    '''Adds a paragraph to the assignment and returns a context manager that yields the paragraph added.
    
    Args:
      p (Paragraph|str): The paragraph instance (or text) to add.
      i (int,default=None): The question that the paragraph should be inserted after. If None, the last question is used.

    Exmaple:

      ass = HomeworkAssignment()
      ...
      with ass._add_paragraph() as p:
        p.add_text('This is a paragraph.')
    '''
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
    '''Wrapper around _add_paragraph to insert a paragraph without 'with' statement. This is equivalent to:
      
      ass = HomeworkAssignment()
      ...
      with ass._add_paragraph():
        pass
      '''
    with self._add_paragraph(*args,**kwargs):
      pass

  @contextlib.contextmanager
  def _add_package(self,p,o=""):
    '''Adds a package to the assignment and returns a context manager that yields the package added.
    
    Args:
      p (Package|str): The package instance (or name) to add.
      o (str,default=''): The package options.

    Exmaple:

      ass = HomeworkAssignment()
      ...
      with ass._add_package('siunitx') as p:
        p.add_option('per-mode=frac')
    '''
    if not isinstance(p,Package):
      p = Package( p )
    p.add_option(o)

    yield p

    self._packages.append( p )

  def add_package(self,*args,**kwargs):
    '''Wrapper around _add_package to add a package without 'with' statement. This is equivalent to:
      
      ass = HomeworkAssignment()
      ...
      with ass._add_package('siunitx','per-mode=frac'):
        pass
      '''
    with self._add_package(*args,**kwargs):
      pass

  @contextlib.contextmanager
  def _add_figure(self,f,name=None):
    '''Adds a figure to the assignment and returns a context manage that yields the figure added.

    Args:
      f (Figure|str): Figure (or filename) to add to the assignment.
      name (str, default=None): A name that the figure can be accessed with (Figures are stored in a dict). If None, the figure's filename will be used.

    Example:
      
      ass = HomeworkAssignment()
      ...
      with ass._add_figure('image.png') as f:
        f.add_caption("A picture of something interesting.")
        f.add_option("width=3in")
    '''
    if not isinstance(f,Figure):
      f = Figure(f)

    if name == None:
      name = f.filename

    # add id to refs stack
    self.refstack.append(id(f))
    yield f
    self.refstack.pop()

    self._figures[name] = f

  def add_figure(self,*args,**kwargs):
    '''Wrapper around _add_figure to add a pacakge without 'with' statement. This is equivalent to :

    ass = HomeworkAssignment()
    f = Figure()
    ...
    with ass._add_figure(f):
      pass
    '''
    with self._add_figure(*args,**kwargs):
      pass

  # perhaps there is a way to use the parent classes
  @contextlib.contextmanager
  def _add_question(self,label='last'):
    refstack = self.refstack
    q = Question()

    # replace the questions _add_part method
    q._add_part = types.MethodType( self._custom_question_add_part, q )

    refstack.append(id(q))
    yield q
    refstack.pop()

    self._order.append( len(self._questions) )
    self._questions.append( q )
    self._labels[label] = id(q)


  @contextlib.contextmanager
  def _add_quiz(self, name='default',q = None):
    if q is None:
      q = BbQuiz()

    yield q

    def Quiz_add_question(self,q=None):
      cm = self._add_question_cm(q)
      return cm

    q._add_question = types.MethodType( self._custom_quiz_add_question, q )


    if not name in self._quizzes:
      self._quizzes[name] = q

  def add_quiz(self,*args,**kwargs):
    with self._add_quiz(*args,**kwargs):
      pass


  def add_space(self,s):
    self.add_paragraph( r'\vspace{'+s+r'}' )

  def add_preamble(self,p):
    self._preamble.append( p )

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

  def get_label(self,label):
    if label in self._labels:
      return self._labels[label]

    return None


  def write(self, stream):
    context = { 'preamble'    : self.preamble_latex
              , 'body'        : self.body_latex
              , 'figures'     : self.figures_latex
              , 'key'         : self.key_latex
              }
    context.update( self._config )
    text = tempita.sub( self.latex_template, **context )

    stream.write(text)

  def write_file(self, filename="/dev/stdout"):
    if filename.endswith('.pdf'):
      texfile = self.get_fn( filename, 'tex' )
    else:
      texfile = filename

    with open(texfile, 'w') as f:
      self.write( f )

    if filename.endswith( '.pdf' ):
      self.latexmk( texfile )


  def latexmk( self, texfile ):
    with open(texfile+'latexmk-cmd.log','w') as f:
      status = call( ['latexmk', '-latexoption=-interaction=nonstopmode', '-pdf', texfile ], stdout=f, stderr=f )
      self._latex_refs.update( parse_aux( self.get_fn( texfile, 'aux' ) ) )
      call( ['latexmk', '-c', texfile ], stdout=f, stderr=f )
    if status:
      with open(texfile+'latexmk-cmd.log','r') as f:
        lines = f.readlines()
      print "====================================="
      print "THERE WAS AND ERROR."
      print "dumping latexmk output to screen:"
      print "====================================="
      print ''.join(lines)
      print "====================================="
      print "====================================="
    


        


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
    tmp = self.get_quiz('default').last_question.auto_answer_instructions
    self.get_quiz('default').last_question.auto_answer_instructions = True
    self.get_quiz('default').set_answer(answer)
    self.get_quiz('default').last_question.auto_answer_instructions = tmp

  def quiz_add_image(self, fn):
    self.get_quiz('default').last_question.add_file( fn )


  def figure_set_data( self, type, val ):
    f = self.last_figure
    if f is None:
      raise Exception("No figures have been added to the assignment yet.")
      return

    if type == 'options':
      f.add_option(val)
      return
    if type == 'label':
      f.add_label(val)
      return
    if type == 'caption':
      f.add_caption(val)
      return

    raise NameError("'"+type+"' is not a recognized data type for figures")

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
    context = {'refs' : self._latex_refs}
    text = tempita.sub(s.getvalue(), **context)
    stream.write(text)
    self.get_quiz(name).push_files()

  def write_quiz_file(self,filename,name='default'):
    with open(filename,'w') as f:
      self.write_quiz(f,name)


  ###################
  # MONKEY PATCHING #
  ###################

  # when a part is added to a question, we need to push the part's
  # reference onto the refstack and pop it off after we are done
  @property
  def _custom_question_add_part(self):
    # again, can we just wrap the function want to replace?
    refstack = self.refstack
    labels = self._labels
    @contextlib.contextmanager
    def _add_part(self,p=None,label='last',prepend=False):
      with Question._add_part(self,prepend) as pp:
        refstack.append(id(pp))
        yield pp
        refstack.pop()
        labels[label] = id(pp)

    return _add_part


  # when a quiz adds a question, it needs to add a sentence identifying the thing (question, part, figure, etc.)
  # it is refering to.
  @property
  def _custom_quiz_add_question(self):
    refstack = self.refstack
    @contextlib.contextmanager
    def _add_question(self,q=None):
      with BbQuiz._add_question(self,q) as qq:
        yield qq
        if len(refstack) > 0:
          qq.add_text("For problem #{{refs['%s']}}:" % refstack[-1], prepend=True )

    return _add_question

