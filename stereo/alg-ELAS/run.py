#!/usr/bin/env python

# Runs ELAS on datasets in Middlebury 2014 format, given the following parameters:
# method_name, im0_path, im1_path, ndisp, output_dir_path.
# Output files are written as expected by the Robust Vision Challenge 2018.

import os
import png
import subprocess
import struct
import sys


# Converts a string to bytes (for writing the string into a file). Provided for
# compatibility with Python 2 and 3.
def StrToBytes(text):
    if sys.version_info[0] == 2:
        return text
    else:
        return bytes(text, 'UTF-8')


# Converts a PNG image to a (grayscale) PGM image.
def ConvertPngToPgm(in_path, out_path):
    png_reader = png.Reader(in_path)
    png_data = png_reader.read()
    png_pixels = []
    for row in png_data[2]:
        png_pixels.extend(row)
    
    if png_data[3]['bitdepth'] != 8:
        raise Exception('bitdepth of ' + in_path + ' is not 8, this is not supported')
    
    # Convert to grayscale if necessary.
    if not png_data[3]['greyscale']:
        gray_pixels = []
        for i in range(0, len(png_pixels), 3):
            r = png_pixels[i + 0]
            g = png_pixels[i + 1]
            b = png_pixels[i + 2]
            # NOTE: One might want to use round() instead of int() here. int()
            #       is used for consistency with the Middlebury devkit.
            gray_pixels.append(int(0.299 * r + 0.587 * g + 0.114 * b))
        png_pixels = gray_pixels
    
    width = png_data[0]
    height = png_data[1]
    
    with open(out_path, 'wb') as pgm_file:
        pgm_file.write(StrToBytes('P5\n'))
        pgm_file.write(StrToBytes(str(width) + ' ' + str(height) + '\n'))
        pgm_file.write(StrToBytes('255\n'))  # maximum value
        pgm_file.write(struct.pack(str(len(png_pixels)) + 'B', *png_pixels))
    
    png_reader.close()


if __name__ == '__main__':
    # Get arguments.
    method_name = sys.argv[1]
    im0_path = sys.argv[2]
    im1_path = sys.argv[3]
    ndisp = sys.argv[4]
    output_dir_path = sys.argv[5]
    
    # The ELAS executable is expected in build/elas relative to this script.
    elas_path = os.path.join(os.path.dirname(__file__), 'build', 'elas')
    
    # Convert the input files from .png to .pgm format, as expected by ELAS.
    im0_pgm_path = im0_path + '.temp.pgm'
    ConvertPngToPgm(im0_path, im0_pgm_path)
    im1_pgm_path = im1_path + '.temp.pgm'
    ConvertPngToPgm(im1_path, im1_pgm_path)
    
    # Run ELAS.
    pfm_output_path = os.path.join(output_dir_path, 'disp0' + method_name + '.pfm')
    program_with_arguments = [elas_path,
                              im0_pgm_path,
                              im1_pgm_path,
                              pfm_output_path,
                              ndisp]
    print('Running: ' + ' '.join(program_with_arguments))
    proc = subprocess.Popen(program_with_arguments,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    
    # Remove temporary files.
    os.remove(im0_pgm_path)
    os.remove(im1_pgm_path)
    
    # Verify ELAS' return code.
    if proc.returncode != 0:
        print('ELAS call failed (return code: ' + str(proc.returncode) + ')')
        sys.exit(1)
    del proc
    
    # Get the runtime from ELAS' output (example: "runtime: 0.96s  (0.68s/MP)")
    text_output = stdout.decode("utf-8").strip()
    if not text_output.startswith('runtime: '):
        print('Cannot parse ELAS output')
        sys.exit(1)
    runtime = text_output[len('runtime: '):text_output.find('s')]
    
    # Write the runtime file.
    time_output_path = os.path.join(output_dir_path, 'time' + method_name + '.txt')
    with open(time_output_path, 'wb') as time_file:
        time_file.write(StrToBytes(runtime))
    
    sys.exit(0)
