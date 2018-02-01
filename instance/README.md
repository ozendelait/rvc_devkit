# Robust Vision Challenge 2018 - Instance Segmentation Devkit #

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.
However, some segmentation benchmarks require users to register and to confirm the license terms before granting access to their data.
Therefore, you need to manually download the following datasets:

Please register on [Cityscapes](https://www.cityscapes-dataset.com/login/) and download the following archives: "leftImg8bit_trainvaltest.zip" and "gtFine_trainvaltest.zip".
Similarly, signup on [WildDash](http://wilddash.cc/accounts/login?next=/download) and download the archive "wd_val_01.zip".

Please prepare the following file structure before running the devkit (Kitti2015 will be downloaded automatically).
```
- devkit/instance/archives/
   - Cityscapes_archives/leftImg8bit_trainvaltest.zip
   - Cityscapes_archives/gtFine_trainvaltest.zip
   - WildDash_archives/wd_val_01.zip
```

The simplest way to use the devkit is to run the main script without any program
arguments:
```
python instance_devkit.py
```
On Windows, one may double-click instance_devkit.py if Python is installed.
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

The [Kitti 2015 segmentation format](TODO) is used as common format for all datasets.
The image names are prefixed by the dataset's benchmark name.
Exactly the same image names are used for the input images and the ground truth files.
```
- test
   - image_2
- training
   - image_2
      - <dataset>_img_name.png
      - ...
   - instance
      - <dataset>_img_name.png
      - ...
```

The label mapping for the instance segmentation is as follows:
TODO

#### Output ####

Result files for an instance segmentation method must be named as follows and placed in the
directory of the corresponding dataset:
```
TODO
timeNAME.txt
```
Here, NAME must be the name of the submitted method.

In addition to the instance segmentation image, the time for calculating the segmentation
must be given for each image. The time in seconds is stored as a floating
point value in ASCII encoding in a text file. The file must contain only that
number.

#### Running ####

To run an algorithm, simply run the devkit script again in the same directory
in which it was run originally:
```
python instance_devkit.py
```

The algorithm folder must be in the same directory. Under these conditions,
the script will offer to run the algorithm. An alternative way to run algorithms
using the command line interface is described below in the respective section.

In general, the script looks for all folders starting with alg-. They must
contain a file named either "run" or "run.py", which is executed by the script
for all datasets. If the file is a Python script, the same interpreter version
used for running the devkit script is used. The following arguments are passed
to the script:

1. The method name to use for the result.
2. The path to the input images.
3. The path to the training data.
4. The directory to output the result files to.
5. Optional additional arguments, if given.


## Result Submission ##

After an instance segmentation method has been run on all datasets, the results can be
automatically packaged for submission to each individual benchmark. To do so,
simply run the devkit script again in the same directory:
```
python instance_devkit.py
```
It will then offer to create the submission archives. Notice that this requires
that results with the same method name are available for all datasets of all
relevant benchmarks (either for training or for both training and testing). If
the option to create a submission is missing, make sure that all required files
exist.

The resulting archives must be submitted to the respective benchmarks:
TODO: How to mark the submissions as belonging to ROB?
* [Cityscapes](https://www.cityscapes-dataset.com/login/)
* [Kitti2015](http://www.cvlibs.net/datasets/kitti/user_login.php)
* [ScanNet](http://www.scan-net.org/)
* [WildDash](http://wilddash.cc/accounts/login)

Furthermore, the submission must be completed by filling a short form on the
Robust Vision Challenge website: TODO


## Command Line Interface ##

As an alternative to the interactive interface, a command line interface is
available:

```
# Download the datasets:
python instance_devkit.py obtain

# Run an algorithm:
# - runfile_path is the path to the executable file or Python script that will
#   be called for each dataset, as described in the section "Running" above
# - method_name is the method name to use in the result files, which will be
#   passed to the runfile as first parameter
# - --training is an optional flag which will run the algorithm on the training
#   datasets only
# - additional_arguments are optional additional arguments that will be passed
#   to the run file after the regular arguments.
python instance_devkit.py run <runfile_path> <method_name> [--training] [additional_arguments]

# Create archives for result submission:
# - method_name is the method to generate the submission archives for, as
#   specified when running the algorithm
# - --training is an optional flag which will create a training-only submission
#   (however, this may only be supported by a subset of benchmarks)
python instance_devkit.py submit <method_name> [--training]
```
