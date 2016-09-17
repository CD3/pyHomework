
def Close(a,b,tol=0.001):
  ''' check that the percent difference between two values is less than some tolerance.'''
  return 2*abs(a - b) < tol*(abs(a)+abs(b))
