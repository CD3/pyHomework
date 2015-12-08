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

