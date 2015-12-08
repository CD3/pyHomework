from .Question import *
from .Answer import *

class Quiz(object):
  Question = Question

  def __init__(self):
    self.questions = []
    pass

  def add_question(self,text=None):
    self.questions.append( Question(text) )

  def get_last_question( self ):
    if len( self.questions ) > 0:
      return self.questions[-1]
    else:
      return None

  def emit(self,emitter=None):
    # support for custom emitters
    if emitter is None:
      emitter = 'bb'

    if hasattr( emitter, '__call__' ):
      return emitter( self )

    if isinstance( emitter, (str,unicode)):
      if emitter == 'bbquiz':
        pass

      if emitter == 'bb':
        tokens = []
        for q in self.questions:
          tokens.append( q.emit('bb') )

        return '\n'.join(tokens)

    raise RuntimeError("Unknown emitter type '%s' given." % emitter)

  @property
  def question(self):
    return self.get_last_question()

def passthrough_fn( fn_name ):
  def func(self, *args, **kwargs):
    return getattr(self.question,fn_name)(*args,**kwargs)
  setattr(Quiz,fn_name, func)
passthroughs = ['add_text'
               ,'add_instruction'
               ,'add_answer'
               ,'set_text'
               ,'set_instruction'
               ,'set_answer'
               ,'clear_text'
               ,'clear_instruction'
               ,'clear_answer'
               ]
for p in passthroughs:
  passthrough_fn(p)

