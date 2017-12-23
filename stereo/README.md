# Robust Vision Challenge 2018 - Stereo Devkit #

## Dataset Download ##

To use the devkit, simply run:
```
python stereo_devkit.py
```
The script will ask about a few settings and then download the datasets into a
folder "datasets" in the current working directory. All datasets are converted to the
[Middlebury 2014 Stereo format](http://vision.middlebury.edu/stereo/data/scenes2014/).
The folder layout is as follows:

```
- datasets
  - test
  - training
```

Within the test and training folders, each subfolder contains a dataset (i.e.,
a stereo pair). The dataset names are prefixed by the dataset's benchmark name.
While additional files are present for datasets of certain
benchmarks (such as object masks), the following files are available for all
datasets.

For test datasets:
```
calib.txt
im0.png
im1.png
```

For training datasets:
```
calib.txt
disp0GT.pfm
im0.png
im1.png
```


## Result Submission ##

According to the Middlebury format, the output files expected for a method are
the following, which must be placed in the same directory as the dataset:
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

In addition to the disparity images, the time for calculating either the
disparity images must be given for each image pair. The time in seconds is
stored as a floating point value in ASCII encoding in a text file. The file must
contain only that number.

After a stereo method has been run on all datasets, the results can be
automatically packaged for submission to each individual benchmark. To do so,
simply run the devkit script again in the same directory:
```
python stereo_devkit.py
```
It will then offer to create the submission archives. Notice that this requires
that results with the same method name are available for all datasets of all
relevant benchmarks (either for training or for both training and testing).

The resulting files must be submitted to the respective benchmarks:
TODO: How to mark the submissions as belonging to ROB?
* [ETH3D2017](https://www.eth3d.net/login)
* [HCI2016](http://hci-benchmark.org/accounts/login?next=/challenges/submissions/create/stereo_geometry&hc=stereo_geometry)
* [Kitti2015](http://www.cvlibs.net/datasets/kitti/user_login.php)
* [Middlebury2014](http://vision.middlebury.edu/stereo/submit3/upload.html)

Furthermore, the submission must be completed by filling a short form on the
Robust Vision Challenge website: TODO
