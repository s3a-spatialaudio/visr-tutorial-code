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
File vbap_l2_panner

Define a VISR atomic component to calculate panning gains using a combined L1/L2
optimization approach
"""

import visr
import pml
import objectmodel

import numpy as np
import cvxpy

cvxpyMajorVersion = int(cvxpy.__version__.split('.')[0])

from helper.vectorFunctions import normalise

class VbapL2Panner( visr.AtomicComponent ):
    """
    Component to calculate panning gains from point sources in an object vector.
    """
    def __init__( self, context, name, parent,
                 numObjects, lspArray ):
        """
        Constructor.

        Parameters:
        -----------

        self:
            The object handle (mandatory argument for Python methods)
        context: visr.SignalFlowContext
            A context object containing the sampling frequency and the block size.
            That's a mandatory parameter for VISR components.
        name: string
            Name of the component to be identified within a containing component.
        parent: visr.Compositcomponent
            A containing component, or None if this is the top-level component.
        numObjects: int
            The number of objects for which gains are computed.
        lspArray: panning.LoudspeakerArray
            Object containing the loudspeaker positions.
        """
        super().__init__( context, name, parent ) # Call the base class contructor (mandatory)
        # Instantiate a parameter input for type "ObjectVector"
        self.objectIn = visr.ParameterInput( "objects", self,
            pml.ObjectVector.staticType,
            pml.DoubleBufferingProtocol.staticType,
            pml.EmptyParameterConfig() )
        # Store the loudspeaker positions in a data member.
        self.L = normalise( lspArray.positions().T, norm=2, axis=0 )
        # We need the number of real loudspeakers because there might be imaginary/virtual
        # loudspeakers in the config.
        self.numSpeakers = lspArray.numberOfRegularLoudspeakers
        # Instantiate a parameter output for the gain matrices.
        self.gainOut = visr.ParameterOutput( "gains", self,
            pml.MatrixParameterFloat.staticType,
            pml.SharedDataProtocol.staticType,
            pml.MatrixParameterConfig( self.numSpeakers, numObjects ) )
        # %% Set up the optimisation problems.
        self.g = cvxpy.Variable( self.L.shape[1] )
        self.b = cvxpy.Parameter( self.L.shape[0] )
        self.prob1 = cvxpy.Problem( cvxpy.Minimize( cvxpy.norm( self.g, 1 ) ),
          [ self.L @ self.g == self.b, self.g >= 0.0 ] )
        # Note: incompatible syntax
        if cvxpyMajorVersion < 1:
            self.l1min = cvxpy.Parameter( sign='positive' )
            self.prob2 = cvxpy.Problem( cvxpy.Minimize( cvxpy.norm( self.g, 2 ) ),
                                       [ self.L @ self.g == self.b,
                                        cvxpy.sum_entries( self.g ) == self.l1min,
                                        self.g >= 0.0 ] )
        else:
            self.l1min = cvxpy.Parameter( nonneg = True )
            self.prob2 = cvxpy.Problem( cvxpy.Minimize( cvxpy.norm( self.g, 2 ) ),
                                       [ self.L @ self.g == self.b,
                                        cvxpy.sum( self.g ) == self.l1min,
                                        self.g >= 0.0 ] )

    def process( self ):
        """
        Process funtcioy called in every iteration.
        """
        # Check whether there is a new object vector input.
        if self.objectIn.protocol.changed():
            self.objectIn.protocol.resetChanged()
            # Access the new data.
            objVec = self.objectIn.protocol.data()
            # Retrieve the output parameter to be set.
            gains = np.asarray( self.gainOut.protocol.data() )
            # Perform the calculation for all point sources in the object vector.
            for obj in [o for o in objVec
             if isinstance( o, objectmodel.PointSource )]:
                try:
                    self.b.value = obj.position
                    self.prob1.solve(solver=cvxpy.ECOS)
                    if self.prob1.status != cvxpy.OPTIMAL:
                        print( "Error1 status: %s" % self.prob1.status )
                        gains[:,obj.objectId] = np.NaN
                        pass
                    self.l1min.value = self.prob1.value
                    self.prob2.solve(solver=cvxpy.ECOS)
                    if self.prob2.status != cvxpy.OPTIMAL:
                        print( "Error2 status: %s" % self.prob2.status )
                        gains[:,obj.objectId] = np.NaN
                        pass
                    # Assign a column in the gain matrix for each point source.
                    # The indexing at the end of the assignment is to discard gains of virtual
                    # loudspeakers.
                    # Note: CVXPY 0.4.11 returns a 2D array, CVXPY >= 1.0 a vector.
                    if cvxpyMajorVersion < 1:
                        gains[:,obj.objectId] = normalise( self.g.value.T )[:,:self.numSpeakers]
                    else:
                        gains[:,obj.objectId] = normalise( self.g.value.T )[:self.numSpeakers]
                except Exception as ex:
                    print( "Caught exception: %s" % str(ex) )
                    gains[:,obj.objectId] = np.NaN
