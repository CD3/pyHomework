# local modules
from .Utils import format_text, Bunch
from .Emitter import *

# standard imports
import re,sys,inspect, random

# non-standard imports
import pint
from pyErrorProp.util import sigfig_round
from pyErrorProp import UncertaintyConvention
from pyErrorProp import UncertainQuantity

uconv = UncertaintyConvention()
units = uconv._UNITREGISTRY
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

class Answer(object):
  DefaultEmitter = PlainEmitter

  def __init__(self):
    # a scratch pad that can be used to store vars and stuff...
    self.scratch = Bunch()

  # other useful names for the scratchpad
  @property
  def vars(self):
    return self.scratch
  @property
  def v(self):
    return self.scratch


  def emit(self,emitter=None):
    if emitter == None:
      emitter = self.DefaultEmitter
    
    if inspect.isclass( emitter ):
      return self.emit( emitter() )

    if not emitter is None and hasattr(emitter,'__call__'):
      return emitter(self)

    raise RuntimeError("Unknown emitter type '%s' given." % emitter)

  def format_X(self,X,*args,**kwargs):
    if not 'formatter' in kwargs:
      kwargs['formatter'] = 'format'

    # if no arguments (other than the formatter) were given, use
    # our __dict__ and scratch
    if len(args) == 0 and len(kwargs.keys()) == 1:
      kwargs.update( self.__dict__ )
      kwargs.update( self.scratch )

    for i in range(len(X)):
      X[i] = format_text( X[i], *args, **kwargs )

  def format_answer(self, *args, **kwargs):
    pass


class RawAnswer(Answer):
  def __init__(self, text=None):
    super(RawAnswer,self).__init__()
    self._text = text

  @property
  def text(self):
    return self._text

  @text.setter
  def text(self,v):
    self._text = v

  @property
  def latex(self):
    return self._text

  def format_answer(self, *args, **kwargs):
    self.format_X([self._text], *args,**kwargs)

class EssayAnswer(RawAnswer):
  def __init__(self, text=None):
    super(EssayAnswer,self).__init__()
    self._text = text

  def load(self,spec):
    self.answer = spec['text']

class ShortAnswer(RawAnswer):
  def __init__(self, text=None):
    super(ShortAnswer,self).__init__()
    self._text = text

