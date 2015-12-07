import re
import pint
from pyErrorProp import sigfig_round

class Answer(object):
  bb_type = 'ESS'

  def __init__(self, answer=None):
    self.answer = answer

  def __str__(self):
    return str(self.answer)

  def type(self,emitter=None):
    '''Returns the blackboard question type string.'''
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        return self.bb_type

    return self.__name__


class LatexAnswer(Answer): pass

class ShortAnswer(Answer):
  bb_type = 'SA'

  def emit(self, emitter = None):
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bbquiz':
        return {'example': self.text}

      if emitter.lower() == 'bb':
        return str(self.answer)



    return str(self.answer)



class NumericalAnswer(Answer):
  bb_type = 'NUM'

  def __init__(self, quantity, units = "", uncertainty = '1%', sigfigs = 3):
    self._quant   = quantity
    self._units   = units
    self._unc     = uncertainty
    self.sigfigs  = sigfigs
  
  @property
  def quantity(self):
    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( self._quant )

  @quantity.setter
  def quantity(self,v):
    self._quant = v

  def _get_mag(self):
    val = self._quant
    if isinstance( self._quant, pint.measurement._Measurement ):
      val = self._quant.value.magnitude
    elif isinstance( self._quant, pint.quantity._Quantity):
      val = self._quant.magnitude

    return val

  @property
  def value(self):
    val = self._get_mag()
    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( val )

  @property
  def uncertainty(self):

    unc = self._unc

    if isinstance( self._unc, (str,unicode) ) and '%' in self._unc:
      unc = self._get_mag() * float( self._unc.replace('%','') ) / 100

    if isinstance( self._quant, pint.measurement._Measurement ):
      unc = self._quant.error.magnitude

    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( unc )

  @uncertainty.setter
  def uncertainty(self,v):
    self._unc = v

  @property
  def units(self):
    unit = self._units
    if isinstance( self._quant, pint.measurement._Measurement ):
      unit = self._quant.value.units
    elif isinstance( self._quant, pint.quantity._Quantity):
      unit = self._quant.units
    return str(unit)

  @units.setter
  def units(self,v):
    self._units = v

  def emit(self, emitter = None):
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bbquiz':
        return {'raw':         self.quantity
               ,'value':       self.value
               ,'unit':        self.units
               ,'uncertainty': self.uncertainty}

      if emitter.lower() == 'bb':
        tokens = []
        tokens.append( self.value )
        tokens.append( self.uncertainty )

        return '\t'.join(tokens)


    return self.quantity

  def __str__(self):
    return self.emit()

class MultipleChoiceAnswer(Answer):
  bb_type = 'MC|MA'

  def type(self,emitter=None):
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        types = self.bb_type.split('|')
        return types[1] if len(self.correct) > 1 else types[0]

    return super(MultipleChoiceAnswer,self).type(emitter)

  def __init__(self):
    self.choices = []
    self.correct = set()

  def filter( self, text ):
    filtered_text = re.sub('^\s*\*\s*','',text)
    return (filtered_text != text, filtered_text)
    
  def add_choice( self, text ):
    correct,filtered_text = self.filter( text )
    self.choices.append( filtered_text )
    if correct:
      self.set_correct( len(self.choices)-1 )

  def add_choices( self, text ):
    for line in text.splitlines():
      line = line.strip()
      if len(line) > 0:
        self.add_choice( line )

  def set_correct( self, i ):
    self.correct.add( i )

  def clear_correct( self ):
    self.correct.clear()

  def num_correct( self ):
    return len(self.correct)

  def emit(self,emitter = None):
    if isinstance( emitter, (str,unicode) ):

      if emitter.lower() == 'bbquiz':
        choices = []
        for i in range( len( self.choices ) ):
          choices.append( self.choices[i] )
          if i in self.correct:
            choices[-1] = '*'+choices[-1]

        return {'choices' : choices }

      if emitter.lower() == 'bb':
        tokens = []
        for i in range( len( self.choices ) ):
          tokens.append( self.choices[i] )
          if i in self.correct:
            tokens.append('correct')
          else:
            tokens.append('incorrect')

        return '\t'.join(tokens)

    tokens = []
    for i in range( len( self.choices ) ):
      if i in self.correct:
        tokens.append( self.choices[i] )

    return ', '.join(tokens)

  def __str__(self):
    return self.emit()

