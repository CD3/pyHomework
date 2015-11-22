from sympy import *

class SymbolCollection:
  def __init__(self):
    # add a - z and A - Z
    sys = symbols('a:Z')
    for s in sys:
      setattr( self, s.__str__(), s )

    # some useful special symbols
    # common unit vectors
    self.rhat = symbols('\hat{r}')
    self.ihat = symbols('\hat{i}')
    self.jhat = symbols('\hat{j}')
    self.khat = symbols('\hat{k}')

    # common indexed variables
    self.qi = symbols('q:10')
    self.mi = symbols('m:10')
    self.Ri = symbols('R:10')

    # circuits
    self.emf = symbols('\mathcal{E}')
    self.Vi  = symbols('Vi')
    self.Vo  = symbols('Vo')
    self.Ii  = symbols('Ii')
    self.Io  = symbols('Io')

    # optics
    self.di   = symbols('d_i')
    self.do   = symbols('d_o')

    self.ni   = symbols('n_i')
    self.nr   = symbols('n_r')
    self.thi  = symbols('th_i')
    self.thr  = symbols('th_r')

    # constants
    self.g_    = symbols('g')
    self.k_    = symbols('k')
    self.c_    = symbols('c')
    self.pi_   = symbols('\pi')
    self.ep0_  = symbols('\epsilon_0')
    self.mu0_  = symbols('\mu_0')

class EquationsCollection:
  def __init__(self):
    self.s = SymbolCollection()
    s = self.s

    self.KineticEnergy             = Eq( s.K, s.m*s.v*s.v/2 )

    self.GravitationalPotentialEnergy = Eq( s.U, s.m * s.g_ * s.h )

    self.CoulombForce              = Eq( s.F, s.k_*s.qi[1]*s.qi[2]/s.r**2 )
    self.vCoulombForce             = Eq( s.F, s.k_*s.qi[1]*s.qi[2]*s.rhat/s.r**2 )

    self.PointChargeField          = Eq( s.E, s.k_*s.q/s.r**2 )
    self.vPointChargeField         = Eq( s.E, s.k_*s.q*s.rhat/s.r**2 )

    self.PointChargePotential      = Eq( s.V, s.k_*s.q/s.r )
    self.PotentialDiffUniformField = Eq( s.V, s.E*s.x )
    self.ElectricPotentialEnergy   = Eq( s.U, s.q * s.V )

    self.CapacitorEquation         = Eq( s.Q, s.C*s.V )
    self.ParallelPlateCapacitor    = Eq( s.C, s.k*s.ep0_*s.A/s.d )

    self.MagneticFieldCircularLoop = Eq( s.B, (s.mu0_ * s.R**2 * s.i)  / ( 2*sqrt(s.R**2 + s.z**2 )**3) )
    self.MagneticFieldLongWire     = Eq( s.B, (s.mu0_ * s.i)  / ( 2*s.pi_*s.r ) )
    self.MagneticFieldFiniteWire   = Eq( s.B, ( (s.mu0_ * s.i)  / ( 4*s.pi_*s.y ) ) * ( s.b / sqrt(s.b**2 + s.y**2) - s.a / sqrt(s.a**2 + s.y**2) ) )

    self.LensEquation          = Eq( 1/s.di + 1/s.do , 1/s.f )
    self.MagnificationEquation = Eq( s.m , -s.di / s.do )
    self.SnellsLaw             = Eq( s.ni*sin(s.thi), s.nr*sin(s.thr) )

  def eval(self, expr, var, context, soli = 0 ):
    solution = solve( expr, var )[soli]
    s = self.s
    c = self.consts
    context.update( { s.pi_ : math.pi,
                      s.k_  : c.CoulombsConstant,
                      s.mu0_  : c.VacuumPermeability,
                      s.ep0_  : c.VacuumPermittivity,
                  } )

    ans = expr_eval( solution, context )

    return ans

  def subs(self, toexpr, fromexpr, var, soli = 0 ):
    sol = solve( fromexpr, var )[soli]
    ret = toexpr.subs( var, sol )
    return ret






