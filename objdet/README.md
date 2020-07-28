# Robust Vision Challenge 2020 - Object Detection Devkit #

The Object detection challenge consists of four datasets:
- [MS COCO](cocodataset.org/)
- [OpenImages](https://storage.googleapis.com/openimages/web/index.html) (OID)
- [Mapillary Vistas](https://www.mapillary.com/dataset/vistas) (MVD)

**Update 2020-07-17: Megvii had to remove Obj365 from the RVC due to internal policy changes (see objects365.org); we will rank the obj. det. challenge using the three benchmarks COCO, OID, and MVD**

## Requirements ##
Install additional requirements with:
    ``` pip install -r requirements.txt ```


## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.
This is done by first specifying the target root directory for all RVC datasets using an environment variable

 ``` export RVC_DATA_DIR=/path/to/rvc_dataroot  ```

Now you can execute the download script ``` bash download_obj_det.sh ``` which will download most of the RVC datasets.
The extracted dataset needs xxxx GB of disk space (COCO: 26GB, OID: 527GB, Objects365: 394GB, MVD: 25GB). Please note that up to 50% more disc space is required during the extraction process.

You need to manually register and download the Mapillary Vistas (Research Edition) dataset:
https://www.mapillary.com/dataset/vistas

You will receive an email with download instructions. Save/Move the downloaded zip file into the folder ${RVC_DATA_DIR}/mvd.

After successfully downloading all datasets, execute this script to extract and delete clean up files:  ``` bash extract_and_cleanup.sh ``` 

### Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ```bash remap_obj_det.sh ```

## Dataset Format / Training ##

The above step creates a joint training and a separate joint validation json file in COCO Object Detection format (only bbox entries, without "segmentation" entries):

http://cocodataset.org/#format-data

The "file_name" tag of each image entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your object detector training framework.

## Result Submission ##

Fill in the "Register Method to RVC" form here: http://www.robustvision.net/submit.php

After that, upload your predictions for the respective test sets of each benchmark:

COCO : https://competitions.codalab.org/competitions/25334
MVD : https://codalab.mapillary.com/competitions/41
OID : https://www.kaggle.com/c/open-images-object-detection-rvc-2020
