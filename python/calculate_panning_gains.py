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
File calculate_panning_gains.py

Perform an offline simulation to calculate the panning gains for the 'VbapL2'
panning algorithm and compare them to the standard VBAP algorithm.
"""

import visr
import rcl
import rrl
import objectmodel as om
import panning
import numpy as np;
import matplotlib.pyplot as plt

# Import the VbapL2 panner.
from vbap_l2_panner import VbapL2Panner

from helper.baseTrigFunctions import rad2deg, sph2cart
from helper.vectorFunctions import angleDifference
from helper.panningVectorMetrics import re

# %% Define an object to set block size and sampling frequency.
# These values are not important for this kind of simulation but they need to be set.
bs = 128
samplingFrequency = 48000
ctxt = visr.SignalFlowContext( bs, samplingFrequency)

numBlocks = 360

numObjects = 1

# Load the loudspeaker configuation
lc = panning.LoudspeakerArray( '../data/bs2051-4+5+0.xml' )

numLsp = lc.numberOfRegularLoudspeakers

# Create components for the two apnning algorithms
pannerVbap = rcl.PanningCalculator( ctxt, 'vbapbCalc', None, numObjects,
                                   arrayConfig=lc )
pannerL2 = VbapL2Panner( ctxt, 'constSpread', None, numObjects,
                       lspArray=lc )

# %% Create signal flow objects for the two algorithms
flowVbap = rrl.AudioSignalFlow( pannerVbap )
flowL2 = rrl.AudioSignalFlow( pannerL2 )

# %% Retrieve parameter inputs and outputs for the two audio objects.
paramInputVbap = flowVbap.parameterReceivePort('objectVectorInput')
paramOutputVbap = flowVbap.parameterSendPort('vbapGains')

paramInputL2 = flowL2.parameterReceivePort('objects')
paramOutputL2 = flowL2.parameterSendPort('gains')

# %% Define a number of object positions in speherical coordinates.
# Here we define a set of positions in the horizontal plane with 1 degree distance.
az = np.linspace( 0.0, 2*np.pi, numBlocks )
el = 10.0*np.pi/180.0

# %% Preallocate a matrix of output gains (#numLsp x #directions)
gainsVbap = np.zeros( (numBlocks, numLsp) )
gainsL2 = np.zeros( (numBlocks, numLsp) )

# %% Run the simulation as a number of iterations, where a new source position
# is set in each iteration.
for bi in range(0,numBlocks):
    # Create a point source with a givel azimuth and elevation.
    ps1 = om.PointSource(0) # 0 is the source id.
    ps1.position = sph2cart( az[bi], el, 1.0 )
    # Set other object properties.
    ps1.channels = [0]; ps1.level=1.0

    # Send the point source as input to the VBAP panning gain calculator.
    ovVbap = paramInputVbap.data()
    ovVbap.set( [ps1] )
    # Trigger sending of a new parameter value./
    paramInputVbap.swapBuffers()
    # Run the signal flow graph for one iteration.
    flowVbap.process()
    # Obtain the computed gains from the parameter output port of the signal flow.
    gainsVbap[bi,:] = np.array(paramOutputVbap.data())[:,0]

    # Same for the VBAP L2 panner.
    ovL2 = paramInputL2.data()
    ovL2.set( [ps1] )
    paramInputL2.swapBuffers()
    flowL2.process()
    gainsL2[bi,:] = np.array(paramOutputL2.data())[:,0]


# Plot the gains for two specific loudspeakers (U+110 and U-110)
plt.figure()
plt.plot( 180/np.pi*az, gainsVbap[:,7], 'b.:', 180/np.pi*az, gainsVbap[:,8], 'b.-', label = 'VBAP' )
plt.plot( 180/np.pi*az, gainsL2[:,7], 'm.:', 180/np.pi*az, gainsL2[:,8], 'm.-', label = 'VBAP L2' )
plt.gca().legend()

# %% Compute energy vector difference
L = lc.positions()[:numLsp,...]

pDes = np.stack( sph2cart( az, el, 1 ), axis=-1 )

reVbap, reDirVbap, reMagVbap = re( gainsVbap, L.T  )
reVbapL2, reDirVbapL2, reMagVbapL2 = re( gainsL2, L.T  )

reAngleDiff = rad2deg(angleDifference( pDes.T, reDirVbap.T ) )
reAngleDiffL2 = rad2deg(angleDifference( pDes.T, reDirVbapL2.T) )

azDeg = rad2deg( az )

plt.figure()
plt.plot( azDeg, reAngleDiff, linestyle='-', color=(0.5,0.5,0.5) )
plt.plot( azDeg, reAngleDiffL2, linestyle='-', color='red' )
plt.xlabel( 'Source azimuth [deg]' )
plt.ylabel( 'Energy direction error [deg]')
plt.tight_layout()
plt.gca().set_aspect( 3 )
# Save plots and plot data
#plt.savefig( '../../figures/offline_simulation_energy_direction_difference.pdf' )
# reData = np.concatenate( (np.reshape( azDeg, (1,-1) ), np.reshape(reAngleDiff, (1,-1)), np.reshape(reAngleDiffL2, (1,-1))), axis=0 )
# np.savetxt( '../../data/offline_simulation_energy_direction_difference.dat', reData.T )

