# Robust Vision Challenge 2020 - Single Image Depth Prediction Devkit #


###########################
## Required Pip Packages ##
###########################

pip install argparse numpy imageio

######################
## Dataset Download ##
######################

For the Robust Vision Challenge 2020, we propose three single-image
depth datasets:
KITTI - http://www.cvlibs.net/datasets/kitti/eval_depth.php?benchmark=depth_prediction
MPI Sintel - http://sintel.is.tue.mpg.de/
rabbitAI - https://rabbitai.de/benchmark/

For the rabbitAI dataset please register at:
https://rabbitai.de/benchmark/register/
you will receive a download link.

To download KITTI and MPI Sintel datasets you may execute:

  bash get_datasets.sh

This will download all the required data and reorder the data into
the a common format (see below), in the directories datasets_mpi_sintel
 and raw_data_mpi_sintel.
The process requires roughly 300GB of space!
The download script will not delete any data, to free space again,
remove all files you don't need.


######################
## Format/Layout ##
######################

The rabbitAI data set as well as the data created by the download script
are structured as follows:
dataset/
└── train
    ├── alley_1
    │   ├── camdata_left
    │   ├── depth_viz
    │   ├── image_01
    │   └── proj_depth
    │       └── groundtruth
    │           ├── image_01
    │           └── image_01_dpt

Where train can also be a different directory (e.g. test/val).
image_? contains the color images for depth prediction, and 
proj_depth/groundtruth/image_0? the corresponding depth imgs.

The depth GT images are encoded as 16bit png, which encode 
depth as depth/256.  

The script clamps depth at 100m (e.g. max val is 25600).
Invalid values are encoded as zero!

We recommend training in a way that allows values >=100 for GT values of 100m.
Note that MPI Sintel also supports larger depths (run get_datasets.sh --clamprange [meter]).
