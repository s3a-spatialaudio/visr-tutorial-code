# -*- coding: utf-8 -*-
"""
Copyright 2018 ISVR / University of Southampton

Author: Andreas Franck
"""

import visr
import pml
import panning
import rcl

from vbap_l2_panner import VbapL2Panner

class VbapL2Renderer( visr.CompositeComponent ):
    def __init__( self, context, name, parent, numberOfObjects, lspArray ):
        numLsp = lspArray.numberOfRegularLoudspeakers
        super().__init__( context, name, parent )
        self.audioIn = visr.AudioInputFloat( "in", self, numberOfObjects )
        self.audioOut = visr.AudioOutputFloat( "out", self, numLsp )
        self.objectIn = visr.ParameterInput( "objects", self,
                                            pml.ObjectVector.staticType,
                                            pml.DoubleBufferingProtocol.staticType,
                                            pml.EmptyParameterConfig()
                                            )
        self.calculator = VbapL2Panner( context, "VbapGainCalculator", self,
                                       numberOfObjects, lspArray )
        self.matrix = rcl.GainMatrix( context, "GainMatrix", self, numberOfObjects,
                                     numLsp, interpolationSteps=context.period,
                                     initialGains=0.0)
        self.audioConnection( self.audioIn, self.matrix.audioPort("in") )
        self.audioConnection( self.matrix.audioPort("out"), self.audioOut )
        self.parameterConnection( self.objectIn,
                                 self.calculator.parameterPort("objects") )
        self.parameterConnection( self.calculator.parameterPort("gains"),
                                self.matrix.parameterPort("gainInput" ) )

class RealtimeVbapL2Renderer( visr.CompositeComponent ):
    def __init__( self, context, name, parent, numberOfObjects, lspArray, nwPort ):
        super().__init__( context, name, parent )
        if not isinstance( lspArray, panning.LoudspeakerArray ):
            lspArray =  panning.LoudspeakerArray( lspArray )
        self.audioIn = visr.AudioInputFloat( "in", self, numberOfObjects )
        self.audioOut = visr.AudioOutputFloat( "out", self,
                                              lspArray.numberOfRegularLoudspeakers )
        self.receiver = rcl.UdpReceiver( context, "NetworkReceiver", self, port=nwPort)
        self.decoder = rcl.SceneDecoder( context, "SceneDecoder", self )
        self.panner = VbapL2Renderer( context, "VbapPanner", self, numberOfObjects, lspArray )
        self.audioConnection( self.audioIn, self.panner.audioPort("in") )
        self.audioConnection( self.panner.audioPort("out"), self.audioOut )
        self.parameterConnection( self.receiver.parameterPort("messageOutput"),
                                 self.decoder.parameterPort("datagramInput") )
        self.parameterConnection( self.decoder.parameterPort("objectVectorOutput"),
                                 self.panner.parameterPort("objects") )




