Modified version of libelas for Middlebury stereo evaluation
included in the SDK with permission by Andreas Geiger

Daniel Scharstein, June 5 2014
updated to latest version of libelas on Oct 15, 2014

see original README.TXT for license

NOTE: the "run" script in this directory expects the "elas" executable in the
subdirectory "build".  To compile, do the following:

cd build
cmake ..
make

-------------------------

the file src/main.cpp was modified; the original version is in src/orig/

Changes to original version:

- new command-line interface

  usage: ./elas im0.pgm im1.pgm disp.pfm maxdisp [no_interp=0]

- saves floating-point disparities in pfm format

- parameter no_interp to control creating sparse vs dense disparity map

- output of timing information to stdout
