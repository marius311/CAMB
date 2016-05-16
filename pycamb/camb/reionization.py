from .baseconfig import CAMB_Structure, dll_import, CAMBError, camblib
from ctypes import c_bool, c_int, c_double, POINTER, byref
from numpy import diff, vectorize

# ---Variables in reionization.f90
# To set the value please just put 
# variablename.value = newvalue

# logical
include_helium_fullreion = dll_import(c_bool, "reionization", "include_helium_fullreion")
# include_helium_fullreion.value = True

# logical
Reionization_AccuracyBoost = dll_import(c_bool, "reionization", "reionization_accuracyboost")
# Reionization_AccuracyBoost.value = 1.

Rionization_zexp = dll_import(c_bool, "reionization", "rionization_zexp")

CAMB_reionization_xe = camblib.__reionization_MOD_reionization_xe
CAMB_reionization_xe.argtypes = (POINTER(c_double),POINTER(c_double),POINTER(c_double))
CAMB_reionization_xe.restype = c_double


#this should only be changed simultaneously as in reionization.f90
max_reionization_redshifts = 200 


# ---Derived Types in reionization.f90

class ReionizationParams(CAMB_Structure):
    """
    Hold sparameters for the reionization model.
    """
    _fields_ = [
        ("Reionization", c_int),  # logical
        ("use_optical_depth", c_int),  # logical
        ("use_custom_xe", c_int),  # logical
        ("redshift", c_double),
        ("delta_redshift", c_double),
        ("fraction", c_double),
        ("optical_depth", c_double),
        ("helium_redshift", c_double),  # helium_redshift  = 3.5_dl
        ("helium_delta_redshift", c_double),  # helium_delta_redshift  = 0.5
        ("helium_redshiftstart", c_double),  # helium_redshiftstart  = 5._dl

        #used if use_custom_xe=True
        ("num_a", c_int),
        ("a", c_double * max_reionization_redshifts),
        ("xe", c_double * max_reionization_redshifts),
    ]

    def set_tau(self, tau, delta_redshift=None):
        """
        Set the optical depth
        :param tau: optical depth
        :param delta_redshift: delta z for reionization
        :return: self
        """
        self.use_custom_xe=False
        self.use_optical_depth = True
        self.optical_depth = tau
        if delta_redshift is not None:
            self.delta_redshift = delta_redshift
        return self

    def set_xe(self, a, xe):
        """
        Set a custom Xe(a) directly.
        :param a: array of scale factors, in descending order
        :param xe: array of free electron fractions, Xe, at each scale factor
        :return: self
        """
        n = self.num_a = len(a)
        if n>max_reionization_redshifts:
            raise CAMBError('Can only give 200 redshift bins. You can modify this max in reionization.[py,f90]')
        if not all(diff(a)<0):
            raise CAMBError("Must pass in array of scale factors in descending order")

        self.use_custom_xe = True
        self.use_optical_depth = False
        for i in range(n): 
            self.a[i]  = a[i]
            self.xe[i] = xe[i]
        return self

    @vectorize
    def get_xe(a,tau=None,xe_recomb=None):
        """
        Get Xe(a)
        :param a: scale factor
        :param tau: (optional) conformal time, might be needed by some algorthims for convenience
        :param xe_recomb: (option) starting value from recombination
        """
        if tau is None: tau=0
        if xe_recomb is None: xe_recomb=0
        return CAMB_reionization_xe(byref(c_double(a)),byref(c_double(tau)),byref(c_double(xe_recomb)))



class ReionizationHistory(CAMB_Structure):
    """
    Internally calculated parameters.
    """
    _fields_ = [
        ("tau_start", c_double),
        ("tau_complete", c_double),
        ("akthom", c_double),
        ("fHe", c_double),
        ("WindowVarMid", c_double),
        ("WindowVarDelta", c_double)
    ]
