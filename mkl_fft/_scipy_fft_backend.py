#!/usr/bin/env python
# Copyright (c) 2019-2020, Intel Corporation
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Intel Corporation nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from . import _pydfti
from . import _float_utils
import mkl

import scipy.fft as _fft

# Complete the namespace (these are not actually used in this module)
from scipy.fft import (
    dct, idct, dst, idst, dctn, idctn, dstn, idstn,
    hfft2, ihfft2, hfftn, ihfftn,
    fftshift, ifftshift, fftfreq, rfftfreq,
    get_workers, set_workers
)

from numpy.core import (array, asarray, shape, conjugate, take, sqrt, prod)

__all__ = ['fft', 'ifft', 'fft2', 'ifft2', 'fftn', 'ifftn',
           'rfft', 'irfft', 'rfft2', 'irfft2', 'rfftn', 'irfftn',
           'hfft', 'ihfft', 'hfft2', 'ihfft2', 'hfftn', 'ihfftn',
           'dct', 'idct', 'dst', 'idst', 'dctn', 'idctn', 'dstn', 'idstn',
           'fftshift', 'ifftshift', 'fftfreq', 'rfftfreq', 'get_workers',
           'set_workers', 'next_fast_len']

__ua_domain__ = 'numpy.scipy.fft'
__implemented = dict()

def __ua_function__(method, args, kwargs):
    """Fetch registered UA function."""
    fn = __implemented.get(method, None)
    if fn is None:
        return NotImplemented
    return fn(*args, **kwargs)


def _implements(scipy_func):
    """Decorator adds function to the dictionary of implemented UA functions"""
    def inner(func):
        __implemented[scipy_func] = func
        return func

    return inner


def _unitary(norm):
    if norm not in (None, "ortho"):
        raise ValueError("Invalid norm value %s, should be None or \"ortho\"."
                         % norm)
    return norm is not None


def _cook_nd_args(a, s=None, axes=None, invreal=0):
    if s is None:
        shapeless = 1
        if axes is None:
            s = list(a.shape)
        else:
            s = take(a.shape, axes)
    else:
        shapeless = 0
    s = list(s)
    if axes is None:
        axes = list(range(-len(s), 0))
    if len(s) != len(axes):
        raise ValueError("Shape and axes have different lengths.")
    if invreal and shapeless:
        s[-1] = (a.shape[axes[-1]] - 1) * 2
    return s, axes


def _tot_size(x, axes):
    s = x.shape
    if axes is None:
        return x.size
    return prod([s[ai] for ai in axes])


@_implements(_fft.fft)
def fft(a, n=None, axis=-1, norm=None, overwrite_x=False, workers=None):
    x = _float_utils.__upcast_float16_array(a)
    output = _pydfti.fft(x, n=n, axis=axis, overwrite_x=overwrite_x)
    if _unitary(norm):
        output *= 1 / sqrt(output.shape[axis])
    return output


@_implements(_fft.ifft)
def ifft(a, n=None, axis=-1, norm=None, overwrite_x=False, workers=None):
    x = _float_utils.__upcast_float16_array(a)
    output = _pydfti.ifft(x, n=n, axis=axis, overwrite_x=overwrite_x)
    if _unitary(norm):
        output *= sqrt(output.shape[axis])
    return output


@_implements(_fft.fft2)
def fft2(a, s=None, axes=(-2,-1), norm=None, overwrite_x=False, workers=None):
    x = _float_utils.__upcast_float16_array(a)
    output = _pydfti.fftn(x, shape=s, axes=axes, overwrite_x=overwrite_x)
    if _unitary(norm):
        factor = 1
        for axis in axes:
            factor *= 1 / sqrt(output.shape[axis])
        output *= factor
    return output


@_implements(_fft.ifft2)
def ifft2(a, s=None, axes=(-2,-1), norm=None, overwrite_x=False, workers=None):
    x = _float_utils.__upcast_float16_array(a)
    output = _pydfti.ifftn(x, shape=s, axes=axes, overwrite_x=overwrite_x)
    if _unitary(norm):
        factor = 1
        _axes = range(output.ndim) if axes is None else axes
        for axis in _axes:
            factor *= sqrt(output.shape[axis])
        output *= factor
    return output


@_implements(_fft.fftn)
def fftn(a, s=None, axes=None, norm=None, overwrite_x=False, workers=None):
    x = _float_utils.__upcast_float16_array(a)
    output = _pydfti.fftn(x, shape=s, axes=axes, overwrite_x=overwrite_x)
    if _unitary(norm):
        factor = 1
        _axes = range(output.ndim) if axes is None else axes
        for axis in _axes:
            factor *= 1 / sqrt(output.shape[axis])
        output *= factor
    return output


@_implements(_fft.ifftn)
def ifftn(a, s=None, axes=None, norm=None, overwrite_x=False, workers=None):
    x = _float_utils.__upcast_float16_array(a)
    output = _pydfti.ifftn(x, shape=s, axes=axes, overwrite_x=overwrite_x)
    if _unitary(norm):
        factor = 1
        _axes = range(output.ndim) if axes is None else axes
        for axis in _axes:
            factor *= sqrt(output.shape[axis])
        output *= factor
    return output


@_implements(_fft.rfft)
def rfft(a, n=None, axis=-1, norm=None):
    x = _float_utils.__upcast_float16_array(a)
    unitary = _unitary(norm)
    x = _float_utils.__downcast_float128_array(x)
    if unitary and n is None:
        x = asarray(x)
        n = x.shape[axis]
    output = _pydfti.rfft_numpy(x, n=n, axis=axis)
    if unitary:
        output *= 1 / sqrt(n)
    return output


@_implements(_fft.irfft)
def irfft(a, n=None, axis=-1, norm=None):
    x = _float_utils.__upcast_float16_array(a)
    x = _float_utils.__downcast_float128_array(x)
    output = _pydfti.irfft_numpy(x, n=n, axis=axis)
    if _unitary(norm):
        output *= sqrt(output.shape[axis])
    return output


@_implements(_fft.rfft2)
def rfft2(a, s=None, axes=(-2, -1), norm=None):
    x = _float_utils.__upcast_float16_array(a)
    x = _float_utils.__downcast_float128_array(a)
    return rfftn(x, s, axes, norm)


@_implements(_fft.irfft2)
def irfft2(a, s=None, axes=(-2, -1), norm=None):
    x = _float_utils.__upcast_float16_array(a)
    x = _float_utils.__downcast_float128_array(x)
    return irfftn(x, s, axes, norm)


@_implements(_fft.rfftn)
def rfftn(a, s=None, axes=None, norm=None):
    unitary = _unitary(norm)
    x = _float_utils.__upcast_float16_array(a)
    x = _float_utils.__downcast_float128_array(x)
    if unitary:
        x = asarray(x)
        s, axes = _cook_nd_args(x, s, axes)

    output = _pydfti.rfftn_numpy(x, s, axes)
    if unitary:
        n_tot = prod(asarray(s, dtype=output.dtype))
        output *= 1 / sqrt(n_tot)
    return output


@_implements(_fft.irfftn)
def irfftn(a, s=None, axes=None, norm=None):
    x = _float_utils.__upcast_float16_array(a)
    x = _float_utils.__downcast_float128_array(x)
    output = _pydfti.irfftn_numpy(x, s, axes)
    if _unitary(norm):
        output *= sqrt(_tot_size(output, axes))
    return output
