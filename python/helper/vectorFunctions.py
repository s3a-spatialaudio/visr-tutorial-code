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
Helper functions for working with vectors.
"""

import numpy as np

def normalise( B, norm=2, axis = -1 ):
    """
    Normalise a vector or a matrix interpreted as a collection of vectors such
    that the norm of each vector is 1.

    Parameters
    ----------

    B: np.ndarray
        Vector or matrix to be normalised.
    norm: int or inf
        p-norm to be used. Default: 2 (l2/Euclidean norm)
    axis: int
        In case of a matrix, the axis index over which the vector normalisation is applied.
        Default: -1 (last dimension)
    Returns
    -------

    np.ndarray, same dimension as B.
    """
    mag = np.linalg.norm( B, ord=norm, axis=axis )
    magExp = np.expand_dims( mag, axis )
    Bnorm = B / magExp
    return Bnorm

def angleDifference( vec1, vec2, axis=-1 ):
    """
    Calculate the angle between between two vectors (or sets of vectors)
    in radian.

    Parameters
    ----------

    vec1: np.ndarray
        First vector or set of vectors (as a matrix). Standard broadcasting rules
        apply.
    vec2: np.ndarray
        Second vector or set of vectors (as a matrix). Standard broadcasting rules
        apply.
    axis: int
        Dimension index of the vectors (in case of a matrix).
        Default: -1 (last dimension)
    Returns:
        Angle in radian, same dimension as the broadcast of vec1 and vec2 minus
        the axis dimension.
    """
    dot= np.sum(normalise(vec1) * normalise(vec2), axis=axis)
    # Clipping is to avoid arguments slightly larger than 1.0 due to numerical accuracy,
    # which would lead to erroneous results of arccos().
    return np.arccos( np.clip(dot, None, 1.0) )
