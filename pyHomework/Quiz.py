from .Question import *
from .Answer import *

class Quiz(object):
  Question = Question

  def __init__(self):
    self.questions = []
    pass

  def add_question(self,text):
    self.questions.append( Question() )



  def get_last_question( self ):
    if len( self.questions ) > 0:
      return self.questions
    else:
      return None

