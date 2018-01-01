// modified 11/28/2013 -- added no_interpolation option via command-line
// changed 12/6/2013 to just use the ipol_gap_width parameter for this purpose

// 11/29/2013 -- changed unknown values from -10 to INFINITY when saving as .pfm

// older changes:

// modified 10/24/2013
// got rid of demo modes
// take disparity range as command line arg
// output pfms directly

// modified by DS 4/4/2013
// - added mode 'midd' to process 9 full-size pairs
// - added support for two param settings (need to recompile)
//   (1 == 'robotics', 2 == 'Middlebury', i.e. hole filling)
// - added printing of timing info
// - turned off autoscaling of disp's


static const char *usage = "\n  usage: %s im0.pgm im1.pgm disp.pfm maxdisp [no_interp=0]\n";



/*
  Copyright 2011. All rights reserved.
  Institute of Measurement and Control Systems
  Karlsruhe Institute of Technology, Germany

  This file is part of libelas.
  Authors: Andreas Geiger

  libelas is free software; you can redistribute it and/or modify it under the
  terms of the GNU General Public License as published by the Free Software
  Foundation; either version 3 of the License, or any later version.

  libelas is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
  PARTICULAR PURPOSE. See the GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along with
  libelas; if not, write to the Free Software Foundation, Inc., 51 Franklin
  Street, Fifth Floor, Boston, MA 02110-1301, USA 
*/

// Demo program showing how libelas can be used, try "./elas -h" for help

#include <iostream>
#include <time.h>
#include "elas.h"
#include "image.h"
#include <math.h>

using namespace std;


// check whether machine is little endian
int littleendian()
{
    int intval = 1;
    uchar *uval = (uchar *)&intval;
    return uval[0] == 1;
}

// write pfm image (added by DS 10/24/2013)
// 1-band PFM image, see http://netpbm.sourceforge.net/doc/pfm.html
void WriteFilePFM(float *data, int width, int height, const char* filename, float scalefactor=1/255.0)
{
    // Open the file
    FILE *stream = fopen(filename, "wb");
    if (stream == 0) {
        fprintf(stderr, "WriteFilePFM: could not open %s\n", filename);
	exit(1);
    }

    // sign of scalefact indicates endianness, see pfms specs
    if (littleendian())
	scalefactor = -scalefactor;

    // write the header: 3 lines: Pf, dimensions, scale factor (negative val == little endian)
    fprintf(stream, "Pf\n%d %d\n%f\n", width, height, scalefactor);

    int n = width;
    // write rows -- pfm stores rows in inverse order!
    for (int y = height-1; y >= 0; y--) {
	float* ptr = data + y * width;
	// change invalid pixels (which seem to be represented as -10) to INF
	for (int x = 0; x < width; x++) {
	    if (ptr[x] < 0)
		ptr[x] = INFINITY;
	}
	if ((int)fwrite(ptr, sizeof(float), n, stream) != n) {
	    fprintf(stderr, "WriteFilePFM: problem writing data\n");
	    exit(1);
	}
    }
    
    // close file
    fclose(stream);
}



// compute disparities of pgm image input pair file_1, file_2
void process (const char* file_1, const char* file_2, const char* outfile, int maxdisp, int no_interp) 
{

    clock_t c0 = clock();

    // load images
    image<uchar> *I1,*I2;
    I1 = loadPGM(file_1);
    I2 = loadPGM(file_2);

    // check for correct size
    if (I1->width()<=0 || I1->height() <=0 || I2->width()<=0 || I2->height() <=0 ||
	I1->width()!=I2->width() || I1->height()!=I2->height()) {
	cout << "ERROR: Images must be of same size, but" << endl;
	cout << "       I1: " << I1->width() <<  " x " << I1->height() << 
	    ", I2: " << I2->width() <<  " x " << I2->height() << endl;
	delete I1;
	delete I2;
	return;    
    }

    // get image width and height
    int32_t width  = I1->width();
    int32_t height = I1->height();

    // allocate memory for disparity images
    const int32_t dims[3] = {width,height,width}; // bytes per line = width
    float* D1_data = (float*)malloc(width*height*sizeof(float));
    float* D2_data = (float*)malloc(width*height*sizeof(float));
  
    // process
    Elas::parameters param(Elas::MIDDLEBURY);
    if (no_interp) {
	//param = Elas::parameters(Elas::ROBOTICS);
	// don't use full 'robotics' setting, just the parameter to fill gaps
        param.ipol_gap_width = 3;
    }
    param.postprocess_only_left = false;
    param.disp_max = maxdisp;
    Elas elas(param);
    elas.process(I1->data,I2->data,D1_data,D2_data,dims);

    // added runtime output - DS 4/4/2013
    clock_t c1 = clock();
    double secs = (double)(c1 - c0) / CLOCKS_PER_SEC;
    printf("runtime: %.2fs  (%.2fs/MP)\n", secs, secs/(width*height/1000000.0));

    // save disparity image

    WriteFilePFM(D1_data, width, height, outfile, 1.0/maxdisp);

    // free memory
    delete I1;
    delete I2;
    free(D1_data);
    free(D2_data);
}

int main (int argc, char** argv) 
{

    if (argc < 5) {
	fprintf(stderr, usage, argv[0]);
	exit(1);
    }

    const char *file1 = argv[1];
    const char *file2 = argv[2];
    const char *outfile = argv[3];
    int maxdisp = atoi(argv[4]);
    int no_interp = 0;
    if (argc > 5)
	no_interp = atoi(argv[5]);

    process(file1, file2, outfile, maxdisp, no_interp);

    return 0;
}
