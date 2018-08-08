#!/usr/bin/env python3

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
Simulate the audio rendering for two different VBAP renderers for a source moving
on a circular trajectory.
"""

import visr
#import rcl
import rrl
import objectmodel as om
import panning


import numpy as np;
import matplotlib.pyplot as plt

from vbap_l2_renderer import VbapL2Renderer
from vbap_renderer import VbapRenderer

from helper.baseTrigFunctions import sph2cart

bs = 128
samplingFrequency = 48000

numBlocks = 128

numObjects = 1

signalLength = bs * numBlocks
t = 1.0/samplingFrequency * np.arange(0,signalLength)

ctxt = visr.SignalFlowContext( bs, samplingFrequency)

lc = panning.LoudspeakerArray( '../data/bs2051-4+5+0.xml' )

numOutputChannels = lc.numberOfRegularLoudspeakers

rendererVbap = VbapRenderer( ctxt, 'renderer', None, numObjects, lspConfig=lc )
rendererL2 = VbapL2Renderer( ctxt, 'renderer', None, numObjects, lspArray=lc )

flowVbap = rrl.AudioSignalFlow( rendererVbap )
flow = rrl.AudioSignalFlow( rendererL2 )

paramInput = flow.parameterReceivePort('objects')

paramInputVbap = flowVbap.parameterReceivePort('objects')

az = np.linspace( 0, 2.0*np.pi, numBlocks )
el = 10.0 * np.pi/180.0
r = 1.0

inSig = np.zeros( (numObjects, signalLength ), dtype=np.float32 )
inSig[0,:] = 0.75*np.sin( 2.0*np.pi*88 * t )

outSigL2 = np.zeros( (numOutputChannels, signalLength ), dtype=np.float32 )
outSigVbap = np.zeros( (numOutputChannels, signalLength ), dtype=np.float32 )


for bi in range(0,numBlocks):
    # x,y,z = sph2cart( az[bi], el, r )
    ps1 = om.PointSource(0)
    # ps1.position = [x,y,z]
    ps1.position = sph2cart( az[bi], el, r )
    ps1.channels = [0]; ps1.level=1.0

    paramInput.data().set( [ps1] )
    paramInput.swapBuffers()
    outSigL2[:,bi*bs:(bi+1)*bs] = flow.process( inSig[:, bi*bs:(bi+1)*bs] )

    paramInputVbap.data().set( [ps1] )
    paramInputVbap.swapBuffers()
    outSigVbap[:,bi*bs:(bi+1)*bs] = flowVbap.process( inSig[:, bi*bs:(bi+1)*bs] )



plt.figure()
plt.plot( t, outSigL2[7,:], 'r-', label='VBAP L2' )
plt.plot( t, outSigVbap[7,:], 'b-', label='VBAP' )
plt.xlabel( 'time [s]' )
plt.ylabel( 'Amplitude' )
plt.tight_layout()
plt.gca().set_aspect( 0.25 )
