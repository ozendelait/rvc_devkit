# Robust Vision Challenge 2022 -  Semantic Segmentation Devkit #

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format. First specifying the target root directory for all RVC datasets using an environment variable

export RVC_DATA_DIR=/path/to/rvc_dataroot

Some segmentation benchmarks require users to register and to confirm the license terms before granting access to their data.
For the Cityscapes dataset, please register at: https://www.cityscapes-dataset.com 

For the WildDash dataset, please register at: https://www.wilddash.cc (Note: you can use the beta or final version of WildDash v2; both use the same evaluation label policy; see the downloaded readme/license for details).

To use the automatic download script, define these environment variables using 

```
# Copy Cityscapes credentials here
export CITYSCAPES_USERNAME="your_cs_username"
export CITYSCAPES_PASSWORD="your_cs_passwd"
# Copy WildDash credentials here
export WILDDASH_USERNAME="your_wd_username"
export WILDDASH_PASSWORD="your_wd_passwd"
```

Now you can execute the download script ``` download_sem_segm.sh ``` which will download most of the RVC datasets automatically.

The semantic segmentation task uses [MSeg](http://vladlen.info/publications/mseg-composite-dataset-multi-domain-semantic-segmentation). Please see the [paper](http://vladlen.info/papers/MSeg.pdf) & [repo](https://github.com/mseg-dataset) regarding requirements and tips on how to start a unified training. 

You need to manually register and download the Mapillary Vistas (Research Edition) dataset:
https://www.mapillary.com/dataset/vistas
Note: RVC2022 uses **MVD v1.2** ! 

You will receive an email with download instructions. Save/Move the downloaded zip file into the folder ${RVC_DATA_DIR}/mvd.

After successfully downloading all datasets, execute this script to extract and delete clean up files: ```extract_and_cleanup_panoptic_segm.sh ```, ``` extract_and_cleanup_inst_segm.sh ```, or ```extract_and_cleanup_sem_segm.sh ```

## Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ``` remap_panoptic_segm.sh ```,  ``` remap_inst_segm.sh ```, or ``` remap_sem_segm.sh ```

## Dataset Format ##

For semantic segmentation, this creates two folders (train and val) at ``` ${RVC_DATA_DIR}/rvc_uint8 ``` with uint8 png annotation files and a symbolic-linked image folders with the same structure as the annotations.
The "file_name" tag of each image entry and annotation entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your training framework.

## Result Submission ##
Fill in the "Register Method to RVC" form here: http://www.robustvision.net/submit.php

After that, upload your predictions for the respective test sets of each benchmark.
Here are the upload links for each of the segmentation tasks:

### Semantic Segmentation Task ###
- ADE20K: http://sceneparsing.csail.mit.edu/eval/
- Cityscapes: https://www.cityscapes-dataset.com/submit/
- MVD v1.2: https://codalab.lisn.upsaclay.fr/competitions/5821
- ScanNet: http://kaldir.vc.in.tum.de/scannet_benchmark/login
- VIPER: https://playing-for-benchmarks.org/submissions/my/
- WildDash2: https://wilddash.cc/challenges/submissions

Some notes: MVD expects category ids in the range [1;65] where "bird" has category_id 1 and there is no unlabeled label. VIPER requires the "file_name" entry to be the same filename as found in the testset (.png instead of jpg ext.). 
