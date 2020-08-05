import math
import png
import struct
import array
import numpy as np

from util import *

UNKNOWN_FLOW_THRESH = 1e9;
UNKNOWN_FLOW = 1e10;

# Middlebury checks
TAG_STRING = 'PIEH'    # use this when WRITING the file
TAG_FLOAT = 202021.25  # check for this when READING the file



def ReadMiddleburyFloFile(path):
    """ Read .FLO file as specified by Middlebury.

    Returns tuple (width, height, u, v, mask), where u, v, mask are flat
    arrays of values.
    """

    with open(path, 'rb') as fil:
        tag = struct.unpack('f', fil.read(4))[0]
        width = struct.unpack('i', fil.read(4))[0]
        height = struct.unpack('i', fil.read(4))[0]

        assert tag == TAG_FLOAT
        
        #data = np.fromfile(path, dtype=np.float, count=-1)
        #data = data[3:]

        fmt = 'f' * width*height*2
        data = struct.unpack(fmt, fil.read(4*width*height*2))

        u = data[::2]
        v = data[1::2]

        mask = map(lambda x,y: abs(x)<UNKNOWN_FLOW_THRESH and abs(y) < UNKNOWN_FLOW_THRESH, u, v)
        mask = list(mask)
        u_masked = map(lambda x,y: x if y else 0, u, mask)
        v_masked = map(lambda x,y: x if y else 0, v, mask)

    return width, height, list(u_masked), list(v_masked), list(mask)

def ReadKittiPngFile(path):
    """ Read 16-bit .PNG file as specified by KITTI-2015 (flow).

    Returns a tuple, (width, height, u, v, mask), where u, v, mask
    are flat arrays of values.
    """
    # Read .png file.
    png_reader = png.Reader(path)
    data = png_reader.read()
    if data[3]['bitdepth'] != 16:
        raise Exception('bitdepth of ' + path + ' is not 16')

    width = data[0]
    height = data[1]

    # Get list of rows.
    rows = list(data[2])

    u = array.array('f', [0]) * width*height
    v = array.array('f', [0]) * width*height
    mask = array.array('f', [0]) * width*height

    for y, row in enumerate(rows):
        for x in range(width):
            ind = width*y+x
            u[ind] = (row[3*x] - 2**15) / 64.0
            v[ind] = (row[3*x+1] - 2**15) / 64.0
            mask[ind] = row[3*x+2]

            # if mask[ind] > 0:
            #     print(u[ind], v[ind], mask[ind], row[3*x], row[3*x+1], row[3*x+2])

    png_reader.close()

    return (width, height, u, v, mask)


def WriteMiddleburyFloFile(path, width, height, u, v, mask=None):
    """ Write .FLO file as specified by Middlebury.
    """

    if mask is not None:
        u_masked = map(lambda x,y: x if y else UNKNOWN_FLOW, u, mask)
        v_masked = map(lambda x,y: x if y else UNKNOWN_FLOW, v, mask)
    else:
        u_masked = u
        v_masked = v

    fmt = 'f' * width*height*2
    # Interleave lists
    data = [x for t in zip(u_masked,v_masked) for x in t]

    with open(path, 'wb') as fil:
        fil.write(str.encode(TAG_STRING))
        fil.write(struct.pack('i', width))
        fil.write(struct.pack('i', height))
        fil.write(struct.pack(fmt, *data))


def WriteKittiPngFile(path, width, height, u, v, mask=None):
    """ Write 16-bit .PNG file as specified by KITTI-2015 (flow).

    u, v are lists of float values
    mask is a list of floats, denoting the *valid* pixels.
    """

    data = array.array('H',[0])*width*height*3
    if mask is None:
        mask = array.array('H',[1])*width*height*3
        pass

    for i,(u_,v_,mask_) in enumerate(zip(u,v,mask)):
        data[3*i] = int(u_*64.0+2**15)
        data[3*i+1] = int(v_*64.0+2**15)
        data[3*i+2] = int(mask_)
        
        # if mask_ > 0:
        #     print(data[3*i], data[3*i+1],data[3*i+2])

    with open(path, 'wb') as png_file:
        png_writer = png.Writer(width=width, height=height, bitdepth=16, compression=3, greyscale=False)
        png_writer.write_array(png_file, data)


def ConvertMiddleburyFloToKittiPng(src_path, dest_path):
    width, height, u, v, mask = ReadMiddleburyFloFile(src_path)
    WriteKittiPngFile(dest_path, width, height, u, v, mask=mask)

def ConvertKittiPngToMiddleburyFlo(src_path, dest_path):
    width, height, u, v, mask = ReadKittiPngFile(src_path)
    WriteMiddleburyFloFile(dest_path, width, height, u, v, mask=mask)


def ParseFilenameKitti(filename):
    # Parse kitti filename (seq_frameno.xx),
    # return seq, frameno, ext.
    # Be aware that seq might contain the dataset name (if contained as prefix)
    ext = filename[filename.rfind('.'):]
    frameno = filename[filename.rfind('_')+1:filename.rfind('.')]
    frameno = int(frameno)
    seq = filename[:filename.rfind('_')]
    return seq, frameno, ext
