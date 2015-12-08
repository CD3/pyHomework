import re,sys,inspect
import pint
import random
from pyErrorProp import sigfig_round
from pyErrorProp import units

class Answer(object):
  bb_type = 'NONE'
  def emit(self,emitter):
    if not emitter is None and hasattr(emitter,'__call__'):
      return emitter(self)

    raise RuntimeError("Unknown emitter type '%s' given." % emitter)

  def type(self,emitter=None):
    '''Returns a type string for the given emitter.'''
    if isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        return self.bb_type

    return self.__name__

  def __str__(self):
    return self.emit()



class EssayAnswer(object):
  bb_type = 'ESS'

  def __init__(self, text=None):
    self.text = text

  def load(self,spec):
    self.answer = spec['text']

  def emit(self,emitter=None):
    # default emitter
    if emitter is None or emitter == 'default':
      return str(self.text)

    return super(EssayAnswer,self).emit(emitter)


class LatexAnswer(Answer): pass


class ShortAnswer(Answer):
  bb_type = 'SA'

  def __init__(self, text=None):
    self.text = text

  def emit(self,emitter=None):
    # default emitter
    if emitter is None or emitter == 'default':
      emitter = 'bb'

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        return str(self.text)

    return super(ShortAnswer,self).emit(emitter)


class NumericalAnswer(Answer):
  bb_type = 'NUM'

  def __init__(self, quantity = None, units = "", uncertainty = '1%', sigfigs = 3):
    self._quant   = quantity
    self._unc     = uncertainty
    self.sigfigs  = sigfigs
  
  @property
  def quantity(self):
    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( self._quant )

  @quantity.setter
  def quantity(self,v):
    if isinstance(v,(str,unicode)):
      self._quant = unit(v)
    else:
      self._quant = v

  def _get_mag(self,q):
    val = q
    if isinstance( q, pint.measurement._Measurement ):
      val = q.value.magnitude
    elif isinstance( q, pint.quantity._Quantity):
      val = q.magnitude

    return val

  @property
  def value(self):
    val = self._get_mag(self._quant)
    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( val )

  @property
  def uncertainty(self):
    unc = self._unc

    if isinstance( self._unc, (str,unicode) ):
      if '%' in self._unc:
        unc = self._quant * float( self._unc.replace('%','') ) / 100
      else:
        unc = units(unc)

    if isinstance( self._quant, pint.measurement._Measurement ):
      unc = self._quant.error

    if isinstance( unc, pint.quantity._Quantity):
      unc = unc.to(self.units).magnitude

    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( unc )

  @uncertainty.setter
  def uncertainty(self,v):
    self._unc = v

  @property
  def units(self):
    unit = ""
    if isinstance( self._quant, pint.measurement._Measurement ):
      unit = self._quant.value.units
    elif isinstance( self._quant, pint.quantity._Quantity):
      unit = self._quant.units
    return str(unit)

  @units.setter
  def units(self,v):
    self._quant.ito(v)

  def emit(self,emitter=None):
    # default emitter
    if emitter is None or emitter == 'default':
      emitter = 'bb'

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter.lower() == 'bb':
        tokens = []
        tokens.append( self.value )
        tokens.append( self.uncertainty )

        return '\t'.join(tokens)

    return super(NumericalAnswer,self).emit(emitter)

  def load(self,spec):
    self.quantity = units( str(spec['value']) )
    self.uncertainty = spec['uncertainty'] if 'uncertainty' in spec else '1%'


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

  def clear_choices( self ):
    self._order = []
    self._choices = []

  def clear_correct( self ):
    self._correct.clear()

  def num_choices( self ):
    return len(self._choices)

  def num_correct( self ):
    return len(self._correct)

  def emit(self,emitter=None):
    # default emitter
    if emitter is None or emitter == 'default':
      emitter = 'default'


    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter == 'default':
        tokens = []
        for (correct,choice) in self.choices:
          if correct:
            tokens.append( choice )

        return ', '.join(tokens)

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

  def load(self,spec):
    self.clear_choices()
    self.clear_correct()
    for choice in spec['choices']:
      self.add_choice( choice )

class OrderedAnswer(Answer):
  bb_type = "ORD"
  def __init__(self):
    self.items = []

  def add_item( self, item ):
    self.items.append( item )

  def add_items( self, text ):
    for line in text.splitlines():
      line = line.strip()
      if len(line) > 0:
        self.add_item( line )

  def clear_items( self ):
    self.items = []

  def load(self,spec):
    self.clear_items()
    for item in spec['ordered']:
      self.add_item( item )

  def emit(self,emitter=None):
    # default emitter
    if emitter is None or emitter == 'default':
      emitter = 'default'

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter == 'default':
        return ' -> '.join(self.items)

      if emitter.lower() == 'bb':
        return '\t'.join(self.items)

    return super(OrderedAnswer,self).emit(emitter)

class TrueFalseAnswer(Answer):
  bb_type = "TF"
  def __init__(self):
    self.answer = None

  def emit(self,emitter=None):
    # default emitter
    if emitter is None or emitter == 'default':
      emitter = 'default'

    # emitters that we support
    if     isinstance( emitter, (str,unicode) ):
      if emitter == 'default':
        if self.answer is None:
          return "Unknown"
        if self.answer:
          return "True"
        if self.answer:
          return "False"

      if emitter.lower() == 'bb':
        return self.emit('default').lower()

    return super(TrueFalseAnswer,self).emit(emitter)

  def load(self,spec):
    self.answer = spec['logical']

def make_answer( spec ):
  for name,obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and issubclass( obj, Answer ):
      try:
        a = obj()
        a.load( spec )
        return a
      except:
        pass


  raise RuntimeError("Could not build answer instance from spec '%s'."%spec)
