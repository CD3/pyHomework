'''
Unit support for numpy array calculations.
'''

import numpy as np
from pyErrorProp import UncertaintyConvention

uconv = UncertaintyConvention()
units = uconv._UNITREGISTRY
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def unitof(q):
  if isinstance(q,Q_):
    return q.units
  else:
    return Q_(1,"dimensionless").units

def magof(q):
  if isinstance(q,Q_):
    return q.magnitude
  else:
    return q

def dot(v1,v2):
  w = sum( [ x[0]*x[1] for x in zip(v1,v2) ] )
  return w

def cross(v1,v2):
  u1 = unitof( v1 )
  u2 = unitof( v2 )
  w  = np.cross(v1,v2)
  return w*Q_(1,u1)*Q_(1,u2)

def magnitude( vec ):
  return np.sqrt( dot( vec, vec ) )

def direction( vec ):
  ret = np.arctan2( vec[1], vec[0] )
  if ret < Q_(0,'radian'):
    ret += Q_(2*3.14159,'radian')
  return ret

def make_vec( components ):
  u = unitof( components[0] )
  c = [ magof(x.to(u)) for x in components ]
  return Q_(c,u)


null = np.array( [0,0,0] )
xhat = np.array( [1,0,0] )
yhat = np.array( [0,1,0] )
zhat = np.array( [0,0,1] )
