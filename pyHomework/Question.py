from .Utils import format_text

class Question(object):
  """A class representing a question.

  A question contains text, instructions, and answers.
  """
  
  def __init__(self):
    self._texts = []
    self._instructions = []
    self._answers = []
    self._images = []

    self.metadata = {}
    self.prepend_instructions = False
    self.join_str = ' '

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
    else:
      X.append(val)

  def clear_X(self,X):
    del X[:]

  def set_X(self, X, val):
    self.clear_X(X)
    self.add_X(X,val)

  def format_X(self,X,*args,**kwargs):
    if not 'formatter' in kwargs:
      kwargs['formatter'] = 'template'
    for i in range(len(X)):
      X[i] = format_text( X[i], *args, **kwargs )



  @property
  def text(self):
    return self.join_X(self._texts)

  @property
  def instructions(self):
    return self.join_X(self._instructions)
  
  @property
  def question(self):
    tmp = [self.text]
    if self.prepend_instructions:
      tmp.insert(0,self.instructions)
    else:
      tmp.append(self.instructions)

    return self.join_X( tmp )

  def add_text(self,v,prepend=False):
    return self.add_X(self._texts,v,prepend)

  def add_instruction(self,v,prepend=False):
    return self.add_X(self._instructions,v,prepend)

  def add_answer(self,v,prepend=False):
    return self.add_X(self._answers,v,prepend)

  def set_text(self,v):
    return self.set_X(self._texts,v)

  def set_instruction(self,v):
    return self.set_X(self._instructions,v)

  def set_answer(self,v):
    return self.set_X(self._answers,v)

  def format_text(self, *args, **kwargs):
    return self.format_X(self._texts,*args,**kwargs)
  format_texts = format_text

  def format_instruction(self, *args, **kwargs):
    return self.format_X(self._instructions,*args,**kwargs)



class PlainTextQuestion(Question):
  pass

class LatexQuestion(Question):
  pass
