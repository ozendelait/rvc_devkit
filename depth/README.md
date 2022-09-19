# Robust Vision Challenge 2022 - Single Image Depth Prediction Devkit


## Required Pip Packages
```
pip install argparse numpy imageio
```

## Dataset Download

For the Robust Vision Challenge 2022, we use four single-image
depth datasets:
- KITTI - http://www.cvlibs.net/datasets/kitti/eval_depth.php?benchmark=depth_prediction
- MPI Sintel - http://sintel.is.tue.mpg.de/
- <s>rabbitAI - https://rabbitai.de/benchmark/</s>
- VIPER - https://playing-for-benchmarks.org/leaderboards/monodepth/

You can use the rabbitAI training dataset to improve your robustness:
https://download.rabbitai.de/benchmarks/rvc_2020/data.zip

To download KITTI and MPI Sintel datasets you may execute:

  bash get_datasets.sh

This will download all the required data and reorder the data into
the a common format (see below), in the directories datasets_mpi_sintel
 and raw_data_mpi_sintel.
The process requires roughly 300GB of space!
The download script will not delete any data, to free space again,
remove all files you don't need.

Note: The VIPER benchmark does not supply any training data but participants still have to submit results for its test set!
You can add any additional public data source you like as long as you reference it.

## Short Format and Layout Description

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

## Detailed Description (from KITTI)

We use the original KITTI depth prediction format, compare KITTI/readme.txt.
A short summary:

Depth maps (annotated and raw Velodyne scans) are saved as uint16 PNG images,
which can be opened with either MATLAB, libpng++ or the latest version of
Python's pillow (from PIL import Image). A 0 value indicates an invalid pixel
(ie, no ground truth exists, or the estimation algorithm didn't produce an
estimate for that pixel). Otherwise, the depth for a pixel can be computed
in meters by converting the uint16 value to float and dividing it by 256.0:

```
depth(u,v) = ((float)I(u,v))/256.0;
valid(u,v) = I(u,v)>0;
```

RGB images are stored as 3-channel RGB images, and intrinsics are stored in
txt file containing 9 float values, that, if cast to a 3x3 matrix represent:

```
f_x     0   o_x
  0   f_y   o_y
  0     0     1
```

Where focal length in horizontal and vertical axis are given by f_x and f_y,
and the focal point by (o_x, o_y).

## Submission ##
Fill in the "Register Method to RVC" form here: http://www.robustvision.net/submit.php

After that, upload your predictions for the respective test sets of each benchmark:

- KITTI      : http://www.cvlibs.net/datasets/kitti/user_submit.php
- MPI Sintel : https://sintel-depth.csail.mit.edu/landing
- VIPER      : https://playing-for-benchmarks.org/submissions/my/

The rabbitai benchmark had technical difficulties and will not be part of RVC2022. You can still use existing (or new) solutions you created with the rabbitai training data and submit the results to the three remaining leaderboards.
