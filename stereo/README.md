# Robust Vision Challenge 2018 - Stereo Devkit #

## Dataset Download ##

To use the devkit, simply run the main script without any program arguments:
```
python stereo_devkit.py
```
The script will ask about a few settings (including the dataset format to use)
and then download the datasets into a folder in the current working directory.
The folder layout is as follows:

```
- datasets_<format_name>
  - metadata
  - test
  - training
```

If the optional program argument `--keep_archives` is given, the downloaded
benchmark archive files will not be deleted after the datasets are extracted
and converted. This is for example useful to avoid re-downloading the archives
if you would like to obtain the datasets in several formats.


## Middlebury 2014 Stereo Format ##

#### Input ####

For the [Middlebury 2014 Stereo format](http://vision.middlebury.edu/stereo/data/scenes2014/),
each subfolder within the training and
test folders contains a dataset (i.e., a stereo pair). The dataset names are
prefixed by the dataset's benchmark name. Each dataset contains the following
files in Middlebury 2014 Stereo format:

```
calib.txt
disp0GT.pfm  (ground truth, for training datasets only)
im0.png
im1.png
```

Extra files are present for certain benchmarks in the respective benchmarks'
formats. Using these files is optional:

```
cameras.txt              : For ETH3D.
images.txt               : For ETH3D.

mask0nocc.png            : For ETH3D, Kitti2015, Middlebury2014 (training datasets only).

gt_sample_count.pfm      : For HCI (training datasets only).
gt_uncertainty.pfm       : For HCI (training datasets only).
mask.png                 : For HCI.
mask_dynamic_objects.png : For HCI (training datasets only).
mask_eval.png            : For HCI (training datasets only).

obj_map.png              : For Kitti2015 (training datasets only).
```

#### Output ####

Result files for a stereo method must be named as follows and placed in the
directory of the corresponding dataset:
```
disp0NAME.pfm
timeNAME.txt
```
Here, NAME must be the name of the submitted method.

The image format must be PFM (http://netpbm.sourceforge.net/doc/pfm.html). This
format uses a small ASCII header that contains the image size. It is followed by
32-bit floating point values for all pixels. The float values are stored as
binary data (i.e., four bytes) in little or big endian format, depending on the
sign of the scale factor in the header. The absolute value of the scale
factor is ignored. Please note that PFM stores the image lines in reverse
order, i.e., the bottommost image line is stored first. The values encode the
disparities in pixels without any scale factor.

In addition to the disparity image, the time for calculating the disparities
must be given for each image pair. The time in seconds is stored as a floating
point value in ASCII encoding in a text file. The file must contain only that
number.


## Kitti 2015 Stereo Format ##

#### Input ####

For the [Kitti 2015 Stereo format](http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=stereo),
the training and test folders contain the following folders having files for all
datasets:

```
disp_occ_0  (ground truth, for training datasets only)
image_2
image_3
```

The filenames are equal to the dataset names (the file extensions may differ).
The dataset names are prefixed by the dataset's benchmark name.

In the following folders, extra files are present for certain benchmarks in the
respective benchmarks' formats. Using these files is optional:

```
cameras                  : For ETH3D.
images                   : For ETH3D.

disp_noc_0               : For ETH3D, Kitti2015, Middlebury2014 (training datasets only).

gt_sample_count          : For HCI (training datasets only).
gt_uncertainty           : For HCI (training datasets only).
mask                     : For HCI.
mask_dynamic_objects     : For HCI (training datasets only).
mask_eval                : For HCI (training datasets only).

obj_map                  : For Kitti2015 (training datasets only).
```

#### Output ####

Result files for a stereo method must be placed in folders named as follows,
which must be placed within the training / test directories:

```
NAME_disp_0
NAME_time
```

Here, NAME must be the name of the submitted method.

The folder NAME_disp_0 must contain the resulting disparity images in the same
format as the provided ground truth.

For each dataset, the folder NAME_time must contain a text file dataset_name.txt
which must contain the time in seconds to compute the disparity image. It is
stored as a floating point value in ASCII encoding. The file must contain only
that number.


## Result Submission ##

After a stereo method has been run on all datasets, the results can be
automatically packaged for submission to each individual benchmark. To do so,
simply run the devkit script again in the same directory:
```
python stereo_devkit.py
```
It will then offer to create the submission archives. Notice that this requires
that results with the same method name are available for all datasets of all
relevant benchmarks (either for training or for both training and testing). If
the option to create a submission is missing, make sure that all required files
exist.

The resulting archives must be submitted to the respective benchmarks:
TODO: How to mark the submissions as belonging to ROB?
* [ETH3D2017](https://www.eth3d.net/login)
* [HCI2016](http://hci-benchmark.org/accounts/login?next=/challenges/submissions/create/stereo_geometry&hc=stereo_geometry)
* [Kitti2015](http://www.cvlibs.net/datasets/kitti/user_login.php)
* [Middlebury2014](http://vision.middlebury.edu/stereo/submit3/upload.html)

Furthermore, the submission must be completed by filling a short form on the
Robust Vision Challenge website: TODO
