# Robust Vision Challenge 2018 - Stereo Devkit #

## Dataset Download ##

The simplest way to use the devkit is to run the main script without any program
arguments:
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

#### Running ####

The devkit includes support for running algorithms on all datasets. As an
example, [ELAS](http://www.cvlibs.net/software/libelas/) is included in the
folder alg-ELAS (TODO: alg-ELAS/README-Middlebury.txt must be adapted). To build
it, run the following:

```
cd alg-ELAS
mkdir build  # The run script expects the executable in the folder "build"
cd build
cmake ..
make
```

To run the algorithm, simply run the devkit script again in the same directory
in which it was run originally:
```
python stereo_devkit.py
```

The folder alg-ELAS must be in the same directory. Under these conditions,
the script will offer to run the algorithm. An alternative way to run algorithms
using the command line interface is described below in the respective section.

In general, the script looks for all folders starting with alg-. They must
contain a file named either "run" or "run.py", which is executed by the script
for all datasets. If the file is a Python script, the same interpreter version
used for running the devkit script is used. The arguments passed to the script
depend on the dataset format. For the Middlebury 2014 Stereo format, the
following arguments are passed to the script:

1. The method name to use for the result.
2. The path to the left image, im0.png.
3. The path to the right image, im1.png.
4. The maximum disparity, ndisp, read from the calib.txt file.
5. The directory to output the result files to.
6. Optional additional arguments, if given.


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

#### Running ####

For this dataset format, the following parameters are passed to the run file:

1. The method name to use for the result.
2. The path to the dataset folder (containing the image_2, image_3, etc. folders).
3. The name of the dataset (i.e., the image filename without the extension .png).
4. The path to the directory NAME_disp_0 to output the disparity image to.
5. The path to the directory NAME_time to output the runtime to.
6. Optional additional arguments, if given.


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


## Command Line Interface ##

As an alternative to the interactive interface, a command line interface is
available:

```
# Download the datasets:
# - format indicates the dataset format to convert all datasets to and must be
#   either middlebury2014 or kitti2015
# - The resolution of the Middlebury datasets can be chosen as [f]ull, [h]alf,
#   or [q]uarter
python stereo_devkit.py obtain <format> --middlebury_resolution {f,F,h,H,q,Q}

# Run an algorithm:
# - format must only be given if the datasets were downloaded in more than one
#   format. In this case, it must indicate the dataset format to run the method
#   on and must be either middlebury2014 or kitti2015
# - runfile_path is the path to the executable file or Python script that will
#   be called for each dataset, as described in the section "Running" for the
#   Middlebury 2014 format above
# - method_name is the method name to use in the result files, which will be
#   passed to the runfile as first parameter
# - --training is an optional flag which will run the algorithm on the training
#   datasets only
# - additional_arguments are optional additional arguments that will be passed
#   to the run file after the regular arguments.
python stereo_devkit.py run [format] <runfile_path> <method_name> [--training] [additional_arguments]

# Create archives for result submission:
# - format behaves the same as for running an algorithm, see above.
# - method_name is the method to generate the submission archives for, as
#   specified when running the algorithm
# - --training is an optional flag which will create a training-only submission
#   (however, this may only be supported by a subset of benchmarks)
python stereo_devkit.py submit [format] <method_name> [--training]
```
