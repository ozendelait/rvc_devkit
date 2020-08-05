# Robust Vision Challenge 2020 - Panoptic, Instance, and Semantic Segmentation Devkit #

**Update 2020-08-05: The  KITTI panoptic challenge server and the COCO semantic segmentation challenge server have technical difficulties. Both challenges will be ranked with the remaining benchmarks. You do not have to change your existing models, as stated by the rules any additional public datasets are allowed during training. **

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format. First specifying the target root directory for all RVC datasets using an environment variable

export RVC_DATA_DIR=/path/to/rvc_dataroot

Some segmentation benchmarks require users to register and to confirm the license terms before granting access to their data.
For the Cityscapes dataset, please register at: https://www.cityscapes-dataset.com 

For the WildDash dataset, please register at: https://www.wilddash.cc (Note: RVC users can already use a alpha version of WildDash v2; see the downloaded readme/license for details).

To use the automatic download script, define these environment variables using 

```
# Copy Cityscapes credentials here
export CITYSCAPES_USERNAME="your_cs_username"
export CITYSCAPES_PASSWORD="your_cs_passwd"
# Copy WildDash credentials here
export WILDDASH_USERNAME="your_wd_username"
export WILDDASH_PASSWORD="your_wd_passwd"
```

Now you can execute the download script ``` download_panoptic_segm.sh ```, ``` download_inst_segm.sh ```, ``` download_sem_segm.sh ``` or which will download most of the RVC datasets.

The semantic segmentation task uses [MSeg](http://vladlen.info/publications/mseg-composite-dataset-multi-domain-semantic-segmentation). Please see the [paper](http://vladlen.info/papers/MSeg.pdf) & [repo](https://github.com/mseg-dataset) regarding requirements and tips on how to start a unified training. 

You need to manually register and download the Mapillary Vistas (Research Edition) dataset:
https://www.mapillary.com/dataset/vistas

You will receive an email with download instructions. Save/Move the downloaded zip file into the folder ${RVC_DATA_DIR}/mvd.

After successfully downloading all datasets, execute this script to extract and delete clean up files: ```extract_and_cleanup_panoptic_segm.sh ```, ``` extract_and_cleanup_inst_segm.sh ```, or ```extract_and_cleanup_sem_segm.sh ```

## Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ``` remap_panoptic_segm.sh ```,  ``` remap_inst_segm.sh ```, or ``` remap_sem_segm.sh ```

## Dataset Format ##

For semantic segmentation, this creates two folders (train and val) at ``` ${RVC_DATA_DIR}/rvc_uint8 ``` with uint8 png annotation files and a symbolic-linked image folders with the same structure as the annotations. For the other two tasks, the above step creates a joint training and a separate joint validation json file in COCO Panoptic format:

http://cocodataset.org/#format-data

The "file_name" tag of each image entry and annotation entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your training framework.

## Result Submission ##
Fill in the "Register Method to RVC" form here: http://www.robustvision.net/submit.php

After that, upload your predictions for the respective test sets of each benchmark.
Here are the upload links for each of the segmentation tasks:

### Semantic Segmentation Task ###
- ADE20K: http://sceneparsing.csail.mit.edu/eval/
- Cityscapes: https://www.cityscapes-dataset.com/submit/
- KITTI: http://www.cvlibs.net/datasets/kitti/user_submit.php
- MVD: https://codalab.mapillary.com/competitions/43
- ScanNet: http://kaldir.vc.in.tum.de/scannet_benchmark/login
- VIPER: https://playing-for-benchmarks.org/submissions/my/
- WildDash2: https://wilddash.cc/challenges/submissions

### Instance Segmentation Task ###
- COCO: https://competitions.codalab.org/competitions/25388#learn_the_details
- Cityscapes: https://www.cityscapes-dataset.com/submit/
- KITTI: http://www.cvlibs.net/datasets/kitti/user_submit.php
- MVD: https://codalab.mapillary.com/competitions/40
- OID: https://www.kaggle.com/c/open-images-instance-segmentation-rvc-2020
- ScanNet: http://kaldir.vc.in.tum.de/scannet_benchmark/login
- VIPER: https://playing-for-benchmarks.org/submissions/my/
- WildDash2: https://wilddash.cc/challenges/submissions

### Panoptic Segmentation Task ###
- COCO: https://competitions.codalab.org/competitions/25386#learn_the_details
- Cityscapes: https://www.cityscapes-dataset.com/submit/
- MVD: https://codalab.mapillary.com/competitions/42
- VIPER: https://playing-for-benchmarks.org/submissions/my/
- WildDash: https://wilddash.cc/challenges/submissions
