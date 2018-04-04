
#------------------------------------------------------------------------------
#   Copyright (c) 2008
#       Roger Hale    roger314159@hotmail.com
#
#   This file is part of MiraMath.
#
#   MiraMath is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   MiraMath is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with MiraMath.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

'''This file is executed to fill the worksheet namespace before any equations are executed. It is shared by all equations'''

import scipy
import scipy.linalg
import scipy.fftpack
import scipy.integrate
import scipy.special
import scipy.signal


#*******************************************************************************************************************
#*Constants visible in worksheet
#*******************************************************************************************************************
___pi__          = scipy.pi
___infinity__    = scipy.inf
_e               = scipy.e


#*******************************************************************************************************************
#*Functions visible in worksheet
#*******************************************************************************************************************

#Matrix and arrays
asarray         = scipy.asarray
asmatrix        = scipy.asmatrix

def vstack(*args):
    return scipy.vstack(args)

def hstack(*args):
    return scipy.hstack(args)

def lsolve(M, v):
    return scipy.linalg.solve(M, v)

def eigenvals(m):
    return asmatrix(scipy.linalg.eigvals(m))

def eigenvecs(m):
    return asmatrix(scipy.linalg.eig(m)[1])

def zeros(*args):
    return scipy.zeros(args)

def ones(*args):
    return scipy.ones(args)

def identity(n):
    return scipy.identity(n)

def reshape(m, r, c):
    return m.reshape([r,c])

def binomial(n, k):
    num = scipy.factorial(n)*1
    denom = scipy.factorial(n-k) * scipy.factorial(k) * 1.0
    return num/denom

#Random numbers
beta            = scipy.random.beta         # Beta distribution (alpha, beta, size)
binomial        = scipy.random.binomial     # Binomial integer distribution (n trial, p probability, size=None)
chisquare       = scipy.random.chisquare    # Chisquare distribution (degrees of freedom, size)
exponential     = scipy.random.exponential  # Exponential distribution (scale=1.0, size=None)
geometric       = scipy.random.geometric    # Geometric distribution (prob success, size)
laplace         = scipy.random.laplace      # laplace(loc=0.0, scale=1.0, size=None)
logistic        = scipy.random.logistic     # logistic(loc=0.0, scale=1.0, size=None)
lognormal       = scipy.random.lognormal    # lognormal(mean=0.0, sigma=1.0, size=None)
logseries       = scipy.random.logseries    # logseries(p, size=None)
negative_binomial = scipy.random.negative_binomial # negative_binomial(n, p, size=None)
noncentral_chisquare = scipy.random.noncentral_chisquare # noncentral_chisquare(df, nonc, size=None)
poisson         = scipy.random.poisson      # Poisson distribution (lambda, size=None)
permutation     = scipy.random.permutation  # Returns a new randomly distributed sequence  (input sequence or integer which is fed into arange())
randint         = scipy.random.randint      # Random integers randint(low, high=None, size=None)
randn           = scipy.randn               # Normal float distribution (shape)
randu           = scipy.rand                # Uniform float distribution (shape)
randu8          = scipy.random.bytes        # Uniform 8-bit ints (shape)
rayleigh        = scipy.random.rayleigh     # rayleigh(scale=1.0, size=None)
uniform         = scipy.random.uniform      # uniform(low=0.0, high=1.0, size=1)

def crandu(*args):
    x = randu(*args)
    y = randu(*args)
    return x + 1j * y

def crandn(*args):
    x = randn(*args)
    y = randn(*args)
    return x + 1j * y

#FFT, etc
fft             = scipy.fftpack.fft
ifft            = scipy.fftpack.ifft
rfft            = scipy.fftpack.rfft
irfft           = scipy.fftpack.irfft
hilbert         = scipy.signal.hilbert
hilbert2        = scipy.signal.hilbert2

