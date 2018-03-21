from util_flow import *
import hashlib
import numpy as np

def md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()

def check_ok(data1,data2):
    for d1,d2 in zip(data1,data2):
        assert(np.all(np.array(d1)==np.array(d2)))
    

def main():
    # Test 1: Read and write FLO file
    width, height, u, v, mask = ReadMiddleburyFloFile('testdata/sintel.flo')
    print(width,height)
    WriteMiddleburyFloFile('testdata/sintel_out.flo', width, height, u, v, mask=mask)
    md5_orig = md5('testdata/sintel.flo')
    md5_new = md5('testdata/sintel_out.flo')
    assert(md5_orig == md5_new)

    # Test 2: Read and write Sintel file
    data1 = ReadKittiPngFile('testdata/kitti.png')
    print(len(u),len(v), len(mask))
    print(width,height)
    WriteKittiPngFile('testdata/kitti_out.png', *data1)
    data2 = ReadKittiPngFile('testdata/kitti_out.png')
    check_ok(data1,data2)

    # Test 3: Convert from Kitti to Sintel and back
    ConvertKittiPngToMiddleburyFlo('testdata/kitti.png', 'testdata/kitti_flo.flo')
    ConvertMiddleburyFloToKittiPng('testdata/kitti_flo.flo', 'testdata/kitti_out.png')
    data1 = ReadKittiPngFile('testdata/kitti.png')
    data2 = ReadMiddleburyFloFile('testdata/kitti_flo.flo')
    data3 = ReadKittiPngFile('testdata/kitti_out.png')

    check_ok(data1,data2)
    check_ok(data1,data3)
    check_ok(data2,data3)

if __name__ == '__main__':
    main()
