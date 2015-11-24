try:
  import sympy
  from .sympy import *
  from .sympy.Equations import *
except:
  pass

try:
  from .numpy.quantity_calcs import *
except:
  pass

from .Constants import *
from .HomeworkAssignment import *
