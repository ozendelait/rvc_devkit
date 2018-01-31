# Robust Vision Challenge 2018 Devkits

This repository contains the devkits for the [Robust Vision Challenge 2018](http://robustvision.net/).
The devkits make it easy to participate in the challenge by:

* downloading the required datasets,
* converting them to a common format, and
* creating archives for submission to the individual benchmarks.

Any updates to the devkits will be provided via this repository.
Notice that using the devkits is not required for participating in the
challenge: alternatively, algorithms can be manually run on each dataset and
results submitted to all benchmarks individually.


## Getting started ##

Prerequisites: Install `git` and `python` (both versions 2.7.x and 3.x should work) if they are not installed yet.

1. Clone this repository:
   
   ```git clone http://cvlibs.net:3000/ageiger/rob_devkit.git```
2. See the README in the subfolder of the task you are interested in (depth,
   flow, etc.) for further task-specific instructions.


## Participating ##

The process for participating in the challenge is as follows.

* After following the instructions for getting started above, download the
  datasets for the task which you are interested in using the devkit for this task.
  See the README in the task subfolder for instructions on this.
* Some of the datasets come with ground truth data and can be used for training
  your algorithm.
* Once you are happy with the results of your algorithm based on the training datasets,
  run your algorithm on all datasets. See the README for the specific task for
  information on the expected result format.
* Use the devkit to create submission archives for all included benchmarks.
* Submit each archive to the respective benchmark website. Make sure to use "_ROB" as
  a posfix to your method name to signal that your submission participates in
  the challenge. For example, if your method was called ELAS, name your
  submission ELAS_ROB.