#Time domain windows
barthann        = scipy.signal.barthann
bartlett        = scipy.signal.bartlett
blackman        = scipy.signal.blackman
blackmanharris  = scipy.signal.blackmanharris
bohman          = scipy.signal.bohman
boxcar          = scipy.signal.boxcar
chebwin         = scipy.signal.chebwin
flattop         = scipy.signal.flattop
gaussian        = scipy.signal.gaussian
hamming         = scipy.signal.hamming
hanning         = scipy.signal.hanning
kaiser          = scipy.signal.kaiser
nuttall         = scipy.signal.nuttall
parzen          = scipy.signal.parzen
slepian         = scipy.signal.slepian
triang          = scipy.signal.triang

#Integration
trapz           = scipy.integrate.trapz
cumtrapz        = scipy.integrate.cumtrapz
simpson         = scipy.integrate.simps
romb            = scipy.integrate.romb

#Trig functions
sin             = scipy.sin
cos             = scipy.cos
tan             = scipy.tan
asin            = scipy.arcsin
acos            = scipy.arccos
atan            = scipy.arctan
cosh            = scipy.cosh
sinh            = scipy.sinh
tanh            = scipy.tanh
acosh           = scipy.arccosh
asinh           = scipy.arcsinh
atanh           = scipy.arctanh

#Special functions
log10           = scipy.log10
log             = scipy.log
exp             = scipy.exp
__zeta__        = scipy.special.zeta

#Complex numbers
arg             = scipy.angle

def Re(z):
    return scipy.real(z)*1

def Im(z):
    return scipy.imag(z)*1



#*********************************************************************************************************************
#*Hidden functions used within equation namespace, but called directly by parser generated code
#*********************************************************************************************************************
__matrix        = scipy.matrix
__sqrt          = scipy.sqrt
__divide        = lambda p, q:p/q
__determinant   = scipy.linalg.det
__conjugate     = scipy.conjugate
__absolute      = scipy.absolute

def __zeros(dimensions, dtype=float):
    return scipy.zeros(dimensions, dtype)

def __factorial(x):
    return scipy.factorial(x)*1

def __transpose(m):
    rows = asmatrix(m).shape[0]
    cols = asmatrix(m).shape[1]
    if rows == 1:
        retval = m.reshape([cols, rows])
    else:
        retval = m.T
    return retval

def __hermitian(m):
    rows = asmatrix(m).shape[0]
    cols = asmatrix(m).shape[1]
    if rows == 1:
        retval = m.reshape([cols, rows])
    else:
        retval = m.T
    return scipy.conj(retval)

def __summation(body_str, label_str, from_str, to_str, g):
    s = """scipy.sum([%s for %s in xrange(%s, %s+1)], dtype=float)""" % (body_str, label_str, from_str, to_str)
    return eval(s, g)


def __summation(func, from_val, to_val, ignore_val):
    return scipy.sum([func(dummy) for dummy in xrange(from_val, to_val+1)], dtype=float)




def __product(body_str, label_str, from_str, to_str, g):
    s = """scipy.product([%s for %s in xrange(%s, %s+1)], dtype=float)""" % (body_str, label_str, from_str, to_str)
    return eval(s, g)

def __substitution(program_string, d, g, inputvars):
    temp_dict = {}
    for k, v in d.iteritems():
        if g.has_key(k):
            temp_dict[k] = g[k]
        g[k] = v

    ret_val = eval(program_string, g)

    for k in d:
        if temp_dict.has_key(k):
            g[k] = temp_dict[k]
        else:
            del g[k]

    return ret_val

def __definite_integral(integrand_func, from_val, to_val, variable_name, g):
    return scipy.integrate.quad(integrand_func, from_val, to_val, args=())[0]

def __differentiate(function_object, variable, g):
    diff = __derivative(function_object)
    return diff(variable)


#Perform numerical differentiation
def __derivative(f):
    """Computes the numerical derivative of a function.
    And we use derivative() as follows:
    Sample function:
    def g(x): return x*x*x

    First derivative:
    dg = __derivative(g)

    Second derivative
    d2g = __derivative(dg) # ==__derivative(__derivative(g))

    Printing the value computed at a given point:
    print dg(3)
    print dg(3, 0.001)
    print dg(3, 1e-10) # smaller h is not always more precise
    """
    def df(x, h=0.1e-5):
        return ( f(x+h/2) - f(x-h/2) )/h
    return df


