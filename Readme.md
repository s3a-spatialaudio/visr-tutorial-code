VISR tutorial code
==================

This set contains example code for the (VISR) Versatile Interactive Scene Renderer software framework.
It accompanies the paper 

[1] Andreas Franck and Filippo Maria Fazi, “VISR – A versatile open software
framework for audio signal processing,” in Proc. Audio Eng. Soc. 2018 Int. Conf.
Spatial Reproduction, Tokyo, Japan, 2018.

We kindly ask to acknowledge the use of this software in publications or software
by citing this paper.

License
-------

Copyright (C) 2018 Andreas Franck
Copyright (C) 2018 University of Southampton

The code is provided under the ISC (Internet Systems Consortium) license
https://www.isc.org/downloads/software-support-policy/isc-license/ :

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

Usage
-----

The files are to be used with the VISR software framework, either from a prebuilt binary package
or built from the source.

The examples are based on the Python extensions, and are to be run from a Python interpreter.

Change into the code/ subdirectory to run the scripts.

Dependencies
------------

Python 3 distribution, e.g., [Anaconda3](https://www.anaconda.com/download/)
[VISR framework](http://cvssp.org/data/s3a/public/VISR) 
[VISR BST](http://cvssp.org/data/s3a/public/BinauralSynthesisToolkit/) (Binaural synthesis Toolkit) for panning auralisation
[cvxpy](www.cvxpy.org) for VBAP L2 renderer example component

Contents
--------


python/
   Contains example code files:

python/vbap_renderer.py
    Defines the VISR components VbapRenderer and RealtimeRenderer described in Sec. 3.2. of [1]
   
python/run_realtime_vbap_renderer.py 
    Run the VBAP renderer as a realtime rendering algorithm, described in Sec. 3.3 of [1]

python/run_realtime_auralization.py 
    Realtime auralization of the VBAP renderer with binaural virtual loudspeaker renderer,
	described in Sec. 3.3 of [1]

python/panning_auralization.py
    VISR component cobining a VBAP renderer and a binaural virtual loudspeaker renderer for 
	realtime auralization, as described in Sec. 3.3 of [1]
	
python/vbap_l2_panner.py
    VISR atomic component for prototyping a panning algorithm, see Sec. 3.4 of [1]
	
python/gain_matrix.py
	VISR atomic component to demonstrate the implementation of audio processing components, 
	see Sec. 3.4 of [1]
	
python/simulate_l2_renderer.py
    Offline script to simulate the audio rendering for VBAP reproduction with a circular source movement.

python/simulate_l2_renderer.py
    Offline script to calculate VBAP panning gains for different object positions
	
python/helper/
    Small utility functions (trigonometry, vector operations, panning metrics)
data/
	Contains several loudspeaker configuration files used by the renderers.
