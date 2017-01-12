import sympy as sy

class SymbolCollection:
  def __init__(self):
    # add a - z and A - Z
    sys = sy.symbols('a:Z')
    for s in sys:
      setattr( self, s.__str__(), s )

    # some greek letters

    self.phi = sy.symbols(r'\phi')
    self.the = sy.symbols(r'\theta')
    self.psi = sy.symbols(r'\psi')
    self.pi  = sy.symbols(r'\pi')
    self.tau = sy.symbols(r'\tau')

    # some useful special symbols
    # common unit vectors
    self.rhat = sy.symbols('\hat{r}')
    self.ihat = sy.symbols('\hat{i}')
    self.jhat = sy.symbols('\hat{j}')
    self.khat = sy.symbols('\hat{k}')

    # common indexed variables
    self.qi = sy.symbols('q:10')
    self.mi = sy.symbols('m:10')
    self.Ri = sy.symbols('R:10')
    self.xi = sy.symbols('x:10')
    self.vi = sy.symbols('v:10')

    # circuits
    self.emf = sy.symbols('\mathcal{E}')
    self.Vi  = sy.symbols('V_i')
    self.Vo  = sy.symbols('V_o')
    self.Vp  = sy.symbols('V_p')
    self.Ii  = sy.symbols('I_i')
    self.Io  = sy.symbols('I_o')
    self.Ip  = sy.symbols('I_p')
    self.Ni  = sy.symbols('N_i')
    self.No  = sy.symbols('N_o')
    self.Di  = sy.symbols('di')
    self.Dt  = sy.symbols('dt')

    # optics
    self.di   = sy.symbols('d_i')
    self.do   = sy.symbols('d_o')

    self.ni   = sy.symbols('n_i')
    self.nr   = sy.symbols('n_r')
    self.thi  = sy.symbols(r'\theta_i')
    self.thr  = sy.symbols(r'\theta_r')

    self.nl   = sy.symbols('n_l')
    self.nm   = sy.symbols('n_m')
    self.Rf   = sy.symbols('R_f')
    self.Rb   = sy.symbols('R_b')


    # constants
    self.g_    = sy.symbols('g_')
    self.G_    = sy.symbols('G_')
    self.k_    = sy.symbols('k_')
    self.e_    = sy.symbols('e_')
    self.c_    = sy.symbols('c_')
    self.pi_   = sy.symbols('\pi_')
    self.ep0_  = sy.symbols('\epsilon_0')
    self.mu0_  = sy.symbols('\mu_0')
    self.R_    = sy.symbols('R_')
    self.kB_    = sy.symbols('kB_')

def merge(d1,d2):
  d3 = d1.copy()
  d3.update(d2)
  return d3


