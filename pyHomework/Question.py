import inspect
from .Utils import format_text
from .Emitter import *
import dpath.util

class Question(object):
  """A class representing a question.

  A question contains text, instructions, and answers.
  """
  DefaultEmitter = PlainEmitter
  
  def __init__(self, text = None):
    # controlled access members
    self._texts = []
    self._instructions = []
    self._answers = []
    self._parts = []

    # regular members
    self.prepend_instructions = False
    self.join_str = ' '

    self.clean_text = True

    if not text is None:
      self.add_text( text )

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

  # properties: getters that return processed versions of the member data

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

  # add operations

  def add_text(self,v,prepend=False):
    return self.add_X(self._texts,v.strip(),prepend)

  def add_instruction(self,v,prepend=False):
    return self.add_X(self._instructions,v.strip(),prepend)

  def add_answer(self,v,prepend=False):
    return self.add_X(self._answers,v,prepend)

  def add_part(self,v=None,prepend=False):
    if not isinstance(v, Question):
      v = Question(v)
    return self.add_X(self._parts,v,prepend)

  # set operations

  def set_text(self,v=None):
    return self.set_X(self._texts,v)

  def set_instruction(self,v=None):
    return self.set_X(self._instructions,v)

  def set_answer(self,v=None):
    return self.set_X(self._answers,v)

  def set_part(self,v=None):
    return self.set_X(self._parts,v)

  # format operations

  def format_text(self, *args, **kwargs):
    return self.format_X(self._texts,*args,**kwargs)
  format_texts = format_text

  def format_part(self, *args, **kwargs):
    for p in self._parts:
      p.format_text(*args,**kwargs)
      p.format_instruction(*args,**kwargs)
  format_parts = format_part

  def format_instruction(self, *args, **kwargs):
    return self.format_X(self._instructions,*args,**kwargs)
  format_instructions = format_instruction


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
