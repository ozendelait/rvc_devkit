import math
import png
import struct

import numpy as np
import scipy.misc as sp

from util import *


# Converts Cityscapes instance segmentation labels to Kitti instance segmentation labels
def ConvertCityscapesToKittiInstances(cs_instance):
    instance = np.zeros(cs_instance.shape,dtype="int32")
    # convert
    instance_mask = cs_instance > 1000
    semantic = cs_instance * (1-instance_mask) + (cs_instance // 1000)
    instance = ((cs_instance + 1 ) % 1000 ) * instance_mask
    kitti_instance = semantic*256 + instance 
    return kitti_instance

def SaveKittiInstance(kitti_instance, dest_path):
    sp.toimage(kitti_instance, high=np.max(kitti_instance), low=np.min(kitti_instance), mode='I').save(dest_path)

