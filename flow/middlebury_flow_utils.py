'''
Created on Jun 27, 2017

According to the c++ source code of Daniel Scharstein and the matlab code of Deqing Sun
Contact: schar@middlebury.edu and dqsun@cs.brown.edu

@author: jjanai
'''
import struct
import numpy as np
import math
import array

UNKNOWN_FLOW_THRESH = 1e9;
UNKNOWN_FLOW = 1e10;            

def writeFlowFile(flow, filename):
    TAG_STRING = 'PIEH'    # use this when WRITING the file

    # sanity check
    if not filename:
        print('ERROR writeFlowFile: empty filename')
        return

    idx = filename.rfind('.');  # in case './xxx/xxx.flo

    if len(filename[idx:]) == 1:
        print('ERROR writeFlowFile: extension required in filename %s' % filename)
        return

    if filename[idx:] != '.flo':
        print('ERROR writeFlowFile: filename %s should have extension ''.flo''' % filename)
        return

    height, width, dim = flow.shape

    if dim != 2:
        print('ERROR writeFlowFile: image must have two bands')
        return

    fid = open(filename, "wb")
    fid.write(TAG_STRING)
    fid.write(struct.pack('i', width))
    fid.write(struct.pack('i', height))

    # arrange into matrix for
    tmp = np.zeros(width * height * dim)
    tmp[np.arange(1,width*height*dim,2) - 1] = flow[:,:,0].flatten()
    tmp[np.arange(1,width*height*dim,2)] = flow[:,:,1].flatten()

    myfmt = 'f' * len(tmp)
    fid.write(struct.pack(myfmt,*tmp))
    fid.close()

def readFlowFile(filename):
    TAG_FLOAT = 202021.25  # check for this when READING the file

    # sanity check
    if not filename:
        print('readFlowFile: empty filename')
        return

    idx = filename.rfind('.');  # in case './xxx/xxx.flo

    if len(filename[idx:]) == 1:
        print('readFlowFile: extension required in filename %s' % filename)
        return

    if filename[idx:] != '.flo':
        print('readFlowFile: filename %s should have extension ''.flo''' % filename)
        return

    fid = open(filename, 'rb');

    if fid.closed:
        print('readFlowFile: could not open %s' % filename)
        return

    tag,     = struct.unpack('f', fid.read(4))  #fread(fid, 1, 'float32');
    width,   = struct.unpack('i', fid.read(4))  #fread(fid, 1, 'int32');
    height,  = struct.unpack('i', fid.read(4))  #fread(fid, 1, 'int32');

    # sanity check
    if tag != TAG_FLOAT:
        print(tag)
        print('readFlowFile(%s): wrong tag (possibly due to big-endian machine?)' % filename)
        return

    if width < 1 or width > 99999:
        print('readFlowFile(%s): illegal width %d' % ( filename, width))
        return

    if height < 1 or height > 99999:
        print('readFlowFile(%s): illegal height %d' % (filename, height))
        return

    dim = 2
    tmp = np.zeros(width * height * dim)

    # arrange into matrix form
    myfmt = 'f' * len(tmp)
    tmp = np.array(struct.unpack(myfmt, fid.read(4 * len(tmp))), dtype=np.float32 ) #fread(fid, inf, 'float32');

    flow = np.zeros([height, width, dim])
    flow[:,:,0] = tmp[np.arange(1,width*height*dim,2)-1].reshape(height,width);
    flow[:,:,1] = tmp[np.arange(1,width*height*dim,2)].reshape(height,width);

    fid.close()

    return flow

