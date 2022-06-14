#!/usr/bin/env python

# Main file of devkit for the flow task of the Robust Vision Challenge 2018.

from benchmark import *
from benchmark_sintel import *
from benchmark_kitti2015 import *
from benchmark_middlebury import *
from benchmark_viper import *
from dataset_format import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from devkit import *


if __name__ == '__main__':
    # Define the list of benchmarks supported by this script (in the order in
    # which they are listed on http://www.robustvision.net/index.php).
    benchmarks = [Kitti2015(), Sintel(), Middlebury(), VIPER()]
    
    # Define the list of dataset formats which are supported.
    dataset_formats = [MiddleburyFormat(), Kitti2015Format()]
    
    # Call the generic devkit main function.
    DevkitMain('Flow', benchmarks, dataset_formats)
