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
File vbap_renderer.py

Define a VBAP renderer signal flow and an extended version that supports realtime
receiving of object metadata via UDP network packages.
"""

import visr
import pml
import panning
import rcl

from gain_matrix import GainMatrix

class VbapRenderer( visr.CompositeComponent ):
    """
    VISR component for rendering object audio to an arbitrary loudspeaker configuration.
    """
    def __init__( self, context, name, parent, numberOfObjects, lspConfig ):
        """
        Constructor, instantiates the component, all contained sub-components,
        and their connections.

        Parameters
        ----------

        self: VbapRenderer
            self argument, mandatory for Python methods.
        context: visr.SignalFlowContext
            A context object containing the sampling frequency and the block size.
            That is a mandatory parameter for VISR components.
        name: string
            Name of the component to be identified within a containing component.
        parent: visr.Compositcomponent
            A containing component, or None if this is the top-level component.
        numberOfObjects: int
            The maximum number of objects to be rendered.
        lspConfig: panning.LoudspeakerArray
            Object containing the loudspeaker positions.
        """
        numLsp = lspConfig.numberOfRegularLoudspeakers
        super().__init__( context, name, parent )
        self.audioIn = visr.AudioInputFloat( "in", self, numberOfObjects )
        self.audioOut = visr.AudioOutputFloat( "out", self, numLsp )
        self.objectIn = visr.ParameterInput( "objects", self,
                                            pml.ObjectVector.staticType,
                                            pml.DoubleBufferingProtocol.staticType,
                                            pml.EmptyParameterConfig()
                                            )
        self.calculator = rcl.PanningCalculator( context, "VbapGainCalculator", self,
                                                numberOfObjects, lspConfig )
        self.matrix = rcl.GainMatrix( context, "GainMatrix", self, numberOfObjects,
                                     numLsp, interpolationSteps=context.period,
                                     initialGains=0.0 )
# Uncomment this and comment the lines above to use the simple, Python-based
# GainMatrix class instead.
#        self.matrix = GainMatrix( context, "GainMatrix", self, numberOfObjects,
#                                  numLsp )
        self.audioConnection( self.audioIn, self.matrix.audioPort("in") )
        self.audioConnection( self.matrix.audioPort("out"), self.audioOut )
        self.parameterConnection( self.objectIn,
                                 self.calculator.parameterPort("objectVectorInput") )
        self.parameterConnection( self.calculator.parameterPort("vbapGains"),
                                self.matrix.parameterPort("gainInput" ) )

class RealtimeVbapRenderer( visr.CompositeComponent ):
    """
    Composite component for VBAP rendering.

    This variant adds a UDP network receiver to accept object metadata as network messages.
    """
    def __init__( self, context, name, parent, numberOfObjects, lspConfig, nwPort ):
        """
        Constructor, instantiates the component, all contained sub-components,
        and their connections.

        Parameters
        ----------

        self: VbapRenderer
            self argument, mandatory for Python methods.
        context: visr.SignalFlowContext
            A context object containing the sampling frequency and the block size.
            That is a mandatory parameter for VISR components.
        name: string
            Name of the component to be identified within a containing component.
        parent: visr.Compositcomponent
            A containing component, or None if this is the top-level component.
        numberOfObjects: int
            The maximum number of objects to be rendered.
        lspConfig: panning.LoudspeakerArray
            Object containing the loudspeaker positions.
        nwPort: int
            Port number of a UDP connection to receive object metadata messages.
        """
        super().__init__( context, name, parent )
        if not isinstance( lspConfig, panning.LoudspeakerArray ):
            lspConfig =  panning.LoudspeakerArray( lspConfig )
        self.audioIn = visr.AudioInputFloat( "in", self, numberOfObjects )
        self.audioOut = visr.AudioOutputFloat( "out", self,
                                              lspConfig.numberOfRegularLoudspeakers )
        self.receiver = rcl.UdpReceiver( context, "NetworkReceiver", self, port=nwPort)
        self.decoder = rcl.SceneDecoder( context, "SceneDecoder", self )
        self.panner = VbapRenderer( context, "VbapPanner", self, numberOfObjects, lspConfig )
        self.audioConnection( self.audioIn, self.panner.audioPort("in") )
        self.audioConnection( self.panner.audioPort("out"), self.audioOut )
        self.parameterConnection( self.receiver.parameterPort("messageOutput"),
                                 self.decoder.parameterPort("datagramInput") )
        self.parameterConnection( self.decoder.parameterPort("objectVectorOutput"),
                                 self.panner.parameterPort("objects") )