class EquationsCollection:
  def __init__(self):
    self.s = SymbolCollection()
    self.c = None
    s = self.s
    c = self.c
    self.consts = dict()

    # GEOMETRY
    self.ArcLength = sy.Eq( s.s, s.the * s.r )

    self.CircumferenceCircle = sy.Eq( s.C, 2*s.pi_ * s.r )
    self.CircumferenceSquare = sy.Eq( s.C, 2*s.l + 2*s.w )

    self.AreaCircle = sy.Eq( s.A, s.pi_ * s.r * s.r )
    self.AreaSquare = sy.Eq( s.A, s.l * s.w )

    self.SurfaceAreaBox      = sy.Eq(s.A, 2*s.h*s.w + 2*s.l*s.w + 2*s.h*s.l)
    self.SurfaceAreaCube     = self.SurfaceAreaBox.subs(s.h, s.l).subs(s.w, s.l)
    self.SurfaceAreaCylinder = sy.Eq(s.A, 2*s.pi_*s.r**2 + 2*s.pi_*s.r*s.h)
    self.SurfaceAreaSphere   = sy.Eq(s.A, 4*s.pi_*s.R**2)
    self.SurfaceAreaCone     = sy.Eq(s.A, s.pi_*s.r**2 + s.pi_*s.r*s.s)

    self.VolumeBox      = sy.Eq(s.V, s.l*s.w*s.h)
    self.VolumeCube     = self.VolumeBox.subs(s.h, s.l).subs(s.w, s.l)
    self.VolumeSphere = sy.Eq( s.V, 4*s.pi_*s.R**3/3 )
    self.VolumeCylinder = sy.Eq( s.V, s.pi_*s.r**2*s.h )
    self.VolumeCone     = sy.Eq( s.V, s.pi_*s.r**2*s.h/3 )


    # MISC MATH

    self.ExpRise                   = sy.Eq( s.x, s.X*(1 - sy.exp(-s.t / s.tau) ) )
    self.ExpDecay                  = sy.Eq( s.x, s.X*sy.exp(-s.t / s.tau) )




    # PHYSICS I (Mechanics)

    self.KineticEnergy                = sy.Eq( s.K, s.m*s.v*s.v/2 )
    self.GravitationalPotentialEnergy = sy.Eq( s.U, s.m * s.g_ * s.h )

    self.KinematicPosition = sy.Eq( s.x, s.xi[0] + s.vi[0]*s.t + (s.a*s.t**2)/2 )
    self.KinematicVelocity = sy.Eq( s.v, s.vi[0] + s.a*s.t )


    # PHYSICS II (Electricity and Magnatism)

    self.CoulombForce              = sy.Eq( s.F, s.k_*s.qi[1]*s.qi[2]/s.r**2 )
    self.vCoulombForce             = sy.Eq( s.F, s.k_*s.qi[1]*s.qi[2]*s.rhat/s.r**2 )

    self.PointChargeField          = sy.Eq( s.E, s.k_*s.q/s.r**2 )
    self.vPointChargeField         = sy.Eq( s.E, s.k_*s.q*s.rhat/s.r**2 )

    self.PointChargePotential      = sy.Eq( s.V, s.k_*s.q/s.r )
    self.PotentialDiffUniformField = sy.Eq( s.V, s.E*s.x )
    self.ElectricPotentialEnergy   = sy.Eq( s.U, s.q * s.V )

    self.CapacitorEquation         = sy.Eq( s.Q, s.C*s.V )
    self.ParallelPlateCapacitor    = sy.Eq( s.C, s.k*s.ep0_*s.A/s.d )

    self.MagneticFieldCircularLoop = sy.Eq( s.B, (s.mu0_ * s.R**2 * s.i)  / ( 2*sy.sqrt(s.R**2 + s.z**2 )**3) )
    self.MagneticFieldLongWire     = sy.Eq( s.B, (s.mu0_ * s.i)  / ( 2*s.pi_*s.r ) )
    self.MagneticFieldFiniteWire   = sy.Eq( s.B, ( (s.mu0_ * s.i)  / ( 4*s.pi_*s.y ) ) * ( s.b / sy.sqrt(s.b**2 + s.y**2) - s.a / sy.sqrt(s.a**2 + s.y**2) ) )

    self.LongInductorInductance    = sy.Eq( s.L, s.mu0_*s.N*s.N*s.A/s.l )
    self.AvgInducedEmf             = sy.Eq( s.emf, -s.L * s.Di / s.Dt )
    self.InductorEnergy            = sy.Eq( s.U, s.L * s.i * s.i / 2 )

    self.ElectricalPower           = sy.Eq( s.P, s.I*s.V )
    self.ResistorPower             = sy.Eq( s.P, s.i*s.i*s.R )
    self.TransformerPower          = sy.Eq( s.Vi*s.Ii, s.Vo*s.Io )
    self.TransformerRatio          = sy.Eq( s.Vi/s.Vo, s.Ni/s.No )

    self.RLCurrentRise             = self.ExpRise.subs(  [(s.x,s.i), (s.X, s.Ip), (s.tau, s.L / s.R )] )
    self.RLCurrentDecay            = self.ExpDecay.subs( [(s.x,s.i), (s.X, s.Ip), (s.tau, s.L / s.R )] )

    self.RLVoltageRise             = self.RLCurrentRise.subs(  [(s.i,s.v),(s.Ip,s.Vp)] )
    self.RLVoltageDecay            = self.RLCurrentDecay.subs( [(s.i,s.v),(s.Ip,s.Vp)] )

    self.LensEquation          = sy.Eq( 1/s.di + 1/s.do , 1/s.f )
    self.MagnificationEquation = sy.Eq( s.m , -s.di / s.do )
    self.SnellsLaw             = sy.Eq( s.ni*sy.sin(s.thi), s.nr*sy.sin(s.thr) )
    self.LensMakersEquation    = sy.Eq( 1/s.f, ( s.nl / s.nm - 1 ) * ( 1/s.Rf - 1/s.Rb ) )


    # THERMO

    self.IdealGasLaw           = sy.Eq( s.P*s.V, s.N*s.kB_*s.T )
    self.IdealGasLawChem       = sy.Eq( s.P*s.V, s.n*s.R_*s.T )
    self.IdealGasEnergy        = sy.Eq( s.U, s.f*s.N*s.kB_*s.T/2 )


    # MISC PHYSICS

    self.SchwarzchildRadius = sy.Eq( s.r, 2*s.G_*s.m/s.c_**2)



  def set_constants(self, c):
    self.c = c
    s = self.s
    self.consts = { s.pi_   : c.Pi,
                    s.k_    : c.CoulombsConstant,
                    s.e_    : c.ElementaryCharge,
                    s.mu0_  : c.VacuumPermeability,
                    s.ep0_  : c.VacuumPermittivity,
                    s.c_    : c.SpeedOfLight,
                    s.G_    : c.GravitationalConstant,
                    s.g_    : c.GravitationalAcceleration,
                    s.R_    : c.UniversalGasConstant,
                    s.kB_   : c.BoltzmannConstant
                  }

  def eval(self, expr, vvar, context, soli = 0 ):

    if not isinstance( vvar, (tuple,list) ):
      return self.eval( expr, [vvar], context, soli )[vvar]

    ans = dict()
    for var in vvar:
      solution = sy.solve( expr, vvar, dict=True )[soli][var]
      ans[var] = expr_eval( solution, merge( context, self.consts ) )
    return ans

  def consts(self):
    return

  def subs(self, toexpr, fromexpr, var, soli = 0 ):
    '''Replace var in toexpr by solving fromexpr and substituting.'''
    sol = sy.solve( fromexpr, var )[soli]
    ret = toexpr.subs( var, sol )
    return ret

def expr_eval( expr, context = {} ):
  '''Evaluates a sympy expression with the given context.'''

  # if we have a list of expressions, evaluate each
  if isinstance( expr, list ):
    results = [ expr_eval(x,context) for x in expr ]
    return results

  # symbols that we have values for
  symbols = context.keys()
  # values of the symbols (these can be pint quantities!)
  vals = [ context[k] for k in symbols ]
  # create a lambda function that can be evaluated
  f = sy.lambdify( symbols, expr, "numpy" )
  # evaluate and return
  return f( *vals )

def Equality_eval(self, var, context, soli = 0):
  solution = sy.solve( self, var )[soli]
  ans = expr_eval( solution, context )
  return ans

try:
  from sympy.core.relational import Equality
  Equality.eval = Equality_eval
except:
  pass




