#!/usr/bin/env python

# Main file of devkit for the stereo task of the Robust Vision Challenge 2018.

from benchmark import *
from benchmark_eth3d import *
from benchmark_kitti2015 import *
from benchmark_middlebury2014 import *
from dataset_format import *
from dataset_format_middlebury2014 import *
from devkit import *


if __name__ == '__main__':
    # Define the list of benchmarks supported by this script (in the order in
    # which they are listed on http://www.robustvision.net/index.php).
    benchmarks = [Middlebury2014(), Kitti2015(), ETH3D2017()]

    # Define the list of dataset formats which are supported.
    dataset_formats = [Middlebury2014Format()]
    
    # Call the generic devkit main function.
    DevkitMain('Stereo', benchmarks, dataset_formats)
