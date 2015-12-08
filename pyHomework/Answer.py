import re
import pint
import random
from pyErrorProp import sigfig_round

class Answer(object):
  bb_type = 'ESS'

  def __init__(self, answer=None):
    self.answer = answer

  def __str__(self):
    return str(self.answer)

  def type(self,emitter=None):
    '''Returns a type string for the given emitter.'''
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        return self.bb_type

    return self.__name__

  def emit(self,emitter):
    raise RuntimeError("Unknown emitter type '%s' given." % emitter)


class LatexAnswer(Answer): pass

class ShortAnswer(Answer):
  bb_type = 'SA'

  def emit(self, emitter = None):
    # default emitter
    if emitter is None or emitter == 'default':
      return str(self.answer)

    # support for user-defined emitter functions
    if not isinstance( emitter, (str,unicode) ):
      return emitter( self )

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bbquiz':
        return {'example': self.text}

      if emitter.lower() == 'bb':
        return str(self.answer)

    return super(ShortAnswer,self).emit(emitter)





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
    # default emitter
    if emitter is None or emitter == 'default':
      return self.quantity

    # support for user-defined emitter functions
    if not isinstance( emitter, (str,unicode) ):
      return emitter( self )

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
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

    return super(NumericalAnswer,self).emit(emitter)



  def __str__(self):
    return self.emit()

class MultipleChoiceAnswer(Answer):
  bb_type = 'MC|MA'

  def type(self,emitter=None):
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        types = self.bb_type.split('|')
        return types[1] if self.num_correct() > 1 else types[0]

    return super(MultipleChoiceAnswer,self).type(emitter)

  def __init__(self):
    self._choices = []
    self._order   = []
    self._correct = set()
    self.randomize = False

  @property
  def choices(self):
    for i in self.order:
      yield (i in self._correct,self._choices[i])

  @property
  def order(self):
    _order = self._order
    if self.randomize:
      random.shuffle( _order )
    for i in _order:
      yield i

  @order.setter
  def order(self,v):
    self._order = v

  def filter( self, text ):
    filtered_text = re.sub('^\s*\*\s*','',text)
    return (filtered_text != text, filtered_text)
    
  def add_choice( self, text ):
    correct,filtered_text = self.filter( text )
    i = len( self._choices )
    self._choices.append( filtered_text )
    self._order.append( i )
    if correct:
      self.set_correct( i )

  def add_choices( self, text ):
    for line in text.splitlines():
      line = line.strip()
      if len(line) > 0:
        self.add_choice( line )

  def set_correct( self, i ):
    self._correct.add( i )

  def clear_correct( self ):
    self._correct.clear()

  def num_correct( self ):
    return len(self._correct)

  def emit(self,emitter = None):
    # default emitter
    if emitter is None or emitter == 'default':
      tokens = []
      for (correct,choice) in self.choices:
        if correct:
          tokens.append( choice )

      return ', '.join(tokens)

    # support for user-defined emitter functions
    if not isinstance( emitter, (str,unicode) ):
      return emitter( self )

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bbquiz':
        choices = []
        for (correct,choice) in self.choices:
          choices.append( choice )
          if correct:
            choices[-1] = '*'+choices[-1]

        return {'choices' : choices }

      if emitter.lower() == 'bb':
        tokens = []
        for (correct,choice) in self.choices:
          tokens.append( choice )
          if correct:
            tokens.append('correct')
          else:
            tokens.append('incorrect')

        return '\t'.join(tokens)

    return super(MultipleChoiceAnswer,self).emit(emitter)


  def __str__(self):
    return self.emit()

