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
File panning_auralization.py

Define a VISR component consisting of a VBAP renderer and a binaural virtual
loudspeaker renderer to auralise the loudspeaker reproduction over headphones.

This class makes uses the VISR Binaural Synthesis Toolkit.
"""

import visr
import panning

from visr_bst import VirtualLoudspeakerRenderer
# Example tracker based on the Razor AHRS tracker
# https://github.com/Razor-AHRS/razor-9dof-ahrs
from visr_bst.tracker import RazorAHRSWithUdpCalibrationTrigger

from vbap_renderer import RealtimeVbapRenderer

class PanningAuralization( visr.CompositeComponent ):
    """
    Signal flow for rendering an object-based scene over a virtual loudspeaker binaural renderer.

    This is an illustrative example, for serious application consider the
    ObjectToVirtualLoudspeakerRenderer component contained in the BST package.
    """
    def __init__( self,
                 context, name, parent,
                 *,                     # This ensures that the remaining arguments are given as keyword arguments.
                 numberOfObjects,
                 lspConfig,
                 sofaFile = None,
                 objectPort = 4242,
                 headTracking = False,
                 trackingPort = "",
                 irTruncationLength = None
                 ):
        """
        Constructor.

        Parameters
        ----------
        context : visr.SignalFlowContext
            Standard visr.Component construction argument, a structure holding the block size and the sampling frequency
        name : string
            Name of the component, Standard visr.Component construction argument
        parent : visr.CompositeComponent
            Containing component if there is one, None if this is a top-level component of the signal flow.
        lspConfig: panning.LoudspeakerArray
            Loudspeaker configuration object used in the ob ject renderer. Must not be None
        numberOfObjects: int
            The number of objects to be rendered.
        sofaFile: string
            BRIR database provided as a SOFA file. This is an alternative to the hrirPosition, hrirData
            (and optionally hrirDelays) argument. Default None means that hrirData and hrirPosition must be provided.
        headTracking: bool
            Whether dynamic headTracking is active. If True, an control input "tracking" is created.
        trackerPort: string
            OS-specific device name of the tracker-s serial port. Examples: Windows:"COM4",
            Linux: "/dev/"/dev/ttyUSB0", Mac OS: "/dev/cu.usbserial-AJ03GSC8"
        irTruncationLength: int or None
            Maximum number of samples of the BRIR impulse responses. Functional only if the BRIR is provided in a SOFA file.
        """
        # Parameter checking
        if not isinstance( lspConfig, panning.LoudspeakerArray ):
            # Try to convert automatically
            lspConfig = panning.LoudspeakerArray( lspConfig )

        super(PanningAuralization, self).__init__( context, name, parent )

        self.objectInput = visr.AudioInputFloat( "audioIn", self, numberOfObjects )
        self.binauralOutput = visr.AudioOutputFloat( "audioOut", self, 2 )

        self.objectRenderer = RealtimeVbapRenderer( context, "ObjectRenderer", self,
                                                    numberOfObjects = numberOfObjects,
                                                    lspConfig=lspConfig,
                                                    nwPort = objectPort )

        self.virtualLoudspeakerRenderer = VirtualLoudspeakerRenderer( context,
                 "VirtualLoudspeakerRenderer", self,
                 sofaFile=sofaFile,
                 headTracking=headTracking,
                 dynamicITD=False,
                 hrirInterpolation=True,
                 irTruncationLength=irTruncationLength,
                 filterCrossfading=True,
                 interpolatingConvolver=False )


        self.audioConnection( self.objectInput, self.objectRenderer.audioPort("in") )
        self.audioConnection( self.objectRenderer.audioPort("out"),
                             self.virtualLoudspeakerRenderer.audioPort("audioIn") )
        self.audioConnection( self.virtualLoudspeakerRenderer.audioPort("audioOut"), self.binauralOutput)

        if headTracking:
            self.tracker = RazorAHRSWithUdpCalibrationTrigger( context, "Tracker", self,
                                                              port=trackingPort,
                                                              calibrationPort=9999)
            self.parameterConnection( self.tracker.parameterPort("orientation"),
                                     self.virtualLoudspeakerRenderer.parameterPort("tracking"))
