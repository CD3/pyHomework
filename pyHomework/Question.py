import inspect, contextlib
from .Utils import format_text
from .Answer import *
from .Emitter import *
import dpath.util

class Question(object):
  """A class representing a question.

  A can question contain:
  
  - text : the actual question itself
  - instructions : extra information needed to answer the question
  - pre_instructions : extra information needed to answer the question, but presented before the question text.
  - answers : one or more answers to the question
  - parts : one or more parts to the questions (sub-questions). these are also questions.
  """
  DefaultEmitter = PlainEmitter
  
  def __init__(self, text = None):
    # controlled access members
    self._texts = []
    self._instructions = []
    self._pre_instructions = []
    self._answers = []
    self._parts = []

    if not text is None:
      self.add_text( text )

    # regular members
    self.prepend_instructions = False
    self.join_str = ' '

    # config options
    self.clean_text = True
    self.auto_answer_instructions = True

  # common operations for different members

  def join_X( self, X):
    j = self.join_str
    s = j.join( X )
    if s.startswith( j ):
      s = s[len(j):]
    if s.endswith( j ):
      s = s[:-len(j)]

    return s

  def add_X(self, X, val, prepend=False):
    if isinstance( val , (str,unicode) ) and self.clean_text:
      val = ' '.join( val.split() )
      
    '''Adds val to list X. If prepend is True, val is inserted to the
    beginning of the list.'''
    if val is None:
      return
    if prepend:
      X.insert(0,val)
      return X[0]
    else:
      X.append(val)
      return X[-1]

  def set_X(self, X, val):
    del X[:]
    return self.add_X(X,val)

  def format_X(self,X,*args,**kwargs):
    if not 'formatter' in kwargs:
      kwargs['formatter'] = 'template'
    for i in range(len(X)):
      X[i] = format_text( X[i], *args, **kwargs )


  def add_text(self,v,prepend=False):
    return self.add_X(self._texts,v,prepend)

  def set_text(self,v=None):
    return self.set_X(self._texts,v)

  def format_text(self, *args, **kwargs):
    return self.format_X(self._texts,*args,**kwargs)
  format_texts = format_text


  def add_instruction(self,v,prepend=False):
    return self.add_X(self._instructions,v.strip(),prepend)

  def set_instruction(self,v=None):
    return self.set_X(self._instructions,v)

  def format_instruction(self, *args, **kwargs):
    return self.format_X(self._instructions,*args,**kwargs)
  format_instructions = format_instruction


  def add_pre_instruction(self,v,prepend=False):
    return self.add_X(self._pre_instructions,v.strip(),prepend)

  def set_pre_instruction(self,v=None):
    return self.set_X(self._pre_instructions,v)

  def format_pre_instruction(self, *args, **kwargs):
    return self.format_X(self.__pre_instructions,*args,**kwargs)
  format_pre_instructions = format_pre_instruction


  def format_question(self, *args, **kwargs):
    self.format_text(*args,**kwargs)
    self.format_instruction(*args,**kwargs)
    self.format_pre_instruction(*args,**kwargs)


  # properties: allow attribute style access to processed data

  @property
  def text_str(self):
    return self.join_X(self._texts)

  @property
  def instructions_str(self):
    return self.join_X(self._instructions)
  
  @property
  def question_str(self):
    tmp = [self.text_str]
    if self.prepend_instructions:
      tmp.insert(0,self.instructions_str)
    else:
      tmp.append(self.instructions_str)

    return self.join_X( tmp )

  @property
  def last_part(self):
    if len( self._parts ) > 0:
      i = -1
      return self._parts[i]
    else:
      return None


  # sub-data: lists/dicts of class instances

  @contextlib.contextmanager
  def _add_answer(self,a,prepend=False):

    if inspect.isclass( a ):
      a = a()

    # the "magic"
    yield a

    # add special instructions for different answer types.
    if self.auto_answer_instructions:
      if isinstance( a, NumericalAnswer ):
        if a.units != 'dimensionless' and a.units != '':
          self.add_instruction('Give your answer in %s.' % a.units,prepend=True)

    self.add_X(self._answers,a,prepend)

  def add_answer(self,*args,**kwargs):
    with self._add_answer(*args,**kwargs):
      pass

  def _set_answer(self,*args,**kwargs):
    del self._answers[:]
    return self._add_answer(*args,**kwargs)

  def set_answer(self,*args,**kwargs):
    with self._set_answer(*args,**kwargs):
      pass

  @contextlib.contextmanager
  def _add_part(self,v=None,prepend=False):
    if not isinstance(v, Question):
      v = Question(v)

    # the "magic"
    yield v

    self.add_X(self._parts,v,prepend)

  def add_part(self,*args,**kwargs):
    with self._add_part(*args,**kwargs):
      pass

  def _set_part(self,*args,**kwargs):
    del self._parts[:]
    return self._add_part(*args,**kwargs)

  def set_part(self,*args,**kwargs):
    with self._set_part(*args,**kwargs):
      pass


  def format_part(self, *args, **kwargs):
    for p in self._parts:
      p.format_text(*args,**kwargs)
      p.format_instruction(*args,**kwargs)
  format_parts = format_part


  # the emit function
  def emit(self,emitter=None):
    if emitter == None:
      emitter = self.DefaultEmitter

    if inspect.isclass( emitter ):
      return self.emit( emitter() )

    if not emitter is None and hasattr(emitter,'__call__'):
      return emitter(self)

    raise RuntimeError("Unknown emitter type '%s' given." % emitter)


class PlainTextQuestion(Question):
  pass

class LatexQuestion(Question):
  pass
