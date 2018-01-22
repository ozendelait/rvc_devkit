# Robust Vision Challenge 2018 - Multi-View Stereo Devkit #

## Requirements ##

You must install the 7zip program into the system path. For example, under
Debian/Ubuntu you can run ``sudo apt install p7zip-full``, under Mac you can
run ``brew install p7zip``, and under Windows you must download from
http://www.7-zip.org/ and install it manually.


## Dataset Download ##

You can download the Middlebury and ETH3D datasets using the command:

    python mvs/mvs_devkit.py --path PATH --action download

where *PATH* will contain the downloaded datasets. If you only want to download
one dataset, you can specify its name explicitly, e.g.:

    python mvs/mvs_devkit.py --path PATH --action download --dataset ETH3D

The above commands will download the datasets in their respective format.
You can download and convert both to a single format using:

    python mvs/mvs_devkit.py --path PATH --action download --format Middlebury

with Middlebury or ETH3D as format. For example, if you downloaded the
Middlebury dataset in the ETH3D format, you will find the data in the
*PATH/dataset_Middlebury/format_ETH3D* folder.


## Dataset Formats ##

The Middlebury format is documented at http://vision.middlebury.edu/mview/data/.

The ETH3D format follows the COLMAP conventions. The format is documented in
detail at https://www.eth3d.net/documentation and https://colmap.github.io/.


## Result Submission ##

You can either create your submission manually according to the instructions
on the benchmark websites at http://vision.middlebury.edu/mview/submit/ and
https://www.eth3d.net/documentation#result-submission or use our provided
automatic submission packager:

    python mvs/mvs_devkit.py --path PATH --action submit

This will package the results from the ETH3D dataset in the ETH3D format and
the results from the Middlebury dataset in the Middlebury format. If you want
to package the submission for a specific format and dataset, run the command:

    python mvs/mvs_devkit.py --path PATH --action submit \
                             --dataset ETH3D --format Middlebury

For the Middlebury dataset, this assumes you provided your result files as:

    PATH/dataset_Middlebury/format_Middlebury/test/dino/dino.ply
    PATH/dataset_Middlebury/format_Middlebury/test/dinoRing/dinoRing.ply
    ...

For the ETH3D dataset, this assumes you provided your result files as:

    PATH/dataset_ETH3D/format_ETH3D/high_res_multi_view/test/door/door.ply
    PATH/dataset_ETH3D/format_ETH3D/high_res_multi_view/test/door/door.txt
    ...

while the .ply file contains the result point cloud and the .txt file the
runtime statistics in the format:

    runtime <runtime_in_seconds>
