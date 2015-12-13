from .Answer import *
from .Question import *
from .Quiz import *
from .Signal import *
import inspect, operator, functools

def get_bases( cls ):
  if not inspect.isclass( cls ):
    cls = cls.__class__

  for b in cls.__bases__:
    if len(b.__bases__) > 0:
      for bb in get_bases( b ):
        yield bb
    yield b

class Emitter(object):
  sig_pre_question  = Signal()
  sig_post_question = Signal()

  def __call__(self,obj):
    if hasattr( self, obj.__class__.__name__ ):
      return getattr(self, obj.__class__.__name__)(obj)

    bases = list( get_bases( obj ) )
    bases.reverse()
    for b in bases:
      if hasattr( self, b.__name__ ):
        return getattr(self, b.__name__)(obj)

    return getattr(self, 'Default')(obj)

  def Default(self,obj):
    return ""


class PlainEmitter(Emitter):
  def Default(self, obj):
    return str(obj)

  def MultipleChoiceAnswer(self, obj):
    tokens = []
    for (correct,choice) in obj.choices:
      if correct:
        tokens.append( choice )

    return ', '.join(tokens)

  def OrderedAnswer(self, obj):
    return ' -> '.join(obj.items)

  def TrueFalseAnswer(self, obj):
    if obj.answer is None:
      return "Unknown"
    if obj.answer:
      return "True"

    return "False"

  def Question(self,obj):
    return obj.question

class BbEmitter(Emitter):
  def __init__( self ):
    pass

  def get_question_type(self,obj):
    if isinstance( obj, NumericalAnswer ):
      return 'NUM'
    if isinstance( obj, MultipleChoiceAnswer ):
      if obj.num_correct() > 1:
        return 'MA'
      else:
        return 'MC'
    if isinstance( obj, TrueFalseAnswer ):
      return 'TF'
    if isinstance( obj, OrderedAnswer ):
      return 'ORD'
    if isinstance( obj, EssayAnswer ):
      return 'ESS'
    if isinstance( obj, ShortAnswer ):
      return 'SA'

  def EssayAnswer(self,obj):
    return ""

  def ShortAnswer(self,obj):
    return str(obj.text)

  def NumericalAnswer(self,obj):
    tokens = []
    tokens.append( obj.value )
    tokens.append( obj.uncertainty )

    return '\t'.join(tokens)
  
  def MultipleChoiceAnswer(self,obj):
      tokens = []
      for (correct,choice) in obj.choices:
        tokens.append( choice )
        if correct:
          tokens.append('correct')
        else:
          tokens.append('incorrect')

      return '\t'.join(tokens)

  def OrderedAnswer(self, obj):
    return '\t'.join(obj.items)

  def TrueFalseAnswer(self, obj):
    if obj.answer is None:
      return "unknown"
    if obj.answer:
      return "true"

    return "false"

  def Question(self,obj):
    answer = obj._answers[0]

    tokens = []
    tokens.append( self.get_question_type( answer ) )
    tokens.append( obj.question )
    tokens.append( answer.emit(self) )

    return '\t'.join( tokens )

  def Quiz(self,obj):
    tokens = []
    for q in obj.questions:
      tokens.append( q.emit(self) )

    return '\n'.join(tokens)



class LatexEmitter(Emitter):
  def __init__(self, listtype = 'easylist', labels = False):
    self.listtype = listtype
    self.labels = labels

  @staticmethod
  def wrap_in_environment(tokens, env):
    tokens.insert(0, r'\begin{'+env+r'}' )
    tokens.append( r'\end{'+env+'}' )

  @staticmethod
  def make_label(obj):
    return r'\label{'+str(id(obj))+r'}'

  @staticmethod
  def make_ref(obj):
    return r'\ref{'+str(id(obj))+r'}'

  def MultipleChoiceAnswer(self,obj):
    tokens = []

    for (correct,choice) in obj.choices:
      lbl = ""
      if self.labels == True:
        lbl = LatexEmitter.make_label(choice)

      if self.listtype.lower() == 'easylist':
        tokens.append( '& '+lbl+choice )
      else:
        tokens.append( r'\item '+lbl+choice )

    if self.listtype.lower() != 'easylist':
      LatexEmitter.wrap_in_environment( tokens, self.listtype.lower() )

    return '\n'.join(tokens)


  def Question(self,obj):
    tokens = []

    lbl = ""
    if self.labels == True:
      lbl = LatexEmitter.make_label(obj)

    if self.listtype.lower() == 'easylist':
      tokens.append( '& '+lbl+obj.question )
      for answer in obj._answers:
        tokens.append( answer.emit(self).replace( '& ', '&& ' ) )
      for part in obj._parts:
        tokens.append( part.emit(self).replace( '& ', '&& ' ) )
    else:
      tokens.append( r'\item '+lbl+obj.question )
      for answer in obj._answers:
        tokens.append( answer.emit(self) )
      for part in obj._parts:
        t = []
        t.append( part.emit(self) )
        LatexEmitter.wrap_in_environment( t, self.listtype.lower() )
        tokens += t

    return '\n'.join( tokens )

  def Quiz(self,obj):
    tokens = []
    i = 0
    tokens += filter( functools.partial(operator.is_not, None), self.sig_post_question(i=i,question=None) )
    for q in obj.questions:
      i += 1
      tokens += filter( functools.partial(operator.is_not, None), self.sig_pre_question(i=i,question=q) )
      tokens.append( q.emit(self) )
      tokens += filter( functools.partial(operator.is_not, None), self.sig_post_question(i=i,question=q) )
    i += 1
    tokens += filter( functools.partial(operator.is_not, None), self.sig_pre_question(i=i,question=None) )

    LatexEmitter.wrap_in_environment( tokens, self.listtype )

    return '\n'.join(tokens)


class LatexKeyEmitter(LatexEmitter):

  def MultipleChoiceAnswer(self,obj):
    tokens = []
    for cc,c in obj.choices:
      if cc:
        tokens.append( self.make_ref( c ) )

    return ', '.join(tokens)

  def NumericalAnswer(self,obj):
    tokens = []
    tokens.append( obj.latex )

    return ' '.join(tokens)

  def Question(self,obj):
    tokens = []
    tokens.append( self.make_ref( obj ) )
    t = []
    for a in obj._answers:
      t.append( a.emit(self) )
    tokens.append( ", ".join(t) )
    return " ".join(tokens)

  def Quiz(self,obj):
    tokens = []
    for q in obj.questions:
      tokens.append( q.emit(self) )

    return '\n\n'.join(tokens)

Answer.DefaultEmitter = PlainEmitter
Question.DefaultEmitter = PlainEmitter
Quiz.DefaultEmitter = PlainEmitter
BbQuiz.DefaultEmitter = BbEmitter
