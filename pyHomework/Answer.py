import re
import pint
from pyErrorProp import sigfig_round

class Answer(object):
  def __init__(self, value=None):
    self.value = value

  def __str__(self):
    return str(self.value)

class LatexAnswer(Answer): pass

class NumericalAnswer(Answer):
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
    elif isinstance( self._quant, pint.measurement._Measurement ):
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


    return self.quantity

  def __str__(self):
    return self.emit()




class MultipleChoiceAnswer(Answer):
  def __init__(self):
    self.choices = []
    self.correct = []

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
      if len(line) > 0:
        self.add_choice( line )

  def set_correct( self, i ):
    self.correct.append(i)

  def clear_correct( self ):
    del self.correct[:]

  def emit(self,emitter = None):
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bbquiz':
        return {'choices' : self.choices }



    ret = ""
    if len(self.correct) > 0:
      ret = self.choices[self.correct[0]]
    for i in range(1,len(self.correct)):
      ret += ", " + self.choices[ self.correct[i] ]
    return ret

  def __str__(self):
    return self.emit()

