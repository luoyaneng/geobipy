""" @MvNormalDistribution
Module defining a multivariate normal distribution with statistical procedures
"""
#from copy import deepcopy
import numpy as np
from ...base  import customFunctions as cf
from .baseDistribution import baseDistribution
from ..core import StatArray
from scipy.stats import multivariate_normal

class MvNormal(baseDistribution):
    """Class extension to geobipy.baseDistribution

    Handles a multivariate normal distribution.  Uses Scipy to evaluate probabilities, 
    but Numpy to generate random samples since scipy is slow.

    MvNormal(mean, variance, ndim, prng)

    Parameters
    ----------
    mean : scalar or array_like
        Mean(s) for each dimension
    variance : scalar or array_like
        Variance for each dimension
    ndim : int, optional
        The number of dimensions in the multivariate normal.
        Only used if mean and variance are scalars that are constant for all dimensions
    prng : numpy.random.RandomState, optional
        A random state to generate random numbers. Required for parallel instantiation.
        
    Returns
    -------
    out : MvNormal
        Multivariate normal distribution.

    """

    def __init__(self, mean, variance, ndim=None, log=False, prng=None):
        """ Initialize a normal distribution
        mu:     :Mean of the distribution
        sigma:  :Standard deviation of the distribution

        """

        if (type(variance) is float): variance = np.float64(variance)

        baseDistribution.__init__(self, prng)

        if ndim is None:
            self._mean = np.copy(mean)

            # Variance
            ndim = np.ndim(variance)
            if ndim == 0:
                self._variance = np.full(np.size(mean), fill_value=variance)

            elif ndim == 1:
                assert np.size(variance) == np.size(mean), Exception('Mismatch in size of mean and variance')
                self._variance = np.asarray(variance)

            elif ndim == 2:
                assert np.all(np.equal(variance.shape,  np.size(mean))), ValueError('Covariance must have same dimensions as the mean')
                self._variance = np.asarray(variance)

            self._constant = False

        else:

            assert np.size(mean) == 1, ValueError("When specifying ndim, mean must be a scalar.")
            assert np.size(variance) == 1, ValueError("When specifying ndim, variance must be a scalar.")

            ndim = np.maximum(1, ndim)
            self._constant = True
            self._mean = np.full(ndim, fill_value=mean)
            self._variance = np.full(ndim, fill_value=variance)
    
        self.log = log
        if log:
            self._mean = np.log(self._mean)


    @property
    def mean(self):
        return np.exp(self._mean) if self.log else self._mean

    @mean.setter
    def mean(self, values):
        self._mean[:] = np.log(values) if self.log else values

    @property
    def multivariate(self):
        return True

    @property
    def ndim(self):
        return np.size(self.mean)

    @ndim.setter
    def ndim(self, newDimension):
        if newDimension == self.ndim:
            return
        assert newDimension > 0, ValueError("Cannot have zero dimensions.")
        assert self._constant, ValueError("Cannot change the dimension of a non-constant multivariate distribution.")
        if np.ndim(self.mean) == 0:
            mean = self._mean
        else:
            mean = self._mean[0]

        if np.ndim(self.variance) == 0:
            variance = self.variance
        else:
            variance = self.variance[0]

        self._mean = np.full(newDimension, fill_value=mean)
        self._variance = np.full(newDimension, fill_value=variance)


    @property
    def std(self):
        return np.sqrt(self.variance)

    @property
    def variance(self):
        return self._variance

    @property
    def inverseVariance(self):
        return cf.Inv(self._variance)

    def deepcopy(self):
        """ Define a deepcopy routine """
        if self._constant:
            return MvNormal(mean=self.mean[0], variance=self.variance[0], ndim=self.ndim, log=self.log, prng=self.prng)
        else:
            return MvNormal(mean=self.mean, variance=self.variance, log=self.log, prng=self.prng)


    def derivative(self, x, order):

        assert order in [1, 2], ValueError("Order must be 1 or 2.")
        if order == 1:
            if self.log:
                x = np.log(x)

            return cf.Ax(self.inverseVariance, x - self._mean)
        elif order == 2:
            return self.inverseVariance


    def rng(self, size = 1):
        """  """

        variance = np.squeeze(self.variance)
        if variance.ndim == 0:
            values = np.sqrt(variance) * self.prng.randn(size) + self._mean
        elif (variance.ndim == 1):
            values = self.prng.multivariate_normal(self._mean, np.diag(variance), size)
        else:
            values = np.squeeze(self.prng.multivariate_normal(self._mean, variance, size))
        
        return np.exp(values) if self.log else values


    def probability(self, x, log):
        """ For a realization x, compute the probability """

        if self.log:
            x = np.log(x)

        if log:

            N = np.size(x)
            nD = self.mean.size

            mean = self._mean
            if (nD == 1):
                mean = np.repeat(self._mean, N)
            else:
                assert (N == nD), TypeError('size of samples {} must equal number of distribution dimensions {} for a multivariate distribution'.format(N, nD))

            nD = self.variance.size
            variance = self.variance
            if nD == 1:
                variance = np.float(variance)

            # return multivariate_normal.logpdf(x, mean, self.variance.copy())
            
            # For a diagonal matrix, the log determinant is the cumulative sum of
            # the log of the diagonal entries

            tmp = cf.LogDet(variance, N)
            dv = 0.5 * tmp
            # subtract the mean from the samples
            xMu = x - mean
            # Start computing the exponent term
            # e^(-0.5*(x-mu)'*inv(cov)*(x-mu))                        (1)
            # Take the inverse of the variance
            tmp = cf.Inv(variance)
            # Compute the multiplication on the right of equation 1
            iv = cf.Ax(tmp, xMu)
            tmp = 0.5 * np.dot(xMu, iv)
            # Probability Density Function
            prob = -(0.5 * N) * np.log(2.0 * np.pi) - dv - tmp
            tmp = np.float64(prob)
            return tmp

        else:
            
            N = x.size
            nD = self.mean.size

            assert (N == nD), TypeError('size of samples {} must equal number of distribution dimensions {} for a multivariate distribution'.format(N, nD))
            # For a diagonal matrix, the determinant is the product of the diagonal
            # entries
            dv = cf.Det(self.variance)
            # print(dv)
            # subtract the mean from the samples.
            xMu = x - self._mean
            # Take the inverse of the variance
            tmp = cf.Inv(self.variance)
            iv = cf.Ax(tmp, xMu)
            exp = np.exp(-0.5 * np.dot(xMu, iv))
            # Probability Density Function
            prob = (1.0 / np.sqrt(((2.0 * np.pi)**N) * dv)) * exp
            return prob

    def summary(self, out=False):
        msg = 'MV Normal Distribution: \n'
        msg += '    Mean: ' + str(self.mean) + '\n'
        msg += '    Variance: ' + str(self.variance) + '\n'
        
        return msg if out else print(msg)
    

    def pad(self, N):
        """ Pads the mean and variance to the given size
        N: Padded size
        """
        if (self.variance.ndim == 1):
            return MvNormal(np.zeros(N,dtype=self.mean.dtype),np.zeros(N, dtype=self.variance.dtype), log=self.log, prng=self.prng)
        if (self.variance.ndim == 2):
            return MvNormal(np.zeros(N,dtype=self.mean.dtype),np.zeros([N,N], dtype=self.variance.dtype), log=self.log, prng=self.prng)


    def bins(self, nBins=100, nStd=4.0, axis=None):
        """Discretizes a range given the mean and variance of the distribution 
        
        Parameters
        ----------
        nBins : int, optional
            Number of bins to return.
        nStd : float, optional
            The bin edges = mean +- nStd * variance.
        dim : int, optional
            Get the bins of this dimension, if None, returns bins for all dimensions.
        
        Returns
        -------
        bins : geobipy.StatArray
            The bin edges.

        """
        
        nStd = np.float64(nStd)
        nD = self.ndim
        if (nD > 1):
            if axis is None:
                bins = np.empty([nD, nBins+1])
                for i in range(nD):
                    tmp = nStd * np.sqrt(self.variance[i])
                    bins[i, :] = np.linspace(self._mean[i] - tmp, self._mean[i] + tmp, nBins+1)
                values = np.squeeze(bins)
            else:
                bins = np.empty(nBins+1)
                tmp = nStd * np.sqrt(self.variance[axis])
                bins[:] = np.linspace(self._mean[axis] - tmp, self._mean[axis] + tmp, nBins+1)
                values = np.squeeze(bins)

        else:
            tmp = nStd * np.sqrt(self.variance)
            values = np.squeeze(np.linspace(self._mean - tmp, self._mean + tmp, nBins+1))

        return StatArray.StatArray(np.exp(values)) if self.log else StatArray.StatArray(values)