class NumericalAnswer(Answer):
  def __init__(self, quantity = None, units = "", uncertainty = '1%', sigfigs = 3):
    super(NumericalAnswer,self).__init__()
    self.quantity = quantity
    self.uncertainty = uncertainty
    self.sigfigs  = sigfigs

    self.min_relative_unc = 0.01

  def _get_mag(self,q):
    val = q
    if isinstance( q, pint.quantity._Quantity):
      val = q.magnitude

    return val

  def _get_nom(self,q):
    val = q

    if isinstance( val, UncertainQuantity._UncertainQuantity ):
      val = q.nominal

    if isinstance( val, pint.measurement._Measurement ):
      val = q.value

    return val

  def _get_unc(self,q):
    val = None

    if isinstance( q, UncertainQuantity._UncertainQuantity ):
      val = q.uncertainty

    if isinstance( q, pint.measurement._Measurement ):
      val = q.error

    return val

  @property
  def quantity(self):
    # let pint format the quantity as a string, but remove "diemensionless" from dimensionless quantities.
    return re.sub(' dimensionless$','','{{:.{:d}E}}'.format( self.sigfigs-1 ).format( self._quant ))

  @quantity.setter
  def quantity(self,v):
    if isinstance(v,(str,unicode)):
      # if value is a string, parse it into a quantity
      v = units(v)

    if isinstance( v, (int,float) ):
      # if value is an int or float, make it a dimensionless quantity
      v = Q_(v,'')

    self._quant = v

  @property
  def latex(self):
    val = self.value
    unc = self.uncertainty
    uni = self.units

    if unc == 0:
      q = Q_(val,uni)
      return '{{:.{:d}eLx}}'.format( self.sigfigs-1 ).format( q )
    else:
      q = Q_(val,uni)
      return '{{:.{:d}eLx}}'.format( self.sigfigs-1 ).format( q )
      q = UQ_(val,unc,uni)
      # this siunitx package will choke if there is a period in the uncertainty
      # so we need to remove it
      s = '{{:.{:d}ueLx}}'.format( self.sigfigs-1 ).format( q )
      uncbeg = s.find( '(' )
      uncend = s.find( ')',uncbeg )
      uncper = s.find( '.',uncbeg)
      if uncbeg < uncper and uncper < uncend:
        s = s[:uncper] + s[uncper+1:]

      return s


  @property
  def value(self):
    val = self._quant

    val = self._get_nom( val )

    val = self._get_mag(val)

    return '{{:.{:d}E}}'.format( self.sigfigs-1 ).format( val )

  @property
  def uncertainty(self):
    fmt = '{{:.{:d}E}}'.format( self.sigfigs-1 )

    # if the quantity has uncertainty, use it
    unc = self._get_unc(self._quant)

    if unc is None:

      unc = self._unc

      # if the uncertainty is None, return zero
      if unc is None:
        unc = 0*self._quant


      # if the uncertainty is a string, make a quantity
      if isinstance( unc, (str,unicode) ):
        if '%' in unc:
          unc = self._quant * float( unc.replace('%','') ) / 100
        else:
          unc = units(unc)

      # if the uncertainty is an int or float, make a dimensionless quantity
      if isinstance( unc, (int,float) ):
        unc = Q_(unc,'')

    # convert unc to units and return magnitude
    unc = self._get_mag(unc.to(self.units))

    if not self.min_relative_unc is None:
    # make sure we don't return anything less than 1% of the nominal value
      val = self._get_mag(self._get_nom(self._quant))
      if abs(self._get_mag(unc)) < self.min_relative_unc*abs(val):
        unc = 0.01*val

    return fmt.format( abs(unc) )

  @uncertainty.setter
  def uncertainty(self,v):
    self._unc = v

  @property
  def units(self):
    unit = ""
    if isinstance( self._quant, UncertainQuantity._UncertainQuantity ):
      unit = self._quant.nominal.units
    if isinstance( self._quant, pint.measurement._Measurement ):
      unit = self._quant.value.units
    elif isinstance( self._quant, pint.quantity._Quantity):
      unit = self._quant.units
    # again, don't return 'dimensionless'

    return re.sub('dimensionless','',str(unit))

  @units.setter
  def units(self,v):
    self._quant.ito(v)

  def load(self,spec):
    val = str(spec['value'])
    if len( val.strip().split() ) < 2:
      val = val + " dimensionless"

    if val.find('+/-') >= 0:
      self.quantity = UQ_(val)
    else:
      self.quantity = Q_(val)

    unc = str(spec.get('uncertainty',""))
    if unc != "":
      self.uncertainty = unc

class MultipleChoiceAnswer(Answer):
  def __init__(self):
    super(MultipleChoiceAnswer,self).__init__()
    # controlled access members
    self._choices = []
    self._order   = []
    self._correct = set()
    self._correct_regex = r'[\*\^]'

    if not hasattr(self,"randomize"): # this allows the user to set a default for all instances
      self.randomize = False
    if not hasattr(self,"add_none_answer"):
      self.add_none_answer = False
    if not hasattr(self,"default_answer"):
      self.default_answer = None


  @property
  def choices(self):
    answers = self._correct
    if len(answers) == 0 and not self.default_answer is None:
      answers.add(self.default_answer)

    for i in self.order:
      yield (i in answers,self._choices[i])
    if self.add_none_answer:
      yield (-1 in answers,"None of the above.")

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

  def format_answer(self, *args, **kwargs):
    self.format_X(self._choices,*args,**kwargs)

  def filter( self, text ):
    filtered_text = re.sub('^\s*%s\s*'%self._correct_regex,'',text)
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

  def set_correct( self, i = None ):
    if i is None:
      i = len(self._choices)

    if isinstance( i, (str,unicode) ):
      i = self.find(i)

    if i >= 0 and i < len(self._choices):
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

  def load(self,spec):
    self.clear_choices()
    self.clear_correct()
    for choice in spec['choices']:
      self.add_choice( choice )

  def find(self, pattern, exact=True):
    if exact:
      return self._choices.index(pattern)
    else:
      '''Add support for fuzzy match'''
      for i in range(len(self._choices)):
        if pattern in self._choices[i]:
          return i
        return -1

class OrderedAnswer(Answer):
  def __init__(self):
    super(OrderedAnswer,self).__init__()
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

class TrueFalseAnswer(Answer):
  def __init__(self):
    super(TrueFalseAnswer,self).__init__()
    self.answer = None

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
