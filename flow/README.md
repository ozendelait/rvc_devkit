# Robust Vision Challenge 2022 - Optical Flow Devkit #

## Dataset Download ##

The simplest way to use the devkit is to run the main script without any program
arguments:
```
python flow_devkit.py
```
On Windows, one may double-click flow_devkit.py if Python is installed.
The script may ask about a few settings and then download the datasets into a
folder in the current working directory. The folder layout is as follows:

```
- datasets_<format_name>
  - metadata
  - test
  - training
```
Note that the script will first download the dataset archives, then 
extract and convert them. The extraction & conversion steps may take a long time after the
downloads have finished to complete.

If the optional program argument `--keep_archives` is given, the downloaded
archive files will not be deleted after the datasets are extracted
and converted.


## Dataset Format ##

#### Input ####

The input file format can be chosen to be either based on Middlebury
(i.e. .flo files) or on KITTI (i.e. PNG files). For the format
descriptions of the individual flow fields, please see the respective
websites.

For Middlebury format, the folder structure is as follows (SEQ denotes
the sequence name, XXXX the frame number, starting with 1.)

```
datasets_middlebury/
    test/
        images/
            SEQ/
                frame_XXXX.png
                ...
            ...
    training/
        images/
            SEQ/
                frame_XXXX.png
                ...
            ...
        flow/
            SEQ/
                frame_XXXX.flo
                ...
            ...
```

For the KITTI format, the structure is

```
datasets_kitti2015/
    testing/
        image_2/
            SEQ_XX.png
            ...
    training/
        image_2/
            SEQ_XX.png
            ...
        flow_occ/
            SEQ_XX.png
            ...
```

#### Output ####

The output structure should be analogous to the input.
If your algorithm is called MYALGO, the expected folder for the
Middlebury format is

```
datasets_middlebury/
    test/
        MYALGO_flow/
            SEQ/
                frame_XXXX.flo
                ...
            ...
```

For KITTI and Middlebury, there needs to be a file ```frame_0010.flo``` in each SEQ directory. 
For Sintel and VIPER there must be a ```frame_00xx.flo``` for each frame pair in each sequence. Note that the VIPER frame pairs are non-consecutive. 
For HD1K (not currently supported), the time for calculating the optical flow is expected in addition to each flow result.
The time in seconds is stored as a floating point value in ASCII encoding in a text file called ```frame_XXXX.txt```.
The file must contain only that number. Runtime files should be placed right next to the flow results in the same directory.

And for KITTI:

```
datasets_kitti2015/
    testing/
        MYALGO_flow_occ/
            SEQ_XX.png
            ...
```


#### Running ####

Currently, it is required to manually call your method and create
an output file structure as described above.

In the Middlebury format, when running a method on pairs of input images, name the resulting .flo file after the lower-indexed input frame image.
For example, if you're running your method on ```frame_0010.png``` and ```frame_0011.png```, name the output file ```frame_0010.flo```.
Thus, the submission packager expects files ```frame_0010.flo``` in each SEQ directory for KITTI and Middlebury,
files ```frame_0001.flo``` through ```frame_0049.flo``` (for example) for Sintel, and one file corresponding to each image pair for VIPER.

It may be necessary to write bash scripts to run your method on each frame pair in each dataset. 

## Result Submission ##

Start your submission by submitting a short form on the
Robust Vision Challenge website: [submission form](http://robustvision.net/submit.php#register).

After a flow method has been run on all datasets, the results can be
automatically packaged for submission to each individual benchmark. To do so,
simply run the devkit script again in the same directory:
```
python flow_devkit.py
```
It will then offer to create the submission archives. Notice that this requires
that results with the same method name are available for the test sets of all
datasets of all relevant benchmarks. If the option to create a submission is
missing, make sure that all required files exist.

The resulting archives must be submitted to the respective benchmarks:
* [MPI-Sintel](http://sintel.is.tue.mpg.de/login)
* [Kitti2015](<http://www.cvlibs.net/datasets/kitti/user_login.php>
)
* [Middlebury](http://vision.middlebury.edu/flow/submit/)
* [VIPER](https://playing-for-benchmarks.org/submissions/my/)

For VIPER submission use the [VIPER toolkit](https://github.com/srrichter/viper) script [prepare_submission.py](https://github.com/srrichter/viper/blob/master/prepare_submission.py) which creates a submission from a folder with results as .flo files ( [details](https://github.com/srrichter/viper/blob/master/EVALUATION.md#optical-flow) ).

To signify that your method is part of a submission to the Robust Vision
Challenge, please add the postfix ``_RVC`` to your algorithm name for all
submissions.

## Command Line Interface ##

As an alternative to the interactive interface, a command line interface is
available:

```
# Download the datasets:
python flow_devkit.py obtain

# Create archives for result submission:
# - method_name is the method to generate the submission archives for, as
#   specified when running the algorithm
python flow_devkit.py submit <method_name>
```
