from .Question import *
from .Answer import *
import dpath.util

class Quiz(object):
  Question = Question
  DefaultEmitter = None

  def __init__(self):
    self._questions = []
    self._order = []
    self._config = {}

  def config(self,key,default=None,value=None):
    if value is None:
      try:
        return dpath.util.get(self._config,key)
      except:
        return default
    else:
      dpath.util.new(self._config,key,value)

  @property
  def questions(self):
    for i in self.order:
      yield self._questions[i]

  @property
  def order(self):
    _order = self._order

    if self.config('/randomize/questions',False):
      random.shuffle( _order )
    for i in _order:
      yield i

  @order.setter
  def order(self,v):
    self._order = v

  def add_question(self,text=None):
    self._order.append( len(self._questions) )
    self._questions.append( Question(text) )

  def get_last_question( self ):
    if len( self._questions ) > 0:
      i = self._order[-1]
      return self._questions[i]
    else:
      return None

  def emit(self,emitter=None):
    if emitter == None:
      emitter = self.DefaultEmitter

    if self.config('randomize/answers', False):
      for q in self._questions:
        for a in q._answers:
          a.randomize = True

    if inspect.isclass( emitter ):
      return self.emit( emitter() )

    if not emitter is None and hasattr(emitter,'__call__'):
      return emitter(self)

    raise RuntimeError("Unknown emitter type '%s' given." % emitter)

  def load(self,spec):
    self._config = spec.get('configuration',{})
    for q in spec['questions']:
      self.add_question()
      try:
        self.add_text( q['text'] )
      except:
        raise RuntimeError("No text found in question: %s" % q)

      if 'instructions' in q:
        self.add_instruction( q['instructions'] )

      self.add_answer( make_answer(q['answer']) )

  def find(self,pattern):
    '''Find and return a question matching a search string.'''
    for q in self.questions:
      if pattern in q.question:
        return q

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

