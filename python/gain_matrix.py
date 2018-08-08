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
File: gain_matrix.py

"""
import numpy as np

import visr
import pml

class GainMatrix( visr.AtomicComponent ):
  """
  VISR atomic component implementing a multichannel audio gain matrix.
  """
  def __init__( self, context, name, parent, nIn, nOut ):
    """
    Constructor, initializes the component.

    Parameters
    ----------

    self: GainMatrix
        Mandatory object handle for Python methods.
    context: visr.SignalFlowContext
        Object providing the sampling frequency and the period (buffer size) for the processing.
    name: string
        Name of the component, must be unique within the containing component.
    parent: visr.CompositeComponent or None
        The containing component, or None if this is a top-level component.
    nIn: int
        Number of input channels.
    nOut:int
        Number of output channels.
    """
    super().__init__( context, name, parent )
    self.audioIn = visr.AudioInputFloat( "in", self, nIn )
    self.audioOut = visr.AudioOutputFloat( "out", self, nOut )
    self.mtxIn = visr.ParameterInput( "gainInput", self,
     pml.MatrixParameterFloat.staticType,
     pml.SharedDataProtocol.staticType,
     pml.MatrixParameterConfig(nOut, nIn ))

  def process( self ):
    """
    Process function, executed for each processed audio block.
    """
    gains  = np.array( self.mtxIn.protocol.data() )
    ins = self.audioIn.data()
    self.audioOut.set( gains @ ins )
