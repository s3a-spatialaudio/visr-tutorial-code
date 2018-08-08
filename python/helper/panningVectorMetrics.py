# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andreas Franck <a.franck@soton.ac.uk>
# Copyright (C) 2018 University of Southampton

# Code accompanying the paper:

# Andreas Franck and Filippo Maria Fazi, “VISR – A versatile open software
# framework for audio signal processing,” in Proc. Audio Eng. Soc. 2018 Int. Conf.
# Spatial Reproduction, Tokyo, Japan, 2018.

# We kindly ask to acknowledge the use of this software in publications or software
# by citing this paper.

# The code is provided under the ISC (Internet Systems Consortium) license
# https://www.isc.org/downloads/software-support-policy/isc-license/ :

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
Functions to calculate the rv (Makita or velocity vector) and re (energy vectors)
to assess panning reproduction.
"""

from helper.vectorFunctions import normalise

import numpy as np

def rv( g, L ):
    """
    Calculate the velocity (Makita) vector for a set of panning gains.

    Parameters
    ----------

    g: array-like or matrix-like.
        Vector of panning gains (or matrix in case of multiple directions
        computed at once)
    L: np.ndarray
        Unit loudspeaker direction vectors, dimensions 2 x #L or 3 #L (#L is
        the number of )
    Returns
    -------
    rv: np.ndarray
        Unnormalised velocity vector(s).
    rvDir: np.ndarray
        Normalised velocity vector(s), unit vectors containing the direction.
    rvMag:
        Magnitude(s) of the velocity vectors.
    """
    rVec = L @ g.T
    mag = np.sum( g, axis = -1 )
    rv = rVec / mag
    rvDir = normalise( rv, norm=2, axis=0 )
    rvMag = np.linalg.norm( rv, ord=2, axis = 0 )
    return rv, rvDir, rvMag

def re( g, L ):
    """
    Calculate the energy vector for a set of panning gains.

    Parameters
    ----------

    g: array-like or matrix-like.
        Vector of panning gains (or matrix in case of multiple directions
        computed at once)
    L: np.ndarray
        Unit loudspeaker direction vectors, dimensions 2 x #L or 3 #L (#L is
        the number of )
    Returns
    -------
    rv: np.ndarray
        Unnormalised energy vector(s).
    rvDir: np.ndarray
        Normalised energy vector(s), unit vectors containing the direction.
    rvMag:
        Magnitude(s) of the energy vectors.
    """
    rVec = L @ (g**2).T
    magSqr = np.sum( g**2, axis = -1 )
    re = rVec / magSqr
    reDir = normalise( re, norm=2, axis=0 )
    reMag = np.linalg.norm( re, ord=2, axis = 0 )
    return re, reDir, reMag
