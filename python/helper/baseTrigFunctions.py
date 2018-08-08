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
Utility functions for angles and coordinate system transformations.
"""

import numpy as np

def deg2rad( phi ):
    return (np.pi/180.0) * phi

def rad2deg( phi ):
    return (180.0/np.pi) * phi

def cart2sph( X ):
    x = X[...,0]
    y = X[...,1]
    z = X[...,2]
    radius = np.sqrt( x*x + y*y + z*z );
    az = np.arctan2( y, x );
    el = np.arcsin( z / radius );
    return az, el, radius

def sph2cart( az, el, r ):
    (azBC, elBC, rBC ) = np.broadcast_arrays( az, el, r )
    elFactor = np.cos( elBC )
    x = np.cos( azBC ) * elFactor * rBC
    y = np.sin( azBC ) * elFactor * rBC
    z = np.sin( elBC ) * rBC
    cart = np.stack( (x,y,z), -1 )
    return cart
