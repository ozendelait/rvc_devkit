# Robust Vision Challenge 2022 - Stereo Devkit #

## Dataset Download ##

The simplest way to use the devkit is to run the main script without any program
arguments:
```
python stereo_devkit.py
```
On Windows, one may double-click stereo_devkit.py if Python is installed.
The script may ask about a few settings and then download the datasets into a
folder in the current working directory. The folder layout is as follows:

```
- datasets_<format_name>
  - metadata
  - test
  - training
```

If the optional program argument `--keep_archives` is given, the downloaded
archive files will not be deleted after the datasets are extracted
and converted.


## Dataset Format ##

#### Input ####

The [Middlebury 2014 Stereo format](http://vision.middlebury.edu/stereo/data/scenes2014/)
is used as common format for all datasets. Each subfolder within the training
and test folders contains a dataset (i.e., a stereo pair). The dataset names are
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
folder alg-ELAS. To build it, run the following:

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
used for running the devkit script is used. The following arguments are passed
to the script:

1. The method name to use for the result.
2. The path to the left image, im0.png.
3. The path to the right image, im1.png.
4. The maximum disparity, ndisp, read from the calib.txt file.
5. The directory to output the result files to.
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
* [ETH3D2017](https://www.eth3d.net/login)
* [Kitti2015](http://www.cvlibs.net/datasets/kitti/user_login.php)
* [Middlebury2014](http://vision.middlebury.edu/stereo/submit3/upload.html)


## Command Line Interface ##

As an alternative to the interactive interface, a command line interface is
available:

```
# Download the datasets:
# - The resolution of the Middlebury datasets can be chosen as [f]ull, [h]alf,
#   or [q]uarter
python stereo_devkit.py obtain --middlebury_resolution {f,F,h,H,q,Q}

# Run an algorithm:
# - runfile_path is the path to the executable file or Python script that will
#   be called for each dataset, as described in the section "Running" above
# - method_name is the method name to use in the result files, which will be
#   passed to the runfile as first parameter
# - --training is an optional flag which will run the algorithm on the training
#   datasets only
# - additional_arguments are optional additional arguments that will be passed
#   to the run file after the regular arguments.
python stereo_devkit.py run <runfile_path> <method_name> [--training] [additional_arguments]

# Create archives for result submission:
# - method_name is the method to generate the submission archives for, as
#   specified when running the algorithm
# - --training is an optional flag which will create a training-only submission
#   (however, this may only be supported by a subset of benchmarks)
python stereo_devkit.py submit <method_name> [--training]
```
