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
Example script to run a realtime VBAP renderer from Python.
"""


import visr
import panning
import rrl
import audiointerfaces as ai

from vbap_renderer import RealtimeVbapRenderer

bs = 512   # Define the period / buffer size
fs = 48000 # Define the sampling rate in Hz

# Define a SignalFlowContext object that is used to pass the sampling frequency
# and period parameter to a component's constructor.
context = visr.SignalFlowContext( bs, fs )

# Define a loudspeaker configuration file incl. VBAP triangulation
# Stereo runs on most (including internal) soundcards.
configFile = '../data/stereo.xml'

# Multichannel Loudspeaker configurations as defined by ITU-R BS.2051.
# Note that the speaker channels are consectutive, i.e., they differ from
# the ITU standard as they omit the channels for the subwoofers (channel 4 and 10
# for 9+10+3)
# Note: The sudio interface used must support the number of output channels.
#configFile = '../data/bs2051-0+5+0.xml'
#configFile = '../data/bs2051-4+5+0.xml'
#configFile = '../data/bs2051-9+10+3.xml'

# Number of objects rendered.
# More objects are possible if the sound card supports a sufficient number of channels.
numObjects = 2

# Create a loudspeaker array object.
lc = panning.LoudspeakerArray( configFile )

# Retrieve number of loudspeakers from file.
numLsp = lc.numberOfRegularLoudspeakers

# Instantiate the signal flow.
renderer = RealtimeVbapRenderer( context, 'renderer', None, numObjects,
                              lspConfig=lc, nwPort=4242 )

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
  "PortAudio", numObjects,
  numLsp,
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
