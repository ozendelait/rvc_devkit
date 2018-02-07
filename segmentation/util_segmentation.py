import math
import png
import struct

import numpy as np
import scipy.misc as sp

from util import *


# Converts Cityscapes instance segmentation labels to Kitti instance segmentation labels
def ConvertCityscapesToKittiInstances(src_path_cs_instance, src_path_cs_semantic, dest_path):
    # read files
    cs_instance = sp.imread(src_path_cs_instance)
    cs_semantic = sp.imread(src_path_cs_semantic)

    # convert
    instance = np.zeros(cs_instance.shape, dtype='int32')
    instance[np.where(cs_instance > 1000)] = 1 + cs_instance[np.where(cs_instance > 1000)] % 1000
    kitti_instance = cs_semantic * 256 + instance

    # save file
    sp.toimage(kitti_instance, high=np.max(kitti_instance), low=np.min(kitti_instance), mode='I').save(dest_path)