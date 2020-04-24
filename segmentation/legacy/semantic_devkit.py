#!/usr/bin/env python

# Main file of devkit for the semantic segmentation task of the Robust Vision Challenge 2018.

from benchmark_cityscapes import Cityscapes
from benchmark_kitti2015 import KITTI2015
from benchmark_wilddash import WildDash
from benchmark_scannet import ScanNet
from benchmark_viper import VIPER
from dataset_format_kitti2015 import KITTI2015Format
from devkit import *


if __name__ == '__main__':
    # Define the list of benchmarks supported by this script (as listed on http://www.robustvision.net/index.php).
    benchmarks = [KITTI2015(), WildDash(), Cityscapes(), ScanNet(), VIPER()]

    # Define the list of dataset formats which are supported.
    dataset_formats = [KITTI2015Format()]
    
    # Call the generic devkit main function.
    DevkitMain('semantic', benchmarks, dataset_formats)
