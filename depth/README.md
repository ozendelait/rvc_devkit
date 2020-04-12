# Robust Vision Challenge 2020 - Single Image Depth Prediction Devkit #


## Required Pip Packages ##
```
pip install argparse numpy imageio
```

## Dataset Download ##

For the Robust Vision Challenge 2018, we propose two large-scale single-image
depth datasets, i.e. ScanNet and KITTI. Please make sure that you have a minimum
of 150GB-200GB disk space for all (raw) datasets available. If you run out of space
while downloading KITTI raw or ScanNet, you can remove unnecessary zip files
after they have been unzipped.

#### KITTI Depth (see http://www.cvlibs.net/datasets/kitti/eval_depth.php?benchmark=depth_prediction) ####

Download depth maps and intrinsics for training data:
```
wget -P datasets_KITTI https://s3.eu-central-1.amazonaws.com/avg-kitti/data_depth_annotated.zip
unzip -d datasets_KITTI datasets_KITTI/data_depth_annotated.zip
```
Use the KITTI raw download script (thanks to Omid Hosseini for sharing) to download KITTI raw:
```
cd raw_data_KITTI && bash raw_data_downloader.sh && cd ..
```
Note that you can remove all image_00, image_01, oxts, and velodyne_points folders if you need
to free some disk space (those files are not required for our challenge):

```
rm -rf raw_data_KITTI/2011_*_*/2011_*_*_drive_*_sync/image_0[0,1]
rm -rf raw_data_KITTI/2011_*_*/2011_*_*_drive_*_sync/oxts
rm -rf raw_data_KITTI/2011_*_*/2011_*_*_drive_*_sync/velodyne_points
```

Selected data (RGB, depth maps, and intrinsics) for validation and test splits:

```
wget -P datasets_KITTI https://s3.eu-central-1.amazonaws.com/avg-kitti/data_depth_selection.zip
unzip datasets_KITTI/data_depth_selection.zip -d datasets_KITTI/
rm -rf datasets_KITTI/depth_selection/test_depth_completion_anonymous
rm -rf datasets_KITTI/depth_selection/val_selection_cropped/velodyne_raw
mv datasets_KITTI/depth_selection/val_selection_cropped datasets_KITTI/val_selection
mv datasets_KITTI/depth_selection/test_depth_prediction_anonymous datasets_KITTI/test
rmdir datasets_KITTI/depth_selection
```

Now, you will need to gather left and right color images from the KITTI raw data to
match with the GT depth maps (which are already aligned with the RGB images). You can
choose to either write a text file containing all matching depth and RGB images (-t txt)
or copy/move/softlink KITTI raw images into the KITTI depth folder structure (-t copy/..)

```
python KITTI/gather_raw_images.py -d datasets_KITTI/train -r raw_data_KITTI/ -t txt -o kitti_train
python KITTI/gather_raw_images.py -d datasets_KITTI/val -r raw_data_KITTI/ -t txt -o kitti_val
```

If you use the -t move option for train and val, you can remove all contents of
the raw_data_KITTI folder to free some more disk space, as all required data
is located in the datasets_KITTI folder.


## Dataset Format ##

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


## Dataset Structure

You can find dataset splits for training, validation and testing for both
datasets in the following structure:

```
dataset_<name>/
    train/
        <scene/drive>/
                     depth/ [/image_02/03]
                           <file_name>.png
            image[_02,_03]/
                           <file_name>.png
                intrinsics/ [/image_02/03]
                           <file_name>.txt
    validation/
        groundtruth_depth/
                          <file_name>.png
                    image/
                          <file_name>.png
               intrinsics/
                          <file_name>.txt
    test/
                    image/
                          <file_name>.png
               intrinsics/
                          <file_name>.txt
```
