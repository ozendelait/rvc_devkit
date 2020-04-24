#!/usr/bin/env python

# Main file of devkit for the instance segmentation task of the Robust Vision Challenge 2018.

from benchmark_cityscapes import Cityscapes
from benchmark_kitti2015 import KITTI2015
from benchmark_wilddash import WildDash
from benchmark_scannet import ScanNet
from dataset_format_kitti2015 import KITTI2015Format
from devkit import *


if __name__ == '__main__':
    # Define the list of benchmarks supported by this script (as listed on http://www.robustvision.net/index.php).
    benchmarks = [KITTI2015(), WildDash(), Cityscapes(), ScanNet()]

    # Define the list of dataset formats which are supported.
    dataset_formats = [KITTI2015Format()]

    # Call the generic devkit main function.
    DevkitMain('instance', benchmarks, dataset_formats)