def flowToColor(flow):
    height, width, dim = flow.shape
    
    if dim != 2:
        print('ERROR: flowToColor: image must have two bands')    
        return np.zeros((height, width, 3))
    
    u = flow[:,:,0]
    v = flow[:,:,1]
    
    maxu = -999
    maxv = -999
    
    minu = 999
    minv = 999
    maxrad = -1
    
    # fix unknown flow
    idxUnknown = np.logical_or(np.isnan(u), np.logical_or(np.isnan(v), np.logical_or(abs(u) > UNKNOWN_FLOW_THRESH, abs(v) > UNKNOWN_FLOW_THRESH)))
    u[idxUnknown] = 0
    v[idxUnknown] = 0
    
    maxu = max(maxu, u.max())
    minu = min(minu, u.min())
    
    maxv = max(maxv, v.max())
    minv = min(minv, v.min())
    
    rad = np.sqrt(u**2+v**2)
    maxrad = max(maxrad, rad.max())
    
    #print('max flow: %.4f flow range: u = %.3f .. %.3f v = %.3f .. %.3f\n' % (maxrad, minu, maxu, minv, maxv))
    
    if maxrad > 0:
        u = u/(maxrad)
        v = v/(maxrad)
    
    # compute color
    img = computeColor(u, v)  
    
    return img
    
def computeColor(u,v):
    nanIdx = np.zeros((u.shape[0], u.shape[1]))
    
    colorwheel = makeColorwheel()
    ncols = colorwheel.shape[0]
    
    rad = np.sqrt(u**2 + v**2)          
    
    a = np.arctan2(-v, -u) / math.pi
    
    fk = np.maximum((a+1) / 2 * (ncols-1), 0) # -1~1 maped to 1~ncols-1
       
    k0 = np.int_(np.floor(fk))         # 0, 1, ..., ncols-1
    
    k1 = np.mod(k0+1, ncols)
    
    f = fk - k0
    
    img = np.zeros((u.shape[0], u.shape[1],3)).astype('uint8')
    
    for i in range(0, colorwheel.shape[1]):
        tmp = colorwheel[:,i]
        col0 = tmp[k0]/255
        col1 = tmp[k1]/255
        col = (1-f) * col0 + f * col1   
       
        idx = rad <= 1   
        col[idx] = 1 - rad[idx] * (1-col[idx])      # increase saturation with radius
        
        nidx = rad > 1 
        col[nidx] = col[nidx] * 0.75                        # out of range
        
        img[:,:,i] = np.uint8(np.floor(255 * col * (1-nanIdx)))
    
    return img    


def makeColorwheel():
    #   color encoding scheme
    
    #   adapted from the color circle idea described at
    #   http://members.shaw.ca/quadibloc/other/colint.htm
    RY = 15
    YG = 6
    GC = 4
    CB = 11
    BM = 13
    MR = 6
    
    ncols = RY + YG + GC + CB + BM + MR
    
    colorwheel = np.zeros((ncols, 3)) # r g b
    
    col = 0
    #RY
    colorwheel[0:RY, 0] = 255
    colorwheel[0:RY, 1] = np.transpose(np.floor(255*(np.arange(0,RY))/RY))
    col = col+RY
    
    #YG
    colorwheel[col+np.arange(0,YG), 0] = np.transpose(255 - np.floor(255*(np.arange(0,YG))/YG))
    colorwheel[col+np.arange(0,YG), 1] = 255
    col = col+YG
    
    #GC
    colorwheel[col+np.arange(0,GC), 1] = 255
    colorwheel[col+np.arange(0,GC), 2] = np.transpose(np.floor(255*(np.arange(0,GC))/GC))
    col = col+GC
    
    #CB
    colorwheel[col+np.arange(0,CB), 1] = np.transpose(255 - np.floor(255*(np.arange(0,CB))/CB))
    colorwheel[col+np.arange(0,CB), 2] = 255
    col = col+CB
    
    #BM
    colorwheel[col+np.arange(0,BM), 2] = 255
    colorwheel[col+np.arange(0,BM), 0] = np.transpose(np.floor(255*(np.arange(0,BM))/BM))
    col = col+BM
    
    #MR
    colorwheel[col+np.arange(0,MR), 2] = np.transpose(255 - np.floor(255*(np.arange(0,MR))/MR))
    colorwheel[col+np.arange(0,MR), 0] = 255
    
    return colorwheel
