# local modules
from .Utils import format_text, Bunch
from .Answer import *
from .Emitter import *

# standard modules
import inspect, contextlib

# non-standard modules
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
    self._post_instructions = []
    self._pre_instructions = []
    self._answers = []
    self._parts = []

    # regular members
    self.join_str = ' '

    # config options
    self.clean_text = True
    self.auto_answer_instructions = True

    # add text if it was given
    if not text is None:
      self.add_text( text )

    # a scratch pad that can be used to store vars and stuff...
    self.scratch = Bunch()


  # other useful names for the scratchpad
  @property
  def vars(self):
    return self.scratch
  @property
  def v(self):
    return self.scratch

  def __getattr__(self,name):
    # check to see if the key is in the namespace
    if name in self.scratch:
      return self.scratch[name]

    raise AttributeError, "'Question' object has no attribute '"+name+"'"

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
    # create a context to format text with
    context = {}
    context.update(self.__dict__)
    context.update(self.scratch)
    context.update(kwargs)
    for i in range(len(args)):
      context[i] = args[i]

    for i in range(len(X)):
      X[i] = format_text( X[i], **context )


  def add_text(self,v,prepend=False):
    return self.add_X(self._texts,v,prepend)

  def set_text(self,v=None):
    return self.set_X(self._texts,v)

  def format_text(self, *args, **kwargs):
    return self.format_X(self._texts,*args,**kwargs)
  format_texts = format_text


  def add_post_instruction(self,v,prepend=False):
    return self.add_X(self._post_instructions,v.strip(),prepend)
  add_instruction = add_post_instruction

  def set_post_instruction(self,v=None):
    return self.set_X(self._post_instructions,v)
  set_instruction = set_post_instruction

  def format_post_instruction(self, *args, **kwargs):
    return self.format_X(self._post_instructions,*args,**kwargs)
  format_instruction = format_post_instruction
  format_instructions = format_instruction


  def add_pre_instruction(self,v,prepend=False):
    return self.add_X(self._pre_instructions,v.strip(),prepend)

  def set_pre_instruction(self,v=None):
    return self.set_X(self._pre_instructions,v)

  def format_pre_instruction(self, *args, **kwargs):
    return self.format_X(self._pre_instructions,*args,**kwargs)
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
  def pre_instructions_str(self):
    return self.join_X(self._pre_instructions)

  @property
  def post_instructions_str(self):
    return self.join_X(self._post_instructions)

  instructions_str = post_instructions_str
  
  @property
  def question_str(self):
    tokens = []
    if len(self._pre_instructions) > 0:
      tokens.append( self.pre_instructions_str )
    if len(self._texts) > 0:
      tokens.append( self.text_str )
    if len(self._post_instructions) > 0:
      tokens.append( self.post_instructions_str )


    return self.join_X( tokens )

  @property
  def last_part(self):
    if len( self._parts ) > 0:
      i = -1
      return self._parts[i]
    else:
      return None


  # sub-data: lists/dicts of class instances

  @contextlib.contextmanager
  def _add_answer(self,a,fmt=True,prepend=False):

    if inspect.isclass( a ):
      a = a()
    a.scratch.update(self.scratch)

    # the "magic"
    yield a
    if fmt:
      a.format_answer()


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
  def _add_part(self,text=None,fmt=True,prepend=False):
    if isinstance(text,Question): # support passing an already constructed question object
      p = text
    else:
      p = Question(text)

    p.scratch.update(self.scratch)
    # the "magic"
    yield p
    if fmt:
      p.format_question()

    self.add_X(self._parts,p,prepend)

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


  def _call(self, err, f, **kwargs):
    # get list of args required by f
    rargs = inspect.getargspec(f).args
    # build args to pass to f from our __dict__ and kwargs.
    # use the value in __dict__ unless an entry exists in kwargs

    args = dict()
    missing = list()
    for a in rargs:
      if a in kwargs:
        args[a] = kwargs[a]
      elif a in self.scratch:
        args[a] = self.scratch[a]
      elif a in self.__dict__:
        args[a] = self.__dict__[a]
      else:
        missing.append(a)

    if len(missing) > 0:
      msg  = "ERROR: could not find all arguments for function.\n"
      msg += "expected: "+str(rargs)+"\n"
      msg += "missing: "+str(missing)+"\n"
      raise RuntimeError(msg)

    if err:
      result = uconv.WithAutoError(3)(f)(**args)
    else:
      result = f(**args)

    return result

  def call(self,f,**kwargs):
    return self._call(False,f,**kwargs)

  def ecall(self,f,**kwargs):
    return self._call(True,f,**kwargs)

class PlainTextQuestion(Question):
  pass

class LatexQuestion(Question):
  pass
