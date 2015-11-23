'''
Unit support for numpy array calculations.
'''

def unitof(q):
  if isinstance(q,Q_):
    return q.units
  else:
    return Q_("dimensionless")

def dot(v1,v2):
  u1 = unitof( v1 )
  u2 = unitof( v2 )
  w  = v1.dot(v2)
  return w*Q_(1,u1)*Q_(1,u2)

def cross(v1,v2):
  u1 = unitof( v1 )
  u2 = unitof( v2 )
  w  = np.cross(v1,v2)
  return w*Q_(1,u1)*Q_(1,u2)

def magnitude( vec ):
  return np.sqrt( dot( vec, vec ) )

def direction( vec ):
  ret = np.arctan2( vec[1], vec[0] )
  if ret < 0*units.radian:
    ret += 2*3.14159*units.radian
  return ret

null = np.array( [0,0,0] )
xhat = np.array( [1,0,0] )
yhat = np.array( [0,1,0] )
zhat = np.array( [0,0,1] )
