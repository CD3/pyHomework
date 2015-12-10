from .Answer import *
from .Question import *
from .Quiz import *

class Emitter(object):
  def __call__( self,obj):
    if hasattr( self, obj.__class__.__name__ ):
      return getattr(self, obj.__class__.__name__)(obj)

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
  def __init__(self, listtype = 'easylist'):
    self.listtype = listtype

  def wrap_in_environment(self, tokens, env ):
    tokens.insert(0, r'\begin{'+env+r'}' )
    tokens.append( r'\end{'+env+'}' )

  def MultipleChoiceAnswer(self,obj):
    tokens = []

    if self.listtype.lower() == 'easylist':
      for (correct,choice) in obj.choices:
        tokens.append( '& '+choice )

    else:
      for (correct,choice) in obj.choices:
        tokens.append( r'\item '+choice )

      self.wrap_in_environment( tokens, self.listtype.lower() )

    return '\n'.join(tokens)


  def Question(self,obj):
    tokens = []

    if self.listtype.lower() == 'easylist':
      tokens.append( '& '+obj.question )
      for answer in obj._answers:
        tokens.append( answer.emit(self).replace( '& ', '&& ' ) )
      for part in obj._parts:
        tokens.append( part.emit(self).replace( '& ', '&& ' ) )
    else:
      tokens.append( r'\item '+obj.question )
      for answer in obj._answers:
        tokens.append( answer.emit(self) )
      for part in obj._parts:
        t = []
        t.append( part.emit(self) )
        self.wrap_in_environment( t, self.listtype.lower() )
        tokens += t

    return '\n'.join( tokens )

  def Quiz(self,obj):

      tokens = []
      for q in self.questions:
        tokens.append( q.emit(emitter) )

      self.wrap_in_environment( tokens, self.listtype )

      return '\n'.join(tokens)

Answer.DefaultEmitter = PlainEmitter
Question.DefaultEmitter = PlainEmitter
Quiz.DefaultEmitter = PlainEmitter
