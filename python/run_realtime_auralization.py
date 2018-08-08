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
Example script to run a realtime VBAP renderer connected to a virtual loudspeaker
auralization tool
"""


import visr
import panning
import rrl
import audiointerfaces as ai

from panning_auralization import PanningAuralization

import os
from sys import platform
from urllib.request import urlretrieve # Load SOFA files on the fly

bs = 512   # Define the period / buffer size
fs = 48000 # Define the sampling rate in Hz

# Define a SignalFlowContext object that is used to pass the sampling frequency
# and period parameter to a component's constructor.
context = visr.SignalFlowContext( bs, fs )

# Define a loudspeaker configuration file incl. VBAP triangulation
# plus a corresponding SOFA file containing BRIR impulse responses
# Note: these configurations must match.

# Stereo Configuration.
# Note: With auralisation, larger setups can be run with standard soundcards.
#configFile = '../data/stereo.xml'
#sofaFileName = 'bbcrdlr_systemA.sofa'

# Multichannel Loudspeaker configurations as defined by ITU-R BS.2051.
# Note that the speaker channels are consectutive, i.e., they differ from
# the ITU standard as they omit the channels for the subwoofers (channel 4 and 10
# for 9+10+3)
# Note: The sudio interface used must support the number of output channels.
#configFile = '../data/bs2051-0+5+0.xml'
#sofaFileName = 'bbcrdlr_systemB.sofa'

configFile = '../data/bs2051-4+5+0.xml'
sofaFileName = 'bbcrdlr_systemD.sofa'

#configFile = '../data/bs2051-9+10+3.xml'
#sofaFileName = 'bbcrdlr_systemH.sofa'

# %% Tracking support.
useTracking = False

# Specific settings for the Razor AHRS
# TODO: Check and adjust port names for the individual system
if platform == 'linux' or platform == 'linux2':
    trackingPort = "/dev/ttyUSB0"
elif platform == 'darwin':
    trackingPort = "/dev/cu.usbserial-AJ03GSC8"
elif platform in ['windows','win32']:
    trackingPort = "COM4"

# %% Search for the SOFA file and download on demand.
# The files used are described in the paper

# Chris Pike and Michael Romanov, "An Impulse Response Dataset for Dynamic
# Data-Based Auralization of Advanced Sound Systems", Proc. Audio Eng. Soc.
# 142nd Conv., May 2017, Berlin, Germany, Engineering Brief,
# http://www.aes.org/e-lib/browse.cfm?elib=18709
sofaDirectory = "../data/"
fullSofaPath = os.path.join( sofaDirectory, sofaFileName )
if not os.path.exists( fullSofaPath ):
    sofaDir = os.path.split( fullSofaPath )[0]
    if not os.path.exists( sofaDir ):
        os.makedirs( sofaDir )
    urlretrieve( 'http://data.bbcarp.org.uk/bbcrd-brirs/sofa/' + sofaFileName,
                fullSofaPath )

# Number of objects rendered.
# More objects are possible if the sound card supports a sufficient number of channels.
numObjects = 2

# Create a loudspeaker array object.
lc = panning.LoudspeakerArray( configFile )

# Instantiate the signal flow.
renderer = PanningAuralization( context, 'auraliser', None,
                               numberOfObjects = numObjects,
                               sofaFile = fullSofaPath,
                               lspConfig = lc,
                               objectPort = 4242,
                               headTracking = useTracking,
                               trackingPort = trackingPort,
                               irTruncationLength = 4096 )

# Instantiate a flow object that contains the runtime infrastructure for the renderer.
flow = rrl.AudioSignalFlow( renderer )

# Define audio interface-specific options if needed. Left empty here.
audioInterfaceOptions = "{}"

# Depending on the operating system and the sound card drivers, additional
# options might be needed. For example, this choses a particular PortAudio
# backend (on Windows)
# audioInterfaceOptions = """{ "hostapi": "WASAPI" }"""

# Instantiate an audio interface.
aIfc = ai.AudioInterfaceFactory.create(
  "PortAudio", numObjects, # numberOfInputs
  2, # Binaural output
  fs,
  bs,
  optionalConfig = audioInterfaceOptions)

# Register the renderer with the audio interface.
aIfc.registerCallback( flow )
# Start processing.
aIfc.start()

print( "Rendering started. Press <q><Return> to quit." )
while( True ):
    i = input( "Press <q><Return> to quit." )
    if i in ['q','Q']:
        break

# Stop the processing.
aIfc.stop()
aIfc.unregisterCallback()

# Cleanup.
del aIfc
del flow
del renderer
